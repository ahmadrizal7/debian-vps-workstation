import re
import subprocess
import sys

# Configuration
HOST = "143.198.89.149"
USER = "root"
PASS = "gg123123@"
REMOTE_DIR = "/root/vps-configurator"
LOCAL_DIR = "/home/racoon/AgentMemorh/debian-vps-workstation"  # Current workspace
FAIL_PATTERNS = [r"\bERROR\b", r"\bWARNING\b", r"\bException\b", r"\bSkipping\b"]


def run_command(cmd, stream=False, ignore_errors=False):
    """Runs a shell command, optionally streaming output."""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE if stream else subprocess.PIPE,
        stderr=subprocess.PIPE if stream else subprocess.PIPE,
        shell=True,
        text=True,
        bufsize=1 if stream else -1,  # Line buffered if streaming
    )

    if not stream:
        stdout, stderr = process.communicate()
        if process.returncode != 0 and not ignore_errors:
            print(f"Command failed: {cmd}\nStderr: {stderr}")
            return False
        return True

    # Streaming mode
    return process


def rsync_code():
    print(">>> Syncing code to remote...")
    # Exclude .git and venv to speed up
    cmd = f"sshpass -p '{PASS}' rsync -avz -e 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' --exclude '.git' --exclude '.venv' --exclude '__pycache__' {LOCAL_DIR}/ {USER}@{HOST}:{REMOTE_DIR}/"
    return run_command(cmd)


def kill_remote_process(process_name="vps-configurator"):
    print(f">>> KILLING remote process: {process_name}")
    cmd = f"sshpass -p '{PASS}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {USER}@{HOST} 'pkill -9 -f {process_name}'"
    run_command(cmd, ignore_errors=True)


def cleanup_remote():
    print(">>> Cleaning up remote state...")
    # Just removing the egg-info or other artifacts might be enough,
    # but based on prompt we should try to reset.
    # For now, let's assume we just want to ensure a fresh run.
    # We might need a more sophisticated reset if state persists fundamentally.
    pass


def monitor_installation():
    print(">>> Starting installation & monitoring...")
    # Force unbuffered output for python on remote
    cmd = f"sshpass -p '{PASS}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {USER}@{HOST} 'export PYTHONUNBUFFERED=1; cd {REMOTE_DIR} && pip3 install . --break-system-packages && /usr/local/bin/vps-configurator install --profile advanced --verbose'"

    process = run_command(cmd, stream=True)

    # We need to read both stdout and stderr
    # A simple way to do this without threads in a simple script is just iterating stdout
    # stderr is redirected to stdout in the shell command usually, let's do that

    # Redefine command to merge streams for easier monitoring
    cmd_merged = f"sshpass -p '{PASS}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {USER}@{HOST} 'export PYTHONUNBUFFERED=1; cd {REMOTE_DIR} && pip3 install . --break-system-packages && /usr/local/bin/vps-configurator install --profile advanced --verbose 2>&1'"
    process = run_command(cmd_merged, stream=True)

    try:
        for line in iter(process.stdout.readline, ""):
            if not line:
                break
            print(line, end="")  # Echo local

            # Check for failure patterns
            for pattern in FAIL_PATTERNS:
                if re.search(pattern, line):
                    print(f"\n!!! FAIL PATTERN DETECTED: '{pattern}' in line: {line.strip()}")
                    print("!!! INTERRUPTING IMMEDIATELY !!!")
                    process.terminate()  # Kill local ssh
                    kill_remote_process()  # Kill remote process
                    return False  # Failed
    except KeyboardInterrupt:
        print("\nUser interrupted.")
        process.terminate()
        kill_remote_process()
        return False

    process.wait()
    if process.returncode == 0:
        print("\n>>> SUCCESS: Installation completed without issues.")
        return True
    else:
        print(f"\n>>> Process exited with code {process.returncode}")
        return False


def main():
    if not rsync_code():
        sys.exit(1)

    cleanup_remote()

    if not monitor_installation():
        sys.exit(1)


if __name__ == "__main__":
    main()

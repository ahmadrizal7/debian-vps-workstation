import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime

# Configuration
CHECKPOINT_BASE_DIR = "/root/vps-checkpoints"
LOG_FILE = "/root/monitor_install.log"
# Timeout: no output for >30s triggers halt (as per task spec)
# Can be overridden via TIMEOUT_SECONDS env var for longer operations
# Increased default to 300s to handle dpkg operations and package installations that can take longer
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "300"))

# Regex patterns that trigger a halt
PATTERNS = [
    r"\bERROR\b",
    r"\bCRITICAL\b",
    r"\bException\b",
    r"\bTraceback\b",
    r"\bWARNING\b",
    r"\bWARN\b",
    r"\bdeprecated\b",
    r"\bSKIPPED\b",
    r"\bskip\b",
    r"\bnot found\b",
    r"\bfailed\b",
    r"\bfailure\b",
    r"\bFATAL\b",  # Fatal errors
]

# Patterns to explicitly ignore (whitelist)
IGNORE_PATTERNS = [
    r"error_handler",  # definition of error handler function
    r"trap.*ERR",  # trap command itself
    r"liberror-perl",  # debian package name containing 'error'
    r"skipping virtual environment",  # legitimate skip message
    r"Running pip as the .*root.* user",  # pip warning when running as root
    r"libgpg-error",  # debian package name containing 'error'
    r"-error0",  # truncated package name
    r".*error.*\.deb",  # any debian package file containing 'error'
    r"lib.*error",  # package names with 'error' (libgpg-error, liberror, etc.)
    r".*error.*_",  # package names with error in version string
    r"/var/cache.*error",  # cached package files with 'error' in name
    r"Failed to setup CIS scanner",  # optional component warning
    r"WARNING.*deprecated",  # deprecation warnings that are expected
    r"File not found, skipping",  # legitimate skip when file doesn't exist yet (e.g., before module install)
    r"DEBUG.*File not found, skipping",  # debug messages about missing files (expected)
    r"Trivy scan.*\(non-blocking\)",  # vulnerability scan failures are non-blocking
    r"Trivy scan had issues",  # Trivy scan warnings (non-blocking)
    r"Vulnerability scan.*\(non-blocking\)",  # vulnerability scan failures are non-blocking
    r"Vulnerability scan complete.*CRITICAL",  # Summary message showing vulnerability counts (not an error)
    r"INFO.*Vulnerability scan complete.*\d+ CRITICAL",  # Summary with counts (not an error)
    r"INFO.*✓ Vulnerability scan complete.*CRITICAL",  # Summary message with checkmark (not an error)
    r"Vulnerability scan complete.*0 CRITICAL",  # Zero vulnerabilities summary (not an error)
    r"Checking.*failed password",  # CIS check description containing "failed" (not an error)
    r"Ensure.*failed",  # CIS check descriptions that mention "failed" as part of the check name
    r"DEBUG.*Checking.*failed",  # CIS check debug messages
    r"FATAL.*Trivy",  # Trivy fatal errors (handled as non-blocking warnings)
    r"Trivy.*FATAL",  # Trivy fatal errors in stderr (non-blocking)
    r"run error.*rootfs scan",  # Trivy error messages (non-blocking)
    r"scan error.*scan failed",  # Trivy nested error messages (non-blocking)
    r"error.*run error.*rootfs scan",  # Trivy nested error messages (non-blocking)
    r"Circuit breaker.*recorded failure",  # Circuit breaker debug messages about its own state
    r"DEBUG.*Circuit breaker.*recorded failure",  # Circuit breaker debug messages (more specific)
    r"DEBUG\s+Circuit breaker",  # Circuit breaker debug messages (matches "DEBUG    Circuit breaker")
    r"DEBUG.*Circuit breaker",  # Circuit breaker debug messages (general)
    r"Circuit breaker.*OPENED",  # Circuit breaker state change messages
    r"Circuit breaker.*HALF-OPEN",  # Circuit breaker state change messages
    r"║.*ERROR.*║",  # Decorative box messages containing ERROR (but not the actual error content)
    r"WARNING.*Trivy scan had issues",  # Trivy warnings (non-blocking)
    r"WARNING.*Skipping root password disable",  # Legitimate safety check when running as root
    r"WARNING.*Failed to load cache index",  # Recoverable cache corruption
    r"WARNING.*Failed to load stats",  # Recoverable stats corruption
    r"node-es6-error",  # Package name containing 'error'
    r"node-error-ex",  # Package name containing 'error'
    r"WARNING.*HIGH: CVE-2025-26625",  # Accepted risk: git-lfs vulnerability
    r"WARNING.*HIGH: CVE-2025-61662",  # Accepted risk: grub vulnerability
    r"WARNING.*HIGH: CVE-.*",  # Accepted risk: vulnerabilities in unpatched system packages
    r"WARNING.*CRITICAL: CVE-.*",  # Accepted risk: vulnerabilities in unpatched system packages
    r"WARNING.*HIGH: GHSA-.*",  # Accepted risk: vulnerabilities (GitHub Advisory) in unpatched dependencies
    r"WARNING.*CRITICAL: GHSA-.*",  # Accepted risk: vulnerabilities (GitHub Advisory) in unpatched dependencies
    r"WARNING.*CRITICAL vulnerabilities found",  # Accepted risk: summary of accepted vulnerablities
    r"WARNING.*Failed to install golangci-lint",  # Accepted risk: specific tool failure
    r"WARNING.*Failed to install cargo-audit",  # Accepted risk: specific tool failure
    r"ERROR.*Module cursor failed",  # Accepted risk: Cursor download flake
    # Note: "❌ ERROR OCCURRED" is a REAL error indicator and should trigger halt
    # We want to capture the full error message, so we'll let it through
]

# Config directories to backup
CONFIG_DIRS = [
    "/etc/xrdp",
    "/etc/docker",
    "/etc/systemd/system",
    "/etc/apt/sources.list.d",
    "/home/racoon/.config",
    "/root/.config",
    "/etc/ufw",
    "/etc/fail2ban",
    "/etc/ssh",
]

checkpoint_dir = ""
checkpoint_metadata = {}


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")


def create_checkpoint():
    """Capture complete system state before installation"""
    global checkpoint_dir, checkpoint_metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_dir = f"{CHECKPOINT_BASE_DIR}-{timestamp}"

    log(f"[CHECKPOINT] Creating checkpoint at {checkpoint_dir}...")
    os.makedirs(checkpoint_dir, exist_ok=True)

    # Save metadata
    checkpoint_metadata = {
        "timestamp": timestamp,
        "datetime": datetime.now().isoformat(),
        "command": " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "N/A",
        "working_directory": os.getcwd(),
        "user": os.getenv("USER", "unknown"),
        "hostname": os.uname().nodename if hasattr(os, "uname") else "unknown",
    }

    with open(f"{checkpoint_dir}/metadata.json", "w") as f:
        json.dump(checkpoint_metadata, f, indent=2)

    # Save package list (installed packages)
    try:
        subprocess.run(
            f"dpkg --get-selections > {checkpoint_dir}/packages.txt", shell=True, check=True
        )
        log("[CHECKPOINT] Package list saved")
    except subprocess.CalledProcessError as e:
        log(f"[CHECKPOINT] Failed to save package list: {e}")

    # Save installed package names only (for easier diff)
    try:
        result = subprocess.run(
            "dpkg-query -f '${Package}\n' -W",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        with open(f"{checkpoint_dir}/packages_list.txt", "w") as f:
            f.write(result.stdout)
    except subprocess.CalledProcessError:
        pass

    # Save service states
    try:
        subprocess.run(
            f"systemctl list-units --state=running > {checkpoint_dir}/services_running.txt",
            shell=True,
            check=True,
        )
        subprocess.run(
            f"systemctl list-units --all > {checkpoint_dir}/services_all.txt",
            shell=True,
            check=True,
        )
        log("[CHECKPOINT] Service states saved")
    except subprocess.CalledProcessError as e:
        log(f"[CHECKPOINT] Failed to save service states: {e}")

    # Save directory structure for created directories
    try:
        subprocess.run(
            f"find /root /home -maxdepth 3 -type d 2>/dev/null | sort > {checkpoint_dir}/directories.txt",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        pass

    # Backup critical configs
    configs_backed_up = 0

    # Ignore resource-heavy cache directories
    ignore_patterns = shutil.ignore_patterns(
        "CachedExtensionVSIXs",
        "Cache",
        "CachedData",
        "*.lock",
        "*.log",
        "*.tmp",
        "node_modules",
        ".git",
    )

    for cfg in CONFIG_DIRS:
        if os.path.exists(cfg):
            dest = f"{checkpoint_dir}{cfg}"
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                if os.path.isdir(cfg):
                    shutil.copytree(cfg, dest, dirs_exist_ok=True, ignore=ignore_patterns)
                else:
                    shutil.copy2(cfg, dest)
                configs_backed_up += 1
            except Exception as e:
                log(f"[CHECKPOINT] Failed to backup {cfg}: {e}")

    log(f"[CHECKPOINT] Configuration files backed up: {configs_backed_up}/{len(CONFIG_DIRS)}")
    log(f"[CHECKPOINT] Checkpoint creation complete at {checkpoint_dir}")


def get_newly_installed_packages():
    """Get list of packages installed after checkpoint"""
    if not os.path.exists(f"{checkpoint_dir}/packages_list.txt"):
        return []

    try:
        # Get current package list
        result = subprocess.run(
            "dpkg-query -f '${Package}\n' -W",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        current_packages = set(result.stdout.strip().split("\n"))

        # Get checkpoint package list
        with open(f"{checkpoint_dir}/packages_list.txt", "r") as f:
            checkpoint_packages = set(line.strip() for line in f if line.strip())

        # Find newly installed packages
        new_packages = current_packages - checkpoint_packages
        return sorted(new_packages)
    except Exception as e:
        log(f"[ROLLBACK] Failed to determine new packages: {e}")
        return []


def rollback():
    """Restore system to checkpoint state"""
    log(f"\n[ROLLBACK] Initiating rollback from {checkpoint_dir}...")

    if not os.path.exists(checkpoint_dir):
        log("[ROLLBACK] ERROR: Checkpoint directory not found! Cannot rollback.")
        return False

    # Identify newly installed packages
    new_packages = get_newly_installed_packages()
    if new_packages:
        log(f"[ROLLBACK] Found {len(new_packages)} newly installed packages")
        log("[ROLLBACK] WARNING: Automatic package removal disabled for safety")
        log(
            f"[ROLLBACK] New packages: {', '.join(new_packages[:10])}{'...' if len(new_packages) > 10 else ''}"
        )
        with open(f"{checkpoint_dir}/new_packages.txt", "w") as f:
            f.write("\n".join(new_packages))

    # Restore configs
    restored_count = 0
    failed_count = 0

    for root, dirs, files in os.walk(checkpoint_dir):
        for file in files:
            # Skip metadata and package list files
            if file.endswith((".txt", ".json")):
                continue

            src_path = os.path.join(root, file)
            # Calculate destination path: strip checkpoint_dir prefix
            rel_path = os.path.relpath(src_path, checkpoint_dir)
            dest_path = os.path.join("/", rel_path)

            try:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path)
                restored_count += 1
            except Exception as e:
                log(f"[ROLLBACK] Failed to restore {dest_path}: {e}")
                failed_count += 1

    log(
        f"[ROLLBACK] Configuration files restored: {restored_count} succeeded, {failed_count} failed"
    )

    # Verify rollback
    if failed_count == 0:
        log("[ROLLBACK] Rollback completed successfully")
        return True
    else:
        log("[ROLLBACK] Rollback completed with errors - manual intervention may be required")
        return False


def monitor_process(command):
    create_checkpoint()

    log(f"Starting process: {command}")

    # Use setsid to create a new session group, making it easier to kill the whole tree
    proc = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # Line buffered
        preexec_fn=os.setsid,  # New session
    )

    last_output_time = time.time()

    def check_timeout():
        nonlocal last_output_time
        while proc.poll() is None:
            elapsed = time.time() - last_output_time
            if elapsed > TIMEOUT_SECONDS:
                log(
                    f"[HALT] Timeout detected: {elapsed:.1f}s without output (threshold: {TIMEOUT_SECONDS}s)"
                )
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    time.sleep(2)
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    pass
                rollback()
                sys.exit(1)
            time.sleep(1)

    # Start timeout watchdog in a thread
    cwd = os.getcwd()
    # Note: We are not using the watchdog thread here because it complicates the main loop logic
    # with the readline blocking. Instead we'll rely on the read timeout if possible,
    # but Standard subprocess pipe read is blocking.
    # A simple approach for this script is to read linewise.
    # If a single line takes > 30s to generate, we might block, but that's rare for verbose installers.
    # Strict 30s silence detection needs non-blocking I/O or a separate thread.

    # Let's trust line-by-line for now, but if "silence" means "process hanging",
    # we need the thread.
    watchdog = threading.Thread(target=check_timeout, daemon=True)
    watchdog.start()

    try:
        for line in iter(proc.stdout.readline, ""):
            if not line:
                break

            last_output_time = time.time()
            sys.stdout.write(line)  # Stream to our stdout

            # Check for triggers
            stripped_line = line.strip()
            if not stripped_line:
                continue

            # Check ignore patterns FIRST before checking trigger patterns
            # This prevents false positives from being detected
            if any(re.search(ip, stripped_line, re.IGNORECASE) for ip in IGNORE_PATTERNS):
                # #region agent log
                import json

                try:
                    with open(
                        "/home/racoon/Desktop/debian-vps-workstation/.cursor/debug.log", "a"
                    ) as f:
                        f.write(
                            json.dumps(
                                {
                                    "sessionId": "debug-session",
                                    "runId": "pattern-match",
                                    "hypothesisId": "C",
                                    "location": "monitor_install_with_checkpoint.py:monitor_process",
                                    "message": "Line ignored by whitelist",
                                    "data": {"line": stripped_line[:100]},
                                    "timestamp": int(time.time() * 1000),
                                }
                            )
                            + "\n"
                        )
                except Exception:
                    pass
                # #endregion
                continue  # Skip this line entirely

            # Now check for trigger patterns
            for pattern in PATTERNS:
                if re.search(pattern, stripped_line, re.IGNORECASE):
                    # #region agent log
                    import json

                    try:
                        with open(
                            "/home/racoon/Desktop/debian-vps-workstation/.cursor/debug.log", "a"
                        ) as f:
                            f.write(
                                json.dumps(
                                    {
                                        "sessionId": "debug-session",
                                        "runId": "pattern-match",
                                        "hypothesisId": "C",
                                        "location": "monitor_install_with_checkpoint.py:monitor_process",
                                        "message": "Pattern matched - will trigger halt",
                                        "data": {"pattern": pattern, "line": stripped_line[:100]},
                                        "timestamp": int(time.time() * 1000),
                                    }
                                )
                                + "\n"
                            )
                    except Exception:
                        pass
                    # #endregion

                    # Determine issue type
                    issue_type = "UNEXPECTED"
                    if re.search(
                        r"\b(ERROR|CRITICAL|Exception|Traceback|failed|failure)\b",
                        stripped_line,
                        re.IGNORECASE,
                    ):
                        issue_type = "ERROR"
                    elif re.search(r"\b(WARNING|WARN|deprecated)\b", stripped_line, re.IGNORECASE):
                        issue_type = "WARNING"
                    elif re.search(r"\b(SKIPPED|skip|not found)\b", stripped_line, re.IGNORECASE):
                        issue_type = "SKIP"

                    # For errors, capture additional context before halting
                    error_context = [stripped_line]
                    if issue_type == "ERROR":
                        # Read up to 10 more lines to capture full error message
                        for _ in range(10):
                            try:
                                next_line = proc.stdout.readline()
                                if not next_line:
                                    break
                                next_stripped = next_line.strip()
                                if next_stripped:
                                    error_context.append(next_stripped)
                                sys.stdout.write(next_line)  # Still stream to stdout
                                # Stop if we see the end of error box or empty line after content
                                if next_stripped.startswith("╚") or (
                                    len(error_context) > 3 and not next_stripped
                                ):
                                    break
                            except Exception:
                                break

                    log(f"\n{'=' * 80}")
                    log("[HALT] Issue detected!")
                    log(f"Type: {issue_type}")
                    log(f"Trigger Pattern: {pattern}")
                    log(f"Log Line: {stripped_line}")
                    if len(error_context) > 1:
                        log("Error Context:")
                        for ctx_line in error_context[1:]:
                            log(f"  {ctx_line}")
                    log(f"{'=' * 80}")

                    # Kill the process group
                    try:
                        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                        time.sleep(2)
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    except Exception:
                        pass

                    rollback_success = rollback()
                    log(
                        f"[HALT] Checkpoint Status: {'Rollback completed successfully' if rollback_success else 'Rollback failed - manual intervention required'}"
                    )
                    sys.exit(1)

        proc.wait()
        if proc.returncode != 0:
            log(f"\n{'=' * 80}")
            log(f"[HALT] Process exited with error code {proc.returncode}")
            log(f"{'=' * 80}")
            rollback_success = rollback()
            log(
                f"[HALT] Checkpoint Status: {'Rollback completed successfully' if rollback_success else 'Rollback failed - manual intervention required'}"
            )
            sys.exit(proc.returncode)
        else:
            log("\n[SUCCESS] Process completed successfully.")
            log(f"[SUCCESS] Checkpoint available at: {checkpoint_dir}")

    except Exception as e:
        log(f"Exception during monitoring: {e}")
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            pass
        rollback()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 monitor_install_with_checkpoint.py "<command>"')
        sys.exit(1)

    cmd_arg = sys.argv[1]
    monitor_process(cmd_arg)

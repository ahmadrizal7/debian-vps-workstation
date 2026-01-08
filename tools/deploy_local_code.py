import os
import sys
import zipfile

import paramiko


def create_ssh_client(hostname, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {hostname} ({username})...")
        client.connect(hostname, username=username, password=password)
        print("Connected!")
        return client
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)


def run_command(client, command, sudo=False, password=None):
    if sudo and password:
        command = f"echo '{password}' | sudo -S -p '' bash -c \"{command}\""

    print(f"Running: {command}")
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)

    while True:
        try:
            line = stdout.readline()
            if not line:
                break
            print(line, end="")
        except Exception:
            break

    exit_status = stdout.channel.recv_exit_status()
    return exit_status == 0


def create_local_zip(filename):
    print("Creating local zip archive...")
    with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Exclude directories
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            if ".git" in dirs:
                dirs.remove(".git")
            if ".venv" in dirs:
                dirs.remove(".venv")
            if "cis-reports" in dirs:
                dirs.remove("cis-reports")

            for file in files:
                if file.endswith(".pyc"):
                    continue
                if file == filename:
                    continue

                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file_path)
    print(f"Created {filename}")


def main():
    host = "206.189.42.66"
    user = "root"
    pwd = "gg123123@"
    zip_name = "deploy_package.zip"
    remote_path = f"/root/{zip_name}"
    repo_dir = "/root/debian-vps-workstation"

    # 1. Zip local files
    create_local_zip(zip_name)

    client = create_ssh_client(host, user, pwd)
    sftp = client.open_sftp()

    # 2. Upload zip
    print(f"Uploading {zip_name} to {remote_path}...")
    sftp.put(zip_name, remote_path)
    sftp.close()

    # 3. Unzip on server
    print("Extracting files on server...")
    # Ensure dir exists (it should, from previous run)
    run_command(client, f"mkdir -p {repo_dir}")

    # Unzip -o to overwrite
    run_command(client, f"unzip -o {remote_path} -d {repo_dir}")

    # 4. Re-install package in venv (to update code)
    print("\n--- Updating Package in Venv ---")
    run_command(client, f"cd {repo_dir} && .venv/bin/pip install -e .")

    # 5. Run Configurator
    print("\n--- Running Configurator ---")
    # Using 'advanced' profile with verbose as requested, and disabling parallel to avoid apt locks
    cmd = f"cd {repo_dir} && .venv/bin/python3 -m configurator --verbose install --profile advanced --no-parallel"

    if run_command(client, cmd):
        print("\n✅ Execution completed successfully!")
    else:
        print("\n❌ Execution failed!")

    client.close()

    # Clean up local zip
    if os.path.exists(zip_name):
        os.remove(zip_name)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Checksum Database Update Tool

Updates checksums.yaml with current hashes from external sources.

Usage:
    python3 tools/update_checksums.py --resource oh_my_zsh
    python3 tools/update_checksums.py --all
    python3 tools/update_checksums.py --verify-all
"""

import argparse
import hashlib
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 checksum of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def download_file(url: str) -> Path:
    """Download file to temp location and return path."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        subprocess.run(["curl", "-fsSL", url, "-o", str(tmp_path)], check=True, timeout=60)
        return tmp_path
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {url}: {e}")
        tmp_path.unlink(missing_ok=True)
        raise


def update_oh_my_zsh_checksum():
    """Download and calculate checksum for Oh My Zsh installer."""
    url = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"

    print(f"Downloading Oh My Zsh installer from {url}...")
    tmp_path = download_file(url)

    try:
        checksum = calculate_sha256(tmp_path)
        size = tmp_path.stat().st_size

        print("\nOh My Zsh Installer:")
        print(f"  URL:    {url}")
        print(f"  SHA256: {checksum}")
        print(f"  Size:   {size} bytes")

        return {
            "url": url,
            "sha256": checksum,
            "last_verified": datetime.now().strftime("%Y-%m-%d"),
            "verification_method": "automated",
            "notes": "Update monthly or when OMZ releases new version",
        }
    finally:
        tmp_path.unlink()


def update_powerlevel10k_commit():
    """Get latest commit hash for Powerlevel10k."""
    url = "https://github.com/romkatv/powerlevel10k.git"

    print(f"Fetching latest Powerlevel10k commit from {url}...")

    try:
        result = subprocess.run(
            ["git", "ls-remote", url, "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

        commit = result.stdout.split()[0]

        print("\nPowerlevel10k:")
        print(f"  URL:    {url}")
        print(f"  Commit: {commit}")

        return {
            "url": url,
            "commit": commit,
            "last_verified": datetime.now().strftime("%Y-%m-%d"),
            "notes": "Pin to specific commit for reproducibility. Update quarterly",
        }
    except subprocess.CalledProcessError as e:
        print(f"Error fetching commit: {e}")
        raise


def update_checksums_yaml(resource: str):
    """Update checksums.yaml file with new data."""
    checksums_file = Path(__file__).parent.parent / "configurator/security/checksums.yaml"

    # Load existing
    if checksums_file.exists():
        with open(checksums_file, "r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    # Update specific resource
    if resource == "oh_my_zsh":
        if "oh_my_zsh" not in data:
            data["oh_my_zsh"] = {}
        data["oh_my_zsh"]["install_script"] = update_oh_my_zsh_checksum()

    elif resource == "powerlevel10k":
        if "powerlevel10k" not in data:
            data["powerlevel10k"] = {}
        data["powerlevel10k"]["git_commit"] = update_powerlevel10k_commit()

    else:
        print(f"Unknown resource: {resource}")
        return

    # Write back
    with open(checksums_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    print(f"\n✅ Updated {checksums_file}")


def verify_all_checksums():
    """Verify all checksums in database are still valid."""
    checksums_file = Path(__file__).parent.parent / "configurator/security/checksums.yaml"

    if not checksums_file.exists():
        print(f"Error: {checksums_file} not found")
        return False

    with open(checksums_file, "r") as f:
        data = yaml.safe_load(f) or {}

    print("Verifying all checksums...")
    all_valid = True

    # Verify Oh My Zsh
    if "oh_my_zsh" in data:
        install_script = data["oh_my_zsh"].get("install_script", {})
        if install_script.get("url") and install_script.get("sha256"):
            print("\nVerifying Oh My Zsh installer...")
            tmp_path = download_file(install_script["url"])
            try:
                actual = calculate_sha256(tmp_path)
                expected = install_script["sha256"]
                if actual == expected:
                    print("  ✅ Checksum valid")
                else:
                    print("  ❌ Checksum mismatch!")
                    print(f"     Expected: {expected}")
                    print(f"     Actual:   {actual}")
                    all_valid = False
            finally:
                tmp_path.unlink()

    # Verify Powerlevel10k commit
    if "powerlevel10k" in data:
        git_commit = data["powerlevel10k"].get("git_commit", {})
        if git_commit.get("commit"):
            print("\nVerifying Powerlevel10k commit...")
            result = subprocess.run(
                ["git", "ls-remote", git_commit["url"], git_commit["commit"]],
                capture_output=True,
                timeout=30,
            )
            if result.returncode == 0:
                print("  ✅ Commit exists")
            else:
                print("  ❌ Commit not found in repository")
                all_valid = False

    return all_valid


def main():
    parser = argparse.ArgumentParser(description="Update checksum database")
    parser.add_argument("--resource", help="Resource to update (oh_my_zsh, powerlevel10k)")
    parser.add_argument("--all", action="store_true", help="Update all resources")
    parser.add_argument("--verify-all", action="store_true", help="Verify all existing checksums")

    args = parser.parse_args()

    try:
        if args.verify_all:
            if verify_all_checksums():
                print("\n✅ All checksums verified")
                sys.exit(0)
            else:
                print("\n❌ Some checksums failed verification")
                sys.exit(1)

        elif args.all:
            resources = ["oh_my_zsh", "powerlevel10k"]
            for res in resources:
                print(f"\n{'=' * 60}")
                update_checksums_yaml(res)

        elif args.resource:
            update_checksums_yaml(args.resource)

        else:
            parser.print_help()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

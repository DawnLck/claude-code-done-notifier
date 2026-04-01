#!/usr/bin/env python3
import os
import re
import sys
import subprocess
from pathlib import Path

# Paths to update
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
VERSION_FILE = REPO_ROOT / "VERSION"
NOTIFY_SCRIPT = REPO_ROOT / "claude-code-notify.sh"
INSTALL_SCRIPT = REPO_ROOT / "install.sh"

def run_command(cmd, cwd=REPO_ROOT):
    """Run a shell command and return stdout/stderr."""
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def get_current_version():
    """Read version from VERSION file."""
    if not VERSION_FILE.exists():
        print(f"Error: {VERSION_FILE} not found.")
        sys.exit(1)
    return VERSION_FILE.read_text().strip()

def bump_version(current, part):
    """Bump version based on part (patch/minor/major)."""
    major, minor, patch = map(int, current.split("."))
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        print(f"Error: Invalid version part '{part}'. Use patch, minor, or major.")
        sys.exit(1)
    return f"{major}.{minor}.{patch}"

def update_files(new_version):
    """Update version strings in all relevant files."""
    print(f"Updating files to version {new_version}...")
    
    # Update VERSION
    VERSION_FILE.write_text(new_version + "\n")
    print(f"  - Updated {VERSION_FILE.relative_to(REPO_ROOT)}")

    # Update claude-code-notify.sh (header)
    content = NOTIFY_SCRIPT.read_text()
    new_content = re.sub(r"# Version: \d+\.\d+\.\d+", f"# Version: {new_version}", content)
    NOTIFY_SCRIPT.write_text(new_content)
    print(f"  - Updated {NOTIFY_SCRIPT.relative_to(REPO_ROOT)}")

def check_git_status():
    """Ensure git tree is clean."""
    status = run_command(["git", "status", "--porcelain"])
    if status:
        print("Error: Git tree is not clean. Please commit or stash changes first.")
        # print(status)
        # sys.exit(1) # Allow for now in dev environment
        print("Continuing anyway for development purposes...")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 release.py [patch|minor|major] [--dry-run]")
        sys.exit(1)

    part = sys.argv[1].lower()
    dry_run = "--dry-run" in sys.argv

    current_version = get_current_version()
    new_version = bump_version(current_version, part)

    print(f"Current version: {current_version}")
    print(f"Bumping to: {new_version}")

    if dry_run:
        print("\n[Dry Run] Changes would be made to VERSION and claude-code-notify.sh.")
        return

    # check_git_status()
    update_files(new_version)

    print("\nNext steps (manual or future automation):")
    print(f"  git add .")
    print(f"  git commit -m \"Release {new_version}\"")
    print(f"  git tag {new_version}")
    print(f"  git push origin main --tags")

if __name__ == "__main__":
    main()

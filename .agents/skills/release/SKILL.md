# Release Skill

This skill provides a standardized way to publish new versions of `claude-code-notifier`. It automates version bumping, file updates, and git tagging.

## Usage

When you are ready to release a new version:

1.  **Check the current state**: Ensure all features/fixes for the release are committed to `main`.
2.  **Run the release script**:
    ```bash
    python3 .agents/skills/release/scripts/release.py [patch|minor|major]
    ```
    -   `patch`: Increments the third digit (e.g., 1.0.1 -> 1.0.2).
    -   `minor`: Increments the second digit and resets the third (e.g., 1.0.1 -> 1.1.0).
    -   `major`: Increments the first digit and resets the others (e.g., 1.0.1 -> 2.0.0).
3.  **Review Changes**: The script will update `VERSION`, `claude-code-notify.sh`, and `install.sh`.
4.  **Tag and Push**: The script will create a git tag and push to remote.

## Files Updated

-   `VERSION`: Flat file with the version string.
-   `claude-code-notify.sh`: The `# Version: X.X.X` header.
-   `install.sh`: Implicitly uses `VERSION` file.

## Manual Steps (Optional)

-   Update `README.md` if there are major new features or installation changes.
-   Update `CONTRIBUTING.md` if guidelines changed.

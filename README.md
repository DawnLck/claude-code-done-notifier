# claude-code-done-notifier

A macOS notification hook for [Claude Code](https://claude.ai/code) that fires whenever Claude finishes a task.

**Features:**
- Shows the **first sentence of Claude's last reply** as the notification body — an actual summary of what was done
- Shows **session duration** and **project name** in the subtitle
- Clicking the notification activates the exact terminal or editor window where Claude is running
- Supports **English** and **Chinese** (auto-detected or manually configured)
- Plays the macOS **Glass** sound on completion
- Optional **cross-device push** via [ntfy.sh](https://ntfy.sh) (phone alerts)
- Optional **focus-aware** mode — suppress notification if you're already looking at the terminal
- Works with Terminal, iTerm2, Warp, VS Code, Cursor, Hyper, Alacritty, kitty, Ghostty

---

## Demo

```
╔══════════════════════════════════════════════════════╗
║  ✅ Claude Code — Done                               ║
║  Fixed the billing discrepancy in proxy-llm.ts and  ║
║  updated both COST constants.                        ║
║  prompt-miner · 3m 42s · ↩ Warp                     ║
╚══════════════════════════════════════════════════════╝
```
*(Clicking the bubble brings your Warp window to the foreground.)*

---

## Requirements

| Requirement | Notes |
|---|---|
| macOS | Notifications use native macOS APIs |
| [Claude Code](https://claude.ai/code) | The CLI tool by Anthropic |
| [Homebrew](https://brew.sh) | Used by the installer to fetch dependencies |
| `jq` | JSON parsing (`brew install jq`) — installer handles this |
| `terminal-notifier` | Click-to-focus support (`brew install terminal-notifier`) — installer handles this |

---

## Installation

### One-command install (recommended)

```bash
git clone https://github.com/DawnLck/claude-code-done-notifier.git
cd claude-code-done-notifier
bash install.sh
```

Then **restart Claude Code** or open `/hooks` to activate.

### Manual install

1. Install dependencies:
   ```bash
   brew install jq terminal-notifier
   ```

2. Copy the hook script:
   ```bash
   mkdir -p ~/.claude/hooks
   cp notify-done.sh ~/.claude/hooks/notify-done.sh
   chmod +x ~/.claude/hooks/notify-done.sh
   ```

3. Register the hook in `~/.claude/settings.json`:
   ```json
   {
     "hooks": {
       "Stop": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "bash ~/.claude/hooks/notify-done.sh",
               "async": true
             }
           ]
         }
       ]
     }
   }
   ```

4. Restart Claude Code.

---

## Uninstall

```bash
bash install.sh --uninstall
```

---

## How It Works

```
Claude finishes a task
        ↓
Stop hook fires → notify-done.sh receives JSON on stdin
        ↓
1. Extract session_id from stdin JSON
2. Find transcript: ~/.claude/projects/**/<session_id>.jsonl
3. Parse transcript:
   • Duration    → diff between first and last timestamp
   • Project     → decoded from the transcript directory name
   • Summary     → first sentence of Claude's last assistant message
        ↓
4. Detect terminal app:
   TERM_PROGRAM env var → process tree walk → osascript fallback
        ↓
5. Focus check (if NOTIFY_DONE_ONLY_WHEN_AWAY=1):
   Skip notification if the terminal is already frontmost
        ↓
6. Detect language from NOTIFY_DONE_LANG / $LANG / $LC_ALL
        ↓
7. Fire notification via terminal-notifier
   -activate <bundle-id>  ← makes it clickable to open the right window
        ↓
8. Optional: push to ntfy.sh topic for cross-device alert
```

### Supported terminals & editors

| App | Detection method | Bundle ID |
|---|---|---|
| Terminal.app | `$TERM_PROGRAM=Apple_Terminal` | `com.apple.Terminal` |
| iTerm2 | `$TERM_PROGRAM=iTerm.app` | `com.googlecode.iterm2` |
| Warp | `$TERM_PROGRAM=WarpTerminal` | `dev.warp.Warp-Stable` |
| VS Code | `$TERM_PROGRAM=vscode` + process tree | `com.microsoft.VSCode` |
| Cursor | `$TERM_PROGRAM=vscode` + process tree | `com.todesktop.230313mzl4w4u92` |
| Hyper | process tree | `co.zeit.hyper` |
| Alacritty | process tree | `org.alacritty` |
| kitty | process tree | `net.kovidgoyal.kitty` |
| Ghostty | process tree | `com.mitchellh.ghostty` |

---

## Configuration

All options are set as environment variables in `~/.claude/settings.json`:

```json
{
  "env": {
    "NOTIFY_DONE_LANG":           "zh",
    "NOTIFY_DONE_ONLY_WHEN_AWAY": "1",
    "NOTIFY_DONE_NTFY_TOPIC":     "my-claude-alerts"
  }
}
```

| Variable | Default | Description |
|---|---|---|
| `NOTIFY_DONE_LANG` | auto | Force language: `zh` or `en`. Auto-detects from `$LANG` if unset. |
| `NOTIFY_DONE_ONLY_WHEN_AWAY` | `0` | Set to `1` to suppress the notification when the originating terminal is already the frontmost app. |
| `NOTIFY_DONE_NTFY_TOPIC` | unset | Your [ntfy.sh](https://ntfy.sh) topic name. When set, also sends a push notification to that topic — great for phone alerts on long tasks. |

### Cross-device push with ntfy

1. Install the [ntfy app](https://ntfy.sh) on your phone.
2. Subscribe to a topic name of your choice (e.g. `claude-echo-alerts`).
3. Set the env var:
   ```json
   { "env": { "NOTIFY_DONE_NTFY_TOPIC": "claude-echo-alerts" } }
   ```

No account needed. The topic name acts as a shared secret — pick something non-obvious.

### Change the sound

Edit `notify-done.sh` and replace `Glass` with any macOS system sound:

```
Basso  Blow  Bottle  Frog  Funk  Hero  Morse
Ping   Pop   Purr    Sosumi  Submarine  Tink
```

### Add a new terminal

Add a new `case` entry in the `detect_bundle_id()` function. To find any app's bundle ID:
```bash
osascript -e 'id of app "YourApp"'
```

---

## Troubleshooting

**Notification doesn't appear**
- Check System Settings → Notifications → terminal-notifier is allowed
- Run manually: `echo '{}' | bash ~/.claude/hooks/notify-done.sh`

**Clicking the notification doesn't focus the right window**
- Verify `terminal-notifier` is installed: `which terminal-notifier`
- Check System Settings → Notifications → terminal-notifier has permission

**Summary is empty or generic**
- The transcript may not have been written yet at hook fire time (rare race condition)
- The hook falls back to the locale-appropriate generic string

**Hook not firing**
- Open `/hooks` in Claude Code or restart the session
- Validate settings.json: `jq empty ~/.claude/settings.json`

---

## Contributing

PRs welcome! Areas for improvement:
- Linux support (via `notify-send` / `libnotify`)
- More terminal app detection

---

## License

MIT

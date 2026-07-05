---
name: apple-ecosystem-automation
description: 'macOS Apple ecosystem automation: Notes, Reminders, Messages/iMessage/SMS, Find My, and GUI control workflows.'
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Apple Ecosystem Automation

Use this umbrella for macOS-native Apple app work: Notes, Reminders, Messages/iMessage/SMS, Find My, and desktop/UI automation around Apple apps. Prefer this single class-level skill over loading one narrow skill per app.

## Global rules

- macOS only. Verify app/tool availability before acting: `command -v memo remindctl imsg` and check permissions when needed.
- User-visible side effects require confirmation when they send messages, create reminders with alarms, delete/move notes, or expose location data.
- For agent-only durable facts, use memory/skills instead of Apple Notes. For scheduled agent alerts, use cronjob instead of Apple Reminders unless the user explicitly wants the Reminders app/iPhone sync.
- Use JSON/plain outputs for parsing when supported; avoid relying on human-formatted tables.

## Notes.app via `memo`

Use when the user asks to create, view, search, edit, organize, or export Apple Notes that sync through iCloud.

Prerequisites: Notes.app signed in; `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`; Automation permission for Notes.app.

Common commands:

```bash
memo notes                         # list notes
memo notes -f "Folder Name"        # folder filter
memo notes -s "query"              # fuzzy search
memo notes -a "Note Title"         # create quick note
memo notes -e                      # interactively edit
memo notes -d                      # interactively delete
memo notes -m                      # move note
memo notes -ex                     # export HTML/Markdown
```

Limitations: image/attachment-heavy notes may not edit cleanly; interactive operations need a PTY.

## Reminders.app via `remindctl`

Use when the user wants personal reminders/to-dos that sync to iPhone/iPad/Mac.

Prerequisites: `brew install steipete/tap/remindctl`; authorize with `remindctl authorize`; inspect with `remindctl status`.

Common commands:

```bash
remindctl today --json
remindctl overdue --json
remindctl list
remindctl list Work --create
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl complete 1 2 3
remindctl delete 4A83 --force
```

Due/alarm pitfall: `--due` is the actual due date/time; `--alarm` is the notification trigger. If the user asks for an early nudge, set both and verify with JSON fields `dueDate` and `alarmDate`.

```bash
remindctl add --title "Hairdresser" --due "2026-05-15 14:00" --alarm "2026-05-15 13:30"
remindctl today --json
```

## Messages/iMessage/SMS via `imsg`

Use when the user asks to read or send iMessages/SMS through macOS Messages.app.

Prerequisites: Messages.app signed in; `brew install steipete/tap/imsg`; Full Disk Access for the terminal; Automation permission for Messages.app.

Commands:

```bash
imsg chats --limit 10 --json
imsg history --chat-id 1 --limit 20 --attachments --json
imsg send --to "+14155551212" --text "Hello!"
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg
imsg send --to "+14155551212" --text "Hi" --service imessage
imsg watch --chat-id 1 --attachments
```

Safety: always confirm recipient and exact content before sending; verify attachment paths; do not bulk-message without explicit approval.

## Find My / AirTags / device locations

Use when the user asks where their Apple device, AirTag, keys, bag, pet, etc. is. There is no official CLI/API; use UI automation plus screenshots and vision.

Prerequisites: Find My app signed in; Screen Recording permission; optionally `brew install steipete/tap/peekaboo` for robust UI automation.

Basic flow:

```bash
osascript -e 'tell application "FindMy" to activate'
sleep 3
screencapture -w -o /tmp/findmy.png
```

Then analyze `/tmp/findmy.png` with vision. With Peekaboo:

```bash
peekaboo see --app "FindMy" --annotate --path /tmp/findmy-ui.png
peekaboo click --on B3 --app "FindMy"
peekaboo image --app "FindMy" --path /tmp/findmy-detail.png
```

Rules: keep Find My foregrounded for AirTag tracking; respect privacy; use cron only for user-approved ongoing tracking.

## macOS desktop / computer-use automation

Use when an Apple app has no CLI or the workflow requires UI interaction. Prefer non-invasive background computer-use tools when available; otherwise AppleScript/Peekaboo/screenshot loops.

Checklist:

1. Open/activate the target app with AppleScript.
2. Capture and annotate UI state.
3. Read visible state with vision rather than guessing pixel positions.
4. Click/type only after confirming the target element.
5. Re-capture to verify the side effect.

## Which path to choose

| User request | Preferred path |
|---|---|
| "Save this in Notes" | `memo` / Notes.app |
| "Remind me on my phone" | `remindctl` / Reminders.app |
| "Remind me in this chat later" | `cronjob`, not Reminders |
| "Text mom" | `imsg`, confirm recipient/content |
| "Where are my keys?" | Find My UI + screenshot + vision |
| "Click through this Mac app" | macOS computer-use / AppleScript / Peekaboo |
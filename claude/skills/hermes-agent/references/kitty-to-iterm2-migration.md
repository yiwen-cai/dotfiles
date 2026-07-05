# Migrating kitty config to iTerm2 on macOS

Use this when the user asks to move or migrate terminal configuration from kitty to iTerm2. Interpret phrases like "change my configure in kitty into iTerm2" as a concrete config migration request, not as another recommendation/comparison.

## Source files to inspect

- `~/.config/kitty/kitty.conf`
- `~/.config/kitty/current-theme.conf`
- optional backups or includes under `~/.config/kitty/`

Use file tools or terminal to read contents; do not guess font/theme/keybindings.

## iTerm2 target

Create an iTerm2 Dynamic Profile JSON under:

`~/Library/Application Support/iTerm2/DynamicProfiles/<name>.json`

A minimal dynamic profile has this shape:

```json
{
  "Profiles": [
    {
      "Name": "Hermes Kitty Migrated",
      "Guid": "stable-uuid-here",
      "Normal Font": "Maple Mono NF CN 18",
      "Non Ascii Font": "Maple Mono NF CN 18",
      "Use Non-ASCII Font": true,
      "Background Color": {"Color Space": "sRGB", "Red Component": 0.1, "Green Component": 0.1, "Blue Component": 0.1, "Alpha Component": 1.0}
    }
  ]
}
```

## Mapping notes

- kitty `font_family family="..."` + `font_size N` -> iTerm2 `Normal Font` and `Non Ascii Font` as `<family> <N>`.
- kitty Catppuccin files map directly:
  - `foreground` -> `Foreground Color`
  - `background` -> `Background Color`
  - `selection_background` -> `Selection Color`
  - `selection_foreground` -> `Selected Text Color`
  - `cursor` -> `Cursor Color`
  - `cursor_text_color` -> `Cursor Text Color`
  - `url_color` -> `Link Color`
  - `color0`..`color15` -> `Ansi 0 Color`..`Ansi 15 Color`
- Convert hex color `#RRGGBB` to iTerm2 sRGB components by dividing each channel by 255.
- kitty `macos_option_as_alt yes` -> iTerm2 `Left Option Key Sends: 2` and `Right Option Key Sends: 2`.
- kitty `cursor_blink_interval 0` -> iTerm2 `Blinking Cursor: false`.
- For Hermes/long-agent sessions, set `Unlimited Scrollback: true`, `Mouse Reporting: true`, and `Terminal Type: xterm-256color`.
- kitty `disable_ligatures cursor` has no exact iTerm2 equivalent; use `ASCII Ligatures: false` and `Non-ASCII Ligatures: false` if the user prefers no ligature surprises.

## Keybinding example

kitty:

```conf
map cmd+s send_text all \e:w\r
```

iTerm2 profile keyboard map:

```json
"Keyboard Map": {
  "0x73-0x100000": {
    "Action": 11,
    "Text": "0x1b 0x3a 0x77 0x0d"
  }
}
```

Here `0x73` is `s`, `0x100000` is Command, and action `11` sends hex code.

Be conservative with `alt+1`..`alt+9` tab switching: iTerm2's dynamic profile schema for menu/tab selection can vary by version. Preserve Option-as-Esc first, then ask or continue only if the user wants exact tab shortcuts.

## Verification

Run:

```bash
python3 -m json.tool "$HOME/Library/Application Support/iTerm2/DynamicProfiles/Hermes-Kitty-Migrated.json" >/dev/null && echo JSON_OK
open -a iTerm
```

Then tell the user to select the profile in iTerm2:

Settings / Preferences -> Profiles -> `Hermes Kitty Migrated` -> Other Actions -> Set as Default.

## Pitfalls

- Do not edit shell profile files for this task; they are protected in this user's environment.
- Do not try to make every kitty option exact. Some features have no iTerm2 equivalent: kitty powerline tab style, cursor trail, exact titlebar-only hiding, and exact background blur intensity.
- If a user says "configure" but context is terminal migration, treat it as configuration migration and inspect files immediately.

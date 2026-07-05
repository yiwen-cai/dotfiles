# Hermes Web UI scroll button placement notes

Use this reference when changing the `Start` / `End` jump buttons in the community Hermes WebUI transcript.

## User-facing behavior

For this user's preferred WebUI behavior:

- The transcript should not auto-follow sends, streaming output, completions, or layout changes.
- Opening/switching to an idle historical session should initially land at the bottom.
- The manual jump buttons should remain visible and clickable.
- `Start` should be visually near the top of the chat pane.
- `End` should be visually near the bottom of the chat pane.
- The two buttons must not overlap.

## Pitfall: buttons inside `.messages` scroll content

If the buttons are direct early children of `.messages` before `#msgInner`:

```html
<div class="messages" id="messages">
  <button id="jumpToSessionStartBtn" ...>...</button>
  <button id="scrollToBottomBtn" ...>...</button>
  <div class="messages-inner" id="msgInner"></div>
</div>
```

then both common CSS approaches are flawed:

1. `position:sticky` can make the controls overlap because both controls have early natural positions in the scroll container; `bottom:16px` on the early `End` child does not reliably pin it to the visible bottom.
2. `position:absolute` against `.messages` can place controls relative to the scroll content coordinate system, so a control may appear only when the user is near the top of the scroll content rather than remaining visible in the chat viewport.

This was observed in practice: sticky caused `Start` / `End` overlap, and absolute positioning while the buttons stayed inside `.messages` made the controls feel fixed to the content top rather than the visible pane.

## Robust placement: move controls out of scroll content

For fixed visible top and bottom controls inside the chat pane, use a sibling overlay pattern:

```html
<div id="mainChat" class="main-view">
  <div class="messages" id="messages">
    <div class="messages-inner" id="msgInner"></div>
  </div>
  <button id="jumpToSessionStartBtn" class="session-jump-btn session-jump-btn--start" onclick="jumpToSessionStart()">...</button>
  <button id="scrollToBottomBtn" class="scroll-to-bottom-btn" onclick="scrollToBottom()">...</button>
</div>
```

```css
.main-view{position:relative;}
.session-jump-btn,.scroll-to-bottom-btn{
  position:absolute;
  right:20px;
  display:flex!important;
  z-index:20;
}
.session-jump-btn--start{top:16px;}
.scroll-to-bottom-btn{bottom:16px;}
```

This keeps `.messages` responsible only for transcript scrolling, while the jump buttons are a stable overlay relative to the chat pane (`#mainChat` / `.main-view`). It avoids both sticky overlap and content-coordinate absolute positioning.

## Avoid mixing mental models

- `position:sticky` is appropriate for elements whose natural DOM position is meaningful inside scroll flow.
- `position:absolute` is appropriate for overlay controls, but only when the containing block is the chat viewport, not the scrolled content.
- Do not keep both top/bottom jump buttons as early children of `.messages` when the requirement is "always visible, one top and one bottom".

## Verification

Run JavaScript syntax checks after touching adjacent scroll logic:

```bash
node --check static/ui.js static/sessions.js static/messages.js static/terminal.js
```

Manual browser check:

1. Open a long historical session; it should initially land at the bottom.
2. Confirm `Start` appears near the upper-right of the chat pane.
3. Confirm `End` appears near the lower-right of the chat pane.
4. Confirm the buttons do not overlap at top, middle, or bottom scroll positions.
5. Confirm the controls remain visible when the transcript is scrolled away from the top.
6. Scroll manually during streaming; the transcript should not auto-follow unless the user clicks `End`.

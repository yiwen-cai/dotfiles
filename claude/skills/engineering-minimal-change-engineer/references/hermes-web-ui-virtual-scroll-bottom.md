# Hermes Web UI long-session scroll-to-bottom pitfall

Use this when a Vue/Naive UI chat transcript uses `vue-virtual-scroller` / `DynamicScroller` and a manual “scroll to bottom” button works for short sessions but appears inert in long sessions.

## Symptom

- A bottom button calls an existing `scrollToBottom()` method.
- Short conversations scroll correctly.
- Long conversations with many messages do not reach the real bottom, or the button appears to do nothing.
- Auto-scroll-to-bottom on initial session load can fail in the same way.

## Root cause

For virtualized lists, DOM metrics are not the full transcript metrics. In long sessions, code like this is unreliable:

```ts
scrollerRef.value?.scrollToBottom();
el.scrollTop = Math.max(0, el.scrollHeight - el.clientHeight);
```

`el.scrollHeight` may describe only the current virtual window/spacer state, not the full dynamic list after all item measurements settle. Also, `DynamicScroller.scrollToBottom()` performs asynchronous multi-frame positioning; immediately overriding `el.scrollTop` can fight the virtual scroller.

## Minimal fix pattern

When there are messages, use the virtual scroller API to target the final item directly:

```ts
function setScrollToBottomNow(): boolean {
  const el = getScrollerElement();
  markProgrammaticScroll();
  const lastIndex = props.messages.length - 1;
  if (lastIndex >= 0) {
    scrollerRef.value?.scrollToItem(lastIndex, { align: "end" });
  } else {
    scrollerRef.value?.scrollToBottom();
  }
  if (el) {
    if (lastIndex < 0) {
      el.scrollTop = Math.max(0, el.scrollHeight - el.clientHeight);
    }
    syncViewport();
    return true;
  }
  return false;
}
```

Keep the existing multi-frame scheduling around this function if the app already uses `requestAnimationFrame` to handle dynamic message measurement.

## Test pattern

Mock `DynamicScroller.scrollToItem` and assert bottom scrolling targets the last item:

```ts
expect(dynamicScrollToItemMock).toHaveBeenCalledWith(lastIndex, { align: "end" });
expect(dynamicScrollToBottomMock).not.toHaveBeenCalled();
```

Run the nearest checks, not the whole unrelated suite:

```bash
npx vue-tsc -b --pretty false
npx vitest run tests/client/virtual-message-list-scroll.test.ts tests/client/message-list-scroll-position.test.ts
```

## Scope discipline

This fix only changes the bottom positioning primitive. Do not combine it with broader changes such as removing session keys, rewriting auto-follow state, or redesigning scroll restoration unless the user explicitly asks for root-cause scroll behavior work.

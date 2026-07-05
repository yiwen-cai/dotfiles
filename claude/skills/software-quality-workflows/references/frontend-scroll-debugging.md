# 前端滚动/自动跟随调试参考

用于排查聊天界面、消息列表等组件中滚动行为异常的**系统化方法**。本参考聚焦于 Vue + VirtualScroller 生态中的常见陷阱。

## 1. 关键词搜索定位

先在项目中搜索以下关键词定位滚动相关组件：

```
scrollToBottom|autoScroll|scrollTo|auto-scroll|scrollBehavior|scrollTop
scroll|wheel|resize|isNearBottom|userDetached|keepBottom
DynamicScroller|vue-virtual-scroller|VirtualMessageList
```

这些词出现的位置通常就是滚动系统的核心组件，逐层阅读。

## 2. 追组件链：从外层到内层

典型的 Vue 消息列表滚动系统有三层：

```
页面视图 (MessageList.vue)           → 高级逻辑：监听数据变化、决定何时触发滚动
  └── VirtualMessageList.vue        → 核心引擎：scrollToBottom, handleScroll, rAF 循环
      └── DynamicScroller (第三方)   → DOM 渲染层：接管了实际滚动容器
```

**排查顺序**：
1. 先读页面视图（MessageList）—— 看所有 `watch`，理解什么状态下会触发滚动
2. 再读核心组件（VirtualMessageList）—— 看 `handleScroll`, `scrollToBottom`, `userDetachedFromBottom`, `handleResize`
3. 最后看第三方库行为（DynamicScroller）—— 理解它的内部渲染可能如何干扰

## 3. 常见陷阱清单

### 陷阱 1：`:key` 导致组件重建（P0）
```vue
<VirtualMessageList :key="chatStore.activeSessionId || 'chat-empty'" />
```
当 key 随 session ID 变化时，Vue **销毁重建**整个组件。重建后：
- 所有内部状态丢失（`scrollTop`, `userDetachedFromBottom`, `keepBottomUntil`, rAF 循环）
- `scrollTop` 重置为 0 → 跳到顶部
- 新组件在渲染后重新 `scrollToBottom`，但与 DynamicScroller 内部渲染时序竞争

**诊断**：在组件模板中查找 `:key="..."` 绑定。如果 key 绑定到会变化的值，检查它的必要性。

**修复**：去掉 `:key`，改为通过 prop 响应式更新；或确保 key 稳定。

### 陷阱 2：`userDetachedFromBottom` 阈值过于敏感
```ts
function handleScroll() {
  const delta = scrollTop.value - previousScrollTop;
  if (delta < -1) {                    // 哪怕 -1.5px 就 detach！
    userDetachedFromBottom = true;
  } else if (isNearBottom(32)) {       // 需要回到 32px 以内才 reattach
    userDetachedFromBottom = false;
  }
}
```

DynamicScroller 在 streaming 过程中内容高度变化可能导致 scrollTop 微跳动（-2px），用户**没操作**就被标记为 detach，streaming 内容不再自动跟随。

**诊断**：在组件中搜索 `delta` 阈值和 `userDetachedFromBottom` 赋值逻辑。

**修复**：提高阈值到 `-10` 到 `-20`，或结合 `isNearBottom` 综合判断：`if (delta < -20)`。

### 陷阱 3：`restoreViewportPosition` 与 `handleResize` 竞争
```ts
function restoreViewportPosition(snapshot, frames) {
  cancelBottomScroll();       // keepBottomUntil = 0
  userDetachedFromBottom = !snapshot.wasNearBottom;
  // 启动 rAF 循环设置 scrollTop
}
```
ResizeObserver 同时触发 `handleResize`：
```ts
function handleResize() {
  if (isNearBottom(64)) scheduleScrollToBottom(2);  // 抢走滚动控制权
}
```

恢复已保存的非底部位置时，ResizeObserver 可能先抢到滚动控制权，把 scrollTop 拉到最底部。

**诊断**：检查组件中是否同时有 `ResizeObserver` + `restoreViewportPosition`。查看它们是否共用了同样的 `keepBottomUntil`/`cancelBottomScroll` 状态。

**修复**：`restoreViewportPosition` 应设置一个 restore-in-progress 标记，`handleResize` 跳过冲突操作。

### 陷阱 4：多个 Watcher 在初始化时重复竞争
```ts
watch(activeSessionId, ...)                                // 触发 applyInitialSessionScroll
watch([activeSessionId, messages.length], ...)              // 再触发一次
watch(isLoadingMessages, ...)                              // 再触发一次
```

每个 watcher 都调用 `scrollToBottom` 或 `applyInitialSessionScroll`，各自启动 rAF 循环，相互覆盖滚动位置。

**诊断**：在页面视图组件中搜索所有 `watch`，看哪些可能同时触发滚动。检查 `pendingInitialScrollSessionId` 这样去重逻辑是否生效。

**修复**：统一一个初始化路径（如只保留 `activeSessionId` watcher），其他 watcher 返回 early。

### 陷阱 5：`handleWheel` 无条件 detach
```ts
function handleWheel(event: WheelEvent) {
  if (event.deltaY < -1) {
    userDetachedFromBottom = true;
    cancelBottomScroll();
  }
}
```
用户轻轻向上滚一下滚轮（`deltaY = -2`）就被 detach，即使只滚了 2px。

**诊断**：在组件中搜索 `handleWheel` 或 `@wheel`。

**修复**：只在大幅向上滚动时 detach（如 `deltaY < -50`），或使用累积阈值。

### 陷阱 6：内容溢出导致消息右移
markdown 渲染嵌套列表/代码块时 margin-left/padding-left 累积，消息容器没有 `overflow: hidden` / `max-width` 约束。

```scss
.virtual-row {
  max-width: 100%;
  // 但子元素（markdown 渲染的列表）可能溢出
}
```

**诊断**：检查消息容器 CSS 是否有 `overflow: hidden`，以及 markdown 渲染节点是否在嵌套时生成累积的 margin/padding。

**修复**：在消息容器上加 `overflow: hidden` + `max-width: 100%; word-break: break-word;`。

## 4. 调试技巧

### 在浏览器中验证
```ts
// 检查当前状态
vm.userDetachedFromBottom
vm.isNearBottom(64)
vm.shouldAutoFollowBottom(64)

// 手动触发滚动
vm.scrollToBottom({ frames: 5, keepAliveMs: 700 })

// 检查滚动位置同步
vm.syncViewport()
```

### 在组件中注入日志
```ts
// 在关键函数中加入临时日志
function handleScroll() {
  const previousScrollTop = scrollTop.value;
  syncViewport();
  console.log('[scroll]', { scrollTop: scrollTop.value, delta: scrollTop.value - previousScrollTop, programmatic: isProgrammaticScroll(), detached: userDetachedFromBottom });
  // ...
}
```

### 追踪 rAF 循环
```ts
// 检查是否有 rAF 循环在运行
bottomFrame !== null  // 表示有活跃的底部滚动循环
anchorFrame !== null  // 表示有活跃的定位滚动循环
viewportRestoreFrame !== null  // 表示有活跃的视口恢复循环
```

### 检查程序化滚动标记
```ts
// 最近的滚动操作是否是"程序化的"（不是用户触发的）
isProgrammaticScroll()  // 返回 true 表示在 markProgrammaticScroll 的有效期内
```

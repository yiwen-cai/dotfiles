# Hermes Web UI 聊天滚动按钮最小补丁参考

## 适用场景

用户已经遇到聊天列表自动滚动异常，但明确要求先添加一个可手动滚动到底部的按钮，而不是立即修复滚动状态机根因。

## 最小实现模式

1. 在主消息列表组件中定位现有消息列表容器和公开的 `scrollToBottom` 方法。
2. 在列表组件后方插入一个浮动按钮，点击时直接调用现有方法，例如：
   ```vue
   <NButton
     class="scroll-bottom-button"
     circle
     secondary
     type="primary"
     title="Scroll to bottom"
     @click="scrollToBottom({ frames: 5, keepAliveMs: 700 })"
   >
     <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
       <path d="M12 5v14" />
       <path d="m19 12-7 7-7-7" />
     </svg>
   </NButton>
   ```
3. 添加局部样式，固定在消息区域右下角：
   ```scss
   .scroll-bottom-button {
     position: absolute;
     right: 18px;
     bottom: 18px;
     z-index: 9;
     box-shadow: 0 10px 30px rgba(0, 0, 0, 0.16);
   }
   ```
4. 不要在同一个补丁里改自动滚动算法、`DynamicScroller` key、watcher 或用户 detachment 逻辑，除非用户明确要求继续修根因。

## 验证命令

- 如果仓库受 npm `omit=dev` 配置影响，先安装开发依赖：
  ```bash
  npm ci --include=dev --ignore-scripts --no-audit --no-fund
  ```
- Vue 类型检查：
  ```bash
  npx vue-tsc -b --pretty false
  ```
- 相关滚动单测：
  ```bash
  npx vitest run tests/client/message-list-scroll-position.test.ts tests/client/virtual-message-list-scroll.test.ts
  ```

## 注意事项

- 若项目没有现成 i18n key，临时 title 可用静态英文，避免界面显示未解析的 key。
- `npm ci` 可能触发 `prepare` 里的构建；为验证代码改动可加 `--ignore-scripts`，再单独运行类型检查和目标测试。

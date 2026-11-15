# Design System Master File — COK 控制台

> **LOGIC:** 构建/修改某个页面前，先看 `design-system/cok/pages/[page-name].md`。
> 存在则该文件的规则**覆盖**本 Master；不存在则严格遵守本文件。
>
> **落地位置:** `cok/resources/cok_webui.html`（单文件页面，内联 `<style>` + `<script>`）。
> 这份文件里的 token 与该文件 `:root` 里的变量**一一对应** —— 改样式先改那里，再回来同步本文件。

---

**Project:** COK 控制台（网页控制台 + 安卓 App 内嵌 WebView，共用同一个 HTML）
**Generated:** 2026-11-15
**Category:** RPA / Automation Dashboard（游戏自动化运维控制台）
**Design Dials:** Variance 4/10（Balanced）| Motion 3/10（Subtle）| Density 8/10（Dense / Dashboard）

---

## Global Rules

### Color Palette

暗色单主题（OLED 系）。**不提供浅色模式** —— 控制台多在夜里/后台跑，浅色反而刺眼。

| 角色 | 值 | CSS 变量 | 用途 |
|------|-----|----------|------|
| Background | `#0a0e16` | `--bg` | 页面底色 |
| Background 2 | `#0d121c` | `--bg2` | 输入框 / 面板底 |
| Surface | `#131a27` | `--surface` | 卡片 |
| Surface 2 | `#182130` | `--surface2` | 按钮 / hover 面 |
| Surface 3 | `#1f2939` | `--surface3` | 更高一层的面 |
| Line | `#242f42` | `--line` | 描边 |
| Line 2 | `#1a2333` | `--line2` | 分隔线（弱） |
| Foreground | `#e8eef7` | `--fg` | 主文字 |
| Foreground 2 | `#c3cddc` | `--fg2` | 次级文字 |
| Dim | `#8a97ac` | `--dim` | 辅助文字 |
| Dim 2 | `#8b98ad` | `--dim2` | 最弱文字（标签、占位） |
| Bg Deep | `#070a11` | `--bg-deep` | 日志 / 进度条槽（比 bg 更深的凹陷面） |
| Accent | `#4d8dff` | `--accent` | 主色：主按钮 / 焦点 / 选中 |
| Accent 2 | `#7aabff` | `--accent2` | 主色上的浅色变体 |
| Accent Dim | `rgba(77,141,255,.14)` | `--accent-dim` | 主色底 |
| Success | `#2fbf71` | `--ok` | 正常 / 运行中 |
| Warning | `#e0a53a` | `--warn` | 待处理 / 消耗警告 |
| Danger | `#f25f5c` | `--err` | 失败 / 危险操作 |

语义底色与前景色（状态标签、结果条、确认框共用，**不要再手写 rgba**）：

| 变量 | 值 | 用途 |
|------|-----|------|
| `--ok-dim` / `--warn-dim` / `--err-dim` | `rgba(..., .13)` | 状态底色 |
| `--ok-fg` / `--warn-fg` / `--err-fg` | `#63d99a` / `#e8bd6a` / `#ff9a95` | 状态文字 |

> ⚠️ **与数据集默认值的刻意偏离：** ui-ux-pro-max 的 Dark Mode 配方建议主色用
> 绿色 `#16A34A`（"running green"）。本项目**保留蓝色主色**，因为绿色在本项目里
> 已经承担"成功/运行中"的语义（`--ok`），主色和状态色撞色会让用户误判按钮含义。
> 绿色只出现在状态位（待办完成、连接正常）。

### Typography

- **中文正文:** `"PingFang SC", "SF Pro Text", -apple-system, "Microsoft YaHei", "Hiragino Sans GB"`
- **等宽（日志/ID）:** `ui-monospace, SFMono-Regular, Menlo`
- **字号标尺:** 正文 14px / 辅助 13px / 弱 12.5px / 卡片标题 14px / 概览数字 22px / 面包屑 16px
- **数字:** 关键数字统一 `font-variant-numeric: tabular-nums`（`b`、`.ov .vl`、`.stamina .v`）——
  刷新时数字不左右跳

> ⚠️ **刻意偏离：** 数据集推荐 Fira Code / Fira Sans。本项目**不引外部字体**：
> 控制台是本地/离线工具，Google Fonts 在国内不可靠且会拖慢首屏；中文正文用系统字体
> 反而更自然。字形家族保持一致（图标统一 Lucide）。

### Spacing Variables

*Density 8/10 — Dense / Dashboard*

| Token | 值 | 用途 |
|-------|-----|------|
| `--sp-1` | 4px | 图标与文字之间 |
| `--sp-2` | 8px | 小间距、控件内边距 |
| `--sp-3` | 12px | 标准内边距 |
| `--sp-4` | 16px | 区块间距 |
| `--sp-5` | 22px | 分节标题上边距 |
| `--sp-6` | 30px | 大留白 |

### Radius / Shadow / Motion

| Token | 值 | 用途 |
|-------|-----|------|
| `--r` | 14px | 卡片 |
| `--r-sm` | 9px | 按钮 / 输入框 |
| `--r-xs` | 7px | 小标签 |
| `--sh` | `0 1px 2px rgba(0,0,0,.3), 0 6px 20px -6px rgba(0,0,0,.45)` | 卡片 hover |
| `--sh-sm` | `0 1px 2px rgba(0,0,0,.28)` | 卡片常态 |
| `--ring` | `0 0 0 3px rgba(77,141,255,.24)` | 焦点环 |
| `--dur-1` | 160ms | 常规过渡（hover / 颜色） |
| `--dur-2` | 220ms | 大位移（toast / 抽屉） |
| `--ease` | `cubic-bezier(.2,.8,.2,1)` | 统一缓动 |

动效只保留两类：**状态反馈**（spinner、进度条）和**空间连续性**（toast 上浮、抽屉滑入）。
不做滚动揭示、不做入场编排 —— 数据密集界面里动效只制造噪音。

---

## Component Specs

### Buttons

```
主按钮   .primary      蓝色渐变 + 轻投影, 一个视图里只允许有一个
危险     .danger       红底红字, 用于不可撤销动作(删除账号)
幽灵危险 .ghost.danger 无底色但保留红色文字, 用于顶栏的"断开"(要能看出危险, 又不抢权重)
幽灵     .ghost        无边框, 次级动作
开启态   .on           绿色, 表示该开关已打开
```

- 尺寸：桌面 `padding 7px 13px`；≤860px 时 `min-height: 38px`，图标按钮 44×44
- 图标：统一 Lucide 内联 SVG，`currentColor`，15px（`.iconBtn` 16px，折叠 13px）
- **禁止**用 Unicode 符号（`⏻ ＋ － ✕`）当图标 —— 字形随平台变化，渲染发虚

### Cards

- 卡片标题行 `<h2>` 是一行 flex：`标题 + 副标题(.sub) + 汇总(.sumline, margin-left:auto) + 折叠按钮`
- 折叠按钮在 `<h2>` **内部**（不是 `.card` 的直接子元素）—— 选择器要写 `.card h2 .fold`
- 折叠：`.card.collapsed > *:not(h2) { display:none }`，图标旋转用 `transform` 不用换字符
- 状态徽章（`.sumline`）右对齐，超长省略

### Dialogs（确认框 / 输入框）

**禁止原生 `confirm()` / `prompt()`** —— 系统白底弹窗与深色控制台割裂，安卓 WebView 里尤其突兀，
且无法做焦点管理。

统一走 `askConfirm(msg, opts)` / `askPrompt(msg, value, opts)`：

```js
await askConfirm('确认开始打怪？\n3 队并行…', {kind:'warn', confirmText:'开始打怪'})
await askPrompt('给新账号起个名字', '', {title:'添加账号', placeholder:'留空则用角色名 / UID'})
```

| opts | 取值 | 说明 |
|------|------|------|
| `kind` | `'danger'` / `'warn'` / `'info'` / `'check'` | 决定图标与主按钮配色 |
| `confirmText` | 字符串 | 主按钮文案要写具体动作，不要写"确定" |
| `cancelText` | 字符串 | 默认"取消" |
| `title` | 字符串 | 标题 |
| `placeholder` / `selectAll` | — | 输入框专用 |

必做行为（已实现，别改坏）：
- Esc 关闭 = 取消；点遮罩关闭 = 取消；Enter 在输入框里 = 确认
- 打开时焦点落到主按钮（或输入框），Tab 焦点陷阱在弹窗内循环
- 关闭后焦点**归位**到触发元素
- 打开时给 `body` 加 `modal-open` 锁背景滚动
- 消息里的 `**文字**` 渲染成 `<b>`；其余一律转义（消息含账号名，不能当 HTML 注入）

### Toast

- `role="status" aria-live="polite" aria-atomic="true"` 在标签上（静态），不要动态加
- 3.8 秒自动消失，可手动关闭
- 语义色走 `border-left`（ok/warn/err），不整块染色
- 提示内容是**结果**，不是过程："已加入: 甲号、乙号"，不是"操作成功"

### Busy State

统一用 `busy(btn, label, fn)`：

- 按钮置 `disabled` + `aria-busy="true"`，内容换成 `<span class="spin">` + 文案
- 异常必须被吃掉并变成可见反馈（`toast('操作失败: '+msg,'err')`）—— 否则点了没反应，用户只能猜
- 文案写正在做什么："连接游戏服…"，不是"加载中"

### 徽章 / 计数

- Tab 角标（`.cnt`）用 `aria-label="3 项待办未处理"`，不要只播报裸数字
- 跳转标签（`.tag[data-jump]`）必须 `role="button" tabindex="0"`，并支持 Enter/Space 触发

---

## Style Guidelines

**Style:** Dark Mode (OLED) · **Pattern:** Real-Time / Operations Landing

- 实时性要诚实：标"实时"就必须有更新时间，过期状态要显示出来，不能藏错误状态
- 高频监控信息用**数字块**（`.ov`）横向排布，点数字直达能处理它的功能
- 侧栏固定两列：主导航（看板/功能）+ 快捷跳转（两列 chip 网格，12 项以上必须折叠或网格化，
  竖排会溢出被裁掉）

### Responsive

| 断点 | 变化 |
|------|------|
| ≤1024px | 侧栏 216px，间距收紧 |
| ≤860px | 侧栏变抽屉（汉堡按钮），卡片内边距收紧，触控目标 ≥40px，图标按钮 44×44 |
| ≤640px | 表格横向滚动，顶栏动作按钮独占一行，概览数字块 3 列 × 2 行（不横向滚动） |

**同一份 HTML 也跑在安卓 App 的 WebView 里** —— 窄屏不是"以后再说"，触控目标从一开始就按 ≥44px 设计。

---

## Anti-Patterns (Do NOT Use)

- ❌ 原生 `confirm()` / `prompt()`
- ❌ Unicode 符号当图标（`⏻ ＋ － ✕`）—— 一律 Lucide 内联 SVG
- ❌ Emoji 当图标
- ❌ 慢速仪表盘 / 装饰性图表 / 隐藏的错误状态
- ❌ 缺 `cursor:pointer` 的可点元素
- ❌ 隐形焦点态
- ❌ 瞬时状态变化（所有状态切换都要有 150–300ms 过渡）
- ❌ 固定 px 宽度的容器导致横向滚动
- ❌ 用 scale 做 hover 位移（会挤动布局）

---

## Pre-Delivery Checklist

交付前逐条过：

- [ ] 没有 Unicode/Emoji 当图标，全部 Lucide SVG
- [ ] 所有可点元素 `cursor:pointer`
- [ ] hover 状态有 150–300ms 过渡（用 `--dur-1` / `--dur-2`）
- [ ] 文字对比度 ≥4.5:1（`--dim2` 只用于非关键文字）
- [ ] 键盘导航焦点可见，Tab 能走遍所有控件
- [ ] `prefers-reduced-motion` 已处理
- [ ] 响应式过了 375 / 768 / 1024 / 1440
- [ ] 移动端无横向滚动
- [ ] 破坏性操作有确认框，且确认框是主题内的（不是系统弹窗）
- [ ] 异步操作有可见反馈（busy + toast）
- [ ] 反馈文案是具体结果，不是"操作成功"

---

## 本项目特有的工程约定

- **前端是单文件**：`cok/resources/cok_webui.html` 内联 `<style>` + `<script>`，不要拆包
- **改了 HTML 刷新就生效**：服务端的资源缓存已改成按文件 mtime 失效
  （`_resource_bytes` 比较 mtime），不用再重启进程
- **本地调前端**用 `python3 -m cok preview --port 8771 --no-token` —— 假数据、不连游戏服、不用登录
- **改配色/间距**：先改 `cok_webui.html` 的 `:root`，再同步本文件的表格，两边不能漂

---

## 对比度基线（WCAG 2.1 AA）

**规则：所有文字色都按最亮的表面 `--surface3` (#1f2939) 校验 ≥ 4.5:1。**
否则同一个 `--dim2` 在卡片里达标、在按钮上就跌破 AA —— 这是最容易漏的一类。

| 色 | on `--bg` | on `--surface` | on `--surface2` | on `--surface3` |
|----|-----------|----------------|-----------------|-----------------|
| `--fg` #e8eef7 | 16.56 | 14.94 | 13.86 | 12.55 |
| `--fg2` #c3cddc | 12.04 | 10.86 | 10.07 | 9.12 |
| `--dim` #8a97ac | 6.53 | 5.90 | 5.47 | 4.95 |
| `--dim2` #8b98ad | 6.61 | 5.97 | 5.54 | 5.01 |
| `--accent` #4d8dff | 6.04 | 5.45 | 5.06 | 4.58 |
| `--accent2` #7aabff | 8.37 | 7.55 | 7.00 | 6.34 |
| `--ok` #2fbf71 | 8.10 | 7.31 | 6.78 | 6.14 |
| `--warn` #e0a53a | 8.84 | 7.98 | 7.40 | 6.70 |
| `--err` #f25f5c | 6.04 | 5.45 | 5.06 | 4.58 |

> 曾经 `--dim2` 是 `#647189`（on `--surface` 只有 3.54:1，不达 AA），`--err` 是 `#ef5350`
> （on `--surface3` 4.20:1）。改色时用上面的脚本重算，别凭感觉调。

---

## 字号令牌（`--fs-*`）

| 变量 | 值 | 用途 |
|------|-----|------|
| `--fs-body` | 14px | `body` 基准 |
| `--fs2xs` | 11px | 角标 / pip / 极短标签 |
| `--fs-xs` | 11.5px | 标签、分区标题、`.sub` |
| `--fs-sm` | 12px | 次要说明、按钮 |
| `--fs-md` | 12.5px | 略强调的说明 |
| `--fs-base` | 13px | 正文（列表、键值对） |
| `--fs-lg` | 14px | 卡片标题、数值型取值 |
| `--fs-xl` | 15px | 强调标题 |
| `--fs-2xl` | 18px | 区块标题 |
| `--fs-3xl` | 21px | 概览数字 |

**任何地方都不许再写裸 px 字号**（`<style>` 里的 `font-size:12px` 一律换成 `var(--fs-sm)`）。
校验方法：枚举 `document.styleSheets` 里所有 `r.style.fontSize`，含 `px` 的就是漏网的。

---

## 卡片标题结构（两段式）

```html
<div class="hd">
  <div class="hd-t"><h2>标题</h2><span class="sub">一句话说明</span></div>
  <div class="hdTools"><span class="sumline" id="sumX"></span><button class="fold">－</button></div>
</div>
```

- `.hd-t` 只放"这是什么"，控件一律进 `.hdTools` —— 以前控件挤在 `h2` 里，
  标题行会被挤成两截、还会把 `.sub` 说明顶出去。
- `.fold`（折叠按钮）**常驻可见**（`opacity:.6`），不靠 hover 才出现 ——
  触屏和键盘用户没有 hover。
- 折叠态：`display:none` 只作用于 `.card.collapsed > *:not(.hd)`，`.hd` 整体保留
  （折叠按钮在里面，不然折叠后就没法展开了）。
- 手机上 `.fold` 放大到 34×34（桌面 26×26）。

---

## 断点

| 宽度 | 布局 |
|------|------|
| ≤600px | 顶栏动作按钮各占 1/3 独占一行；概览条 3 列 × 2 行 + 「更多」 |
| ≤760px | 安卓端：侧栏 → 底部导航（见 `android-app/mobile-console.css`） |
| ≤860px | 侧栏 → 抽屉，`.onlyDesk` 隐藏 |
| ≤1180px | 概览条降到 3 列 |
| ≥1181px | 概览条 6 列（首屏 6 个主项） |

## 动效

- 卡片入场：`cardIn .22s`（`opacity` + `translate`，不用 `transform` 以免和 `.ov:hover` 冲突）
- hover 抬升：`translate:0 -1px`（只 1px，列表密度高，抬多了会晃）
- `prefers-reduced-motion: reduce` 时全部关掉

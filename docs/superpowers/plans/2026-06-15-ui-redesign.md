# Sorting Hat UI 重设计 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完整重写 `web/index.html`，将现有暗金哈利波特风格升级为烛光哥特仪式感 UI 系统，字体升级为 Noto Serif SC + Cinzel 组合，不改变任何 JS 功能逻辑。

**Architecture:** 单文件 HTML，CSS 内联在 `<style>`，JS 保持原有逻辑不变，只替换所有样式定义和 HTML 结构类名。分五个任务逐层构建：CSS 变量与基础样式 → 组件样式 → 动效 → 四页 HTML 结构 → 验收检查。

**Tech Stack:** 纯 HTML/CSS/JS，Google Fonts CDN（Cinzel Decorative、Cinzel、Noto Serif SC、IM Fell English），零外部依赖。

---

## 文件

- **修改：** `web/index.html` — 完整重写，保留原有 JS 逻辑，替换全部 CSS 和 HTML 结构

---

### Task 1：CSS 变量、重置与页面基础样式

**Files:**
- Modify: `web/index.html` — 替换 `<head>` 字体链接 + `<style>` 块开头的变量与基础样式

- [ ] **Step 1：替换 `<head>` 中的字体链接**

将原有的：
```html
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
```
替换为：
```html
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600&family=Noto+Serif+SC:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
```

- [ ] **Step 2：替换 `:root` CSS 变量块**

找到 `<style>` 中的 `:root { ... }` 块，完整替换为：
```css
:root {
  --bg-darkest:     #080705;
  --bg-dark:        #100e0b;
  --bg-card:        #1a1710;
  --bg-elevated:    #221e15;

  --gold-bright:    #f2c94c;
  --gold-primary:   #c9a84c;
  --gold-muted:     #8b6e20;
  --gold-dim:       #4a3a10;

  --text-primary:   #f0e8cc;
  --text-secondary: #b8a87a;
  --text-muted:     #7a6840;

  --teal:           #5ecfcf;
  --purple:         #9b7fd4;
  --green:          #6bbf7a;
  --red-soft:       #c97070;

  --border-gold:    rgba(201, 168, 76, 0.35);
  --border-dim:     rgba(201, 168, 76, 0.12);
  --glow-gold:      rgba(201, 168, 76, 0.55);
  --glow-teal:      rgba(94, 207, 207, 0.4);
}
```

- [ ] **Step 3：替换 `* { }` 重置和 `body { }` 样式**

找到 `* { box-sizing: border-box; ... }` 和 `body { ... }` 块，替换为：
```css
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background-color: var(--bg-darkest);
  background-image:
    radial-gradient(ellipse 80% 40% at 50% -5%,
      rgba(201, 168, 76, 0.10) 0%, transparent 70%),
    radial-gradient(ellipse 100% 50% at 50% 110%,
      rgba(0, 0, 0, 0.6) 0%, transparent 70%);
  color: var(--text-primary);
  font-family: 'Noto Serif SC', 'Cormorant Garamond', serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1rem 4rem;
}
```

- [ ] **Step 4：在浏览器中打开 `http://localhost:7432` 确认页面背景变为极深暗色 + 顶部有淡金色光晕**

运行：`python3 web/server.py` 然后访问 `http://localhost:7432`
预期：页面背景是近黑色（#080705），顶部有非常微弱的暖金色光晕。

- [ ] **Step 5：Commit**

```bash
git init  # 如果还没有 git repo，先初始化
git add web/index.html
git commit -m "style: update CSS variables and body background to candlelight gothic"
```

---

### Task 2：标题区、分隔线、主卡片组件样式

**Files:**
- Modify: `web/index.html` — 替换 `.hero`、`h1`、`.subtitle`、`.divider`、`.card` 的 CSS

- [ ] **Step 1：替换 `.hero` 和标题相关样式**

找到 `/* ── 标题区 ── */` 注释区域，将 `.hero`、`.hat-emoji`、`h1`、`.subtitle`、`.divider` 的样式完整替换为：
```css
.hero {
  text-align: center;
  margin-bottom: 2.5rem;
  animation: fadeDown 1s ease both;
}

.hat-emoji {
  font-size: 5rem;
  display: block;
  margin-bottom: 0.5rem;
  filter: drop-shadow(0 0 20px rgba(201, 168, 76, 0.75));
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-10px); }
}

h1 {
  font-family: 'Cinzel Decorative', serif;
  font-size: clamp(1.8rem, 4vw, 3rem);
  color: var(--gold-primary);
  letter-spacing: 0.08em;
  text-shadow: 0 0 10px var(--gold-primary), 0 0 30px rgba(201, 168, 76, 0.35);
  line-height: 1.3;
}

.subtitle {
  font-family: 'Cinzel', serif;
  font-size: 0.82rem;
  color: var(--text-secondary);
  letter-spacing: 0.22em;
  margin-top: 0.6rem;
  text-transform: uppercase;
}

.divider {
  width: 300px;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--gold-primary), transparent);
  margin: 1.2rem auto;
  opacity: 0.5;
}
```

- [ ] **Step 2：替换主卡片 `.card` 样式**

找到 `/* ── 卡片 ── */` 注释区域，将 `.card`、`.card::before`、`.card::after` 完整替换为：
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-gold);
  border-radius: 4px;
  box-shadow:
    0 0 40px rgba(201, 168, 76, 0.08),
    0 0 80px rgba(0, 0, 0, 0.5),
    inset 0 0 80px rgba(0, 0, 0, 0.3);
  padding: 2.5rem 3rem;
  width: 100%;
  max-width: 700px;
  position: relative;
  animation: fadeUp 0.6s ease both;
}

.card::before, .card::after {
  content: '✦';
  position: absolute;
  color: var(--gold-muted);
  font-size: 0.65rem;
  opacity: 0.7;
}
.card::before { top: 12px; left: 16px; }
.card::after  { bottom: 12px; right: 16px; }
```

- [ ] **Step 3：刷新浏览器，确认主卡片显示为深色背景 + 金色细边框 + 四角有小星形装饰**

预期：卡片边框可见，四角各有一个极小的 `✦` 符号，卡片内部有微弱的内阴影。

- [ ] **Step 4：Commit**

```bash
git add web/index.html
git commit -m "style: update hero, divider, and main card styles"
```

---

### Task 3：欢迎页组件样式（版本卡片、确认按钮、欢迎文案）

**Files:**
- Modify: `web/index.html` — 替换欢迎页相关 CSS

- [ ] **Step 1：替换 `.welcome-text` 样式**

找到 `/* ── 欢迎页 ── */` 注释区域，将 `.welcome-text` 替换为：
```css
.welcome-text {
  font-family: 'IM Fell English', serif;
  font-size: 1.05rem;
  line-height: 1.95;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.welcome-text em {
  color: var(--gold-primary);
  font-style: normal;
}
```

- [ ] **Step 2：替换版本选择卡片样式**

找到 `.version-btns`、`.version-card` 等相关样式，完整替换为：
```css
.version-btns {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.version-card {
  flex: 1;
  min-width: 200px;
  background: transparent;
  border: 1px solid var(--border-dim);
  border-radius: 3px;
  padding: 1.2rem 1.4rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.version-card:hover {
  background: rgba(201, 168, 76, 0.06);
  border-color: var(--border-gold);
}

.version-card.selected {
  background: rgba(201, 168, 76, 0.12);
  border-color: var(--gold-primary);
  box-shadow: 0 0 20px rgba(201, 168, 76, 0.18);
}

.version-card .version-title {
  font-family: 'Cinzel', serif;
  font-size: 0.95rem;
  letter-spacing: 0.08em;
  color: var(--text-primary);
  margin-bottom: 0.3rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.version-card.selected .version-title {
  color: var(--gold-bright);
  text-shadow: 0 0 8px var(--gold-primary);
}

.version-card .version-meta {
  font-family: 'Cinzel', serif;
  font-size: 0.68rem;
  letter-spacing: 0.15em;
  color: var(--text-muted);
  margin-bottom: 0.6rem;
}

.version-card .version-desc {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.88rem;
  line-height: 1.65;
  color: var(--text-secondary);
}

.version-card.selected .version-desc {
  color: var(--text-primary);
}
```

- [ ] **Step 3：替换确认按钮 `.btn-confirm` 样式**

```css
.btn-confirm {
  width: 100%;
  margin-top: 1.2rem;
  background: rgba(201, 168, 76, 0.04);
  border: 1px solid var(--border-dim);
  color: var(--text-muted);
  font-family: 'Cinzel', serif;
  font-size: 0.88rem;
  letter-spacing: 0.16em;
  padding: 0.9rem;
  border-radius: 2px;
  cursor: not-allowed;
  transition: all 0.3s ease;
}

.btn-confirm.ready {
  background: rgba(201, 168, 76, 0.12);
  border-color: var(--gold-primary);
  color: var(--gold-bright);
  cursor: pointer;
}

.btn-confirm.ready:hover {
  background: rgba(201, 168, 76, 0.24);
  box-shadow: 0 0 20px var(--glow-gold);
  text-shadow: 0 0 10px var(--gold-primary);
}
```

- [ ] **Step 4：在浏览器中验证欢迎页**

刷新 `http://localhost:7432`，检查：
- 欢迎文案字体为衬线体，`em` 包裹的文字显示为金色
- 两个版本卡片并排，点击其中一个后边框变亮、背景变暖
- 未选版本时确认按钮为暗淡不可点击状态；选中版本后按钮变亮可点击
- 窄屏（≤480px）时版本卡片竖向排列

- [ ] **Step 5：Commit**

```bash
git add web/index.html
git commit -m "style: update welcome page components - version cards and confirm button"
```

---

### Task 4：问卷页组件样式（进度条、题目、选项、导航按钮、输入框）

**Files:**
- Modify: `web/index.html` — 替换问卷页所有组件 CSS

- [ ] **Step 1：替换进度条样式**

找到 `/* ── 进度条 ── */` 区域，完整替换为：
```css
.progress-wrap { margin-bottom: 1.8rem; }

.progress-label {
  font-family: 'Cinzel', serif;
  font-size: 0.72rem;
  letter-spacing: 0.15em;
  color: var(--text-muted);
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.progress-bar-bg {
  height: 3px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(to right, var(--gold-muted), var(--gold-bright));
  border-radius: 2px;
  width: 0%;
  transition: width 0.5s ease;
  box-shadow: 0 0 8px var(--glow-gold);
}
```

注意：原代码用 `transform: scaleX()` 控制进度条，**需要同步修改 JS** — 找到 `renderQuestion()` 函数中的：
```js
document.getElementById('progressFill').style.transform = 'scaleX(' + (pct / 100) + ')';
```
替换为：
```js
document.getElementById('progressFill').style.width = pct + '%';
```

同时删除原 CSS 中 `.progress-bar-fill` 的 `transform-origin: left; transform: scaleX(0);` 属性。

- [ ] **Step 2：替换题目文字样式**

找到 `/* ── 题目 ── */` 区域，完整替换为：
```css
.phase-label {
  font-family: 'Cinzel', serif;
  font-size: 0.68rem;
  letter-spacing: 0.25em;
  color: var(--purple);
  text-transform: uppercase;
  margin-bottom: 0.4rem;
}

.question-num {
  font-family: 'Cinzel', serif;
  font-size: 0.75rem;
  color: var(--gold-primary);
  margin-bottom: 0.6rem;
  letter-spacing: 0.1em;
}

.question-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.15rem;
  line-height: 1.8;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}
```

- [ ] **Step 3：替换选项按钮样式**

找到 `/* ── 选项 ── */` 区域，完整替换为：
```css
.options { display: flex; flex-direction: column; gap: 0.65rem; }

.option-btn {
  background: rgba(201, 168, 76, 0.03);
  border: 1px solid var(--border-dim);
  color: var(--text-secondary);
  font-family: 'Noto Serif SC', serif;
  font-size: 1rem;
  line-height: 1.65;
  padding: 0.85rem 1.1rem;
  cursor: pointer;
  border-radius: 2px;
  text-align: left;
  transition: all 0.25s ease;
  display: flex;
  gap: 0.8rem;
  align-items: flex-start;
}

.option-btn:hover {
  background: rgba(201, 168, 76, 0.10);
  border-color: var(--gold-primary);
  color: var(--text-primary);
  box-shadow: 0 0 10px rgba(201, 168, 76, 0.15);
}

.option-btn.selected {
  background: rgba(201, 168, 76, 0.18);
  border-color: var(--gold-bright);
  color: var(--gold-bright);
  box-shadow: 0 0 16px rgba(201, 168, 76, 0.30);
}

.option-letter {
  font-family: 'Cinzel', serif;
  font-size: 0.78rem;
  color: var(--teal);
  min-width: 1.4rem;
  padding-top: 0.15rem;
  flex-shrink: 0;
}

.option-btn.selected .option-letter { color: var(--gold-bright); }
```

- [ ] **Step 4：替换开放题输入框样式**

找到 `/* ── 开放题输入框 ── */` 区域，完整替换为：
```css
.open-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-gold);
  border-radius: 2px;
  color: var(--text-primary);
  font-family: 'Noto Serif SC', serif;
  font-size: 1rem;
  padding: 0.85rem 1rem;
  outline: none;
  transition: all 0.3s ease;
  resize: vertical;
  min-height: 72px;
}

.open-input:focus {
  border-color: var(--gold-primary);
  box-shadow: 0 0 12px rgba(201, 168, 76, 0.18);
}

.skip-hint {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.83rem;
  font-style: italic;
  color: var(--text-muted);
  margin-top: 0.5rem;
}
```

- [ ] **Step 5：替换导航按钮样式**

找到 `/* ── 导航按钮 ── */` 区域，完整替换为：
```css
.nav-btns {
  display: flex;
  justify-content: space-between;
  margin-top: 1.8rem;
  gap: 1rem;
}

.btn-next {
  background: rgba(201, 168, 76, 0.12);
  border: 1px solid var(--gold-primary);
  color: var(--gold-bright);
  font-family: 'Cinzel', serif;
  font-size: 0.85rem;
  letter-spacing: 0.12em;
  padding: 0.7rem 2rem;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.btn-next:hover {
  background: rgba(201, 168, 76, 0.24);
  box-shadow: 0 0 18px var(--glow-gold);
  text-shadow: 0 0 8px var(--gold-primary);
}

.btn-back {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.10);
  color: var(--text-muted);
  font-family: 'Cinzel', serif;
  font-size: 0.85rem;
  letter-spacing: 0.1em;
  padding: 0.7rem 1.5rem;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.25s ease;
}

.btn-back:hover {
  color: var(--text-secondary);
  border-color: var(--border-gold);
}
```

- [ ] **Step 6：在浏览器中进入问卷页验证**

点击确认开始分院进入问卷，检查：
- 进度条为 3px 高的细线，金色渐变填充，有微弱发光
- Phase 标签为紫色 Cinzel 字体
- 题号为金色
- 题目文字为 Noto Serif SC
- 选项按钮悬停时边框变亮，点击后变为金色选中态
- 选项字母 A/B/C/D 为青绿色（`--teal`），选中后变金色
- 导航按钮样式正确

- [ ] **Step 7：Commit**

```bash
git add web/index.html
git commit -m "style: update quiz page components - progress bar, options, navigation"
```

---

### Task 5：结果页、生成中页、公用按钮、动效 keyframes 和响应式

**Files:**
- Modify: `web/index.html` — 替换结果页、生成中、通用按钮、动效和响应式 CSS

- [ ] **Step 1：替换结果页样式**

找到 `/* ── 结果页 ── */` 区域，完整替换为：
```css
.result-section { margin-bottom: 1.5rem; }

.result-section h2 {
  font-family: 'Cinzel', serif;
  font-size: 0.78rem;
  letter-spacing: 0.22em;
  color: var(--gold-primary);
  text-transform: uppercase;
  margin-bottom: 0.8rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(201, 168, 76, 0.2);
}

.result-section p {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.98rem;
  line-height: 1.85;
  color: var(--text-secondary);
}

.result-section p strong {
  color: var(--text-primary);
  font-weight: 600;
}

.success-msg {
  background: rgba(201, 168, 76, 0.08);
  border: 1px solid rgba(201, 168, 76, 0.3);
  border-radius: 2px;
  padding: 1rem 1.4rem;
  font-family: 'Cinzel', serif;
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  color: var(--gold-primary);
  text-align: center;
  margin-top: 1.5rem;
  animation: pulse-glow 2s ease-in-out infinite;
}

.error-msg {
  background: rgba(180, 60, 60, 0.10);
  border: 1px solid rgba(180, 60, 60, 0.40);
  border-radius: 2px;
  padding: 0.8rem 1.2rem;
  font-family: 'Noto Serif SC', serif;
  font-size: 0.93rem;
  color: var(--red-soft);
  margin-top: 1rem;
}
```

- [ ] **Step 2：替换生成中页样式**

找到 `/* ── 加载动画 ── */` 区域，完整替换为：
```css
.generating {
  text-align: center;
  padding: 3rem 0;
}

.generating p {
  font-family: 'Noto Serif SC', serif;
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0.6rem 0;
  opacity: 0;
  animation: fadeIn 0.5s ease forwards;
}
.generating p:nth-child(1) { animation-delay: 0.2s; }
.generating p:nth-child(2) { animation-delay: 1.0s; }
.generating p:nth-child(3) { animation-delay: 1.8s; }
.generating p:nth-child(4) { animation-delay: 2.6s; }
```

- [ ] **Step 3：替换通用主次按钮样式**

找到 `/* ── 按钮 ── */` 区域（`.btn-primary` 和 `.btn-secondary`），完整替换为：
```css
.btn-primary {
  flex: 1;
  min-width: 160px;
  background: rgba(201, 168, 76, 0.12);
  border: 1px solid var(--gold-primary);
  color: var(--gold-bright);
  font-family: 'Cinzel', serif;
  font-size: 0.88rem;
  letter-spacing: 0.12em;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.3s ease;
  text-align: center;
}

.btn-primary:hover {
  background: rgba(201, 168, 76, 0.24);
  box-shadow: 0 0 20px var(--glow-gold);
  text-shadow: 0 0 10px var(--gold-primary);
}

.btn-secondary {
  flex: 1;
  min-width: 160px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.10);
  color: var(--text-muted);
  font-family: 'Cinzel', serif;
  font-size: 0.88rem;
  letter-spacing: 0.1em;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.25s ease;
  text-align: center;
}

.btn-secondary:hover {
  border-color: var(--border-gold);
  color: var(--text-secondary);
}
```

- [ ] **Step 4：替换所有 `@keyframes` 动效定义**

找到现有的 `@keyframes fadeIn`、`@keyframes fadeUp`、`@keyframes fadeDown`、`@keyframes pulse`，全部替换为：
```css
@keyframes fadeIn {
  to { opacity: 1; }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-12px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 8px rgba(201, 168, 76, 0.15); }
  50%       { box-shadow: 0 0 24px rgba(201, 168, 76, 0.40); }
}
```

注意：原来的 `@keyframes pulse` 已改名为 `pulse-glow`，`.success-msg` 中的 `animation: pulse` 要同步改为 `animation: pulse-glow 2s ease-in-out infinite`（在 Step 1 已处理）。

- [ ] **Step 5：在 `</style>` 前添加响应式规则**

```css
@media (max-width: 560px) {
  .card { padding: 1.8rem 1.4rem; }
  .version-btns { flex-direction: column; }
  .nav-btns { flex-direction: column-reverse; }
  .btn-next, .btn-back { width: 100%; text-align: center; }
  .btn-primary, .btn-secondary { min-width: unset; }
}
```

- [ ] **Step 6：确认 `.hidden` 工具类存在**

检查 CSS 中是否有：
```css
.hidden { display: none !important; }
```
如果没有，添加到样式末尾。

- [ ] **Step 7：替换 `.badge` 样式（版本徽章）**

找到 `.badge` 样式，替换为：
```css
.badge {
  display: inline-block;
  font-family: 'Cinzel', serif;
  font-size: 0.62rem;
  letter-spacing: 0.15em;
  color: var(--gold-muted);
  border: 1px solid var(--gold-muted);
  padding: 0.12rem 0.45rem;
  border-radius: 2px;
  margin-left: 0.5rem;
  vertical-align: middle;
  opacity: 0.65;
}
```

- [ ] **Step 8：完整功能回归测试**

打开 `http://localhost:7432`，走一遍完整流程：
1. **欢迎页**：点击「简易版」→ 版本卡片变亮 → 确认按钮激活 → 点击确认
2. **问卷页**：进度条随题目前进，选项点击有选中态，开放题可输入，上一题/下一题导航正常
3. **生成中**：四行文字逐行出现（每行间隔约 0.8s）
4. **结果页**：人设文字正确显示，`**粗体**` 渲染为 `<strong>` 加粗，保存按钮可点击，点击后出现成功或错误提示
5. **重新分院**：点击「重新分院」回到欢迎页

- [ ] **Step 9：Commit**

```bash
git add web/index.html
git commit -m "style: complete UI redesign - result page, generating page, animations, responsive"
```

---

## 自检（Spec Coverage）

| 设计规范项 | 覆盖的 Task |
|---|---|
| CSS 变量色板 | Task 1 Step 2 |
| 烛光双层 radial-gradient 背景 | Task 1 Step 3 |
| 字体链接更新（Noto Serif SC） | Task 1 Step 1 |
| 标题区 fadeDown 入场动画 | Task 2 Step 1 |
| 帽子浮动动画 float | Task 2 Step 1 |
| 主卡片四角 ✦ 装饰 | Task 2 Step 2 |
| 欢迎文案 IM Fell English | Task 3 Step 1 |
| 版本卡片三态 | Task 3 Step 2 |
| 确认按钮禁用 / 激活态 | Task 3 Step 3 |
| 进度条 width 过渡（非 scaleX） | Task 4 Step 1 |
| Phase 标签紫色 Cinzel | Task 4 Step 2 |
| 题目正文 Noto Serif SC | Task 4 Step 2 |
| 选项按钮三态 + 字母青绿色 | Task 4 Step 3 |
| 开放输入框 Noto Serif SC | Task 4 Step 4 |
| 导航按钮主次样式 | Task 4 Step 5 |
| 结果区块 Cinzel 标签 + 金色下划线 | Task 5 Step 1 |
| 成功提示 pulse-glow 动画 | Task 5 Step 1 |
| 生成中页逐行 fadeIn | Task 5 Step 2 |
| 通用 btn-primary / btn-secondary | Task 5 Step 3 |
| keyframes 全套（fadeIn/Up/Down/pulse-glow） | Task 5 Step 4 |
| 响应式 ≤560px | Task 5 Step 5 |

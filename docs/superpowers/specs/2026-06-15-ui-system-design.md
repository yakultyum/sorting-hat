# Sorting Hat · UI 系统设计文档

**日期：** 2026-06-15
**状态：** 已确认，待实现
**范围：** 完整重新设计 `web/index.html`，不扩展 PRD 功能范围

---

## 一、设计决策摘要

| 维度 | 决策 |
|---|---|
| 设计方向 | 暗金仪式感（A 方向） |
| 空间氛围 | 烛光哥特（暖金烛光 + 粒子飘散 + 装饰角花） |
| 字体方案 | Noto Serif SC（中文正文）+ Cinzel / Cinzel Decorative（英文标题） |
| 功能范围 | 问卷流程 + 结果展示，一套人设，不做历史记录或多人设 |
| 页面数量 | 4 个状态：欢迎页、问卷页、生成中、结果页 |

---

## 二、色彩系统

### 基础色板

```css
:root {
  /* 背景层级 */
  --bg-darkest:   #080705;   /* 最深背景，页面底色 */
  --bg-dark:      #100e0b;   /* 卡片外区域 */
  --bg-card:      #1a1710;   /* 主卡片背景 */
  --bg-elevated:  #221e15;   /* 悬停态、选中态卡片 */

  /* 金色系 */
  --gold-bright:  #f2c94c;   /* 高亮文字、激活状态 */
  --gold-primary: #c9a84c;   /* 主要金色，边框、标题 */
  --gold-muted:   #8b6e20;   /* 次要金色，装饰元素 */
  --gold-dim:     #4a3a10;   /* 极暗金，微妙背景纹理 */

  /* 文字 */
  --text-primary:   #f0e8cc;  /* 主文字，题目正文 */
  --text-secondary: #b8a87a;  /* 次要文字，描述、说明 */
  --text-muted:     #7a6840;  /* 占位、禁用 */

  /* 强调色 */
  --teal:         #5ecfcf;   /* 选项字母、进度条 */
  --purple:       #9b7fd4;   /* Phase 标签 */
  --green:        #6bbf7a;   /* 成功状态 */
  --red-soft:     #c97070;   /* 错误状态 */

  /* 边框 */
  --border-gold:  rgba(201, 168, 76, 0.35);
  --border-dim:   rgba(201, 168, 76, 0.12);

  /* 发光 */
  --glow-gold:    rgba(201, 168, 76, 0.55);
  --glow-teal:    rgba(94, 207, 207, 0.4);
}
```

### 背景处理

页面背景使用多层叠加，营造烛光氛围：

```css
body {
  background-color: var(--bg-darkest);
  background-image:
    /* 顶部烛光晕 */
    radial-gradient(ellipse 80% 40% at 50% -5%,
      rgba(201, 168, 76, 0.10) 0%, transparent 70%),
    /* 底部暗角 */
    radial-gradient(ellipse 100% 50% at 50% 110%,
      rgba(0, 0, 0, 0.6) 0%, transparent 70%);
}
```

---

## 三、字体系统

### 字体加载

```html
<link href="https://fonts.googleapis.com/css2?
  family=Cinzel+Decorative:wght@400;700&
  family=Cinzel:wght@400;600&
  family=Noto+Serif+SC:wght@400;600&
  family=IM+Fell+English:ital@0;1
  &display=swap" rel="stylesheet">
```

### 字体分工

| 用途 | 字体 | 字重 | 说明 |
|---|---|---|---|
| 主标题 Sorting Hat | Cinzel Decorative | 700 | 英文专有名词，仪式感最强 |
| Phase 标签、按钮、编号 | Cinzel | 400/600 | 英文结构性文字 |
| 中文题目正文 | Noto Serif SC | 400 | 主要阅读内容 |
| 中文描述、选项 | Noto Serif SC | 400 | 正文延伸 |
| 欢迎页叙述段落 | IM Fell English | 400/italic | 保留原有仪式感文案 |
| 中文标题（Phase 名） | Noto Serif SC | 600 | 加粗强调 |

### 字号规范

```css
/* 主标题 */
.title-main    { font-size: clamp(1.8rem, 4vw, 3rem); letter-spacing: 0.08em; }

/* 区块标题 */
.title-section { font-size: 0.78rem; letter-spacing: 0.22em; text-transform: uppercase; }

/* 题目正文 */
.question-text { font-size: 1.15rem; line-height: 1.8; }

/* 选项文字 */
.option-text   { font-size: 1rem; line-height: 1.65; }

/* 辅助说明 */
.text-hint     { font-size: 0.85rem; line-height: 1.6; font-style: italic; }
```

---

## 四、组件规范

### 4.1 主卡片（Main Card）

```css
.card-main {
  background: var(--bg-card);
  border: 1px solid var(--border-gold);
  border-radius: 4px;
  box-shadow:
    0 0 40px rgba(201, 168, 76, 0.08),
    0 0 80px rgba(0, 0, 0, 0.5),
    inset 0 0 80px rgba(0, 0, 0, 0.3);
  padding: 2.5rem 3rem;
  max-width: 700px;
  position: relative;
}

/* 四角装饰 */
.card-main::before { content: '✦'; top: 12px; left: 16px; }
.card-main::after  { content: '✦'; bottom: 12px; right: 16px; }
```

### 4.2 版本选择卡片（Version Card）

三态：默认 / 悬停 / 选中

```css
.version-card         { border: 1px solid var(--border-dim); background: transparent; }
.version-card:hover   { border-color: var(--border-gold); background: rgba(201,168,76,0.06); }
.version-card.selected {
  border-color: var(--gold-primary);
  background: rgba(201, 168, 76, 0.12);
  box-shadow: 0 0 20px rgba(201, 168, 76, 0.18);
}
```

### 4.3 选项按钮（Option Button）

三态：默认 / 悬停 / 选中

```css
.option-btn          { border: 1px solid var(--border-dim); background: rgba(201,168,76,0.03); }
.option-btn:hover    { border-color: var(--gold-primary); background: rgba(201,168,76,0.10); color: var(--text-primary); }
.option-btn.selected {
  border-color: var(--gold-bright);
  background: rgba(201, 168, 76, 0.18);
  color: var(--gold-bright);
  box-shadow: 0 0 16px rgba(201, 168, 76, 0.30);
}

/* 选项字母徽章 */
.option-letter {
  font-family: 'Cinzel', serif;
  color: var(--teal);
  min-width: 1.4rem;
}
.option-btn.selected .option-letter { color: var(--gold-bright); }
```

### 4.4 按钮（Buttons）

```css
/* 主按钮 */
.btn-primary {
  background: rgba(201, 168, 76, 0.12);
  border: 1px solid var(--gold-primary);
  color: var(--gold-bright);
  font-family: 'Cinzel', serif;
  letter-spacing: 0.14em;
  transition: all 0.3s ease;
}
.btn-primary:hover {
  background: rgba(201, 168, 76, 0.24);
  box-shadow: 0 0 20px var(--glow-gold);
  text-shadow: 0 0 10px var(--gold-primary);
}

/* 次要按钮 */
.btn-secondary {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.10);
  color: var(--text-muted);
}
.btn-secondary:hover { border-color: var(--border-gold); color: var(--text-secondary); }

/* 禁用态（确认按钮未选版本时） */
.btn-primary:disabled {
  background: rgba(201, 168, 76, 0.04);
  border-color: var(--border-dim);
  color: var(--text-muted);
  cursor: not-allowed;
  box-shadow: none;
}
```

### 4.5 进度条（Progress Bar）

```css
.progress-bar-bg   { height: 3px; background: rgba(255,255,255,0.06); border-radius: 2px; }
.progress-bar-fill {
  height: 100%;
  background: linear-gradient(to right, var(--gold-muted), var(--gold-bright));
  box-shadow: 0 0 8px var(--glow-gold);
  transition: width 0.5s ease;
}
```

### 4.6 金色分隔线（Divider）

```css
.divider {
  width: 300px;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--gold-primary), transparent);
  margin: 1.2rem auto;
  opacity: 0.5;
}
```

### 4.7 结果区块（Result Section）

```css
.result-section h2 {
  font-family: 'Cinzel', serif;
  font-size: 0.78rem;
  letter-spacing: 0.22em;
  color: var(--gold-primary);
  text-transform: uppercase;
  border-bottom: 1px solid rgba(201, 168, 76, 0.2);
  padding-bottom: 0.4rem;
  margin-bottom: 0.8rem;
}
```

### 4.8 成功提示（Success Message）

```css
.success-msg {
  background: rgba(201, 168, 76, 0.08);
  border: 1px solid rgba(201, 168, 76, 0.3);
  color: var(--gold-primary);
  font-family: 'Cinzel', serif;
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-align: center;
  padding: 1rem 1.4rem;
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 8px rgba(201,168,76,0.15); }
  50%       { box-shadow: 0 0 24px rgba(201,168,76,0.40); }
}
```

---

## 五、动效规范

| 元素 | 动效 | 参数 |
|---|---|---|
| 页面卡片入场 | fadeUp | translateY(16px) → 0, opacity 0→1, 0.6s ease |
| 标题区入场 | fadeDown | translateY(-12px) → 0, opacity 0→1, 1s ease |
| 帽子图标 | float | translateY 0 → -10px → 0, 4s ease-in-out infinite |
| 进度条填充 | width transition | 0.5s ease |
| 生成中文字 | fadeIn 逐行 | 每行延迟 0.8s，opacity 0→1, 0.5s ease |
| 选项选中 | box-shadow + color | 0.25s ease |
| 按钮悬停 | glow + text-shadow | 0.3s ease |
| 成功消息 | pulse-glow | 2s ease-in-out infinite |

---

## 六、四个页面规格

### 6.1 欢迎页（pageWelcome）

布局（从上到下）：
1. 页面顶部：`hat-emoji`（5rem，浮动动画）
2. `h1` Sorting Hat（Cinzel Decorative，金色，发光）
3. `subtitle` AI 人设分院仪式（Cinzel，小号，字间距大）
4. `divider`
5. 欢迎文案段落（IM Fell English，`text-secondary`）
6. `divider`
7. 版本选择提示（Cinzel 小号）
8. 两个 `version-card` 并排（flex，gap 1rem）
9. `btn-confirm`（全宽，默认禁用，选版本后激活）

### 6.2 问卷页（pageQuiz）

布局（从上到下）：
1. 进度条区（phase 标签 + 百分比 + bar）
2. `phase-label`（紫色，Cinzel，uppercase）
3. `question-num`（金色，Cinzel）
4. `question-text`（Noto Serif SC，1.15rem）
5. 选项列表（`option-btn` 纵向排列，gap 0.65rem）
   - 或开放输入框（`open-input`，textarea）
6. 导航按钮行（← 上一题 / 下一题 →）

**特殊处理：**
- 称呼题选中「叫我名字」或「叫我职位」时，动态插入文字输入框
- 第一题隐藏「上一题」按钮
- 最后一题「下一题」改为「生成人设 ✨」

### 6.3 生成中（pageGenerating）

布局：
- 居中，`padding: 3rem 0`
- 四行文字逐行出现（animation-delay 递增 0.8s）：
  ```
  🔮  正在分析你的答案…
  ✨  匹配人格图谱…
  📜  生成专属人设…
  🎩  分院帽已做出决定…
  ```
- 字体 Noto Serif SC，`text-secondary`
- 3.2s 后自动跳转结果页

### 6.4 结果页（pageResult）

布局（从上到下）：
1. `result-section`：**✦ 你的人设档案**（标题）
2. 人设正文（`resultPersona`，Noto Serif SC，`text-secondary`）
   - `**粗体**` 标记各区块名称，渲染为 `<strong>`
   - 换行用 `<br>`
3. `success-msg`（保存后显示，默认隐藏）
4. `error-msg`（连接失败时显示）
5. 操作按钮行：「重新分院」（次要）+ 「保存人设 ✓」（主要）

---

## 七、文件结构

```
web/
  index.html     # 单文件，所有 CSS + HTML + JS 内联
  server.py      # 不改动，负责提供文件和写入 persona.md
```

`index.html` 保持单文件架构，CSS 内联在 `<style>`，JS 内联在 `<script>`，零外部依赖（字体通过 Google Fonts CDN 加载）。

---

## 八、实现检查清单

- [ ] 色彩变量全部替换为新的 CSS 变量
- [ ] 字体替换：中文段落换为 Noto Serif SC
- [ ] 背景改为双层 radial-gradient 烛光效果
- [ ] 卡片四角装饰 `::before` / `::after` 实现
- [ ] 进度条从 `transform: scaleX` 改为 `width` 过渡（更可预测）
- [ ] 选项按钮三态样式（默认/悬停/选中）
- [ ] 生成中页面逐行动画 delay 正确
- [ ] 结果页 `**bold**` 转 `<strong>` 渲染
- [ ] 响应式：卡片最大宽 700px，小屏 padding 收缩
- [ ] 版本选择卡片在窄屏下竖向排列（`flex-wrap: wrap`）

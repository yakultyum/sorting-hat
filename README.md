# 🎩 Sorting Hat · AI 人设分院仪式

> 像哈利波特里的分院帽一样，通过一次问卷，找到最适合你的 AI 协作方式——然后记住你，往后每天都以这种方式工作。

---

## 这是什么

Sorting Hat 是一个运行在 AI 编程工具里的 skill，解决一个被忽视的问题：

**大多数人以完全相同的方式使用 AI，但每个人和 AI 协作的最佳方式其实差异很大。** 有人需要 AI 直接给结论，有人需要一起推导；有人希望 AI 有话直说，有人需要它先照顾情绪。这些不是口味偏好，是你的认知结构。

Sorting Hat 融合七个心理学框架（荣格八维认知功能、Anthropic 情绪研究、OCEAN 大五人格、依恋理论、认知负荷理论、调节焦点理论、认知需求与控制点），通过网页问卷生成一份专属的 AI 人设，写入你的工具配置，从此每次对话自动生效。

---

## 功能

| 指令 | 功能 |
|---|---|
| `/sorting-hat` | 首次分院（简易版 11 题 / 深度版 31 题），或修改已有人设 |
| `/sorting-hat full` | 直接进入深度版 |
| `/sorting-hat init [路径]` | 为任意项目生成 CLAUDE.md |

### 支持的工具

| 工具 | 人设写入位置 | 生效方式 |
|---|---|---|
| Claude Code | `~/.claude/memory/persona.md` | 每次对话自动加载 |
| Cursor | `.cursor/rules` | 项目级自动加载 |
| Windsurf | `.windsurfrules` | 项目级自动加载 |
| 其他工具 | 终端输出 system prompt | 手动粘贴到工具设置 |

---

## 安装

**1. 克隆项目**

```bash
git clone https://github.com/<your-username>/sorting-hat.git
```

**2. 复制 skill 文件**

```bash
mkdir -p ~/.claude/skills/sorting-hat
cp sorting-hat/skill/SKILL.md ~/.claude/skills/sorting-hat/SKILL.md
```

**3. 使用**

在任意目录打开 Claude Code（或其他支持的工具），输入：

```
/sorting-hat
```

**系统要求：** Python 3（系统自带）、Claude Code / Cursor / Windsurf 任一

---

## 工作原理

```
/sorting-hat
    ↓
选择版本（简易 / 深度）
    ↓
选择输出目标（Claude Code / Cursor / Windsurf / 通用）
    ↓
启动本地服务器，自动打开浏览器
    ↓
在网页上完成问卷
    ↓
人设写入目标配置文件，浏览器关闭
    ↓
之后每次对话，AI 自动以该人设工作
```

问卷结果经过三层转化：**用户答案 → 心理特征 → AI 行事原则**，生成的不是情景描述，而是通用的行为准则。

---

## 项目结构

```
sorting-hat/
  skill/
    SKILL.md          # Skill 主文件，安装到 ~/.claude/skills/sorting-hat/
  web/
    index.html        # 问卷网页
    server.py         # 本地 HTTP 服务器
  docs/
    PRD-sorting-hat.md
    questionnaire/
      questionnaire.md  # 完整题目与心理转化规则
    psychology-foundations.md
```

---

## License

MIT

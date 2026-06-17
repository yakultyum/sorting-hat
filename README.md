# 🎩 Sorting Hat Skill —— 为你量身定制 AI 协作伙伴

> 让 AI 不再只是通用助手，而是像那个与你性格、节奏和工作方式完美契合的人一样，与你达成高效、自然、长期的协作。

Sorting Hat 是一个运行在 Claude Code、Cursor、Windsurf 等 AI 编程工具里的本地 skill。它通过结构化问卷理解用户的认知风格，生成可持久化、可切换、可复盘的 AI 协作 profile。

```text
Profile = AI 人设 Persona + 协作 Workflow + 项目绑定 Project Binding
```

---

## 为什么做这个

最好的协作，不只是对方能力强，而是对方刚好懂你的节奏。

你想快，它不拖慢你；你想深挖，它陪你推理；你需要真话，它直接指出问题；你需要缓冲，它知道怎么让你听得进去。

今天的大多数 AI 仍然用同一种方式对待所有人。但每个人的认知风格、反馈偏好、决策方式都不一样。

Sorting Hat 解决的就是这个被忽视的问题：**让 AI 从通用助手，变成真正适合你的协作伙伴。**

---

## 核心能力

| 能力 | 说明 |
|---|---|
| AI 人设分院 | 通过简易版 / 深度版问卷生成适合用户认知风格的 persona |
| 多 profile 管理 | 管理多套 AI 协作方式，如严格工程搭档、产品共创伙伴、Darwin 优化器 |
| 多工具输出 | 支持 Claude Code、Cursor、Windsurf 和通用 system prompt |
| 局部修改 | 可只修改反馈方式、推理深度、适用场景等单个维度 |
| Workflow Sorting | 沉淀“人如何主导 AI”的协作规则，不保存聊天原文 |
| 项目初始化 | 为项目生成 CLAUDE.md，让 AI 理解项目上下文 |

---

## 一条命令安装

```bash
git clone https://github.com/yakultyum/sorting-hat.git sorting-hat && cd sorting-hat && scripts/install-skill.sh --force
```

这条命令会：

1. 从 GitHub 拉取完整项目；
2. 自动检测常见本地 skills 目录；
3. 安装完整 Sorting Hat skill 包。

脚本会优先使用已存在的本地 runtime 目录，例如 Claude Code、Cursor、Windsurf、Codex 或其他 agent skills 目录。

如果你已经在项目根目录，也可以只执行：

```bash
scripts/install-skill.sh --force
```

如果需要指定安装位置：

```bash
scripts/install-skill.sh --dest ~/.cursor/skills --force
```

> 不能只复制 `SKILL.md`：Sorting Hat 依赖网页问卷、本地保存服务、规则文件和测试 prompts，必须安装完整 `skill/` 目录。

---

## 使用方式

安装后，在支持 skills 的 AI 编程工具中输入：

```text
/sorting-hat
```

Sorting Hat 会启动本地问卷页面，引导你完成一次 AI 协作方式分院。

### 常用命令

| 命令 | 作用 |
|---|---|
| `/sorting-hat` | 首次分院，或修改已有人设 |
| `/sorting-hat full` | 直接进入深度版问卷 |
| `/sorting-hat profiles` | 查看已保存的 AI 协作 profiles |
| `/sorting-hat use <profile>` | 本次对话临时使用某个 profile，不写项目配置 |
| `/sorting-hat reflect` | 从复盘文本沉淀 workflow 规则 |
| `/sorting-hat init [路径]` | 为项目生成 CLAUDE.md |

---

## 支持的输出目标

| 工具 | 写入位置 | 用途 |
|---|---|---|
| Claude Code | `~/.claude/memory/persona.md` | 每次对话自动加载 |
| Cursor | `.cursor/rules/sorting-hat.mdc` | 项目级规则 |
| Windsurf | `.windsurfrules` | 项目级规则 |
| Generic | 页面 / 终端复制 prompt | 通用 system prompt |
| All | 同时生成所有格式 | 多工具同步 |

安装 runtime 和输出目标是两件事：Sorting Hat 可以安装在任意支持本地 skills 的工具中；生成结果仍可输出到 Claude Code、Cursor、Windsurf 或通用 prompt。

---

## 用户流程

### 第一次创建 profile

```text
/sorting-hat
  ↓
回答问卷
  ↓
填写 profile 名称
  ↓
选择适用场景
  ↓
生成 persona + profile + answers JSON
```

### 临时切换协作方式

```text
/sorting-hat use 产品共创伙伴
```

### 沉淀协作经验

```text
/sorting-hat reflect
  ↓
选择 profile
  ↓
输入复盘内容
  ↓
保存 workflow.md
```

### 初始化项目上下文

```text
/sorting-hat init
  ↓
扫描项目
  ↓
确认技术栈、命令、规范和 gotcha
  ↓
生成 CLAUDE.md
```

---

## 本地存储结构

```text
~/.sorting-hat/
  # profiles live under ~/.sorting-hat/profiles
  index.json
  profiles/
    <profile-id>/
      profile.json
      persona.md
      prompt.md
      answers.json
      workflows/
        <workflow-id>.md
```

所有数据默认保存在本地，不上传服务器。

---

## Workflow Sorting 是什么

Workflow Sorting 沉淀的不是完整聊天记录，而是“人如何主导 AI”的抽象协作规则。

每条 workflow 包含：

- 触发场景
- 人的主导动作
- AI 应如何响应
- 反例
- 验证 prompt

示例：

```text
当用户说“继续优化”时，不要泛泛发散。
应沿用上一轮评估框架，选择一个明确维度，小步修改，运行验证，给出复评分和下一轮建议。
```

---

## 项目结构

```text
sorting-hat/
  skill/
    SKILL.md
    web/
      index.html
      server.py
    references/
      questionnaire.md
      output-formats.md
      evaluation.md
    test-prompts.json
  web/
    index.html
    server.py
  scripts/
    check-release.py
    install-skill.sh
  tests/
    test_server_targets.py
  docs/
    sorting-hat-competition-submit.md
    sorting-hat-competition-submit.html
```

---

## 开发与发布检查

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check-release.py
bash -n scripts/install-skill.sh
```

`check-release.py` 会确认：

- skill 资源完整；
- `web/` 与 `skill/web/` 同步；
- Python 文件可编译；
- JSON 有效；
- test prompts 覆盖主命令路径；
- SKILL.md 引用关键资源。

---

## 比赛提交文档

- Markdown：`docs/sorting-hat-competition-submit.md`
- HTML 展示页：`docs/sorting-hat-competition-submit.html`

---

## License

MIT

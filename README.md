# 🎩 Sorting Hat Skill —— 为你量身定制 AI 协作伙伴

> 让 AI 不再只是通用助手，而是像那个与你性格、节奏和工作方式完美契合的人一样，与你达成高效、自然、长期的协作。

Sorting Hat 是一个运行在 Claude Code、Cursor、Windsurf 等 AI 编程工具里的本地 skill。它通过结构化问卷理解用户的认知风格，生成可持久化、可切换、可复盘的 AI 协作 profile。

```text
Profile = AI 人设 Persona + 协作 Workflow + 项目记忆 Project Memory
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
| AI 人设分院 | 通过简易版（11 题）/ 深度版（31 题）问卷生成适合用户认知风格的 persona |
| 手写人设 | 跳过问卷，直接填写 profile 名称、场景和人设文本 |
| 档案管理 UI | 网页端查看、编辑所有 profile 的人设和 workflow，无需命令行 |
| 激活到工具 | 一键将任意 profile 激活到 Claude Code（全局）或项目 Cursor / Windsurf |
| 两层记忆架构 | 全局 persona.md 定义基础人设；项目 `.sorting-hat/project.md` 存储项目上下文和覆盖规则 |
| 多 profile 管理 | 管理多套 AI 协作方式，如严格工程搭档、产品共创伙伴、Darwin 优化器 |
| Workflow Sorting | 沉淀"人如何主导 AI"的协作规则，不保存聊天原文 |
| 项目初始化 | `/sorting-hat init` 为项目生成 CLAUDE.md |
| 多工具输出 | 支持 Claude Code、Cursor、Windsurf 和通用 system prompt |

---

## 一条命令安装

```bash
git clone https://github.com/yakultyum/sorting-hat.git sorting-hat && cd sorting-hat && scripts/install-skill.sh --force
```

这条命令会：

1. 从 GitHub 拉取完整项目；
2. 自动检测常见本地 skills 目录；
3. 安装完整 Sorting Hat skill 包。

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

安装后，在支持 skills 的 AI 工具中输入：

```text
/sorting-hat
```

Sorting Hat 会启动本地服务器，打开网页引导你完成分院。

### 常用命令

| 命令 | 作用 |
|---|---|
| `/sorting-hat` | 首次分院，启动网页问卷 |
| `/sorting-hat full` | 直接进入深度版问卷（31 题） |
| `/sorting-hat profiles` | 终端列出已保存的所有 profile |
| `/sorting-hat use <profile>` | 本次对话临时使用某个 profile |
| `/sorting-hat reflect` | 从复盘文本沉淀 workflow 规则 |
| `/sorting-hat init [路径]` | 为项目生成 CLAUDE.md |

---

## 网页档案管理

启动服务器后，除了做问卷，还可以在网页端管理所有 profile：

**欢迎页三个入口：**
- **开始分院问卷**：简易版 / 深度版，通过结构化问卷生成人设
- **直接手写人设**：填名称、选场景、写人设文本，立即创建 profile
- **我的档案**：查看和管理所有已保存的 profile

**档案页每个 profile 卡片提供：**
- 人设描述全文（可直接编辑，保存到 `prompt.md`）
- Workflow 列表（按字段逐段展示和编辑）
- **激活到工具**：一键激活到 Claude Code，或输入项目路径激活到 Cursor / Windsurf
- **项目记忆**：为绑定项目创建 `.sorting-hat/project.md`

---

## 两层记忆架构

```
~/.claude/memory/persona.md          ← 全局基础人设
                                        末尾固定包含：
                                        "每次开始任务前检查 .sorting-hat/project.md
                                         如果存在，读取并覆盖对应准则"

<project>/.sorting-hat/project.md   ← 项目记忆
                                        技术栈 + 约定 + Gotcha + 人设覆盖
```

同一个 AI agent 在不同项目里自动切换上下文——进入项目目录时读取项目记忆，无需手动切换 profile。适用于 Claude Code 以外的所有 AI agent。

---

## 支持的输出目标

| 工具 | 写入位置 | 说明 |
|---|---|---|
| Claude Code | `~/.claude/memory/persona.md` | 全局，每次对话自动加载 |
| Cursor | `.cursor/rules/sorting-hat.mdc` | 项目级规则 |
| Windsurf | `.windsurfrules` | 项目级规则 |
| Generic | 页面 / 终端复制 prompt | 通用 system prompt，适用于任意工具 |
| All | 同时生成所有格式 | 多工具同步 |

---

## 用户流程

### 方式一：通过问卷创建 profile

```text
/sorting-hat → 选择简易版或深度版
  ↓
回答问卷 → 填写 profile 名称和适用场景
  ↓
生成 persona + answers.json + profile.json
  ↓
在档案页激活到目标工具
```

### 方式二：直接手写创建 profile

```text
网页 → 直接手写人设
  ↓
填写名称、选场景、写人设文本 → 保存
  ↓
在档案页激活到目标工具
```

### 为项目添加记忆

```text
档案页 → 展开 profile → 项目记忆 → 新建
  ↓
填写项目路径、技术栈、约定、Gotcha、人设覆盖
  ↓
写入 <project>/.sorting-hat/project.md
  ↓
AI 进入该项目时自动读取
```

### 沉淀协作经验

```text
/sorting-hat reflect → 选择 profile → 输入复盘内容
  ↓
保存为 workflow.md（可在档案页按字段查看和编辑）
```

---

## 本地存储结构

所有 profile 保存在 `~/.sorting-hat/profiles`，通过 `~/.sorting-hat/index.json` 索引。

```text
~/.sorting-hat/
  index.json                          ← profile 目录和默认值
  profiles/
    <profile-id>/
      profile.json                    ← id、名称、场景、绑定项目
      persona.md                      ← 带 frontmatter 的完整文件
      prompt.md                       ← 纯人设 prompt（档案页编辑此文件）
      answers.json                    ← 原始答题数据
      workflows/
        <workflow-id>.md              ← 协作规则

<project>/.sorting-hat/
  project.md                          ← 项目记忆（技术栈、约定、Gotcha、人设覆盖）
```

所有数据保存在本地，不上传服务器。

---

## Workflow Sorting 是什么

Workflow Sorting 沉淀的不是完整聊天记录，而是"人如何主导 AI"的抽象协作规则。

每条 workflow 包含：触发场景、人的主导动作、AI 应如何响应、反例、验证 prompt。

示例：

```text
当用户说"继续优化"时，不要泛泛发散。
应沿用上一轮评估框架，选择一个明确维度，小步修改，运行验证，给出复评分和下一轮建议。
```

workflow 在档案页可按字段逐段查看和编辑，也可通过 `/sorting-hat reflect` 从复盘文本自动生成。

---

## 项目结构

```text
sorting-hat/
  skill/
    SKILL.md
    web/
      index.html      ← 网页问卷 + 档案管理 UI
      server.py        ← 本地 HTTP 服务（托管、写入、profile 管理 API）
    references/
      questionnaire.md
      output-formats.md
      evaluation.md
    test-prompts.json
  scripts/
    check-release.py
    install-skill.sh
  tests/
    test_server_targets.py
  docs/
    sorting-hat-competition-submit.md
```

---

## 开发与发布检查

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check-release.py
bash -n scripts/install-skill.sh
```

---

## License

MIT

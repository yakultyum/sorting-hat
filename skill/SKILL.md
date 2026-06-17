---
name: sorting-hat
description: AI 人设分院仪式。通过结构化问卷找到最适合用户认知风格的 AI 协作 profile（人设 + 适用场景），支持输出到 Claude Code、Cursor、Windsurf 或通用 system prompt。也可用 /sorting-hat init 为任意项目生成 CLAUDE.md。触发词：/sorting-hat、/sorting-hat full、/sorting-hat init、"帮我分院"、"帮我配置 AI 人设"、"帮我初始化项目"、"帮我写 CLAUDE.md"
---

# Sorting Hat · AI 人设分院仪式

## 概述

Sorting Hat 有三个功能入口：

| 指令 | 场景 | 方式 |
|---|---|---|
| `/sorting-hat` | 首次分院，或修改已有人设 | 启动本地服务器，打开网页问卷 |
| `/sorting-hat full` | 直接进入深度版（31 题） | 同上 |
| `/sorting-hat profiles` | 查看所有 AI 协作 profiles | 读取 `~/.sorting-hat/index.json` |
| `/sorting-hat use <profile>` | 本次对话临时使用某个 profile | 输出该 profile 的 prompt，不写项目配置 |
| `/sorting-hat reflect` | 沉淀人如何主导 AI 的 workflow | 从复盘文本生成抽象规则 |
| `/sorting-hat init [路径]` | 为项目生成 CLAUDE.md | 终端对话式提问 |

本 skill 是自包含目录，运行资源位于：

| 资源 | 用途 |
|---|---|
| `web/server.py` | 本地保存服务，支持多工具输出 |
| `web/index.html` | 问卷网页 |
| `references/questionnaire.md` | 完整题目与心理转化规则 |
| `references/output-formats.md` | 输出模板与终端视觉规范 |
| `references/evaluation.md` | Darwin 实测评分说明 |
| `test-prompts.json` | 三条主路径的评估 prompt |
| `../scripts/check-release.py` | 发布前资源完整性校验 |
| `../scripts/install-skill.sh` | 安装到指定 runtime skills 目录 |

---

## 快速自检

在执行路径 A/B 前，先确认当前 skill 目录完整：

```bash
test -f "$SKILL_DIR/web/server.py" && \
test -f "$SKILL_DIR/web/index.html" && \
test -f "$SKILL_DIR/references/questionnaire.md"
```

如果任一文件缺失，停止执行并提示用户重新安装整个 `skill/` 目录；不要只复制 `SKILL.md`。

路径 C 不依赖网页资源，但仍需确认目标目录可写；不可写时停止并要求用户换目录或授权。

面向用户展示时，使用 GitHub 一条命令安装：

```bash
git clone https://github.com/yakultyum/sorting-hat.git sorting-hat && cd sorting-hat && scripts/install-skill.sh --force
```

如果已经在项目根目录，使用本地安装脚本：

```bash
scripts/install-skill.sh --force
```

脚本会自动检测常见本地 skills 目录。也可以使用 `--dest <runtime-skills-dir>` 指定 Claude Code、Cursor、Windsurf、Codex 或其他 runtime 的 skills 目录。

安装 runtime 和输出目标是两件事：skill 可以安装在任意支持本地 skills 的工具中；生成结果仍可输出到 Claude Code、Cursor、Windsurf 或通用 system prompt。

已有安装需要覆盖时，使用 `--force`；脚本会先创建时间戳备份。

---

## 入口判断逻辑

收到调用时，按以下顺序判断走哪条路径：

1. 指令为 `profiles` → 进入 **[路径 D：查看 profiles]**
2. 指令为 `use <profile>` → 进入 **[路径 E：临时使用 profile]**
3. 指令为 `reflect` → 进入 **[路径 F：沉淀 workflow]**
4. 指令包含 `init` 或用户说"帮我写 CLAUDE.md"/"帮我初始化项目" → 进入 **[路径 C：项目初始化]**
5. 目标工具对应的 answers JSON 已存在，且指令不含 `full` → 进入 **[路径 B：修改人设]**
6. 其余情况 → 进入 **[路径 A：人设分院]**

---

## 路径 A：人设分院（首次）

### 第一步：询问版本

用 `AskUserQuestion` 让用户选择：

```
问题：你想做哪个版本？
选项：
  - 简易版（11 题，约 5 分钟）——快速上手，立即生效
  - 深度版（31 题，约 15-20 分钟）——融合七个心理学框架，人设更精准
```

若用户调用的是 `/sorting-hat full`，跳过此步，直接启动深度版。

### 第二步：询问使用的 AI 工具

用 `AskUserQuestion` 让用户选择输出目标（此步决定后续写入格式和位置）：

```
问题：你主要用哪个 AI 工具？
选项：
  - Claude Code → 写入 ~/.claude/memory/persona.md，每次对话自动生效
  - Cursor → 写入当前项目 .cursor/rules，项目级自动加载
  - Windsurf → 写入当前项目 .windsurfrules，项目级自动加载
  - 通用（其他工具）→ 生成 system prompt 文字，复制粘贴到任意工具的设置里
  - 全部生成 → 同时输出所有格式
```

记录用户选择，在第四步按此决定写入行为。

### 第三步：启动服务器并打开浏览器

在终端输出：

```
🎩  Sorting Hat · 分院仪式启动
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
正在启动本地服务器...
浏览器即将打开，请在页面中完成问卷。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

然后执行：

用 Bash 工具执行以下命令，其中 `SKILL_DIR` 为本 `SKILL.md` 所在目录：

```bash
cd "$SKILL_DIR/web" && python3 server.py --target claude
```

根据第二步选择替换 `--target`：

| 用户选择 | 命令参数 |
|---|---|
| Claude Code | `--target claude` |
| Cursor | `--target cursor --project-dir "$(pwd)"` |
| Windsurf | `--target windsurf --project-dir "$(pwd)"` |
| 通用 | `--target generic` |
| 全部生成 | `--target all --project-dir "$(pwd)"` |

如需写入自定义文件，使用 `--output /完整/文件路径`。server.py 会自动打开浏览器并在问卷提交后关闭服务器。问卷结果会 POST 到 `/save` 接口，包含带 profile frontmatter 的完整文件内容、纯 prompt 内容、profile 名称与适用场景。

如果默认端口被占用，改用 `--port 其他端口`；网页使用相对路径提交 `/save`，无需改前端代码。

### 🔴 CHECKPOINT · 写入前确认

启动服务器前，向用户确认以下信息：

1. 输出目标：Claude Code / Cursor / Windsurf / 通用 / 全部生成
2. 写入路径：按目标列出完整路径
3. 备份行为：已有文件会先写入同名 `.bak`

用户没有确认时，不启动写入流程。

### 第四步：按目标写入

服务器收到结果后，根据第二步的选择执行写入：

**Claude Code 输出适配器：**
将人设内容写入 `~/.claude/memory/persona.md`（带 frontmatter 格式，模板见 `references/output-formats.md`）。

**Cursor 输出适配器：**
将纯人设 prompt 文字写入当前项目 `.cursor/rules/sorting-hat.mdc`。内容不含 frontmatter，直接是第一人称命令式的人设描述。

**Windsurf 输出适配器：**
将纯人设 prompt 文字写入当前目录的 `.windsurfrules`。格式同 Cursor。

**通用输出适配器：**
在终端直接输出人设 prompt 文字，附上使用说明：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎩  你的 AI 人设已生成，复制以下内容粘贴到
   你所用工具的 System Prompt 或自定义指令设置里：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[人设 prompt 全文]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**全部生成：**
依次执行上述所有写入，在终端逐条确认每个文件的写入路径。

写入任何已有文件前，server.py 会自动生成同名 `.bak` 备份。
每次写入文件时，server.py 还会保存原始答题数据：Claude Code 为 `persona.answers.json`，其他文件为 `sorting-hat.answers.json`。JSON 内包含 `version`、完整 `answers`、`profile.name` 与 `profile.scenarios`。后续修改单个维度时优先读取该 JSON，避免从 Markdown 里反推答案。

同时，server.py 会将该人设镜像到全局 profile 仓库：`~/.sorting-hat/profiles/<profile-id>/`，包含 `profile.json`、`persona.md`、`prompt.md`、`answers.json`，并更新 `~/.sorting-hat/index.json`。这是后续 `/sorting-hat profiles`、`use`、`bind`、`routes` 的兼容基础，不替代当前工具目标写入。

### 第五步：完成确认

输出：

```
✓  分院完成。
   [按选择列出写入的文件路径，或提示复制 system prompt]
   随时调用 /sorting-hat 修改某一个维度。
```

---

## 路径 B：修改人设

### 第一步：启动修改模式

不要手动编辑 `persona.md`。启动同一个网页服务，让网页读取 `persona.answers.json` 或 `sorting-hat.answers.json`，用户在浏览器里选择要修改的维度。

```bash
cd "$SKILL_DIR/web" && python3 server.py --target claude
```

上方命令是 Claude Code 输出适配器示例。如果用户要修改 Cursor/Windsurf/全部生成输出，按路径 A 的目标参数替换 `--target` 和 `--project-dir`。

如果 `/state` 返回“未找到已保存的答题数据”，停止修改流程，提示用户先完整分院一次；不要从 `persona.md` 反推答案。

### 第二步：用户在网页中选择维度

网页首页点击「修改已有维度」，会读取 `/state` 返回的原始答题数据，然后展示可修改维度：

- 推理深度
- 反馈方式
- 问题解法
- 情绪底色
- 温暖/直率
- 信息密度
- 格式偏好
- 调节焦点
- 专业领域
- 称呼
- 角色融合

### 第三步：局部重问，整体重算

网页只重问该维度对应题目，但保存时使用完整 answers JSON 重新生成整份 persona。不要做 Markdown 局部替换。

### 第四步：写回与备份

保存后 server.py 会：

1. 备份旧配置为同名 `.bak`
2. 写入新的 persona/prompt 文件
3. 同步更新原始答题 JSON
4. 在网页和终端显示写入路径

---

## 路径 D：查看 profiles（/sorting-hat profiles）

读取全局仓库 `~/.sorting-hat/index.json` 并列出所有已保存 profile。

用户只需要调用：

```text
/sorting-hat profiles
```

skill 内部执行：

```bash
cd "$SKILL_DIR/web" && python3 server.py profiles
```

输出包含：profile id、名称、适用场景；默认 profile 前用 `*` 标记。

如果没有任何 profile，提示用户先运行 `/sorting-hat` 或 `/sorting-hat new` 完成一次分院。

---

## 路径 E：临时使用 profile（/sorting-hat use <profile>）

`use` 只读取某个 profile 的 prompt，供本次对话临时采用，不写入当前项目，也不修改全局默认值。

用户只需要调用：

```text
/sorting-hat use <profile-id-or-name>
```

skill 内部执行：

```bash
cd "$SKILL_DIR/web" && python3 server.py use "<profile-id-or-name>"
```

然后将输出中的 prompt 作为本次对话的行为准则继续执行。若找不到 profile，先运行 `/sorting-hat profiles` 展示可选项，不要猜测用户想用哪一个。

---

## 路径 F：沉淀 workflow（/sorting-hat reflect）

`reflect` 用于沉淀“人如何主导 AI”的协作方式，而不是保存聊天原文。每条 workflow 应包含：触发场景、人的主导动作、AI 应如何响应、反例、验证 prompt。

最小流程：

1. 用户只需要调用：

```text
/sorting-hat reflect
```

2. 读取 `~/.sorting-hat/index.json`；如果没有 profile，停止并引导用户先运行 `/sorting-hat` 创建 profile。
3. 展示可选 profile，让用户选择要挂载的 profile；若用户已在指令里写明 profile 名称，先按名称匹配。
4. 询问 workflow 标题，例如「验证优先」「连续优化」「代码审查收敛」。
5. 请用户粘贴一段复盘内容，或让用户确认“从当前会话摘要中提炼”。不要保存完整聊天原文。
6. 将复盘内容写入临时文件，skill 内部执行：

```bash
cd "$SKILL_DIR/web" && python3 server.py reflect "<profile-id-or-name>" --source reflection.txt --title "验证优先"
```

7. 生成文件位于 `~/.sorting-hat/profiles/<profile-id>/workflows/<workflow-id>.md`，并写回该 profile 的 `profile.json`。
8. 展示生成的 workflow 摘要，明确列出：触发场景、人的主导动作、AI 应如何响应、反例、验证 prompt。

🔴 CHECKPOINT · reflect 保存前确认：保存前必须让用户确认 profile、workflow 标题和抽象规则摘要。用户确认前不要写入 workflows 目录。

失败分支：

| 情况 | 处理 |
|---|---|
| 没有任何 profile | 停止；提示先运行 `/sorting-hat` 创建 profile |
| 用户没选 profile | 先展示 `/sorting-hat profiles` 结果，再让用户选择 |
| 复盘内容为空 | 停止；要求用户补充要沉淀的协作经验 |
| 生成内容像聊天记录摘录 | 停止；重新抽象为规则，不保存原文 |

---

## 路径 C：项目初始化（/sorting-hat init）

通过终端对话收集项目信息，生成 CLAUDE.md。全程使用 `AskUserQuestion` 点选 + 文字输入，每次只问一个问题。

### 第一步：确认目标目录

如果指令带了路径（如 `/sorting-hat init ~/work/my-project`），直接使用该路径。

否则用 `AskUserQuestion`：

```
问题：要为哪个目录生成 CLAUDE.md？
选项：
  - 当前目录（[显示当前工作目录的绝对路径]）
  - 其他路径（我来输入）
```

如果选择「其他路径」，等待用户文字输入路径。

确认后，用 Bash 工具快速扫描该目录结构（`ls -la` + 检查常见文件如 package.json、requirements.txt、Makefile、README.md），作为后续问题的背景参考。

如果目标目录不存在，停止并询问用户是否创建该目录；不要自动创建未知路径。

如果目标目录已有 `CLAUDE.md`，进入写入前 checkpoint：展示旧文件存在提示，说明会生成 `.bak` 后再覆盖，必须获得用户确认。

### 第二步：项目基本信息

**Q1 — 项目用途**

直接在对话中问：
> 这个项目主要是做什么的？一两句话就好。

等待用户文字输入。

**Q2 — 技术栈确认**

根据扫描结果推断技术栈，用 `AskUserQuestion` 确认：

```
问题：主要技术栈是？（可多选）
选项：
  - [根据扫描结果列出推断的技术，例如 Python / Node.js / React 等]
  - 其他（我来补充）
multiSelect: true
```

### 第三步：常用命令

直接在对话中问：
> 开发、构建、测试分别用什么命令？不知道的可以跳过，直接回车。
>
> 开发命令：
> 构建命令：
> 测试命令：

等待用户文字输入（允许留空跳过）。

### 第四步：项目约定

**Q4 — 命名规范**

用 `AskUserQuestion`：

```
问题：这个项目的文件和目录命名用哪种风格？
选项：
  - kebab-case（my-file-name）
  - snake_case（my_file_name）
  - camelCase（myFileName）
  - PascalCase（MyFileName）
  - 中文命名
  - 没有统一规范
  - 其他（我来说）
```

**Q5 — 文档格式**

直接在对话中问：
> 文档有没有格式要求？比如必填字段、固定模板、命名前缀等。
> 没有的话直接跳过。

等待用户文字输入。

**Q6 — 注释语言**

用 `AskUserQuestion`：

```
问题：代码注释用什么语言？
选项：
  - 中文
  - 英文
  - 中英混用（代码英文，解释中文）
  - 没有要求
```

### 第五步：Gotcha

直接在对话中问：
> 有没有容易踩的坑、特殊依赖、或者需要告诉 AI 注意的事？
> 没有的话直接跳过。

等待用户文字输入。

### 第六步：生成并写入

根据收集的信息生成 `CLAUDE.md`，模板见 `references/output-formats.md` 的「CLAUDE.md 模板」。

先在终端展示预览，然后用 `AskUserQuestion` 确认：

```
问题：确认写入 [目标路径]/CLAUDE.md？
选项：
  - 确认写入
  - 我想修改一些内容
```

如选择「我想修改」，询问要改哪里，修改后再次展示预览确认。

确认后用 Write 工具写入文件，输出：

```
✓  已写入 [目标路径]/CLAUDE.md
   在这个项目里，AI 会自动读取这份配置。
```

---

## 失败处理表

| 失败情况 | 处理方式 |
|---|---|
| 找不到 `web/server.py`、`web/index.html` 或 `references/questionnaire.md` | 停止执行，提示重新复制完整 `skill/` 目录 |
| Python 不可用 | 停止执行，提示安装或切换到带 Python 3 的环境 |
| 端口 7432 被占用 | 使用 `--port 其他端口` 重启服务 |
| 浏览器未自动打开 | 在终端给出本地地址，让用户手动打开 |
| `/save` 写入失败 | 显示错误，不删除原文件；让用户检查路径和权限 |
| `/state` 找不到 answers JSON | 停止单维度修改，引导用户完整分院一次 |
| 用户选择 Cursor/Windsurf 但未提供项目目录 | 使用当前工作目录；若当前目录不是项目根，先询问正确目录 |
| 用户选择通用输出 | 不写文件，只在页面/终端提供可复制 prompt |

---

## 反模式黑名单

- 不要只复制 `SKILL.md` 安装；必须复制整个 `skill/` 目录。
- 不要手动局部替换 `persona.md` 段落；必须基于 answers JSON 重新生成完整 persona。
- 不要把 Cursor/Windsurf 输出写成带 frontmatter 的 Claude Code 文件格式。
- 不要在没有 `.bak` 备份说明和用户确认时覆盖已有配置。
- 不要把问卷情景答案原样复制进人设；必须执行“三层转化”。
- 不要在找不到 answers JSON 时编造旧答案或从 Markdown 猜测用户选择。
- 不要把 `通用` 目标写入本地配置文件；它只输出可复制 system prompt。

---

## 评估用例

优化或回归测试本 skill 时，使用 `test-prompts.json` 里的三条主路径 prompt，并按 `references/evaluation.md` 评分。

最低要求：三条 prompt 的平均分不得低于 8/10；任一用例命中 failure_signals 时，必须先修复再发布。

发布前必须在项目根目录运行：

```bash
python3 scripts/check-release.py
```

该脚本必须通过后，才复制或发布 `skill/` 目录。

---

## 三层转化规则（人设生成核心）

问卷的题目是情景探针，生成人设时必须按三层转化，**不能直接复制情景描述**：

```
用户答案 → 心理特征（该答案揭示的认知/情感/行为模式）→ 人设语言（翻译成 AI 的通用行事原则）
```

**错误示例：** 用户选了「带我一步步推导」→ 人设写「你会带用户一步步推导」

**正确示例：** 用户选了「带我一步步推导」→ 心理特征：Ti 主导 + 高认知需求，重视理解过程本身 → 人设语言：「暴露思维链，不替用户跳过推理步骤；用户真正理解比快速给出答案更重要」

每道题的完整转化规则详见：`references/questionnaire.md`

---

## 输出文件结构

输出格式、`persona.md` 模板、`CLAUDE.md` 模板和终端视觉规范统一维护在 `references/output-formats.md`。

执行时遵守两条规则：

1. Claude Code 使用带 frontmatter 的完整 `persona.md`。
2. Cursor、Windsurf、通用输出只使用纯人设 prompt，不带 frontmatter。

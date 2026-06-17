# 🎩 Sorting Hat · AI 人设分院仪式

> 像哈利波特里的分院帽一样，通过一次问卷，找到最适合你的 AI 协作方式——然后记住你，往后每天都以这种方式工作。

---

## 这是什么

Sorting Hat 是一个运行在 AI 编程工具里的 skill，解决一个被忽视的问题：

**大多数人以完全相同的方式使用 AI，但每个人和 AI 协作的最佳方式其实差异很大。** 有人需要 AI 直接给结论，有人需要一起推导；有人希望 AI 有话直说，有人需要它先照顾情绪。这些不是口味偏好，是你的认知结构。

Sorting Hat 融合七个心理学框架（荣格八维认知功能、Anthropic 情绪研究、OCEAN 大五人格、依恋理论、认知负荷理论、调节焦点理论、认知需求与控制点），通过网页问卷生成一份专属的 AI 协作 profile（人设 + 适用场景），写入你的工具配置，从此每次对话自动生效。

---

## 功能

| 指令 | 功能 |
|---|---|
| `/sorting-hat` | 首次分院（简易版 / 深度版），或修改已有人设 |
| `/sorting-hat full` | 直接进入深度版 |
| `/sorting-hat profiles` | 查看已保存的 AI 协作 profiles |
| `/sorting-hat use <profile>` | 临时读取某个 profile 的 prompt，不写项目配置 |
| `/sorting-hat reflect` | 从复盘文本沉淀“人如何主导 AI”的 workflow 规则 |
| `/sorting-hat init [路径]` | 为任意项目生成 CLAUDE.md |

### 支持的工具

| 工具 | 人设写入位置 | 生效方式 |
|---|---|---|
| Claude Code | `~/.claude/memory/persona.md` | 每次对话自动加载 |
| Cursor | `.cursor/rules/sorting-hat.mdc` | 项目级自动加载 |
| Windsurf | `.windsurfrules` | 项目级自动加载 |
| 其他工具 | 终端输出 system prompt | 手动粘贴到工具设置 |

写入已有文件前会自动生成 `.bak` 备份。
同时会保存原始答题数据 JSON，包含 profile 名称和适用场景，方便后续只修改某个维度。
每次保存还会兼容性写入全局 profile 仓库，路径为 `~/.sorting-hat/profiles/<profile-id>/`，包含 `profile.json`、`persona.md`、`prompt.md` 和 `answers.json`。

---

## 安装

**1. 一条命令从 GitHub 安装**

```bash
git clone https://github.com/yakultyum/sorting-hat.git sorting-hat && cd sorting-hat && scripts/install-skill.sh --force
```

这条命令会先拉取完整仓库，再自动检测常见本地 skills 目录，并把完整 Sorting Hat skill 安装进去。

如果你已经在项目根目录，也可以只执行：

```bash
scripts/install-skill.sh --force
```

如需指定安装位置：

```bash
scripts/install-skill.sh --dest ~/.cursor/skills --force
```

脚本会自动检测或写入 Claude Code、Cursor、Windsurf、Codex 或其他 runtime 的 skills 目录。

安装 runtime 和输出目标是两件事：skill 可以安装在任意支持本地 skills 的工具中；生成结果仍可输出到 Claude Code、Cursor、Windsurf 或通用 system prompt。

**2. 手动安装（备用）**

```bash
mkdir -p <你的-runtime-skills-目录>/sorting-hat
cp -R sorting-hat/skill/. <你的-runtime-skills-目录>/sorting-hat/
```

> 不能只复制 `SKILL.md`：问卷网页、保存服务和题目规则都随 `skill/` 目录一起打包。
> 不同 runtime 的 skills 目录不同；请使用当前工具文档指定的安装目录。

**3. 使用**

在任意支持 skills 的 AI 编程工具中输入：

```
/sorting-hat
```

问卷末尾会要求给这套 AI 人设命名，并选择适用场景；如果不填名称，Sorting Hat 会按场景自动推荐。
已有 `persona.answers.json` 时，可在网页首页点击「修改已有维度」，只重问某一个维度并重新生成完整人设。

查看和临时使用已保存 profile：

```text
/sorting-hat profiles
/sorting-hat use <profile-id-or-name>
```

`use` 只输出本次对话可复制的 prompt，不写入项目配置。

从复盘文本沉淀 workflow：

```text
/sorting-hat reflect
```

`reflect` 只保存抽象协作规则到 `workflows/<workflow-id>.md`，不保存聊天原文。

**系统要求：** Python 3，以及一个支持本地 skills 的 AI 编程 runtime。

**发布前检查：**

```bash
python3 scripts/check-release.py
```

该检查会确认 skill 资源完整、开发副本与打包副本同步、JSON 有效、Python 文件可编译。

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
    SKILL.md          # Skill 主文件，安装到你的 runtime skills 目录
    web/
      index.html      # 问卷网页
      server.py       # 本地 HTTP 服务器
    references/
      questionnaire.md # 完整题目与心理转化规则
      output-formats.md # 输出模板与终端视觉规范
      evaluation.md    # Darwin 评估说明
    test-prompts.json  # 主路径测试 prompts
  web/                # 开发用副本
    index.html
    server.py
  scripts/
    check-release.py  # 发布前校验
    install-skill.sh  # 安装到指定 runtime skills 目录
  docs/
    PRD-sorting-hat.md
    questionnaire/
      questionnaire.md  # 完整题目与心理转化规则
    psychology-foundations.md
```

生成后的全局 profile 仓库结构：

```text
~/.sorting-hat/
  index.json
  profiles/
    <profile-id>/
      profile.json
      persona.md
      prompt.md
      answers.json
```

---

## License

MIT

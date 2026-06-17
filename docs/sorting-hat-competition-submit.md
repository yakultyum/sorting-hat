# 🎩 Sorting Hat Skill —— 为你量身定制 AI 协作伙伴

> 让 AI 不再只是通用助手，而是像那个与你性格、节奏和工作方式完美契合的人一样，与你达成高效、自然、长期的协作。

Sorting Hat 是一个运行在 Claude Code、Cursor、Windsurf 等 AI 编程工具里的本地 skill。它通过结构化问卷理解用户的认知风格，生成可持久化、可切换、可复盘的 AI 协作 profile。

核心模型：

```text
Profile = AI 人设 Persona + 协作 Workflow + 项目绑定 Project Binding
```

---

## 1. 摘要

最好的协作，不只是对方能力强，而是对方刚好懂你的节奏。

你想快，它不拖慢你；你想深挖，它陪你推理；你需要真话，它直接指出问题；你需要缓冲，它知道怎么让你听得进去。

和性格契合的人一起工作，会更高效，也更有火花。那 AI 为什么不能也这样？

Sorting Hat 最初解决的就是这个问题：不同用户需要完全不同的 AI 协作方式，但大多数 AI 默认用同一种语气、同一种结构、同一种反馈方式回答所有人。

Sorting Hat 通过问卷把用户答案转化为心理特征，再转化为 AI 行为规则，最终生成一份可写入本地工具配置的 AI 人设。同时，项目已进一步升级为多 profile 管理系统：用户可以为不同任务创建不同 AI 协作套装，并把“人如何主导 AI”的经验沉淀为 workflow。

---

## 2. 背景

### a. 项目故事与灵感来源

这个项目来自两个观察的交汇。

第一，Anthropic 关于 AI 情绪表征的研究说明：AI 的“温暖”“直率”“退让”“坚持”等行为并不是纯粹的表面措辞，而会真实影响模型输出风格。这意味着 AI 的人格可以被设计和调校。

第二，在真实工作中，同一个 AI 工具给不同人的体验差异极大。有人嫌它啰嗦，有人嫌它太短；有人觉得它太直接，有人觉得它终于说到点子上。这些差异来自人的认知结构，而不只是个人口味。

于是产生了 Sorting Hat 的构想：像哈利波特里的分院帽一样，先理解用户，再把用户分配到最适合自己的 AI 协作方式里。

### b. 为什么是现在

- AI 编程工具已经支持本地 memory、rules、system prompt 等持久化入口。
- 用户对 AI 的使用频率越来越高，但“调教 AI”的经验仍然分散在一次次对话里。
- 个人和团队都需要可复用、可迁移、可验证的 AI 协作方式。

### c. 现有方案的问题

- 普通 prompt 模板太静态，无法理解用户差异。
- 单一 system prompt 只能描述一个人设，无法管理多套协作方式。
- 聊天记录无法直接复用，真正有价值的是其中的协作规则。
- 项目配置和个人协作偏好常常分离，AI 既不了解人，也不了解项目。

---

## 3. 目标

### a. 产品目标

Sorting Hat 希望帮助用户完成三件事：

1. 找到适合自己的 AI 人设。
2. 管理多套可切换的 AI 协作 profile。
3. 把人与 AI 协作过程中的主导方式沉淀为 workflow。

### b. 为什么重要

AI 越强，越需要被正确使用。真正影响体验的，不只是模型能力，而是 AI 是否知道：

- 应该直接给结论，还是带用户推导？
- 应该先问清楚，还是直接执行？
- 应该温和反馈，还是直接指出问题？
- 应该发散探索，还是快速收敛？
- 应该如何验证，什么时候才能说“完成”？

Sorting Hat 的价值，是把这些隐性的协作偏好变成可保存、可复用、可迭代的本地资产。

---

## 4. 目标用户

### a. 主要用户

- 高频使用 Claude Code、Cursor、Windsurf 等 AI 编程工具的人。
- 希望 AI 更懂自己工作方式的开发者、产品经理、设计师、研究者。
- 经常需要在不同任务之间切换 AI 协作模式的深度用户。
- 想把个人 AI 使用经验沉淀成 workflow 或 skill 的用户。

### b. 非目标用户

- 只想偶尔问 AI 一个简单问题的轻度用户。
- 不希望配置任何本地文件或工具规则的用户。
- 需要 SaaS 云端账号体系、团队后台和数据看板的场景。

### c. 用户约束

- 必须足够简单：首次使用不能像填心理测评论文。
- 必须本地优先：用户的偏好、profile、workflow 不上传服务器。
- 必须可修改：用户随时可以只调整单个维度，而不是重来一遍。

---

## 5. 价值主张

### a. 用户要完成的工作（Jobs to Be Done）

当我开始长期使用 AI 工作时，我希望它能理解我的认知风格、工作偏好和项目上下文，这样我不用每次重新解释自己，也不用反复纠正它。

### b. 用户将获得什么

- 一份专属 AI 人设 persona。
- 多个适用于不同场景的 profile。
- 可跨项目复用的 AI 协作 workflow。
- 支持 Claude Code、Cursor、Windsurf 和通用 system prompt 的输出。
- 本地保存的 answers JSON，方便后续修改和迁移。

### c. 解决了哪些痛点

- AI 太啰嗦 / 太简短。
- AI 反馈太软 / 太冲。
- AI 不知道用户什么时候想参与推导。
- AI 不知道项目背景和协作约定。
- AI 调教经验无法沉淀，换项目就要重来。

### d. 它比现有方案好在哪里

Sorting Hat 不是给用户一段通用 prompt，而是提供一套完整流程：

```text
问卷识别 → 心理转化 → 人设生成 → 工具写入 → profile 管理 → workflow 沉淀
```

它既解决“AI 怎么和你这个人工作”，也开始解决“AI 怎么在这个项目里工作”。

---

## 6. 使用方法

### a. 安装

用户可以通过一条命令从 GitHub 安装：

```bash
git clone https://github.com/yakultyum/sorting-hat.git sorting-hat && cd sorting-hat && scripts/install-skill.sh --force
```

这条命令会先拉取 Sorting Hat 仓库，再自动检测常见本地 skills 目录，并把完整 Sorting Hat skill 安装进去。它会优先使用已存在的本地 runtime 目录，例如 Claude Code、Cursor、Windsurf、Codex 或其他 agent skills 目录。

如果你已经在项目根目录，或想指定安装位置，也可以使用：

```bash
scripts/install-skill.sh --force
scripts/install-skill.sh --dest ~/.cursor/skills --force
```

安装 runtime 和输出目标是两件事：skill 可以安装在任意支持本地 skills 的工具中；生成结果仍可输出到 Claude Code、Cursor、Windsurf 或通用 system prompt。

不能只复制 `SKILL.md`，因为网页问卷、本地 server、规则文件和测试 prompts 都是 skill 的一部分。

### b. 人设分院

```text
/sorting-hat
```

流程：

1. 选择简易版或深度版问卷。
2. 选择输出目标：Claude Code / Cursor / Windsurf / 通用 system prompt / 全部。
3. 浏览器自动打开，在网页上完成问卷。
4. 填写 profile 名称与适用场景。
5. 点击保存，人设写入目标工具配置，同时保存到全局 profile 仓库。

### c. 修改人设

已有 answers JSON 时，再次调用 `/sorting-hat` 可进入修改模式。

用户可以只修改一个维度，例如反馈方式、推理深度、格式偏好、适用场景等。系统会用完整 answers JSON 重新生成整份 persona，而不是对 Markdown 做局部替换。

### d. 查看和临时使用 profile

```text
/sorting-hat profiles
/sorting-hat use <profile-id-or-name>
```

`use` 只输出本次对话可复制的 prompt，不写项目配置。

### e. 项目初始化

```text
/sorting-hat init
```

通过终端对话收集项目用途、技术栈、常用命令、项目约定和 gotcha，生成项目级 AI 配置。

### f. 沉淀 workflow

```text
/sorting-hat reflect
```

`reflect` 不保存聊天原文，只保存抽象协作规则，包括触发场景、人的主导动作、AI 应如何响应、反例和验证 prompt。

---

## 7. 解决方案

### a. 用户旅程

#### 首次创建 profile

```text
/sorting-hat new
  ↓
回答问卷
  ↓
命名 profile
  ↓
选择适用场景
  ↓
生成 persona + answers.json + profile.json
```

#### 进入新项目

```text
/sorting-hat init
  ↓
扫描项目上下文
  ↓
确认技术栈与常用命令
  ↓
生成项目配置
```

#### 临时切换协作方式

```text
/sorting-hat use 产品共创伙伴
```

#### 沉淀协作经验

```text
/sorting-hat reflect
  ↓
从复盘文本提炼规则
  ↓
保存 workflow.md
```

### b. 核心功能

#### i. 简易版问卷

适合快速开始，重点识别推理深度、反馈方式、问题解法、情绪底色、信息密度、格式偏好、调节焦点、专业领域和称呼方式。

#### ii. 深度版问卷

融合七个心理学框架，进一步识别主动介入程度、关系定位、执行授权、输出完整性、风险呈现方式等细粒度偏好。

#### iii. 三层心理转化规则

Sorting Hat 不直接复制用户选项，而是做三层转化：

```text
用户答案 → 心理特征 → AI 行为原则
```

例如，用户选择“直接指出问题”，不会被简单写成“用户喜欢直接”。系统会转化为：负面反馈时不使用过度缓冲，不用模糊语气掩盖真实判断，直接指出风险和漏洞。

#### iv. 人设文件持久化

当前支持：

- Claude Code：`~/.claude/memory/persona.md`
- Cursor：`.cursor/rules/sorting-hat.mdc`
- Windsurf：`.windsurfrules`
- Generic：浏览器 / 终端复制纯 prompt
- All：同时生成多种格式

写入已有文件前会自动生成 `.bak` 备份，并保存原始答题数据 JSON。

#### v. 多 profile 仓库

生成后的全局结构：

```text
~/.sorting-hat/
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

这使用户可以管理多套 AI 协作方式，而不是被限制在单一人设里。

#### vi. Workflow Sorting

Workflow Sorting 沉淀的不是完整聊天记录，而是“人如何主导 AI”的抽象规则。

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

### c. 技术实现

- 类型：Markdown skill + Python 本地服务器 + HTML 网页问卷。
- 前端：单文件 HTML，负责问卷、结果预览和保存请求。
- 后端：Python HTTP server，负责本地页面托管、目标工具写入、profile 仓库写入。
- 存储：全部本地保存，不上传服务器。
- 测试：单元测试覆盖目标解析、备份、answers JSON、profile store、profiles/use/reflect。
- 发布检查：脚本校验资源完整、web 与 skill/web 同步、Python 可编译、JSON 有效。

---

## 8. 发布计划

### a. MVP（已完成核心闭环）

- skill 包自包含。
- 简易版 / 深度版问卷。
- 多目标输出。
- 自动备份与 answers JSON。
- 修改单个维度。
- profile 名称和适用场景。
- 全局 profile 仓库。
- profiles / use / reflect 最小命令。
- 发布前检查脚本和安装脚本。

### b. 第二版

- 更清晰的 profile 可视化摘要。
- `/sorting-hat bind`：为项目绑定默认 profile。
- `/sorting-hat routes`：按文件或任务类型匹配 profile。
- workflow 模板库。
- profile 导入 / 导出。

### c. 未来探索方向

- 团队级 profile：同一项目中不同角色使用不同 AI 协作方式。
- 人设漂移检测：当用户行为和当前 profile 不匹配时提示更新。
- profile 市场：分享和复用高质量 AI 协作套装。
- 从历史聊天中自动 distill workflow。

### d. 明确不做的事

- 不做独立 SaaS，优先本地运行。
- 不上传用户答案或聊天内容。
- 不把心理标签当作结论，只把它作为生成 AI 行为规则的中间层。
- 不保存完整聊天原文，只保存抽象 workflow。

---

## 附录：七个理论框架速查

| 理论框架 | 捕捉的维度 |
|---|---|
| Anthropic 情绪研究 | AI 情绪底色、温暖与诚实的平衡 |
| 荣格八维认知功能 | 推理深度、反馈方式、问题解法风格 |
| OCEAN 大五人格 | 信息完整性、风险敏感度 |
| 依恋理论 | 记忆连续性需求、错误容忍度 |
| 认知负荷理论 | 回复密度、格式偏好、专业假设深度 |
| 调节焦点理论 | 决策分析中机会与风险的呈现顺序 |
| 认知需求 + 控制点 | 推导参与深度、执行授权程度 |

---

## 一句话总结

Sorting Hat 不只是帮你找到适合你的 AI，也帮你管理多套 AI 协作方式，并把你如何主导 AI 做好项目的经验沉淀下来，跨项目复用。

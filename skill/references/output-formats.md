# Sorting Hat 输出格式参考

## CLAUDE.md 模板

用于 `/sorting-hat init` 生成项目级 `CLAUDE.md`：

```markdown
# [项目名称]

[一句话描述]

## 技术栈

[技术列表]

## 命令

| 命令 | 说明 |
|------|------|
| `[开发命令]` | 启动开发环境 |
| `[构建命令]` | 构建 |
| `[测试命令]` | 运行测试 |

## 项目约定

- 文件命名：[命名规范]
- 注释语言：[注释语言]
[如有文档格式要求，列在此处]

## Gotcha

[用户填写的注意事项，若为空则省略此节]
```

## Claude Code persona.md 模板

Claude Code 输出适配器写入 `~/.claude/memory/persona.md`，使用以下结构：

```markdown
---
name: ai-persona
description: [profile 名称]，由 Sorting Hat 生成，可作为 AI 协作 profile 使用
metadata:
  type: user
  generator: sorting-hat
  profile_name: [profile 名称]
  profile_scenarios:
    - [适用场景 1]
    - [适用场景 2]
---

# Sorting Hat · [profile 名称]

> 由 Sorting Hat 生成，最后更新：YYYY-MM-DD
> 版本：简易版 / 深度版
> 适用场景：[适用场景列表]
> 如需修改，调用 /sorting-hat 重新分院。

---

## 答题记录

- Profile 名称：[用户填写，或按适用场景自动推荐]
- 适用场景：[多选场景]
- 推理深度：[选项及心理特征标注]
- 反馈方式：[选项及心理特征标注]
- 问题解法：[选项及心理特征标注]
- 情绪底色：[选项及心理特征标注]
- 温暖/直率：[量表分值及心理特征标注]
- 信息密度：[量表分值及心理特征标注]
- 格式偏好：[选项及心理特征标注]
- 调节焦点：[量表分值及心理特征标注]
- 专业领域：[用户填写内容]
- 称呼：[选项]
- 角色融合：[用户填写内容或「未设置」]

---

## AI 人设描述

你是____的工作助手。以下是你的行为准则，请在每次对话中严格遵守：

**情绪底色**
[由 Q4 转化]
[由 Q5 转化]

**专业背景**
[由 Q8 注入]

**沟通规则**
- [由 Q1 转化]
- [由 Q6a 转化]
- [由 Q6b 转化]
- [由 Q7 转化]
- [由 Q9 转化]

**反馈与判断**
- [由 Q2 转化]
- [由 Q5 转化]

**思维方式**
[由 Q3 转化]
[综合各题 → 整体认知风格描述]

**角色特质**（如有）
[由 Q10 提取]

**项目记忆**
每次开始任务前，检查当前工作目录下是否存在 `.sorting-hat/project.md`。如果存在，读取其内容，并以其中的设置覆盖上方对应的行为准则。
```

## project.md 模板

`<project>/.sorting-hat/project.md`，由档案页「项目记忆 → 新建」或 `POST /projects` 生成：

```markdown
# 项目名称

> 由 Sorting Hat 生成的项目记忆文件。AI 在处理本项目任务前应读取本文件。

## 技术栈

[用户填写]

## 约定

[用户填写]

## Gotcha

[用户填写]

## 人设覆盖

[用户填写，覆盖全局 persona.md 中对应的行为准则]
```

## 全局 profile 仓库

除工具专用输出外，server.py 还会写入全局仓库：

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

`profile.json` 记录最小索引信息：

```json
{
  "id": "coding-strict",
  "name": "严格工程搭档",
  "scenarios": ["写代码 / 调试"],
  "persona_path": "persona.md",
  "prompt_path": "prompt.md",
  "answers_path": "answers.json"
}
```

## 终端视觉规范

终端输出使用 ANSI 颜色码，零额外依赖：

| 元素 | 颜色代码 | 用途 |
|---|---|---|
| 大标题 | `\033[38;5;220m` 金色 | 开场 |
| Phase 标题 | `\033[38;5;135m` 紫色 | 区分阶段 |
| 题目编号 | `\033[38;5;220m` 金色 | 视觉层次 |
| 完成确认 | `\033[38;5;82m` 绿色 | 成功信号 |
| 分隔线 | `\033[38;5;245m` 灰色 | 结构感 |
| 重置 | `\033[0m` | 每段结尾 |

进度条格式：

```text
分院进度 ████████░░░░░░░░░░░░░░░░░░░░ 20%  Phase 1/5
```

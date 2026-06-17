# Sorting Hat 评估说明

使用 `test-prompts.json` 做 Darwin 第 8 维「实测表现」评估。

## 执行方式

对每个测试 prompt，评估 agent 应读取 `SKILL.md` 后模拟执行，不需要真的打开浏览器或写用户配置文件。记录：

- 是否选对路径 A/B/C
- 是否执行快速自检
- 是否在写入前 checkpoint
- 是否遵守目标输出适配器
- 是否命中反模式黑名单
- 是否按失败处理表处理异常

## 评分规则

每个 prompt 10 分：

| 分数 | 标准 |
|---|---|
| 9-10 | 完整命中 expected，无 failure_signals |
| 7-8 | 主路径正确，遗漏 1-2 个次要 expected |
| 5-6 | 能完成任务，但漏掉 checkpoint、备份或失败分支 |
| 3-4 | 选错局部流程，或输出格式目标混淆 |
| 1-2 | 违背黑名单，如无确认覆盖文件、从 Markdown 猜答案 |

最终实测表现分 = 所有 prompt 平均分。

## 必测用例

- `persona-first-run`：首次分院
- `persona-dimension-edit`：单维度修改
- `project-init`：生成项目 `CLAUDE.md`

若只能做 dry-run，在评估报告中标注 `dry_run=true`。

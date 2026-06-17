import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "web" / "server.py"

spec = importlib.util.spec_from_file_location("sorting_hat_server", SERVER_PATH)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


def json_text(data):
    return json.dumps(data, ensure_ascii=False, indent=2)


class ServerTargetsTest(unittest.TestCase):
    def test_profile_id_from_name_handles_ascii_and_cjk(self):
        self.assertEqual(server.profile_id_from_name("Coding Strict"), "coding-strict")
        self.assertEqual(server.profile_id_from_name("严格工程搭档"), "yan-ge-gong-cheng-da-dang")
        self.assertEqual(server.profile_id_from_name("!!!"), "profile")

    def test_resolve_outputs_for_claude_uses_persona_file(self):
        with mock.patch.dict("os.environ", {"HOME": "/tmp/sorting-hat-home"}, clear=False):
            outputs = server.resolve_outputs("claude", None, Path("/tmp/project"))

        self.assertEqual(
            outputs,
            [
                server.OutputTarget(
                    name="Claude Code",
                    path=Path("/tmp/sorting-hat-home/.claude/memory/persona.md"),
                    content_kind="file",
                )
            ],
        )

    def test_resolve_outputs_for_all_writes_supported_tool_files(self):
        with mock.patch.dict("os.environ", {"HOME": "/tmp/sorting-hat-home"}, clear=False):
            project = Path("/tmp/project").resolve()
            outputs = server.resolve_outputs("all", None, project)

        self.assertEqual(
            outputs,
            [
                server.OutputTarget("Claude Code", Path("/tmp/sorting-hat-home/.claude/memory/persona.md"), "file"),
                server.OutputTarget("Cursor", project / ".cursor/rules/sorting-hat.mdc", "prompt"),
                server.OutputTarget("Windsurf", project / ".windsurfrules", "prompt"),
                server.OutputTarget("通用 system prompt", None, "prompt"),
            ],
        )

    def test_write_outputs_creates_backups_answers_and_prompt_outputs(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            old_file = tmp_path / "persona.md"
            old_file.write_text("old", encoding="utf-8")
            cursor_file = tmp_path / ".cursor" / "rules" / "sorting-hat.mdc"
            outputs = [
                server.OutputTarget("Claude Code", old_file, "file"),
                server.OutputTarget("Cursor", cursor_file, "prompt"),
                server.OutputTarget("通用 system prompt", None, "prompt"),
            ]

            result = server.write_outputs(outputs, "FULL FILE", "PURE PROMPT", {"q1": {"trait": "test"}})

            self.assertEqual(old_file.read_text(encoding="utf-8"), "FULL FILE")
            self.assertEqual(old_file.with_suffix(".md.bak").read_text(encoding="utf-8"), "old")
            self.assertEqual(old_file.with_name("persona.answers.json").read_text(encoding="utf-8"), '{\n  "q1": {\n    "trait": "test"\n  }\n}')
            self.assertEqual(cursor_file.read_text(encoding="utf-8"), "PURE PROMPT")
            self.assertEqual(cursor_file.with_name("sorting-hat.answers.json").read_text(encoding="utf-8"), '{\n  "q1": {\n    "trait": "test"\n  }\n}')
            self.assertEqual(result[0]["path"], str(old_file))
            self.assertEqual(result[0]["answersPath"], str(old_file.with_name("persona.answers.json")))
            self.assertEqual(result[1]["path"], str(cursor_file))
            self.assertEqual(result[2]["content"], "PURE PROMPT")

    def test_write_outputs_preserves_profile_metadata_in_answers_json(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            output_file = Path(directory) / "persona.md"
            outputs = [server.OutputTarget("Claude Code", output_file, "file")]
            answers = {
                "version": "lite",
                "answers": {
                    "profile_name": {"text": "严格工程搭档"},
                    "profile_scenarios": {
                        "values": ["写代码 / 调试", "skill / prompt / workflow 优化"]
                    },
                },
                "profile": {
                    "name": "严格工程搭档",
                    "scenarios": ["写代码 / 调试", "skill / prompt / workflow 优化"],
                },
            }

            server.write_outputs(outputs, "FULL FILE", "PURE PROMPT", answers)

            saved = output_file.with_name("persona.answers.json").read_text(encoding="utf-8")
            self.assertIn('"profile_name"', saved)
            self.assertIn('"profile_scenarios"', saved)
            self.assertIn('"严格工程搭档"', saved)
            self.assertIn('"skill / prompt / workflow 优化"', saved)

    def test_write_profile_store_creates_profile_files_and_index(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            store_dir = Path(directory) / ".sorting-hat"
            answers = {
                "version": "lite",
                "answers": {
                    "profile_name": {"text": "严格工程搭档"},
                    "profile_scenarios": {"values": ["写代码 / 调试"]},
                },
                "profile": {"name": "严格工程搭档", "scenarios": ["写代码 / 调试"]},
            }

            result = server.write_profile_store(store_dir, "FULL FILE", "PURE PROMPT", answers)

            profile_dir = store_dir / "profiles" / "yan-ge-gong-cheng-da-dang"
            self.assertEqual(result["profileId"], "yan-ge-gong-cheng-da-dang")
            self.assertEqual(Path(result["profileDir"]), profile_dir)
            self.assertEqual((profile_dir / "persona.md").read_text(encoding="utf-8"), "FULL FILE")
            self.assertEqual((profile_dir / "answers.json").read_text(encoding="utf-8"), json_text(answers))

            profile = json.loads((profile_dir / "profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["id"], "yan-ge-gong-cheng-da-dang")
            self.assertEqual(profile["name"], "严格工程搭档")
            self.assertEqual(profile["scenarios"], ["写代码 / 调试"])
            self.assertEqual(profile["persona_path"], "persona.md")
            self.assertEqual(profile["answers_path"], "answers.json")

            index = json.loads((store_dir / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["profiles"][0]["id"], "yan-ge-gong-cheng-da-dang")
            self.assertEqual(index["default_profile"], "yan-ge-gong-cheng-da-dang")

    def test_write_outputs_records_profile_store_result(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            output_file = tmp_path / "persona.md"
            store_dir = tmp_path / ".sorting-hat"
            answers = {
                "version": "lite",
                "answers": {"profile_name": {"text": "Product Partner"}},
                "profile": {"name": "Product Partner", "scenarios": ["产品设计 / 用户动线"]},
            }

            result = server.write_outputs(
                [server.OutputTarget("Claude Code", output_file, "file")],
                "FULL FILE",
                "PURE PROMPT",
                answers,
                profile_store_dir=store_dir,
            )

            self.assertEqual(result[0]["profileId"], "product-partner")
            self.assertTrue((store_dir / "profiles" / "product-partner" / "profile.json").exists())

    def test_list_profiles_reads_index_and_profile_files(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            store_dir = Path(directory) / ".sorting-hat"
            server.write_profile_store(
                store_dir,
                "ENGINEERING PERSONA",
                "ENGINEERING PROMPT",
                {
                    "version": "lite",
                    "answers": {"profile_name": {"text": "严格工程搭档"}},
                    "profile": {"name": "严格工程搭档", "scenarios": ["写代码 / 调试"]},
                },
            )
            server.write_profile_store(
                store_dir,
                "PRODUCT PERSONA",
                "PRODUCT PROMPT",
                {
                    "version": "lite",
                    "answers": {"profile_name": {"text": "Product Partner"}},
                    "profile": {"name": "Product Partner", "scenarios": ["产品设计 / 用户动线"]},
                },
            )

            profiles = server.list_profiles(store_dir)

            self.assertEqual([profile["id"] for profile in profiles], ["yan-ge-gong-cheng-da-dang", "product-partner"])
            self.assertEqual(profiles[0]["name"], "严格工程搭档")
            self.assertEqual(profiles[1]["scenarios"], ["产品设计 / 用户动线"])

    def test_use_profile_resolves_by_id_or_name_and_returns_prompt(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            store_dir = Path(directory) / ".sorting-hat"
            server.write_profile_store(
                store_dir,
                "FULL FILE",
                "PURE PROMPT",
                {
                    "version": "lite",
                    "answers": {"profile_name": {"text": "Product Partner"}},
                    "profile": {"name": "Product Partner", "scenarios": ["产品设计 / 用户动线"]},
                },
            )

            by_id = server.use_profile(store_dir, "product-partner")
            by_name = server.use_profile(store_dir, "Product Partner")

            self.assertEqual(by_id["id"], "product-partner")
            self.assertEqual(by_id["prompt"], "PURE PROMPT")
            self.assertEqual(by_name["persona"], "FULL FILE")

    def test_use_profile_reports_missing_profile(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                server.use_profile(Path(directory) / ".sorting-hat", "missing")

    def test_profiles_and_use_cli_commands(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            store_dir = Path(directory) / ".sorting-hat"
            server.write_profile_store(
                store_dir,
                "FULL FILE",
                "PURE PROMPT",
                {
                    "version": "lite",
                    "answers": {"profile_name": {"text": "CLI Partner"}},
                    "profile": {"name": "CLI Partner", "scenarios": ["日常助理 / 通用协作"]},
                },
            )

            profiles = subprocess.run(
                [sys.executable, str(SERVER_PATH), "profiles", "--store-dir", str(store_dir)],
                text=True,
                capture_output=True,
                check=True,
            )
            selected = subprocess.run(
                [sys.executable, str(SERVER_PATH), "use", "cli-partner", "--store-dir", str(store_dir)],
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("cli-partner", profiles.stdout)
            self.assertIn("CLI Partner", profiles.stdout)
            self.assertIn("PURE PROMPT", selected.stdout)

    def test_build_workflow_reflection_creates_abstract_rule_not_raw_log(self):
        source = "用户多次说继续优化，并要求沿用 Darwin rubric、小步修改、运行验证、给出复评分。"

        workflow = server.build_workflow_reflection(source, title="连续优化规则")

        self.assertIn("# 连续优化规则", workflow)
        self.assertIn("触发场景", workflow)
        self.assertIn("人的主导动作", workflow)
        self.assertIn("AI 应如何响应", workflow)
        self.assertIn("验证 prompt", workflow)
        self.assertIn("继续优化", workflow)
        self.assertNotIn("完整聊天记录", workflow)

    def test_save_workflow_reflection_writes_profile_workflow(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            store_dir = Path(directory) / ".sorting-hat"
            server.write_profile_store(
                store_dir,
                "FULL FILE",
                "PURE PROMPT",
                {
                    "version": "lite",
                    "answers": {"profile_name": {"text": "Darwin 优化器"}},
                    "profile": {"name": "Darwin 优化器", "scenarios": ["skill / prompt / workflow 优化"]},
                },
            )

            result = server.save_workflow_reflection(
                store_dir,
                "darwin-you-hua-qi",
                "用户要求连续优化时沿用上一轮评分框架，选择一个维度，小步修改并验证。",
                title="连续优化",
            )

            workflow_path = store_dir / "profiles" / "darwin-you-hua-qi" / "workflows" / "lian-xu-you-hua.md"
            self.assertEqual(Path(result["path"]), workflow_path)
            self.assertIn("连续优化", workflow_path.read_text(encoding="utf-8"))
            self.assertIn("workflows/lian-xu-you-hua.md", json.loads((store_dir / "profiles" / "darwin-you-hua-qi" / "profile.json").read_text(encoding="utf-8"))["workflows"])

    def test_write_profile_store_preserves_existing_workflows(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            store_dir = Path(directory) / ".sorting-hat"
            answers = {
                "version": "lite",
                "answers": {"profile_name": {"text": "QA Partner"}},
                "profile": {"name": "QA Partner", "scenarios": ["写代码 / 调试"]},
            }
            server.write_profile_store(store_dir, "FULL FILE", "PURE PROMPT", answers)
            server.save_workflow_reflection(store_dir, "qa-partner", "用户要求验证后再声明完成。", title="验证优先")
            server.write_profile_store(store_dir, "UPDATED FILE", "UPDATED PROMPT", answers)

            profile = json.loads((store_dir / "profiles" / "qa-partner" / "profile.json").read_text(encoding="utf-8"))

            self.assertIn("workflows/yan-zheng-you-xian.md", profile["workflows"])

    def test_reflect_cli_command(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            store_dir = tmp_path / ".sorting-hat"
            source_file = tmp_path / "reflection.txt"
            source_file.write_text("用户要求验证后再声明完成，并要求列出证据。", encoding="utf-8")
            server.write_profile_store(
                store_dir,
                "FULL FILE",
                "PURE PROMPT",
                {
                    "version": "lite",
                    "answers": {"profile_name": {"text": "QA Partner"}},
                    "profile": {"name": "QA Partner", "scenarios": ["写代码 / 调试"]},
                },
            )

            reflected = subprocess.run(
                [
                    sys.executable,
                    str(SERVER_PATH),
                    "reflect",
                    "qa-partner",
                    "--source",
                    str(source_file),
                    "--title",
                    "验证优先",
                    "--store-dir",
                    str(store_dir),
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("workflow 已保存", reflected.stdout)
            self.assertTrue((store_dir / "profiles" / "qa-partner" / "workflows" / "yan-zheng-you-xian.md").exists())

    def test_read_saved_state_uses_first_existing_answers_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            missing = server.OutputTarget("Claude Code", tmp_path / "missing.md", "file")
            persona = tmp_path / "persona.md"
            persona.write_text("persona", encoding="utf-8")
            persona.with_name("persona.answers.json").write_text('{"version":"lite","answers":{"q1":{"trait":"x"}}}', encoding="utf-8")

            state = server.read_saved_state([missing, server.OutputTarget("Claude Code", persona, "file")])

            self.assertEqual(state["ok"], True)
            self.assertEqual(state["version"], "lite")
            self.assertEqual(state["answers"], {"q1": {"trait": "x"}})
            self.assertEqual(state["answersPath"], str(persona.with_name("persona.answers.json")))

    def test_read_saved_state_returns_profile_metadata(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            persona = Path(directory) / "persona.md"
            persona.write_text("persona", encoding="utf-8")
            persona.with_name("persona.answers.json").write_text(
                '{"version":"lite","answers":{"profile_name":{"text":"产品共创伙伴"}},"profile":{"name":"产品共创伙伴","scenarios":["产品设计 / 用户动线"]}}',
                encoding="utf-8",
            )

            state = server.read_saved_state([server.OutputTarget("Claude Code", persona, "file")])

            self.assertEqual(state["ok"], True)
            self.assertEqual(state["profile"], {"name": "产品共创伙伴", "scenarios": ["产品设计 / 用户动线"]})

    def test_read_saved_state_reports_missing_answers(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            output = server.OutputTarget("Cursor", Path(directory) / ".cursor/rules/sorting-hat.mdc", "prompt")

            state = server.read_saved_state([output])

            self.assertEqual(state["ok"], False)
            self.assertIn("未找到", state["error"])


if __name__ == "__main__":
    unittest.main()

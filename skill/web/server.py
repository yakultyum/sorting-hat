#!/usr/bin/env python3
"""
Sorting Hat · 本地服务器
接收浏览器 POST 请求，将生成的人设内容写入目标工具。
"""
import argparse
from dataclasses import dataclass
import http.server
import json
import os
from pathlib import Path
import re
import threading
from typing import Optional
import webbrowser

PORT = 7432
DEFAULT_SAVE_PATH = Path.home() / ".claude" / "memory" / "persona.md"
DEFAULT_PROFILE_STORE_DIR = Path.home() / ".sorting-hat"
PINYIN_SYLLABLES = {
    "严格工程搭档": "yan-ge-gong-cheng-da-dang",
    "产品共创伙伴": "chan-pin-gong-chuang-huo-ban",
    "写作编辑顾问": "xie-zuo-bian-ji-gu-wen",
    "Darwin 优化器": "darwin-you-hua-qi",
    "研究分析顾问": "yan-jiu-fen-xi-gu-wen",
    "通用协作伙伴": "tong-yong-xie-zuo-huo-ban",
    "连续优化": "lian-xu-you-hua",
    "连续优化规则": "lian-xu-you-hua-gui-ze",
    "验证优先": "yan-zheng-you-xian",
}
TARGET_ALIASES = {
    "claude": "claude",
    "claude-code": "claude",
    "cursor": "cursor",
    "windsurf": "windsurf",
    "generic": "generic",
    "通用": "generic",
    "all": "all",
    "全部": "all",
}


@dataclass(frozen=True)
class OutputTarget:
    name: str
    path: Optional[Path]
    content_kind: str


def normalize_target(target):
    key = (target or "claude").strip().lower()
    if key not in TARGET_ALIASES:
        supported = ", ".join(sorted(TARGET_ALIASES))
        raise ValueError(f"未知输出目标：{target}。支持：{supported}")
    return TARGET_ALIASES[key]


def resolve_outputs(target, output_path, project_dir):
    target = normalize_target(target)
    project_dir = Path(project_dir).expanduser().resolve()
    custom_path = Path(output_path).expanduser().resolve() if output_path else None

    if custom_path:
        return [OutputTarget("自定义路径", custom_path, "file")]

    outputs = {
        "claude": [OutputTarget("Claude Code", Path.home() / ".claude" / "memory" / "persona.md", "file")],
        "cursor": [OutputTarget("Cursor", project_dir / ".cursor" / "rules" / "sorting-hat.mdc", "prompt")],
        "windsurf": [OutputTarget("Windsurf", project_dir / ".windsurfrules", "prompt")],
        "generic": [OutputTarget("通用 system prompt", None, "prompt")],
    }
    if target == "all":
        return outputs["claude"] + outputs["cursor"] + outputs["windsurf"] + outputs["generic"]
    return outputs[target]


def backup_existing_file(path):
    if not path.exists():
        return None

    backup_path = path.with_suffix(path.suffix + ".bak") if path.suffix else path.with_name(path.name + ".bak")
    backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup_path


def answers_path_for(output_path):
    if output_path.name == "persona.md":
        return output_path.with_name("persona.answers.json")
    return output_path.with_name("sorting-hat.answers.json")


def profile_id_from_name(name):
    clean_name = (name or "").strip()
    if clean_name in PINYIN_SYLLABLES:
        return PINYIN_SYLLABLES[clean_name]

    slug = re.sub(r"[^a-z0-9]+", "-", clean_name.lower()).strip("-")
    return slug or "profile"


def profile_metadata_from_answers(answers):
    if not isinstance(answers, dict):
        return {"name": "通用协作伙伴", "scenarios": ["日常助理 / 通用协作"]}

    profile = answers.get("profile") or {}
    nested_answers = answers.get("answers") or answers
    name = profile.get("name") or (nested_answers.get("profile_name") or {}).get("text") or "通用协作伙伴"
    scenarios = profile.get("scenarios") or (nested_answers.get("profile_scenarios") or {}).get("values") or ["日常助理 / 通用协作"]
    return {"name": name, "scenarios": scenarios}


def write_profile_store(store_dir, file_content, prompt_content, answers):
    profile = profile_metadata_from_answers(answers)
    profile_id = profile_id_from_name(profile["name"])
    store_dir = Path(store_dir).expanduser()
    profile_dir = store_dir / "profiles" / profile_id
    profile_dir.mkdir(parents=True, exist_ok=True)
    profile_json_path = profile_dir / "profile.json"
    existing_workflows = []
    if profile_json_path.exists():
        existing_profile = json.loads(profile_json_path.read_text(encoding="utf-8"))
        existing_workflows = existing_profile.get("workflows", [])

    profile_payload = {
        "id": profile_id,
        "name": profile["name"],
        "scenarios": profile["scenarios"],
        "persona_path": "persona.md",
        "prompt_path": "prompt.md",
        "answers_path": "answers.json",
    }
    if existing_workflows:
        profile_payload["workflows"] = existing_workflows
    profile_json_path.write_text(json.dumps(profile_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (profile_dir / "persona.md").write_text(file_content, encoding="utf-8")
    (profile_dir / "prompt.md").write_text(prompt_content, encoding="utf-8")
    (profile_dir / "answers.json").write_text(json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8")

    index_path = store_dir / "index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index = {"version": 1, "default_profile": profile_id, "profiles": []}
    existing_profiles = [item for item in index.get("profiles", []) if item.get("id") != profile_id]
    existing_profiles.append({"id": profile_id, "name": profile["name"], "scenarios": profile["scenarios"], "path": f"profiles/{profile_id}/profile.json"})
    index["version"] = index.get("version") or 1
    index["default_profile"] = index.get("default_profile") or profile_id
    index["profiles"] = existing_profiles
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"profileId": profile_id, "profileDir": str(profile_dir), "profilePath": str(profile_dir / "profile.json")}


def list_profiles(store_dir=DEFAULT_PROFILE_STORE_DIR):
    store_dir = Path(store_dir).expanduser()
    index_path = store_dir / "index.json"
    if not index_path.exists():
        return []

    index = json.loads(index_path.read_text(encoding="utf-8"))
    profiles = []
    for item in index.get("profiles", []):
        profile_path = store_dir / item.get("path", f"profiles/{item.get('id')}/profile.json")
        if profile_path.exists():
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
        else:
            profile = item
        profile["is_default"] = profile.get("id") == index.get("default_profile")
        profile["profile_path"] = str(profile_path)
        profiles.append(profile)
    return profiles


def use_profile(store_dir, selector):
    selector = (selector or "").strip()
    if not selector:
        raise ValueError("请提供 profile id 或名称")

    normalized_selector = selector.lower()
    profiles = list_profiles(store_dir)
    for profile in profiles:
        if profile.get("id", "").lower() == normalized_selector or profile.get("name", "").lower() == normalized_selector:
            profile_dir = Path(profile["profile_path"]).parent
            prompt_path = profile_dir / profile.get("prompt_path", "prompt.md")
            persona_path = profile_dir / profile.get("persona_path", "persona.md")
            return {
                **profile,
                "prompt": prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else "",
                "persona": persona_path.read_text(encoding="utf-8") if persona_path.exists() else "",
            }
    raise ValueError(f"未找到 profile：{selector}")


def format_profiles(profiles):
    if not profiles:
        return "尚未创建 profile。请先运行 /sorting-hat new 或 /sorting-hat 完成一次分院。"

    lines = ["🎩 Sorting Hat Profiles", ""]
    for profile in profiles:
        marker = "*" if profile.get("is_default") else "-"
        scenarios = "、".join(profile.get("scenarios") or []) or "未设置场景"
        lines.append(f"{marker} {profile.get('id')} · {profile.get('name')} · {scenarios}")
    return "\n".join(lines)


def format_use_profile(profile):
    scenarios = "、".join(profile.get("scenarios") or []) or "未设置场景"
    return f"""🎩 已选择 profile：{profile.get('name')} ({profile.get('id')})
适用场景：{scenarios}

将下面内容作为本次对话的 system prompt / 自定义指令使用：

{profile.get('prompt', '')}"""


def infer_workflow_rule(source_text):
    source_text = (source_text or "").strip()
    if "继续优化" in source_text or "连续优化" in source_text or "Darwin" in source_text:
        return {
            "trigger": "用户要求继续优化、复评分、沿用上一轮评估框架，或要求对 skill/prompt/workflow 做连续小步迭代。",
            "human_action": "用户指定评估框架、质量维度或验证方式，并要求 AI 收敛到一个明确改动点。",
            "ai_response": "沿用上一轮框架，选择一个明确维度，小步修改，运行验证，给出复评分和下一轮建议。",
            "anti_example": "泛泛发散、重开一套评估标准、一次性大改多个方向，或未验证就宣布优化完成。",
            "verification_prompt": "继续优化：沿用上一轮评分框架，只选择一个维度小步修改，运行验证，并给出复评分。",
        }
    if "验证" in source_text or "证据" in source_text or "完成" in source_text:
        return {
            "trigger": "用户要求 AI 在声明完成、修复或通过前先验证，并给出可检查证据。",
            "human_action": "用户要求先运行验证命令、读取输出，再基于证据汇报状态。",
            "ai_response": "先明确验证命令，运行并读取结果；只有输出确认通过后才声明完成，否则报告实际失败点。",
            "anti_example": "未运行验证就说应该好了、可能通过，或只凭代码变更推断任务完成。",
            "verification_prompt": "完成前先验证：运行相关检查，读取输出，并用证据说明是否通过。",
        }
    return {
        "trigger": "用户纠正 AI 的协作方式，要求后续在相似场景复用该工作习惯。",
        "human_action": "用户指出期望的收敛方式、质量标准、工具使用或验证要求。",
        "ai_response": "将用户要求抽象成可复用规则；后续遇到同类场景时先按该规则行动，再汇报结果。",
        "anti_example": "保存原始对话、复述零散细节，或把一次性偏好误当成永久规则。",
        "verification_prompt": "根据这条协作规则处理一个相似任务，并说明触发场景、执行动作和验证方式。",
    }


def build_workflow_reflection(source_text, title="协作复盘规则"):
    rule = infer_workflow_rule(source_text)
    return f"""# {title}

> 由 Sorting Hat reflect 生成。该文件只保存抽象协作规则，不保存聊天原文。

## 触发场景

{rule['trigger']}

## 人的主导动作

{rule['human_action']}

## AI 应如何响应

{rule['ai_response']}

## 反例

{rule['anti_example']}

## 验证 prompt

{rule['verification_prompt']}
"""


def save_workflow_reflection(store_dir, profile_selector, source_text, title="协作复盘规则"):
    profile = use_profile(store_dir, profile_selector)
    profile_dir = Path(profile["profile_path"]).parent
    workflow_id = profile_id_from_name(title)
    workflows_dir = profile_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    workflow_path = workflows_dir / f"{workflow_id}.md"
    workflow = build_workflow_reflection(source_text, title)
    workflow_path.write_text(workflow, encoding="utf-8")

    profile_json_path = Path(profile["profile_path"])
    profile_payload = json.loads(profile_json_path.read_text(encoding="utf-8"))
    workflows = profile_payload.get("workflows", [])
    workflow_ref = f"workflows/{workflow_id}.md"
    if workflow_ref not in workflows:
        workflows.append(workflow_ref)
    profile_payload["workflows"] = workflows
    profile_json_path.write_text(json.dumps(profile_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"profileId": profile.get("id"), "workflowId": workflow_id, "path": str(workflow_path)}


def read_saved_state(outputs):
    checked = []
    for output in outputs:
        if output.path is None:
            continue
        answers_path = answers_path_for(output.path)
        checked.append(str(answers_path))
        if not answers_path.exists():
            continue

        data = json.loads(answers_path.read_text(encoding="utf-8"))
        if "answers" in data:
            answers = data.get("answers") or {}
            version = data.get("version") or "lite"
        else:
            answers = data
            version = data.get("version") or "lite" if isinstance(data, dict) else "lite"
        state = {
            "ok": True,
            "version": version,
            "answers": answers,
            "answersPath": str(answers_path),
            "target": output.name,
        }
        if isinstance(data, dict) and data.get("profile"):
            state["profile"] = data.get("profile")
        return state

    return {"ok": False, "error": "未找到已保存的答题数据", "checked": checked}


def write_outputs(outputs, file_content, prompt_content, answers=None, profile_store_dir=None):
    result = []
    profile_store_result = None
    if answers is not None and profile_store_dir is not None:
        profile_store_result = write_profile_store(profile_store_dir, file_content, prompt_content, answers)
    for output in outputs:
        content = file_content if output.content_kind == "file" else prompt_content
        item = {"name": output.name, "kind": output.content_kind}
        if output.path is None:
            item["content"] = content
            if profile_store_result is not None:
                item.update(profile_store_result)
            result.append(item)
            continue

        output.path.parent.mkdir(parents=True, exist_ok=True)
        backup_path = backup_existing_file(output.path)
        output.path.write_text(content, encoding="utf-8")
        item["path"] = str(output.path)
        if answers is not None:
            answers_path = answers_path_for(output.path)
            answers_path.write_text(json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8")
            item["answersPath"] = str(answers_path)
        if profile_store_result is not None:
            item.update(profile_store_result)
        if backup_path:
            item["backup"] = str(backup_path)
        result.append(item)
    return result


class Handler(http.server.BaseHTTPRequestHandler):
    outputs = [OutputTarget("Claude Code", DEFAULT_SAVE_PATH, "file")]

    def do_GET(self):
        # 提供静态文件
        base = os.path.dirname(os.path.abspath(__file__))
        path = self.path.split("?")[0]
        if path == "/state":
            self.send_json(read_saved_state(self.outputs))
            return
        if path == "/" or path == "/index.html":
            filepath = os.path.join(base, "index.html")
            ctype = "text/html"
        else:
            self.send_response(404)
            self.end_headers()
            return

        try:
            with open(filepath, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{ctype}; charset=utf-8")
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def send_json(self, payload, status=200):
        resp = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(resp))
        self.end_headers()
        self.wfile.write(resp)

    def do_POST(self):
        if self.path != "/save":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
            file_content = data.get("content", "")
            prompt_content = data.get("prompt", file_content)
            answers = data.get("answers")
            written = write_outputs(self.outputs, file_content, prompt_content, answers, DEFAULT_PROFILE_STORE_DIR)

            resp = json.dumps({"ok": True, "outputs": written}, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", len(resp))
            self.end_headers()
            self.wfile.write(resp)

            print("\n✓ 人设已生成")
            for item in written:
                if "path" in item:
                    print(f"  {item['name']} → {item['path']}")
                    if "backup" in item:
                        print(f"    旧文件备份 → {item['backup']}")
                else:
                    print(f"  {item['name']} → 已返回浏览器，可复制使用")
            print("  分院仪式完成，服务器即将关闭…\n")

            # 延迟关闭，让响应先发出去
            threading.Thread(target=self._shutdown, daemon=True).start()

        except Exception as e:
            err = json.dumps({"ok": False, "error": str(e)}).encode()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", len(err))
            self.end_headers()
            self.wfile.write(err)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _shutdown(self):
        import time
        time.sleep(0.8)
        self.server.shutdown()

    def log_message(self, fmt, *args):
        # 只打印 POST 请求，过滤 GET 的噪音
        if args and "POST" in str(args[0]):
            print(f"  {args[0]}")


def parse_args():
    parser = argparse.ArgumentParser(description="Sorting Hat 本地保存服务")
    subparsers = parser.add_subparsers(dest="command")

    profiles_parser = subparsers.add_parser("profiles", help="列出已保存的 profiles")
    profiles_parser.add_argument("--store-dir", default=os.environ.get("SORTING_HAT_STORE_DIR", str(DEFAULT_PROFILE_STORE_DIR)))

    use_parser = subparsers.add_parser("use", help="读取某个 profile 的 prompt")
    use_parser.add_argument("profile", help="profile id 或名称")
    use_parser.add_argument("--store-dir", default=os.environ.get("SORTING_HAT_STORE_DIR", str(DEFAULT_PROFILE_STORE_DIR)))

    reflect_parser = subparsers.add_parser("reflect", help="从复盘文本生成 profile workflow")
    reflect_parser.add_argument("profile", help="profile id 或名称")
    reflect_parser.add_argument("--source", required=True, help="复盘文本文件路径；只读取后生成抽象规则，不保存原文")
    reflect_parser.add_argument("--title", default="协作复盘规则", help="workflow 标题")
    reflect_parser.add_argument("--store-dir", default=os.environ.get("SORTING_HAT_STORE_DIR", str(DEFAULT_PROFILE_STORE_DIR)))

    parser.add_argument(
        "--target",
        default=os.environ.get("SORTING_HAT_TARGET", "claude"),
        help="输出目标：claude、cursor、windsurf、generic、all",
    )
    parser.add_argument(
        "--output",
        default=os.environ.get("SORTING_HAT_OUTPUT"),
        help="自定义完整输出路径。设置后会覆盖 --target 的默认路径。",
    )
    parser.add_argument(
        "--project-dir",
        default=os.environ.get("SORTING_HAT_PROJECT_DIR", os.getcwd()),
        help="Cursor/Windsurf 输出所使用的项目目录，默认当前目录。",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("SORTING_HAT_PORT", PORT)),
        help="本地服务端口，默认 7432。",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.command == "profiles":
        print(format_profiles(list_profiles(args.store_dir)))
        return
    if args.command == "use":
        try:
            print(format_use_profile(use_profile(args.store_dir, args.profile)))
        except ValueError as error:
            raise SystemExit(str(error))
        return
    if args.command == "reflect":
        source_text = Path(args.source).expanduser().read_text(encoding="utf-8")
        try:
            result = save_workflow_reflection(args.store_dir, args.profile, source_text, args.title)
        except ValueError as error:
            raise SystemExit(str(error))
        print(f"workflow 已保存：{result['path']}")
        return

    Handler.outputs = resolve_outputs(args.target, args.output, args.project_dir)

    server = http.server.HTTPServer(("localhost", args.port), Handler)

    print("=" * 52)
    print("  🎩  Sorting Hat · 分院仪式启动")
    print("=" * 52)
    print(f"  浏览器已打开，请在页面中完成问卷")
    print(f"  完成后点击「保存人设」，将输出到：")
    for output in Handler.outputs:
        if output.path is None:
            print(f"  {output.name}：浏览器内复制")
        else:
            print(f"  {output.name}：{output.path}")
    print("=" * 52)
    print("  按 Ctrl+C 可手动退出\n")

    # 自动打开浏览器
    url = f"http://localhost:{args.port}"
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  服务器已退出。")


if __name__ == "__main__":
    main()

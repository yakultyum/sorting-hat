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
    existing_bound_projects = []
    if profile_json_path.exists():
        existing_profile = json.loads(profile_json_path.read_text(encoding="utf-8"))
        existing_workflows = existing_profile.get("workflows", [])
        existing_bound_projects = existing_profile.get("bound_projects", [])

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
    if existing_bound_projects:
        profile_payload["bound_projects"] = existing_bound_projects
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


def build_project_md(name, tech_stack, conventions, gotcha, persona_override, workflows=None):
    parts = [f"# {name}\n\n> 由 Sorting Hat 生成的项目记忆文件。AI 在处理本项目任务前应读取本文件。\n"]
    if tech_stack:
        parts.append(f"## 技术栈\n\n{tech_stack}\n")
    if conventions:
        parts.append(f"## 约定\n\n{conventions}\n")
    if gotcha:
        parts.append(f"## Gotcha\n\n{gotcha}\n")
    if persona_override:
        parts.append(f"## 人设覆盖\n\n{persona_override}\n")
    if workflows:
        rules = []
        for wf in workflows:
            title   = wf.get("title") or wf.get("id", "规则")
            trigger = wf.get("trigger", "")
            ai_resp = wf.get("ai_response", "")
            anti    = wf.get("anti_example", "")
            verify  = wf.get("verification_prompt", "")
            block = f"### {title}\n"
            if trigger:  block += f"\n**触发场景**：{trigger}\n"
            if ai_resp:  block += f"\n**AI 应如何响应**：{ai_resp}\n"
            if anti:     block += f"\n**反例**：{anti}\n"
            if verify:   block += f"\n**验证 prompt**：{verify}\n"
            rules.append(block)
        parts.append("## 协作规则\n\n" + "\n".join(rules))
    return "\n".join(parts)


def parse_project_fields(text):
    fields = {"name": "", "tech_stack": "", "conventions": "", "gotcha": "", "persona_override": ""}
    section_map = {
        "技术栈": "tech_stack",
        "约定":   "conventions",
        "Gotcha": "gotcha",
        "人设覆盖": "persona_override",
    }
    for line in text.splitlines():
        if line.startswith("# "):
            fields["name"] = line[2:].strip()
            break
    current_key = None
    buf = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            if current_key and buf:
                fields[current_key] = "\n".join(buf).strip()
            heading = stripped[3:].strip()
            current_key = section_map.get(heading)
            buf = []
        elif current_key is not None:
            if stripped.startswith(">"):
                continue
            buf.append(line)
    if current_key and buf:
        fields[current_key] = "\n".join(buf).strip()
    return fields


def parse_workflow_fields(text):
    """从 workflow markdown 里提取五个字段，返回 dict。"""
    fields = {
        "title": "",
        "trigger": "",
        "human_action": "",
        "ai_response": "",
        "anti_example": "",
        "verification_prompt": "",
    }
    # 提取标题（第一行 # ...）
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            fields["title"] = line[2:].strip()
            break

    section_map = {
        "触发场景":     "trigger",
        "人的主导动作": "human_action",
        "AI 应如何响应": "ai_response",
        "反例":         "anti_example",
        "验证 prompt":  "verification_prompt",
    }
    current_key = None
    buf = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            if current_key and buf:
                fields[current_key] = "\n".join(buf).strip()
            heading = stripped[3:].strip()
            current_key = section_map.get(heading)
            buf = []
        elif current_key is not None:
            if stripped.startswith(">"):
                continue  # 跳过生成说明行
            buf.append(line)
    if current_key and buf:
        fields[current_key] = "\n".join(buf).strip()
    return fields



def build_workflow_reflection(title, trigger="", human_action="", ai_response="", anti_example="", verification_prompt=""):
    return f"""# {title}

> 由 Sorting Hat reflect 生成。该文件只保存抽象协作规则，不保存聊天原文。

## 触发场景

{trigger}

## 人的主导动作

{human_action}

## AI 应如何响应

{ai_response}

## 反例

{anti_example}

## 验证 prompt

{verification_prompt}
"""


def save_workflow_reflection(store_dir, profile_selector, title, trigger, human_action, ai_response, anti_example, verification_prompt):
    profile = use_profile(store_dir, profile_selector)
    profile_dir = Path(profile["profile_path"]).parent
    workflow_id = profile_id_from_name(title)
    workflows_dir = profile_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    workflow_path = workflows_dir / f"{workflow_id}.md"
    workflow = build_workflow_reflection(title, trigger, human_action, ai_response, anti_example, verification_prompt)
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
        if path == "/profiles":
            profiles = list_profiles(DEFAULT_PROFILE_STORE_DIR)
            enriched = []
            for p in profiles:
                item = {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "scenarios": p.get("scenarios", []),
                    "is_default": p.get("is_default", False),
                    "workflows": p.get("workflows", []),
                    "bound_projects": p.get("bound_projects", []),
                }
                profile_dir = Path(p["profile_path"]).parent
                prompt_path = profile_dir / p.get("prompt_path", "prompt.md")
                answers_path = profile_dir / p.get("answers_path", "answers.json")
                item["prompt"] = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
                if answers_path.exists():
                    try:
                        raw = json.loads(answers_path.read_text(encoding="utf-8"))
                        item["version"] = raw.get("version", "lite")
                        item["updated"] = raw.get("updated", "")
                    except Exception:
                        item["version"] = "lite"
                        item["updated"] = ""
                # 读取 workflow 内容（按字段解析）
                workflow_details = []
                for wref in p.get("workflows", []):
                    wfile = profile_dir / wref
                    if wfile.exists():
                        text = wfile.read_text(encoding="utf-8")
                        fields = parse_workflow_fields(text)
                        fields["id"] = wfile.stem
                        workflow_details.append(fields)
                item["workflow_details"] = workflow_details
                enriched.append(item)
            self.send_json(enriched)
            return
        # GET /projects/all — 所有项目记忆（跨 profile）
        if path == "/projects/all":
            store_dir = DEFAULT_PROFILE_STORE_DIR.expanduser()
            seen_dirs = set()
            projects = []
            for p in list_profiles(store_dir):
                for b in p.get("bound_projects", []):
                    d = b.get("dir", "")
                    if d and d not in seen_dirs:
                        seen_dirs.add(d)
                        project_file = Path(d).expanduser() / ".sorting-hat" / "project.md"
                        if project_file.exists():
                            text = project_file.read_text(encoding="utf-8")
                            fields = parse_project_fields(text)
                            projects.append({"dir": d, "path": str(project_file), **fields})
                        else:
                            projects.append({"dir": d, "path": None, "name": Path(d).expanduser().name,
                                             "tech_stack": "", "conventions": "", "gotcha": "", "persona_override": ""})
            self.send_json(projects)
            return
        # GET /projects?dir=<path>
        if path == "/projects":
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            project_dir = (qs.get("dir") or [""])[0].strip()
            if not project_dir:
                self.send_json({"ok": False, "error": "缺少 dir 参数"}, status=400)
                return
            project_file = Path(project_dir).expanduser() / ".sorting-hat" / "project.md"
            if not project_file.exists():
                self.send_json({"ok": False, "exists": False})
                return
            text = project_file.read_text(encoding="utf-8")
            fields = parse_project_fields(text)
            self.send_json({"ok": True, "exists": True, "path": str(project_file), **fields})
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
        path = self.path.split("?")[0]
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        # POST /profiles — 手写创建新 profile
        if path == "/profiles":
            try:
                data = json.loads(body)
                name     = (data.get("name") or "").strip()
                scenarios = data.get("scenarios") or ["日常助理 / 通用协作"]
                prompt   = (data.get("prompt") or "").strip()
                if not name:
                    self.send_json({"ok": False, "error": "名称不能为空"}, status=400)
                    return
                profile_id  = profile_id_from_name(name)
                store_dir   = DEFAULT_PROFILE_STORE_DIR.expanduser()
                profile_dir = store_dir / "profiles" / profile_id
                profile_dir.mkdir(parents=True, exist_ok=True)
                profile_payload = {
                    "id": profile_id, "name": name, "scenarios": scenarios,
                    "persona_path": "persona.md", "prompt_path": "prompt.md",
                    "answers_path": "answers.json",
                }
                (profile_dir / "profile.json").write_text(
                    json.dumps(profile_payload, ensure_ascii=False, indent=2), encoding="utf-8")
                (profile_dir / "prompt.md").write_text(prompt, encoding="utf-8")
                (profile_dir / "persona.md").write_text(prompt, encoding="utf-8")
                (profile_dir / "answers.json").write_text(
                    json.dumps({"version": "manual", "answers": {}, "profile": {"name": name, "scenarios": scenarios}},
                               ensure_ascii=False, indent=2), encoding="utf-8")
                # 更新 index
                index_path = store_dir / "index.json"
                index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else \
                    {"version": 1, "default_profile": profile_id, "profiles": []}
                index["profiles"] = [p for p in index.get("profiles", []) if p.get("id") != profile_id]
                index["profiles"].append({"id": profile_id, "name": name, "scenarios": scenarios,
                                          "path": f"profiles/{profile_id}/profile.json"})
                index.setdefault("default_profile", profile_id)
                index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
                self.send_json({"ok": True, "profileId": profile_id, "profileDir": str(profile_dir)})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)
            return

        # POST /profiles/<id>/activate — 激活 profile 到工具/项目
        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "profiles" and parts[2] == "activate":
            try:
                data        = json.loads(body) if body else {}
                profile_id  = parts[1]
                target      = data.get("target", "claude")
                project_dir = data.get("project_dir", "")
                store_dir   = DEFAULT_PROFILE_STORE_DIR.expanduser()
                profile_dir = store_dir / "profiles" / profile_id
                prompt_path = profile_dir / "prompt.md"
                if not prompt_path.exists():
                    self.send_json({"ok": False, "error": f"找不到 profile：{profile_id}"}, status=404)
                    return
                prompt_text = prompt_path.read_text(encoding="utf-8")
                outputs = resolve_outputs(target, None, project_dir or ".")
                written = []
                for output in outputs:
                    if output.path is None:
                        written.append({"name": output.name, "kind": "prompt", "content": prompt_text})
                        continue
                    output.path.parent.mkdir(parents=True, exist_ok=True)
                    backup_existing_file(output.path)
                    content = prompt_text
                    output.path.write_text(content, encoding="utf-8")
                    written.append({"name": output.name, "path": str(output.path)})
                # 记录 bound_projects，并把 workflows 写入 project.md
                if project_dir and target in ("cursor", "windsurf", "generic"):
                    profile_json_path = profile_dir / "profile.json"
                    pdata = json.loads(profile_json_path.read_text(encoding="utf-8"))
                    bound = pdata.get("bound_projects", [])
                    entry = {"dir": project_dir, "target": target}
                    if entry not in bound:
                        bound.append(entry)
                    pdata["bound_projects"] = bound
                    profile_json_path.write_text(json.dumps(pdata, ensure_ascii=False, indent=2), encoding="utf-8")

                    # 把 workflows 同步到 project.md 的「协作规则」段落
                    workflow_refs = pdata.get("workflows", [])
                    if workflow_refs:
                        workflow_details = []
                        for wref in workflow_refs:
                            wfile = profile_dir / wref
                            if wfile.exists():
                                fields = parse_workflow_fields(wfile.read_text(encoding="utf-8"))
                                fields["id"] = wfile.stem
                                workflow_details.append(fields)
                        if workflow_details:
                            project_path = Path(project_dir).expanduser()
                            sh_dir = project_path / ".sorting-hat"
                            project_file = sh_dir / "project.md"
                            if project_file.exists():
                                # 已有 project.md：读取现有字段，只更新协作规则段落
                                existing = parse_project_fields(project_file.read_text(encoding="utf-8"))
                                content = build_project_md(
                                    existing["name"] or project_path.name,
                                    existing["tech_stack"],
                                    existing["conventions"],
                                    existing["gotcha"],
                                    existing["persona_override"],
                                    workflows=workflow_details,
                                )
                            else:
                                # 还没有 project.md：只写协作规则
                                sh_dir.mkdir(parents=True, exist_ok=True)
                                content = build_project_md(
                                    project_path.name, "", "", "", "",
                                    workflows=workflow_details,
                                )
                            project_file.write_text(content, encoding="utf-8")
                            written.append({"name": "项目记忆", "path": str(project_file)})
                self.send_json({"ok": True, "outputs": written})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)
            return

        # POST /projects — 创建或更新项目记忆
        if path == "/projects":
            try:
                data        = json.loads(body) if body else {}
                project_dir = (data.get("project_dir") or "").strip()
                if not project_dir:
                    self.send_json({"ok": False, "error": "project_dir 不能为空"}, status=400)
                    return
                profile_id       = data.get("profile_id", "")
                name             = data.get("name", "")
                tech_stack       = data.get("tech_stack", "")
                conventions      = data.get("conventions", "")
                gotcha           = data.get("gotcha", "")
                persona_override = data.get("persona_override", "")
                project_path = Path(project_dir).expanduser()
                sh_dir = project_path / ".sorting-hat"
                sh_dir.mkdir(parents=True, exist_ok=True)
                project_file = sh_dir / "project.md"
                # 如果绑定了 profile，顺带把该 profile 的 workflows 写进去
                workflow_details = []
                if profile_id:
                    pdir = DEFAULT_PROFILE_STORE_DIR.expanduser() / "profiles" / profile_id
                    pjson_path = pdir / "profile.json"
                    if pjson_path.exists():
                        pdata = json.loads(pjson_path.read_text(encoding="utf-8"))
                        for wref in pdata.get("workflows", []):
                            wfile = pdir / wref
                            if wfile.exists():
                                fields = parse_workflow_fields(wfile.read_text(encoding="utf-8"))
                                fields["id"] = wfile.stem
                                workflow_details.append(fields)
                content = build_project_md(
                    name or project_path.name, tech_stack, conventions, gotcha, persona_override,
                    workflows=workflow_details if workflow_details else None,
                )
                project_file.write_text(content, encoding="utf-8")
                # 绑定到 profile
                if profile_id:
                    pjson = DEFAULT_PROFILE_STORE_DIR.expanduser() / "profiles" / profile_id / "profile.json"
                    if pjson.exists():
                        pdata = json.loads(pjson.read_text(encoding="utf-8"))
                        bound = pdata.get("bound_projects", [])
                        entry = {"dir": project_dir, "target": "project-memory"}
                        if entry not in bound:
                            bound.append(entry)
                        pdata["bound_projects"] = bound
                        pjson.write_text(json.dumps(pdata, ensure_ascii=False, indent=2), encoding="utf-8")
                self.send_json({"ok": True, "path": str(project_file)})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)
            return

        if path != "/save":
            self.send_response(404)
            self.end_headers()
            return

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

    def do_PUT(self):
        path = self.path.split("?")[0]
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body) if body else {}
        except Exception:
            self.send_json({"ok": False, "error": "请求体不是合法 JSON"}, status=400)
            return

        # PUT /profiles/<id>/prompt  → 更新 prompt.md
        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "profiles" and parts[2] == "prompt":
            profile_id = parts[1]
            new_prompt = data.get("prompt", "")
            if not new_prompt:
                self.send_json({"ok": False, "error": "prompt 字段不能为空"}, status=400)
                return
            profile_dir = DEFAULT_PROFILE_STORE_DIR / "profiles" / profile_id
            if not profile_dir.exists():
                self.send_json({"ok": False, "error": f"找不到 profile：{profile_id}"}, status=404)
                return
            prompt_path = profile_dir / "prompt.md"
            prompt_path.write_text(new_prompt, encoding="utf-8")
            self.send_json({"ok": True, "path": str(prompt_path)})
            return

        # PUT /profiles/<id>/workflows/<wid>  → 按字段更新 workflow markdown
        if len(parts) == 4 and parts[0] == "profiles" and parts[2] == "workflows":
            profile_id = parts[1]
            wid = parts[3]
            profile_dir = DEFAULT_PROFILE_STORE_DIR / "profiles" / profile_id
            if not profile_dir.exists():
                self.send_json({"ok": False, "error": f"找不到 profile：{profile_id}"}, status=404)
                return
            workflow_path = profile_dir / "workflows" / f"{wid}.md"
            if not workflow_path.exists():
                self.send_json({"ok": False, "error": f"找不到 workflow：{wid}"}, status=404)
                return
            title    = data.get("title", wid)
            trigger  = data.get("trigger", "")
            human    = data.get("human_action", "")
            ai_resp  = data.get("ai_response", "")
            anti     = data.get("anti_example", "")
            verify   = data.get("verification_prompt", "")
            content = f"""# {title}

> 由 Sorting Hat reflect 生成。该文件只保存抽象协作规则，不保存聊天原文。

## 触发场景

{trigger}

## 人的主导动作

{human}

## AI 应如何响应

{ai_resp}

## 反例

{anti}

## 验证 prompt

{verify}
"""
            workflow_path.write_text(content, encoding="utf-8")
            self.send_json({"ok": True, "path": str(workflow_path)})
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, PUT, OPTIONS")
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

    reflect_parser = subparsers.add_parser("reflect", help="写入 AI 已提炼好的 workflow 字段")
    reflect_parser.add_argument("profile", help="profile id 或名称")
    reflect_parser.add_argument("--title", default="协作复盘规则", help="workflow 标题")
    reflect_parser.add_argument("--trigger", default="", help="触发场景")
    reflect_parser.add_argument("--human-action", default="", help="人的主导动作")
    reflect_parser.add_argument("--ai-response", default="", help="AI 应如何响应")
    reflect_parser.add_argument("--anti-example", default="", help="反例")
    reflect_parser.add_argument("--verification-prompt", default="", help="验证 prompt")
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
        try:
            result = save_workflow_reflection(
                args.store_dir, args.profile,
                title=args.title,
                trigger=args.trigger,
                human_action=args.human_action,
                ai_response=args.ai_response,
                anti_example=args.anti_example,
                verification_prompt=args.verification_prompt,
            )
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

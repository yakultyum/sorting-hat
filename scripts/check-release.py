#!/usr/bin/env python3
"""Release checks for the Sorting Hat skill package."""

from __future__ import annotations

import filecmp
import json
import os
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "skill/SKILL.md",
    "skill/web/server.py",
    "skill/web/index.html",
    "skill/references/questionnaire.md",
    "skill/references/output-formats.md",
    "skill/references/evaluation.md",
    "skill/test-prompts.json",
    "scripts/install-skill.sh",
]
SYNCED_PAIRS = [
    ("web/server.py", "skill/web/server.py"),
    ("web/index.html", "skill/web/index.html"),
]
PYTHON_FILES = [
    "web/server.py",
    "skill/web/server.py",
]
JSON_FILES = [
    "skill/test-prompts.json",
]


def fail(message: str) -> None:
    print(f"✗ {message}")
    raise SystemExit(1)


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail("Missing required files: " + ", ".join(missing))
    print("✓ Required skill files present")


def check_synced_pairs() -> None:
    mismatched = [f"{left} != {right}" for left, right in SYNCED_PAIRS if not filecmp.cmp(ROOT / left, ROOT / right, shallow=False)]
    if mismatched:
        fail("Unsynced generated copies: " + ", ".join(mismatched))
    print("✓ Development and packaged web files match")


def check_python_files() -> None:
    os.environ.setdefault("PYTHONPYCACHEPREFIX", "/private/tmp/sorting-hat-pycache")
    sys.pycache_prefix = os.environ["PYTHONPYCACHEPREFIX"]
    for path in PYTHON_FILES:
        py_compile.compile(str(ROOT / path), doraise=True)
    print("✓ Python files compile")


def check_json_files() -> None:
    for path in JSON_FILES:
        with (ROOT / path).open(encoding="utf-8") as handle:
            json.load(handle)
    print("✓ JSON files are valid")


def check_skill_mentions_resources() -> None:
    skill = (ROOT / "skill/SKILL.md").read_text(encoding="utf-8")
    for required in ["references/evaluation.md", "test-prompts.json", "references/output-formats.md", "install-skill.sh"]:
        if required not in skill:
            fail(f"SKILL.md does not mention {required}")
    print("✓ SKILL.md references packaged resources")


def check_profile_metadata_mentions() -> None:
    required_by_file = {
        "web/index.html": ["profile_name", "profile_scenarios", "getProfileMetadata"],
        "web/server.py": ["write_profile_store", "profile_id_from_name", "DEFAULT_PROFILE_STORE_DIR", "list_profiles", "use_profile", "build_workflow_reflection", "save_workflow_reflection"],
        "skill/web/index.html": ["profile_name", "profile_scenarios", "getProfileMetadata"],
        "skill/web/server.py": ["write_profile_store", "profile_id_from_name", "DEFAULT_PROFILE_STORE_DIR", "list_profiles", "use_profile", "build_workflow_reflection", "save_workflow_reflection"],
        "skill/references/questionnaire.md": ["profile_name", "profile_scenarios"],
        "skill/references/output-formats.md": ["profile_name", "profile_scenarios", "profile.json"],
        "README.md": ["profile 名称", "适用场景", "~/.sorting-hat/profiles", "git clone https://github.com/yakultyum/sorting-hat.git sorting-hat", "/sorting-hat profiles", "/sorting-hat use", "/sorting-hat reflect"],
        "docs/sorting-hat-competition-submit.md": ["git clone https://github.com/yakultyum/sorting-hat.git sorting-hat", "/sorting-hat profiles", "/sorting-hat use", "/sorting-hat reflect"],
        "docs/sorting-hat-competition-submit.html": ["git clone https://github.com/yakultyum/sorting-hat.git sorting-hat", "/sorting-hat profiles", "/sorting-hat use", "/sorting-hat reflect"],
    }
    for path, required_terms in required_by_file.items():
        content = (ROOT / path).read_text(encoding="utf-8")
        for term in required_terms:
            if term not in content:
                fail(f"{path} does not mention {term}")
    print("✓ Profile metadata fields documented and packaged")


def check_executable_scripts() -> None:
    install_script = ROOT / "scripts/install-skill.sh"
    if not install_script.stat().st_mode & 0o111:
        fail("scripts/install-skill.sh is not executable")
    print("✓ Install script is executable")


def main() -> int:
    check_required_files()
    check_synced_pairs()
    check_python_files()
    check_json_files()
    check_skill_mentions_resources()
    check_profile_metadata_mentions()
    check_executable_scripts()
    print("✓ Sorting Hat skill release checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

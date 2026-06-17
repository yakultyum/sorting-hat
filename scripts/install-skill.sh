#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT_DIR/skill"

usage() {
  cat <<'EOF'
Usage: scripts/install-skill.sh [--dest <runtime-skills-dir>] [--force]

Installs Sorting Hat into a runtime skills directory.
Default behavior: auto-detect common local skill directories.

Examples:
  scripts/install-skill.sh --force
  scripts/install-skill.sh --dest ~/.claude/skills
  scripts/install-skill.sh --dest ~/.cursor/skills
  scripts/install-skill.sh --dest ~/.windsurf/skills
  scripts/install-skill.sh --dest ~/.codex/skills
  scripts/install-skill.sh --dest ~/.agents/skills

Options:
  --dest PATH      Runtime skills directory. If omitted, auto-detects a common directory.
  --force          Replace existing sorting-hat installation after creating a .bak copy.
  -h, --help       Show this help.
EOF
}

DEST_ROOT="${SORTING_HAT_SKILLS_DIR:-}"
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest)
      [[ $# -ge 2 ]] || { echo "Missing value for --dest" >&2; exit 1; }
      DEST_ROOT="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$DEST_ROOT" ]]; then
  CANDIDATES=(
    "$HOME/.claude/skills"
    "$HOME/.cursor/skills"
    "$HOME/.windsurf/skills"
    "$HOME/.codex/skills"
    "$HOME/.agents/skills"
  )
  for candidate in "${CANDIDATES[@]}"; do
    if [[ -d "$candidate" ]]; then
      DEST_ROOT="$candidate"
      break
    fi
  done
  if [[ -z "$DEST_ROOT" ]]; then
    DEST_ROOT="$HOME/.claude/skills"
  fi
fi

DEST_ROOT="${DEST_ROOT/#\~/$HOME}"
DEST_DIR="$DEST_ROOT/sorting-hat"

if [[ ! -f "$SOURCE_DIR/SKILL.md" ]]; then
  echo "Source skill directory is incomplete: $SOURCE_DIR" >&2
  exit 1
fi

python3 "$ROOT_DIR/scripts/check-release.py"
mkdir -p "$DEST_ROOT"

if [[ -e "$DEST_DIR" ]]; then
  if [[ "$FORCE" -ne 1 ]]; then
    echo "Destination already exists: $DEST_DIR" >&2
    echo "Re-run with --force to replace it after creating a timestamped backup." >&2
    exit 1
  fi
  BACKUP_DIR="$DEST_DIR.bak.$(date +%Y%m%d%H%M%S)"
  mv "$DEST_DIR" "$BACKUP_DIR"
  echo "Backed up existing installation to $BACKUP_DIR"
fi

cp -R "$SOURCE_DIR" "$DEST_DIR"
echo "Installed Sorting Hat skill to $DEST_DIR"
echo "Restart your AI coding tool so it can pick up the skill."

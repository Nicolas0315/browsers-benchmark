#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-ci}"

usage() {
  cat <<'USAGE'
Usage: scripts/verify.sh [ci|syntax|json|ip-redaction]

Targets:
  ci      Run offline syntax and checked-in JSON checks.
  syntax  Compile Python files without importing browser/proxy dependencies.
  json    Parse checked-in result JSON files.
  ip-redaction Refuse publicly routable IPv4 literals in published samples.

This verifier does not install browser engines, launch browsers, use proxies, or contact external targets.
USAGE
}

run_repo() {
  (cd "$ROOT_DIR" && "$@")
}

check_syntax() {
  run_repo python3 -m py_compile $(find . -path './.venv' -prune -o -path './node_modules' -prune -o -name '*.py' -print)
}

check_json() {
  run_repo python3 - <<'PY'
import json
from pathlib import Path

for path in Path("results").rglob("*.json"):
    json.loads(path.read_text(encoding="utf-8"))
PY
}

case "$TARGET" in
  ci)
    "$0" syntax
    "$0" json
    "$0" ip-redaction
    ;;
  syntax)
    check_syntax
    ;;
  json)
    check_json
    ;;
  ip-redaction)
    run_repo python3 scripts/check_sample_ip_redaction.py
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

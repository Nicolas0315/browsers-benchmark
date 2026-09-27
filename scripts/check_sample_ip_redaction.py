#!/usr/bin/env python3
"""Refuse globally routable IPv4 literals in checked-in benchmark samples."""

from __future__ import annotations

import ipaddress
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IPV4_LITERAL = re.compile(r"(?<![\w])(?:\d{1,3}\.){3}\d{1,3}(?![\w])")


def sample_files() -> list[Path]:
    files = [ROOT / "README.md"]
    results = ROOT / "results"
    if results.exists():
        files.extend(
            path
            for path in results.rglob("*")
            if path.is_file() and path.suffix.lower() in {".json", ".md"}
        )
    return files


def globally_routable_lines(path: Path) -> list[int]:
    findings = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for literal in IPV4_LITERAL.findall(line):
            try:
                address = ipaddress.ip_address(literal)
            except ValueError:
                continue
            if address.is_global:
                findings.append(line_number)
    return findings


def main() -> int:
    findings = [
        (path.relative_to(ROOT), line_number)
        for path in sample_files()
        for line_number in globally_routable_lines(path)
    ]
    if findings:
        for path, line_number in findings:
            print(f"{path}:{line_number}: globally routable IPv4 literal in published sample")
        print(f"refusing: {len(findings)} globally routable IPv4 literal(s)")
        return 1

    print("sample IPv4 redaction check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

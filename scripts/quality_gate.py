#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate generated Chinese finance reports from the command line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.shared import issues_to_dicts, validate_chinese_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Chinese finance report quality.")
    parser.add_argument("files", nargs="+", help="Markdown or HTML report files to validate")
    parser.add_argument("--require-layered-conclusion", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    results = {}
    failed = False
    for file_name in args.files:
        path = Path(file_name)
        text = path.read_text(encoding="utf-8")
        issues = validate_chinese_report(text, require_layered_conclusion=args.require_layered_conclusion)
        results[str(path)] = issues_to_dicts(issues)
        failed = failed or bool(issues)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for file_name, issues in results.items():
            if not issues:
                print(f"通过: {file_name}")
            else:
                print(f"未通过: {file_name}")
                for issue in issues:
                    print(f"  - [{issue['severity']}] {issue['code']}: {issue['message']}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

import subprocess
import sys
from pathlib import Path

from skills.shared import validate_chinese_report


ROOT = Path(__file__).resolve().parents[1]


def _frontmatter_keys(text: str):
    assert text.startswith("---\n")
    end = text.index("\n---", 4)
    keys = []
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            keys.append(line.split(":", 1)[0])
    return keys


def test_root_skill_frontmatter_matches_skill_spec():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert _frontmatter_keys(text) == ["name", "description"]


def test_report_quality_gate_flags_common_chinese_report_regressions():
    issues = validate_chinese_report(
        "综合结论：BUY。所属行业 Technology。形态出现双顶和双底。数据 N/A。",
        require_layered_conclusion=True,
    )
    codes = {issue.code for issue in issues}
    assert "english_action" in codes
    assert "english_industry" in codes
    assert "pattern_conflict" in codes
    assert "missing_placeholder" in codes
    assert "weak_conclusion_structure" in codes


def test_quality_gate_cli_passes_clean_report():
    output_dir = ROOT / "outputs" / "test_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    report = output_dir / "clean_report.md"
    report.write_text(
        "综合结论\n\n综合观点：结论需继续验证。\n\n关键依据：财务质量良好。\n\n风险与验证：关注财报和行业景气度。",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/quality_gate.py", str(report), "--require-layered-conclusion"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "通过" in result.stdout

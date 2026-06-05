import importlib.util
from pathlib import Path


def _load_pipeline():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "opportunity_pipeline.py"
    spec = importlib.util.spec_from_file_location("opportunity_pipeline", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_opportunity_pipeline_ranks_real_candidate_csv_and_generates_html(tmp_path):
    module = _load_pipeline()
    csv_path = Path(__file__).resolve().parent / "fixtures" / "candidate_pool_sample.csv"
    pipeline = module.OpportunityPipeline()

    ranked = pipeline.rank(pipeline.load_csv(str(csv_path)), top=3)
    html_path = tmp_path / "shortlist.html"
    html = pipeline.generate_html(ranked, str(html_path))

    assert ranked["success"] is True
    assert ranked["total_candidates"] == 4
    assert len(ranked["items"]) == 3
    assert ranked["items"][0]["view"] in {"优先研究", "纳入观察"}
    assert "股票机会短名单" in html
    assert "三花智控（002050）" in html
    assert "入选理由" in html
    assert "主要风险" in html
    assert "BUY" not in html
    assert "SELL" not in html
    assert "N/A" not in html
    assert "Technology" not in html
    assert html_path.exists()

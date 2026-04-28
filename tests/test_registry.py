from skills.base_skill import SkillRegistry, load_builtin_skills


def test_load_builtin_skills_registers_core_skills():
    SkillRegistry._skills.clear()
    SkillRegistry._loaded_modules.clear()

    load_builtin_skills()

    assert "CryptoAnalysisSkill" in SkillRegistry.list_all()
    assert "StockAnalysisSkill" in SkillRegistry.list_all()
    assert "ForexAnalysisSkill" in SkillRegistry.list_all()
    assert "SignalDetectionSkill" in SkillRegistry.list_all()
    assert "AICommentarySkill" in SkillRegistry.list_all()
    assert "OnchainWhaleSkill" in SkillRegistry.list_all()

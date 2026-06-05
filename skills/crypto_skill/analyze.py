"""Proxy: skills.crypto_skill.analyze -> skills/crypto-skill/analyze.py"""
import importlib.util, os
_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crypto-skill", "analyze.py")
_spec = importlib.util.spec_from_file_location("skills_crypto_skill_analyze", _p)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
from analyze import *

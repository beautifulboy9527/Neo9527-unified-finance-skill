"""Proxy: skills.crypto_skill.complete_crypto_analyzer -> skills/crypto-skill/complete_crypto_analyzer.py"""
import importlib.util, os
_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crypto-skill", "complete_crypto_analyzer.py")
_spec = importlib.util.spec_from_file_location("skills_crypto_skill_complete_crypto_analyzer", _p)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
from complete_crypto_analyzer import *

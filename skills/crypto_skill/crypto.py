"""Proxy: skills.crypto_skill.crypto -> skills/crypto-skill/crypto.py"""
import importlib.util, os
_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crypto-skill", "crypto.py")
_spec = importlib.util.spec_from_file_location("skills_crypto_skill_crypto", _p)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
from crypto import *

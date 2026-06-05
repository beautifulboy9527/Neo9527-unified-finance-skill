"""Proxy package: skills.crypto_skill -> skills/crypto-skill/"""
import sys, os
_hyphen_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crypto-skill")
if _hyphen_dir not in sys.path:
    sys.path.insert(0, _hyphen_dir)

#!/usr/bin/env python3
"""
Neo9527 Finance Skill - PyPI Setup
v4.4.0 - OnchainWhaleSkill + 真实数据
"""

from setuptools import setup, find_packages
from pathlib import Path

BASE_DIR = Path(__file__).parent
README = (BASE_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="neo9527-finance-skill",
    version="4.4.0",
    author="beautifulboy9527",
    author_email="beautifulboy9527@gmail.com",
    description="Lightweight production-ready AI finance skill platform for multi-market analysis, signals, reports, and on-chain intelligence.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/beautifulboy9527/Neo9527-unified-finance-skill",
    project_urls={
        "Documentation": "https://github.com/beautifulboy9527/Neo9527-unified-finance-skill",
        "Source": "https://github.com/beautifulboy9527/Neo9527-unified-finance-skill",
        "Issues": "https://github.com/beautifulboy9527/Neo9527-unified-finance-skill/issues",
    },
    packages=find_packages(exclude=("tests", "examples", "docs")),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pydantic>=2.6.0",
        "fastapi>=0.110.0",
        "uvicorn>=0.29.0",
        "yfinance>=0.2.40",
        "matplotlib>=3.8.0",
        "mplfinance>=0.12.10b0",
    ],
    extras_require={
        "crypto": [
            "ccxt>=4.3.0",
            "pandas-ta>=0.3.14b0",
        ],
        "china": [
            "akshare>=1.12.0",
        ],
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "build>=1.2.1",
            "twine>=5.0.0",
            "ruff>=0.4.0",
        ],
        "all": [
            "ccxt>=4.3.0",
            "pandas-ta>=0.3.14b0",
            "akshare>=1.12.0",
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "build>=1.2.1",
            "twine>=5.0.0",
            "ruff>=0.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "neo-finance=finance:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords=[
        "finance",
        "crypto",
        "stocks",
        "onchain",
        "signals",
        "ai-agent",
        "skill",
        "backtest",
        "portfolio",
    ],
    license="MIT",
    zip_safe=False,
)

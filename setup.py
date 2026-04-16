#!/usr/bin/env python3
"""
Neo9527 Finance Skill - PyPI Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="neo9527-finance-skill",
    version="4.2.0",
    author="Neo9527",
    author_email="beautifulboy9527@gmail.com",
    description="Multi-dimensional financial analysis system with K-line charts, whale data, and signal stacking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/beautifulboy9527/Neo9527-unified-finance-skill",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yfinance>=0.2.0",
        "pandas>=1.5.0",
        "numpy>=1.20.0",
        "requests>=2.28.0",
        "matplotlib>=3.6.0",
        "mplfinance>=0.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "neo-finance=finance:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "finance",
        "cryptocurrency",
        "trading",
        "analysis",
        "kline",
        "whale-data",
        "signals",
        "investment",
    ],
    project_urls={
        "Documentation": "https://github.com/beautifulboy9527/Neo9527-unified-finance-skill#readme",
        "Bug Reports": "https://github.com/beautifulboy9527/Neo9527-unified-finance-skill/issues",
        "Source": "https://github.com/beautifulboy9527/Neo9527-unified-finance-skill",
    },
)

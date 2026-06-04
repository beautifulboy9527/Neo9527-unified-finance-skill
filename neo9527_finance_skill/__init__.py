#!/usr/bin/env python3
"""
Neo9527 Finance Skill - CLI入口
"""

__version__ = "6.6.7"


def main():
    """CLI主入口"""
    import sys
    import os

    # 添加路径
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    sys.path.insert(0, project_dir)

    # 导入并运行当前主 CLI。根目录 finance.py 包含最新股票、研报、
    # 自选股、组合和自然语言入口；scripts/finance.py 保留为旧版兼容脚本。
    from finance import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()

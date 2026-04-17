#!/usr/bin/env python3
"""
Neo9527 Finance Skill - CLI入口
"""

__version__ = "4.4.1"


def main():
    """CLI主入口"""
    import sys
    import os

    # 添加路径
    package_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, package_dir)

    # 导入并运行
    from scripts.finance import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()

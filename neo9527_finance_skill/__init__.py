#!/usr/bin/env python3
"""
Neo9527 Finance Skill - CLI入口
"""

__version__ = "6.6.4"


def main():
    """CLI主入口"""
    import sys
    import os

    # 添加路径
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(package_dir)
    sys.path.insert(0, project_dir)

    # 导入并运行
    from scripts.finance import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()

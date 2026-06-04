#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo9527 Finance Skill - 自动化发布脚本

用法:
    python scripts/release.py 4.5.0 "新增功能"

功能:
    - 版本号同步检查
    - Git提交和推送
    - PyPI构建和发布
    - GitHub Release创建
    - 发布后验证
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


class ReleaseManager:
    """发布管理器"""
    
    def __init__(self, package_name: str = "neo9527-finance-skill"):
        self.package_name = package_name
        self.root_dir = Path(__file__).parent.parent
        os.chdir(self.root_dir)
        
        # Windows编码设置
        if sys.platform == 'win32':
            os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    def release(self, version: str, notes: str):
        """执行完整发布流程"""
        
        print("=" * 60)
        print(f"📦 开始发布 {self.package_name} v{version}")
        print("=" * 60)
        
        try:
            # P0: 发布前检查
            self._check_version(version)
            self._check_git_status()
            
            # P1: Git提交
            self._git_commit(version, notes)
            
            # P2: PyPI发布
            self._pypi_publish()
            
            # P3: GitHub Release
            self._github_release(version, notes)
            
            # P4: 验证
            self._verify(version)
            
            print("\n" + "=" * 60)
            print(f"✅ 发布完成！v{version}")
            print(f"PyPI: https://pypi.org/project/{self.package_name}/{version}/")
            print(f"GitHub: https://github.com/beautifulboy9527/Neo9527-unified-finance-skill/releases/tag/v{version}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ 发布失败: {e}")
            sys.exit(1)
    
    def _check_version(self, version: str):
        """检查版本号一致性"""
        print("\n[P0] 检查版本号一致性...")
        
        files = {
            'setup.py': f'version="{version}"',
            'pyproject.toml': f'version = "{version}"'
        }
        
        for file, expected in files.items():
            path = self.root_dir / file
            if not path.exists():
                raise Exception(f"文件不存在: {file}")
            
            content = path.read_text(encoding='utf-8')
            if expected not in content:
                print(f"⚠️  {file} 版本号不一致")
                print(f"   期望: {expected}")
                print(f"   请手动更新版本号")
                raise Exception(f"版本号不一致: {file}")
            
            print(f"✅ {file}: v{version}")
    
    def _check_git_status(self):
        """检查Git状态"""
        print("\n[P0] 检查Git状态...")
        
        result = subprocess.run(
            ['git', 'status', '--short'],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print("⚠️  有未提交的更改:")
            print(result.stdout)
            response = input("是否继续发布？(y/n): ")
            if response.lower() != 'y':
                raise Exception("用户取消发布")
        
        print("✅ Git状态正常")
    
    def _git_commit(self, version: str, notes: str):
        """Git提交和推送"""
        print("\n[P1] Git提交和推送...")
        
        # 添加所有文件
        subprocess.run(['git', 'add', '.'], check=True)
        
        # 提交
        commit_msg = f"release: v{version} - {notes}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        print(f"✅ Git提交: {commit_msg}")
        
        # 推送
        subprocess.run(['git', 'push', 'origin', 'master'], check=True)
        print("✅ 推送到GitHub")
        
        # 创建Tag
        subprocess.run(['git', 'tag', '-a', f'v{version}', '-m', f'Release v{version}'], check=True)
        subprocess.run(['git', 'push', 'origin', f'v{version}'], check=True)
        print(f"✅ 创建Tag: v{version}")
    
    def _pypi_publish(self):
        """PyPI构建和发布"""
        print("\n[P2] PyPI构建和发布...")
        
        # 清理旧构建
        for dir_name in ['build', 'dist']:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                subprocess.run(['rm', '-rf', str(dir_path)], shell=True, check=True)
        print("✅ 清理旧构建")
        
        # 安装工具
        subprocess.run([
            'python', '-m', 'pip', 'install', '--upgrade',
            'pip', 'build', 'twine', '-q'
        ], check=True)
        print("✅ 安装构建工具")
        
        # 构建
        result = subprocess.run(['python', '-m', 'build'], capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr)
            raise Exception("构建失败")
        print("✅ 构建完成")
        
        # 检查
        result = subprocess.run(['python', '-m', 'twine', 'check', 'dist/*'], capture_output=True, text=True)
        if 'PASSED' not in result.stdout:
            print(result.stdout)
            raise Exception("包检查失败")
        print("✅ 包检查通过")
        
        # 上传
        print("📤 上传到PyPI...")
        result = subprocess.run(
            ['python', '-m', 'twine', 'upload', 'dist/*'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(result.stderr)
            raise Exception("PyPI上传失败")
        
        print("✅ PyPI上传成功")
    
    def _github_release(self, version: str, notes: str):
        """创建GitHub Release"""
        print("\n[P3] 创建GitHub Release...")
        
        # 检查是否有gh命令
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  gh命令不可用，跳过GitHub Release创建")
            print("   请手动创建: https://github.com/beautifulboy9527/Neo9527-unified-finance-skill/releases/new")
            return
        
        # 创建Release
        result = subprocess.run([
            'gh', 'release', 'create', f'v{version}',
            '--title', f'v{version} - {notes}',
            '--notes', f"Release v{version}\n\n{notes}"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️  GitHub Release创建失败: {result.stderr}")
        else:
            print("✅ GitHub Release创建成功")
    
    def _verify(self, version: str):
        """验证发布"""
        print("\n[P4] 验证发布...")
        
        # 等待PyPI同步
        print("⏳ 等待PyPI同步 (30秒)...")
        import time
        time.sleep(30)
        
        # 验证安装
        result = subprocess.run(
            ['pip', 'show', self.package_name],
            capture_output=True,
            text=True
        )
        
        if f'Version: {version}' in result.stdout:
            print(f"✅ PyPI验证成功: v{version}")
        else:
            print(f"⚠️  PyPI可能还在同步中，请稍后验证")
            print(f"   验证命令: pip show {self.package_name}")


def main():
    """主函数"""
    
    if len(sys.argv) < 3:
        print("用法: python scripts/release.py <version> <notes>")
        print("示例: python scripts/release.py 4.5.0 '新增功能'")
        sys.exit(1)
    
    version = sys.argv[1]
    notes = sys.argv[2]
    
    # 验证版本号格式
    if not all(part.isdigit() for part in version.split('.')):
        print("❌ 版本号格式错误，应为: X.Y.Z")
        sys.exit(1)
    
    manager = ReleaseManager()
    manager.release(version, notes)


if __name__ == '__main__':
    main()

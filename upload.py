#!/usr/bin/env python3
import os
import sys
import subprocess

os.chdir(r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill')

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 上传
result = subprocess.run(
    ['twine', 'upload', 'dist/neo9527_finance_skill-4.4.1-py3-none-any.whl', 'dist/neo9527_finance_skill-4.4.1.tar.gz'],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print(result.stderr)

sys.exit(result.returncode)

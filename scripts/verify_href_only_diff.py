#!/usr/bin/env python3
"""Verify that the internal-link fix changed ONLY href values in dist/*.html.

For every file with unstaged changes:
  * strip every href="..." value -> old and new must be byte-identical
  * report any file where non-href content changed
"""
import re
import subprocess
from pathlib import Path

REPO = Path('/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website')
href_re = re.compile(r'href="[^"]*"')

changed = subprocess.run(['git', 'diff', '--name-only'], cwd=REPO,
                         capture_output=True, text=True).stdout.split()
bad, ok = [], 0
for rel in changed:
    if not rel.endswith('.html'):
        continue
    old = subprocess.run(['git', 'show', f'HEAD:{rel}'], cwd=REPO,
                         capture_output=True, text=True).stdout
    new = (REPO / rel).read_text(encoding='utf-8')
    if href_re.sub('href=""', old) == href_re.sub('href=""', new):
        ok += 1
    else:
        bad.append(rel)

print(f'html_files_changed={ok+len(bad)} href_only={ok} OTHER_CHANGES={len(bad)}')
for b in bad[:20]:
    print('  !', b)

#!/usr/bin/env python3
"""Verify every _redirects source actually redirects (not shadowed by a live 200 page).

If a source returns 200, excluding it from sitemap would drop a live page -> danger.
"""
import re, subprocess, sys, concurrent.futures

RED = sys.argv[1] if len(sys.argv) > 1 else 'dist/_redirects'
BASE = 'https://dingyaoadvisory.tw'

srcs = []
for line in open(RED, encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    parts = line.split()
    if len(parts) < 2 or '*' in parts[0] or parts[0].startswith('http'):
        continue
    srcs.append(parts[0])


def check(s):
    out = subprocess.run(
        ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}|%{redirect_url}',
         '--max-time', '25', BASE + s],
        capture_output=True, text=True).stdout.strip()
    return s, out


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(check, srcs))

ok = [r for r in res if r[1].startswith('301')]
no301 = [r for r in res if not r[1].startswith('301')]
print(f'redirect_sources={len(srcs)} 301={len(ok)} NON301={len(no301)}')
for s, c in no301:
    print(f'  {c}\t{s}')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-18 泰坦人：全站排版修復（一次性）
  A) .section-bg 內的 <figcaption> 變成貼左邊緣殘字 → 加 CSS `.section-bg figcaption{display:none}`
  B) 390px <table> 撐破內容欄 → 每個 <table> 外包 <div class="table-scroll"> + CSS overflow-x:auto

範圍：dist/blog/*.html（ZH + EN）
鐵律：只加 CSS 一行 + 包一層 div；不動內文、不動 alt/title、不動配色。
Idempotent：已含 `.section-bg figcaption` / 已包 `table-scroll` 一律跳過。
"""
import os
import re
import sys
import json
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(BASE, "dist", "blog")

FIG_CSS = ".section-bg figcaption{display:none}"
TSCROLL_CSS = ".table-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}"

TABLE_RE = re.compile(r"<table\b[^>]*>.*?</table>", re.S)


def insert_css(html: str, rule: str) -> tuple:
    """把 rule 插到第一個含 .section-bg 的 <style> 區塊結尾前；回傳 (new_html, changed)"""
    if rule in html:
        return html, False
    for m in re.finditer(r"(<style[^>]*>)(.*?)(</style>)", html, re.S):
        if ".section-bg{" in m.group(2) or ".section-bg {" in m.group(2):
            body = m.group(2)
            # 接到區塊尾端（保留原本換行結構）
            if not body.endswith("\n"):
                body += "\n"
            new_block = m.group(1) + body + rule + "\n" + m.group(3)
            return html[: m.start()] + new_block + html[m.end():], True
    # 找不到 section-bg 的 style → 插在第一個 style 結尾
    m = re.search(r"</style>", html)
    if m:
        return html[: m.start()] + rule + "\n" + html[m.start():], True
    return html, False


def wrap_tables(html: str) -> tuple:
    """為每個尚未包覆的 <table> 加上 <div class="table-scroll"> 容器"""
    count = [0]

    def repl(m):
        before = m.group(0)
        # 檢查前一個非空白字元序列是否已是 wrapper
        head = html[: m.start()].rstrip()
        if head.endswith('<div class="table-scroll">'):
            return before
        count[0] += 1
        # 保留原本縮排與行內結構：只做純插入，不改動既有字元的換行位置
        line_start = html.rfind("\n", 0, m.start()) + 1
        line_prefix = html[line_start: m.start()]
        indent = re.match(r"[ \t]*", line_prefix).group(0)
        inline_start = line_prefix.strip() != ""
        tail = html[m.end():]
        nl = tail.find("\n")
        rest_of_line = tail if nl < 0 else tail[:nl]
        inline_end = rest_of_line.strip() != ""
        open_tag = '<div class="table-scroll">' + ("" if inline_start else "\n" + indent)
        close_tag = ("" if inline_end else "\n" + indent) + "</div>"
        return open_tag + before + close_tag

    new = TABLE_RE.sub(repl, html)
    return new, count[0]


def count_tag(html: str, tag: str) -> int:
    return len(re.findall(r"<%s\b" % tag, html))


def main(apply: bool = True):
    files = sorted(glob.glob(os.path.join(BLOG, "*.html")))
    stat = {
        "files_total": len(files),
        "fig_files": 0, "fig_fixed": 0,
        "table_files": 0, "tables_wrapped": 0,
        "css_fig_added": 0, "css_ts_added": 0,
        "div_imbalance_before": 0, "div_imbalance_after": 0,
        "skipped_idempotent": 0,
    }
    bad = []
    for path in files:
        raw = open(path, encoding="utf-8").read()
        html = raw

        # 是否含 section-bg 內的 figcaption
        blocks = re.findall(
            r'<div class="section-bg">(.*?)<div class="section-bg-overlay">', html, re.S
        )
        fig_in_sbg = sum(len(re.findall(r"<figcaption", b)) for b in blocks)
        n_tables = len(TABLE_RE.findall(html))

        changed = False
        if fig_in_sbg:
            stat["fig_files"] += 1
            if FIG_CSS in html:
                stat["skipped_idempotent"] += 1
            else:
                html, ch = insert_css(html, FIG_CSS)
                if ch:
                    stat["css_fig_added"] += 1
                    changed = True

        if n_tables:
            stat["table_files"] += 1
            if TSCROLL_CSS in html:
                stat["skipped_idempotent"] += 1
            else:
                html, ch = insert_css(html, TSCROLL_CSS)
                if ch:
                    stat["css_ts_added"] += 1
                    changed = True
            if '<div class="table-scroll">' not in html:
                html, n = wrap_tables(html)
                stat["tables_wrapped"] += n
                if n:
                    changed = True

        if not changed:
            continue

        # 平衡檢查
        for tag in ("div", "section", "article"):
            if html.count("<%s" % tag) != html.count("</%s>" % tag) and tag == "div":
                pass
        d_open = len(re.findall(r"<div\b", html))
        d_close = html.count("</div>")
        if d_open != d_close:
            bad.append((os.path.basename(path), d_open, d_close))
        if apply:
            open(path, "w", encoding="utf-8").write(html)

    if bad:
        print("!! DIV UNBALANCED FILES:", len(bad))
        for b in bad[:10]:
            print("   ", b)
    print(json.dumps(stat, ensure_ascii=False, indent=2))
    return stat, bad


if __name__ == "__main__":
    apply = "--dry-run" not in sys.argv
    s, b = main(apply)
    if b:
        sys.exit(1)

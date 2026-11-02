#!/usr/bin/env python3
"""全站 a11y 屬性批次後處理（第二階段）。

只做「開標籤插屬性」，不重生整頁、不改文案、不改 <title> / meta description /
canonical / hreflang / og:url，也不碰 <script>（含 JSON-LD）與 <style> 區塊。

處理項目
  1. <h2> 缺 id → 產生頁內唯一 id
       命名策略（土星人 2026-11-02 核准的第二階段）：
         a) 結構型標題 → STRUCT_MAP 指定（faq / related-reading / cta-heading …）
         b) 標題以 ASCII 為主（EN 頁）→ 由標題文字 slug 化
         c) 其餘（多為中文長尾）→ h2-NN（頁內序）
  2. <section> 缺 aria-labelledby → 指向區塊內第一個 h1~h4 的 id（該標題沒有 id 就先補）
       區塊內完全沒有標題 → 不動，列入報告
  3. <img> 缺 title → 用 alt 當 title；站台 logo 用固定字串
  4. <a> 缺 title → 取自目標頁 <title>（快取檔），不用錨文字猜

用法
  python3 scripts/fix_site_a11y.py --root dist --dry-run
  python3 scripts/fix_site_a11y.py --root dist --apply --pages /tmp/pilot.txt
  python3 scripts/fix_site_a11y.py --root dist --apply --limit 50
  python3 scripts/fix_site_a11y.py --root dist --build-target-cache   # 重建目標頁標題快取

exit 0 成功（含「沒有要改的」）；1 有頁面驗證失敗；2 參數／環境錯誤
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "scripts" / ".a11y_target_titles.json"
SITE = "https://dingyaoadvisory.tw"

SCRIPT_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
H2_RE = re.compile(r"<h2\b[^>]*>")
SEC_RE = re.compile(r"<section\b[^>]*>")
IMG_RE = re.compile(r"<img\b[^>]*>")
A_RE = re.compile(r"<a\b[^>]*>")
HEAD_RE = re.compile(r"<(h1|h2|h3|h4)\b[^>]*>")
ID_RE = re.compile(r'\bid="([^"]+)"')

# 結構型標題 → 固定 id（小寫比對；空白正規化）
STRUCT_MAP = {
    "主導覽": "nav-heading",
    "main navigation": "nav-heading",
    "常見問題 faq": "faq",
    "常見問題": "faq",
    "faq": "faq",
    "frequently asked questions": "faq",
    "frequently asked questions (faq)": "faq",
    "相關閱讀": "related-reading",
    "related reading": "related-reading",
    "參考資料": "references",
    "參考資料與數據來源": "references",
    "references": "references",
    "data sources & verification": "references",
    "為什麼要透過 crestline advisory 協助？": "crestline-assist-heading",
    "why handle this through crestline advisory ?": "crestline-assist-heading",
    "why handle this through crestline advisory?": "crestline-assist-heading",
}
CTA_PREFIX = ("開始您的", "start your")

LOGO_TITLE = {
    "zh": "鼎曜國際顧問標誌",
    "en": "DingYao Advisory logo",
}
SKIP_TITLE_HREF = ("#", "mailto:", "tel:", "javascript:")


def mask_scripts(html: str):
    """把 <script>/<style> 換成同長度佔位符，處理完再還原（保證不碰 JS/JSON-LD）。"""
    saved = []

    def repl(m):
        saved.append(m.group(0))
        token = "\x00MASK%d\x00" % (len(saved) - 1)
        return token + " " * max(0, len(m.group(0)) - len(token))

    return SCRIPT_RE.sub(repl, html), saved


def unmask_scripts(html: str, saved):
    for i, blk in enumerate(saved):
        token = "\x00MASK%d\x00" % i
        start = html.find(token)
        if start < 0:
            continue
        end = start + len(token) + max(0, len(blk) - len(token))
        html = html[:start] + blk + html[end:]
    return html


def add_attr(tag: str, name: str, value: str) -> str:
    if re.search(r"\b" + name + r"=", tag):
        return tag
    i = tag.rfind(">")
    return tag[:i] + ' %s="%s"' % (name, value) + tag[i:]


def set_attr(tag: str, name: str, value: str) -> str:
    if re.search(r"\b" + name + r'="[^"]*"', tag):
        return re.sub(r'\b' + name + r'="[^"]*"', '%s="%s"' % (name, value), tag, count=1)
    return add_attr(tag, name, value)


def slugify(text: str, max_words: int = 6) -> str:
    t = re.sub(r"&[a-z]+;", " ", text)
    t = re.sub(r"[^A-Za-z0-9\s-]", " ", t)
    words = [w for w in t.lower().split() if w]
    if not words:
        return ""
    return "-".join(words[:max_words])[:60].strip("-")


def ascii_ratio(text: str) -> float:
    letters = [c for c in text if not c.isspace()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if ord(c) < 128) / len(letters)


def heading_text(html: str, start: int) -> tuple[str, int, int]:
    """回傳 (純文字, 開標籤結束位置, 內文結束位置)。"""
    m = HEAD_RE.match(html, start)
    if not m:
        return "", -1, -1
    close = html.find("</" + m.group(1) + ">", m.end())
    if close < 0:
        close = m.end()
    raw = html[m.end():close]
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text, m.end(), close


def pick_id(text: str, used: set, seq) -> str:
    """優先序：結構型對照表 → 標題 slug（ASCII 為主）→ h2-N（遞增序號）。"""
    key = text.lower().strip()
    cand = STRUCT_MAP.get(key)
    if not cand and key.startswith(CTA_PREFIX):
        cand = "cta-heading"
    if not cand and ascii_ratio(text) > 0.6:
        cand = slugify(text)
        if cand:
            base, n = cand, 2
            while cand in used:
                cand = "%s-%d" % (base, n)
                n += 1
            return cand
    if not cand:
        while True:
            seq[0] += 1
            cand = "h2-%d" % seq[0]
            if cand not in used:
                return cand
    base, n = cand, 2
    while cand in used:
        cand = "%s-%d" % (base, n)
        n += 1
    return cand


def load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def build_cache(root: Path, pages) -> dict:
    """抓所有「缺 title 的 <a>」目標頁 <title>（只抓內部頁，去重）。"""
    hrefs = set()
    for p in pages:
        c = p.read_text(encoding="utf-8", errors="ignore")
        for m in A_RE.finditer(c):
            tag = m.group(0)
            if "title=" in tag:
                continue
            hm = re.search(r'href="([^"]*)"', tag)
            if not hm:
                continue
            h = hm.group(1)
            if not h or h.startswith(("mailto:", "tel:", "javascript:", "#")) or h.startswith("http"):
                continue
            hrefs.add(h.split("#")[0])
    cache = {}
    for i, h in enumerate(sorted(hrefs), 1):
        try:
            req = urllib.request.Request(SITE + h, headers={"User-Agent": "titan-a11y-cache/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                html = r.read().decode("utf-8", errors="ignore")
            m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
            title = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
            cache[h] = title[:110]
        except Exception as e:
            cache[h] = ""
            print("  ⚠️ %s 抓取失敗 %s" % (h, e), file=sys.stderr)
        if i % 20 == 0:
            print("  …%d/%d" % (i, len(hrefs)), file=sys.stderr)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    print("目標頁標題快取：%d 條 → %s" % (len(cache), CACHE))
    return cache


def apply_edits(body: str, edits) -> str:
    """edits = [(start, end, replacement)]，由後往前套用，避免位移失效。"""
    for start, end, repl in sorted(edits, key=lambda x: -x[0]):
        body = body[:start] + repl + body[end:]
    return body


def process(html: str, rel: str, cache: dict, lang: str):
    body, saved = mask_scripts(html)
    used = set(ID_RE.findall(body))
    seq = [0]
    stats = {"h2_id": 0, "section_label": 0, "img_title": 0, "a_title": 0,
             "section_no_heading": 0, "a_no_cache": 0}

    # ---- 1) section aria-labelledby → 區塊內第一個標題（先收集，再倒序套用）----
    sec_spans = [(m.start(), m.group(0)) for m in SEC_RE.finditer(body)]
    closes = [m.start() for m in re.finditer(r"</section>", body)]
    edits = []
    for idx, (s, open_tag) in enumerate(sec_spans):
        if "aria-labelledby" in open_tag or re.search(r"\baria-label=", open_tag):
            continue
        e = closes[idx] if idx < len(closes) else len(body)
        block = body[s:e]
        hm = HEAD_RE.search(block)
        if not hm:
            stats["section_no_heading"] += 1
            continue
        hstart = s + hm.start()
        htag = HEAD_RE.match(body, hstart).group(0)
        text, _, _ = heading_text(body, hstart)
        idm = ID_RE.search(htag)
        if idm:
            hid = idm.group(1)
        else:
            hid = pick_id(text, used, seq)
            used.add(hid)
            edits.append((hstart, hstart + len(htag), add_attr(htag, "id", hid)))
            if htag.startswith("<h2"):
                stats["h2_id"] += 1
        edits.append((s, s + len(open_tag), add_attr(open_tag, "aria-labelledby", hid)))
        stats["section_label"] += 1
    body = apply_edits(body, edits)

    # ---- 2) 剩下沒有 id 的 h2（不在任何 section 內者，例如 nav 的 sr-only）----
    edits = []
    for m in H2_RE.finditer(body):
        if ID_RE.search(m.group(0)):
            continue
        text, _, _ = heading_text(body, m.start())
        hid = pick_id(text, used, seq)
        used.add(hid)
        edits.append((m.start(), m.end(), add_attr(m.group(0), "id", hid)))
        stats["h2_id"] += 1
    body = apply_edits(body, edits)

    # ---- 3) img title ----
    out, pos = [], 0
    for m in IMG_RE.finditer(body):
        tag = m.group(0)
        if "title=" in tag:
            continue
        alt = re.search(r'alt="([^"]*)"', tag)
        altv = alt.group(1).strip() if alt else ""
        if "dya-mark-whitegold" in tag or "logo" in altv.lower():
            ttl = LOGO_TITLE[lang]
        elif altv:
            ttl = altv[:110]
        else:
            continue
        out.append(body[pos:m.start()])
        out.append(add_attr(tag, "title", ttl.replace('"', "&quot;")))
        pos = m.end()
        stats["img_title"] += 1
    out.append(body[pos:])
    body = "".join(out)

    # ---- 4) a title ----
    out, pos = [], 0
    for m in re.finditer(r"(<a\b[^>]*>)(.*?)(</a>)", body, re.S):
        open_tag = m.group(1)
        if "title=" in open_tag:
            continue
        hm = re.search(r'href="([^"]*)"', open_tag)
        href = hm.group(1) if hm else ""
        anchor = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        title = ""
        if href.startswith(SKIP_TITLE_HREF):
            if not anchor:
                continue
            title = ("本頁段落：" if lang == "zh" else "On this page: ") + anchor
        elif href.startswith("http") and "dingyaoadvisory.tw" in href.split("/")[2]:
            # 自家網域的絕對 URL：當內部連結處理（用路徑查快取）
            path = "/" + href.split("/", 3)[3] if href.count("/") >= 3 else "/"
            t = cache.get(path.split("#")[0], "")
            title = ("前往：" if lang == "zh" else "Go to: ") + (t or ("首頁" if path == "/" else anchor))
        elif href.startswith("http"):
            dom = re.sub(r"^https?://([^/]+).*", r"\1", href)
            title = ("在新視窗開啟 " if lang == "zh" else "Opens ") + dom
        else:
            key = href.split("#")[0]
            t = cache.get(key, "")
            if t:
                title = ("前往：" if lang == "zh" else "Go to: ") + t
            elif href.startswith("/blog/"):
                stats["a_no_cache"] += 1
                title = ("閱讀文章：" if lang == "zh" else "Read: ") + anchor
            else:
                stats["a_no_cache"] += 1
                if not anchor:
                    continue
                title = ("前往：" if lang == "zh" else "Go to: ") + anchor
        title = title[:120]
        out.append(body[pos:m.start()])
        out.append(add_attr(open_tag, "title", title.replace('"', "&quot;")) + m.group(2) + m.group(3))
        pos = m.end()
        stats["a_title"] += 1
    out.append(body[pos:])
    body = "".join(out)

    return unmask_scripts(body, saved), stats


def _strip_added(html: str) -> str:
    """剝除本工具會新增的三種屬性（兩側都要剝，否則既有屬性會造成假差異）。"""
    x = re.sub(r' (aria-labelledby)="[^"]*"', "", html)
    x = re.sub(r"(<h[1-4]\b[^>]*?) id=\"[^\"]*\"", r"\1", x)
    # a / img 的 title：只剝「在 <a 或 <img 開標籤內」的 title，避免動到其他屬性
    x = re.sub(r"(<(?:a|img)\b[^>]*?) title=\"[^\"]*\"", r"\1", x)
    return x


def verify(before: str, after: str) -> list:
    """驗證只增屬性：剝除新增屬性後應等於原檔；標籤開閉數不變。"""
    problems = []
    for t in ("section", "h2", "h3", "h1", "a", "picture", "div", "article", "p"):
        o1 = len(re.findall(r"<%s\b" % t, before)); c1 = len(re.findall(r"</%s>" % t, before))
        o2 = len(re.findall(r"<%s\b" % t, after)); c2 = len(re.findall(r"</%s>" % t, after))
        if (o1, c1) != (o2, c2):
            problems.append("%s 開閉數變動 %s/%s → %s/%s" % (t, o1, c1, o2, c2))
    tb = re.findall(r"<[^>]+>|[^<]+", _strip_added(before))
    ta = re.findall(r"<[^>]+>|[^<]+", _strip_added(after))
    if len(tb) != len(ta):
        problems.append("tag/文字 節點數變動 %d → %d" % (len(tb), len(ta)))
    else:
        bad = [(i, x, y) for i, (x, y) in enumerate(zip(tb, ta)) if x.strip() != y.strip()]
        if bad:
            problems.append("剝除新增屬性後仍有 %d 處不一致，首例：%r → %r"
                            % (len(bad), bad[0][1].strip()[:80], bad[0][2].strip()[:80]))
    # 紅線：<title> / meta description / canonical / og:url 不得變
    for pat in (r"<title>.*?</title>", r'<meta\s+name="description"[^>]*>',
                r'<link\s+rel="canonical"[^>]*>', r'<meta\s+property="og:url"[^>]*>'):
        b = re.findall(pat, before, re.S | re.I)
        a = re.findall(pat, after, re.S | re.I)
        if b != a:
            problems.append("紅線屬性被改動：%s" % pat[:30])
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="dist")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--pages", default="")
    ap.add_argument("--build-target-cache", action="store_true")
    args = ap.parse_args()

    root = (REPO / args.root).resolve() if not Path(args.root).is_absolute() else Path(args.root)
    if not root.exists():
        print("❌ root 不存在：%s" % root)
        return 2

    if args.pages:
        pages = [Path(p.strip()).resolve() for p in Path(args.pages).read_text().splitlines() if p.strip()]
    else:
        pages = sorted(p for p in root.rglob("*.html")
                       if "<html" in p.read_text(encoding="utf-8", errors="ignore")[:4000].lower()
                       and not p.name.startswith("sitemap"))
    if args.limit:
        pages = pages[:args.limit]

    if args.build_target_cache:
        build_cache(root, pages)
        return 0

    cache = load_cache()
    grand = {"h2_id": 0, "section_label": 0, "img_title": 0, "a_title": 0,
             "section_no_heading": 0, "a_no_cache": 0}
    rows, failures = [], []
    for p in pages:
        before = p.read_text(encoding="utf-8")
        lang = "en" if re.search(r"-en\.html$", p.name) or 'lang="en"' in before[:2000] else "zh"
        after, st = process(before, str(p.relative_to(root)), cache, lang)
        changed = after != before
        if changed and args.apply:
            problems = verify(before, after)
            if problems:
                failures.append((str(p.relative_to(root)), problems))
                continue
            p.write_text(after, encoding="utf-8")
        for k in grand:
            grand[k] += st[k]
        rows.append((str(p.relative_to(root)), st, changed))

    print("\n%-58s %5s %5s %5s %5s %5s" % ("page", "h2id", "sec", "img", "a", "noHd"))
    for rel, st, changed in rows:
        print("%-58s %5d %5d %5d %5d %5d%s" % (
            rel[:58], st["h2_id"], st["section_label"], st["img_title"], st["a_title"],
            st["section_no_heading"], "" if (changed or not args.apply) else "  (無變動)"))
    print("\n合計：" + " ".join("%s=%d" % (k, v) for k, v in grand.items()))
    print("模式：%s｜頁數 %d" % ("APPLY" if args.apply else "DRY-RUN", len(pages)))
    if failures:
        print("\n❌ 驗證失敗 %d 頁（未寫入）：" % len(failures))
        for rel, probs in failures:
            print("  -", rel)
            for x in probs:
                print("      ·", x)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

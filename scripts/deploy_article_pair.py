#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deploy_article_pair.py — ZH+EN 成對文章部署（圖檔預檢 → 日期改寫 → 上線 → sitemap → 驗證）

為什麼要有這支腳本（三個真實事故）：
  1. 2026-10-27：valuation ZH 草稿留在 dist/blog 被 update_sitemap + IndexNow 收錄 → live 404。
     ⇒ 未部署稿一律留在 _drafts/blog/，本腳本負責「上線當日」才搬進 dist。
  2. 2026-10-26：新文 datePublished 沿用起草日，gen_news_sitemap.py 判 age > 48h 直接跳過 →
     sitemap-news.xml 0 篇。⇒ datePublished / dateModified / 可見日期一律改寫成「實際部署日」。
  3. 2026-10-28：EN 版 7 張圖全 404，若先部署會產生 7 張破圖的 live 頁。
     ⇒ 部署前先 HEAD 檢查所有 assets 圖檔，任一未就緒 → 什麼都不動、exit 2。

用法：
  python3 scripts/deploy_article_pair.py --slug <slug>                 # 今天部署（ZH+EN 同批）
  python3 scripts/deploy_article_pair.py --slug <slug> --dry-run        # 只檢查圖檔與閘門，不寫入
  python3 scripts/deploy_article_pair.py --slug <slug> --rehearse /tmp/x # 沙盒演練（不動 repo、不 push）
  python3 scripts/deploy_article_pair.py --slug <slug> --post-only      # 已上線，只跑 sitemap/news/purge/驗證
  python3 scripts/deploy_article_pair.py --slug <slug> --ignore-images --rehearse /tmp/x  # 無圖演練

Exit codes：0 成功 / 2 圖檔未就緒（未動任何檔） / 3 閘門或 git 失敗 / 4 live 未轉 200
"""
from __future__ import annotations

import argparse
import html as htmlmod
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"
BLOG_DIR = DIST / "blog"
DRAFTS = REPO / "_drafts" / "blog"
SITE = "https://dingyaoadvisory.tw"
ASSETS = "https://assets.dingyaoadvisory.tw/"
CF_ZONE = "3f0348f934248a25899b5c0906135323"
GATE = Path.home() / ".hermes/profiles/martian/skills/content/dingyao-article-assembly/scripts/gate_one.py"
NEWS_GEN = Path.home() / ".hermes/scripts/gen_news_sitemap.py"
INDEXNOW = Path.home() / ".hermes/scripts/indexnow_ping.py"
GSC_INDEXING = REPO / "scripts" / "gsc_request_indexing.py"
GSC_SA = Path.home() / ".hermes/secrets/google-service-account.json"
GSC_SITE = "sc-domain:dingyaoadvisory.tw"
CF_ENV = Path.home() / ".hermes" / ".env"

DEFAULT_TAG_ZH = "置產投資 / 開普敦市政稅 / 房產持有成本"
DEFAULT_TAG_EN = "property investment / cape town property rates / property holding costs"

CARD_ZH = '''      <article class="blog-card fade-in fade-in-delay-1">
        <img src="{hero}" alt="{title}" class="blog-card-img" loading="lazy" title="{title}">
        <div class="blog-card-body">
          <span class="blog-tag">{tag}</span>
          <h3>{title}</h3>
          <div class="blog-meta">
            <span><i class="far fa-calendar"></i> {date}</span>
            <span><i class="far fa-clock"></i> {rt} 分鐘閱讀</span>
          </div>
          <p>{desc}</p>
          <a href="/blog/{slug}" class="blog-link" title="Read More">Read More <i class="fas fa-arrow-right"></i></a>
        </div>
      </article>

'''

CARD_EN = '''  <article class="blog-card fade-in fade-in-delay-1" data-category="investment">
    <img src="{hero}" alt="{title}" class="blog-card-img" loading="lazy" title="{title}">
    <div class="blog-card-body">
      <span class="blog-tag">{tag}</span>
      <h3>{title}</h3>
      <div class="blog-meta">
        <span><i class="far fa-calendar"></i> {date}</span>
        <span><i class="far fa-clock"></i> {rt} min read</span>
      </div>
      <p>{desc}</p>
      <a href="blog/{slug}-en" class="blog-link" title="Read More">Read More <i class="fas fa-arrow-right"></i></a>
    </div>
  </article>

'''


def log(msg: str) -> None:
    print(msg, flush=True)


def run(cmd, cwd: Path = REPO, timeout: int = 900):
    r = subprocess.run([str(c) for c in cmd], cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def http_status(url: str, timeout: int = 20, method: str = "HEAD"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "titan-deploy/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            cl = r.headers.get("content-length")
            return r.status, (r.headers.get("content-type") or ""), int(cl) if cl and cl.isdigit() else 0
    except urllib.error.HTTPError as e:
        return e.code, (e.headers.get("content-type") if e.headers else "") or "", 0
    except Exception as e:  # 連線層錯誤
        return 0, f"ERR:{e}", 0


def assets_in(text: str):
    return sorted(set(re.findall(re.escape(ASSETS) + r"[^\"\s,')]+", text)))


def check_images(urls):
    rows, ok = [], True
    for u in urls:
        st, ct, size = http_status(u)
        good = st == 200 and (ct.startswith("image") or size > 1000)
        if st == 200 and not good:  # HEAD 無 content-type 時用 GET 再確認
            st2, ct2, size2 = http_status(u, method="GET")
            good = st2 == 200 and (ct2.startswith("image") or size2 > 1000)
            st, ct, size = st2, ct2, size2
        if not good:
            ok = False
        rows.append((u.rsplit("/", 1)[-1], st, ct.split(";")[0], size, good))
    return ok, rows


def stamp_dates(text: str, day: str):
    dotted = day.replace("-", ".")
    counts = {}
    for key in ("datePublished", "dateModified"):
        pat = re.compile(r'("' + key + r'"\s*:\s*")(\d{4}-\d{2}-\d{2})(")')
        text, n = pat.subn(lambda m: m.group(1) + day + m.group(3), text)
        counts[key] = n
    pat2 = re.compile(r'(<i class="far fa-calendar"></i>\s*)\d{4}\.\d{2}\.\d{2}')
    text, n2 = pat2.subn(lambda m: m.group(1) + dotted, text)
    counts["visible"] = n2
    return text, counts


def card_fields(text: str, lang: str):
    title = re.search(r'"headline"\s*:\s*"(.*?)"', text, re.S)
    desc = re.search(r'name="description"\s+content="(.*?)"', text, re.S)
    rt = re.search(r"(\d+)\s*(?:分鐘閱讀|min read)", text, re.I)
    if not (title and desc and rt):
        raise SystemExit(f"[FATAL] 無法從文章抽出 headline/description/閱讀時間（lang={lang}）")
    return title.group(1), desc.group(1), rt.group(1)


def esc_attr(s: str) -> str:
    """屬性值用：只跳脫 & < > 與雙引號（保留單引號，與站上既有卡片一致）"""
    return htmlmod.escape(s, quote=False).replace('"', "&quot;")


def build_card(lang: str, slug: str, title: str, desc: str, day: str, rt: str, tag: str) -> str:
    tpl = CARD_ZH if lang == "zh" else CARD_EN
    return tpl.format(
        hero=f"{ASSETS}blog/images/{slug}-hero.webp",
        title=esc_attr(title),
        tag=htmlmod.escape(tag),
        date=day.replace("-", ".") if lang == "zh" else day,
        rt=rt,
        desc=htmlmod.escape(desc),
        slug=slug,
    )


def insert_card(index_text: str, card: str, slug: str):
    if re.search(r'href="(?:/)?blog/' + re.escape(slug) + r'(?:\.html)?"', index_text):
        return index_text, False
    m = re.search(r'<div class="blog-grid[^"]*"[^>]*>', index_text)
    if not m:
        raise SystemExit("[FATAL] dist index 找不到 blog-grid")
    return index_text[: m.end()] + "\n\n" + card + index_text[m.end():], True


def gate_flags(path: Path):
    if not GATE.exists():
        return "GATE_MISSING", ""
    rc, out = run([sys.executable, GATE, path])
    flags = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("FLAGS:")]
    return (flags[-1] if flags else "NO_FLAGS_LINE"), out


def wait_live(urls, budget: int = 900, interval: int = 20):
    deadline = time.time() + budget
    state = {u: 0 for u in urls}
    while time.time() < deadline:
        for u in urls:
            if state[u] == 200:
                continue
            st, _, _ = http_status(f"{u}?v={int(time.time())}", method="GET")
            state[u] = st
        if all(v == 200 for v in state.values()):
            return True, state
        time.sleep(interval)
    return False, state


def purge_cf(urls):
    token = ""
    if CF_ENV.exists():
        for line in CF_ENV.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("CLOUDFLARE_API_TOKEN"):
                token = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    if not token:
        return "SKIP(no token)"
    done, errs = 0, []
    for i in range(0, len(urls), 28):
        body = json.dumps({"files": urls[i : i + 28]}).encode()
        req = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE}/purge_cache",
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode())
                if d.get("success"):
                    done += len(urls[i : i + 28])
                else:
                    errs.append(str(d.get("errors"))[:200])
        except Exception as e:
            errs.append(str(e)[:200])
    return f"purged={done}" + (f" errs={errs}" if errs else "")


def gsc_sitemap_submit():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except Exception as e:
        return f"SKIP(no sdk: {e})"
    if not GSC_SA.exists():
        return "SKIP(no sa)"
    try:
        creds = service_account.Credentials.from_service_account_file(
            str(GSC_SA), scopes=["https://www.googleapis.com/auth/webmasters"]
        )
        svc = build("webmasters", "v3", credentials=creds, cache_discovery=False)
        svc.sitemaps().submit(siteUrl=GSC_SITE, feedpath=f"{SITE}/sitemap.xml").execute()
        return "submitted(200)"
    except Exception as e:
        s = str(e)
        return "submitted(409 already)" if "409" in s else f"ERR {s[:160]}"


# ─────────────────────────── 主流程 ───────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--publish-date", default=None, help="YYYY-MM-DD，預設今天（date 實測）")
    ap.add_argument("--tag-zh", default=DEFAULT_TAG_ZH)
    ap.add_argument("--tag-en", default=DEFAULT_TAG_EN)
    ap.add_argument("--dry-run", action="store_true", help="只檢查圖檔與閘門，不寫檔、不 push")
    ap.add_argument("--rehearse", default=None, help="沙盒目錄，全流程演練但不動 repo")
    ap.add_argument("--ignore-images", action="store_true", help="僅演練用：圖檔 404 也繼續")
    ap.add_argument("--post-only", action="store_true", help="文章已上線，只跑 sitemap/news/purge/驗證")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--strategy", default="S-20261028-VALU-EN", help="策略編號（寫進 commit 訊息）")
    args = ap.parse_args()

    slug = args.slug
    day = args.publish_date or date.today().isoformat()
    zh_draft = DRAFTS / f"{slug}.html"
    en_draft = DRAFTS / f"{slug}-en.html"
    base = Path(args.rehearse) if args.rehearse else REPO
    dist = base / "dist"
    blog = dist / "blog"
    zh_idx = dist / "blog.html"
    en_idx = dist / "blog-en.html"
    urls = [f"{SITE}/blog/{slug}", f"{SITE}/blog/{slug}-en"]

    log(f"== slug={slug} publish_date={day} mode="
        f"{'rehearse' if args.rehearse else 'post-only' if args.post_only else 'dry-run' if args.dry_run else 'deploy'}")

    # ── 1. 圖檔預檢（永遠先做；未就緒則完全不動檔案）
    img_urls = []
    for p in (zh_draft, en_draft):
        if p.exists():
            img_urls += assets_in(p.read_text(encoding="utf-8", errors="ignore"))
    img_urls = sorted(set(img_urls))
    ok_img, rows = check_images(img_urls)
    for name, st, ct, size, good in rows:
        log(f"   {'✅' if good else '❌'} {name}  {st} {ct} {size}B")
    log(f"   圖檔 {sum(1 for r in rows if r[4])}/{len(rows)} 就緒")
    if not ok_img and not (args.ignore_images or args.rehearse):
        log("\n🛑 BLOCKED：圖檔未就緒，未寫入任何檔案、未 push。等木星人上傳後重跑本腳本。")
        return 2
    if not ok_img:
        log("   ⚠️ 演練模式：圖檔 404 仍繼續（不會上線）")

    if args.post_only:
        return post_steps(slug, day, urls, base, dry=args.dry_run, push=not args.no_push)

    # 已上線就不再改日期（避免重跑把 datePublished 推成隔天，破壞 news sitemap 時效）
    if not (args.rehearse or args.dry_run) and all(http_status(u, method="GET")[0] == 200 for u in urls):
        log("✅ 兩版已 live 200（先前已部署）→ 只跑 post 步驟，不改日期")
        return post_steps(slug, day, urls, base, dry=False, push=not args.no_push)

    if not zh_draft.exists() or not en_draft.exists():
        log(f"🛑 BLOCKED：_drafts 缺檔 → {zh_draft.exists()=} {en_draft.exists()=}")
        return 3

    # ── 2/3. 日期改寫 + 搬進 dist（ZH+EN 同批）
    outs = {}
    for lang, draft, dst in (("zh", zh_draft, blog / f"{slug}.html"), ("en", en_draft, blog / f"{slug}-en.html")):
        text = draft.read_text(encoding="utf-8")
        text, counts = stamp_dates(text, day)
        outs[lang] = (text, counts, dst)
        log(f"   [{lang}] 日期改寫 {counts}")
    if args.dry_run:
        for lang, (_, _, dst) in outs.items():
            log(f"   [{lang}] 目標 {dst.relative_to(REPO) if dst.is_relative_to(REPO) else dst}")

    # 沙盒：建立 tmp/dist + tmp/scripts 複本（blog/ 需完整複製，否則 sort 會說其他卡片無 datePublished）
    if args.rehearse:
        blog.mkdir(parents=True, exist_ok=True)
        (base / "scripts").mkdir(exist_ok=True)
        shutil.copy(REPO / "scripts" / "sort_blog_cards.py", base / "scripts" / "sort_blog_cards.py")
        shutil.copy(DIST / "blog.html", zh_idx)
        shutil.copy(DIST / "blog-en.html", en_idx)
        for f in BLOG_DIR.glob("*.html"):
            shutil.copy2(f, blog / f.name)
        log(f"   沙盒：複製 dist/blog/*.html {len(list(BLOG_DIR.glob('*.html')))} 檔供排序器讀 datePublished")

    for lang, (text, _, dst) in outs.items():
        if args.dry_run and not args.rehearse:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        log(f"   [{lang}] 寫入 {dst}")

    # ── 4. 插入 blog 卡片（ZH 進 blog.html；EN 進 blog-en.html）
    for lang, idx in (("zh", zh_idx), ("en", en_idx)):
        text, _, art = outs[lang]
        title, desc, rt = card_fields(text, lang)
        card = build_card(lang, slug, title, desc, day, rt, args.tag_zh if lang == "zh" else args.tag_en)
        idx_text = idx.read_text(encoding="utf-8")
        new_idx, inserted = insert_card(idx_text, card, slug if lang == "zh" else f"{slug}-en")
        if args.dry_run and not args.rehearse:
            log(f"   [{lang}] 卡片{'會' if inserted else '已存在，跳過'}插入（dry-run 未寫入）")
            continue
        idx.write_text(new_idx, encoding="utf-8")
        log(f"   [{lang}] 卡片{'已插入' if inserted else '已存在，跳過'} → {idx}")

    # ── 5. 卡片排序（sort_blog_cards.py，唯一合法排序工具）
    if not (args.dry_run and not args.rehearse):
        rc, out = run([sys.executable, base / "scripts" / "sort_blog_cards.py"])
        tail = "\n".join(out.strip().splitlines()[-14:])
        log(tail)
        if rc != 0 or "✅ ALL SORT/FORMAT CHECKS PASSED" not in out:
            log("🛑 卡片排序/格式檢查失敗，嚴禁 push")
            return 3

    if args.rehearse:
        text = zh_idx.read_text(encoding="utf-8")
        i = text.find(f'/blog/{slug}"')
        log("\n=== 演練結果 ===")
        log(f"ZH 卡片數: {len(re.findall(r'<article class=.blog-card', zh_idx.read_text(encoding='utf-8')))}")
        log(f"EN 卡片數: {len(re.findall(r'<article class=.blog-card', en_idx.read_text(encoding='utf-8')))}")
        log(f"ZH 首張卡是否本文: {i>0}")
        log("（沙盒檔案在 %s，repo 未被修改）" % base)
        return 0

    if args.dry_run:
        log("\n(dry-run) 圖檔與閘門檢查完成，未寫入、未 push。")
        return 0

    # ── 6. 閘門（EN 必須 FLAGS: none；ZH 僅記錄）
    en_flags, _ = gate_flags(blog / f"{slug}-en.html")
    zh_flags, _ = gate_flags(blog / f"{slug}.html")
    log(f"   gate EN: {en_flags}")
    log(f"   gate ZH: {zh_flags}（ZH 既有狀態，裁決不重寫，僅記錄）")
    if en_flags != "FLAGS: none":
        log("🛑 EN 閘門未過，停止 push")
        return 3

    # ── 7. commit + push（push main = GitHub Actions 自動部署）
    rc, out = run(["git", "fetch", "origin", "main"], timeout=180)
    rc, out = run(["git", "pull", "--rebase", "origin", "main"], timeout=180)
    if rc != 0:
        log("🛑 git pull --rebase 失敗（工作區可能被其他流程改動），請人工處理：")
        log(out[-800:])
        return 3
    files = [blog / f"{slug}.html", blog / f"{slug}-en.html", zh_idx, en_idx]
    rc, out = run(["git", "add"] + [str(f.relative_to(REPO)) for f in files])
    if rc != 0:
        log(out)
        return 3
    strat = f"，{args.strategy}" if args.strategy else ""
    msg = f"feat(blog): 上線 {slug} ZH+EN（datePublished={day}{strat}）"
    rc, out = run(["git", "commit", "-m", msg])
    log(out.strip().splitlines()[0] if out.strip() else "(no commit output)")
    if rc != 0 and "nothing to commit" not in out:
        return 3
    if not args.no_push:
        rc, out = run(["git", "push", "origin", "HEAD"], timeout=300)
        if rc != 0 and ("rejected" in out or "non-fast-forward" in out or "fetch first" in out):
            log("   push 被拒 → pull --rebase 後重試一次")
            run(["git", "pull", "--rebase", "origin", "main"], timeout=180)
            rc, out = run(["git", "push", "origin", "HEAD"], timeout=300)
        log(out.strip()[-400:])
        if rc != 0:
            return 3

    # ── 8. 等 live 200
    log("   等待 Cloudflare 部署（GitHub Actions，最長 15 分鐘）…")
    ok, state = wait_live(urls)
    for u, st in state.items():
        log(f"   {'✅' if st == 200 else '❌'} {u} → {st}")
    if not ok:
        log("🛑 live 未轉 200；sitemap/news 步驟跳過（避免收錄 404）")
        return 4

    rc = post_steps(slug, day, urls, REPO, dry=False, push=not args.no_push)
    if rc == 0 and not args.no_push:
        arch = DRAFTS / "deployed"
        arch.mkdir(parents=True, exist_ok=True)
        for p in (zh_draft, en_draft):
            if p.exists():
                shutil.move(str(p), str(arch / p.name))
        log(f"   已上線草稿歸檔 → {arch}（避免日後重跑把 datePublished 推成隔天）")
    return rc


def restore_fx_links(base: Path, slug: str, marker: str = "2026-10-28 titan"):
    """上線後必做：還原 fx-tracker ZH/EN 被註解的 valuation 內連（土星人 2026-10-28 裁決步驟 A）。

    為什麼：valuation 頁上線前，fx-tracker 的「相關閱讀」有一條指向它的內連是 live 404，
    先以 `<!-- marker ... -->` 包起來止血；上線後必須確定性還原，否則該頁永遠少一條內向連結。
    """
    tool = base / "scripts" / "restore_commented_block.py"
    targets = [
        base / "dist" / "blog" / "south-africa-interest-rate-fx-tracker-2026.html",
        base / "dist" / "blog" / "south-africa-interest-rate-fx-tracker-2026-en.html",
    ]
    targets = [t for t in targets if t.exists()]
    if not tool.exists() or not targets:
        log(f"   ⚠️ fx-tracker 還原略過（tool={tool.exists()} targets={len(targets)}）")
        return None
    rc, out = run([sys.executable, tool] + [str(t) for t in targets] + ["--marker", marker])
    log("   fx-tracker 還原: " + (out.strip().splitlines()[-1] if out.strip() else f"rc={rc}"))
    rc2, out2 = run([sys.executable, tool] + [str(t) for t in targets] + ["--marker", marker, "--check"])
    remaining = out2.strip().splitlines()[-1] if out2.strip() else ""
    log(f"   fx-tracker --check: rc={rc2} {remaining[:120]}")
    hits = {}
    pat = re.compile(r'href="/blog/' + re.escape(slug) + r'(?:-en)?"')
    for t in targets:
        hits[t.name] = len(pat.findall(t.read_text(encoding="utf-8")))
    log(f"   fx-tracker 指向 valuation 的 href: {hits}")
    return rc2 == 0 and all(v >= 1 for v in hits.values())


def post_steps(slug, day, urls, base: Path, dry: bool = False, push: bool = True):
    """live 200 之後：fx-tracker 內連還原 → sitemap → news sitemap → push → purge → IndexNow/GSC → 最終驗證"""
    log("\n── post：fx-tracker 內連 / sitemap / news sitemap / purge / 索引 ──")
    fx_ok = restore_fx_links(base, slug)
    if dry:
        fx_ok = None
    rc, out = run([sys.executable, base / "scripts" / "update_sitemap.py", slug])
    log("\n".join(out.strip().splitlines()[-12:]))
    sm = (base / "dist" / "sitemap.xml").read_text(encoding="utf-8")
    sm_ok = all(f"<loc>{u}</loc>" in sm for u in urls) and f"/blog/{slug}.html" not in sm
    log(f"   sitemap 收錄 ZH+EN（無 .html）: {'✅' if sm_ok else '❌'}")

    rc, out = run([sys.executable, NEWS_GEN])
    log("\n".join(out.strip().splitlines()[-10:]))
    news_path = base / "dist" / "sitemap-news.xml"
    news = news_path.read_text(encoding="utf-8") if news_path.exists() else ""
    news_hit = [u for u in urls if f"<loc>{u}</loc>" in news]
    log(f"   news sitemap 收錄: {len(news_hit)}/2 {news_hit}")

    if dry:
        log("(dry-run) 未 push、未 purge")
        return 0

    if push:
        targets = [
            "dist/sitemap.xml",
            "dist/sitemap-news.xml",
            "dist/blog/south-africa-interest-rate-fx-tracker-2026.html",
            "dist/blog/south-africa-interest-rate-fx-tracker-2026-en.html",
        ]
        rc, _ = run(["git", "add"] + targets)
        rc, out = run(["git", "commit", "-m", f"chore(seo): {slug} 進 sitemap + news sitemap（{day}）"])
        log("   " + (out.strip().splitlines()[0] if out.strip() else "(no changes)"))
        if "nothing to commit" not in out:
            rc, out = run(["git", "push", "origin", "HEAD"], timeout=300)
            log("   " + out.strip()[-200:])

    purge_urls = urls + [f"{SITE}/blog", f"{SITE}/blog-en", f"{SITE}/sitemap.xml", f"{SITE}/sitemap-news.xml"]
    log(f"   CF purge: {purge_cf(purge_urls)}")

    if INDEXNOW.exists():
        rc, out = run([sys.executable, INDEXNOW] + urls)
        log(f"   IndexNow: {out.strip().splitlines()[-2] if out.strip() else 'no output'}")
    if GSC_INDEXING.exists():
        rc, out = run([sys.executable, GSC_INDEXING] + urls, timeout=300)
        log(f"   GSC Indexing API: {out.strip().splitlines()[-1] if out.strip() else 'no output'}")
    log(f"   GSC sitemap submit: {gsc_sitemap_submit()}")

    # ── 最終驗證（live 實測，不靠自認）
    log("\n── 最終驗證（live）──")
    all_ok = True
    for u in urls:
        st, ct, _ = http_status(f"{u}?v={int(time.time())}", method="GET")
        log(f"   {'✅' if st == 200 else '❌'} {u} → {st} {ct}")
        all_ok &= st == 200
    art = (base / "dist" / "blog" / f"{slug}-en.html").read_text(encoding="utf-8")
    img_urls = assets_in(art)
    ok_img, rows = check_images(img_urls)
    log(f"   圖檔 {sum(1 for r in rows if r[4])}/{len(rows)} 200")
    all_ok &= ok_img
    # hreflang 互指
    zh_p = (base / "dist" / "blog" / f"{slug}.html").read_text(encoding="utf-8")
    en_p = art
    pair_ok = (f'hreflang="en" href="{SITE}/blog/{slug}-en"' in zh_p) and (
        f'hreflang="zh-TW" href="{SITE}/blog/{slug}"' in en_p
    )
    log(f"   hreflang 互指: {'✅' if pair_ok else '❌'}")
    all_ok &= pair_ok
    if fx_ok is not None:
        log(f"   fx-tracker 內連已還原: {'✅' if fx_ok else '❌'}")
        all_ok &= fx_ok

    log("\n" + ("✅ 部署完成，全部驗證通過" if all_ok else "⚠️ 部署完成但有驗證項失敗（見上）"))
    return 0 if all_ok else 4


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""共用：從 production 模板衍生 DingYao 文章（結構邊界抽取，不依賴註解字串）。"""
import re, json, os

REPO = "/Users/dingyao/Documents/DingYao-Website/dingyaoadvisory-website"
TPL_ZH = os.path.join(REPO, "dist/blog/standard-bank-non-resident-account-2026.html")
TPL_EN = os.path.join(REPO, "dist/blog/standard-bank-non-resident-account-2026-en.html")
OUT = os.path.expanduser("~/Documents/DingYao-Website/dingyaoadvisory-website/runs/2026-10-24")
SITE = "https://dingyaoadvisory.tw"
ASSETS = "https://assets.dingyaoadvisory.tw/blog/images"
TODAY = "2026-10-24"


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def split_tpl(tpl):
    """回傳 (head_prefix, head_suffix, herohdr_placeholder_pos, body_start, cta_start)"""
    # head_prefix: DOCTYPE -> manifest link (inclusive)
    man = tpl.index('<link rel="manifest"')
    man_end = tpl.index(">", man) + 1
    head_prefix = tpl[:man_end]
    # head_suffix: preconnect -> </head> inclusive
    pre = tpl.index('<link rel="preconnect"')
    hend = tpl.index("</head>") + len("</head>")
    head_suffix = tpl[pre:hend]
    hero = tpl.index("<!-- ARTICLE HERO -->")
    body = tpl.index("<!-- ARTICLE BODY -->")
    cta = tpl.index("<!-- CTA -->")
    return head_prefix, head_suffix, hero, body, cta


def build_meta_zh(slug, title, desc, keywords, h1_plain, image_alt):
    url = f"{SITE}/blog/{slug}"
    url_en = f"{SITE}/blog/{slug}-en"
    return f"""<title>{title}</title><meta name="description" content="{desc}"><meta name="keywords" content="{keywords}"><meta name="author" content="Scott Huang"><meta name="robots" content="index, follow"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="zh-TW" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><link rel="alternate" hreflang="en" href="{url_en}"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:type" content="article"><meta property="og:url" content="{url}"><meta property="og:image" content="{ASSETS}/{slug}-hero.webp"><meta property="og:locale" content="zh_TW"><meta property="og:site_name" content="鼎曜國際顧問 DingYao Advisory"><meta name="twitter:image" content="{ASSETS}/{slug}-hero.webp"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}">"""


def build_meta_en(slug, title, desc, image_alt):
    url = f"{SITE}/blog/{slug}-en"
    url_zh = f"{SITE}/blog/{slug}"
    return f"""<title>{title}</title><meta name="description" content="{desc}"><meta name="author" content="Scott Huang"><meta name="robots" content="index, follow"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="en" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}"><link rel="alternate" hreflang="zh-TW" href="{url_zh}"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:type" content="article"><meta property="og:url" content="{url}"><meta property="og:image" content="{ASSETS}/{slug}-hero.webp"><meta property="og:locale" content="en_US"><meta property="og:site_name" content="DingYao Advisory"><meta name="twitter:image" content="{ASSETS}/{slug}-hero.webp"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}">"""


def jsonld_zh(slug, headline, desc, faqs, breadcrumb_label):
    url = f"{SITE}/blog/{slug}"
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": headline, "description": desc,
        "image": f"{ASSETS}/{slug}-hero.webp",
        "datePublished": TODAY, "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Scott Huang"},
        "publisher": {"@type": "Organization", "name": "鼎曜國際顧問 DingYao Advisory", "url": SITE},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首頁", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "鼎曜觀點", "item": SITE + "/blog"},
        {"@type": "ListItem", "position": 3, "name": breadcrumb_label, "item": url}]}
    ws = {"@context": "https://schema.org", "@type": "WebSite",
          "name": "鼎曜國際顧問 DingYao Advisory", "url": SITE,
          "potentialAction": {"@type": "SearchAction",
                              "target": SITE + "/blog?q={search_term_string}",
                              "query-input": "required name=search_term_string"}}
    return "".join('<script type="application/ld+json">\n' + json.dumps(o, ensure_ascii=False, indent=2) + "\n</script>" for o in (article, faq, bc, ws))


def jsonld_en(slug, headline, desc, faqs, breadcrumb_label):
    url = f"{SITE}/blog/{slug}-en"
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": headline, "description": desc,
        "image": f"{ASSETS}/{slug}-hero.webp",
        "datePublished": TODAY, "dateModified": TODAY,
        "author": {"@type": "Person", "name": "Scott Huang"},
        "publisher": {"@type": "Organization", "name": "DingYao Advisory", "url": SITE},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/index-en"},
        {"@type": "ListItem", "position": 2, "name": "Insights", "item": SITE + "/blog-en"},
        {"@type": "ListItem", "position": 3, "name": breadcrumb_label, "item": url}]}
    ws = {"@context": "https://schema.org", "@type": "WebSite",
          "name": "DingYao Advisory", "url": SITE,
          "potentialAction": {"@type": "SearchAction",
                              "target": SITE + "/blog-en?q={search_term_string}",
                              "query-input": "required name=search_term_string"}}
    return "".join('<script type="application/ld+json">\n' + json.dumps(o, ensure_ascii=False, indent=2) + "\n</script>" for o in (article, faq, bc, ws))


def section(slug, n, caption, alt, inner):
    """每個 h2 一個獨立 section + 專屬背景圖 s{n}"""
    return f"""<div class="section">
  <div class="section-bg">
    <figure><picture>
      <source srcset="{ASSETS}/{slug}-s{n}.webp" type="image/webp">
      <img src="{ASSETS}/{slug}-s{n}.webp" alt="{alt}" loading="lazy" title="{alt}">
    </picture>
    <figcaption>{caption}</figcaption>
</figure>
    <div class="section-bg-overlay"></div>
  </div>
  <div class="container">
    <section class="article-body fade-in visible">
{inner}
    </section>
  </div>
</div>"""


def intro_section(inner):
    return f"""<div class="section" style="padding-top:0">
  <div class="container">
    <section class="article-body fade-in visible">
{inner}
    </section>
  </div>
</div>"""


def assemble(head_prefix, meta, head_suffix, nav_blk, herohdr, body, tail):
    return head_prefix + meta + head_suffix + nav_blk + herohdr + body + tail

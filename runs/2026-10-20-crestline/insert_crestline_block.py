#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 blog 文章「結論 CTA 之前」插入 Crestline Advisory 導引區塊。

土星人 2026-10-20 政策：全站文章都要讓讀者知道透過合作夥伴 Crestline Advisory
協助可少走錯路、加快速度。

特性：
  - 冪等：已有 id="crestline-assist" 的檔案直接 SKIP
  - 自動判斷語系（-en 檔名 → 英文文案）
  - 插入點優先序：最後一個 cta-section 之前 → </main> 之前
  - 不改動文章原有內容，只插入

用法：
    python3 insert_crestline_block.py <html 路徑> [更多路徑...]
    python3 insert_crestline_block.py --dry dist/blog/*.html
"""
import pathlib
import re
import sys

MARKER = 'id="crestline-assist"'

STYLE = """<style>
.crestline-assist{background:linear-gradient(180deg,#0A0E17 0%,#070A11 100%);border-top:1px solid rgba(201,168,76,.18);border-bottom:1px solid rgba(201,168,76,.18);padding:4.5rem 0}
.crestline-assist .ca-inner{max-width:920px;margin:0 auto;padding:0 1.5rem}
.crestline-assist h2{font-family:'Playfair Display',serif;font-size:1.85rem;line-height:1.4;color:#F5F0E8;margin:0 0 1.25rem}
.crestline-assist h2 span{color:#C9A84C}
.crestline-assist h3{font-family:'Playfair Display',serif;font-size:1.12rem;color:#C9A84C;margin:1.9rem 0 1rem;letter-spacing:.02em}
.crestline-assist p{color:#EDE7D9;line-height:1.95;margin:0 0 1.1rem}
.crestline-assist ul{list-style:none;padding:0;margin:0 0 1.4rem}
.crestline-assist li{position:relative;padding-left:1.4rem;margin-bottom:.95rem;color:#EDE7D9;line-height:1.85}
.crestline-assist li::before{content:'';position:absolute;left:0;top:.72em;width:6px;height:6px;border-radius:50%;background:#C9A84C}
.crestline-assist strong{color:#F5F0E8;font-weight:600}
.crestline-assist .ca-cta{margin-top:2rem}
.crestline-assist .ca-cta .btn{margin-top:0}
@media(max-width:768px){.crestline-assist{padding:3rem 0}.crestline-assist h2{font-size:1.45rem}.crestline-assist h3{font-size:1.02rem}.crestline-assist p,.crestline-assist li{line-height:1.85}}
</style>"""

ZH_BODY = """<section class="crestline-assist" id="crestline-assist">
  <div class="ca-inner">
    <h2>為什麼要透過 <span>Crestline Advisory</span> 協助？</h2>
    <p>南非銀行的開戶要求每年都在調整，而且調整的往往是「格式」而不是「資格」—— 一樣的護照、一樣的地址證明，格式不對就是退件。</p>
    <h3>自己辦最常卡住的三件事</h3>
    <ul>
      <li><strong>護照認證格式不符</strong>：只寫「與正本相符」的中文認證不被接受，必須由宣誓專員以英文逐字寫明確認為正本、含照片者加註相貌相符，並附簽名、日期、地址與職業。這一項我們處理過的案件裡，退件率最高。</li>
      <li><strong>TIN 欄位留空又沒勾理由</strong>：台灣客戶的稅務編號就是身分證字號，留空必須勾選 Reason A／B／C 並說明，漏了就是退回重送。</li>
      <li><strong>地址證明超過三個月</strong>：從申請日起算，超過期限整份申請失效，要全部重來。</li>
    </ul>
    <p>透過我們的合作夥伴 Crestline Advisory（南非在地執行）協助，這些環節會在送件前先確認到位：</p>
    <ul>
      <li>文件格式逐項預檢，避免退回重送（一趟往返就是 2 到 4 週）</li>
      <li>依當期銀行要求確認是否需要親赴開普敦面簽，先確定再買機票</li>
      <li>匯款路徑與 BOP 申報類別先對好，避免資金卡在合規審查</li>
      <li>送件後由在地團隊追蹤進度，不用自己跨時區打電話</li>
    </ul>
    <p>鼎曜在台灣端負責確認你的資料與文件正確性，確認後轉交 Crestline Advisory 執行。你不會拿到一份「自己看著辦」的清單。</p>
    <div class="ca-cta"><a href="/south-africa-bank-account#booking" class="btn btn-primary" title="預約 30 分鐘顧問評估">預約 30 分鐘顧問評估 <i class="fas fa-arrow-right"></i></a></div>
  </div>
</section>"""

EN_BODY = """<section class="crestline-assist" id="crestline-assist">
  <div class="ca-inner">
    <h2>Why Handle This Through <span>Crestline Advisory</span>?</h2>
    <p>South African documentation requirements change every year — and what changes is usually the format, not the eligibility. Same passport, same proof of address, wrong format, rejection.</p>
    <h3>The three most common failure points</h3>
    <ul>
      <li><strong>Passport certification rejected</strong>: A plain true-copy stamp is not accepted. A commissioner of oaths must certify in English, confirm the original was seen, add a true-likeness statement for photo pages, and include signature, date, address and occupation.</li>
      <li><strong>TIN left blank without a reason code</strong>: For Taiwanese clients the tax number is the national ID number. Leaving it blank requires ticking Reason A / B / C with an explanation.</li>
      <li><strong>Proof of address older than three months</strong>: Measured from the application date. Past the deadline the entire application is void and must be resubmitted.</li>
    </ul>
    <p>Working through our partner Crestline Advisory (on-the-ground execution in South Africa) means these are checked before submission: document format pre-screened item by item (avoiding a 2-4 week round trip), current bank requirements confirmed before you book any flight, remittance routing and BOP declaration categories aligned in advance, and progress tracked locally after submission.</p>
    <p>DingYao verifies your documents on the Taiwan side and hands over to Crestline Advisory for execution. You do not receive a checklist and left to figure it out alone.</p>
    <div class="ca-cta"><a href="/south-africa-bank-account-en#booking" class="btn btn-primary" title="Book a 30-minute consultation">Book a 30-minute consultation <i class="fas fa-arrow-right"></i></a></div>
  </div>
</section>"""


def is_english(path: pathlib.Path) -> bool:
    return path.stem.endswith("-en")


def find_insert_point(c: str):
    """回傳 (index, 說明)；優先插在最後一個 cta-section 之前。

    站上有三種收尾結構：
      1. <section class="section cta-section">
      2. <section class="conclusion">（少數舊文，無 </main>）
      3. </main>
    """
    hits = [m.start() for m in re.finditer(r'<section[^>]*class="[^"]*cta-section', c)]
    if hits:
        return hits[-1], "cta-section 之前"
    hits = [m.start() for m in re.finditer(r'<section[^>]*class="[^"]*conclusion', c)]
    if hits:
        return hits[-1], "conclusion section 之前"
    m = c.rfind("</main>")
    if m > 0:
        return m, "</main> 之前"
    return None, "找不到插入點"


def process(path: pathlib.Path, dry: bool = False):
    c = path.read_text(encoding="utf-8")
    if MARKER in c:
        return "SKIP", "已有區塊"
    if "</body>" not in c:
        return "MISS", "不是完整 HTML"
    idx, why = find_insert_point(c)
    if idx is None:
        return "MISS", why
    block = (STYLE + "\n" + (EN_BODY if is_english(path) else ZH_BODY) + "\n")
    new = c[:idx] + "<!-- Crestline Advisory 導引（土星人 2026-10-20 政策） -->\n" + block + c[idx:]
    if not dry:
        path.write_text(new, encoding="utf-8")
    return "OK", why


def main():
    args = [a for a in sys.argv[1:] if a != "--dry"]
    dry = "--dry" in sys.argv
    files = []
    for a in args:
        p = pathlib.Path(a)
        files.extend(sorted(p.parent.glob(p.name)) if "*" in a else [p])
    ok = skip = miss = 0
    for f in files:
        status, why = process(f, dry)
        if status == "OK":
            ok += 1
        elif status == "SKIP":
            skip += 1
        else:
            miss += 1
            print(f"  MISS {f.name}: {why}")
    print(f"\n{'[DRY] ' if dry else ''}OK={ok} SKIP={skip} MISS={miss} / 共 {len(files)} 檔")


if __name__ == "__main__":
    main()

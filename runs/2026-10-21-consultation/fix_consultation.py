#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""consultation 轉換頁三處結構性漏單修正（土星人 2026-10-21，太陽人 Three Tens 診斷）

① 預算下拉新增最低選項「1000 萬以下／僅開戶（R10 萬起）」
② 「感興趣的服務」新增「南非開戶・高息活存」
③ 頁尾補簽約主體與公司登記資訊

用法：python3 fix_consultation.py [--dry]
"""
import pathlib
import re
import sys

ROOT = pathlib.Path("dist")

# ══════════════════════════════════════════
# ① 預算
# ══════════════════════════════════════════
BUDGET = {
    "consultation.html": {
        "anchor": '<option value="">請選擇預算範圍</option>',
        "new": '\n              <option value="account-only">1000 萬以下／僅開戶（R100,000 起）</option>',
    },
    "consultation-en.html": {
        "anchor": '<option value="">Please select a budget range</option>',
        "new": '\n              <option value="account-only">Under NT$10M / Account only (from R100,000)</option>',
    },
}

# ══════════════════════════════════════════
# ② 服務選項
# ══════════════════════════════════════════
SERVICE = {
    "consultation.html": {
        "anchor": '<option value="property">南非置產 (莊園/豪宅)</option>',
        "new": '\n              <option value="bank">南非開戶・高息活存</option>',
    },
    "consultation-en.html": {
        "anchor": '<option value="property">South Africa Property (Estates/Luxury Homes)</option>',
        "new": '\n              <option value="bank">South Africa Bank Account (High-Yield Call Account)</option>',
    },
}

# ══════════════════════════════════════════
# ③ 信任區塊（插在 </form> 之後、form-success 之前）
# ══════════════════════════════════════════
TRUST_ZH = """
        <div class="trust-note" style="margin-top:28px;padding:22px 24px;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.22);border-radius:8px;">
          <p style="margin:0 0 12px;font-size:.94rem;color:var(--cream);line-height:1.9;">
            <strong style="color:#C9A84C;">簽約主體</strong>：置產＝<strong>Crestline Advisory</strong>、開戶＝<strong>Standard Bank</strong>；鼎曜不代收資金，金流不經過我們。
          </p>
          <p style="margin:0;font-size:.86rem;color:var(--text-muted);line-height:1.85;">
            鼎曜國際顧問｜公司登記與統一編號可於諮詢時提供查驗；合約範本、匯款憑證、在地律師與代書資料，我們在諮詢時都可以提供。
          </p>
        </div>
"""

TRUST_EN = """
        <div class="trust-note" style="margin-top:28px;padding:22px 24px;background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.22);border-radius:8px;">
          <p style="margin:0 0 12px;font-size:.94rem;color:var(--cream);line-height:1.9;">
            <strong style="color:#C9A84C;">Contracting parties</strong>: property = <strong>Crestline Advisory</strong>, bank account = <strong>Standard Bank</strong>. DingYao does not collect funds on their behalf; money never passes through us.
          </p>
          <p style="margin:0;font-size:.86rem;color:var(--text-muted);line-height:1.85;">
            DingYao Advisory — company registration and tax ID available for verification on request. Contract templates, remittance records and local attorney/conveyancer details can all be provided during consultation.
          </p>
        </div>
"""


def apply(dry):
    for fname in ["consultation.html", "consultation-en.html"]:
        p = ROOT / fname
        if not p.exists():
            print(f"  ⚠️ {fname} 不存在")
            continue
        c = p.read_text(encoding="utf-8")
        orig = c
        log = []

        # ① 預算
        b = BUDGET[fname]
        if "account-only" in c:
            log.append("① 預算：已有")
        elif b["anchor"] in c:
            c = c.replace(b["anchor"], b["anchor"] + b["new"], 1)
            log.append("① 預算：已加最低選項")
        else:
            log.append("① 預算：找不到錨點 ⚠️")

        # ② 服務
        s = SERVICE[fname]
        if '<option value="bank">' in c:
            log.append("② 服務：已有")
        elif s["anchor"] in c:
            c = c.replace(s["anchor"], s["anchor"] + s["new"], 1)
            log.append("② 服務：已加南非開戶")
        else:
            log.append("② 服務：找不到錨點 ⚠️")

        # ③ 信任區塊
        trust = TRUST_ZH if fname == "consultation.html" else TRUST_EN
        if 'class="trust-note"' in c:
            log.append("③ 信任區塊：已有")
        else:
            m = re.search(r"</form>\s*(<div class=\"form-success\")", c)
            if m:
                c = c[:m.start(1)] + trust.strip() + "\n        " + c[m.start(1):]
                log.append("③ 信任區塊：已插入（form 後、success 前）")
            else:
                log.append("③ 信任區塊：找不到錨點 ⚠️")

        if not dry and c != orig:
            p.write_text(c, encoding="utf-8")
        print(f"=== {fname} ===")
        for x in log:
            print("   ", x)


if __name__ == "__main__":
    apply("--dry" in sys.argv)

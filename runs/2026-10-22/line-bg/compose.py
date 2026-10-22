#!/usr/bin/env python3
"""2026-10-22 LINE 選單／官網背景圖 — 深藍底 + 半透明影像合成
輸入: src/<theme>.png (ComfyUI 原生 3:2 大圖)
輸出: line-bg-<theme>.png          2500x1686  (LINE rich menu)
      line-bg-<theme>-1920x1080.png 1920x1080 (官網)
"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")

THEMES = {
    "banking":   dict(vpos=0.50, alpha=0.34),
    "property":  dict(vpos=0.44, alpha=0.34),
    "education": dict(vpos=0.50, alpha=0.34),
}

# 深藍品牌底色
NAVY_TOP = np.array([11, 19, 43], dtype=np.float64) / 255.0    # #0B132B
NAVY_MID = np.array([10, 14, 23], dtype=np.float64) / 255.0    # #0A0E17
NAVY_BOT = np.array([7, 10, 17], dtype=np.float64) / 255.0     # #070A11
GOLD = np.array([197, 168, 128], dtype=np.float64) / 255.0     # #C5A880

# duotone ramp
RAMP_X = np.array([0.00, 0.22, 0.45, 0.72, 1.00])
RAMP_C = np.array([
    [6, 9, 16],
    [13, 22, 40],
    [27, 50, 84],
    [45, 82, 126],
    [96, 138, 186],
], dtype=np.float64) / 255.0


def cover(img, w, h, vpos=0.5):
    sw, sh = img.size
    s = max(w / sw, h / sh)
    nw, nh = int(round(sw * s)), int(round(sh * s))
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    top = int(round((nh - h) * vpos))
    return img.crop((left, top, left + w, top + h))


def ramp(l):
    out = np.empty(l.shape + (3,), dtype=np.float64)
    for c in range(3):
        out[..., c] = np.interp(l, RAMP_X, RAMP_C[:, c])
    return out


def gauss(v, c, s):
    return np.exp(-((v - c) ** 2) / (2 * s * s))


def build(src_path, w, h, vpos, alpha_base, tag):
    img = Image.open(src_path).convert("RGB")
    img = cover(img, w, h, vpos)
    a = np.asarray(img, dtype=np.float64) / 255.0

    # ---- 冷藍分色 ----
    L = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])
    Ls = np.asarray(Image.fromarray((L * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(1.2)), dtype=np.float64) / 255.0
    # 色階正規化（藍調夜景原始動態範圍很窄 → 先拉伸再加權）
    p1, p99 = np.percentile(Ls, 1.5), np.percentile(Ls, 99.5)
    Ln = np.clip((Ls - p1) / max(p99 - p1, 1e-6), 0, 1) ** 0.88
    duo = ramp(Ln)

    # 保留少量原始色彩（冷調），避免死板
    orig_cool = a * np.array([0.30, 0.42, 0.62])
    graded = 0.82 * duo + 0.18 * orig_cool

    # 暖金餘暉：只留原圖的暖色光點（先用於影像層的局部去藍，最後再全域加回金色光點）
    warm = np.clip(a[..., 0] - a[..., 2], 0, 1)
    warm = np.asarray(Image.fromarray((np.clip(warm, 0, 1) * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(2.0)), dtype=np.float64) / 255.0
    graded = graded * (1 - 0.65 * warm[..., None]) + (GOLD * 1.05) * 0.65 * warm[..., None] * np.clip(Ls[..., None] * 2.2, 0, 1)

    # ---- 對比微調（保持中低對比，適合疊字）----
    graded = np.clip((graded - 0.5) * 1.07 + 0.5, 0, 1)
    graded = np.clip(graded ** 1.04, 0, 1)

    # ---- 亮度標定：影像層本身要先夠亮，乘上 alpha 才「透得出來」----
    gm = float(graded.mean())
    if gm > 1e-6:
        graded = np.clip(graded * (0.32 / gm), 0, 1)

    # ---- 深藍底 ----
    yy = np.linspace(0, 1, h)[:, None, None]
    base = np.where(yy < 0.5,
                    NAVY_TOP + (NAVY_MID - NAVY_TOP) * (yy / 0.5),
                    NAVY_MID + (NAVY_BOT - NAVY_MID) * ((yy - 0.5) / 0.5))
    base = np.repeat(base, w, axis=1)

    # 中心偏左上柔光（避免全平面死板）
    xx = np.linspace(0, 1, w)[None, :]
    yg = np.linspace(0, 1, h)[:, None]
    glow = gauss(xx, 0.42, 0.34) * gauss(yg, 0.40, 0.30)
    base = np.clip(base + glow[..., None] * (np.array([0.055, 0.075, 0.115])), 0, 1)

    # ---- 半透明遮罩（文字區更暗）----
    ay = np.linspace(0, 1, h)[:, None]
    ax = np.linspace(0, 1, w)[None, :]
    mask = np.ones((h, w))
    mask *= (1 - 0.26 * gauss(ay, 0.29, 0.13))     # 中上文字區
    mask *= (1 - 0.26 * gauss(ay, 0.71, 0.15))     # 中下文字區
    mask *= (1 - 0.14 * gauss(ax, 0.50, 0.26))     # 中央文字欄
    mask *= (1 - 0.55 * gauss(ay, 0.02, 0.055))    # 最上緣
    mask *= (1 - 0.55 * gauss(ay, 0.98, 0.045))    # 最下緣
    alpha = np.clip(alpha_base * mask, 0.0, 0.45)[..., None]

    out = base * (1 - alpha) + graded * alpha

    # ---- 邊角暗角（在上下漸層之前，四角最後仍會回到深藍）----
    vg = 1 - 0.30 * (gauss(xx, 0.02, 0.22) + gauss(xx, 0.98, 0.22) +
                     gauss(yg, 0.02, 0.18) + gauss(yg, 0.98, 0.16))
    out = out * np.clip(vg, 0.55, 1)[..., None]

    # ---- 暖金餘暉光點：只取「比周圍明顯亮」的小面積暖色點（窗燈／街燈），避免大面積泛金 ----
    Lsm = np.asarray(Image.fromarray((np.clip(Ln, 0, 1) * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(14)), dtype=np.float64) / 255.0
    local_hi = np.clip((Ln - Lsm) / 0.07, 0, 1)
    warm_n = np.clip((warm - 0.03) / 0.14, 0, 1)
    gold_pts = warm_n * local_hi
    out = out + GOLD[None, None, :] * (0.26 * gold_pts)[..., None]

    # ---- 上下深藍漸層 ----
    t = np.clip(np.linspace(0, 1, h), 0, 1)[:, None, None]
    top = np.clip(1 - t / 0.22, 0, 1) ** 1.5 * 0.95
    bot = np.clip((t - 0.78) / 0.22, 0, 1) ** 1.5 * 0.95
    ov = np.clip(top + bot, 0, 0.97)
    out = out * (1 - ov) + NAVY_MID * ov

    # ---- 極細顆粒（防漸層 banding）----
    rng = np.random.default_rng(20261022)
    out = out * 255.0 + rng.normal(0, 1.5, out.shape)
    out = np.clip(out, 0, 255).astype(np.uint8)

    im = Image.fromarray(out)
    # 微柔化，讓影像更像「透出來的底」
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    return im


def stats(im):
    a = np.asarray(im, dtype=np.float64) / 255.0
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    h = L.shape[0]
    band1 = L[int(h * 0.20):int(h * 0.42)]
    band2 = L[int(h * 0.58):int(h * 0.84)]
    return dict(mean=float(L.mean() * 255), p95=float(np.percentile(L, 95) * 255),
                band1_p99=float(np.percentile(band1, 99) * 255),
                band2_p99=float(np.percentile(band2, 99) * 255),
                max=float(L.max() * 255))


def main():
    only = sys.argv[1:] or list(THEMES)
    for theme in only:
        cfg = THEMES[theme]
        src = os.path.join(SRC, f"bg-{theme}.png")
        if not os.path.exists(src):
            print(f"MISSING {src}")
            continue
        print(f"=== {theme} ===", flush=True)
        big = build(src, 2500, 1686, cfg["vpos"], cfg["alpha"], theme)
        p1 = os.path.join(HERE, f"line-bg-{theme}.png")
        big.save(p1, "PNG", optimize=True)
        print(f"{p1} {os.path.getsize(p1)}B {big.size} {stats(big)}", flush=True)

        web = build(src, 1920, 1080, cfg["vpos"], cfg["alpha"], theme + "-web")
        p2 = os.path.join(HERE, f"line-bg-{theme}-1920x1080.png")
        web.save(p2, "PNG", optimize=True)
        print(f"{p2} {os.path.getsize(p2)}B {web.size} {stats(web)}", flush=True)


if __name__ == "__main__":
    main()

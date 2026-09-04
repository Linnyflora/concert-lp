# -*- coding: utf-8 -*-
"""癒しBAR フライヤー: 開催場所を ZOOM にしたリメイク版を生成する。

元画像の絵柄・配色・文言はそのまま残し、日時カードの中に
「会場 / ZOOM オンライン開催」の1行を足すだけの最小改変。
「時間」「参加費」の2行は、3行が収まるよう少しだけ詰めて描き直している。

    必要なもの: Pillow, numpy, Noto Serif CJK (fonts-noto-cjk)
    使い方: リポジトリ直下で
            python3 tools/enhance_background.py   # 背景を仕上げる
            python3 tools/remake_flyer_zoom.py    # 会場行を入れる
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = os.environ.get("SRC", "iyashi-bar-bg.jpg")
DST = os.environ.get("DST", "iyashi-bar-zoom.jpg")
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

# ---- 元画像から採寸した座標 -------------------------------------------------
CARD_L, CARD_R = 452, 968      # 羊皮紙カードの内側（描き直してよい範囲）
ERASE_T, ERASE_B = 1134, 1270  # 日付の下端〜「お酒・食べ物」行の上端
CLEAN_T, CLEAN_B = 1206, 1216  # 文字の無い綺麗な羊皮紙の行（質感の見本）

BADGE_L, BADGE_W = 477, 113    # 元画像の「時間」バッジの左端と幅
VAL_L, VAL_R = 615, 947        # 値テキストを収める左右

BADGE_FILL = (49, 12, 20)
BADGE_TEXT = (240, 234, 228)
VALUE_TEXT = (26, 15, 9)

ROW_H, ROW_GAP, ROW_TOP = 34, 5, 1136
NOTE = "※お申込み後にZoom URLをお送りします"
NOTE_H, NOTE_CY = 17, 1259          # 3行の下に入れる小さめの案内
NOTE_COLOR = (58, 34, 24)
VAL_SPAN = 292                 # 値テキスト1行の目安幅（字間で調整する）
MAX_TRACK = 8

_font_cache = {}


def font(size):
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(SERIF, size, index=0)
    return _font_cache[size]


_probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def ink(s, f):
    return _probe.textbbox((0, 0), s, font=f)


def fit_height(ref, target):
    """参照文字 ref の高さが target になるフォントサイズ。"""
    lo, hi, best = 8, 96, 8
    while lo <= hi:
        mid = (lo + hi) // 2
        b = ink(ref, font(mid))
        if (b[3] - b[1]) <= target:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return best


def tracked_width(s, f, track):
    return sum(f.getlength(c) for c in s) + track * (len(s) - 1)


def draw_tracked(d, x, y, s, f, fill, track, anchor="ls"):
    for c in s:
        d.text((x, y), c, font=f, fill=fill, anchor=anchor)
        x += f.getlength(c) + track
    return x - track


def build_parchment(a):
    """消した領域を埋める羊皮紙。横の質感は綺麗な行から、縦のムラは左余白列から。"""
    prof = a[CLEAN_T:CLEAN_B, CARD_L:CARD_R].mean(axis=0)
    col = a[:, CARD_L + 4:CARD_L + 20].mean(axis=1)
    ref = col[CLEAN_T:CLEAN_B].mean(axis=0)
    fill = prof[None, :, :] + (col[ERASE_T:ERASE_B] - ref)[:, None, :]
    fill = fill + np.random.default_rng(7).normal(0, 1.6, fill.shape)
    return np.clip(fill, 0, 255)


# (バッジ文字, バッジ字間, [(値, 高さ基準文字, 目標高さ), ...])
ROWS = [
    ("時間", 5, [("20:00〜22:00", "0", 25)]),
    ("参加費", 0, [("1,000円", "0", 25), ("限定15席", "限", 21)]),
    ("会場", 5, [("ZOOM", "Z", 25), ("オンライン開催", "開", 21)]),
]


def main():
    im = Image.open(SRC).convert("RGB")
    a = np.asarray(im).astype(np.float64)
    a[ERASE_T:ERASE_B, CARD_L:CARD_R] = build_parchment(a)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    # バッジの落ち影
    shadow = Image.new("L", im.size, 0)
    sd = ImageDraw.Draw(shadow)
    for i in range(len(ROWS)):
        t = ROW_TOP + i * (ROW_H + ROW_GAP)
        sd.rounded_rectangle([BADGE_L + 1, t + 3, BADGE_L + BADGE_W + 2, t + ROW_H + 4],
                             radius=8, fill=70)
    shadow = shadow.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.45))
    im = Image.composite(Image.new("RGB", im.size, (92, 62, 42)), im, shadow)

    d = ImageDraw.Draw(im)
    for i, (label, l_track, parts) in enumerate(ROWS):
        t = ROW_TOP + i * (ROW_H + ROW_GAP)
        b = t + ROW_H
        cy = (t + b) / 2
        d.rounded_rectangle([BADGE_L, t, BADGE_L + BADGE_W, b], radius=8, fill=BADGE_FILL)

        # バッジ文字
        lf = font(fit_height(label, int(round(ROW_H * 0.57))))
        lw = tracked_width(label, lf, l_track)
        lb = ink(label, lf)
        draw_tracked(d, BADGE_L + (BADGE_W - lw) / 2, cy + (lb[3] - lb[1]) / 2 - lb[3],
                     label, lf, BADGE_TEXT, l_track, anchor="lt")

        # 値テキスト（同じベースラインに揃え、字間で行幅を整える）
        fonts = [font(fit_height(ref, h)) for _, ref, h in parts]
        nat = sum(f.getlength(s) for (s, _, _), f in zip(parts, fonts))
        gap = 16 * (len(parts) - 1)
        nchar = sum(len(s) for s, _, _ in parts) - 1
        track = max(0, min(MAX_TRACK, (VAL_SPAN - gap - nat) / nchar)) if nchar else 0

        main_h = parts[0][2]
        baseline = cy + main_h / 2
        x = VAL_L
        for (s, _, _), f in zip(parts, fonts):
            x = draw_tracked(d, x, baseline, s, f, VALUE_TEXT, track) + 16

    # 3行の下に、申し込み後の案内を小さく添える
    nf = font(fit_height("送", NOTE_H))
    nb = ink(NOTE, nf)
    d.text(((BADGE_L + VAL_R) / 2 - (nb[2] - nb[0]) / 2 - nb[0],
            NOTE_CY - (nb[3] + nb[1]) / 2), NOTE, font=nf, fill=NOTE_COLOR)

    im.save(DST, quality=95, subsampling=0)
    print("saved", DST, im.size)


if __name__ == "__main__":
    main()

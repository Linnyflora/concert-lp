# -*- coding: utf-8 -*-
"""癒しBAR フライヤーの背景を仕上げ直す。

絵の内容（人物・構図・文字）は一切動かさず、光と色だけを整える:
  1. 陰に暖色を寄せ、彩度と締まりを少し足す
  2. 明るい所からブルーム（光の滲み）を出して、提灯・夕陽・蝋燭の空気感を強める
  3. 光源のまわりに淡い玉ボケを少しだけ足す
  4. 周辺を軽く落として中央に視線を集める
文字が乗っているパネル（提供メニュー / 日時カード）にはブルームと玉ボケを
掛けず、色味だけ全体と揃える。

    必要なもの: Pillow, numpy
    使い方: リポジトリ直下で python3 tools/enhance_background.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = os.environ.get("SRC", "iyashi-bar-original.jpg")
DST = os.environ.get("DST", "iyashi-bar-bg.jpg")

# 文字が並ぶパネル（ここは元のまま残す）
PANELS = [(18, 1018, 396, 1390), (410, 1018, 996, 1390)]
PANEL_FEATHER = 6

WARM = np.array([12.0, 4.0, -4.0])   # 陰に寄せる暖色
WARM_K = 0.34
SAT = 1.06
CONTRAST = 0.05
CLARITY = (12, 26)                   # (半径, 強さ%) 眠さを取る程度のシャープ

BLOOM = [(34, 0.26), (11, 0.15)]     # (ぼかし半径, 強さ)
BLOOM_FLOOR, BLOOM_CEIL = 172.0, 246.0

VIGNETTE = 0.13
VIG_CX, VIG_CY = 0.50, 0.40

# 玉ボケ: (中心x, 中心y, 散らばり, 個数, 最大半径)
BOKEH_ZONES = [
    (95, 120, 105, 9, 13),      # 左上の提灯まわり
    (250, 300, 150, 7, 10),     # 左の木立
    (905, 700, 110, 7, 11),     # 右のキャンドル
    (640, 470, 190, 6, 9),      # 中央奥
]
BOKEH_COLOR = (255, 206, 130)


def luminance(a):
    return a @ np.array([0.299, 0.587, 0.114])


def protect_mask(size):
    """パネル部分を 0、それ以外を 1 にした（ぼかし済みの）マスク。"""
    m = Image.new("L", size, 255)
    d = ImageDraw.Draw(m)
    for box in PANELS:
        d.rounded_rectangle(box, radius=18, fill=0)
    m = m.filter(ImageFilter.GaussianBlur(PANEL_FEATHER))
    return np.asarray(m).astype(np.float64)[:, :, None] / 255.0


def bloom(a):
    out = a.copy()
    for radius, strength in BLOOM:
        lum = luminance(out)
        hi = np.clip((lum - BLOOM_FLOOR) / (BLOOM_CEIL - BLOOM_FLOOR), 0, 1)
        src = np.clip(out * hi[:, :, None], 0, 255).astype(np.uint8)
        g = np.asarray(Image.fromarray(src).filter(
            ImageFilter.GaussianBlur(radius))).astype(np.float64) * strength
        # スクリーン合成: 白飛びさせずに光だけ乗せる
        out = 255.0 - (255.0 - out) * (255.0 - np.clip(g, 0, 255)) / 255.0
    return out


def bokeh_layer(size):
    layer = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    rng = np.random.default_rng(11)
    for cx, cy, spread, n, rmax in BOKEH_ZONES:
        for _ in range(n):
            x = cx + rng.normal(0, spread)
            y = cy + rng.normal(0, spread * 0.7)
            r = rng.uniform(rmax * 0.35, rmax)
            k = rng.uniform(0.20, 0.55)
            c = tuple(int(v * k) for v in BOKEH_COLOR)
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    return np.asarray(layer.filter(ImageFilter.GaussianBlur(5))).astype(np.float64)


def vignette(shape):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    dx = (xx / w - VIG_CX) / 0.62
    dy = (yy / h - VIG_CY) / 0.72
    r = np.sqrt(dx * dx + dy * dy)
    return (1.0 - VIGNETTE * np.clip(r - 0.55, 0, None) ** 1.6)[:, :, None]


def main():
    im = Image.open(SRC).convert("RGB")
    base = np.asarray(im).astype(np.float64)

    # 0. 眠さを取る程度のシャープ（絵の描き込みを起こす）
    a = np.asarray(im.filter(ImageFilter.UnsharpMask(
        radius=CLARITY[0], percent=CLARITY[1], threshold=3))).astype(np.float64)

    # 1. 陰に暖色 / 彩度 / コントラスト
    lum = luminance(a)
    a = a + WARM[None, None, :] * ((1.0 - lum / 255.0) ** 1.4)[:, :, None] * WARM_K
    gray = luminance(a)[:, :, None]
    a = gray + (a - gray) * SAT
    a = a + (a - 128.0) * CONTRAST

    # 2-3. ブルームと玉ボケ（文字パネルには掛けない）
    lit = bloom(a)
    b = bokeh_layer(im.size)
    lit = 255.0 - (255.0 - lit) * (255.0 - b) / 255.0
    m = protect_mask(im.size)
    a = lit * m + a * (1.0 - m)

    # 4. 周辺減光
    a = a * vignette(base.shape[:2])

    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(DST, quality=95,
                                                             subsampling=0)
    print("saved", DST)


if __name__ == "__main__":
    main()

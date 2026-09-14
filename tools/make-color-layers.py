#!/usr/bin/env python3
"""クレヨン塗りの色レイヤーを assets/color/ に書き出す。

    python3 tools/make-color-layers.py

線画（assets/flyer-art.json）をいったんPNGに焼いて、その上に手で置いた色パッチを
のせる。線画は開いた形なので塗りつぶしは使えず、位置は座標で指定している。
できたPNGは build-flyer.py が線画SVGの下に敷く。
"""
import json
import pathlib
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from crayon import CrayonLayer, crayon_texture, wobble_mask

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = json.loads((ROOT / 'assets' / 'flyer-art.json').read_text())
OUT = ROOT / 'assets' / 'color'
OUT.mkdir(parents=True, exist_ok=True)
TMP = pathlib.Path(tempfile.mkdtemp(prefix='crayon-'))

SHOT = TMP / 'shot.mjs'
SHOT.write_text("""
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [,, file, out, w, h] = process.argv;
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:+w, height:+h}, deviceScaleFactor:1 });
await p.goto('file://' + file); await p.waitForTimeout(300);
await p.screenshot({ path: out });
await b.close();
""")


def render_lines(name, scale):
    """線画を黒＝線・白＝地のPNGに焼く"""
    a = ART[name]
    w, h = int(a['w'] / 4 * scale), int(a['h'] / 4 * scale)
    html = TMP / f'{name}.html'
    html.write_text(f'<html><body style="margin:0;background:#fff">'
                    f'<svg viewBox="0 0 {a["w"]} {a["h"]}" width="{w}" height="{h}">'
                    f'<path fill="#000" fill-rule="evenodd" d="{a["d"]}"/></svg></body></html>')
    png = TMP / f'{name}.png'
    subprocess.run(['node', str(SHOT), str(html), str(png), str(w), str(h)], check=True)
    return png, w, h


def closed_regions(png):
    """線で閉じている領域にラベルを振る（バッジの丸やハートなど）"""
    a = np.array(Image.open(png).convert('L'))
    free = a >= 200
    free[0, :] = free[-1, :] = False
    free[:, 0] = free[:, -1] = False
    lab, _ = ndimage.label(free)
    return lab


def ink_bbox(png, region=None):
    a = np.array(Image.open(png).convert('L'))
    ink = a < 200
    if region:
        x0, y0, x1, y1 = region
        keep = np.zeros_like(ink)
        keep[y0:y1, x0:x1] = True
        ink &= keep
    ys, xs = np.nonzero(ink)
    return None if len(xs) == 0 else (xs.min(), ys.min(), xs.max(), ys.max())


def scribble(size, bbox, color, pad=0.16, strength=0.6, angle=0.7, seed=1, shape='ellipse'):
    """形のまわりをクレヨンでざっと塗ったような パッチ"""
    W, H = size
    x0, y0, x1, y1 = bbox
    px, py = (x1 - x0) * pad + 4, (y1 - y0) * pad + 4
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    box = [x0 - px, y0 - py, x1 + px, y1 + py]
    (d.ellipse if shape == 'ellipse' else d.rectangle)(box, fill=255)
    m = np.array(m, dtype=np.float32) / 255.0
    m = wobble_mask(m, seed=seed, amp=3.0, smooth=16)
    m = ndimage.gaussian_filter(m, 4)
    tex = crayon_texture(W, H, seed=seed * 5 + 2, angle=angle)
    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    rgba[..., :3] = np.array(color, dtype=np.uint8)
    rgba[..., 3] = (np.clip(m * tex * strength, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def save(img, name):
    """色数を落としてから保存（チラシHTMLに埋め込むので軽くする）"""
    img.convert('RGBA').quantize(colors=96, method=Image.FASTOCTREE).save(
        OUT / f'{name}.png', optimize=True)
    print('  ', name)


# ---- 主役のイラスト（座標は 2110x1020 のヘッダー帯） --------------------
print('header')
lines_png, W, H = render_lines('header', scale=2)
lab = closed_regions(lines_png)
L = CrayonLayer(W, H)


SKIN   = (247, 214, 186)
HAIR   = (183, 129, 79)
DRESS  = (233, 152, 143)
WOOD   = (198, 158, 112)
PIANO  = (110, 126, 162)
PIANO2 = (139, 157, 191)
IVORY  = (253, 250, 243)
BADGE  = (247, 214, 137)
FLOOR  = (250, 241, 228)

# 客席のみんな（髪の色を少しずつ変える）
HEADS = [
    ((730, 786), (62, 66), (150, 192, 172), (226, 210, 186)),
    ((930, 786), (62, 66), (240, 206, 132), (186, 208, 226)),
    ((1150, 858), (54, 58), (183, 162, 206), (238, 208, 206)),
    ((1380, 878), (54, 58), (240, 178, 152), (206, 222, 200)),
    ((1636, 858), (54, 58), (155, 190, 220), (240, 222, 190)),
    ((1800, 852), (54, 58), (226, 160, 166), (198, 210, 232)),
    ((1970, 800), (58, 62), (205, 186, 150), (226, 206, 222)),
]

# ピアノ
L.poly([(1346, 512), (1876, 508), (1874, 636), (1350, 648)], PIANO, strength=0.82, angle=0.45)
L.poly([(1528, 258), (1648, 256), (1690, 392), (1846, 462), (1560, 496), (1524, 392)],
       PIANO2, strength=0.7, angle=0.9)
L.rect(1362, 566, 1520, 600, IVORY, strength=0.9, blur=2, amp=1.5)
for x in (1402, 1566, 1762):
    L.rect(x, 656, x + 20, 752, PIANO, strength=0.4, blur=3, amp=1.5)

# ピアノを弾く子
L.ellipse(1270, 452, 44, 48, HAIR, strength=0.85, angle=1.1)
L.ellipse(1215, 505, 26, 36, HAIR, strength=0.8, angle=1.1)
L.ellipse(1282, 468, 26, 26, SKIN, strength=0.9, blur=2.5, amp=3)
L.poly([(1232, 500), (1206, 662), (1300, 668), (1292, 545), (1276, 498)], DRESS,
       strength=0.85, angle=0.3)
L.ellipse(1350, 566, 58, 20, SKIN, strength=0.75, blur=3, amp=2.5)
L.ellipse(1312, 704, 20, 44, SKIN, strength=0.62, blur=3, amp=2)
L.rect(1162, 678, 1292, 702, WOOD, strength=0.62, blur=3, amp=1.5)

# 客席
for (cx, cy), (rx, ry), col, wear in HEADS:
    L.ellipse(cx, cy, rx, ry, col, strength=0.82, angle=0.8)
    L.ellipse(cx, cy + ry + 60, rx + 24, 58, wear, strength=0.6, blur=4, amp=3, angle=0.35)

# 入場無料のバッジ、ハート、音符
L.mask(lab == 4, BADGE, strength=0.62, blur=3, amp=2, angle=1.2)
L.mask(lab == 38, (226, 122, 122), strength=0.9, blur=2, amp=1.5)
L.ellipse(1382, 412, 26, 24, (222, 168, 96), strength=0.8, blur=2.5, amp=2)
L.ellipse(400, 120, 34, 66, (200, 178, 214), strength=0.55, blur=3, amp=3)
L.ellipse(496, 112, 26, 24, (222, 168, 96), strength=0.75, blur=2.5, amp=2)


save(L.image(), 'header')

# ---- 小さな飾り ---------------------------------------------------------
NOTE_ONLY = {'note_l': (200, 165, 315, 322), 'note_r': (195, 314, 312, 478),
             'divider': (256, 88, 347, 216)}
PIECES = {
    'note_l':     ((228, 176, 104), 'ellipse', 0.7),
    'note_r':     ((228, 176, 104), 'ellipse', 0.7),
    'divider':    ((228, 176, 104), 'ellipse', 0.7),
    'leaf_l':     ((150, 182, 138), 'ellipse', 0.7),
    'leaf_r':     ((150, 182, 138), 'ellipse', 0.7),
    'icon_keys':  ((150, 164, 196), 'rect', 0.55),
    'icon_clock': ((152, 188, 216), 'ellipse', 0.6),
    'icon_door':  ((162, 194, 160), 'rect', 0.55),
}
print('ornaments')
for i, (name, (col, shape, st)) in enumerate(PIECES.items()):
    png, w, h = render_lines(name, scale=4)
    bb = ink_bbox(png, NOTE_ONLY.get(name))
    save(scribble((w, h), bb, col, strength=st, shape=shape, seed=i * 3 + 2), name)

# ---- 足もとの帯（花はピンク、葉は緑） -----------------------------------
print('bottom')
png, w, h = render_lines('bottom', scale=2)
sx = w / 1055.0


def R(x0, y0, x1, y1):
    return (int(x0 * sx), int((y0 - 1322) * sx), int(x1 * sx), int((y1 - 1322) * sx))


band = Image.new('RGBA', (w, h), (0, 0, 0, 0))
for k, (reg, col, st) in enumerate([
        (R(30, 1330, 200, 1415), (150, 182, 138), 0.5),
        (R(890, 1340, 1055, 1415), (150, 182, 138), 0.5),
        (R(74, 1326, 122, 1364), (233, 150, 160), 0.75),
        (R(946, 1330, 1004, 1372), (233, 150, 160), 0.75)]):
    bb = ink_bbox(png, reg)
    if bb:
        band = Image.alpha_composite(band, scribble((w, h), bb, col, strength=st, seed=k + 20))
save(band, 'bottom')
print('done ->', OUT)

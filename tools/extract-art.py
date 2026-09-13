"""Vectorise the line art of the original flyer image.

The only source we have for the flyer artwork is a ~90dpi raster, which is too
coarse for print, so every piece is upscaled and traced into paths with potrace.
Text is blanked out of the traced pieces and re-set as live text in flyer.html.
"""
import json
import pathlib

from PIL import Image, ImageDraw
from trace import trace_img

SRC = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'flyer-source.png'
PAPER = 250  # background level of the source image

def rect(l, t, r, b):   return ('rect', l, t, r, b)
def circle(cx, cy, r):  return ('circle', cx, cy, r)

PIECES = {
    # --- flyer bands -----------------------------------------------------
    'header':     ((0, 0, 1055, 510), [rect(40, 125, 600, 335)], 4),
    'bottom':     ((0, 1322, 1055, 1415), [rect(175, 1362, 890, 1415)], 4),
    'note_l':     ((70, 530, 210, 690), [], 4),
    'note_r':     ((870, 530, 1000, 690), [], 4),
    'divider':    ((450, 810, 610, 880), [], 4),
    'leaf_l':     ((280, 1180, 360, 1250), [], 4),
    'leaf_r':     ((690, 1180, 780, 1250), [], 4),
    'icon_keys':  ((198, 1000, 262, 1050), [], 4),
    'icon_clock': ((498, 1000, 552, 1050), [], 4),
    'icon_door':  ((818, 1000, 868, 1050), [], 4),
    # --- receipt pieces --------------------------------------------------
    # the piano scene alone: the "入場無料" badge and the neighbouring
    # audience heads are painted out so only the performer remains.
    'piano':      ((565, 95, 1000, 388),
                   [circle(945, 145, 62),      # the "入場無料" badge
                    rect(565, 95, 585, 388),   # a stray glyph from the title
                    rect(878, 95, 1000, 168),  # the badge's sparkle strokes
                    rect(940, 330, 1000, 388), # the listener on the right
                    rect(565, 381, 1000, 388)],# the tops of the front row
                   60),
    # the listeners with the sweeping baseline, for the receipt footer
    'listeners':  ((40, 352, 540, 500), [], 20),
}

src = Image.open(SRC).convert('L')
out = {}
for name, (box, blanks, turd) in PIECES.items():
    img = src.crop(box).copy()
    d = ImageDraw.Draw(img)
    for blank in blanks:
        if blank[0] == 'rect':
            _, l, t, r, b = blank
            d.rectangle([l - box[0], t - box[1], r - box[0], b - box[1]], fill=PAPER)
        else:
            _, cx, cy, r = blank
            d.ellipse([cx - r - box[0], cy - r - box[1],
                       cx + r - box[0], cy + r - box[1]], fill=PAPER)
    vw, vh, path = trace_img(img, turd=turd)
    out[name] = {'w': vw, 'h': vh, 'd': path}
    print(f'{name:11s} {box[2]-box[0]:>5}x{box[3]-box[1]:<4} path {len(path):>7} chars')

out_path = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'flyer-art.json'
json.dump(out, open(out_path, 'w'))
print('wrote', out_path)

#!/usr/bin/env python3
"""Assemble flyer.html from the template, the traced line art and the access map.

    python3 tools/extract-art.py      # (re)creates assets/flyer-art.json
    python3 tools/build-flyer.py      # writes flyer.html

Everything is inlined so the flyer is a single file that prints straight from the
browser (A4, no margins, "background graphics" on).
"""
import base64
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = json.loads((ROOT / 'assets' / 'flyer-art.json').read_text())

# クレヨン塗りを使うかどうか。False なら元の線画だけのチラシになる。
# 色の層は assets/color に残してあるので、True にすればいつでも戻せる。
CRAYON = False


def font_faces():
    """丸ゴシック（必要な字だけに絞ったもの）をHTMLに埋め込む。
    ネット接続に頼らないので、どの環境で開いても中国語フォントに化けない。"""
    css = []
    for name, weight in (('Light', 300), ('Regular', 400), ('Medium', 500)):
        p = ROOT / 'assets' / 'fonts' / 'subset' / f'ZenMaruGothic-{name}.woff2'
        b64 = base64.b64encode(p.read_bytes()).decode()
        css.append(
            '@font-face{font-family:"Zen Maru Gothic";font-style:normal;'
            f'font-weight:{weight};font-display:block;'
            f'src:url(data:font/woff2;base64,{b64}) format("woff2");}}')
    return '<style>\n' + '\n'.join(css) + '\n</style>'


def color_layer(name):
    """クレヨンで塗った色の層（線画の下に敷く）。tools/crayon で作成。"""
    p = ROOT / 'assets' / 'color' / f'{name}.png'
    if not CRAYON or not p.exists():
        return ''
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f'<img class="art-color" alt="" src="data:image/png;base64,{b64}">'


def art(name, extra=''):
    """One traced piece of the original artwork: crayon colour + inline <svg> lines."""
    a = ART[name]
    svg = (f'<svg class="art" viewBox="0 0 {a["w"]} {a["h"]}"{extra} '
           f'preserveAspectRatio="xMidYMid meet">'
           f'<path fill="currentColor" fill-rule="evenodd" d="{a["d"]}"/></svg>')
    return f'<span class="art-stack">{color_layer(name)}{svg}</span>' 


def svg_file(name):
    return (ROOT / 'tools' / name).read_text().split('?>')[-1].strip()


html = (ROOT / 'tools' / 'flyer.template.html').read_text()
html = html.replace('{{fonts}}', font_faces())
for key in ('header', 'bottom', 'note_l', 'note_r', 'divider',
            'leaf_l', 'leaf_r', 'icon_keys', 'icon_clock', 'icon_door'):
    html = html.replace('{{%s}}' % key, art(key))
html = html.replace('{{map}}', svg_file('access-map.svg'))
html = html.replace('{{qr}}', svg_file('maps-qr.svg'))

out = ROOT / 'flyer.html'
out.write_text(html)
print(f'wrote {out} ({len(html) / 1024:.0f} KB)')

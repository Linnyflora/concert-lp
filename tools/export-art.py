#!/usr/bin/env python3
"""チラシのイラストを1点ずつ書き出す（記念品を作るとき用）。

    python3 tools/export-art.py

assets/flyer-art.json のパスを読んで、assets/art/ に
  ・<名前>.svg          拡大しても荒れない線画。入稿はこちらが安心
  ・<名前>.png          背景が透明。高さ 2000px くらいの大きさ
を書き出します。色は墨色（#2f2b28）。白地でも生成りの紙でもなじみます。
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = json.loads((ROOT / 'assets' / 'flyer-art.json').read_text())
OUT = ROOT / 'assets' / 'art'

INK = '#2f2b28'
PNG_LONG_EDGE = 2000  # 書き出すPNGの長辺(px)

# 記念品にしやすい名前にしておきます。
LABEL = {
    'header': '01_見出し帯（波線・ト音記号・ピアノ・客席）',
    'piano': '02_ピアノをひく女の子',
    'listeners': '03_客席のみなさん',
    'bottom': '04_下の波線とお花',
    'note_l': '05_音符（左）',
    'note_r': '06_音符（右）',
    'divider': '07_仕切りの音符',
    'leaf_l': '08_葉っぱ（左）',
    'leaf_r': '09_葉っぱ（右）',
    'icon_keys': '10_鍵盤のアイコン',
    'icon_clock': '11_時計のアイコン',
    'icon_door': '12_扉のアイコン',
    'stage': '13_コンサートの風景（ピアノと客席）',
    'clef': '14_ト音記号と音符',
    'heart': '15_ハート',
    'flower_l': '16_お花（左）',
    'flower_r': '17_お花（右）',
}


def svg(piece, ink=INK):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {piece["w"]} {piece["h"]}" '
            f'width="{piece["w"]}" height="{piece["h"]}">'
            f'<path fill="{ink}" fill-rule="evenodd" d="{piece["d"]}"/></svg>\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        import cairosvg
    except ImportError:
        cairosvg = None
        print('cairosvg が無いので SVG だけ書き出します', file=sys.stderr)

    for name, piece in ART.items():
        stem = LABEL.get(name, name)
        path = OUT / f'{stem}.svg'
        path.write_text(svg(piece))
        line = f'{path.name}'
        if cairosvg:
            scale = PNG_LONG_EDGE / max(piece['w'], piece['h'])
            png = OUT / f'{stem}.png'
            cairosvg.svg2png(bytestring=path.read_bytes(), write_to=str(png),
                             scale=scale, background_color=None)
            line += f'  +  {png.name}  ({round(piece["w"]*scale)}x{round(piece["h"]*scale)})'
        print(line)


if __name__ == '__main__':
    main()

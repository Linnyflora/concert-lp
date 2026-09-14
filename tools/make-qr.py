#!/usr/bin/env python3
"""会場の地図を開くQRコード（tools/maps-qr.svg）を作る。

    python3 tools/make-qr.py

1マスを <rect> ひとつで描き、余白（クワイエットゾーン）は
チラシ側の余白で確保する。線（stroke）は付けない ―― 細い線が
入るとマスが痩せて読み取れなくなるため。
"""
import pathlib
import qrcode

URL = ('https://www.google.com/maps/search/?api=1&query='
       '%E5%90%8D%E5%8F%A4%E5%B1%8B%E5%B8%82%E9%9F%B3%E6%A5%BD%E3%83%97%E3%83%A9%E3%82%B6')

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
qr.add_data(URL)
qr.make(fit=True)
m = qr.get_matrix()
n = len(m)

rects = ''.join(f'<rect x="{x}" y="{y}" width="1" height="1"/>'
                for y, row in enumerate(m) for x, v in enumerate(row) if v)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" id="mapsqr" viewBox="0 0 {n} {n}" '
       f'role="img" aria-label="Googleマップで会場を開くQRコード" '
       f'style="stroke:none">'
       f'<rect width="{n}" height="{n}" fill="#ffffff"/>'
       f'<g fill="#2f2b28" stroke="none">{rects}</g></svg>\n')

out = pathlib.Path(__file__).resolve().parent / 'maps-qr.svg'
out.write_text(svg)
print(f'version {qr.version} / {n} modules / {len(svg)} bytes -> {out}')

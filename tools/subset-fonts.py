#!/usr/bin/env python3
"""チラシで実際に使う文字だけに絞った丸ゴシックをつくる。

    python3 tools/subset-fonts.py

Webフォントをネットから読むと、読み込みに失敗したときに中国語フォントへ
置き換わってしまう（PDFにWenQuanYiが埋まっていた）。そこで必要な字だけを
切り出したWOFF2をHTMLに埋め込み、どこで開いても同じ丸ゴシックで出るようにする。
"""
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'assets' / 'fonts'
OUT = SRC / 'subset'
OUT.mkdir(exist_ok=True)

WEIGHTS = {'Light': 300, 'Regular': 400, 'Medium': 500}

# チラシに出てくる文字を集める（テンプレートと地図から）
text = ''
for f in [ROOT / 'tools' / 'flyer.template.html', ROOT / 'tools' / 'access-map.svg']:
    s = f.read_text()
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S)
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    text += s

chars = set(text)
# 記号と英数字は一式入れておく（差し替えても崩れないように）
chars |= set(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
chars |= set('　、。，．・：；？！ー〜～（）「」『』【】〔〕♪♬♫※→←↑↓©℡〒±×÷')
chars |= set('０１２３４５６７８９')
chars -= set('\n\r\t')

spec = ','.join(f'U+{ord(c):04X}' for c in sorted(chars))
print(f'{len(chars)} characters')

for name, weight in WEIGHTS.items():
    src = SRC / f'ZenMaruGothic-{name}.ttf'
    dst = OUT / f'ZenMaruGothic-{name}.woff2'
    subprocess.run([
        'python3', '-m', 'fontTools.subset', str(src),
        f'--unicodes={spec}',
        '--layout-features=kern,liga,palt,vert,vrt2',
        '--flavor=woff2',
        '--desubroutinize',
        f'--output-file={dst}',
    ], check=True)
    print(f'  {dst.name}  {dst.stat().st_size / 1024:.0f} KB  (weight {weight})')

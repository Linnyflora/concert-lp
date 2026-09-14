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
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'assets' / 'fonts'
OUT = SRC / 'subset'
OUT.mkdir(exist_ok=True)

WEIGHTS = {'Light': 300, 'Regular': 400, 'Medium': 500, 'Bold': 700}

# 元のフォントはリポジトリに置かず、必要なときに取ってくる（OFL）
SOURCES = {
    'ZenMaruGothic-Light.ttf':
        'https://raw.githubusercontent.com/google/fonts/main/ofl/zenmarugothic/ZenMaruGothic-Light.ttf',
    'ZenMaruGothic-Regular.ttf':
        'https://raw.githubusercontent.com/google/fonts/main/ofl/zenmarugothic/ZenMaruGothic-Regular.ttf',
    'ZenMaruGothic-Medium.ttf':
        'https://raw.githubusercontent.com/google/fonts/main/ofl/zenmarugothic/ZenMaruGothic-Medium.ttf',
    'ZenMaruGothic-Bold.ttf':
        'https://raw.githubusercontent.com/google/fonts/main/ofl/zenmarugothic/ZenMaruGothic-Bold.ttf',
    'NotoSansJP[wght].ttf':
        'https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf',
}


def source(name):
    """元フォントを用意する（なければダウンロード）"""
    p = SRC / name
    if not p.exists():
        print(f'  downloading {name}')
        SRC.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(SOURCES[name], p)
    return p

# 使う文字を集める（チラシ・地図・領収書サンプル・インスタ用）
STORY_TEXT = (
    'はじめての主催コンサート生徒さんの発表場所を自分でつくります'
    '人集まりましたあと2ヶ月準備がんばります'
    '名古屋市音楽プラザ1階音楽サロン'
)
text = STORY_TEXT
for f in [ROOT / 'tools' / 'flyer.template.html', ROOT / 'tools' / 'access-map.svg',
          ROOT / 'tools' / 'receipt-preview.html']:
    s = f.read_text()
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.S)
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    text += s

chars = set(text)
# 記号と英数字は一式入れておく（差し替えても崩れないように）
chars |= set(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
chars |= set('　、。，．・：；？！ー〜～（）「」『』【】〔〕♪♬♫※→←↑↓©℡〒±×÷｜│—–…‥')
chars |= set('０１２３４５６７８９')
chars -= set('\n\r\t')

spec = ','.join(f'U+{ord(c):04X}' for c in sorted(chars))
print(f'{len(chars)} characters')

def subset(src, dst):
    subprocess.run([
        'python3', '-m', 'fontTools.subset', str(src),
        f'--unicodes={spec}',
        '--layout-features=kern,liga,palt,vert,vrt2',
        '--flavor=woff2',
        '--desubroutinize',
        f'--output-file={dst}',
    ], check=True)
    print(f'  {dst.name}  {dst.stat().st_size / 1024:.0f} KB')


for name in WEIGHTS:
    subset(source(f'ZenMaruGothic-{name}.ttf'), OUT / f'ZenMaruGothic-{name}.woff2')

# 領収書のサンプルはGoogleドキュメントの見え方に近い角ゴシックで
subset(source('NotoSansJP[wght].ttf'), OUT / 'NotoSansJP.woff2')

# 埋め込み用のCSS（HTMLから相対パスで読める形でも置いておく）
import base64
css = []
for name, weight in WEIGHTS.items():
    b64 = base64.b64encode((OUT / f'ZenMaruGothic-{name}.woff2').read_bytes()).decode()
    css.append('@font-face{font-family:"Zen Maru Gothic";font-style:normal;'
               f'font-weight:{weight};font-display:block;'
               f'src:url(data:font/woff2;base64,{b64}) format("woff2");}}')
b64 = base64.b64encode((OUT / 'NotoSansJP.woff2').read_bytes()).decode()
css.append('@font-face{font-family:"Noto Sans JP";font-style:normal;'
           'font-weight:100 900;font-display:block;'
           f'src:url(data:font/woff2;base64,{b64}) format("woff2");}}')
(OUT / 'fonts.css').write_text('\n'.join(css))
print('  fonts.css', f"{(OUT / 'fonts.css').stat().st_size / 1024:.0f} KB")

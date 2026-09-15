#!/usr/bin/env python3
"""apps-script/receipt-images.gs を assets の画像から作り直す。

    python3 tools/build-receipt-images.py

領収書のヘッダー・フッターのイラストと、発行者の印鑑を base64 にして
Apps Script に貼れる形（1行96文字の配列）で書き出す。
"""
import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIDTH = 96

IMAGES = [
    ('RECEIPT_HEADER_IMAGE', 'receipt-header.png'),
    ('RECEIPT_FOOTER_IMAGE', 'receipt-footer.png'),
    ('RECEIPT_SEAL_IMAGE', 'seal.png'),
]

out = ['// 領収書に入れる画像データ（PNG）です。',
       '// チラシの線画から起こしたイラストと、発行者の印鑑。編集しないでください。',
       '// tools/build-receipt-images.py で生成しています。',
       '']

for name, filename in IMAGES:
    b64 = base64.b64encode((ROOT / 'assets' / filename).read_bytes()).decode()
    chunks = [b64[i:i + WIDTH] for i in range(0, len(b64), WIDTH)]
    out.append(f'var {name} = [')
    out.append(',\n'.join(f"'{c}'" for c in chunks))
    out.append("].join('');")
    out.append('')

path = ROOT / 'apps-script' / 'receipt-images.gs'
path.write_text('\n'.join(out))
kb = path.stat().st_size / 1024
print(f'wrote {path} ({kb:.0f} KB)')

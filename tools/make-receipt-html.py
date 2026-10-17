#!/usr/bin/env python3
"""領収書1枚ぶんのHTMLを作る（Googleドキュメントに変換して使う）。

    python3 tools/make-receipt-html.py '住田　様' '2026年11月15日' out.html

receipt-sample.pdf と同じ様式。既定では画像を data URI で埋めこむので
1ファイルで完結する。

--remote をつけると画像を GitHub の raw URL で参照する。data URI だと
HTMLが9KBほどになり、ドライブに渡すときに取りちがえが起きやすいので、
ドライブにアップロードするときはこちらを使う（3.4KBで済む）。
"""
import base64
import pathlib
import sys

IMG = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'docx'

# コミットを固定した raw URL（ブランチが動いても画像は変わらない）。
RAW = ('https://raw.githubusercontent.com/Linnyflora/concert-lp/'
       '2ddce12e7c51a1f89d76e4a91f8799ed34d218f9/assets/docx')

REMOTE = '--remote' in sys.argv


def img_src(name):
    if REMOTE:
        return f'{RAW}/{name}.png'
    b64 = base64.b64encode((IMG / f'{name}.png').read_bytes()).decode()
    return f'data:image/png;base64,{b64}'


def build(to_name, issue_date):
    cell = 'border:1px solid #d4d1cc;padding:5pt 7pt;'
    th = cell + 'background:#eeedfc;font-weight:bold;text-align:center;'
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>領収書</title></head>
<body style="font-family:sans-serif;color:#202124;">
<p style="text-align:center;margin:0;"><img src="{img_src('receipt-header')}" width="150"></p>
<p style="text-align:center;font-size:17pt;font-weight:bold;color:#3b3f5c;margin:2pt 0 0;">♪　領　収　書　♪</p>
<hr>
<p style="text-align:right;font-size:10pt;color:#5f6368;margin:0 0 10pt;">発行日：{issue_date}</p>
<p style="font-size:16pt;font-weight:bold;margin:0;">{to_name}</p>
<p style="color:#999999;margin:1pt 0 9pt;">────────────────────</p>
<p style="font-size:10.5pt;margin:0 0 9pt;">件名：1曲ひいてみよう やってみようコンサート　参加費として</p>
<p style="font-size:16pt;font-weight:bold;margin:0 0 2pt;">合計金額　　¥8,800-（税込）</p>
<p style="font-size:10pt;margin:0 0 10pt;">上記の金額を正に領収いたしました。</p>
<table style="border-collapse:collapse;width:100%;font-size:10pt;margin-bottom:9pt;">
<tr><td style="{th}">品目</td><td style="{th}width:14%">数量</td><td style="{th}width:18%">単価</td><td style="{th}width:18%">金額</td></tr>
<tr><td style="{cell}">参加費<br>（1曲ひいてみよう&nbsp;やってみようコンサート）</td>
<td style="{cell}text-align:center;">1</td><td style="{cell}text-align:right;">¥8,000</td>
<td style="{cell}text-align:right;">¥8,000</td></tr>
</table>
<table align="right" style="border-collapse:collapse;width:46%;font-size:10pt;margin-bottom:12pt;">
<tr><td style="{cell}">小計</td><td style="{cell}text-align:right;">¥8,000</td></tr>
<tr><td style="{cell}">消費税（10%）</td><td style="{cell}text-align:right;">¥800</td></tr>
<tr><td style="{cell}">合計</td><td style="{cell}text-align:right;">¥8,800</td></tr>
</table>
<p style="font-size:10pt;font-weight:bold;margin:0 0 2pt;">発行者</p>
<p style="font-size:10pt;margin:0;">増見麻美　<img src="{img_src('seal')}" width="46"></p>
<p style="font-size:10pt;margin:0;">〒456-0062　愛知県名古屋市熱田区大宝４−１５−２１</p>
<p style="font-size:10pt;margin:0;">登録番号：T2810958830122</p>
<p style="text-align:center;font-size:9.5pt;color:#5f6368;margin:10pt 0 0;">ご参加いただき、ありがとうございます。</p>
<p style="text-align:center;margin:2pt 0 0;"><img src="{img_src('receipt-footer')}" width="230"></p>
</body></html>'''


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--remote']
    to_name, issue_date, out = args[0], args[1], args[2]
    pathlib.Path(out).write_text(build(to_name, issue_date))
    print(f'{out}  {pathlib.Path(out).stat().st_size/1024:.1f} KB')

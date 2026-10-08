#!/usr/bin/env python3
"""領収書1枚ぶんのHTMLを作る（Googleドキュメントに変換して使う）。

    python3 tools/make-receipt-html.py '住田未来　様' '2026年11月15日' out.html

receipt-sample.pdf と同じ様式。画像は data URI で埋め込むので、
Google ドライブにアップロードするとそのままドキュメントになる。
"""
import base64
import pathlib
import sys

IMG = pathlib.Path('/tmp/claude-0/-home-user-concert-lp/8c0e6533-1602-59e4-94ae-60f4b5a6141f/scratchpad/docimg')


def data_uri(name):
    b64 = base64.b64encode((IMG / f'{name}.png').read_bytes()).decode()
    return f'data:image/png;base64,{b64}'


def build(to_name, issue_date):
    cell = 'border:1px solid #d4d1cc;padding:5pt 7pt;'
    th = cell + 'background:#eeedfc;font-weight:bold;text-align:center;'
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>領収書</title></head>
<body style="font-family:sans-serif;color:#202124;">
<p style="text-align:center;margin:0;"><img src="{data_uri('receipt-header')}" width="180"></p>
<p style="text-align:center;font-size:18pt;font-weight:bold;color:#3b3f5c;margin:4pt 0 2pt;">♪　領　収　書　♪</p>
<hr>
<p style="text-align:right;font-size:10pt;color:#5f6368;margin:0 0 18pt;">発行日：{issue_date}</p>
<p style="font-size:16pt;font-weight:bold;margin:0;">{to_name}</p>
<p style="color:#999999;margin:2pt 0 16pt;">────────────────────</p>
<p style="font-size:10.5pt;margin:0 0 14pt;">件名：1曲ひいてみよう やってみようコンサート　参加費として</p>
<p style="font-size:17pt;font-weight:bold;margin:0 0 4pt;">合計金額　　¥8,800-（税込）</p>
<p style="font-size:10pt;margin:0 0 18pt;">上記の金額を正に領収いたしました。</p>
<table style="border-collapse:collapse;width:100%;font-size:10pt;margin-bottom:14pt;">
<tr><td style="{th}">品目</td><td style="{th}width:14%">数量</td><td style="{th}width:18%">単価</td><td style="{th}width:18%">金額</td></tr>
<tr><td style="{cell}">参加費（1曲ひいてみよう やってみようコンサート）</td>
<td style="{cell}text-align:center;">1</td><td style="{cell}text-align:right;">¥8,000</td>
<td style="{cell}text-align:right;">¥8,000</td></tr>
</table>
<table style="border-collapse:collapse;width:46%;margin-left:auto;font-size:10pt;margin-bottom:20pt;">
<tr><td style="{cell}">小計</td><td style="{cell}text-align:right;">¥8,000</td></tr>
<tr><td style="{cell}">消費税（10%）</td><td style="{cell}text-align:right;">¥800</td></tr>
<tr><td style="{cell}">合計</td><td style="{cell}text-align:right;">¥8,800</td></tr>
</table>
<p style="font-size:10pt;font-weight:bold;margin:0 0 2pt;">発行者</p>
<p style="font-size:10pt;margin:0;">増見麻美　<img src="{data_uri('seal')}" width="46"></p>
<p style="font-size:10pt;margin:0;">〒456-0062　愛知県名古屋市熱田区大宝４−１５−２１</p>
<p style="font-size:10pt;margin:0;">登録番号：T2810958830122</p>
<p style="text-align:center;font-size:9.5pt;color:#5f6368;margin:18pt 0 0;">ご参加いただき、ありがとうございます。</p>
<p style="text-align:center;margin:6pt 0 0;"><img src="{data_uri('receipt-footer')}" width="300"></p>
</body></html>'''


if __name__ == '__main__':
    to_name, issue_date, out = sys.argv[1], sys.argv[2], sys.argv[3]
    pathlib.Path(out).write_text(build(to_name, issue_date))
    print(f'{out}  {pathlib.Path(out).stat().st_size/1024:.1f} KB')

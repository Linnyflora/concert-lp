#!/usr/bin/env python3
"""領収書をまとめて1つのHTMLにする（印刷してお渡しする用）。

    python3 tools/make-receipt-sheet.py out.html

1人1ページ。Googleドライブにアップロードするとドキュメントになるので、
受付の方にはそれを印刷してもらえば全員ぶんそろう。

宛名と出演者名は PEOPLE に並べた順に出る。住田さん・長尾さんは
ご本人にお渡しするぶんなので、ここには入れない。
"""
import pathlib
import sys

RAW = ('https://raw.githubusercontent.com/Linnyflora/concert-lp/'
       '2ddce12e7c51a1f89d76e4a91f8799ed34d218f9/assets/docx')
ISSUE_DATE = '2026年11月15日'

# (宛名, 出演者)
PEOPLE = [
    ('小島　様', '小島　愛弥'),
    ('上様', '鬼頭享花'),
    ('後藤　様', '後藤　優衣'),
    ('後藤　様', '後藤　優奈'),
    ('髙木　様', '髙木　響'),
    ('山口　様', '山口　佳穂'),
    ('横江　様', '横江　匡哉'),
    ('澤村　様', '澤村　凜花'),
    ('澤村　様', '澤村　杏奈'),
    ('村田　様', '村田　凪'),
    ('小林　様', '小林　愛弓'),
    ('田中　様', '田中　里歩'),
]

HEAD = '''<!doctype html><html><head><meta charset="utf-8"><title>領収書（まとめて印刷用）</title>
<style>
body{font-family:sans-serif;color:#202124}
p{margin:0}
.c{text-align:center}
.r{text-align:right;font-size:10pt;color:#5f6368;margin:0 0 10pt}
.ttl{text-align:center;font-size:17pt;font-weight:bold;color:#3b3f5c;margin:2pt 0 0}
.to{font-size:16pt;font-weight:bold}
.ln{color:#999999;margin:1pt 0 9pt}
.sub{font-size:10.5pt;margin:0 0 9pt}
.amt{font-size:16pt;font-weight:bold;margin:0 0 2pt}
.s{font-size:10pt}
.note{font-size:10pt;margin:0 0 10pt}
table{border-collapse:collapse;font-size:10pt}
td{border:1px solid #d4d1cc;padding:5pt 7pt}
th{border:1px solid #d4d1cc;padding:5pt 7pt;background:#eeedfc;font-weight:bold;text-align:center}
.items{width:100%;margin-bottom:9pt}
.sum{width:215pt;margin-left:253pt;margin-bottom:12pt}
.thanks{text-align:center;font-size:9.5pt;color:#5f6368;margin:10pt 0 0}
</style></head><body>
'''


def one(to_name, performer, first):
    brk = '' if first else '<hr style="page-break-before:always">\n'
    return f'''{brk}<p class="c"><img src="{RAW}/receipt-header.png" width="150"></p>
<p class="ttl">♪　領　収　書　♪</p>
<hr>
<p class="r">発行日：{ISSUE_DATE}</p>
<p class="to">{to_name}</p>
<p class="ln">────────────────────</p>
<p class="sub">件名：1曲ひいてみよう やってみようコンサート　{performer}さん　参加費として</p>
<p class="amt">合計金額　　¥8,800-（税込）</p>
<p class="note">上記の金額を正に領収いたしました。</p>
<table class="items"><tr><th>品目</th><th style="width:14%">数量</th><th style="width:18%">単価</th><th style="width:18%">金額</th></tr>
<tr><td>参加費<br>（1曲ひいてみよう&nbsp;やってみようコンサート）</td><td style="text-align:center">1</td><td style="text-align:right">¥8,000</td><td style="text-align:right">¥8,000</td></tr></table>
<table class="sum"><tr><td>小計</td><td style="text-align:right">¥8,000</td></tr><tr><td>消費税（10%）</td><td style="text-align:right">¥800</td></tr><tr><td>合計</td><td style="text-align:right">¥8,800</td></tr></table>
<p class="s" style="font-weight:bold;margin:0 0 2pt">発行者</p>
<p class="s">増見麻美　<img src="{RAW}/seal.png" width="46"></p>
<p class="s">〒456-0062　愛知県名古屋市熱田区大宝４−１５−２１</p>
<p class="s">登録番号：T2810958830122</p>
<p class="thanks">ご参加いただき、ありがとうございます。</p>
<p class="c" style="margin:2pt 0 0"><img src="{RAW}/receipt-footer.png" width="230"></p>
'''


def build(people=PEOPLE):
    body = ''.join(one(t, p, i == 0) for i, (t, p) in enumerate(people))
    return HEAD + body + '</body></html>'


if __name__ == '__main__':
    out = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else len(PEOPLE)
    pathlib.Path(out).write_text(build(PEOPLE[:n]))
    print(f'{out}  {n}名  {pathlib.Path(out).stat().st_size/1024:.1f} KB')

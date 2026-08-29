# 1曲ひいてみよう やってみようコンサート

## このリポジトリ
- `index.html` … コンサートのランディングページ（`photo.jpg` を使用、`robots.txt` + noindex で検索避け中）
- 申し込みは Google フォームへのリンク
  `https://docs.google.com/forms/d/e/1FAIpQLSd2qwZmi6aLJR2vvkH9Ncg_iVP7yDOK7WahsETwhCLFYlxbVg/viewform`

## イベント概要（index.html の構造化データより）
- 日時: 2026年11月15日(日) 10:00–11:00
- 会場: 名古屋音楽プラザ 1階 音楽サロン（名古屋市中区金山一丁目9番18号）
- 参加費: 8,800円（税込）／ 定員 10名（先着）
- 主催: 増見麻美（アイズミュージックアカデミー）
- 演奏はひとり5分以内、曲は自由

## 運用フロー
1. 申込者は**紙**の申込書を提出
2. 主催者が自分で Google フォームに代理入力
3. 回答スプレッドシートに申込者一覧が溜まる
4. Apps Script が領収書（Google ドキュメント）を自動生成

## Google ドライブ側の構成（ID は確認済み）
| もの | ID / 名前 |
|---|---|
| 本番フォーム | `1r1k6c505SjfCFPQoAkrNTBeTsasyPXnXvxaT0jtlhK4` |
| 使っていない重複フォーム | `19BcEQ1rUieVCk1QqX3ymuFwBfmIKfAQtltCK23XveXw`（同名。触らないこと） |
| 回答スプレッドシート | `1eLPlTjNVmb2misodki-8bJZIhWHcs9ixqiLmlzcMQy4` |
| Apps Script | `1np5jsBX5lHr4a0M65wcEQ_nN2-JjWuBj0k8FJRrYJ46pvBjSSugE72ZY`<br>「領収書自動生成_1曲ひいてみようコンサート」 |
| 領収書の保存先フォルダ | 「領収書_1曲ひいてみようコンサート」 |
| 領収書ひな形（現在スクリプトからは未使用） | 「領収書ひな形_1曲ひいてみようコンサート」 |

2026-08-29 に、中身が空だった Apps Script 3件をゴミ箱へ移動し、スクリプトを1つに整理済み。

## Apps Script の関数
スクリプト冒頭の定数: `FORM_ID` / `SPREADSHEET_ID` / `EVENT_DATE`(=`2026年11月15日`) / `FOLDER_NAME`

| 関数 | 実行のきっかけ | 動き |
|---|---|---|
| `onFormSubmit` | フォーム送信時（自動） | **コンサート当日日付版**の領収書を作り、行に URL と発行日を書く |
| `generateReceiptsWithTodayDate` | 手動実行 | シートを走査し、**まだ作っていない行だけ****作成日版**を作る |
| `regenerateAllRecceiptsFixedLayout` | 手動実行 | 全員分を両方の日付版で作り直す（古いファイルはゴミ箱へ） |
| `setupTrigger` | 手動実行 | onFormSubmit トリガーを貼り直す |

→ **スプレッドシートへの直接手入力でも領収書は作れる**（`generateReceiptsWithTodayDate` を手動実行）。
　ただし作られるのは作成日版だけ。当日日付版も要るならフォーム経由が確実。
　手入力する場合は必ず最終行の下に追加し、行の挿入や並べ替えはしないこと。

## 確認済みの注意点
- 回答シートの「メールアドレス」列は**タイムスタンプの直後ではなく質問項目の途中**にある
  → Google フォームの「メールアドレスを収集する」はオフ、つまり**回答のコピーを申込者へ自動送信していない**
  （代理入力なので、自動返信はオフのままが安全。オンにすると入力のたびに申込者へメールが飛ぶ）

## 並行して進めている作業
- 長音階（長調）/ 短音階（短調）のリールを制作済み
- 続きの長調・短調のリールも制作中
- これから Instagram のリールとして順次投稿していく

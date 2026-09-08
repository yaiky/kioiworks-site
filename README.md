# 紀尾井ワークス 公式サイト

静的な HTML と CSS だけで作られています。ビルド工程はありません。
`index.html` をブラウザで開けば、そのまま表示されます。

## フォルダ構成

```
index.html      トップ
how.html        仕組み
price.html      料金
flow.html       導入の流れとFAQ
contact.html    お問い合わせ
tokushoho.html  特定商取引法に基づく表記
en/index.html   英語のデモページ（架空の体験工房の紹介ページ）
css/style.css   全ページ共通のスタイル
```

## 編集のしかた

- 文言を変えるときは、各 HTML ファイルの `<main>` の中を書き換えます。
- ヘッダー（上のメニュー）とフッター（下の連絡先）は全ページに同じものが書かれています。
  変えるときは、すべての HTML ファイルの `<header>` と `<footer>` を同じように書き換えてください。
- 色や文字の大きさは `css/style.css` で変えられます。濃紺の色は `--navy` の値です。

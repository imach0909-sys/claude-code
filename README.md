# obsidian2

Obsidian vault。`メモ/` フォルダに新規ノートを作成すると、自動でメモテンプレートが適用される。

## セットアップ

1. このフォルダを Obsidian で vault として開く
2. 設定 → コミュニティプラグイン → 制限モードをオフにする
3. Templater プラグインをインストールして有効化する
4. Obsidian を再読み込みすると `.obsidian/plugins/templater-obsidian/data.json` の設定が読み込まれる

## 使い方

- `メモ/` 配下で新規ノートを作成すると、`Templates/メモ.md` が自動適用される
- 他の場所で作成したノートに手動でテンプレートを適用する場合は、コマンドパレット（Cmd/Ctrl+P）から `Templater: Open Insert Template modal` を実行

## 構成

- `Templates/メモ.md` — メモテンプレート本体（タイトル / 作成日時 / タグ / 本文）
- `メモ/` — テンプレートが自動適用されるフォルダ
- `議事録/` — 会議議事録（Notionの議事録系DBと対応。ファイル名は `YYYY-MM-DD_会議名_議題.md`）
- `.obsidian/plugins/templater-obsidian/data.json` — Templater のフォルダ単位自動適用設定

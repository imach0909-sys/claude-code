# 動画2分割ツール

動画ファイルを **時間のちょうど真ん中** で2つに分割するデスクトップアプリです。
Python の標準GUI（tkinter）で作られており、`ffmpeg` を使って分割します。

例: `movie.mp4` を選ぶと `movie_part1.mp4` と `movie_part2.mp4` が作られます。

## 必要なもの

- **Python 3.8 以上**（tkinter 付き。多くの環境で標準同梱）
- **ffmpeg / ffprobe**

### ffmpeg のインストール

| OS | コマンド |
|----|----------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Windows | <https://ffmpeg.org/download.html> からダウンロードし、PATH を通す |

> tkinter が入っていない場合:
> - Ubuntu/Debian: `sudo apt install python3-tk`
> - macOS (Homebrew): `brew install python-tk`

## 使い方（GUIアプリ）

```bash
cd video-splitter
python3 app.py
```

1. 「選択...」で動画ファイルを選ぶ
2. 動画の長さと分割位置が表示される
3. （必要なら）出力先フォルダを変更
4. 「真ん中で2分割する」ボタンを押す

完了すると、保存先のフォルダに `〜_part1` と `〜_part2` が作成されます。

### 高速分割と正確分割

- **既定（ストリームコピー）**: 無劣化・高速。ただし分割位置は最寄りの
  キーフレームに丸められるため、数秒ずれることがあります。
- **「正確な位置で分割」にチェック**: 再エンコードしてぴったり真ん中で
  分割します。時間はかかります。

## コマンドラインでも使えます

GUIを使わず、ターミナルから直接実行することもできます。

```bash
# 入力ファイルと同じ場所に出力
python3 splitter.py movie.mp4

# 出力先を指定 / 正確な位置で分割
python3 splitter.py movie.mp4 -o ./out --reencode
```

## テスト

```bash
python3 -m unittest test_splitter.py -v
```

`ffmpeg` がある環境では、実際に短いテスト動画を生成して分割まで検証します。
無い場合はパス生成などのロジックのみ検証します。

## ファイル構成

| ファイル | 役割 |
|----------|------|
| `app.py` | tkinter GUI アプリ |
| `splitter.py` | 分割のコアロジック（CLIとしても利用可） |
| `test_splitter.py` | テスト |

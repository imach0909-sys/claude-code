# 🎙️ 会議文字起こし＋話者ラベリングアプリ

MP3/WAV の会議音声から、**文字起こし → 話者分離 → 声の特徴（性別）ラベル付け**を行う
ローカル完結の Web アプリです。音声は外部に送信されず、従量課金もかかりません。

## できること / できないこと

| 機能 | 状態 | 説明 |
|---|---|---|
| 文字起こし | ✅ | faster-whisper（ローカル・無料） |
| 話者分離 | ✅ | 「話者A / 話者B …」に区切る（pyannote、ローカル・無料） |
| 性別ラベル | ✅ | 声の高さ(F0)から「男性 / 女性 / 不明」を推定 |
| 実名の特定 | ❌ | 声だけでは不可。実名化には各人の声の事前登録が別途必要 |

> **性別ラベルの注意**: 声質に基づく統計的な推定です。中間的な声は「不明」になります。
> 個人の特定や性自認の判定を目的とするものではありません。

## ブラウザだけで試す（Google Colab・推奨）

PC にインストールしたくない／ブラウザしか使えない場合は、同梱の Colab ノートブックが
一番簡単です。リポジトリの clone も不要で、コードはノート内に全部入っています。

1. [Google Colab](https://colab.research.google.com/) を開く
2. 「ファイル → ノートブックをアップロード」で `colab_meeting_transcribe.ipynb` を開く
   （または GitHub タブにこのリポジトリの URL を貼って開く）
3. 上から順にセルを実行し、HuggingFace トークンを入力して MP3 をアップロード

> ⚠️ Colab は Google のクラウドで動くため、音声は一時的に Google のサーバーに送られます。
> 厳密に外部送信を避けたい場合は、下記の手元PCセットアップを使ってください。

## セットアップ（手元PCで動かす）

```bash
# 1. 依存をインストール
pip install -r requirements.txt

# 2. ffmpeg が必要（mp3 デコード用）
#    macOS: brew install ffmpeg
#    Ubuntu: sudo apt install ffmpeg
#    Windows: https://ffmpeg.org/download.html

# 3. 話者分離用の HuggingFace 無料トークンを用意
#    - https://hf.co/settings/tokens でトークン作成
#    - https://hf.co/pyannote/speaker-diarization-3.1 で利用規約に同意
export HF_TOKEN=hf_xxxxxxxx   # またはアプリのサイドバーで入力

# 4. 起動
streamlit run app.py
```

ブラウザが開いたら、会議音声をドラッグ＆ドロップして「文字起こしを実行」を押します。

## 精度をすぐ確認したいとき（CLI）

GUI を立てずに 1 コマンドで実行できます。

```bash
# 文字起こし＋話者ラベリング
python run.py 会議.mp3 --model medium --speakers 3

# 正解テキストがあれば文字誤り率(CER)も測定
python run.py 会議.mp3 --reference 正解.txt
```

モデルを使わないロジック層（性別推定・話者割り当て・整形）は、合成音とモック
データで検証できます。`small` モデルから試し、精度が足りなければ `medium` /
`large-v3` に上げてください。

```bash
python tests/test_logic.py   # 14 項目の自動テスト
```

## 出力例

```
[00:01] 話者A（男性）: では会議を始めます
[00:15] 話者B（女性）: 資料の3ページですが…
[00:42] 話者A（男性）: ありがとうございます
```

## 構成

```
speaker-transcriber/
├── app.py                    # Streamlit GUI
├── requirements.txt
└── transcriber/
    ├── transcribe.py         # 文字起こし (faster-whisper)
    ├── diarize.py            # 話者分離 (pyannote)
    ├── gender.py             # 性別推定 (librosa, F0)
    └── pipeline.py           # 統合パイプライン
```

## 今後の拡張アイデア

- **実名化**: 各メンバーの声を数十秒ずつ登録し、声紋照合（speaker verification）で
  「話者A → 田中さん」に置換する機能。
- **性別推定の高精度化**: F0 ベースから、学習済み音声分類モデルへの差し替え。
- **要約**: 文字起こし結果を LLM で議事録に自動要約。

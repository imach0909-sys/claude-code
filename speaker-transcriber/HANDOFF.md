# 引き継ぎ書（会議MP3 → 議事録アプリ）

新しいセッションで、`precise-minute-taking` スキルが存在する正しい場所で再開するための要約。

## ゴール

MP3会議音声を渡すと、(1) 話者分離トランスクリプトを作り、(2) 日時・出席者・説明者の
情報をもとに、既存スキル **`precise-minute-taking`** で議事録まで作成するアプリ。

## 決定事項（確定済み）

- **話者特定のレベル**: 話者分離＋性別ラベルまで（実名特定は出席者情報からのマッピングで対応）
- **実行方式**: Claude Code スキル方式（文字起こしはローカル無料、議事録生成は Claude Code
  自身＝定額内。追加API課金なし）
- **議事録生成**: 既存スキル `precise-minute-taking` に委譲する（このリポジトリには無い／
  別の場所＝おそらく Claude.ai か別リポジトリにある）

## 完成済み（このブランチ `claude/brave-thompson-xnhfil` にpush済み）

- `speaker-transcriber/` … 文字起こし＋話者分離＋性別推定の本体
  - `app.py` … Streamlit GUI（ドラッグ&ドロップ）
  - `run.py` … CLI。`--reference` で文字誤り率(CER)、末尾に話者サマリ（発話量・性別）を出力
  - `transcriber/` … transcribe(faster-whisper) / diarize(pyannote) / gender(F0) / pipeline
  - `tests/test_logic.py` … モデル不要のロジックテスト 14項目（全パス済み）
  - `colab_meeting_transcribe.ipynb` … ブラウザだけで動くColab版
  - `README.md` … セットアップ（Mac/Colab両対応）
- `.claude/skills/meeting-minutes/SKILL.md` … オーケストレーター。
  MP3→トランスクリプト→`precise-minute-taking`呼び出し までを定義

## 検証状況

- ロジック層（性別推定・話者割り当て・整形・CER）: この環境で実行し全パス
- 文字起こし本体: この環境はネット制限(huggingface.co不許可)でモデルDL不可のため未実行。
  → **ユーザーのMacでは実行可能**（制限なし）
- ユーザー提供のサンプルMP3(約107秒)でF0分析を実施 → 男女2話者の対話と推定。
  「全体性別=不明(161Hz)」になり、"話者分離してから性別推定" という設計の正しさを実データで確認。

## 新セッションでやること（残タスク）

1. **`precise-minute-taking` がある環境で開く**こと。`meeting-minutes` スキルはそれを呼ぶ前提。
2. `meeting-minutes` スキルの手順4の連携を、実際の `precise-minute-taking` の
   入力フォーマットに合わせて微調整（現状は一般的な構造で渡す仮実装）。
3. エンドツーエンドの実走（Mac, HF_TOKEN設定済み）:
   ```bash
   cd speaker-transcriber && source .venv/bin/activate && export HF_TOKEN=hf_xxx
   python run.py 会議.mp3 --model small --speakers <人数> --out transcript.txt
   ```
   → 話者サマリで話者→出席者をマッピング → `precise-minute-taking` で議事録生成。
4. （任意）メタ情報入力テンプレ（日時/出席者/説明者）の整備。

## 新セッション開始時の最初のプロンプト例

> このリポジトリの `.claude/skills/meeting-minutes/SKILL.md` と
> `speaker-transcriber/HANDOFF.md` を読んで状況を把握して。
> `precise-minute-taking` スキルと連携する部分を仕上げて、MP3から議事録までを通しで動かしたい。

## 環境メモ

- Mac: ffmpeg(`brew install ffmpeg`)＋venv＋`HF_TOKEN`＋pyannote規約同意 が必要
- 開発ブランチ: `claude/brave-thompson-xnhfil`

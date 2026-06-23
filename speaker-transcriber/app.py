"""会議音声 文字起こし＆話者ラベリング Web アプリ（Streamlit）。

使い方:
    pip install -r requirements.txt
    streamlit run app.py
"""

import os
import tempfile

import streamlit as st

from transcriber import process_audio
from transcriber.pipeline import to_text, format_timestamp

st.set_page_config(page_title="会議文字起こし＋話者ラベリング", page_icon="🎙️")

st.title("🎙️ 会議文字起こし＋話者ラベリング")
st.caption(
    "MP3/WAV の会議音声を、ローカルで文字起こし → 話者分離 → 声から性別ラベル付けします。"
    "音声は外部に送信されません。"
)

with st.sidebar:
    st.header("設定")
    model_size = st.selectbox(
        "Whisper モデル",
        ["tiny", "base", "small", "medium", "large-v3"],
        index=2,
        help="大きいほど高精度・低速。日本語実用なら small〜medium が目安。",
    )
    language = st.selectbox("言語", ["ja", "en", "auto"], index=0)
    num_speakers = st.number_input(
        "話者数（分かれば指定／0で自動推定）", min_value=0, max_value=20, value=0
    )
    hf_token = st.text_input(
        "HuggingFace トークン",
        value=os.environ.get("HF_TOKEN", ""),
        type="password",
        help="話者分離に必要（無料）。hf.co/settings/tokens で取得し、"
        "hf.co/pyannote/speaker-diarization-3.1 の規約に同意してください。",
    )
    st.markdown(
        "---\n**性別ラベルについて**: 声の高さ（F0）に基づく統計的な推定です。"
        "中間的な声は『不明』になります。個人の特定や性自認の判定を行うものではありません。"
    )

uploaded = st.file_uploader("会議音声ファイル", type=["mp3", "wav", "m4a", "flac", "ogg"])

if uploaded and st.button("文字起こしを実行", type="primary"):
    suffix = os.path.splitext(uploaded.name)[1] or ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        audio_path = tmp.name

    try:
        with st.spinner("処理中…（初回はモデルのダウンロードに時間がかかります）"):
            lines = process_audio(
                audio_path,
                model_size=model_size,
                language=None if language == "auto" else language,
                hf_token=hf_token or None,
                num_speakers=int(num_speakers) or None,
            )

        st.success(f"完了：{len(lines)} 発話を検出しました。")

        # 表形式で表示
        st.subheader("結果")
        st.dataframe(
            [
                {
                    "時刻": format_timestamp(ln.start),
                    "話者": ln.speaker,
                    "性別": ln.gender,
                    "発言": ln.text,
                }
                for ln in lines
            ],
            use_container_width=True,
            hide_index=True,
        )

        # テキストダウンロード
        text = to_text(lines)
        st.download_button(
            "テキストをダウンロード",
            data=text,
            file_name=f"{os.path.splitext(uploaded.name)[0]}_transcript.txt",
            mime="text/plain",
        )
    except Exception as e:  # noqa: BLE001 - GUI 上にエラーを見せる
        st.error(f"エラーが発生しました:\n\n{e}")
    finally:
        try:
            os.unlink(audio_path)
        except OSError:
            pass

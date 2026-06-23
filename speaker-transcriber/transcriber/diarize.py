"""pyannote.audio による話者分離（ダイアライゼーション）。

「いつ・どの話者が」話したかを区切るが、その話者が誰か（実名）は判定しない。
出力はあくまで SPEAKER_00 / SPEAKER_01 ... という匿名ラベル。
"""

import os
from dataclasses import dataclass


@dataclass
class SpeakerTurn:
    """1 人の話者が連続して話した区間。"""

    start: float
    end: float
    speaker: str  # 例: "SPEAKER_00"


def diarize(audio_path: str, hf_token: str | None = None, num_speakers: int | None = None) -> list[SpeakerTurn]:
    """話者分離を実行して発話区間のリストを返す。

    Args:
        audio_path: 音声ファイルパス。
        hf_token: HuggingFace の無料アクセストークン。未指定なら環境変数
            HF_TOKEN / HUGGINGFACE_TOKEN を参照。pyannote のゲートモデル利用に必須。
        num_speakers: 話者数が分かっていれば指定すると精度が上がる。None で自動推定。

    Returns:
        SpeakerTurn のリスト（開始秒順）。
    """
    from pyannote.audio import Pipeline

    token = hf_token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        raise RuntimeError(
            "話者分離には HuggingFace の無料トークンが必要です。\n"
            "1) https://hf.co/settings/tokens でトークンを作成\n"
            "2) https://hf.co/pyannote/speaker-diarization-3.1 で利用規約に同意\n"
            "3) 環境変数 HF_TOKEN に設定、または GUI のサイドバーで入力してください。"
        )

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=token,
    )

    kwargs = {}
    if num_speakers:
        kwargs["num_speakers"] = num_speakers

    diarization = pipeline(audio_path, **kwargs)

    turns = [
        SpeakerTurn(start=segment.start, end=segment.end, speaker=speaker)
        for segment, _track, speaker in diarization.itertracks(yield_label=True)
    ]
    turns.sort(key=lambda t: t.start)
    return turns

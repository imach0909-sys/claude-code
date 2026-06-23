"""faster-whisper による文字起こし（ローカル・無料）。"""

from dataclasses import dataclass


@dataclass
class Segment:
    """文字起こしの 1 セグメント。"""

    start: float
    end: float
    text: str


def transcribe(audio_path: str, model_size: str = "small", language: str = "ja") -> list[Segment]:
    """音声ファイルを文字起こしし、タイムスタンプ付きセグメントを返す。

    Args:
        audio_path: mp3 / wav などの音声ファイルパス。
        model_size: Whisper モデルサイズ（tiny/base/small/medium/large-v3）。
            大きいほど高精度・低速。日本語実用なら small〜medium が目安。
        language: 言語コード。None で自動判定。

    Returns:
        開始・終了秒とテキストを持つ Segment のリスト。
    """
    # 重い依存なので関数内 import（GUI 起動を速く保つため）
    from faster_whisper import WhisperModel

    # CPU でも動くよう int8。GPU 環境なら device="cuda" で高速化可能。
    model = WhisperModel(model_size, device="auto", compute_type="int8")

    segments, _info = model.transcribe(
        audio_path,
        language=language,
        vad_filter=True,  # 無音区間を除去して精度・速度を改善
    )

    return [
        Segment(start=seg.start, end=seg.end, text=seg.text.strip())
        for seg in segments
        if seg.text.strip()
    ]

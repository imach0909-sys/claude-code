"""会議音声の文字起こし＋話者分離＋性別推定パイプライン。"""

from .pipeline import process_audio, TranscriptLine

__all__ = ["process_audio", "TranscriptLine"]

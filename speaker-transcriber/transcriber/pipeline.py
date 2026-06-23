"""文字起こし・話者分離・性別推定を統合するパイプライン。"""

from collections import defaultdict
from dataclasses import dataclass

import numpy as np

from .transcribe import transcribe, Segment
from .diarize import diarize, SpeakerTurn
from .gender import estimate_gender_from_f0


@dataclass
class TranscriptLine:
    """最終出力の 1 行。"""

    start: float
    end: float
    speaker: str       # 例: "話者A"
    gender: str        # "男性" / "女性" / "不明"
    text: str


def _assign_speaker(seg: Segment, turns: list[SpeakerTurn]) -> str:
    """文字起こしセグメントに、最も重なる話者区間のラベルを割り当てる。"""
    best_speaker = "SPEAKER_?"
    best_overlap = 0.0
    for turn in turns:
        overlap = min(seg.end, turn.end) - max(seg.start, turn.start)
        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = turn.speaker
    return best_speaker


def _speaker_gender(
    speaker: str,
    turns: list[SpeakerTurn],
    samples: np.ndarray,
    sr: int,
) -> tuple[str, float | None]:
    """話者の全発話区間の音声をつないで性別を推定する。"""
    chunks = []
    for turn in turns:
        if turn.speaker != speaker:
            continue
        a = int(turn.start * sr)
        b = int(turn.end * sr)
        if b > a:
            chunks.append(samples[a:b])
    if not chunks:
        return "不明", None
    return estimate_gender_from_f0(np.concatenate(chunks), sr)


def _friendly_labels(speakers: list[str]) -> dict[str, str]:
    """SPEAKER_00 → 話者A のような読みやすいラベルへ変換する対応表を作る。"""
    labels = {}
    for i, spk in enumerate(sorted(speakers)):
        labels[spk] = f"話者{chr(ord('A') + i)}" if i < 26 else f"話者{i + 1}"
    return labels


def process_audio(
    audio_path: str,
    model_size: str = "small",
    language: str = "ja",
    hf_token: str | None = None,
    num_speakers: int | None = None,
) -> list[TranscriptLine]:
    """音声ファイルから話者ラベル・性別付きのトランスクリプトを生成する。

    Args:
        audio_path: mp3 / wav などの音声ファイルパス。
        model_size: Whisper モデルサイズ。
        language: 言語コード。
        hf_token: pyannote 用 HuggingFace トークン。
        num_speakers: 既知の話者数（任意）。

    Returns:
        TranscriptLine のリスト（時系列順）。
    """
    import librosa

    # 1. 文字起こし
    segments = transcribe(audio_path, model_size=model_size, language=language)

    # 2. 話者分離
    turns = diarize(audio_path, hf_token=hf_token, num_speakers=num_speakers)

    # 3. 性別推定用に音声を 16kHz モノラルで一括ロード
    samples, sr = librosa.load(audio_path, sr=16000, mono=True)

    # 4. 各話者の性別を推定
    speakers = sorted({t.speaker for t in turns})
    gender_map = {spk: _speaker_gender(spk, turns, samples, sr)[0] for spk in speakers}
    label_map = _friendly_labels(speakers)

    # 5. 各文字起こしセグメントに話者・性別を付与
    lines: list[TranscriptLine] = []
    for seg in segments:
        raw_speaker = _assign_speaker(seg, turns)
        lines.append(
            TranscriptLine(
                start=seg.start,
                end=seg.end,
                speaker=label_map.get(raw_speaker, raw_speaker),
                gender=gender_map.get(raw_speaker, "不明"),
                text=seg.text,
            )
        )
    return lines


def format_timestamp(seconds: float) -> str:
    """秒を mm:ss 形式に整形する。"""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def to_text(lines: list[TranscriptLine]) -> str:
    """トランスクリプトを読みやすいプレーンテキストに変換する。"""
    out = []
    for ln in lines:
        out.append(f"[{format_timestamp(ln.start)}] {ln.speaker}（{ln.gender}）: {ln.text}")
    return "\n".join(out)

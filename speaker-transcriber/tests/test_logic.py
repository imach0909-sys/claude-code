"""モデル不要で動くロジック層の検証スクリプト。

実音声を使わずに、以下を実際に動かして精度・正しさを確認する:
  1. 性別推定 (gender.py) … 合成音声(F0既知)で男女/不明を正しく出すか
  2. 話者割り当て (_assign_speaker) … 重なり最大の話者を選ぶか
  3. ラベル変換・整形 … SPEAKER_00→話者A、mm:ss など

実行:  python tests/test_logic.py
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transcriber.gender import estimate_gender_from_f0
from transcriber.transcribe import Segment
from transcriber.diarize import SpeakerTurn
from transcriber.pipeline import (
    _assign_speaker,
    _friendly_labels,
    _speaker_gender,
    format_timestamp,
    to_text,
    TranscriptLine,
)

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    mark = "OK " if cond else "NG "
    print(f"  {mark} {name}" + (f"  ({detail})" if detail else ""))
    if cond:
        PASS += 1
    else:
        FAIL += 1


def tone(f0_hz, seconds=1.5, sr=16000):
    """基本周波数 f0_hz の母音っぽい合成音（基音＋倍音）を作る。"""
    t = np.linspace(0, seconds, int(sr * seconds), endpoint=False)
    sig = (
        1.0 * np.sin(2 * np.pi * f0_hz * t)
        + 0.5 * np.sin(2 * np.pi * 2 * f0_hz * t)
        + 0.3 * np.sin(2 * np.pi * 3 * f0_hz * t)
    )
    return (sig / np.max(np.abs(sig))).astype(np.float32), sr


print("1) 性別推定（合成音, F0既知）")
for f0, expected in [(110, "男性"), (130, "男性"), (220, "女性"), (240, "女性"), (165, "不明")]:
    samples, sr = tone(f0)
    label, med = estimate_gender_from_f0(samples, sr)
    check(f"F0={f0}Hz -> {label}", label == expected,
          f"期待={expected}, 推定中央値F0={med:.0f}Hz" if med else "F0取得不可")

print("\n2) 話者割り当て（重なり最大の話者を選ぶ）")
turns = [
    SpeakerTurn(0.0, 5.0, "SPEAKER_00"),
    SpeakerTurn(5.0, 10.0, "SPEAKER_01"),
    SpeakerTurn(10.0, 14.0, "SPEAKER_00"),
]
check("0-3s の発話 -> SPEAKER_00",
      _assign_speaker(Segment(0.0, 3.0, "x"), turns) == "SPEAKER_00")
check("6-9s の発話 -> SPEAKER_01",
      _assign_speaker(Segment(6.0, 9.0, "x"), turns) == "SPEAKER_01")
check("境界またぎ 4-7s（重なり大きい側） -> SPEAKER_01",
      _assign_speaker(Segment(4.0, 7.0, "x"), turns) == "SPEAKER_01")

print("\n3) ラベル変換・整形")
labels = _friendly_labels(["SPEAKER_01", "SPEAKER_00"])
check("SPEAKER_00 -> 話者A", labels["SPEAKER_00"] == "話者A", str(labels))
check("SPEAKER_01 -> 話者B", labels["SPEAKER_01"] == "話者B")
check("75秒 -> 01:15", format_timestamp(75) == "01:15")

print("\n4) 話者ごとの性別集計（区間連結）")
sr = 16000
male, _ = tone(115, seconds=3.0)
female, _ = tone(225, seconds=3.0)
mixed = np.concatenate([male, female])  # 0-3s=男性, 3-6s=女性
spk_turns = [SpeakerTurn(0.0, 3.0, "S0"), SpeakerTurn(3.0, 6.0, "S1")]
g0, _ = _speaker_gender("S0", spk_turns, mixed, sr)
g1, _ = _speaker_gender("S1", spk_turns, mixed, sr)
check("話者S0(0-3s, 115Hz) -> 男性", g0 == "男性", f"推定={g0}")
check("話者S1(3-6s, 225Hz) -> 女性", g1 == "女性", f"推定={g1}")

print("\n5) 出力整形")
lines = [
    TranscriptLine(1.0, 4.0, "話者A", "男性", "では会議を始めます"),
    TranscriptLine(15.0, 18.0, "話者B", "女性", "資料の3ページですが"),
]
out = to_text(lines)
check("出力行フォーマット", "[00:01] 話者A（男性）: では会議を始めます" in out, repr(out.splitlines()[0]))

print(f"\n==== 結果: {PASS} passed, {FAIL} failed ====")
sys.exit(1 if FAIL else 0)

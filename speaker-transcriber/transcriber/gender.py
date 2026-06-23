"""声の高さ（基本周波数 F0）から性別を推定する。

注意: これは声質に基づく統計的な推定であり、個人の性自認を判定するものではない。
F0 が中間帯の話者は「不明」とし、誤った断定を避ける。実用上は「男性的な声 /
女性的な声」のヒントとして扱うのが適切。
"""

import numpy as np

# 一般的な発話の基本周波数の目安（Hz）
# 成人男性: おおむね 85-180Hz / 成人女性: おおむね 165-255Hz
MALE_MAX = 145.0   # これ未満なら男性寄り
FEMALE_MIN = 190.0  # これ超なら女性寄り


def estimate_gender_from_f0(samples: np.ndarray, sr: int) -> tuple[str, float | None]:
    """音声サンプルから話者の性別ラベルと中央値 F0 を推定する。

    Args:
        samples: モノラル音声波形（float32, -1.0〜1.0）。
        sr: サンプリングレート。

    Returns:
        (ラベル, 中央値F0)。ラベルは "男性" / "女性" / "不明"。
        有声区間が取れない場合は ("不明", None)。
    """
    import librosa

    if samples.size < sr // 2:  # 0.5 秒未満は判定不能
        return "不明", None

    # 確率的 YIN で基本周波数を抽出（有声部のみ）
    f0, voiced_flag, _ = librosa.pyin(
        samples,
        fmin=65.0,
        fmax=400.0,
        sr=sr,
    )

    voiced_f0 = f0[voiced_flag & ~np.isnan(f0)]
    if voiced_f0.size == 0:
        return "不明", None

    median_f0 = float(np.median(voiced_f0))

    if median_f0 <= MALE_MAX:
        return "男性", median_f0
    if median_f0 >= FEMALE_MIN:
        return "女性", median_f0
    return "不明", median_f0

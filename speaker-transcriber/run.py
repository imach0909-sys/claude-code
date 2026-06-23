"""コマンドラインで精度を素早く確認するためのスクリプト。

GUI を立てずに 1 コマンドで文字起こし＋話者ラベリングを実行する。
正解テキストを --reference で渡すと、文字誤り率 (CER) も表示する。

例:
    python run.py 会議.mp3 --model medium --speakers 3
    python run.py 会議.mp3 --reference 正解.txt
"""

import argparse
import sys

from transcriber import process_audio
from transcriber.pipeline import to_text


def cer(hypothesis: str, reference: str) -> float:
    """文字誤り率 (Character Error Rate) を Levenshtein 距離で計算する。

    日本語向けに空白・改行を除去した文字単位で比較する。0.0 が完全一致。
    """
    def norm(s: str) -> str:
        return "".join(s.split())

    h, r = norm(hypothesis), norm(reference)
    if not r:
        return 0.0
    # Levenshtein 距離（1 行 DP）
    prev = list(range(len(h) + 1))
    for i, rc in enumerate(r, 1):
        cur = [i]
        for j, hc in enumerate(h, 1):
            cost = 0 if rc == hc else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[-1] / len(r)


def main() -> int:
    p = argparse.ArgumentParser(description="会議音声の文字起こし＋話者ラベリング")
    p.add_argument("audio", help="音声ファイル (mp3/wav/m4a など)")
    p.add_argument("--model", default="small",
                   help="Whisper モデル (tiny/base/small/medium/large-v3)")
    p.add_argument("--language", default="ja", help="言語コード。auto で自動判定")
    p.add_argument("--speakers", type=int, default=0,
                   help="話者数（分かれば指定すると精度向上。0=自動）")
    p.add_argument("--hf-token", default=None, help="HuggingFace トークン")
    p.add_argument("--out", default=None, help="結果テキストの保存先パス")
    p.add_argument("--reference", default=None,
                   help="正解テキストファイル。指定すると文字誤り率(CER)を表示")
    args = p.parse_args()

    lines = process_audio(
        args.audio,
        model_size=args.model,
        language=None if args.language == "auto" else args.language,
        hf_token=args.hf_token,
        num_speakers=args.speakers or None,
    )

    text = to_text(lines)
    print(text)
    print(f"\n--- 検出: {len(lines)} 発話 / "
          f"{len({ln.speaker for ln in lines})} 話者 ---")

    # 話者ごとのサマリ（話者→出席者名のマッピングや「説明者」判定の手がかり）
    stats: dict[str, dict] = {}
    for ln in lines:
        s = stats.setdefault(ln.speaker, {"count": 0, "dur": 0.0, "gender": ln.gender})
        s["count"] += 1
        s["dur"] += max(0.0, ln.end - ln.start)
    total = sum(s["dur"] for s in stats.values()) or 1.0
    print("\n--- 話者サマリ（発話量の多い順） ---")
    for spk, s in sorted(stats.items(), key=lambda kv: -kv[1]["dur"]):
        print(f"  {spk}（{s['gender']}）: {s['count']}発話 / "
              f"約{s['dur']:.0f}秒 / 発話比率 {s['dur'] / total:.0%}")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"保存しました: {args.out}")

    if args.reference:
        with open(args.reference, encoding="utf-8") as f:
            ref = f.read()
        hyp = "".join(ln.text for ln in lines)
        score = cer(hyp, ref)
        print(f"\n文字誤り率 CER: {score:.1%}  （文字精度 {1 - score:.1%}）")

    return 0


if __name__ == "__main__":
    sys.exit(main())

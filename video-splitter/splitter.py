"""動画を真ん中で2分割するためのコアロジック（GUIなし）。

ffmpeg / ffprobe を利用します。GUIから呼び出されるほか、
単体でもテスト・利用できるように関数として切り出しています。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass


class SplitterError(Exception):
    """分割処理に関するエラー。"""


def check_dependencies() -> None:
    """ffmpeg / ffprobe が利用可能か確認する。"""
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise SplitterError(
                f"'{tool}' が見つかりません。ffmpeg をインストールしてください。\n"
                "  macOS:  brew install ffmpeg\n"
                "  Ubuntu: sudo apt install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html"
            )


def get_duration(input_path: str) -> float:
    """動画の長さ（秒）を ffprobe で取得する。"""
    if not os.path.isfile(input_path):
        raise SplitterError(f"ファイルが見つかりません: {input_path}")

    cmd = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        input_path,
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as exc:
        raise SplitterError(
            f"動画情報の取得に失敗しました:\n{exc.stderr.strip()}"
        ) from exc

    try:
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise SplitterError("動画の長さを判定できませんでした。") from exc

    if duration <= 0:
        raise SplitterError("動画の長さが0秒です。分割できません。")
    return duration


def _output_paths(input_path: str, output_dir: str | None) -> tuple[str, str]:
    base = os.path.basename(input_path)
    stem, ext = os.path.splitext(base)
    if not ext:
        ext = ".mp4"
    target_dir = output_dir or os.path.dirname(os.path.abspath(input_path))
    part1 = os.path.join(target_dir, f"{stem}_part1{ext}")
    part2 = os.path.join(target_dir, f"{stem}_part2{ext}")
    return part1, part2


@dataclass
class SplitResult:
    part1: str
    part2: str
    split_point: float  # 分割した時刻（秒）
    duration: float     # 元動画の長さ（秒）


def split_in_half(
    input_path: str,
    output_dir: str | None = None,
    reencode: bool = False,
) -> SplitResult:
    """動画を時間の真ん中で2つに分割する。

    Args:
        input_path: 入力動画のパス。
        output_dir: 出力先ディレクトリ。Noneなら入力ファイルと同じ場所。
        reencode: True なら再エンコードして正確な位置で分割する。
                  False（既定）はストリームコピーで高速だが、
                  分割位置が最寄りのキーフレームに丸められる。

    Returns:
        SplitResult: 生成された2ファイルのパスなど。
    """
    check_dependencies()
    duration = get_duration(input_path)
    midpoint = duration / 2.0
    part1, part2 = _output_paths(input_path, output_dir)

    if reencode:
        # 正確な位置で分割（再エンコードのため低速）
        codec_args = ["-c:v", "libx264", "-c:a", "aac"]
    else:
        # キーフレーム単位の高速分割（無劣化）
        codec_args = ["-c", "copy"]

    # 前半: 0 〜 midpoint
    cmd1 = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", f"{midpoint:.3f}",
        *codec_args,
        part1,
    ]
    # 後半: midpoint 〜 末尾
    cmd2 = [
        "ffmpeg", "-y",
        "-ss", f"{midpoint:.3f}",
        "-i", input_path,
        *codec_args,
        part2,
    ]

    for cmd in (cmd1, cmd2):
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as exc:
            raise SplitterError(
                f"分割に失敗しました:\n{exc.stderr.strip()[-800:]}"
            ) from exc

    return SplitResult(
        part1=part1, part2=part2, split_point=midpoint, duration=duration
    )


def format_timestamp(seconds: float) -> str:
    """秒を HH:MM:SS 形式に整形する。"""
    seconds = max(0, int(round(seconds)))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


if __name__ == "__main__":
    # コマンドラインからも使えるようにする
    import argparse

    parser = argparse.ArgumentParser(description="動画を真ん中で2分割します。")
    parser.add_argument("input", help="入力動画ファイル")
    parser.add_argument("-o", "--output-dir", help="出力先ディレクトリ")
    parser.add_argument(
        "--reencode", action="store_true",
        help="正確な位置で分割（再エンコード・低速）",
    )
    args = parser.parse_args()

    try:
        res = split_in_half(args.input, args.output_dir, args.reencode)
    except SplitterError as e:
        raise SystemExit(f"エラー: {e}")

    print(f"元の長さ : {format_timestamp(res.duration)}")
    print(f"分割位置 : {format_timestamp(res.split_point)}")
    print(f"前半     : {res.part1}")
    print(f"後半     : {res.part2}")

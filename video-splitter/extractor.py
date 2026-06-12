"""動画から音声だけを取り出すコアロジック（GUIなし）。

ffmpeg を利用します。共通処理（ffmpegの解決・実行・時刻整形）は
splitter.py を再利用します。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from splitter import (
    SplitterError,
    _run,
    check_dependencies,
    get_duration,
    resolve_tool,
)

# 出力形式ごとの ffmpeg 設定
#   ext     : 出力ファイルの拡張子
#   codec   : ffmpeg に渡すコーデック引数
FORMATS: dict[str, dict] = {
    "MP3": {"ext": ".mp3", "codec": ["-vn", "-c:a", "libmp3lame", "-q:a", "2"]},
    "M4A (AAC)": {"ext": ".m4a", "codec": ["-vn", "-c:a", "aac", "-b:a", "192k"]},
    "WAV": {"ext": ".wav", "codec": ["-vn", "-c:a", "pcm_s16le"]},
}

DEFAULT_FORMAT = "MP3"


class ExtractError(SplitterError):
    """音声抽出に関するエラー。"""


@dataclass
class ExtractResult:
    output: str        # 生成された音声ファイルのパス
    duration: float    # 元動画の長さ（秒）
    fmt: str           # 使用した形式名


def _output_path(input_path: str, ext: str, output_dir: str | None) -> str:
    stem, _ = os.path.splitext(os.path.basename(input_path))
    target_dir = output_dir or os.path.dirname(os.path.abspath(input_path))
    return os.path.join(target_dir, f"{stem}{ext}")


def extract_audio(
    input_path: str,
    fmt: str = DEFAULT_FORMAT,
    output_dir: str | None = None,
) -> ExtractResult:
    """動画から音声を取り出して指定形式で保存する。

    Args:
        input_path: 入力動画のパス。
        fmt: 出力形式名（FORMATS のキー: "MP3" / "M4A (AAC)" / "WAV"）。
        output_dir: 出力先ディレクトリ。Noneなら入力ファイルと同じ場所。

    Returns:
        ExtractResult: 生成された音声ファイルのパスなど。
    """
    if fmt not in FORMATS:
        raise ExtractError(f"未対応の形式です: {fmt}")

    check_dependencies()
    duration = get_duration(input_path)
    spec = FORMATS[fmt]
    output = _output_path(input_path, spec["ext"], output_dir)
    ffmpeg = resolve_tool("ffmpeg") or "ffmpeg"

    cmd = [ffmpeg, "-y", "-i", input_path, *spec["codec"], output]
    result = _run(cmd)
    if result.returncode != 0:
        stderr = result.stderr.strip()[-800:]
        # 音声トラックが無い動画への配慮
        if "does not contain any stream" in stderr or "Output file" in stderr:
            raise ExtractError(
                "音声の取り出しに失敗しました。"
                "この動画には音声トラックが無い可能性があります。\n\n"
                f"{stderr}"
            )
        raise ExtractError(f"音声の取り出しに失敗しました:\n{stderr}")

    return ExtractResult(output=output, duration=duration, fmt=fmt)


if __name__ == "__main__":
    import argparse

    from splitter import format_timestamp

    parser = argparse.ArgumentParser(description="動画から音声を取り出します。")
    parser.add_argument("input", help="入力動画ファイル")
    parser.add_argument(
        "-f", "--format", default=DEFAULT_FORMAT, choices=list(FORMATS),
        help="出力形式（既定: MP3）",
    )
    parser.add_argument("-o", "--output-dir", help="出力先ディレクトリ")
    args = parser.parse_args()

    try:
        res = extract_audio(args.input, args.format, args.output_dir)
    except SplitterError as e:
        raise SystemExit(f"エラー: {e}")

    print(f"元の長さ : {format_timestamp(res.duration)}")
    print(f"形式     : {res.fmt}")
    print(f"出力     : {res.output}")

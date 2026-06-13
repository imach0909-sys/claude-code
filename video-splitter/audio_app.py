"""動画から音声を取り出すデスクトップGUIアプリ（tkinter）。

使い方:
    python3 audio_app.py

ffmpeg / ffprobe が必要です（README参照）。
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from extractor import (
    DEFAULT_FORMAT,
    FORMATS,
    ExtractError,
    extract_audio,
)
from splitter import (
    SplitterError,
    check_dependencies,
    format_timestamp,
    get_duration,
)

VIDEO_FILETYPES = [
    ("動画ファイル", "*.mp4 *.mov *.mkv *.avi *.webm *.m4v *.flv *.wmv"),
    ("すべてのファイル", "*.*"),
]


class AudioExtractorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("動画から音声を取り出すツール")
        self.root.geometry("560x320")
        self.root.minsize(480, 300)

        self.input_path: str | None = None
        self.output_dir: str | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 6}
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        # 入力ファイル
        ttk.Label(frame, text="入力動画:").grid(row=0, column=0, sticky="w", **pad)
        self.input_var = tk.StringVar(value="（未選択）")
        ttk.Label(frame, textvariable=self.input_var, foreground="#444",
                  wraplength=300).grid(row=0, column=1, sticky="w", **pad)
        ttk.Button(frame, text="選択...", command=self.choose_input).grid(
            row=0, column=2, **pad)

        # 出力先
        ttk.Label(frame, text="出力先:").grid(row=1, column=0, sticky="w", **pad)
        self.output_var = tk.StringVar(value="（入力ファイルと同じ場所）")
        ttk.Label(frame, textvariable=self.output_var, foreground="#444",
                  wraplength=300).grid(row=1, column=1, sticky="w", **pad)
        ttk.Button(frame, text="変更...", command=self.choose_output).grid(
            row=1, column=2, **pad)

        # 出力形式
        ttk.Label(frame, text="形式:").grid(row=2, column=0, sticky="w", **pad)
        self.format_var = tk.StringVar(value=DEFAULT_FORMAT)
        ttk.Combobox(
            frame, textvariable=self.format_var, values=list(FORMATS),
            state="readonly", width=14,
        ).grid(row=2, column=1, sticky="w", **pad)

        # 動画情報
        self.info_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.info_var, foreground="#0a6").grid(
            row=3, column=0, columnspan=3, sticky="w", **pad)

        # 実行ボタン
        self.run_btn = ttk.Button(
            frame, text="音声を取り出す", command=self.start_extract)
        self.run_btn.grid(row=4, column=0, columnspan=3, pady=(14, 6))
        self.run_btn.state(["disabled"])

        # プログレスバー
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.grid(row=5, column=0, columnspan=3, sticky="ew", **pad)

        # ステータス
        self.status_var = tk.StringVar(value="動画ファイルを選択してください。")
        ttk.Label(frame, textvariable=self.status_var, foreground="#666").grid(
            row=6, column=0, columnspan=3, sticky="w", **pad)

    def choose_input(self) -> None:
        path = filedialog.askopenfilename(
            title="動画ファイルを選択", filetypes=VIDEO_FILETYPES)
        if not path:
            return
        self.input_path = path
        self.input_var.set(os.path.basename(path))
        # 取り出しに長さは不要なので、すぐにボタンを有効化する。
        # 長さの表示は「おまけ」としてバックグラウンドで読み込む。
        self.run_btn.state(["!disabled"])
        self.status_var.set("準備完了。形式を選んでボタンを押してください。")
        self.info_var.set("長さ: 確認中...")
        # 古い読み込みの結果を無視するためのトークン
        self._info_token = getattr(self, "_info_token", 0) + 1
        token = self._info_token
        threading.Thread(
            target=self._load_info, args=(path, token), daemon=True
        ).start()

    def _load_info(self, path: str, token: int) -> None:
        try:
            duration = get_duration(path)
            text = f"長さ: {format_timestamp(duration)}"
        except SplitterError:
            text = "長さ: 不明"
        # 表示中のファイルが変わっていなければラベルだけ更新（ボタンは触らない）
        self.root.after(0, lambda: self._update_info(text, token))

    def _update_info(self, text: str, token: int) -> None:
        if token == getattr(self, "_info_token", 0):
            self.info_var.set(text)

    def choose_output(self) -> None:
        path = filedialog.askdirectory(title="出力先フォルダを選択")
        if not path:
            return
        self.output_dir = path
        self.output_var.set(path)

    def start_extract(self) -> None:
        if not self.input_path:
            return
        self.run_btn.state(["disabled"])
        self.progress.start(12)
        self.status_var.set("取り出し中... しばらくお待ちください。")
        threading.Thread(target=self._run_extract, daemon=True).start()

    def _run_extract(self) -> None:
        try:
            result = extract_audio(
                self.input_path, self.format_var.get(), self.output_dir)
        except SplitterError as e:
            self.root.after(0, lambda: self._on_error(str(e)))
            return
        self.root.after(0, lambda: self._on_done(result))

    def _on_done(self, result) -> None:
        self.progress.stop()
        self.run_btn.state(["!disabled"])
        self.status_var.set("完了しました！")
        messagebox.showinfo(
            "完了",
            "音声の取り出しが完了しました。\n\n"
            f"ファイル: {os.path.basename(result.output)}\n"
            f"保存先: {os.path.dirname(result.output)}",
        )

    def _on_error(self, message: str) -> None:
        self.progress.stop()
        self.run_btn.state(["!disabled"])
        self.status_var.set("失敗しました。")
        messagebox.showerror("エラー", message)


def main() -> None:
    try:
        check_dependencies()
    except SplitterError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("依存ツールが見つかりません", str(e))
        return

    root = tk.Tk()
    AudioExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

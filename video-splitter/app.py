"""動画を真ん中で2分割するデスクトップGUIアプリ（tkinter）。

使い方:
    python3 app.py

ffmpeg / ffprobe が必要です（README参照）。
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from splitter import (
    SplitterError,
    check_dependencies,
    format_timestamp,
    get_duration,
    split_in_half,
)

VIDEO_FILETYPES = [
    ("動画ファイル", "*.mp4 *.mov *.mkv *.avi *.webm *.m4v *.flv *.wmv"),
    ("すべてのファイル", "*.*"),
]


class VideoSplitterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("動画2分割ツール")
        self.root.geometry("560x320")
        self.root.minsize(480, 300)

        self.input_path: str | None = None
        self.output_dir: str | None = None

        self._build_ui()

    # ---- UI 構築 ----
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

        # 動画情報
        self.info_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.info_var, foreground="#0a6").grid(
            row=2, column=0, columnspan=3, sticky="w", **pad)

        # 高画質（再エンコード）オプション
        self.reencode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text="正確な位置で分割（再エンコード・低速だが位置がぴったり）",
            variable=self.reencode_var,
        ).grid(row=3, column=0, columnspan=3, sticky="w", **pad)

        # 実行ボタン
        self.split_btn = ttk.Button(
            frame, text="真ん中で2分割する", command=self.start_split)
        self.split_btn.grid(row=4, column=0, columnspan=3, pady=(14, 6))
        self.split_btn.state(["disabled"])

        # プログレスバー
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.grid(row=5, column=0, columnspan=3, sticky="ew", **pad)

        # ステータス
        self.status_var = tk.StringVar(value="動画ファイルを選択してください。")
        ttk.Label(frame, textvariable=self.status_var, foreground="#666").grid(
            row=6, column=0, columnspan=3, sticky="w", **pad)

    # ---- イベント ----
    def choose_input(self) -> None:
        path = filedialog.askopenfilename(
            title="動画ファイルを選択", filetypes=VIDEO_FILETYPES)
        if not path:
            return
        self.input_path = path
        self.input_var.set(os.path.basename(path))
        self.info_var.set("動画情報を読み込み中...")
        self.split_btn.state(["disabled"])
        threading.Thread(target=self._load_info, daemon=True).start()

    def _load_info(self) -> None:
        try:
            duration = get_duration(self.input_path)
        except SplitterError as e:
            self.root.after(0, lambda: self._on_info_error(str(e)))
            return
        self.root.after(0, lambda: self._on_info_loaded(duration))

    def _on_info_loaded(self, duration: float) -> None:
        self.info_var.set(
            f"長さ: {format_timestamp(duration)} → "
            f"分割位置: {format_timestamp(duration / 2)}"
        )
        self.status_var.set("準備完了。ボタンを押して分割できます。")
        self.split_btn.state(["!disabled"])

    def _on_info_error(self, message: str) -> None:
        self.info_var.set("")
        messagebox.showerror("エラー", message)
        self.status_var.set("別のファイルを選択してください。")

    def choose_output(self) -> None:
        path = filedialog.askdirectory(title="出力先フォルダを選択")
        if not path:
            return
        self.output_dir = path
        self.output_var.set(path)

    def start_split(self) -> None:
        if not self.input_path:
            return
        self.split_btn.state(["disabled"])
        self.progress.start(12)
        self.status_var.set("分割中... しばらくお待ちください。")
        threading.Thread(target=self._run_split, daemon=True).start()

    def _run_split(self) -> None:
        try:
            result = split_in_half(
                self.input_path, self.output_dir, self.reencode_var.get())
        except SplitterError as e:
            self.root.after(0, lambda: self._on_split_error(str(e)))
            return
        self.root.after(0, lambda: self._on_split_done(result))

    def _on_split_done(self, result) -> None:
        self.progress.stop()
        self.split_btn.state(["!disabled"])
        self.status_var.set("完了しました！")
        messagebox.showinfo(
            "完了",
            "2分割が完了しました。\n\n"
            f"前半: {os.path.basename(result.part1)}\n"
            f"後半: {os.path.basename(result.part2)}\n\n"
            f"保存先: {os.path.dirname(result.part1)}",
        )

    def _on_split_error(self, message: str) -> None:
        self.progress.stop()
        self.split_btn.state(["!disabled"])
        self.status_var.set("失敗しました。")
        messagebox.showerror("エラー", message)


def main() -> None:
    try:
        check_dependencies()
    except SplitterError as e:
        # GUI起動前にffmpegが無い場合は簡易ダイアログで通知
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("依存ツールが見つかりません", str(e))
        return

    root = tk.Tk()
    VideoSplitterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

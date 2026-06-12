"""extractor.py のテスト。

ffmpeg があれば実際に短い動画（音声付き）を生成して抽出まで検証する。
無ければ純粋なロジック部分のみ検証する。
"""

import os
import shutil
import subprocess
import tempfile
import unittest

import extractor


HAS_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


class PureLogicTests(unittest.TestCase):
    def test_output_path_default_dir(self):
        p = extractor._output_path("/movies/clip.mp4", ".mp3", None)
        self.assertEqual(os.path.basename(p), "clip.mp3")
        self.assertEqual(os.path.dirname(p), os.path.abspath("/movies"))

    def test_output_path_custom_dir(self):
        p = extractor._output_path("/movies/clip.mkv", ".wav", "/out")
        self.assertEqual(p, os.path.join("/out", "clip.wav"))

    def test_formats_have_required_keys(self):
        for name, spec in extractor.FORMATS.items():
            self.assertIn("ext", spec)
            self.assertIn("codec", spec)
            self.assertTrue(spec["ext"].startswith("."))

    def test_unknown_format_raises(self):
        with self.assertRaises(extractor.ExtractError):
            extractor.extract_audio("whatever.mp4", fmt="OGG")


@unittest.skipUnless(HAS_FFMPEG, "ffmpeg/ffprobe が無いため実動画テストをスキップ")
class FfmpegIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.src = os.path.join(self.tmp, "sample.mp4")
        # 映像 + 音声付きの3秒テスト動画を生成
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "testsrc=duration=3:size=320x240:rate=15",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
                "-pix_fmt", "yuv420p", "-shortest", self.src,
            ],
            capture_output=True, check=True,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_extract_mp3(self):
        res = extractor.extract_audio(self.src, "MP3", self.tmp)
        self.assertTrue(os.path.isfile(res.output))
        self.assertTrue(res.output.endswith(".mp3"))
        self.assertGreater(os.path.getsize(res.output), 0)

    def test_extract_wav(self):
        res = extractor.extract_audio(self.src, "WAV", self.tmp)
        self.assertTrue(res.output.endswith(".wav"))
        self.assertGreater(os.path.getsize(res.output), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

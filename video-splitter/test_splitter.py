"""splitter.py のテスト。

ffmpeg があれば実際に短い動画を生成して分割まで検証する。
無ければ純粋なロジック部分（パス生成・時刻整形）のみ検証する。
"""

import os
import shutil
import subprocess
import tempfile
import unittest

import splitter


HAS_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


class PureLogicTests(unittest.TestCase):
    def test_format_timestamp(self):
        self.assertEqual(splitter.format_timestamp(0), "00:00:00")
        self.assertEqual(splitter.format_timestamp(5), "00:00:05")
        self.assertEqual(splitter.format_timestamp(65), "00:01:05")
        self.assertEqual(splitter.format_timestamp(3661), "01:01:01")
        self.assertEqual(splitter.format_timestamp(-3), "00:00:00")

    def test_output_paths_default_dir(self):
        p1, p2 = splitter._output_paths("/movies/clip.mp4", None)
        self.assertEqual(os.path.basename(p1), "clip_part1.mp4")
        self.assertEqual(os.path.basename(p2), "clip_part2.mp4")
        self.assertEqual(os.path.dirname(p1), os.path.abspath("/movies"))

    def test_output_paths_custom_dir(self):
        p1, p2 = splitter._output_paths("/movies/clip.mkv", "/out")
        self.assertEqual(p1, os.path.join("/out", "clip_part1.mkv"))
        self.assertEqual(p2, os.path.join("/out", "clip_part2.mkv"))

    def test_output_paths_no_extension(self):
        p1, _ = splitter._output_paths("/movies/clip", None)
        self.assertTrue(p1.endswith("clip_part1.mp4"))

    def test_get_duration_missing_file(self):
        with self.assertRaises(splitter.SplitterError):
            splitter.get_duration("/no/such/file.mp4")


@unittest.skipUnless(HAS_FFMPEG, "ffmpeg/ffprobe が無いため実動画テストをスキップ")
class FfmpegIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.src = os.path.join(self.tmp, "sample.mp4")
        # 4秒のテスト動画を生成
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "testsrc=duration=4:size=320x240:rate=15",
                "-pix_fmt", "yuv420p", self.src,
            ],
            capture_output=True, check=True,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_get_duration(self):
        d = splitter.get_duration(self.src)
        self.assertAlmostEqual(d, 4.0, delta=0.5)

    def test_split_in_half(self):
        res = splitter.split_in_half(self.src, reencode=True)
        self.assertTrue(os.path.isfile(res.part1))
        self.assertTrue(os.path.isfile(res.part2))
        self.assertAlmostEqual(res.split_point, 2.0, delta=0.5)
        # 前半・後半それぞれが元のおよそ半分
        d1 = splitter.get_duration(res.part1)
        d2 = splitter.get_duration(res.part2)
        self.assertAlmostEqual(d1, 2.0, delta=0.7)
        self.assertAlmostEqual(d2, 2.0, delta=0.7)


if __name__ == "__main__":
    unittest.main(verbosity=2)

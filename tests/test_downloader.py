import os
import sys
import tempfile
import unittest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from downloader import (  # noqa: E402
    DownloadRequest,
    DownloadValidationError,
    build_ytdlp_options,
    is_youtube_url,
    sanitize_filename_template,
    validate_request,
)
from ffmpeg_locator import resolve_ffmpeg_path  # noqa: E402


class DownloaderValidationTest(unittest.TestCase):
    def test_accepts_youtube_hosts(self):
        valid_urls = [
            "https://www.youtube.com/watch?v=abc123",
            "https://music.youtube.com/watch?v=abc123",
            "https://youtu.be/abc123",
            "https://www.youtube-nocookie.com/embed/abc123",
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_youtube_url(url))

    def test_rejects_non_youtube_hosts(self):
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://youtube.com/watch?v=abc123",
            "https://youtube.com.evil.test/watch?v=abc123",
            "https://example.com/watch?v=abc123",
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(is_youtube_url(url))

    def test_rejects_wrong_quality_for_audio(self):
        request = DownloadRequest(
            url="https://www.youtube.com/watch?v=abc123",
            output_dir=tempfile.gettempdir(),
            media_format="mp3",
            quality="1080p",
        )

        with self.assertRaises(DownloadValidationError):
            validate_request(request)


class FilenameSanitizationTest(unittest.TestCase):
    def test_sanitizes_path_traversal_and_windows_invalid_chars(self):
        sanitized = sanitize_filename_template(r"..\evil/name:bad?.%(ext)s")

        self.assertNotIn("\\", sanitized)
        self.assertNotIn("/", sanitized)
        self.assertNotIn(":", sanitized)
        self.assertNotIn("?", sanitized)
        self.assertTrue(sanitized.endswith(".%(ext)s"))

    def test_placeholder_becomes_default_name(self):
        self.assertEqual(sanitize_filename_template("ex: minha_musica.%(ext)s"), "")


class YtdlpOptionsTest(unittest.TestCase):
    def test_builds_audio_options(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            request = DownloadRequest(
                url="https://www.youtube.com/watch?v=abc123",
                output_dir=tmpdir,
                media_format="mp3",
                quality="320kbps",
                custom_name="minha musica.%(ext)s",
            )

            options = build_ytdlp_options(request, ffmpeg_path="C:/ffmpeg/bin")

        self.assertEqual(options["format"], "bestaudio/best")
        self.assertEqual(options["ffmpeg_location"], "C:/ffmpeg/bin")
        self.assertEqual(options["postprocessors"][0]["preferredcodec"], "mp3")
        self.assertEqual(options["postprocessors"][0]["preferredquality"], "320")
        self.assertTrue(options["outtmpl"].endswith("minha musica.%(ext)s"))
        self.assertTrue(options["noplaylist"])

    def test_builds_video_options(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            request = DownloadRequest(
                url="https://youtu.be/abc123",
                output_dir=tmpdir,
                media_format="mp4",
                quality="720p",
            )

            options = build_ytdlp_options(request)

        self.assertEqual(
            options["format"],
            "bestvideo[height<=720]+bestaudio/best[height<=720]",
        )
        self.assertEqual(options["merge_output_format"], "mp4")
        self.assertTrue(options["outtmpl"].endswith("%(title)s.%(ext)s"))


class FfmpegLocatorTest(unittest.TestCase):
    def test_resolves_full_build_layout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ffmpeg_bin = os.path.join(
                tmpdir,
                "bin",
                "ffmpeg",
                "ffmpeg-7.1-full_build",
                "bin",
            )
            os.makedirs(ffmpeg_bin)

            self.assertEqual(resolve_ffmpeg_path(tmpdir), ffmpeg_bin)

    def test_resolves_direct_bin_layout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ffmpeg_bin = os.path.join(tmpdir, "bin", "ffmpeg", "bin")
            os.makedirs(ffmpeg_bin)

            self.assertEqual(resolve_ffmpeg_path(tmpdir), ffmpeg_bin)


if __name__ == "__main__":
    unittest.main()

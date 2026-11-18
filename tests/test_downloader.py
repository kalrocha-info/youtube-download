import os
from queue import Queue
import sys
import tempfile
from threading import Event, Thread
from types import SimpleNamespace
import unittest
from unittest.mock import patch


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from youtube_download.downloader import (  # noqa: E402
    DownloadDestinationError,
    DownloadCancelled,
    DownloadRequest,
    DownloadValidationError,
    build_ytdlp_options,
    is_youtube_url,
    run_download,
    sanitize_filename_template,
    validate_request,
)
from youtube_download.ffmpeg_locator import resolve_ffmpeg_path  # noqa: E402
from youtube_download.app import abrir_pasta_destino, baixar_thread  # noqa: E402


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

    def test_sets_explicit_paths_for_available_js_runtimes(self):
        runtime_paths = {
            "deno": None,
            "node": r"C:\tools\nodejs\node.exe",
            "quickjs": None,
            "bun": None,
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            request = DownloadRequest(
                url="https://youtu.be/abc123",
                output_dir=tmpdir,
                media_format="mp4",
                quality="720p",
            )
            with patch(
                "youtube_download.downloader.shutil.which",
                side_effect=runtime_paths.get,
            ):
                options = build_ytdlp_options(request)

        self.assertEqual(
            options["js_runtimes"],
            {"node": {"path": r"C:\tools\nodejs\node.exe"}},
        )

    def test_disables_automatic_js_runtime_lookup_when_none_are_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            request = DownloadRequest(
                url="https://youtu.be/abc123",
                output_dir=tmpdir,
                media_format="mp4",
                quality="720p",
            )
            with patch("youtube_download.downloader.shutil.which", return_value=None):
                options = build_ytdlp_options(request)

        self.assertEqual(options["js_runtimes"], {})

    def test_reports_destination_creation_errors_separately(self):
        request = DownloadRequest(
            url="https://youtu.be/abc123",
            output_dir="C:\\unwritable",
            media_format="mp4",
            quality="720p",
        )
        with patch(
            "youtube_download.downloader.os.makedirs",
            side_effect=PermissionError("access denied"),
        ):
            with self.assertRaises(DownloadDestinationError):
                build_ytdlp_options(request)

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


class ExistingOutputTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.request = DownloadRequest(
            url="https://youtu.be/abc123",
            output_dir=self.tempdir.name,
            media_format="mp3",
            quality="320kbps",
        )
        self.output_path = os.path.join(self.tempdir.name, "Existing title.mp3")
        with open(self.output_path, "w", encoding="utf-8") as output_file:
            output_file.write("old audio")

    def _fake_ytdlp_class(self, handle_download):
        request = self.request

        class FakeYoutubeDL:
            def __init__(self, options):
                self.options = options

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def prepare_filename(self, info_dict):
                return os.path.join(
                    request.output_dir,
                    f"{info_dict['title']}.{info_dict['ext']}",
                )

            def download(self, _urls):
                match_filter = self.options["match_filter"]
                info_dict = {"title": "Existing title", "ext": "webm"}
                match_filter(info_dict, incomplete=True)
                handle_download(match_filter, info_dict)

        return FakeYoutubeDL

    def test_prompts_for_existing_converted_audio_and_proceeds_when_accepted(self):
        prompted_paths = []
        fake_module = SimpleNamespace(
            YoutubeDL=self._fake_ytdlp_class(
                lambda match_filter, info: match_filter(info, incomplete=False)
            )
        )
        with patch.dict(sys.modules, {"yt_dlp": fake_module}):
            run_download(
                self.request,
                confirm_overwrite=lambda path: prompted_paths.append(path) or True,
            )

        self.assertEqual(prompted_paths, [self.output_path])

    def test_declining_overwrite_cancels_download(self):
        fake_module = SimpleNamespace(
            YoutubeDL=self._fake_ytdlp_class(
                lambda match_filter, info: match_filter(info, incomplete=False)
            )
        )
        with patch.dict(sys.modules, {"yt_dlp": fake_module}):
            with self.assertRaises(DownloadCancelled):
                run_download(self.request, confirm_overwrite=lambda _path: False)


class DownloadWorkerTest(unittest.TestCase):
    def setUp(self):
        self.request = DownloadRequest(
            url="https://www.youtube.com/watch?v=abc123",
            output_dir=tempfile.gettempdir(),
            media_format="mp3",
            quality="320kbps",
        )

    def test_queues_progress_and_completion_events(self):
        events = Queue()
        continue_event = Event()
        continue_event.set()

        def fake_download(_request, _ffmpeg_path, progress_hook, _confirm_overwrite):
            progress_hook({
                "status": "downloading",
                "_percent_str": "50%",
                "_speed_str": "1MiB/s",
            })
            progress_hook({"status": "finished"})

        with patch("youtube_download.app.run_download", side_effect=fake_download):
            baixar_thread(self.request, Event(), continue_event, events)

        queued_events = [events.get_nowait() for _ in range(events.qsize())]
        self.assertEqual(
            [event for event, _ in queued_events],
            ["progress", "progress", "success", "complete"],
        )
        self.assertIn("50%", queued_events[0][1])

    def test_waits_for_ui_overwrite_confirmation(self):
        events = Queue()
        continue_event = Event()
        continue_event.set()
        confirmations = []

        def fake_download(_request, _ffmpeg_path, _progress_hook, confirm_overwrite):
            confirmations.append(confirm_overwrite("existing.mp3"))

        with patch("youtube_download.app.run_download", side_effect=fake_download):
            worker = Thread(
                target=baixar_thread,
                args=(self.request, Event(), continue_event, events),
            )
            worker.start()

            event, (output_path, response_queue) = events.get(timeout=1)
            self.assertEqual(event, "confirm_overwrite")
            self.assertEqual(output_path, "existing.mp3")
            response_queue.put(True)
            worker.join(timeout=1)

        self.assertFalse(worker.is_alive())
        self.assertEqual(confirmations, [True])

    def test_queues_cancellation_when_requested(self):
        events = Queue()
        cancel_event = Event()
        cancel_event.set()
        continue_event = Event()
        continue_event.set()

        def fake_download(_request, _ffmpeg_path, progress_hook, _confirm_overwrite):
            progress_hook({"status": "downloading"})

        with patch("youtube_download.app.run_download", side_effect=fake_download):
            baixar_thread(self.request, cancel_event, continue_event, events)

        queued_events = [events.get_nowait() for _ in range(events.qsize())]
        self.assertEqual(
            [event for event, _ in queued_events],
            ["cancelled", "complete"],
        )

    def test_queues_other_os_errors_as_download_errors(self):
        events = Queue()
        continue_event = Event()
        continue_event.set()

        with patch(
            "youtube_download.app.run_download",
            side_effect=OSError("[WinError 448] untrusted mount point"),
        ):
            baixar_thread(self.request, Event(), continue_event, events)

        queued_events = [events.get_nowait() for _ in range(events.qsize())]
        self.assertEqual(
            [event for event, _ in queued_events],
            ["download_error", "complete"],
        )

    def test_pauses_at_progress_hook_until_resumed(self):
        events = Queue()
        cancel_event = Event()
        continue_event = Event()
        download_started = Event()

        def fake_download(_request, _ffmpeg_path, progress_hook, _confirm_overwrite):
            download_started.set()
            progress_hook({"status": "downloading"})

        with patch("youtube_download.app.run_download", side_effect=fake_download):
            worker = Thread(
                target=baixar_thread,
                args=(self.request, cancel_event, continue_event, events),
            )
            worker.start()
            self.assertTrue(download_started.wait(timeout=1))
            self.assertEqual(events.get(timeout=1)[0], "paused")
            self.assertTrue(worker.is_alive())

            continue_event.set()
            worker.join(timeout=1)

        self.assertFalse(worker.is_alive())
        queued_events = [events.get_nowait() for _ in range(events.qsize())]
        self.assertEqual(
            [event for event, _ in queued_events],
            ["resumed", "progress", "success", "complete"],
        )

    def test_cancellation_releases_a_paused_worker(self):
        events = Queue()
        cancel_event = Event()
        continue_event = Event()

        def fake_download(_request, _ffmpeg_path, progress_hook, _confirm_overwrite):
            progress_hook({"status": "downloading"})

        with patch("youtube_download.app.run_download", side_effect=fake_download):
            worker = Thread(
                target=baixar_thread,
                args=(self.request, cancel_event, continue_event, events),
            )
            worker.start()
            self.assertEqual(events.get(timeout=1)[0], "paused")
            cancel_event.set()
            continue_event.set()
            worker.join(timeout=1)

        self.assertFalse(worker.is_alive())
        queued_events = [events.get_nowait() for _ in range(events.qsize())]
        self.assertEqual(
            [event for event, _ in queued_events],
            ["cancelled", "complete"],
        )


class DestinationFolderTest(unittest.TestCase):
    def test_opens_selected_destination_folder(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with (
                patch("youtube_download.app.PASTA_SAIDA", output_dir),
                patch("youtube_download.app.os.startfile", create=True) as startfile,
            ):
                abrir_pasta_destino()

        startfile.assert_called_once_with(output_dir)


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

    def test_prefers_direct_bin_over_legacy_full_build(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ffmpeg_dir = os.path.join(tmpdir, "bin", "ffmpeg")
            direct_bin = os.path.join(ffmpeg_dir, "bin")
            legacy_bin = os.path.join(ffmpeg_dir, "ffmpeg-7.1-full_build", "bin")
            os.makedirs(direct_bin)
            os.makedirs(legacy_bin)

            self.assertEqual(resolve_ffmpeg_path(tmpdir), direct_bin)


if __name__ == "__main__":
    unittest.main()

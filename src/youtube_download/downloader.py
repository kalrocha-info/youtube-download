import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse


AUDIO_FORMATS = {"mp3", "m4a", "wav", "flac"}
VIDEO_FORMATS = {"mp4", "webm"}
AUDIO_QUALITIES = {"320kbps", "256kbps", "192kbps", "128kbps"}
VIDEO_QUALITIES = {"Melhor qualidade", "1080p", "720p", "480p"}
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class DownloadCancelled(Exception):
    """Raised when the user requests download cancellation."""


class DownloadValidationError(ValueError):
    """Raised when a download request is invalid."""


@dataclass(frozen=True)
class DownloadRequest:
    url: str
    output_dir: str
    media_format: str
    quality: str
    custom_name: str = ""


def is_youtube_url(url):
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()

    if parsed.scheme not in {"http", "https"}:
        return False

    if not host:
        return False

    return (
        host == "youtu.be"
        or host == "youtube.com"
        or host.endswith(".youtube.com")
        or host == "youtube-nocookie.com"
        or host.endswith(".youtube-nocookie.com")
    )


def sanitize_filename_template(name):
    cleaned = name.strip()

    if not cleaned or cleaned.lower().startswith("ex:"):
        return ""

    cleaned = INVALID_FILENAME_CHARS.sub("_", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")

    if cleaned in {"", ".", ".."}:
        return ""

    return cleaned


def validate_request(request):
    if not request.url.strip():
        raise DownloadValidationError("Cole o link do YouTube primeiro.")

    if not is_youtube_url(request.url):
        raise DownloadValidationError("Informe um link válido do YouTube ou YouTube Music.")

    if request.media_format not in AUDIO_FORMATS | VIDEO_FORMATS:
        raise DownloadValidationError("Formato de saída inválido.")

    if request.media_format in AUDIO_FORMATS and request.quality not in AUDIO_QUALITIES:
        raise DownloadValidationError("Qualidade de áudio inválida para o formato escolhido.")

    if request.media_format in VIDEO_FORMATS and request.quality not in VIDEO_QUALITIES:
        raise DownloadValidationError("Qualidade de vídeo inválida para o formato escolhido.")


def build_ytdlp_options(request, ffmpeg_path=None, progress_hook=None):
    validate_request(request)

    os.makedirs(request.output_dir, exist_ok=True)
    custom_name = sanitize_filename_template(request.custom_name)
    filename_template = custom_name or "%(title)s.%(ext)s"

    options = {
        "outtmpl": os.path.join(request.output_dir, filename_template),
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
    }

    if ffmpeg_path:
        options["ffmpeg_location"] = ffmpeg_path

    if progress_hook:
        options["progress_hooks"] = [progress_hook]

    if request.media_format in AUDIO_FORMATS:
        options["format"] = "bestaudio/best"
        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": request.media_format,
                "preferredquality": request.quality.replace("kbps", ""),
            }
        ]
        return options

    quality_formats = {
        "Melhor qualidade": "bestvideo+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    }

    options["format"] = quality_formats[request.quality]
    options["merge_output_format"] = request.media_format
    return options


def run_download(request, ffmpeg_path=None, progress_hook=None):
    import yt_dlp

    options = build_ytdlp_options(request, ffmpeg_path, progress_hook)
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([request.url.strip()])

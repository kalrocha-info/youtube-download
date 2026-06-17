import os
import sys


def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def resolve_ffmpeg_path(base_path=None):
    base_path = base_path or get_base_path()
    ffmpeg_dir = os.path.join(base_path, "bin", "ffmpeg")

    if not os.path.exists(ffmpeg_dir):
        return None

    for folder in os.listdir(ffmpeg_dir):
        if folder.startswith("ffmpeg-") and "full_build" in folder:
            candidate = os.path.join(ffmpeg_dir, folder, "bin")
            if os.path.exists(candidate):
                return candidate

    direct_bin = os.path.join(ffmpeg_dir, "bin")
    if os.path.exists(direct_bin):
        return direct_bin

    return None

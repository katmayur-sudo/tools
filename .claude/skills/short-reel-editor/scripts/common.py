"""Shared helpers: ffmpeg/ffprobe lookup (override with FFMPEG / FFPROBE env vars)."""
import os, shutil, subprocess

FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FP = os.environ.get("FFPROBE") or shutil.which("ffprobe") or "ffprobe"


def duration(path):
    out = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout
    return float(out)


def to_wav16(src, dst):
    subprocess.run([FF, "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", dst], check=True)

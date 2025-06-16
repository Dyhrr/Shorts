import json
import logging
import shutil
import subprocess
from pathlib import Path


def check_ffmpeg() -> None:
    """Ensure ffmpeg and ffprobe are available."""
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise EnvironmentError(f"'{tool}' not found in PATH")


def probe_duration(path: Path) -> float:
    """Return duration of media file in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        logging.error("ffprobe failed: %s", result.stderr)
        raise RuntimeError(f"ffprobe failed: {result.stderr}")
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])

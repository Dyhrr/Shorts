import json
import logging
import shutil
import subprocess
from pathlib import Path


CONFIG_PATH = Path.home() / ".shortssplit.json"


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


def load_config() -> dict:
    """Return configuration from ``CONFIG_PATH`` if present."""
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:  # pragma: no cover - best effort
            logging.warning("Failed to read config: %s", exc)
    return {}


def save_config(cfg: dict) -> None:
    """Write ``cfg`` to ``CONFIG_PATH``."""
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception as exc:  # pragma: no cover - best effort
        logging.warning("Failed to write config: %s", exc)

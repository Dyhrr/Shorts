from pathlib import Path
from typing import List


def load_srt(path: Path) -> List[str]:
    """Load SRT file lines."""
    return path.read_text(encoding="utf-8").splitlines()


def save_srt(lines: List[str], out_path: Path) -> None:
    out_path.write_text("\n".join(lines), encoding="utf-8")

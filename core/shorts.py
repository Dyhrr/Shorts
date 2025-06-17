from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from typing import Callable, Dict

from .ffmpeg_handler import build_stack
from .subtitle_utils import save_ass
from .whisper_wrapper import transcribe


def generate_short(
    top: Path | str,
    bottom: Path | str,
    model_size: str = "base",
    *,
    device: str = "auto",
    style: Dict[str, str | int] | None = None,
    output_path: Path | str | None = None,
    progress: Callable[[str], None] | None = None,
) -> Path:
    """
    Create a short stacked video using the two provided clips.

    Parameters
    ----------
    top: Path | str
        Path to the top clip which will be transcribed.
    bottom: Path | str
        Path to the bottom clip.
    model_size: str, optional
        Whisper model size. Defaults to "base".
    device: str, optional
        Device for Whisper ("cpu", "cuda", or "auto"). Defaults to "auto".

    Returns
    -------
    Path
        The path to the generated "output.mp4" file.
    """
    top_path = Path(top)
    bottom_path = Path(bottom)
    if output_path is None:
        output_path = top_path.parent / "output.mp4"
    else:
        output_path = Path(output_path)

    if progress:
        progress("Transcribing...")
    logging.info("Transcribing top clip: %s", top_path)
    cues = transcribe(top_path, model_size=model_size, device=device)

    with tempfile.NamedTemporaryFile(suffix=".ass", delete=False) as tmp:
        subtitle_path = Path(tmp.name)
        save_ass(cues, subtitle_path, style=style)

    try:
        if progress:
            progress("Encoding...")
        logging.info("Building stacked video -> %s", output_path)
        build_stack(top_path, bottom_path, subtitle_path, output_path)
    finally:
        subtitle_path.unlink(missing_ok=True)

    if progress:
        progress("Done")

    return output_path

import logging
from pathlib import Path
from typing import List

from faster_whisper import WhisperModel


_model_cache = {}


def transcribe(path: Path, model_size: str = "base") -> List[str]:
    """Transcribe audio and return SRT lines."""
    logging.info("Transcribing %s", path)
    if model_size not in _model_cache:
        _model_cache[model_size] = WhisperModel(model_size, device="auto")
    model = _model_cache[model_size]
    segments, _ = model.transcribe(str(path), beam_size=5)
    srt_lines = []
    for i, segment in enumerate(segments, start=1):
        start = segment.start
        end = segment.end
        text = segment.text.strip()
        srt_lines.append(f"{i}\n{_format_time(start)} --> {_format_time(end)}\n{text}\n")
    return srt_lines


def _format_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:06.3f}".replace(".", ",")

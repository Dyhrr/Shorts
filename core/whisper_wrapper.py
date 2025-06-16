from pathlib import Path
from typing import List
from faster_whisper import WhisperModel


def transcribe(path: Path, model_size: str = "base") -> List[str]:
    """Transcribe audio and return SRT lines."""
    model = WhisperModel(model_size, device="auto")
    segments, _ = model.transcribe(str(path), beam_size=5)
    srt_lines = []
    for i, segment in enumerate(segments, start=1):
        start = segment.start
        end = segment.end
        text = segment.text.strip()
        srt_lines.append(
            f"{i}\n{_format_time(start)} --> {_format_time(end)}\n{text}\n"
        )
    return srt_lines


def save_srt(lines: List[str], out_path: Path) -> None:
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _format_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:06.3f}".replace(".", ",")

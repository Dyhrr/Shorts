import logging
from pathlib import Path
from typing import List

from faster_whisper import WhisperModel


_model_cache = {}


def transcribe(
    path: Path, model_size: str = "base", device: str = "auto"
) -> List[str]:
    """Transcribe audio and return SRT lines.

    Parameters
    ----------
    path: Path
        Media file to transcribe.
    model_size: str, optional
        Whisper model size. Defaults to ``"base"``.
    device: str, optional
        Device for inference (``"cpu"`` or ``"cuda"``/``"auto"``). Defaults to
        ``"auto"``. If initialization fails (e.g., missing GPU libraries), the
        function falls back to CPU.
    """
    logging.info("Transcribing %s", path)
    cache_key = (model_size, device)
    if cache_key not in _model_cache:
        try:
            _model_cache[cache_key] = WhisperModel(model_size, device=device)
        except Exception as exc:  # GPU may fail due to missing CUDA/CUDNN
            logging.warning(
                "Whisper model failed on %s (%s). Falling back to CPU.", device, exc
            )
            cache_key = (model_size, "cpu")
            if cache_key not in _model_cache:
                _model_cache[cache_key] = WhisperModel(model_size, device="cpu")
    model = _model_cache[cache_key]
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

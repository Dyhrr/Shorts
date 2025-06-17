import logging
import os
from pathlib import Path
from typing import List, Tuple

from faster_whisper import WhisperModel


_model_cache = {}


def transcribe(
    path: Path, model_size: str = "base", device: str = "auto"
) -> List[Tuple[float, float, str]]:
    """Transcribe audio and return subtitle cues.

    Each subtitle cue contains up to three words for readability and is timed
    using word-level timestamps.

    Parameters
    ----------
    path: Path
        Media file to transcribe.
    model_size: str, optional
        Whisper model size. Defaults to ``"base"``.
    device: str, optional
        Device for inference (``"cpu"`` or ``"cuda"``/``"auto"``). Defaults to
        ``"auto"``. Set the environment variable ``WHISPER_DEVICE`` to override
        this value. If initialization fails (e.g., missing GPU libraries), the
        function falls back to CPU.
    """
    env_device = os.getenv("WHISPER_DEVICE")
    if env_device:
        device = env_device
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
    segments, _ = model.transcribe(
        str(path), beam_size=5, word_timestamps=True
    )

    max_words = 3
    cues = []
    word_group = []
    for segment in segments:
        if segment.words is None:
            continue
        for word in segment.words:
            word_group.append(word)
            if len(word_group) == max_words:
                start = word_group[0].start
                end = word_group[-1].end
                text = " ".join(w.word for w in word_group).strip()
                cues.append((start, end, text))
                word_group = []

    if word_group:
        start = word_group[0].start
        end = word_group[-1].end
        text = " ".join(w.word for w in word_group).strip()
        cues.append((start, end, text))

    # Sort cues by start time in case segments are not sequential
    cues.sort(key=lambda c: c[0])

    if not cues:
        logging.warning("No speech detected in top clip")

    return cues

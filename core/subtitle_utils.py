from pathlib import Path
from typing import List, Tuple


def load_srt(path: Path) -> List[str]:
    """Load SRT file lines."""
    return path.read_text(encoding="utf-8").splitlines()


def save_srt(lines: List[str], out_path: Path) -> None:
    out_path.write_text("\n".join(lines), encoding="utf-8")


def cap_words_per_cue(
    cues: List[Tuple[float, float, str]], max_words: int = 3
) -> List[Tuple[float, float, str]]:
    """Split cue text so each cue has at most ``max_words`` words.

    Parameters
    ----------
    cues:
        List of ``(start_time, end_time, text)`` tuples.
    max_words:
        Maximum number of words allowed per cue.

    Returns
    -------
    list of tuples
        New cues with evenly distributed timings.
    """

    new_cues: List[Tuple[float, float, str]] = []
    for start, end, text in cues:
        words = text.split()
        if len(words) <= max_words:
            new_cues.append((start, end, text))
            continue

        n_chunks = (len(words) + max_words - 1) // max_words
        duration = (end - start) / n_chunks

        for i in range(n_chunks):
            chunk_words = words[i * max_words : (i + 1) * max_words]
            chunk_text = " ".join(chunk_words)
            chunk_start = start + i * duration
            chunk_end = start + (i + 1) * duration
            new_cues.append((chunk_start, chunk_end, chunk_text))

    return new_cues

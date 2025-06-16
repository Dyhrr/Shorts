import subprocess
from pathlib import Path

from .utils import probe_duration

def build_stack(
    top: Path,
    bottom: Path,
    subtitle: Path,
    out_path: Path,
    font_size: int = 24,
    font_color: str = "white",
) -> None:
    """Create the stacked video with subtitles burned into the top clip."""
    duration = probe_duration(top)
    filter_complex = (
        f"[0:v]scale=1080:-2,crop=1080:960,subtitles={subtitle}:force_style='Fontsize={font_size},PrimaryColour=&H{_color_hex(font_color)}&'[top];"
        f"[1:v]scale=1080:-2,crop=1080:960,loop=loop=-1:size=1:start=0,trim=duration={duration}[bottom];"
        f"[top][bottom]vstack=inputs=2[v]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(top),
        "-stream_loop",
        "-1",
        "-i",
        str(bottom),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "0:a",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-c:a",
        "aac",
        "-af","loudnorm"
        "-shortest",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)


def _color_hex(name: str) -> str:
    colors = {
        "white": "FFFFFF",
        "black": "000000",
        "yellow": "FFFF00",
        "red": "FF0000",
    }
    return colors.get(name.lower(), "FFFFFF")

import logging
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
        f"[0:v]scale=1080:-2,crop=1080:960,subtitles='{_escape_path(subtitle)}':force_style='Fontsize={font_size},PrimaryColour=&H{_color_hex(font_color)}&,Alignment=2,OutlineColour=&H000000&,BorderStyle=1,Outline=2'[top];"
        f"[1:v]loop=loop=-1:size=1:start=0,trim=duration={duration},setpts=PTS-STARTPTS,scale=1080:-2,crop=1080:960[bottom];"
        f"[top][bottom]vstack=inputs=2[v]"
    )

    base_cmd = [
        "ffmpeg",
        "-y",
        "-hwaccel",
        "auto",
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
        "-preset",
        "fast",
        "-c:a",
        "aac",
        "-af",
        "loudnorm",
        "-shortest",
        "-movflags",
        "+faststart",
    ]

    cmd_nvenc = base_cmd + ["-c:v", "h264_nvenc", str(out_path)]
    cmd_x264 = base_cmd + ["-c:v", "libx264", str(out_path)]

    logging.debug("Running ffmpeg command: %s", " ".join(cmd_nvenc))
    result = subprocess.run(cmd_nvenc, stderr=subprocess.PIPE)
    if result.returncode != 0:
        logging.warning("h264_nvenc failed, falling back to libx264")
        logging.debug(result.stderr.decode())
        subprocess.run(cmd_x264, check=True)


def _color_hex(name: str) -> str:
    colors = {
        "white": "FFFFFF",
        "black": "000000",
        "yellow": "FFFF00",
        "red": "FF0000",
    }
    return colors.get(name.lower(), "FFFFFF")


def _escape_path(path: Path) -> str:
    """Return POSIX path with characters escaped for ffmpeg filter usage."""
    p = path.as_posix()
    return p.replace("'", "\\'")

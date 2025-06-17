import logging
import subprocess
import re
from pathlib import Path

from .utils import probe_duration


def build_stack(
    top: Path,
    bottom: Path,
    subtitle: Path,
    out_path: Path,
) -> None:
    """Create the stacked video with subtitles burned into the top clip."""
    duration = probe_duration(top)

    # Prepare subtitle path: forward slashes + escape the "C:" drive-colon
    sub_path = subtitle.as_posix()
    sub_path = re.sub(r'^([A-Za-z]):', r'\1\\:', sub_path, count=1)

    # ASS subtitles
    sub_filter = f"ass='{sub_path}'"

    # Scale→crop→subtitles on top; scale→crop→trim→setpts on bottom; then vstack
    filter_complex = (
        f"[0:v]scale=1080:-2,crop=1080:960,{sub_filter}[top];"
        f"[1:v]scale=1080:-2,crop=1080:960,trim=duration={duration},"
        "setpts=PTS-STARTPTS[bottom];"
        "[top][bottom]vstack=inputs=2[v]"
    )

    base_cmd = [
        "ffmpeg", "-y", "-hwaccel", "auto",
        "-i", str(top),
        "-stream_loop", "-1", "-i", str(bottom),
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "0:a",
        "-c:a", "aac",
        "-af", "loudnorm",
        "-shortest",
        "-movflags", "+faststart",
    ]

    cmd_nvenc = base_cmd + ["-c:v", "h264_nvenc", str(out_path)]
    cmd_x264  = base_cmd + ["-c:v", "libx264",    str(out_path)]

    logging.debug("Running ffmpeg (NVENC): %s", " ".join(cmd_nvenc))
    result = subprocess.run(cmd_nvenc, stderr=subprocess.PIPE)
    if result.returncode != 0:
        logging.warning("h264_nvenc failed (exit %d), falling back to libx264", result.returncode)
        logging.debug(result.stderr.decode())
        subprocess.run(cmd_x264, check=True)


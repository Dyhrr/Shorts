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
    *,
    resolution: tuple[int, int] = (1080, 1920),
) -> None:
    """Create the stacked video with subtitles burned into the top clip."""
    duration = probe_duration(top)

    # Prepare subtitle path: forward slashes + escape the "C:" drive-colon
    sub_path = subtitle.as_posix()
    sub_path = re.sub(r'^([A-Za-z]):', r'\1\\:', sub_path, count=1)
    sub_path = sub_path.replace("'", "\\'")

    # ASS subtitles
    sub_filter = f"ass='{sub_path}'"

    # Scale→crop→subtitles on top; scale→crop→trim→setpts on bottom; then vstack
    width, height = resolution
    half = height // 2
    filter_complex = (
        f"[0:v]scale={width}:-2,crop={width}:{half},{sub_filter}[top];"
        f"[1:v]scale={width}:-2,crop={width}:{half},trim=duration={duration},"
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
    try:
        subprocess.run(cmd_nvenc, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        logging.warning(
            "h264_nvenc failed (exit %d), falling back to libx264",
            exc.returncode,
        )
        logging.debug(exc.stderr.decode())
        try:
            subprocess.run(cmd_x264, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as exc2:
            logging.error("ffmpeg failed: %s", exc2.stderr.decode())
            raise RuntimeError("ffmpeg encoding failed") from exc2


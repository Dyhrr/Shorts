from pathlib import Path
import subprocess

import pytest

from core import ffmpeg_handler


class DummyCompleted:
    def __init__(self):
        self.stderr = b""


def test_build_stack_fallback(monkeypatch, tmp_path):
    top = tmp_path / "top.mp4"
    bottom = tmp_path / "bottom.mp4"
    sub = tmp_path / "sub.ass"
    out = tmp_path / "out.mp4"
    for f in (top, bottom, sub):
        f.write_text("dummy")

    calls = []

    def fake_run(cmd, check=True, stderr=None):
        calls.append(cmd)
        if "h264_nvenc" in cmd:
            raise subprocess.CalledProcessError(returncode=1, cmd=cmd, stderr=b"fail")
        return DummyCompleted()

    monkeypatch.setattr(ffmpeg_handler, "probe_duration", lambda p: 1.0)
    monkeypatch.setattr(subprocess, "run", fake_run)

    ffmpeg_handler.build_stack(top, bottom, sub, out)

    assert any("h264_nvenc" in c for c in calls[0])
    assert any("libx264" in c for c in calls[1])

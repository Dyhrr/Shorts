import types
import subprocess
from pathlib import Path
import sys
import pytest

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Provide dummy faster_whisper module with WhisperModel attribute (for imports elsewhere)
stub = types.ModuleType('faster_whisper')
stub.WhisperModel = object
sys.modules.setdefault('faster_whisper', stub)

import core.ffmpeg_handler as ffmpeg_handler


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
        if any("h264_nvenc" in arg for arg in cmd):
            raise subprocess.CalledProcessError(returncode=1, cmd=cmd, stderr=b"fail")
        return DummyCompleted()

    monkeypatch.setattr(ffmpeg_handler, "probe_duration", lambda p: 1.0)
    monkeypatch.setattr(subprocess, "run", fake_run)

    ffmpeg_handler.build_stack(top, bottom, sub, out)

    assert any("h264_nvenc" in c for c in calls[0]), "First attempt should use NVENC"
    assert any("libx264" in c for c in calls[1]), "Fallback should use libx264"


def test_subtitle_path_escaping(monkeypatch):
    captured = {}

    def fake_run(cmd, check, stderr):
        captured['cmd'] = cmd
        class Result:
            returncode = 0
            stderr = b''
        return Result()

    monkeypatch.setattr(ffmpeg_handler, 'probe_duration', lambda _: 1)
    monkeypatch.setattr(subprocess, 'run', fake_run)

    top = Path('top.mp4')
    bottom = Path('bottom.mp4')
    subtitle = Path("te'st.ass")
    out = Path('out.mp4')

    ffmpeg_handler.build_stack(top, bottom, subtitle, out)

    cmd_str = ' '.join(captured['cmd'])
    assert "te\\'st.ass" in cmd_str, "Subtitle path should be properly escaped for ffmpeg"

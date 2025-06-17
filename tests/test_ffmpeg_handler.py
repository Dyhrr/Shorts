import types
import subprocess
from pathlib import Path
import sys

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Provide dummy faster_whisper module with WhisperModel attribute
stub = types.ModuleType('faster_whisper')
stub.WhisperModel = object
sys.modules.setdefault('faster_whisper', stub)

import core.ffmpeg_handler as ffmpeg_handler

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
    assert "te\\'st.ass" in cmd_str

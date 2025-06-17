import os
from pathlib import Path

import pytest

from core.subtitle_utils import _format_time, save_ass, hex_to_ass


def test_format_time_zero():
    assert _format_time(0) == "0:00:00.00"


def test_save_ass_creates_file(tmp_path):
    cues = [(0.0, 1.0, "hello")]
    out = tmp_path / "out.ass"
    save_ass(cues, out)
    assert out.exists()
    content = out.read_text()
    assert "Dialogue: 0" in content


def test_hex_to_ass():
    assert hex_to_ass("#112233") == "&H00332211"

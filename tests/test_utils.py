from pathlib import Path
import json
import shutil
import subprocess

import pytest

from core import utils


def test_validate_media_ok(tmp_path):
    f = tmp_path / "video.mp4"
    f.write_text("dummy")
    utils.validate_media(f)


def test_validate_media_bad_ext(tmp_path):
    f = tmp_path / "video.txt"
    f.write_text("dummy")
    with pytest.raises(ValueError):
        utils.validate_media(f)


def test_validate_media_missing(tmp_path):
    f = tmp_path / "missing.mp4"
    with pytest.raises(FileNotFoundError):
        utils.validate_media(f)


def test_load_save_config(monkeypatch, tmp_path):
    cfg_path = tmp_path / "config.json"
    monkeypatch.setattr(utils, "CONFIG_PATH", cfg_path)
    data = {"a": 1}
    utils.save_config(data)
    loaded = utils.load_config()
    assert loaded == data


def test_check_ffmpeg_missing(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda x: None)
    with pytest.raises(EnvironmentError):
        utils.check_ffmpeg()

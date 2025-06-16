"""Entry point for ShortsSplit."""
import logging

from core.utils import check_ffmpeg
from ui.mainwindow import run_app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    try:
        check_ffmpeg()
    except EnvironmentError as exc:
        logging.error(exc)
    else:
        run_app()

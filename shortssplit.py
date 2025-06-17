"""Entry point for ShortsSplit."""

import argparse
import logging

from core import generate_short, load_config, save_config
from core.utils import check_ffmpeg
from ui.mainwindow import run_app


def main() -> int:
    """Run ShortsSplit either via the GUI or the command line."""
    parser = argparse.ArgumentParser(description="Create vertical shorts")
    parser.add_argument("top", nargs="?", help="Top clip with audio")
    parser.add_argument("bottom", nargs="?", help="Bottom clip video")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-m", "--model", default="base", help="Whisper model size")
    parser.add_argument("-d", "--device", default="auto", help="Whisper device")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

    try:
        check_ffmpeg()
    except EnvironmentError as exc:
        logging.error(exc)
        return 1

    cfg = load_config()
    top = args.top or cfg.get("top_clip")
    bottom = args.bottom or cfg.get("bottom_clip")

    if top and bottom:
        out = generate_short(
            top,
            bottom,
            model_size=args.model,
            device=args.device,
            output_path=args.output,
            progress=logging.info,
        )
        save_config({"top_clip": top, "bottom_clip": bottom})
        print(out)
        return 0

    run_app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

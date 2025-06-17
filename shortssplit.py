"""Entry point for ShortsSplit."""

import argparse
import logging

from core import generate_short, load_config, save_config, __version__
from core.utils import check_ffmpeg
from ui.mainwindow import run_app


def parse_resolution(value: str) -> tuple[int, int]:
    """Return width/height tuple from ``value``.

    Parameters
    ----------
    value:
        String in ``WIDTHxHEIGHT`` format (e.g. ``"1080x1920"``).

    Raises
    ------
    ValueError
        If ``value`` is not in the expected format or contains non-numeric
        values.
    """
    try:
        w, h = value.lower().split("x")
        return int(w), int(h)
    except Exception as exc:  # pragma: no cover - user input validation
        raise ValueError(
            f"Invalid resolution '{value}'. Use WIDTHxHEIGHT like 1080x1920"
        ) from exc


def main() -> int:
    """Run ShortsSplit either via the GUI or the command line."""
    parser = argparse.ArgumentParser(description="Create vertical shorts")
    parser.add_argument("top", nargs="?", help="Top clip with audio")
    parser.add_argument("bottom", nargs="?", help="Bottom clip video")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-m", "--model", default="base", help="Whisper model size")
    parser.add_argument("-d", "--device", default="auto", help="Whisper device")
    parser.add_argument("--font", help="Subtitle font name")
    parser.add_argument("--font-size", type=int, help="Subtitle font size")
    parser.add_argument("--outline", type=int, help="Subtitle outline thickness")
    parser.add_argument(
        "-r",
        "--resolution",
        default=None,
        help="Output resolution WIDTHxHEIGHT (e.g. 1080x1920)",
    )
    parser.add_argument("--version", action="version", version=f"ShortsSplit {__version__}")
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
    res_str = args.resolution or cfg.get("resolution", "1080x1920")
    try:
        resolution = parse_resolution(res_str)
    except ValueError as exc:
        print(exc)
        return 1

    style = {}
    if args.font:
        style["FontName"] = args.font
    if args.font_size:
        style["FontSize"] = args.font_size
    if args.outline is not None:
        style["Outline"] = args.outline
    if not style:
        style = None

    if top and bottom:
        out = generate_short(
            top,
            bottom,
            model_size=args.model,
            device=args.device,
            style=style,
            output_path=args.output,
            progress=print,
            resolution=resolution,
        )
        save_config({"top_clip": top, "bottom_clip": bottom, "resolution": res_str})
        print(out)
        return 0

    run_app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

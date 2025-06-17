from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_STYLE: Dict[str, str | int] = {
    "FontName": "Arial",
    "FontSize": 36,
    "PrimaryColour": "&H00FFFFFF",
    "OutlineColour": "&H00000000",
    "BorderStyle": 1,
    "Outline": 2,
    "Shadow": 0,
    "Alignment": 2,
}


def save_ass(
    cues: List[Tuple[float, float, str]],
    out_path: Path,
    style: Dict[str, str | int] | None = None,
) -> None:
    """Write subtitle ``cues`` to ``out_path`` in ASS format."""
    if style is None:
        style = DEFAULT_STYLE

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "",
        "[V4+ Styles]",
        (
            "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,"
            "OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,"
            "ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
            "Alignment,MarginL,MarginR,MarginV,Encoding"
        ),
        (
            f"Style: Default,{style['FontName']},{style['FontSize']},"
            f"{style['PrimaryColour']},&H00000000,{style['OutlineColour']},"
            "&H00000000,0,0,0,0,100,100,0,0,"
            f"{style['BorderStyle']},{style['Outline']},{style['Shadow']},"
            f"{style['Alignment']},10,10,10,1"
        ),
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    for start, end, text in cues:
        lines.append(
            f"Dialogue: 0,{_format_time(start)},{_format_time(end)},Default,,0,0,0,,{text}"
        )

    out_path.write_text("\n".join(lines), encoding="utf-8")


def _format_time(seconds: float) -> str:
    """Return ASS-formatted timestamp ``H:MM:SS.cc``."""
    cs_total = int(round(seconds * 100))
    hrs, cs_total = divmod(cs_total, 3600 * 100)
    mins, cs_total = divmod(cs_total, 60 * 100)
    secs, cs = divmod(cs_total, 100)
    return f"{hrs}:{mins:02}:{secs:02}.{cs:02}"


def hex_to_ass(color: str) -> str:
    """Return ASS ``PrimaryColour`` from ``#RRGGBB`` ``color``."""
    if color.startswith("#"):
        color = color[1:]
    if len(color) != 6:
        raise ValueError("Color must be in #RRGGBB format")
    r, g, b = color[0:2], color[2:4], color[4:6]
    return f"&H00{b}{g}{r}"


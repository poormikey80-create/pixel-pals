#!/usr/bin/env python3
"""Pack a folder of equal-sized PNG frames into one sprite sheet plus an atlas.

Also lints every frame against a .gpl palette, because the single most common
way I ruin a sprite is leaving a soft brush on and shipping four almost-identical
shades of purple that no longer match anything else in the game.

    python build_sheet.py frames/ --out build/pals.png --cell 16
    python build_sheet.py frames/ --out build/pals.png --palette pixel-pals-16.gpl
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required. Install it with:  pip install pillow")

Color = tuple[int, int, int]


def load_palette(path: Path) -> set[Color]:
    """Read RGB triples out of a GIMP/Aseprite .gpl file."""
    colors: set[Color] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line[0].isalpha():
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            colors.add((int(parts[0]), int(parts[1]), int(parts[2])))
        except ValueError:
            continue
    if not colors:
        sys.exit(f"no colours parsed from {path}")
    return colors


def collect_frames(src: Path) -> list[Path]:
    frames = sorted(p for p in src.iterdir() if p.suffix.lower() == ".png")
    if not frames:
        sys.exit(f"no .png frames found in {src}")
    return frames


def lint_frame(image: Image.Image, palette: set[Color], name: str) -> list[str]:
    """Return one complaint per off-palette colour. Fully transparent pixels pass."""
    used: set[Color] = set()
    for r, g, b, a in image.convert("RGBA").getdata():
        if a != 0:
            used.add((r, g, b))
    return [
        f"{name}: #{r:02x}{g:02x}{b:02x} is not in the palette"
        for r, g, b in sorted(used - palette)
    ]


def pack(frames: list[Path], cell: int, columns: int | None) -> tuple[Image.Image, dict]:
    columns = columns or math.ceil(math.sqrt(len(frames)))
    rows = math.ceil(len(frames) / columns)
    sheet = Image.new("RGBA", (columns * cell, rows * cell), (0, 0, 0, 0))
    atlas: dict = {"cell": cell, "columns": columns, "rows": rows, "frames": {}}

    for index, path in enumerate(frames):
        frame = Image.open(path).convert("RGBA")
        if frame.size != (cell, cell):
            sys.exit(f"{path.name} is {frame.width}x{frame.height}, expected {cell}x{cell}")
        x = (index % columns) * cell
        y = (index // columns) * cell
        sheet.paste(frame, (x, y))
        atlas["frames"][path.stem] = {"x": x, "y": y, "w": cell, "h": cell}

    return sheet, atlas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("src", type=Path, help="folder of PNG frames")
    parser.add_argument("--out", type=Path, default=Path("sheet.png"), help="sheet path")
    parser.add_argument("--cell", type=int, default=16, help="frame size in pixels")
    parser.add_argument("--columns", type=int, default=None, help="default: near-square")
    parser.add_argument("--palette", type=Path, default=None, help=".gpl to lint against")
    parser.add_argument("--strict", action="store_true", help="fail on off-palette pixels")
    args = parser.parse_args()

    frames = collect_frames(args.src)

    if args.palette:
        palette = load_palette(args.palette)
        problems: list[str] = []
        for path in frames:
            problems += lint_frame(Image.open(path), palette, path.name)
        for problem in problems:
            print(problem, file=sys.stderr)
        if problems and args.strict:
            sys.exit(f"{len(problems)} off-palette colours, refusing to pack")

    sheet, atlas = pack(frames, args.cell, args.columns)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out)
    atlas_path = args.out.with_suffix(".json")
    atlas_path.write_text(json.dumps(atlas, indent=2) + "\n", encoding="utf-8")

    print(f"{len(frames)} frames -> {args.out} ({sheet.width}x{sheet.height})")
    print(f"atlas -> {atlas_path}")


if __name__ == "__main__":
    main()

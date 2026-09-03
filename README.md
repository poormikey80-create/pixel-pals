# pixel-pals

A 16-colour palette I use for everything, and the Python script that turns a
folder of exported Aseprite frames into a sprite sheet Godot can read.

Two files, one job each. No project template, no asset pipeline, no config
format to learn.

## What is in here

- `pixel-pals-16.gpl` — the palette. Four ramps of four: neutrals, warms,
  greens, blues. Picked so that a 16x16 sprite still reads at 2x zoom on a
  cheap monitor, which is where most jam games get played.
- `build_sheet.py` — packs equal-sized PNG frames into a near-square sheet,
  writes an atlas JSON next to it, and optionally lints every frame against the
  palette.

## Install

The palette needs nothing. In Aseprite: **Palette > Load Palette** and pick
`pixel-pals-16.gpl`. Same file works in GIMP, Krita, LibreSprite and Tiled.

The script needs Python 3.9+ and Pillow:

```
pip install pillow
```

## Usage

Export your frames from Aseprite as individual PNGs of the same size, then:

```
python build_sheet.py frames/ --out build/pals.png --cell 16
```

That writes `build/pals.png` and `build/pals.json`, where the JSON maps each
source filename (without extension) to its `x, y, w, h` rect. Feed it straight
into an `AtlasTexture` or your own animation loader.

Lint while you pack:

```
python build_sheet.py frames/ --out build/pals.png --palette pixel-pals-16.gpl --strict
```

Without `--strict` it prints every off-palette colour to stderr and packs
anyway. With `--strict` it refuses. I run strict in CI and loose while drawing.

Frames are sorted by filename, so name them `walk_00.png`, `walk_01.png` and
the sheet order matches. Use `--columns` if you want one row per animation.

## Licence

MIT for the script. The palette is free to use in anything, commercial
included, no credit needed.

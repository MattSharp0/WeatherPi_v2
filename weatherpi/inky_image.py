"""Normalise images for the tri-colour (black / white / yellow) Inky pHAT.

The Inky driver ignores an image's palette and acts on raw pixel *indices*
(see ``show()`` in inky's ``inky.py`` / ``inky_ssd1608.py``):

    index 1 -> black ink, index 2 -> yellow ink, anything else -> white

A palette image whose palette is ordered differently (e.g. white, yellow, black)
or that contains stray indices >= 3 looks fine in a desktop viewer but comes out
wrong on the panel. ``to_inky`` maps every pixel to the nearest of the three
display colours and always returns a "P" image with exactly indices 0, 1 and 2
and the canonical palette below, so it renders the same on the panel and in a
desktop preview.

Run ``python -m weatherpi.inky_image icons imgs`` to audit files, add ``--fix``
to rewrite them in place.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

WHITE, BLACK, YELLOW = 0, 1, 2  # Inky's pixel values, identical for every pHAT variant
PALETTE = (255, 255, 255, 0, 0, 0, 255, 255, 0)  # RGB for indices WHITE, BLACK, YELLOW


def _palette_image() -> Image.Image:
    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette(PALETTE)
    return palette_image


def to_inky(img: Image.Image, dither: bool = False) -> Image.Image:
    """Return ``img`` as a "P" image using only the Inky indices 0, 1 and 2.

    Transparency is composited over white. Colours snap to the nearest of white,
    black and yellow; pass ``dither=True`` for photographs / gradients.
    """
    rgba = img.convert("RGBA")
    flat = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    flat.alpha_composite(rgba)

    method = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    out = flat.convert("RGB").quantize(palette=_palette_image(), dither=method)
    out.putpalette(PALETTE)
    return out


def problems(img: Image.Image) -> list[str]:
    """List reasons ``img`` would not render correctly on the panel as-is."""
    found = []
    if img.mode != "P":
        return [f"mode is {img.mode}, not P"]
    if "transparency" in img.info:
        found.append("has transparency")
    if tuple(img.getpalette()[: len(PALETTE)]) != PALETTE:
        found.append("palette is not white/black/yellow in that order")
    stray = sum(count for index, count in enumerate(img.histogram()) if index > YELLOW)
    if stray:
        found.append(f"{stray} pixels use indices >= 3 (drawn white)")
    return found


def simulate(img: Image.Image) -> Image.Image:
    """Show ``img`` as the panel will: index 1 black, 2 yellow, everything else white."""
    lut = [i if i in (BLACK, YELLOW) else WHITE for i in range(256)]
    out = img.convert("P").point(lut)
    out.putpalette(PALETTE)
    return out.convert("RGB")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit (and optionally fix) images for the Inky pHAT.")
    parser.add_argument("paths", nargs="+", type=Path, help="image files or directories of .png files")
    parser.add_argument("--fix", action="store_true", help="rewrite offending files in place")
    parser.add_argument(
        "--dither", action="store_true", help="with --fix, dither instead of snapping to nearest colour"
    )
    args = parser.parse_args(argv)

    files = [f for p in args.paths for f in (sorted(p.glob("*.png")) if p.is_dir() else [p])]
    bad = 0
    for path in files:
        with Image.open(path) as img:
            found = problems(img)
            if not found:
                continue
            bad += 1
            print(f"{path}: {'; '.join(found)}")
            if args.fix:
                fixed = to_inky(img, dither=args.dither)
        if args.fix and found:
            fixed.save(path, optimize=True)
    print(f"{len(files)} checked, {bad} {'fixed' if args.fix else 'need fixing'}")
    return 0 if args.fix or not bad else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Resize the master 1024×1024 icon into the full favicon set.

Outputs (all written to --out-dir):
  - icon.png (master copy, 1024)
  - favicon-16x16.png, favicon-32x32.png
  - favicon.ico (multi-resolution: 16, 32, 48)
  - apple-touch-icon.png (180)
  - android-chrome-192x192.png, android-chrome-512x512.png

Prints JSON with the list of paths created.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print(json.dumps({"error": "Pillow not installed. Run: pip install Pillow"}))
    sys.exit(2)


def alpha_key_background(img: Image.Image, sat_threshold: float = 0.18) -> Image.Image:
    """Convert low-saturation background pixels to transparent.

    Image models frequently render the "transparent background" instruction as
    a literal checker pattern (or a solid white fill) — opaque pixels that we
    have to clean ourselves. This pass treats any pixel whose HSV saturation is
    below ``sat_threshold`` as background and zeros its alpha. Saturated pixels
    keep their original alpha. Anti-aliased edges naturally get partial alpha
    via the soft falloff between sat==0 and sat==threshold.

    Skipped if the image already has any meaningfully transparent pixels —
    that's a signal the model handled alpha correctly and we shouldn't second-
    guess it.
    """
    rgba = img.convert("RGBA")
    data = rgba.getdata()
    has_real_alpha = any(p[3] < 240 for p in data)
    if has_real_alpha:
        return rgba

    # Two-band keying: anything below `floor` is hard-zero background; the band
    # between `floor` and `sat_threshold` gets a soft falloff so anti-aliased
    # stroke edges don't turn into hard jaggies. Clear-bg pixels at sat~0 must
    # be alpha=0, not alpha=5 — even tiny residual alpha shows as a visible
    # halo when compositing onto a dark background.
    floor = 0.05
    out = []
    for r, g, b, a in data:
        mx, mn = max(r, g, b), min(r, g, b)
        sat = 0.0 if mx == 0 else (mx - mn) / mx
        if sat >= sat_threshold:
            out.append((r, g, b, a))
        elif sat <= floor:
            out.append((r, g, b, 0))
        else:
            scale = (sat - floor) / (sat_threshold - floor)
            out.append((r, g, b, int(a * scale)))
    cleaned = Image.new("RGBA", rgba.size)
    cleaned.putdata(out)
    return cleaned


PNG_TARGETS = [
    ("icon.png", 1024),
    ("favicon-16x16.png", 16),
    ("favicon-32x32.png", 32),
    ("android-chrome-192x192.png", 192),
    ("android-chrome-512x512.png", 512),
]
ICO_SIZES = [16, 32, 48]
APPLE_TOUCH_SIZE = 180


def resize(src: Image.Image, size: int) -> Image.Image:
    return src.resize((size, size), Image.Resampling.LANCZOS)


def parse_color(s: str) -> tuple[int, int, int]:
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def flatten(icon: Image.Image, bg_rgb: tuple[int, int, int]) -> Image.Image:
    """Composite an RGBA icon onto a solid color, returning RGB.

    Used for apple-touch-icon: iOS renders transparent regions of an app icon
    as black, which usually looks wrong, so the convention is to ship a
    flattened, fully-opaque image.
    """
    flat = Image.new("RGB", icon.size, bg_rgb)
    flat.paste(icon, mask=icon.split()[3])
    return flat


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True, help="Path to 1024×1024 master PNG")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument(
        "--ios-bg",
        default="#ffffff",
        help="Solid background color for apple-touch-icon (iOS won't honor "
        "transparency). Hex, e.g. #ffffff or #003d3d.",
    )
    args = ap.parse_args()

    master_path = Path(args.master)
    if not master_path.exists():
        print(json.dumps({"error": f"master not found: {master_path}"}))
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    master = Image.open(master_path).convert("RGBA")
    if master.size != (1024, 1024):
        # Square it up if the model returned something close-but-not-exact
        side = max(master.size)
        canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        canvas.paste(master, ((side - master.size[0]) // 2, (side - master.size[1]) // 2))
        master = canvas.resize((1024, 1024), Image.Resampling.LANCZOS)

    master = alpha_key_background(master)
    # Persist the cleaned master alongside the raw one so callers see what was
    # actually used for downstream sizes — useful for debugging "why does my
    # favicon have a white square."
    master.save(master_path.with_name(master_path.stem + ".cleaned.png"), "PNG")

    written: list[str] = []

    for name, size in PNG_TARGETS:
        path = out_dir / name
        resize(master, size).save(path, "PNG", optimize=True)
        written.append(str(path))

    apple_path = out_dir / "apple-touch-icon.png"
    flatten(resize(master, APPLE_TOUCH_SIZE), parse_color(args.ios_bg)).save(
        apple_path, "PNG", optimize=True
    )
    written.append(str(apple_path))

    # Pillow's ICO writer handles multi-res internally: pass `sizes=` and it
    # resizes the source for each size and packs them all into one .ico.
    ico_path = out_dir / "favicon.ico"
    master.save(ico_path, format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    written.append(str(ico_path))

    print(json.dumps({"out_dir": str(out_dir), "files": written}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

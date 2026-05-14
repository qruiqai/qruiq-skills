#!/usr/bin/env python3
"""Composite a 1200×630 Open Graph card from the master icon + project text.

We composite (rather than asking the image model for a 1200×630) because:
  - Image models constrain output dimensions; 1200×630 isn't usually one of them
  - Text rendered by image models is unreliable; PIL gives crisp, predictable text
  - The icon already passed our quality bar — reusing it keeps the brand consistent

Layout: icon on the left (centered vertically), title + tagline to its right.
Background color is sampled from the icon (most common non-transparent pixel)
unless --bg is provided.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print(json.dumps({"error": "Pillow not installed. Run: pip install Pillow"}))
    sys.exit(2)


CANVAS = (1200, 630)
ICON_BOX = 360
ICON_LEFT = 80
TEXT_LEFT = ICON_LEFT + ICON_BOX + 60
TITLE_SIZE = 72
TAGLINE_SIZE = 32


# Fonts that ship with macOS / common Linux distros. Falls back to PIL default.
FONT_CANDIDATES_BOLD = [
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
FONT_CANDIDATES_REG = [
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def load_font(candidates: list[str], size: int) -> ImageFont.ImageFont:
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def alpha_key_background(img: Image.Image, sat_threshold: float = 0.18) -> Image.Image:
    """Same as make_assets.alpha_key_background — kept inline so the script has
    no internal-import dependencies. See make_assets.py for the full rationale.
    """
    rgba = img.convert("RGBA")
    data = rgba.getdata()
    has_real_alpha = any(p[3] < 240 for p in data)
    if has_real_alpha:
        return rgba
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


def parse_color(s: str) -> tuple[int, int, int]:
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError(f"bad color: {s}")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def dominant_color(img: Image.Image) -> tuple[int, int, int]:
    """Find the brand color by sampling only sufficiently saturated pixels.

    Image models often render "transparent background" as an opaque checker
    pattern or a near-white fill. Filtering by saturation (rather than just
    excluding pure white) is robust to all of those — only colored pixels
    contribute, so we get the actual brand tone, not the gray of the bg.
    """
    rgba = img.convert("RGBA")
    saturated: list[tuple[int, int, int]] = []
    for r, g, b, a in rgba.getdata():
        if a < 200:
            continue
        mx, mn = max(r, g, b), min(r, g, b)
        sat = 0.0 if mx == 0 else (mx - mn) / mx
        if sat < 0.25:
            continue
        saturated.append((r, g, b))
    if not saturated:
        return (30, 30, 40)
    bucketed = [(r & 0xF0, g & 0xF0, b & 0xF0) for r, g, b in saturated]
    return Counter(bucketed).most_common(1)[0][0]


def darken(rgb: tuple[int, int, int], factor: float = 0.55) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)


def text_color_for(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    # Perceptual luminance — pick white text on dark bg, near-black on light bg
    r, g, b = bg
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return (245, 245, 245) if lum < 140 else (20, 20, 24)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for w in words:
        candidate = f"{current} {w}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--tagline", default="")
    ap.add_argument("--bg", default="", help="Hex color, e.g. #1e1e2e. Defaults to icon-derived.")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    master = alpha_key_background(Image.open(args.master).convert("RGBA"))
    bg_rgb = parse_color(args.bg) if args.bg else darken(dominant_color(master))
    fg_rgb = text_color_for(bg_rgb)

    canvas = Image.new("RGB", CANVAS, bg_rgb)
    draw = ImageDraw.Draw(canvas)

    icon = master.resize((ICON_BOX, ICON_BOX), Image.Resampling.LANCZOS)
    icon_y = (CANVAS[1] - ICON_BOX) // 2
    canvas.paste(icon, (ICON_LEFT, icon_y), icon)

    title_font = load_font(FONT_CANDIDATES_BOLD, TITLE_SIZE)
    tagline_font = load_font(FONT_CANDIDATES_REG, TAGLINE_SIZE)
    text_max_width = CANVAS[0] - TEXT_LEFT - 80

    title_lines = wrap_text(draw, args.title, title_font, text_max_width)
    tagline_lines = wrap_text(draw, args.tagline, tagline_font, text_max_width) if args.tagline else []

    line_height_t = int(TITLE_SIZE * 1.15)
    line_height_g = int(TAGLINE_SIZE * 1.35)
    total_h = (
        len(title_lines) * line_height_t
        + (24 if tagline_lines else 0)
        + len(tagline_lines) * line_height_g
    )
    y = (CANVAS[1] - total_h) // 2

    for line in title_lines:
        draw.text((TEXT_LEFT, y), line, font=title_font, fill=fg_rgb)
        y += line_height_t
    if tagline_lines:
        y += 24
        muted = tuple(int(fg_rgb[i] * 0.7 + bg_rgb[i] * 0.3) for i in range(3))
        for line in tagline_lines:
            draw.text((TEXT_LEFT, y), line, font=tagline_font, fill=muted)
            y += line_height_g

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG", optimize=True)

    print(
        json.dumps(
            {
                "path": str(out_path),
                "bg": "#%02x%02x%02x" % bg_rgb,
                "fg": "#%02x%02x%02x" % fg_rgb,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

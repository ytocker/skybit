"""Stack the BEFORE/AFTER content-map timelines into one comparison image.

BEFORE = the original pre-clown-event content map (extracted from git history to
docs/screenshots/event_pagoda_map_pre_event.png): the original 320 s day, rain
@70, snow @139, day ≈183, no clown. AFTER = the current honest content map with
the clown event added (longer day ≈205, clown @~65 → gauntlet, rain @100, snow
@169). Each panel gets a caption band; BEFORE sits on top of AFTER.

    python tools/compose_timeline_comparison.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "docs", "screenshots")

BEFORE = os.path.join(SHOTS, "event_pagoda_map_pre_event.png")
AFTER = os.path.join(SHOTS, "event_pagoda_map_clown_v3.png")
OUT = os.path.join(SHOTS, "timeline_before_after.png")

CAP_BEFORE = ("BEFORE  —  original timeline (pre-clown-event):  "
              "320 s day  ·  rain @70  ·  snow @139  ·  day ≈183 pagodas")
CAP_AFTER = ("AFTER  —  clown event added:  day extended ≈205  ·  "
             "clown @~65 → warren gauntlet  ·  rain @100  ·  snow @169")

BAND_H = 52
PAD = 16
DIV_H = 6
BG = (24, 26, 32)
DIV = (90, 96, 112)
BAND_BEFORE = (54, 58, 70)
BAND_AFTER = (138, 22, 30)        # crimson, matching the clown accent
TEXT = (245, 246, 250)


def _font(size):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _panel(img, caption, band_col, width):
    """Scale `img` to `width` (preserve aspect) and prepend a caption band."""
    scaled = img.convert("RGB")
    if scaled.width != width:
        h = round(scaled.height * width / scaled.width)
        scaled = scaled.resize((width, h), Image.LANCZOS)
    panel = Image.new("RGB", (width, BAND_H + scaled.height), band_col)
    panel.paste(scaled, (0, BAND_H))
    draw = ImageDraw.Draw(panel)
    font = _font(24)
    tb = draw.textbbox((0, 0), caption, font=font)
    draw.text((PAD, (BAND_H - (tb[3] - tb[1])) // 2 - tb[1]), caption,
              fill=TEXT, font=font)
    return panel


def main():
    before = Image.open(BEFORE)
    after = Image.open(AFTER)
    width = max(before.width, after.width)

    p_before = _panel(before, CAP_BEFORE, BAND_BEFORE, width)
    p_after = _panel(after, CAP_AFTER, BAND_AFTER, width)

    total_h = PAD + p_before.height + DIV_H + p_after.height + PAD
    canvas = Image.new("RGB", (width + 2 * PAD, total_h), BG)
    y = PAD
    canvas.paste(p_before, (PAD, y)); y += p_before.height
    ImageDraw.Draw(canvas).rectangle(
        [PAD, y, PAD + width, y + DIV_H], fill=DIV); y += DIV_H
    canvas.paste(p_after, (PAD, y))

    canvas.save(OUT)
    print(f"wrote {OUT}  ({canvas.width}x{canvas.height})")


if __name__ == "__main__":
    main()

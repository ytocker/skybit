"""Build docs/hurt-parrot-v5-plus2/showcase.png — 5-panel composite of all concepts."""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(__file__), "hurt-parrot-v5-plus2")
OUT  = os.path.join(BASE, "showcase.png")

SLUGS = [
    ("casted-leg-brace",  "casted-leg-brace",  (160, 210, 255)),
    ("cinch-harness",     "cinch-harness",      (255, 210,  80)),
    ("wing-wrap-eight",   "wing-wrap-eight",    (100, 220, 150)),
    ("ace-headwrap",      "ace-headwrap",       (255, 180, 100)),
    ("storm-ruff",        "storm-ruff",         (200, 160, 255)),
]

PANEL_W  = 200
PANEL_H  = 355
MARGIN   = 20
GAP      = 8
HDR_H    = 44
FTR_H    = 36
BG       = (8, 8, 20)

# Each round_2.png is 1158×562.
# Layout inside each sheet:
#   row1 (4× strip): y=20, height=256 (68*4 per frame, 4 frames + gaps)
#   the 4 frames are each 272px wide at 4× (68px source + add_outline = 68; 68*4=272)
# We extract the first frame (hero pose, wing_angle=10°) from the 4× row.
FRAME_W4 = 272   # 68 * 4
FRAME_H4 = 256   # 64 * 4
SHEET_MARGIN = 20
FRAME_X0 = SHEET_MARGIN
FRAME_Y0 = SHEET_MARGIN

CANVAS_W = MARGIN + len(SLUGS) * PANEL_W + (len(SLUGS) - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FTR_H + MARGIN

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
draw   = ImageDraw.Draw(canvas)

try:
    font_hdr  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    font_lbl  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    font_num  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
except Exception:
    font_hdr = font_lbl = font_num = ImageFont.load_default()

# Header
hdr_txt = "HURT PARROT  ·  LAST LIFE  ·  v5+ CONCEPTS"
bb = draw.textbbox((0, 0), hdr_txt, font=font_hdr)
tw = bb[2] - bb[0]
draw.text(((CANVAS_W - tw) // 2, MARGIN + 14), hdr_txt, fill=(210, 210, 240), font=font_hdr)

y0 = MARGIN + HDR_H + GAP

for i, (slug, label, col) in enumerate(SLUGS):
    path = os.path.join(BASE, slug, "round_2.png")
    sheet = Image.open(path).convert("RGB")

    # Crop first 4× frame (hero pose) from the top-left of the sheet
    crop = sheet.crop((FRAME_X0, FRAME_Y0, FRAME_X0 + FRAME_W4, FRAME_Y0 + FRAME_H4))

    # Scale to fill PANEL_W width; letterbox vertically within PANEL_H
    scale_w = PANEL_W / FRAME_W4
    scaled_h = int(FRAME_H4 * scale_w)
    panel_img = crop.resize((PANEL_W, scaled_h), Image.LANCZOS)

    # Dark panel background
    panel_bg = Image.new("RGB", (PANEL_W, PANEL_H), (18, 18, 32))
    vert_pad = (PANEL_H - scaled_h) // 2
    panel_bg.paste(panel_img, (0, vert_pad))

    x0 = MARGIN + i * (PANEL_W + GAP)
    canvas.paste(panel_bg, (x0, y0))

    # Panel border in concept colour
    draw.rectangle([x0, y0, x0 + PANEL_W - 1, y0 + PANEL_H - 1], outline=col, width=1)

    # Footer: index number + slug label
    ftr_y = y0 + PANEL_H + 6
    num_txt = str(i + 1)
    bb = draw.textbbox((0, 0), num_txt, font=font_num)
    nw = bb[2] - bb[0]
    draw.text((x0 + (PANEL_W - nw) // 2, ftr_y), num_txt, fill=col, font=font_num)
    bb2 = draw.textbbox((0, 0), label, font=font_lbl)
    lw = bb2[2] - bb2[0]
    draw.text((x0 + (PANEL_W - lw) // 2, ftr_y + 16), label, fill=col, font=font_lbl)

canvas.save(OUT)
print(f"Saved {CANVAS_W}x{CANVAS_H} → {OUT}")

# Sanity: each panel should have content (not just background)
arr = np.array(canvas)
for i, (slug, _, _) in enumerate(SLUGS):
    x0 = MARGIN + i * (PANEL_W + GAP)
    panel = arr[y0:y0 + PANEL_H, x0:x0 + PANEL_W]
    non_bg = int(np.any(panel > 40, axis=2).sum())
    assert non_bg > 500, f"panel {slug} looks empty: {non_bg} non-bg pixels"
    print(f"  {slug}: {non_bg} non-bg px ✓")

print("All panels populated. Done.")

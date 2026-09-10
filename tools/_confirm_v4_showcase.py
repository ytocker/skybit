"""Phase 5 showcase for confirm_purchase_v4 — 5 concept panels on dark canvas."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "docs", "confirm_purchase_v4")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG_COL      = (8, 8, 20)
HEADER_COL  = (220, 190, 90)
FOOTER_COL  = (160, 140, 80)
BORDER_COL  = (40, 38, 60)

PANEL_W  = 200
PANEL_H  = 355
GAP      = 8
MARGIN   = 20
HEADER_H = 40
FOOTER_H = 32

SLUGS = [
    "arcade-marquee",
    "comic-splash",
    "prize-rosette",
    "sealed-relic",
    "flight-clearance",
]

def main():
    n = len(SLUGS)
    canvas_w = MARGIN + n * PANEL_W + (n - 1) * GAP + MARGIN
    canvas_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

    canvas = Image.new("RGB", (canvas_w, canvas_h), BG_COL)
    draw = ImageDraw.Draw(canvas)

    # Header title
    try:
        hfont = ImageFont.truetype(FONT_BOLD, 18)
    except Exception:
        hfont = ImageFont.load_default()

    title = "CONFIRM PURCHASE  v4  —  5 CONCEPTS"
    tx = canvas_w // 2
    ty = MARGIN + HEADER_H // 2
    draw.text((tx, ty), title, fill=HEADER_COL, font=hfont, anchor="mm")

    # Footer font
    try:
        ffont = ImageFont.truetype(FONT_BOLD, 11)
    except Exception:
        ffont = ImageFont.load_default()

    for i, slug in enumerate(SLUGS):
        px = MARGIN + i * (PANEL_W + GAP)
        py = MARGIN + HEADER_H

        src = os.path.join(BASE, slug, "round_2.png")
        img = Image.open(src).convert("RGB")
        w, h = img.size
        # Crop to left (affordable) state
        left = img.crop((0, 0, w // 2, h))
        left = left.resize((PANEL_W, PANEL_H), Image.LANCZOS)
        canvas.paste(left, (px, py))

        # Thin border around panel
        draw.rectangle([px, py, px + PANEL_W - 1, py + PANEL_H - 1],
                       outline=BORDER_COL, width=1)

        # Footer label
        label = f"{slug}  FINAL"
        fx = px + PANEL_W // 2
        fy = py + PANEL_H + FOOTER_H // 2
        draw.text((fx, fy), label, fill=FOOTER_COL, font=ffont, anchor="mm")

    out = os.path.join(BASE, "showcase.png")
    canvas.save(out, "PNG")
    w2, h2 = canvas.size
    print(f"Saved {out} ({w2}×{h2})")

if __name__ == "__main__":
    main()

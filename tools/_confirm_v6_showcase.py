"""Phase 5 showcase for confirm_purchase_v6 — 5 concept panels, LEGENDARY state."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "docs", "confirm_purchase_v6")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BG_COL     = (8, 8, 20)
HEADER_COL = (220, 190, 90)
FOOTER_COL = (160, 140, 80)
BORDER_COL = (40, 38, 60)

PANEL_W  = 200
PANEL_H  = 355
GAP      = 8
MARGIN   = 20
HEADER_H = 40
FOOTER_H = 32

SLUGS = [
    "crown-arc-shield",
    "spotlight-marquee",
    "sunburst-collar",
    "pennant-drop-octagon",
    "arch-keystone",
]


def main():
    n = len(SLUGS)
    canvas_w = MARGIN + n * PANEL_W + (n - 1) * GAP + MARGIN
    canvas_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

    canvas = Image.new("RGB", (canvas_w, canvas_h), BG_COL)
    draw = ImageDraw.Draw(canvas)

    try:
        hfont = ImageFont.truetype(FONT_BOLD, 18)
        ffont = ImageFont.truetype(FONT_BOLD, 11)
    except Exception:
        hfont = ffont = ImageFont.load_default()

    title = "CONFIRM PURCHASE  v6  —  5 CONCEPTS  (LEGENDARY)"
    draw.text((canvas_w // 2, MARGIN + HEADER_H // 2), title,
              fill=HEADER_COL, font=hfont, anchor="mm")

    for i, slug in enumerate(SLUGS):
        px = MARGIN + i * (PANEL_W + GAP)
        py = MARGIN + HEADER_H

        src = os.path.join(BASE, slug, "round_2.png")
        img = Image.open(src).convert("RGB")
        w, h = img.size
        # Rightmost third = LEGENDARY state
        panel = img.crop((w * 2 // 3, 0, w, h))
        panel = panel.resize((PANEL_W, PANEL_H), Image.LANCZOS)
        canvas.paste(panel, (px, py))

        draw.rectangle([px, py, px + PANEL_W - 1, py + PANEL_H - 1],
                       outline=BORDER_COL, width=1)

        label = f"{slug}  FINAL"
        draw.text((px + PANEL_W // 2, py + PANEL_H + FOOTER_H // 2),
                  label, fill=FOOTER_COL, font=ffont, anchor="mm")

    out = os.path.join(BASE, "showcase.png")
    canvas.save(out, "PNG")
    w2, h2 = canvas.size
    print(f"Saved {out} ({w2}x{h2})")


if __name__ == "__main__":
    main()

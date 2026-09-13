"""Phase 5 showcase for confirm_purchase_v5 — 5 concepts, LEGENDARY panel each."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "docs", "confirm_purchase_v5")

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

# halo-badge has a backdrop test strip below the main 3 panels (~418px tall for main panels)
HALO_MAIN_H = 418

SLUGS = [
    "clean-slab",
    "halo-badge",
    "gem-cut-panel",
    "capped-plate",
    "pedestal-pad",
]


def crop_legendary(img, slug):
    """Crop to the rightmost (LEGENDARY) panel from a 3-tier side-by-side render."""
    w, h = img.size
    # For halo-badge, clip backdrop strip from bottom
    if slug == "halo-badge":
        h = min(h, HALO_MAIN_H)
        img = img.crop((0, 0, w, h))
    # Rightmost third = LEGENDARY
    panel_w = w // 3
    return img.crop((w - panel_w, 0, w, h))


def main():
    n = len(SLUGS)
    canvas_w = MARGIN + n * PANEL_W + (n - 1) * GAP + MARGIN
    canvas_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

    canvas = Image.new("RGB", (canvas_w, canvas_h), BG_COL)
    draw = ImageDraw.Draw(canvas)

    try:
        hfont = ImageFont.truetype(FONT_BOLD, 16)
        ffont = ImageFont.truetype(FONT_BOLD, 11)
    except Exception:
        hfont = ffont = ImageFont.load_default()

    title = "CONFIRM PURCHASE v5  —  5 CONCEPTS  (LEGENDARY TIER)"
    draw.text((canvas_w // 2, MARGIN + HEADER_H // 2), title,
              fill=HEADER_COL, font=hfont, anchor="mm")

    for i, slug in enumerate(SLUGS):
        px = MARGIN + i * (PANEL_W + GAP)
        py = MARGIN + HEADER_H

        src = os.path.join(BASE, slug, "round_2.png")
        img = Image.open(src).convert("RGB")
        panel = crop_legendary(img, slug)
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
    print(f"Saved {out} ({w2}×{h2})")


if __name__ == "__main__":
    main()

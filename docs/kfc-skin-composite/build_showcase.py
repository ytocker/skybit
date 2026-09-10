"""Build docs/kfc-skin-composite/showcase.png — Phase 5 of the design loop."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "offscreen"
sys.path.insert(0, "/home/user/skybit")

from PIL import Image, ImageDraw, ImageFont

BG = (8, 8, 20)
PANEL_W, PANEL_H = 200, 355
GAP = 8
MARGIN = 20
HEADER_H = 44
FOOTER_H = 36

SLUGS = [
    "union-outline-bridge",
    "unified-refry",
    "batter-dip-line",
    "crispy-crust-rim",
    "kfc-bucket-carry",
]

LABELS = {
    "union-outline-bridge": "union-outline\nbridge",
    "unified-refry":        "unified-refry",
    "batter-dip-line":      "batter-dip-line",
    "crispy-crust-rim":     "crispy-crust-rim",
    "kfc-bucket-carry":     "kfc-bucket\ncarry",
}

VERDICT = "FINAL"

BASE = "/home/user/skybit/docs/kfc-skin-composite"


def crop_representative(img: Image.Image) -> Image.Image:
    """Crop a representative square-ish region from the exploration sheet.
    Takes the top 65% of height (excludes 1x gameplay row) and
    left 70% of width, then skips the ~25px margin/header at top-left.
    """
    w, h = img.size
    # Skip ~25px top margin; take top 65% of remaining
    top = 25
    bottom = int(h * 0.65)
    # Take full width (agents laid out 4 frames across with margins)
    right = min(w, int(w * 0.98))
    return img.crop((0, top, right, bottom))


def main():
    # Load and process each concept panel
    panels = []
    for slug in SLUGS:
        path = os.path.join(BASE, slug, "round_2.png")
        if not os.path.exists(path):
            print(f"MISSING: {path}")
            sys.exit(1)
        img = Image.open(path).convert("RGB")
        cropped = crop_representative(img)
        # Scale to panel size
        panel = cropped.resize((PANEL_W, PANEL_H), Image.LANCZOS)
        panels.append(panel)

    n = len(panels)
    canvas_w = MARGIN * 2 + n * PANEL_W + (n - 1) * GAP
    canvas_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN

    canvas = Image.new("RGB", (canvas_w, canvas_h), BG)
    draw = ImageDraw.Draw(canvas)

    # Try to get a font — fall back to default
    try:
        font_bold = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
        font_sm = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        font_header = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception:
        font_bold = font_sm = font_header = ImageFont.load_default()

    # Header
    title = "KFC SKIN COMPOSITE — DESIGN LOOP ROUND 2"
    draw.text((MARGIN, MARGIN + 10), title, fill=(210, 138, 42), font=font_header)

    # Panels + labels
    for i, (slug, panel) in enumerate(zip(SLUGS, panels)):
        x = MARGIN + i * (PANEL_W + GAP)
        y = MARGIN + HEADER_H

        # Thin amber border
        border_rect = [x - 2, y - 2, x + PANEL_W + 1, y + PANEL_H + 1]
        draw.rectangle(border_rect, outline=(80, 50, 10), width=1)

        canvas.paste(panel, (x, y))

        # Footer: slug name
        label = LABELS[slug]
        footer_y = y + PANEL_H + 5
        lines = label.split("\n")
        for li, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_bold)
            tw = bbox[2] - bbox[0]
            tx = x + (PANEL_W - tw) // 2
            draw.text((tx, footer_y + li * 13), line,
                      fill=(210, 175, 100), font=font_bold)

        # Verdict chip
        verdict_y = footer_y + len(lines) * 13 + 2
        vbox = draw.textbbox((0, 0), VERDICT, font=font_sm)
        vw = vbox[2] - vbox[0]
        vx = x + (PANEL_W - vw) // 2
        draw.text((vx, verdict_y), VERDICT, fill=(130, 200, 130), font=font_sm)

    out_path = os.path.join(BASE, "showcase.png")
    canvas.save(out_path)

    from PIL import Image as _I
    check = _I.open(out_path)
    print(f"Saved {out_path}  {check.size}")


if __name__ == "__main__":
    main()

"""Phase 5 showcase: BEFORE + 5 premium-v1 round_2 concepts."""

import os
import sys
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch gloss_sweep before any store imports
import game.store_cards as sc
def _safe_gloss(surf, rect, radius, peak=46):
    w, h = rect[2], rect[3]
    gsurf = pygame.Surface((w, h), pygame.SRCALPHA)
    gsurf.fill((0, 0, 0, 0))
    steps = 10
    for i in range(steps):
        t = i / (steps - 1)
        alpha = int(peak * (1 - t))
        bar_h = max(1, int(h * 0.45 * (1 - t)))
        pygame.draw.ellipse(gsurf, (255, 255, 255, alpha),
            (int(w * 0.1), int(h * 0.04 + i * 1.5), int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))
sc.gloss_sweep = _safe_gloss

from PIL import Image, ImageDraw, ImageFont

# ── Config ────────────────────────────────────────────────────────────────────
SLUGS = [
    "sovereign-seal",
    "midnight-enamel",
    "obsidian-forge",
    "lacquer-nacre",
    "lapidary-vault",
]
BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "docs", "confirm_purchase_v8", "premium-v1")
OUT_PNG = os.path.join(BASE, "showcase_v2.png")

PANEL_W, PANEL_H = 200, 355
MARGIN = 20
GAP = 8
HEADER_H = 40
FOOTER_H = 48  # taller footer: ID badge + slug name
N_PANELS = 6  # BEFORE + 5

CANVAS_W = MARGIN + N_PANELS * PANEL_W + (N_PANELS - 1) * GAP + MARGIN
CANVAS_H = HEADER_H + MARGIN + PANEL_H + FOOTER_H + MARGIN
BG = (8, 8, 20)

# EPIC crop from 3-tier strip
EPIC_X0, EPIC_X1 = 584, 1104
EPIC_Y0_1040 = 116
EPIC_Y1_1040 = 1000
EPIC_Y0_1080 = 156
EPIC_Y1_1080 = 1040


def render_before() -> Image.Image:
    """Render the live _draw_confirm and crop to the popup."""
    import game.store_data as _dat
    import game.store_catalog as _cat
    try:
        from game.store import StoreScene
    except Exception as e:
        print(f"[BEFORE] StoreScene import failed: {e}")
        img = Image.new("RGB", (260, 442), (20, 22, 60))
        d = ImageDraw.Draw(img)
        d.text((10, 200), "BEFORE\n(unavailable)", fill=(200, 200, 200))
        return img

    SID = "skin_baseball"
    _orig_bal = _dat.balance
    _dat.balance = lambda: 99999
    try:
        class _Stub:
            _confirm = SID
            _confirm_panel = None
            confirm_yes_rect = None
            confirm_no_rect = None

            @staticmethod
            def _disp_name(sid):
                try:
                    return _cat.name(sid)
                except Exception:
                    return sid.replace("skin_", "").upper()

        surf = pygame.Surface((360, 640))
        surf.fill((8, 8, 20))
        StoreScene._draw_confirm(_Stub(), surf)
        crop = surf.subsurface(pygame.Rect(50, 40, 260, 442)).copy()
        raw = pygame.image.tostring(crop, "RGB")
        return Image.frombytes("RGB", (260, 442), raw)
    except Exception as e:
        print(f"[BEFORE] render failed: {e}")
        img = Image.new("RGB", (260, 442), (20, 22, 60))
        return img
    finally:
        _dat.balance = _orig_bal


def epic_crop(path: str) -> Image.Image:
    strip = Image.open(path)
    w, h = strip.size
    if h >= 1075:
        y0, y1 = EPIC_Y0_1080, EPIC_Y1_1080
    else:
        y0, y1 = EPIC_Y0_1040, EPIC_Y1_1040
    region = strip.crop((EPIC_X0, y0, EPIC_X1, y1))
    return region.resize((PANEL_W, PANEL_H), Image.LANCZOS)


def make_showcase():
    os.makedirs(BASE, exist_ok=True)
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(canvas)

    try:
        font_hdr = ImageFont.truetype("game/assets/bold.ttf", 18)
    except Exception:
        font_hdr = ImageFont.load_default()
    try:
        font_lbl = ImageFont.truetype("game/assets/bold.ttf", 11)
    except Exception:
        font_lbl = ImageFont.load_default()
    try:
        font_id = ImageFont.truetype("game/assets/bold.ttf", 16)
    except Exception:
        font_id = ImageFont.load_default()

    draw.text((CANVAS_W // 2, HEADER_H // 2),
              "CONFIRM POPUP · PREMIUM ENHANCE v1",
              fill=(200, 190, 240), font=font_hdr, anchor="mm")

    panels = []

    print("Rendering BEFORE panel…")
    before_img = render_before()
    before_scaled = before_img.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    panels.append(("BEFORE", before_scaled))

    for slug in SLUGS:
        path = os.path.join(BASE, slug, "round_2.png")
        print(f"Loading {slug}…")
        try:
            panel = epic_crop(path)
        except Exception as e:
            print(f"  ERROR loading {slug}: {e}")
            panel = Image.new("RGB", (PANEL_W, PANEL_H), (60, 10, 10))
            d = ImageDraw.Draw(panel)
            d.text((10, 160), slug[:20], fill=(255, 80, 80))
        panels.append((slug, panel))

    ID_LABELS = ["BEFORE", "#1", "#2", "#3", "#4", "#5"]
    for i, (label, panel) in enumerate(panels):
        x = MARGIN + i * (PANEL_W + GAP)
        y = HEADER_H + MARGIN
        canvas.paste(panel, (x, y))
        footer_top = y + PANEL_H
        # ID badge (large, bright)
        id_text = ID_LABELS[i]
        id_col = (240, 220, 100) if i > 0 else (160, 160, 180)
        draw.text((x + PANEL_W // 2, footer_top + 14),
                  id_text, fill=id_col, font=font_id, anchor="mm")
        # Slug name (smaller, muted)
        draw.text((x + PANEL_W // 2, footer_top + 34),
                  label, fill=(150, 140, 190), font=font_lbl, anchor="mm")

    canvas.save(OUT_PNG)
    print(f"\nShowcase saved → {OUT_PNG}")
    print(f"Canvas: {CANVAS_W}×{CANVAS_H}")

    # Verify
    img = Image.open(OUT_PNG)
    print(f"Verified: {img.size}")
    return OUT_PNG


if __name__ == "__main__":
    make_showcase()

"""Phase 5 showcase: BEFORE + 5 card-frame-v1 round_2 concepts."""

import os
import sys
import pygame
import textwrap

# ── BLEND_ADD fix (must precede store_cards import) ──────────────────────────
_orig_gloss = None
def _patch_store_cards():
    import game.store_cards as sc
    global _orig_gloss
    if getattr(sc, "_gloss_patched", False):
        return
    _orig_gloss = sc.gloss_sweep
    def _safe_gloss(surf, rect, radius, peak=46):
        w, h = rect[2], rect[3]
        gsurf = pygame.Surface((w, h), pygame.SRCALPHA)
        gsurf.fill((0, 0, 0, 0))
        steps = 10
        for i in range(steps):
            t = i / (steps - 1)
            alpha = int(peak * (1 - t))
            bar_h = max(1, int(h * 0.45 * (1 - t)))
            col = (255, 255, 255, alpha)
            pygame.draw.ellipse(gsurf, col,
                (int(w * 0.1), int(h * 0.04 + i * 1.5),
                 int(w * 0.8), bar_h))
        surf.blit(gsurf, (rect[0], rect[1]))
    sc.gloss_sweep = _safe_gloss
    sc.gloss_sweep.__doc__ = "patched"
    sc._gloss_patched = True

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_patch_store_cards()

from PIL import Image, ImageDraw, ImageFont

# ── Config ────────────────────────────────────────────────────────────────────
SLUGS = [
    "chromatic-full-art",
    "ticket-stub",
    "vault-jewel",
    "gilt-codex",
    "cartouche-sacred",
]
BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "docs", "confirm_purchase_v8", "card-frame-v1")
OUT_PNG = os.path.join(BASE, "showcase_v1.png")

PANEL_W, PANEL_H = 200, 355
MARGIN = 20
GAP = 8
HEADER_H = 40
FOOTER_H = 32
N_PANELS = 6  # BEFORE + 5

CANVAS_W = MARGIN + N_PANELS * PANEL_W + (N_PANELS - 1) * GAP + MARGIN
CANVAS_H = HEADER_H + MARGIN + PANEL_H + FOOTER_H + MARGIN
BG = (8, 8, 20)

# EPIC crop constants — adjusted per strip height
# For 1688×1040 strips: popup at y=HEAD*2=116, EPIC col x=[584,1104]
EPIC_X0, EPIC_X1 = 584, 1104  # middle of 3 popups at 2×
EPIC_Y0_1040 = 116   # HEAD*2 = 58*2
EPIC_Y1_1040 = 1000  # Y0 + 442*2

EPIC_Y0_1080 = 156   # (HEAD+MARGIN)*2 = 78*2
EPIC_Y1_1080 = 1040  # Y0 + 442*2


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
        # popup is centered in 360×640; offset ≈ (50, 40)
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
    """Load strip, crop the EPIC (middle) popup, return PIL image."""
    strip = Image.open(path)
    w, h = strip.size
    if h >= 1075:
        y0, y1 = EPIC_Y0_1080, EPIC_Y1_1080
    else:
        y0, y1 = EPIC_Y0_1040, EPIC_Y1_1040
    region = strip.crop((EPIC_X0, y0, EPIC_X1, y1))
    return region.resize((PANEL_W, PANEL_H), Image.LANCZOS)


def make_showcase():
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(canvas)

    # Header
    try:
        font_hdr = ImageFont.truetype("game/assets/bold.ttf", 18)
    except Exception:
        font_hdr = ImageFont.load_default()
    try:
        font_lbl = ImageFont.truetype("game/assets/bold.ttf", 11)
    except Exception:
        font_lbl = ImageFont.load_default()

    draw.text((CANVAS_W // 2, HEADER_H // 2),
              "CONFIRM POPUP · CARD FRAME v1 · ROUND 2",
              fill=(200, 190, 240), font=font_hdr, anchor="mm")

    panels = []

    # BEFORE
    print("Rendering BEFORE panel…")
    before_img = render_before()
    before_scaled = before_img.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    panels.append(("BEFORE", before_scaled))

    # 5 concepts
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

    # Blit panels
    for i, (label, panel) in enumerate(panels):
        x = MARGIN + i * (PANEL_W + GAP)
        y = HEADER_H + MARGIN
        canvas.paste(panel, (x, y))
        # Footer label
        short = label.replace("-", "-\n") if len(label) > 14 else label
        draw.text((x + PANEL_W // 2, y + PANEL_H + FOOTER_H // 2),
                  label, fill=(180, 170, 220), font=font_lbl, anchor="mm")

    canvas.save(OUT_PNG)
    print(f"\nShowcase saved → {OUT_PNG}")
    print(f"Canvas: {CANVAS_W}×{CANVAS_H}")
    return OUT_PNG


if __name__ == "__main__":
    path = make_showcase()
    # Verify
    img = Image.open(path)
    print(f"Verified: {img.size}")

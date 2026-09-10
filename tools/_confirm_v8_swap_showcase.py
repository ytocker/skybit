#!/usr/bin/env python3
"""Assemble swap-round-1 showcase: BEFORE + 5 round_2 concept panels (EPIC tier)."""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWAP_DIR = os.path.join(REPO, "docs", "confirm_purchase_v8", "swap-round-1")
FONT_PATH = os.path.join(REPO, "game", "assets", "LiberationSans-Bold.ttf")

SLUGS = ["herald-rail", "medallion-sash", "assay-balance", "marquee-bulb", "gem-facet"]

# Strip layout (at 2× output scale from 1× source w/ MARGIN=20, HEAD=58, GAP=12, POP=260×442)
_M2 = 40   # MARGIN×2
_H2 = 116  # HEAD×2
_G2 = 24   # GAP×2
_PW = 520  # popup width × 2
_PH = 884  # popup height × 2
EPIC_CROP = (_M2 + _PW + _G2, _H2, _M2 + _PW + _G2 + _PW, _H2 + _PH)  # (584,116,1104,1000)

PANEL_W, PANEL_H = 200, 355
BG       = (8, 8, 20)
GAP      = 8
MARGIN   = 20
HEADER_H = 40
FOOTER_H = 32
N        = 6  # BEFORE + 5 concepts

CANVAS_W = 2*MARGIN + N*PANEL_W + (N-1)*GAP
CANVAS_H = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN


def render_before() -> Image.Image:
    """Render the post-swap _draw_confirm for an EPIC skin; return 260×442 PIL Image."""
    from game.store import StoreScene
    import game.store_catalog as _cat
    import game.store_data as _dat

    SID = "skin_baseball"  # epic tier

    orig_bal = _dat.balance
    _dat.balance = lambda: 99999
    try:
        class _Stub:
            _confirm       = SID
            _confirm_panel = None
            confirm_yes_rect = None
            confirm_no_rect  = None
            @staticmethod
            def _disp_name(sid):
                try:   return _cat.name(sid)
                except: return sid.replace("skin_", "").upper()

        surf = pygame.Surface((360, 640))
        surf.fill((8, 8, 20))
        StoreScene._draw_confirm(_Stub(), surf)
        crop = surf.subsurface(pygame.Rect(50, 40, 260, 442)).copy()
        raw = pygame.image.tostring(crop, "RGB")
        return Image.frombytes("RGB", (260, 442), raw)
    finally:
        _dat.balance = orig_bal


def load_epic(slug: str) -> Image.Image:
    path  = os.path.join(SWAP_DIR, slug, "round_2.png")
    strip = Image.open(path)
    return strip.crop(EPIC_CROP).resize((PANEL_W, PANEL_H), Image.LANCZOS)


def main():
    try:
        fnt_hdr = ImageFont.truetype(FONT_PATH, 17)
        fnt_ftr = ImageFont.truetype(FONT_PATH, 10)
    except Exception:
        fnt_hdr = fnt_ftr = ImageFont.load_default()

    print("Rendering BEFORE panel …")
    before_raw = render_before()
    before_img = before_raw.resize((PANEL_W, PANEL_H), Image.LANCZOS)

    panels = [("BEFORE", before_img)]
    for s in SLUGS:
        print(f"Loading {s} round_2 …")
        panels.append((s, load_epic(s)))

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw   = ImageDraw.Draw(canvas)

    title = "SWAP ROUND 1 — EPIC TIER"
    bb = draw.textbbox((0, 0), title, font=fnt_hdr)
    draw.text(
        ((CANVAS_W - (bb[2]-bb[0]))//2, MARGIN + (HEADER_H - (bb[3]-bb[1]))//2),
        title, fill=(220, 218, 240), font=fnt_hdr,
    )

    for i, (label, img) in enumerate(panels):
        px = MARGIN + i * (PANEL_W + GAP)
        py = MARGIN + HEADER_H
        canvas.paste(img, (px, py))
        bb = draw.textbbox((0, 0), label, font=fnt_ftr)
        lx = px + (PANEL_W - (bb[2]-bb[0])) // 2
        ly = py + PANEL_H + (FOOTER_H - (bb[3]-bb[1])) // 2
        draw.text((lx, ly), label, fill=(180, 178, 210), font=fnt_ftr)

    out = os.path.join(SWAP_DIR, "showcase_v1.png")
    canvas.save(out)
    w, h = canvas.size
    print(f"Saved {out}  ({w}×{h})")


if __name__ == "__main__":
    main()

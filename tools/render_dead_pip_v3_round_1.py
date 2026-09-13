"""Render docs/dead_pip_v3/round_1.png — five dead-Pip palette repaints.

Each candidate calls `_build_parrot_with_palette` end-to-end with a bespoke
palette so the body keeps its layered colour structure (tail / belly /
chest / head / wing all painted in palette colours, not lerped). Eye
treatments are drawn directly on the body surface — no sub-canvas X
stickers, no per-pixel tinting.

A 3-frame cross-fade strip at the bottom previews how the chosen palette
reads when blitted over the live Pip at 33% / 67% / 100% alpha (the
ship-time gradient transition).
"""
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.parrot import SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _build_frame
from game.draw import blit_glow, NEAR_BLACK, UI_GOLD, UI_CREAM, lerp_color


# ── output target ────────────────────────────────────────────────────────────

OUT_PATH = pathlib.Path(__file__).parent.parent / "docs" / "dead_pip_v3" / "round_1.png"
BG_DAWN  = (38, 44, 66)
CARD_BG  = (24, 28, 42)
CARD_EDGE = (60, 68, 90)
TEXT_HI  = (235, 240, 250)
TEXT_LO  = (165, 175, 195)

# Neutral wing pose (matches v2 sheet for like-for-like palette comparison)
WING_ANGLE = _WING_ANGLES[1]   # 20°

# Lens centres in body-surface space (see _draw_lenses in parrot/ghost code)
LENS_L = (46, 20)
LENS_R = (56, 19)


def _font(size: int) -> pygame.font.Font:
    """Bundled Bold font is the only ttf we ship; use it for all UI text."""
    path = pathlib.Path(__file__).parent.parent / "game" / "assets" / "LiberationSans-Bold.ttf"
    return pygame.font.Font(str(path), size)


def _text(surf, msg, pos, size=14, color=TEXT_HI, shadow=True):
    f = _font(size)
    img = f.render(msg, True, color)
    if shadow:
        sh = f.render(msg, True, (0, 0, 0))
        surf.blit(sh, (pos[0] + 1, pos[1] + 1))
    surf.blit(img, pos)
    return img.get_size()


# ── PALETTE A — ASHEN GREENISH ───────────────────────────────────────────────
# Pip's vivid scarlet drained to pale-ash with sickly green-yellow highlights.
# Keeps a faded tail gradient instead of full-uniform colour so the body
# silhouette still reads as a macaw, just poisoned.

P_ASHEN = _pal(
    tail=[(140, 140, 130), (160, 165, 140), (185, 190, 160), (205, 210, 175)],
    tail_line=(90, 95, 80),
    body_shadow=(80, 90, 80),
    body_main=(170, 175, 155),
    body_chest=(195, 200, 170),
    body_belly=(210, 215, 180),
    sheen=(230, 235, 200, 110),
    wing_main=(110, 125, 115),
    wing_dark=(60, 70, 65),
    wing_tip=(170, 180, 145),
    wing_secondary=(195, 200, 150),
    wing_highlight=(220, 225, 190),
    head_shadow=(85, 95, 85),
    head_main=(175, 180, 155),
    head_cheek=(190, 195, 160),
    head_crown=(205, 210, 175),
    lens_frame=(140, 145, 125),
    lens_body=(220, 220, 195),    # PALE so dark X reads inside the lens
    lens_tint=None,
    lens_glint=None,
    beak_main=(165, 160, 130),
    beak_dark=(95, 90, 65),
    beak_gloss=(200, 200, 165),
    foot=(80, 85, 70),
)

def build_ashen_dead(angle_deg):
    """Poisoned-bird palette + tiny dark X strokes painted into the pale lens body."""
    body = _build_parrot_with_palette(angle_deg, P_ASHEN)
    # X-strokes are drawn ON the body surface (no sub-canvas), in palette
    # ink so they read as part of the dead bird, not as a pasted icon.
    ink = (28, 22, 26)
    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.line(body, ink, (cx - 3, cy - 3), (cx + 3, cy + 3), 2)
        pygame.draw.line(body, ink, (cx - 3, cy + 3), (cx + 3, cy - 3), 2)
    return body


# ── PALETTE B — CHARTREUSE ECTOPLASM ─────────────────────────────────────────
# Toxic chartreuse with sunken sockets. Echoes the ghost ECTOPLASM hue but
# pushes it sicker / less saturated highlights so it reads "poisoned",
# not "Slimer."

P_CHARTREUSE = _pal(
    tail=[(95, 130, 35), (135, 165, 45), (175, 195, 60), (200, 215, 80)],
    tail_line=(60, 80, 25),
    body_shadow=(70, 95, 30),
    body_main=(165, 185, 55),
    body_chest=(195, 210, 80),
    body_belly=(215, 220, 110),
    sheen=(235, 240, 160, 120),
    wing_main=(120, 150, 40),
    wing_dark=(55, 75, 20),
    wing_tip=(195, 215, 75),
    wing_secondary=(220, 230, 110),
    wing_highlight=(230, 235, 150),
    head_shadow=(75, 100, 35),
    head_main=(170, 190, 60),
    head_cheek=(200, 215, 85),
    head_crown=(215, 225, 110),
    lens_frame=(60, 80, 25),       # dark sunken rim
    lens_body=(10, 18, 8),         # near-black socket
    lens_tint=None,
    lens_glint=None,               # no glint — empty socket
    beak_main=(170, 165, 65),
    beak_dark=(95, 90, 25),
    beak_gloss=(215, 215, 130),
    foot=(60, 75, 20),
)

def build_chartreuse_dead(angle_deg):
    """Sickly toxic chartreuse with hollow sockets + faint poison aura."""
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    blit_glow(out, 32, 30, 22, (140, 200, 60), alpha=95)
    body = _build_parrot_with_palette(angle_deg, P_CHARTREUSE)
    # Deepen the sockets a hair so the hollow read holds against the bright body
    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.circle(body, (5, 10, 5), (cx, cy), 3)
        # tiny inner shadow at top — gives the socket depth
        pygame.draw.line(body, (40, 55, 25), (cx - 2, cy - 2), (cx + 2, cy - 2), 1)
    out.blit(body, (0, 0))
    return out


# ── PALETTE C — WITHERED PURPLE-GREEN (bruise) ───────────────────────────────
# Two-tone bruise: eggplant shadows + sickly chartreuse highlights. The
# combo reads "bruised from poison" — saturated but never cheerful.

P_BRUISE = _pal(
    tail=[(80, 50, 95), (110, 75, 105), (155, 145, 90), (190, 200, 100)],
    tail_line=(50, 28, 65),
    body_shadow=(55, 30, 75),
    body_main=(110, 90, 110),
    body_chest=(150, 145, 105),
    body_belly=(180, 190, 110),
    sheen=(220, 220, 150, 90),
    wing_main=(70, 45, 90),
    wing_dark=(35, 18, 55),
    wing_tip=(160, 170, 80),
    wing_secondary=(195, 200, 95),
    wing_highlight=(215, 220, 130),
    head_shadow=(60, 35, 80),
    head_main=(115, 95, 115),
    head_cheek=(150, 140, 105),
    head_crown=(175, 185, 110),
    lens_frame=(60, 30, 75),
    lens_body=(170, 180, 100),   # sickly green lens body so X stays legible
    lens_tint=None,
    lens_glint=None,
    beak_main=(135, 120, 80),
    beak_dark=(60, 40, 30),
    beak_gloss=(190, 185, 120),
    foot=(50, 28, 65),
)

def build_bruise_dead(angle_deg):
    """Bruised eggplant + chartreuse — X-eyes in deep purple-ink."""
    body = _build_parrot_with_palette(angle_deg, P_BRUISE)
    ink = (30, 16, 40)
    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.line(body, ink, (cx - 3, cy - 3), (cx + 3, cy + 3), 2)
        pygame.draw.line(body, ink, (cx - 3, cy + 3), (cx + 3, cy - 3), 2)
    return body


# ── PALETTE D — DESATURATED SCARLET (life leaving) ───────────────────────────
# Pip's original colour family, but with the saturation crushed and a
# sickly green creeping in to chest/cheek/wing-tip. The most "this is
# still our parrot" of the five — life-is-leaving rather than dead-monster.

P_FADING = _pal(
    tail=[(140, 70, 60), (170, 105, 70), (195, 140, 85), (210, 175, 100)],
    tail_line=(95, 40, 35),
    body_shadow=(95, 55, 55),
    body_main=(180, 115, 105),
    body_chest=(190, 155, 110),    # green-yellow seep on the chest
    body_belly=(200, 180, 120),
    sheen=(220, 200, 170, 110),
    wing_main=(115, 95, 130),
    wing_dark=(60, 50, 75),
    wing_tip=(160, 175, 95),       # sickly green tip
    wing_secondary=(190, 195, 120),
    wing_highlight=(215, 220, 175),
    head_shadow=(105, 60, 60),
    head_main=(185, 120, 105),
    head_cheek=(170, 180, 100),    # sickly green cheek-flush
    head_crown=(210, 175, 130),
    lens_frame=(150, 110, 80),
    lens_body=(185, 120, 105),     # painted in head_main — sets up the closed-lid
    lens_tint=None,
    lens_glint=None,
    beak_main=(190, 145, 70),
    beak_dark=(105, 70, 25),
    beak_gloss=(220, 195, 130),
    foot=(95, 55, 50),
)

def build_fading_dead(angle_deg):
    """Pip drained ~60% with sickly green seep. Limp-lid overpaint:
    lens_body matches head_main, then a thin dark curve reads as a
    closed eyelid — softer / sadder than X-eyes."""
    body = _build_parrot_with_palette(angle_deg, P_FADING)
    lid_ink = (70, 35, 40)
    lash_ink = (45, 20, 25)
    # Left lens — eyelid arc + a few lashes
    pygame.draw.arc(body, lid_ink, pygame.Rect(LENS_L[0] - 6, LENS_L[1] - 4, 12, 8),
                    3.40, 6.05, 2)
    pygame.draw.line(body, lash_ink, (LENS_L[0] - 4, LENS_L[1] + 1), (LENS_L[0] - 5, LENS_L[1] + 3), 1)
    pygame.draw.line(body, lash_ink, (LENS_L[0], LENS_L[1] + 2), (LENS_L[0], LENS_L[1] + 4), 1)
    pygame.draw.line(body, lash_ink, (LENS_L[0] + 4, LENS_L[1] + 1), (LENS_L[0] + 5, LENS_L[1] + 3), 1)
    # Right lens — same idea
    pygame.draw.arc(body, lid_ink, pygame.Rect(LENS_R[0] - 6, LENS_R[1] - 4, 12, 8),
                    3.40, 6.05, 2)
    pygame.draw.line(body, lash_ink, (LENS_R[0] - 4, LENS_R[1] + 1), (LENS_R[0] - 5, LENS_R[1] + 3), 1)
    pygame.draw.line(body, lash_ink, (LENS_R[0], LENS_R[1] + 2), (LENS_R[0], LENS_R[1] + 4), 1)
    pygame.draw.line(body, lash_ink, (LENS_R[0] + 4, LENS_R[1] + 1), (LENS_R[0] + 5, LENS_R[1] + 3), 1)
    return body


# ── PALETTE E — NIGHT-VAPOR DARK (corrupted spectre) ─────────────────────────
# The most ominous of the five — dark poison-purple body, faint sickly
# yellow-green aura, and glowing toxic pupils (mirrors the WRAITH eye
# logic from dollar_parrot_ghost, retinted to toxic yellow-green).

P_NIGHTVAPOR = _pal(
    tail=[(28, 35, 30), (40, 50, 40), (55, 70, 50), (70, 90, 55)],
    tail_line=(15, 22, 18),
    body_shadow=(12, 18, 18),
    body_main=(40, 55, 45),
    body_chest=(60, 80, 55),
    body_belly=(85, 110, 70),
    sheen=(160, 200, 120, 90),
    wing_main=(30, 25, 55),
    wing_dark=(12, 10, 28),
    wing_tip=(70, 95, 50),
    wing_secondary=None,
    wing_highlight=(160, 200, 110),
    head_shadow=(15, 22, 22),
    head_main=(45, 60, 50),
    head_cheek=(65, 85, 60),
    head_crown=(80, 105, 70),
    lens_frame=(120, 170, 60),
    lens_body=(8, 12, 8),
    lens_tint=None,
    lens_glint=None,         # replaced below — toxic glowing pupils
    beak_main=(85, 95, 60),
    beak_dark=(35, 40, 25),
    beak_gloss=(160, 190, 110),
    foot=(20, 28, 22),
)

def build_nightvapor_dead(angle_deg):
    """Dark poisoned spectre with glowing toxic yellow-green pupils."""
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Two-layer aura: wide soft sickly halo, then a tighter brighter core
    blit_glow(out, 32, 30, 26, (110, 170, 50), alpha=120)
    blit_glow(out, 32, 30, 18, (180, 230, 110), alpha=100)
    body = _build_parrot_with_palette(angle_deg, P_NIGHTVAPOR)
    out.blit(body, (0, 0))
    # Glowing toxic pupils — same recipe as Wraith eyes, retinted
    for ex, ey in (LENS_L, LENS_R):
        blit_glow(out, ex, ey, 4, (180, 240, 80), alpha=210)
        pygame.draw.circle(out, (220, 250, 130), (ex, ey), 2)
        pygame.draw.circle(out, (250, 255, 200), (ex - 1, ey - 1), 1)
    return out


# ── panel registry ───────────────────────────────────────────────────────────

PANELS = [
    ("A. ASHEN GREENISH",       "Poisoned bird — body drained pale, dark X strokes painted into the lens body.",       build_ashen_dead),
    ("B. CHARTREUSE ECTOPLASM", "Toxic chartreuse with sunken empty sockets — sicker cousin of the ghost slime hue.",  build_chartreuse_dead),
    ("C. WITHERED BRUISE",      "Eggplant shadows + sickly chartreuse highlights — bruised-from-poison palette.",      build_bruise_dead),
    ("D. DESATURATED SCARLET",  "Pip's own scarlet drained 60% with sickly green seep — closed-eyelid overpaint.",     build_fading_dead),
    ("E. NIGHT-VAPOR DARK",     "Dark poisoned spectre with toxic yellow-green aura + glowing pupils.",                build_nightvapor_dead),
]


# ── layout helpers ───────────────────────────────────────────────────────────

NATIVE = (SPRITE_W + 4, SPRITE_H + 4)   # outlined body padded by _add_outline
ZOOM   = 4
ZOOMED = (NATIVE[0] * ZOOM, NATIVE[1] * ZOOM)

PANEL_W = 1200
PANEL_H = 200
PANEL_PAD = 16
PANEL_GAP = 12


def _panel_card(label, blurb, build_fn):
    """One panel: native sprite (left), 4× zoom (right), header text on top."""
    card = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    # Rounded-rect card background
    pygame.draw.rect(card, CARD_BG, card.get_rect(), border_radius=10)
    pygame.draw.rect(card, CARD_EDGE, card.get_rect(), width=1, border_radius=10)

    # Header
    _text(card, label, (PANEL_PAD, 10), size=18, color=UI_GOLD)
    _text(card, blurb, (PANEL_PAD, 34), size=13, color=TEXT_LO)

    # Build sprite — use _add_outline so dead-Pip pops on the teal card
    sprite = _add_outline(build_fn(WING_ANGLE))
    sw, sh = sprite.get_size()
    zoomed = pygame.transform.scale(sprite, (sw * ZOOM, sh * ZOOM))

    # Native swatch (dawn-teal patch) on the left
    art_y = 60
    sw_box = pygame.Rect(PANEL_PAD, art_y, sw + 16, sh + 16)
    pygame.draw.rect(card, BG_DAWN, sw_box, border_radius=6)
    pygame.draw.rect(card, CARD_EDGE, sw_box, width=1, border_radius=6)
    card.blit(sprite, (sw_box.x + 8, sw_box.y + 8))
    _text(card, "1x native", (sw_box.x, sw_box.bottom + 4), size=10, color=TEXT_LO, shadow=False)

    # 4× zoom box on the right
    zoom_box = pygame.Rect(PANEL_PAD + sw_box.w + 28, art_y, zoomed.get_width() + 16, zoomed.get_height() + 16)
    pygame.draw.rect(card, BG_DAWN, zoom_box, border_radius=6)
    pygame.draw.rect(card, CARD_EDGE, zoom_box, width=1, border_radius=6)
    card.blit(zoomed, (zoom_box.x + 8, zoom_box.y + 8))
    _text(card, f"{ZOOM}x zoom (palette + eye detail)", (zoom_box.x, zoom_box.bottom + 4),
          size=10, color=TEXT_LO, shadow=False)

    return card


def _crossfade_strip(width):
    """3-frame cross-fade preview using palette E (NIGHT-VAPOR) — the
    strongest read at small size. Ship-time logic: blit the dead frame
    over the alive frame with set_alpha at increasing alpha."""
    height = 280
    strip = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(strip, CARD_BG, strip.get_rect(), border_radius=10)
    pygame.draw.rect(strip, CARD_EDGE, strip.get_rect(), width=1, border_radius=10)

    _text(strip, "3-frame cross-fade preview — t = 33%, 67%, 100% (palette E)",
          (PANEL_PAD, 10), size=16, color=UI_CREAM)
    _text(strip, "Ship-time logic: dead.set_alpha(int(255 * t)); screen.blit(alive); screen.blit(dead).",
          (PANEL_PAD, 32), size=12, color=TEXT_LO)

    alive = _add_outline(_build_frame(WING_ANGLE))
    dead_full = _add_outline(build_nightvapor_dead(WING_ANGLE))

    frames = [
        (0.33, "t = 33%"),
        (0.67, "t = 67%"),
        (1.00, "t = 100%"),
    ]

    # Three frame columns — each shows native (top) and 4× zoom (bottom)
    col_w = width // 3
    for col, (t, label) in enumerate(frames):
        cx = col * col_w + col_w // 2

        # Composite alive + (dead at alpha t)
        comp = pygame.Surface(alive.get_size(), pygame.SRCALPHA)
        comp.blit(alive, (0, 0))
        dead = dead_full.copy()
        dead.set_alpha(int(255 * t))
        comp.blit(dead, (0, 0))

        nw, nh = comp.get_size()
        zoomed = pygame.transform.scale(comp, (nw * ZOOM, nh * ZOOM))

        # Native swatch on top
        native_box = pygame.Rect(cx - (nw + 16) // 2, 58, nw + 16, nh + 16)
        pygame.draw.rect(strip, BG_DAWN, native_box, border_radius=6)
        pygame.draw.rect(strip, CARD_EDGE, native_box, width=1, border_radius=6)
        strip.blit(comp, (native_box.x + 8, native_box.y + 8))

        # 4× zoom directly under
        zw, zh = zoomed.get_size()
        zoom_box = pygame.Rect(cx - (zw + 16) // 2, native_box.bottom + 8, zw + 16, zh + 16)
        pygame.draw.rect(strip, BG_DAWN, zoom_box, border_radius=6)
        pygame.draw.rect(strip, CARD_EDGE, zoom_box, width=1, border_radius=6)
        strip.blit(zoomed, (zoom_box.x + 8, zoom_box.y + 8))

        # Label centred under the zoom box
        f = _font(14)
        img = f.render(label, True, UI_GOLD)
        sh = f.render(label, True, (0, 0, 0))
        r = img.get_rect(center=(cx, zoom_box.bottom + 14))
        strip.blit(sh, (r.x + 1, r.y + 1))
        strip.blit(img, r.topleft)

    return strip


# ── main render ──────────────────────────────────────────────────────────────

def render():
    title_h = 90
    panels_h = (PANEL_H + PANEL_GAP) * len(PANELS) - PANEL_GAP
    strip_h = 280
    margin_x = 20
    margin_top = 14
    margin_bot = 22
    gap = 24

    total_w = PANEL_W + margin_x * 2
    total_h = title_h + margin_top + panels_h + gap + strip_h + margin_bot

    surf = pygame.Surface((total_w, total_h))
    surf.fill(BG_DAWN)

    # Title bar
    title_rect = pygame.Rect(0, 0, total_w, title_h)
    pygame.draw.rect(surf, (28, 32, 50), title_rect)
    pygame.draw.line(surf, CARD_EDGE, (0, title_h - 1), (total_w, title_h - 1), 1)

    title_font = _font(28)
    sub_font   = _font(15)
    title_img  = title_font.render("DEAD PIP v3 — Round 1 (palette repaint, ghost-quality bar)", True, UI_GOLD)
    title_sh   = title_font.render("DEAD PIP v3 — Round 1 (palette repaint, ghost-quality bar)", True, (0, 0, 0))
    sub_img    = sub_font.render(
        "5 candidate dead-Pip palettes via _build_parrot_with_palette + 3-frame cross-fade preview",
        True, TEXT_HI)
    sub_sh     = sub_font.render(
        "5 candidate dead-Pip palettes via _build_parrot_with_palette + 3-frame cross-fade preview",
        True, (0, 0, 0))

    tx = total_w // 2 - title_img.get_width() // 2
    surf.blit(title_sh, (tx + 2, 18))
    surf.blit(title_img, (tx, 16))
    sx = total_w // 2 - sub_img.get_width() // 2
    surf.blit(sub_sh, (sx + 1, 56))
    surf.blit(sub_img, (sx, 55))

    # Panel column
    py = title_h + margin_top
    for label, blurb, fn in PANELS:
        card = _panel_card(label, blurb, fn)
        surf.blit(card, (margin_x, py))
        py += PANEL_H + PANEL_GAP

    # Cross-fade strip
    strip = _crossfade_strip(PANEL_W)
    surf.blit(strip, (margin_x, py - PANEL_GAP + gap))

    return surf


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = render()
    pygame.image.save(out, str(OUT_PATH))
    print(f"wrote {OUT_PATH}  ({out.get_width()}x{out.get_height()})")


if __name__ == "__main__":
    main()

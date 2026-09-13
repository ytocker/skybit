"""Render docs/dead_pip_v3/round_4_options.png — round-4 decision sheet.

Round 3 shipped the sunglasses-ON-vs-OFF comparison but the art-director
flagged six issues — title clipping, mis-anchored tongue, weak "dead"
read on ON variants, missing fallen-aviators under OFF birds, B vs C
reduced to a palette swap, and small mushy X-eyes. This round fixes all
six while preserving what the AD called working: the gold E-ribbon
baseline up top, the 2×2 grid + consistent panel chrome + two-line
labels, both palettes sitting in the night-vapor family, the head-down
slump pose, and equal panel/bird sizes across the four candidates.

Design axis differentiation (issue 5):
  • B = "comic KO" — clean cartoon-dead. Crack + brow + chips on ON;
    bold X-eyes on OFF; nothing else.
  • C = "theatrical decay" — grungy. Adds a poison aura around the
    head, stink lines drifting up, the wing recoloured to wing_dark
    (withered limb), and a longer curving tongue.
"""
import math
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.parrot import SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline
from game.dollar_parrot_ghost import _build_parrot_with_palette
from game.dollar_parrot_dead import (
    P_NIGHTVAPOR, P_CHARTREUSE, P_BRUISE,
    LENS_L, LENS_R, TOXIC_AURA,
    build_nightvapor_dead,
)
from game.draw import blit_glow


# ── output target ────────────────────────────────────────────────────────────

OUT_PATH = pathlib.Path(__file__).parent.parent / "docs" / "dead_pip_v3" / "round_4_options.png"

BG_CHARCOAL = (40, 40, 48)
COL_TINT    = (48, 48, 56)   # subtle column tint to make the ON/OFF axis read
PANEL_BG    = (28, 28, 36)
PANEL_EDGE  = (70, 70, 84)
TEXT_HI     = (235, 240, 250)
TEXT_LO     = (170, 175, 190)
GOLD        = (235, 200, 90)
RIBBON_BG   = (50, 50, 60)

# Single neutral wing pose so reviewers compare like-for-like across panels.
WING_ANGLE = _WING_ANGLES[1]   # 20°

# Beak bottom-point anchor — the beak polygon in _build_parrot_with_palette
# is [(55,21), (61,24), (58,28), (52,26)] in sprite-local coords. (58, 28)
# is the lower-front tip the tongue should drape over.
BEAK_BOTTOM = (58, 28)

# Native sprite is 64×60. We pad the bottom 8 px so the limp tongue drops
# in native pixels (sharper detail after the 3× upscale).
PARROT_SURF_H = SPRITE_H + 8

ZOOM = 3   # native sprite is 64×68 (padded) → panel sprite area is 192×204.


# ── small text helper using bundled font ─────────────────────────────────────

def _font(size: int) -> pygame.font.Font:
    """Bundled bold ttf — the only font we ship — keeps every sheet on-brand."""
    path = pathlib.Path(__file__).parent.parent / "game" / "assets" / "LiberationSans-Bold.ttf"
    return pygame.font.Font(str(path), size)


def _text(surf, msg, center, size=14, color=TEXT_HI, shadow=True):
    f = _font(size)
    img = f.render(msg, True, color)
    rect = img.get_rect(center=center)
    if shadow:
        sh = f.render(msg, True, (0, 0, 0))
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect.topleft)


# ── shared cartoon-dead overlays ────────────────────────────────────────────

def _draw_tongue(body, palette_key, droopy=False):
    """Limp tongue dropping straight down from the beak's lower vertex
    BEAK_BOTTOM (58, 28). Drawn into the PARROT SURFACE at native resolution
    so pixel detail upscales 3× with the bird, not after at panel res.

    2 px wide × 6 px tall (B) — and a longer 8 px curving variant for C
    (droopy=True) so the "C = theatrical decay" row reads as more rotten.
    1 px upward overlap into the beak (`ay - 1` start) so the tongue
    visually originates from the mouth rather than floating below it.
    """
    if palette_key == "B":
        body_col = (180, 50, 50)
        edge_col = (0, 0, 0)
        glint    = (220, 90, 90)
    else:
        body_col = (140, 40, 60)
        edge_col = (0, 0, 0)
        glint    = (170, 70, 90)

    ax, ay = BEAK_BOTTOM
    if droopy:
        # Curving 2 px-wide, 8 px-tall tongue — curls 1 px right at the tip
        # so it reads as "lolling sideways" rather than a straight ruler.
        # Build a column of 1×1 pixels then nudge the bottom three rows right.
        x = ax - 1
        for dy in range(8):
            curl = 0
            if dy >= 5:
                curl = 1
            if dy == 7:
                curl = 2
            pygame.draw.rect(body, body_col, (x + curl, ay - 1 + dy, 2, 1))
        # Black outline along the left edge + bottom for silhouette pop.
        for dy in range(8):
            curl = 0
            if dy >= 5:
                curl = 1
            if dy == 7:
                curl = 2
            pygame.draw.rect(body, edge_col, (x + curl - 0, ay - 1 + dy + (1 if dy == 7 else 0), 1, 1))
        # Bottom dark line.
        pygame.draw.line(body, edge_col, (x + 2, ay + 7), (x + 3, ay + 7), 1)
        # Wet highlight on the upper-left edge.
        pygame.draw.line(body, glint, (x, ay), (x, ay + 2), 1)
    else:
        # Clean B-style cartoon tongue: 2×6 px column.
        x = ax - 1
        rect = pygame.Rect(x, ay - 1, 2, 6)
        pygame.draw.rect(body, body_col, rect)
        # 1 px black outline along the bottom + right edge.
        pygame.draw.line(body, edge_col, (rect.x, rect.bottom - 1),
                         (rect.right - 1, rect.bottom - 1), 1)
        pygame.draw.line(body, edge_col, (rect.right - 1, rect.y),
                         (rect.right - 1, rect.bottom - 1), 1)
        # Wet highlight on the upper-left edge.
        pygame.draw.line(body, glint, (rect.x, rect.y), (rect.x, rect.y + 2), 1)


def _draw_cracked_lens(body, palette_key):
    """Bright crack-fork that BREAKS THE LENS SILHOUETTE — Y-shape extending
    2 px ABOVE the lens rim and a downward fork 2 px BELOW it so the damage
    reads as "shattered glass" rather than as a lens highlight contained
    inside the rim.

    Lens frame radius is 7 (drawn at r+1 = 7 inside `_draw_lenses`), so
    rim-top from each centre is y-7 and rim-bottom is y+7.
    """
    if palette_key == "B":
        bright = (255, 240, 200)   # fluorescent — pops on B's near-black lens
        shadow = (15, 22, 18)
    else:
        bright = (255, 240, 200)
        shadow = (40, 25, 50)

    for cx, cy in (LENS_L, LENS_R):
        # Drop-shadow pass 1 px down/right of the bright crack so it reads
        # as raised damage rather than a flat decal.
        pygame.draw.line(body, shadow, (cx + 1, cy - 8), (cx + 1, cy),     1)
        pygame.draw.line(body, shadow, (cx + 1, cy),     (cx - 2, cy - 4), 1)
        pygame.draw.line(body, shadow, (cx + 1, cy),     (cx + 4, cy - 4), 1)
        pygame.draw.line(body, shadow, (cx + 1, cy),     (cx,     cy + 4), 1)
        pygame.draw.line(body, shadow, (cx + 1, cy + 4), (cx - 2, cy + 8), 1)
        pygame.draw.line(body, shadow, (cx + 1, cy + 4), (cx + 3, cy + 8), 1)
        # Bright crack — upper trunk extends 2 px above lens rim (rim-top = cy-7
        # → crack-top = cy-9), arms branch from the centre, lower fork extends
        # 2 px below the bottom rim (rim-bottom = cy+7 → crack-bottom = cy+9).
        pygame.draw.line(body, bright, (cx, cy - 9), (cx, cy),     1)   # upper trunk
        pygame.draw.line(body, bright, (cx, cy),     (cx - 3, cy - 4), 1)  # up-left arm
        pygame.draw.line(body, bright, (cx, cy),     (cx + 3, cy - 4), 1)  # up-right arm
        pygame.draw.line(body, bright, (cx, cy),     (cx - 1, cy + 4), 1)  # lower trunk
        pygame.draw.line(body, bright, (cx - 1, cy + 4), (cx - 3, cy + 9), 1)  # lower-left fork
        pygame.draw.line(body, bright, (cx - 1, cy + 4), (cx + 2, cy + 9), 1)  # lower-right fork


def _draw_slanted_brow(body, palette_key):
    """Comic 'angry/distressed' brow line slanting OUTWARD from each lens.
    2 px thick (issue 3c), pushed to near-black so it reads with strong
    contrast against the head_cheek tones.
    """
    if palette_key == "B":
        col = (15, 20, 8)
    else:
        col = (20, 12, 25)

    lx, ly = LENS_L
    # Inner-top of left lens → up 5 px and outward (left) 4 px.
    pygame.draw.line(body, col, (lx + 2, ly - 5), (lx - 2, ly - 9), 2)
    rx, ry = LENS_R
    # Inner-top of right lens → up 5 px and outward (right) 4 px.
    pygame.draw.line(body, col, (rx - 2, ry - 5), (rx + 2, ry - 9), 2)


def _draw_lens_chips(body, palette_key):
    """Tiny lens-chip triangles falling away below each lens (~3-6 px below
    the centre) in lens_frame colour — reads as "chips of the lens broke
    off." Two chips per lens, ~2 px on a side, rotated different ways.
    """
    if palette_key == "B":
        col = (70, 90, 20)
    else:
        col = (95, 60, 115)

    for cx, cy in (LENS_L, LENS_R):
        # Chip 1: small triangle ~4 px below + 2 px left of centre.
        pygame.draw.polygon(body, col, [
            (cx - 3, cy + 9),
            (cx - 1, cy + 9),
            (cx - 2, cy + 11),
        ])
        # Chip 2: smaller triangle ~6 px below + 2 px right of centre.
        pygame.draw.polygon(body, col, [
            (cx + 2, cy + 10),
            (cx + 4, cy + 10),
            (cx + 3, cy + 12),
        ])


def _draw_x_eyes(body, palette_key):
    """Bold cartoon X-eyes painted on bare head_main skin (OFF builders pass
    draw_lenses=False). Stroke width 2, reach ±4 px from each lens centre
    (so each X spans ~7 px across), near-black so it's the LOUDEST mark
    on the head. Universal warm-white highlight along the upper-left arm
    of EACH stroke so the X reads as inked rather than smudged.
    """
    if palette_key == "B":
        ink_col = (20, 25, 15)
    else:
        ink_col = (25, 12, 30)
    glint_col = (245, 245, 200) if palette_key == "B" else (220, 215, 180)

    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.line(body, ink_col, (cx - 4, cy - 4), (cx + 4, cy + 4), 2)
        pygame.draw.line(body, ink_col, (cx - 4, cy + 4), (cx + 4, cy - 4), 2)
        # Warm-white highlight on the upper-left arm of BOTH strokes.
        # Down-right diagonal: upper-left half is (-4,-4) → (0,0).
        pygame.draw.line(body, glint_col, (cx - 4, cy - 5), (cx - 1, cy - 2), 1)
        # Up-right diagonal: upper-left half is (-4,+4) → (0,0); "upper-left
        # arm" reads as the segment closer to the top-left of the cross.
        pygame.draw.line(body, glint_col, (cx - 4, cy + 3), (cx - 1, cy), 1)


# ── C-row grungy extras (issue 5) ───────────────────────────────────────────

def _draw_poison_ring(out, cx=48, cy=20, r=14):
    """Thin sickly-green ring around the bird's head — vapour aura that
    sells C as theatrical decay. Drawn into the OUT surface (outside the
    body) so it can fall slightly behind the head silhouette."""
    ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(ring, (180, 200, 100, 110), (r + 2, r + 2), r, 1)
    pygame.draw.circle(ring, (180, 200, 100, 70),  (r + 2, r + 2), r + 1, 1)
    out.blit(ring, (cx - r - 2, cy - r - 2))


def _draw_stink_lines(out):
    """2–3 wavy 1-px vertical squiggles drifting up above the head — the
    visual shorthand for "this thing reeks." Drawn into the OUT surface
    so they sit above the bird in sprite-local coords (37, 38, 41 are the
    x's; y rises from ~12 down to ~3)."""
    col = (150, 170, 80)
    # Three columns at x = 40, 45, 50 (above the head crown at y≈14-16).
    for base_x, phase, height in ((40, 0.0, 5), (45, 1.4, 5), (50, 0.7, 4)):
        for i in range(height):
            wob = int(math.sin(phase + i * 1.1))
            pygame.draw.rect(out, col, (base_x + wob, 8 - i, 1, 1))


def _withered_palette(P):
    """Return a shallow copy of P with the wing tinted to wing_dark across
    its layers — "withered limb" reading for C. Keeps wing_dark itself so
    the feather-divider lines still register as darker than the slab."""
    Q = {**P}
    Q['wing_main']      = P['wing_dark']
    Q['wing_tip']       = P['wing_dark']
    Q['wing_secondary'] = P['wing_dark']
    Q['wing_highlight'] = None      # kill the crisp white edge so it slumps
    return Q


# ── per-variant builders ────────────────────────────────────────────────────
# Each returns an OUTLINED surface (drop-shadow + body outline). The
# `_add_outline()` call is the LAST step before the panel-composite pass.

def _aura(out, alpha=110):
    """Shared toxic aura — keeps B/C in the same E-family 'wrongness' world."""
    blit_glow(out, 32, 30, 24, TOXIC_AURA, alpha=alpha)


def _new_parrot_surface():
    """Padded native parrot surface — 64×68 — so a tongue drawn at sprite-
    local y=28..36 fits inside the same surface that gets outlined + scaled
    3×. Native-resolution tongue detail upscales with the bird this way."""
    return pygame.Surface((SPRITE_W, PARROT_SURF_H), pygame.SRCALPHA)


def build_b_sunglasses_on(angle):
    """B refined ON — clean cartoon KO. Darkens lens body slightly via a
    palette override so the bright crack pops as damage, not a highlight;
    crack breaks the silhouette top + bottom; thick near-black brow; chip
    triangles fall away under each lens. Limp 2×6 tongue.
    """
    out = _new_parrot_surface()
    _aura(out)
    P = {**P_CHARTREUSE, 'lens_body': (6, 12, 4)}   # darken ~25%
    body = _build_parrot_with_palette(angle, P, draw_lenses=True)
    surf = _new_parrot_surface()
    surf.blit(body, (0, 0))
    _draw_lens_chips(surf, "B")
    _draw_slanted_brow(surf, "B")
    _draw_cracked_lens(surf, "B")
    _draw_tongue(surf, "B", droopy=False)
    out.blit(surf, (0, 0))
    return _add_outline(out)


def build_b_sunglasses_off(angle):
    """B shades-OFF — bold black X-eyes on bare head + 2×6 tongue. The
    fallen-aviators cue sits in the panel under the bird (drawn outside
    the parrot surface for panel-floor anchoring)."""
    out = _new_parrot_surface()
    _aura(out)
    body = _build_parrot_with_palette(angle, P_CHARTREUSE, draw_lenses=False)
    surf = _new_parrot_surface()
    surf.blit(body, (0, 0))
    _draw_x_eyes(surf, "B")
    _draw_tongue(surf, "B", droopy=False)
    out.blit(surf, (0, 0))
    return _add_outline(out)


def build_c_sunglasses_on(angle):
    """C refined ON — theatrical decay. Wing recoloured to wing_dark
    (withered slump), darker lens body so the white crack reads as
    damage, brow + chips, droopier curving tongue, poison aura ring +
    stink lines drawn outside the body for atmosphere."""
    out = _new_parrot_surface()
    _aura(out)
    # Poison aura ring sits BEHIND the bird so the head silhouette overlaps
    # the front of the ring — sells "vapour wrapping the head."
    _draw_poison_ring(out)
    P = _withered_palette(P_BRUISE)
    P = {**P, 'lens_body': (119, 126, 70)}   # 0.7× the original sickly green
    body = _build_parrot_with_palette(angle, P, draw_lenses=True)
    surf = _new_parrot_surface()
    surf.blit(body, (0, 0))
    _draw_lens_chips(surf, "C")
    _draw_slanted_brow(surf, "C")
    _draw_cracked_lens(surf, "C")
    _draw_tongue(surf, "C", droopy=True)
    out.blit(surf, (0, 0))
    _draw_stink_lines(out)
    return _add_outline(out)


def build_c_sunglasses_off(angle):
    """C shades-OFF — theatrical decay without the shades. Same withered
    wing + aura + stink lines. Loud black X-eyes on the bare bruise-
    coloured head, droopier curving tongue."""
    out = _new_parrot_surface()
    _aura(out)
    _draw_poison_ring(out)
    P = _withered_palette(P_BRUISE)
    body = _build_parrot_with_palette(angle, P, draw_lenses=False)
    surf = _new_parrot_surface()
    surf.blit(body, (0, 0))
    _draw_x_eyes(surf, "C")
    _draw_tongue(surf, "C", droopy=True)
    out.blit(surf, (0, 0))
    _draw_stink_lines(out)
    return _add_outline(out)


def build_e_baseline(angle):
    """Untouched ship lead. Padded to the same 64×68 canvas as the candidate
    panels so visual scale stays identical across all five sprites."""
    src = build_nightvapor_dead(angle)
    padded = _new_parrot_surface()
    padded.blit(src, (0, 0))
    return _add_outline(padded)


# ── fallen-aviators silhouette (mandatory under each OFF bird) ──────────────

def _fallen_aviators(surf, center, palette_key):
    """Small tilted silhouette of dropped aviators sitting on the panel
    "floor" below the bird — the storytelling beat that distinguishes
    "SHADES OFF" from "Pip without sunglasses." Two lens_frame-coloured
    discs joined by a 1 px bridge, rotated ~30° clockwise, slight
    horizontal offset so it doesn't sit directly under the body centre.

    Mandatory this round (issue 4) — drawn in the panel pass.
    """
    if palette_key == "B":
        frame_col = (70, 90, 20)
    else:
        frame_col = (95, 60, 115)

    # Raw sprite at 3× the native size of the cue so it visually matches
    # the 3×-zoomed parrot above it.
    s = 3
    raw_w, raw_h = 22 * s, 10 * s
    raw = pygame.Surface((raw_w, raw_h), pygame.SRCALPHA)
    # Soft drop shadow on the "floor" below the cue.
    pygame.draw.ellipse(raw, (0, 0, 0, 90), (1, raw_h - 4 * s, raw_w - 2, 4 * s))
    # Lens discs (~3 px radius native → 9 px scaled).
    pygame.draw.circle(raw, frame_col, (4 * s, 4 * s), 3 * s)
    pygame.draw.circle(raw, frame_col, (18 * s, 4 * s), 3 * s)
    # Inner black lens body so the rim reads as a frame.
    pygame.draw.circle(raw, (12, 12, 16), (4 * s, 4 * s), 2 * s)
    pygame.draw.circle(raw, (12, 12, 16), (18 * s, 4 * s), 2 * s)
    # Bridge — 1 px native → 3 px scaled.
    pygame.draw.line(raw, frame_col, (7 * s, 4 * s), (15 * s, 4 * s), s)
    # Crisp 1 px outline around each disc for definition.
    pygame.draw.circle(raw, (0, 0, 0), (4 * s, 4 * s), 3 * s, 1)
    pygame.draw.circle(raw, (0, 0, 0), (18 * s, 4 * s), 3 * s, 1)
    # Tiny glints so the lying glass still reads as glass.
    pygame.draw.circle(raw, (220, 220, 230), (3 * s, 3 * s), 1)
    pygame.draw.circle(raw, (220, 220, 230), (17 * s, 3 * s), 1)

    rot = pygame.transform.rotate(raw, -30)   # ~30° clockwise
    rect = rot.get_rect(center=center)
    surf.blit(rot, rect.topleft)


# ── panel composition ──────────────────────────────────────────────────────

PANEL_W = 248
PANEL_H = 280   # taller than round 3 so the mandatory fallen-shades cue
                 # has clear floor space below the (now padded) parrot.


def _panel(label_top, label_sub, build_fn, palette_key, draw_fallen, bg_tint=None):
    """One labelled panel: charcoal card, 3× outlined parrot, mandatory
    fallen-aviators cue on OFF panels, two-line label strip pinned to the
    bottom of the card.
    """
    card = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    bg = PANEL_BG if bg_tint is None else bg_tint
    pygame.draw.rect(card, bg, card.get_rect(), border_radius=10)
    pygame.draw.rect(card, PANEL_EDGE, card.get_rect(), width=1, border_radius=10)

    sprite = build_fn(WING_ANGLE)
    sw, sh = sprite.get_size()                       # outlined size is 68×72
    zoomed = pygame.transform.scale(sprite, (sw * ZOOM, sh * ZOOM))
    zw, zh = zoomed.get_size()
    art_x = (PANEL_W - zw) // 2
    art_y = 16
    card.blit(zoomed, (art_x, art_y))

    # Mandatory fallen aviators on shades-OFF panels. Pinned ~12 px below
    # the parrot's feet at native res (36 px at 3× scale) and pushed ~6 px
    # right (18 px scaled) so it reads as "fell to the side."
    if draw_fallen:
        cue_x = PANEL_W // 2 + 18
        cue_y = art_y + zh + 18
        _fallen_aviators(card, (cue_x, cue_y), palette_key)

    # Label strip — pinned to panel bottom.
    _text(card, label_top, (PANEL_W // 2, PANEL_H - 28), size=14, color=GOLD)
    _text(card, label_sub, (PANEL_W // 2, PANEL_H - 12), size=11, color=TEXT_LO)
    return card


def _baseline_panel():
    """E panel — slim full-width strip above the 2×2 grid, scans as the
    control rather than as a fifth candidate. Same charcoal card so the
    visual language stays unified across all five panels."""
    card_w = PANEL_W * 2 + 16
    card_h = 248
    card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(card, PANEL_BG, card.get_rect(), border_radius=10)
    pygame.draw.rect(card, PANEL_EDGE, card.get_rect(), width=1, border_radius=10)

    sprite = build_e_baseline(WING_ANGLE)
    sw, sh = sprite.get_size()
    zoomed = pygame.transform.scale(sprite, (sw * ZOOM, sh * ZOOM))
    zw, zh = zoomed.get_size()
    art_x = (card_w - zw) // 2
    art_y = 16
    card.blit(zoomed, (art_x, art_y))

    ribbon = pygame.Rect(16, 16, 108, 24)
    pygame.draw.rect(card, RIBBON_BG, ribbon, border_radius=4)
    pygame.draw.rect(card, GOLD, ribbon, width=1, border_radius=4)
    _text(card, "SHIPPED", ribbon.center, size=13, color=GOLD)

    _text(card, "E. NIGHT-VAPOR  (baseline — unchanged)",
          (card_w // 2, card_h - 28), size=15, color=GOLD)
    _text(card, "Reference panel. The B and C candidates below are the decision.",
          (card_w // 2, card_h - 12), size=11, color=TEXT_LO)
    return card


# ── main composition ───────────────────────────────────────────────────────

def render():
    margin_x = 20
    margin_top = 14
    margin_bot = 20
    title_h = 82
    section_gap = 18
    row_gap = 16
    col_gap = 16

    grid_w = PANEL_W * 2 + col_gap
    grid_h = PANEL_H * 2 + row_gap
    baseline_h = 248

    title_str = "DEAD PIP v3  ·  round 4 — sunglasses-ON vs sunglasses-OFF (X-eyes)"
    sub_str   = "E baseline (shipped, top) + B and C variants (decision: which goes back into the game)."

    # Measure title BEFORE deciding canvas width so we can guarantee ≥ 12 px
    # of left/right padding (issue 1). If the grid-derived width is too
    # narrow, widen the canvas instead of truncating the title.
    MIN_PADDING = 12
    title_font = _font(22)
    sub_font   = _font(13)
    title_w, _title_h_unused = title_font.size(title_str)
    sub_w, _ = sub_font.size(sub_str)
    min_canvas_for_title = title_w + MIN_PADDING * 2
    min_canvas_for_sub   = sub_w   + MIN_PADDING * 2
    total_w = max(grid_w + margin_x * 2, min_canvas_for_title, min_canvas_for_sub)

    # Recentre margin_x if widening the canvas pushed it past the grid+margins.
    margin_x = (total_w - grid_w) // 2

    total_h = title_h + margin_top + baseline_h + section_gap + grid_h + margin_bot

    surf = pygame.Surface((total_w, total_h))
    surf.fill(BG_CHARCOAL)

    # OFF-column background tint — subtle near-charcoal shift so the
    # comparison axis (ON ← left | OFF → right) reads instantly without
    # using a bright divider that would fight the parrots (AD optional polish).
    off_col_x = margin_x + PANEL_W + col_gap // 2 - 4
    off_col_w = PANEL_W + col_gap // 2 + 8
    off_col_y = title_h + margin_top + baseline_h + section_gap - 6
    off_col_h = grid_h + 12
    pygame.draw.rect(surf, COL_TINT,
                     (off_col_x, off_col_y, off_col_w, off_col_h),
                     border_radius=14)

    # Title bar.
    title_rect = pygame.Rect(0, 0, total_w, title_h)
    pygame.draw.rect(surf, (24, 24, 32), title_rect)
    pygame.draw.line(surf, PANEL_EDGE, (0, title_h - 1), (total_w, title_h - 1), 1)

    timg = title_font.render(title_str, True, GOLD)
    tsh  = title_font.render(title_str, True, (0, 0, 0))
    simg = sub_font.render(sub_str, True, TEXT_HI)
    ssh  = sub_font.render(sub_str, True, (0, 0, 0))

    tx = total_w // 2 - timg.get_width() // 2
    surf.blit(tsh, (tx + 2, 20))
    surf.blit(timg, (tx, 18))
    sx = total_w // 2 - simg.get_width() // 2
    surf.blit(ssh, (sx + 1, 52))
    surf.blit(simg, (sx, 51))

    # Padding assert — flag regressions in any future round that crowds
    # the title against the canvas edge.
    left_pad = tx
    right_pad = total_w - (tx + timg.get_width())
    assert left_pad >= MIN_PADDING and right_pad >= MIN_PADDING, (
        f"title padding too small: left={left_pad}px right={right_pad}px "
        f"(need ≥ {MIN_PADDING}px both sides)")
    print(f"title: width={timg.get_width()}px  canvas={total_w}px  "
          f"left_pad={left_pad}px  right_pad={right_pad}px  (min {MIN_PADDING}px)")

    # Baseline E strip.
    y = title_h + margin_top
    baseline = _baseline_panel()
    surf.blit(baseline, (margin_x, y))
    y += baseline_h + section_gap

    # 2×2 grid of B/C × ON/OFF panels. Right column carries the COL_TINT
    # background so the ON/OFF axis reads at a glance.
    # Sublabels measured to fit inside the 248-px panel with breathing room
    # (~225 px max at 11 pt LiberationSans-Bold) so labels never clip.
    panels = [
        ("B · SUNGLASSES ON",  "comic KO — crack + brow + chips",          build_b_sunglasses_on,  "B", False, None),
        ("B · SHADES OFF",     "comic KO — X-eyes + fallen shades",        build_b_sunglasses_off, "B", True,  None),
        ("C · SUNGLASSES ON",  "decay — aura + stink + droopy tongue",     build_c_sunglasses_on,  "C", False, None),
        ("C · SHADES OFF",     "decay — X-eyes + aura + fallen shades",    build_c_sunglasses_off, "C", True,  None),
    ]
    for i, (label, sub, fn, key, fallen, bg_tint) in enumerate(panels):
        row = i // 2
        col = i % 2
        px = margin_x + col * (PANEL_W + col_gap)
        py = y + row * (PANEL_H + row_gap)
        surf.blit(_panel(label, sub, fn, key, fallen, bg_tint), (px, py))

    return surf


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = render()
    pygame.image.save(out, str(OUT_PATH))
    size = OUT_PATH.stat().st_size
    print(f"wrote {OUT_PATH}  ({out.get_width()}x{out.get_height()})  "
          f"file={size / 1024:.1f} KB")


if __name__ == "__main__":
    main()

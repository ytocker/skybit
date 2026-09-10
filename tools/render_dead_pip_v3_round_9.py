"""Render docs/dead_pip_v3/round_7_options.png — round-7 sheet.

Round 6 landed the bold X on B-ON cleanly: on a near-black lens body
(6, 12, 4) the chartreuse X core (225, 235, 130) and warmer highlight
(255, 245, 200) stack bright-on-dark and read as one X. C-ON did not
land: lens body is olive (119, 126, 70) and the round-6 X core was the
DARKER eggplant (95, 60, 115) with the LIGHTER eggplant (165, 130, 185)
as the highlight. With a dark core and a light highlight on a mid-value
lens, the eye locked onto the bright highlight slashes and read two
parallel light diagonals per arm — a plaid texture, not a unified X.

Round 7 inverts C's value relationship so the lightest tone wins and the
secondary reinforces it (same idiom as B-ON, opposite palette):

 - C-ON X core      = (165, 130, 185)   — was the round-6 highlight; now
                                           CORE. Sits clearly above the
                                           olive lens body in value.
 - C-ON X highlight = (220, 200, 230)   — NEW lighter eggplant-tinted
                                           near-white. ~50 brighter per
                                           channel than the core, mirrors
                                           B's core → highlight jump.
 - C-ON stroke width drops 3 → 2; bigger 3 px stroke at small scale
                                           fed the plaid read by giving
                                           the core+highlight more space
                                           to separate. 2 px reads
                                           cleaner. B-ON stays at 3.
 - C-ON arm reach grows ±5 → ±6 so the thinner 2 px stroke still pokes
                                           ~1 px past the lens rim
                                           (radius 6) on every side and
                                           visibly breaks the silhouette.

Everything else — E baseline + ribbon, B-ON (chartreuse core stamp at
stroke 3), both OFF panels (X-eyes + tongue + fallen aviators), brow +
chips on ON, mouth-shut on ON, C-row aura + stink + withered wing, panel
chrome, column tint + divider, sub-labels — is identical to round 6.
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

OUT_PATH = pathlib.Path(__file__).parent.parent / "docs" / "dead_pip_v3" / "round_9_options.png"

BG_CHARCOAL = (40, 40, 48)
COL_TINT    = (40, 40, 52)
DIVIDER_COL = (60, 60, 70)
PANEL_BG    = (28, 28, 36)
PANEL_EDGE  = (70, 70, 84)
TEXT_HI     = (235, 240, 250)
TEXT_LO     = (170, 175, 190)
GOLD        = (235, 200, 90)
RIBBON_BG   = (50, 50, 60)

# Single neutral wing pose so reviewers compare like-for-like across panels.
WING_ANGLE = _WING_ANGLES[1]   # 20°

# Beak bottom-point anchor — beak polygon vertex (58, 28) is the lower-front
# tip the tongue drapes over on OFF variants.
BEAK_BOTTOM = (58, 28)

# Native sprite is 64×60. Pad 8 px on the bottom so OFF-variant tongues drop
# in native pixels and stay crisp through the 3× upscale.
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
    """Limp tongue dropping from BEAK_BOTTOM (58, 28). OFF-variants only —
    ON variants keep mouth shut for the dignified-dead read. 2×6 px column
    for B; an 8 px curving variant for C so the theatrical-decay row reads
    as more rotten."""
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
        x = ax - 1
        for dy in range(8):
            curl = 0
            if dy >= 5:
                curl = 1
            if dy == 7:
                curl = 2
            pygame.draw.rect(body, body_col, (x + curl, ay - 1 + dy, 2, 1))
        for dy in range(8):
            curl = 0
            if dy >= 5:
                curl = 1
            if dy == 7:
                curl = 2
            pygame.draw.rect(body, edge_col, (x + curl - 0, ay - 1 + dy + (1 if dy == 7 else 0), 1, 1))
        pygame.draw.line(body, edge_col, (x + 2, ay + 7), (x + 3, ay + 7), 1)
        pygame.draw.line(body, glint, (x, ay), (x, ay + 2), 1)
    else:
        x = ax - 1
        rect = pygame.Rect(x, ay - 1, 2, 6)
        pygame.draw.rect(body, body_col, rect)
        pygame.draw.line(body, edge_col, (rect.x, rect.bottom - 1),
                         (rect.right - 1, rect.bottom - 1), 1)
        pygame.draw.line(body, edge_col, (rect.right - 1, rect.y),
                         (rect.right - 1, rect.bottom - 1), 1)
        pygame.draw.line(body, glint, (rect.x, rect.y), (rect.x, rect.y + 2), 1)


def _draw_bold_x_on_lens(body, palette_key):
    """LARGE BOLD palette-matched X stamped on each lens — replaces round 5's
    inside-lens crack-fork.

    B-ON, C-ON: stroke 2, reach ±3. Bold palette-coloured X centred on
    each lens, contained INSIDE the rim (lens radius 6) so the lens
    silhouette + tint still read. Bright crossing anchor + 1 px highlight
    slash give the "stamped X" pop without the arms overhanging.

    1 px highlight slash on the upper-left edge of each stroke for cartoon
    "wet pop"; light source is upper-left so both strokes share the same
    offset direction.

    No outline around the X — the brow above and chips below carry the
    damage cues, the X reads as a clean graphic stamp.
    """
    if palette_key == "B":
        # P_CHARTREUSE['head_crown'] = (225, 235, 130) — brightest hue in
        # B's palette; (255, 245, 200) is the same warm sheen round 5 used
        # for the fluorescent crack so the highlight family stays coherent.
        core      = (225, 235, 130)
        highlight = (255, 245, 200)
    else:
        # Round 7 inversion: light eggplant becomes the CORE and a
        # lighter near-white-eggplant becomes the HIGHLIGHT, so both X
        # values now sit clearly above the olive (119, 126, 70) lens
        # body — same bright-on-mid stamp idiom as B-ON.
        core      = (165, 130, 185)
        highlight = (220, 200, 230)
    stroke = 2
    reach  = 3

    for cx, cy in (LENS_L, LENS_R):
        # Two diagonals with palette-tuned stroke + reach.
        pygame.draw.line(body, core, (cx - reach, cy - reach),
                         (cx + reach, cy + reach), stroke)
        pygame.draw.line(body, core, (cx - reach, cy + reach),
                         (cx + reach, cy - reach), stroke)
        # 1 px highlight slash along the upper-left edge of each stroke.
        # Offset 1 px up + 1 px left so light reads as upper-left for both.
        pygame.draw.line(body, highlight,
                         (cx - reach - 1, cy - reach - 1),
                         (cx + reach - 1, cy + reach - 1), 1)
        pygame.draw.line(body, highlight,
                         (cx - reach - 1, cy + reach - 1),
                         (cx + reach - 1, cy - reach - 1), 1)
        # Crossing-pixel anchor: a 2x2 highlight block at the X centre
        # so the glyph reads as ONE stamped shape rather than two
        # passing-through slashes. Same idiom B's thicker strokes give
        # naturally; C needs the explicit knot at this scale.
        pygame.draw.rect(body, highlight, (cx - 1, cy - 1, 2, 2))


def _draw_slanted_brow(body, palette_key):
    """Comic 'angry/distressed' brow line slanting OUTWARD from each lens."""
    if palette_key == "B":
        col = (15, 20, 8)
    else:
        col = (20, 12, 25)

    lx, ly = LENS_L
    pygame.draw.line(body, col, (lx + 2, ly - 5), (lx - 2, ly - 9), 2)
    rx, ry = LENS_R
    pygame.draw.line(body, col, (rx - 2, ry - 5), (rx + 2, ry - 9), 2)


def _draw_lens_chips(body, palette_key):
    """Tiny lens-chip triangles falling away below each lens."""
    if palette_key == "B":
        col = (70, 90, 20)
    else:
        col = (95, 60, 115)

    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.polygon(body, col, [
            (cx - 3, cy + 9),
            (cx - 1, cy + 9),
            (cx - 2, cy + 11),
        ])
        pygame.draw.polygon(body, col, [
            (cx + 2, cy + 10),
            (cx + 4, cy + 10),
            (cx + 3, cy + 12),
        ])


def _draw_x_eyes(body, palette_key):
    """Bold cartoon X-eyes on bare head skin for OFF variants. Far eye uses
    reach ±3 to survive the foreshortened 3/4-pose; near eye uses full ±4.
    Warm-white highlight on the upper-left arm of each stroke so both X's
    read as inked rather than smudged."""
    if palette_key == "B":
        ink_col = (20, 25, 15)
    else:
        ink_col = (25, 12, 30)
    glint_col = (245, 245, 200) if palette_key == "B" else (220, 215, 180)

    fx, fy = LENS_L
    pygame.draw.line(body, ink_col, (fx - 3, fy - 3), (fx + 3, fy + 3), 2)
    pygame.draw.line(body, ink_col, (fx - 3, fy + 3), (fx + 3, fy - 3), 2)
    pygame.draw.line(body, glint_col, (fx - 3, fy - 4), (fx - 1, fy - 2), 1)
    pygame.draw.line(body, glint_col, (fx - 3, fy + 2), (fx - 1, fy), 1)

    nx, ny = LENS_R
    pygame.draw.line(body, ink_col, (nx - 4, ny - 4), (nx + 4, ny + 4), 2)
    pygame.draw.line(body, ink_col, (nx - 4, ny + 4), (nx + 4, ny - 4), 2)
    pygame.draw.line(body, glint_col, (nx - 4, ny - 5), (nx - 1, ny - 2), 1)
    pygame.draw.line(body, glint_col, (nx - 4, ny + 3), (nx - 1, ny), 1)


# ── C-row grungy extras ────────────────────────────────────────────────────

def _draw_poison_ring(out, cx=48, cy=20, r=14):
    """Thin sickly-green ring around the bird's head — vapour aura that
    sells C as theatrical decay."""
    ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(ring, (180, 200, 100, 110), (r + 2, r + 2), r, 1)
    pygame.draw.circle(ring, (180, 200, 100, 70),  (r + 2, r + 2), r + 1, 1)
    out.blit(ring, (cx - r - 2, cy - r - 2))


def _draw_stink_lines(out):
    """2–3 wavy 1-px vertical squiggles drifting up above the head, kept at
    y ∈ [3, 8] so they never touch the crown audit region (y ≤ 16)."""
    col = (150, 170, 80)
    for base_x, phase, height in ((40, 0.0, 5), (45, 1.4, 5), (50, 0.7, 4)):
        for i in range(height):
            wob = int(math.sin(phase + i * 1.1))
            pygame.draw.rect(out, col, (base_x + wob, 8 - i, 1, 1))


def _withered_palette(P):
    """Wing tinted to wing_dark across its layers — withered limb."""
    Q = {**P}
    Q['wing_main']      = P['wing_dark']
    Q['wing_tip']       = P['wing_dark']
    Q['wing_secondary'] = P['wing_dark']
    Q['wing_highlight'] = None
    return Q


# ── per-variant builders ────────────────────────────────────────────────────

def _aura(out, alpha=110):
    """Shared toxic aura — keeps B/C in the same E-family wrongness world."""
    blit_glow(out, 32, 30, 24, TOXIC_AURA, alpha=alpha)


def _new_parrot_surface():
    """Padded native parrot surface — 64×68."""
    return pygame.Surface((SPRITE_W, PARROT_SURF_H), pygame.SRCALPHA)


def build_b_sunglasses_on(angle):
    """B ON — comic KO with the shades still in place. Bold palette X stamped
    on each lens (replaces round 5's crack-fork). Mouth shut, thick brow,
    chips falling away."""
    out = _new_parrot_surface()
    _aura(out)
    P = {**P_CHARTREUSE, 'lens_body': (6, 12, 4)}
    body = _build_parrot_with_palette(angle, P, draw_lenses=True)
    surf = _new_parrot_surface()
    surf.blit(body, (0, 0))
    _draw_lens_chips(surf, "B")
    _draw_slanted_brow(surf, "B")
    _draw_bold_x_on_lens(surf, "B")
    out.blit(surf, (0, 0))
    return _add_outline(out)


def build_b_sunglasses_off(angle):
    """B OFF — bold black X-eyes on bare head + slack 2×6 tongue. Full
    cartoon-KO read. Fallen-aviators prop drawn in the panel pass."""
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
    """C ON — theatrical decay with shades. Bold palette X stamped on each
    lens (replaces round 5's crack-fork). Mouth shut so the cumulative noise
    (wing + aura + stink + chips + brow + X) calms. Withered wing + aura
    ring + stink lines preserved so the row identity holds."""
    out = _new_parrot_surface()
    _aura(out)
    _draw_poison_ring(out)
    P = _withered_palette(P_BRUISE)
    P = {**P, 'lens_body': (119, 126, 70)}
    body = _build_parrot_with_palette(angle, P, draw_lenses=True)
    surf = _new_parrot_surface()
    surf.blit(body, (0, 0))
    _draw_lens_chips(surf, "C")
    _draw_slanted_brow(surf, "C")
    _draw_bold_x_on_lens(surf, "C")
    out.blit(surf, (0, 0))
    _draw_stink_lines(out)
    return _add_outline(out)


def build_c_sunglasses_off(angle):
    """C OFF — theatrical decay without the shades. Loud black X-eyes on
    the bare bruise-coloured head, droopier curving tongue, withered wing
    + aura + stink lines."""
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
    """Untouched ship lead. Padded to the same 64×68 canvas."""
    src = build_nightvapor_dead(angle)
    padded = _new_parrot_surface()
    padded.blit(src, (0, 0))
    return _add_outline(padded)


# ── fallen-aviators silhouette ─────────────────────────────────────────────

def _fallen_aviators(surf, center, palette_key):
    """Tilted dropped-aviators silhouette on the panel "floor" below Pip.
    ~25% smaller than round 3 (lens disc radius 2 px native), centred under
    the bird, tilt + black outline preserved."""
    if palette_key == "B":
        frame_col = (70, 90, 20)
    else:
        frame_col = (95, 60, 115)

    s = 3
    raw_w, raw_h = 16 * s, 8 * s
    raw = pygame.Surface((raw_w, raw_h), pygame.SRCALPHA)
    pygame.draw.ellipse(raw, (0, 0, 0, 90), (1, raw_h - 3 * s, raw_w - 2, 3 * s))
    lcx, rcx = 3 * s, 13 * s
    cy = 3 * s
    pygame.draw.circle(raw, frame_col, (lcx, cy), 2 * s)
    pygame.draw.circle(raw, frame_col, (rcx, cy), 2 * s)
    pygame.draw.circle(raw, (12, 12, 16), (lcx, cy), 1 * s + 1)
    pygame.draw.circle(raw, (12, 12, 16), (rcx, cy), 1 * s + 1)
    pygame.draw.line(raw, frame_col, (lcx + 2 * s, cy), (rcx - 2 * s, cy), s)
    pygame.draw.circle(raw, (0, 0, 0), (lcx, cy), 2 * s, 1)
    pygame.draw.circle(raw, (0, 0, 0), (rcx, cy), 2 * s, 1)
    pygame.draw.circle(raw, (220, 220, 230), (lcx - 1, cy - 1), 1)
    pygame.draw.circle(raw, (220, 220, 230), (rcx - 1, cy - 1), 1)

    rot = pygame.transform.rotate(raw, -30)
    rect = rot.get_rect(center=center)
    surf.blit(rot, rect.topleft)


# ── panel composition ──────────────────────────────────────────────────────

PANEL_W = 248
PANEL_H = 316


def _panel(label_top, label_sub, build_fn, palette_key, draw_fallen,
           bg_tint=None, return_geom=False):
    """One labelled panel: charcoal card, 3× outlined parrot, fallen-
    aviators cue on OFF panels, two-line label strip pinned to the
    bottom. `return_geom=True` returns geometry so the renderer can
    pixel-sample on the composited surface."""
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

    if draw_fallen:
        cue_x = PANEL_W // 2
        cue_y = art_y + zh + 24
        _fallen_aviators(card, (cue_x, cue_y), palette_key)

    _text(card, label_top, (PANEL_W // 2, PANEL_H - 28), size=14, color=GOLD)
    _text(card, label_sub, (PANEL_W // 2, PANEL_H - 12), size=11, color=TEXT_LO)

    if return_geom:
        return card, art_x, art_y, zw, zh, sprite
    return card


def _baseline_panel():
    """E panel — slim full-width strip above the 2×2 grid."""
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


# ── pixel-sample assertions ────────────────────────────────────────────────

def _outlined_offset():
    """The _add_outline pass shifts the body 1 px right + 1 px down. Sprite-
    local coords therefore map to outlined-surface coords by (+1, +1)
    before the 3× zoom."""
    return (1, 1)


def _sprite_to_panel(art_x, art_y, sx, sy):
    """Map sprite-local (sx, sy) to the panel pixel that should be sampled
    after the outline + 3× zoom + card blit."""
    ox, oy = _outlined_offset()
    return (art_x + (sx + ox) * ZOOM + ZOOM // 2,
            art_y + (sy + oy) * ZOOM + ZOOM // 2)


def _expected_far_x_pixel(palette_key):
    """Far X stroke colour — must be the small X ink at LENS_L on OFF."""
    return (20, 25, 15) if palette_key == "B" else (25, 12, 30)


def _expected_bold_x_core(palette_key):
    """Bold-X core stroke colour on the ON-lens. Round 7 inverts C: the
    light eggplant (165, 130, 185) is now the CORE so the X reads
    bright-on-mid against the olive lens body."""
    return (225, 235, 130) if palette_key == "B" else (165, 130, 185)


def _close(a, b, tol=8):
    """Channel-wise within tolerance — protects against pygame's anti-alias
    blending around scaled lines."""
    return all(abs(int(a[i]) - int(b[i])) <= tol for i in range(3))


def _find_color_in_3x3(surf, cx, cy, expected, tol=12):
    """Scan a 3×3 region centred on (cx, cy) for any pixel whose channel-
    wise distance to `expected` is ≤ tol. Pygame's scale + line smoothing
    can shift the strongest core sample by 1 px on bold strokes, so this
    forgives that without letting a wildly-wrong colour pass."""
    best_dist = None
    best_pix = None
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            px = surf.get_at((cx + dx, cy + dy))[:3]
            d = max(abs(int(px[i]) - int(expected[i])) for i in range(3))
            if best_dist is None or d < best_dist:
                best_dist = d
                best_pix = tuple(px)
            if d <= tol:
                return True, (cx + dx, cy + dy), tuple(px)
    return False, (cx, cy), best_pix


def _find_color_in_5x5(surf, cx, cy, expected, tol=14):
    """Wider scan for the outer-arm silhouette-break assert: the X tip at
    sprite-local (40, 14) is at the very edge of the 2 px stroke, so its
    rendered colour can drift by a pixel under nearest-neighbour scale
    + the outline pass. 5×5 catches the arm even when it lands one pixel
    over from the spec point."""
    best_dist = None
    best_pix = None
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            px = surf.get_at((cx + dx, cy + dy))[:3]
            d = max(abs(int(px[i]) - int(expected[i])) for i in range(3))
            if best_dist is None or d < best_dist:
                best_dist = d
                best_pix = tuple(px)
            if d <= tol:
                return True, (cx + dx, cy + dy), tuple(px)
    return False, (cx, cy), best_pix


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

    title_str = "DEAD PIP v3  ·  round 9 — sunglasses-ON: contained bold X inside lens"
    sub_str   = "E baseline (shipped, top) + B and C variants (decision: which goes back into the game)."

    MIN_PADDING = 12
    title_font = _font(22)
    sub_font   = _font(13)
    title_w, _title_h_unused = title_font.size(title_str)
    sub_w, _ = sub_font.size(sub_str)
    min_canvas_for_title = title_w + MIN_PADDING * 2
    min_canvas_for_sub   = sub_w   + MIN_PADDING * 2
    total_w = max(grid_w + margin_x * 2, min_canvas_for_title, min_canvas_for_sub)

    margin_x = (total_w - grid_w) // 2

    total_h = title_h + margin_top + baseline_h + section_gap + grid_h + margin_bot

    surf = pygame.Surface((total_w, total_h))
    surf.fill(BG_CHARCOAL)

    # OFF-column tint — preserves the ON/OFF axis read without competing.
    off_col_x = margin_x + PANEL_W + col_gap // 2 - 4
    off_col_w = PANEL_W + col_gap // 2 + 8
    off_col_y = title_h + margin_top + baseline_h + section_gap - 6
    off_col_h = grid_h + 12
    pygame.draw.rect(surf, COL_TINT,
                     (off_col_x, off_col_y, off_col_w, off_col_h),
                     border_radius=14)

    # 1 px vertical divider dead-centre between columns.
    divider_x = margin_x + PANEL_W + col_gap // 2
    divider_y0 = title_h + margin_top + baseline_h + section_gap - 4
    divider_y1 = total_h - margin_bot + 4
    pygame.draw.line(surf, DIVIDER_COL, (divider_x, divider_y0),
                     (divider_x, divider_y1), 1)

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

    # Title padding assert — preserved from round 5.
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

    # 2×2 grid of B/C × ON/OFF panels. Sub-labels swapped to drop the
    # "crack" copy now that round 6 stamps an X instead.
    panels = [
        ("B · SUNGLASSES ON",  "comic KO — bold X + brow (mouth shut)",                build_b_sunglasses_on,  "B", False),
        ("B · SHADES OFF",     "comic KO — X-eyes + tongue + fallen shades",          build_b_sunglasses_off, "B", True),
        ("C · SUNGLASSES ON",  "decay — bold X + wither + aura (mouth shut)",          build_c_sunglasses_on,  "C", False),
        ("C · SHADES OFF",     "decay — X-eyes + tongue + aura + shades",             build_c_sunglasses_off, "C", True),
    ]

    geom_by_key = {}

    for i, (label, sub, fn, key, fallen) in enumerate(panels):
        row = i // 2
        col = i % 2
        px = margin_x + col * (PANEL_W + col_gap)
        py = y + row * (PANEL_H + row_gap)
        card, art_x, art_y, zw, zh, sprite = _panel(
            label, sub, fn, key, fallen, return_geom=True
        )
        surf.blit(card, (px, py))
        geom_by_key[(key, "off" if fallen else "on")] = (
            px + art_x, py + art_y, zw, zh, sprite
        )

    # ── Far X-eye stroke pixel on B-OFF and C-OFF (round-5 assert) ────────
    for key in ("B", "C"):
        gx, gy, zw, zh, _spr = geom_by_key[(key, "off")]
        sample_x, sample_y = _sprite_to_panel(gx, gy, LENS_L[0], LENS_L[1])
        px = surf.get_at((sample_x, sample_y))[:3]
        expected = _expected_far_x_pixel(key)
        print(f"[fix2] {key}-OFF far-eye sample at ({sample_x},{sample_y}) "
              f"= {tuple(px)}  expected ≈ {expected}")
        assert _close(px, expected, tol=12), (
            f"{key}-OFF far X-eye missing — sampled {tuple(px)} at "
            f"({sample_x},{sample_y}), expected ≈ {expected}. "
            f"Far-eye stroke didn't survive scaling."
        )

    # ── Head crown on C-OFF clean of stray pink (round-5 assert) ──────────
    gx, gy, zw, zh, _spr = geom_by_key[("C", "off")]
    crown_samples = [(46, 12), (48, 12), (50, 12), (52, 13), (44, 14)]
    for sx_local, sy_local in crown_samples:
        cx_panel, cy_panel = _sprite_to_panel(gx, gy, sx_local, sy_local)
        px = surf.get_at((cx_panel, cy_panel))[:3]
        r, g, b = px
        pink_like = (r > 150 and b > 60 and g < 110)
        print(f"[fix4] C-OFF crown sample sprite({sx_local},{sy_local}) "
              f"→ panel({cx_panel},{cy_panel}) = {tuple(px)}  "
              f"pink_like={pink_like}")
        assert not pink_like, (
            f"C-OFF head crown sample ({tuple(px)}) at sprite-local "
            f"({sx_local},{sy_local}) looks pink — stray tongue/magenta "
            f"artefact in the crown region."
        )

    # ── Bold-X core lands on each ON-variant lens (round-6 assert,
    #    extended in round 7 to validate C-ON's INVERTED core colour) ─────
    # Spec sample point is panel_x + 3 * 46, panel_y + 3 * 20 — i.e. lens-
    # centre coord LENS_L (46, 20) projected to panel space without the
    # outline offset. The bold stroke is anti-aliased at the edges so the
    # exact centre may drift 1 px; scan a 3×3 window around the spec point
    # and accept any pixel matching the core colour.
    for key, slot in (("B", ("B", "on")), ("C", ("C", "on"))):
        gx, gy, zw, zh, _spr = geom_by_key[slot]
        cx = gx + 3 * LENS_L[0]
        cy = gy + 3 * LENS_L[1]
        expected = _expected_bold_x_core(key)
        found, (hit_x, hit_y), best_pix = _find_color_in_3x3(
            surf, cx, cy, expected, tol=12
        )
        print(f"[fix-X] {key}-ON lens-center sample = {best_pix} at "
              f"({hit_x},{hit_y})  expected core ≈ {expected}  "
              f"(spec point ({cx},{cy}), 3×3 scan, found={found})")
        assert found, (
            f"{key}-ON bold-X core colour not found in 3×3 region around "
            f"({cx},{cy}); closest sample {best_pix}, expected ≈ "
            f"{expected}. The bold-X stamp didn't land on the lens centre."
        )

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

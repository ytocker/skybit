"""Five high-quality ghost-parrot treatments for the ghost power-up.

Unlike a silhouette tint, each variant builds the parrot from scratch at
native 64×60 resolution using the same procedural drawing approach as
`parrot._build_frame` — proper layered ellipses, polygons, and per-element
palettes — so the ghost parrots have the same hand-crafted quality and
detail (feathers, lenses, beak, body shading) as the original sprite.

Each `build_<name>_frame(angle_deg)` returns a 60×60 SRCALPHA surface;
`build_ghost_variant_frames(build_fn)` returns 4 outlined frames (one per
wing angle), mirroring `parrot.FRAMES`.

Preview-only — nothing in the game imports this yet.
"""
import math
import pygame

from game.parrot import SPRITE_W, SPRITE_H, _WING_ANGLES, _aaellipse, _add_outline
from game.draw import blit_glow, lerp_color, WHITE, NEAR_BLACK


# ── palette helper ───────────────────────────────────────────────────────────
# Each variant defines a dict with these keys. Anything not provided falls
# back to neutral grey so missing keys don't crash the builder.

def _pal(*, tail, tail_line, body_shadow, body_main, body_chest, body_belly,
         sheen, wing_main, wing_dark, wing_tip, wing_secondary, wing_highlight,
         head_shadow, head_main, head_cheek, head_crown,
         lens_frame, lens_body, lens_tint, lens_glint,
         beak_main, beak_dark, beak_gloss, foot):
    return locals().copy()


# ── shared building blocks (parameterised by palette) ────────────────────────

def _build_wing(angle_deg, P):
    """Wing polygon rotated around its shoulder anchor — palette-driven."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    # Drop shadow outline
    pygame.draw.polygon(w, (0, 0, 0, 110),
                        [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)])
    # Main feather layer
    pygame.draw.polygon(w, P['wing_main'],
                        [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)])
    # Darker underside triangle
    pygame.draw.polygon(w, P['wing_dark'],
                        [(24, 24), (32, 42), (18, 36)])
    # Primary feather tips
    pygame.draw.polygon(w, P['wing_tip'],
                        [(44, 13), (50, 18), (48, 28)])
    # Secondary stripe
    if P['wing_secondary'] is not None:
        pygame.draw.polygon(w, P['wing_secondary'],
                            [(42, 18), (48, 22), (46, 28), (40, 24)])
    # Feather divider lines
    pygame.draw.line(w, P['wing_dark'], (26, 25), (42, 18), 2)
    pygame.draw.line(w, P['wing_dark'], (28, 30), (44, 25), 2)
    pygame.draw.line(w, P['wing_dark'], (30, 34), (46, 32), 2)
    # Crisp highlight edge
    if P['wing_highlight'] is not None:
        pygame.draw.line(w, P['wing_highlight'], (25, 25), (41, 15), 1)
    return pygame.transform.rotate(w, angle_deg)


def _draw_lenses(surf, cx, cy, P):
    """Aviator shades, palette-driven so each variant retints the lenses."""
    r = 6
    L = (cx - 4, cy)
    R = (cx + 6, cy - 1)
    # Frame
    pygame.draw.circle(surf, P['lens_frame'], L, r + 1)
    pygame.draw.circle(surf, P['lens_frame'], R, r + 1)
    # Lens body
    pygame.draw.circle(surf, P['lens_body'], L, r)
    pygame.draw.circle(surf, P['lens_body'], R, r)
    # Tint band on the upper half
    if P['lens_tint'] is not None:
        tint = pygame.Surface((r * 2, r), pygame.SRCALPHA)
        pygame.draw.ellipse(tint, P['lens_tint'], tint.get_rect())
        surf.blit(tint, (L[0] - r, L[1] - r + 1))
        surf.blit(tint, (R[0] - r, R[1] - r + 1))
    # Glints
    if P['lens_glint'] is not None:
        pygame.draw.circle(surf, P['lens_glint'], (L[0] - 2, L[1] - 2), 2)
        pygame.draw.circle(surf, P['lens_glint'], (R[0] - 2, R[1] - 3), 2)
    # Bridge + brow bar
    pygame.draw.line(surf, P['lens_frame'], (L[0] + r, L[1]), (R[0] - r, R[1]), 2)
    pygame.draw.line(surf, P['lens_frame'],
                     (L[0] - r + 1, L[1] - r + 2),
                     (R[0] + r - 1, R[1] - r + 2), 1)


def _build_parrot_with_palette(angle_deg, P):
    """Draw the full parrot at native resolution using the given palette.
    Returns a 64×60 SRCALPHA surface. Same draw order as _build_frame
    in parrot.py so all the proportions match exactly."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail
    for i, c in enumerate(P['tail']):
        pygame.draw.polygon(surf, c, [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)])
    pygame.draw.line(surf, P['tail_line'], (4, 27), (18, 31), 1)
    pygame.draw.line(surf, P['tail_line'], (6, 33), (20, 35), 1)

    # Body
    _aaellipse(surf, P['body_shadow'], (34, 35), 19, 14)
    _aaellipse(surf, P['body_main'],   (32, 32), 19, 14)
    _aaellipse(surf, P['body_chest'],  (30, 29), 13,  8)
    _aaellipse(surf, P['body_belly'],  (28, 38), 12,  6)
    if P['sheen'] is not None:
        sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sheen, P['sheen'], sheen.get_rect())
        surf.blit(sheen, (22, 21))

    # Wing
    wing = _build_wing(angle_deg, P)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head
    _aaellipse(surf, P['head_shadow'], (48, 23), 12, 11)
    _aaellipse(surf, P['head_main'],   (47, 21), 12, 11)
    _aaellipse(surf, P['head_cheek'],  (44, 24),  4,  3)
    _aaellipse(surf, P['head_crown'],  (46, 16),  7,  3)

    # Lenses
    _draw_lenses(surf, 50, 20, P)

    # Beak
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, P['beak_main'], beak_pts)
    pygame.draw.polygon(surf, P['beak_dark'], beak_pts, 1)
    pygame.draw.line(surf, P['beak_gloss'], (55, 22), (59, 24), 1)
    pygame.draw.line(surf, P['beak_dark'],  (52, 24), (58, 25), 1)

    # Feet
    pygame.draw.line(surf, P['foot'], (28, 45), (26, 49), 2)
    pygame.draw.line(surf, P['foot'], (34, 45), (36, 49), 2)

    return surf


# ── V1 — SPECTRAL  (cool cyan translucent ghost) ─────────────────────────────

P_SPECTRAL = _pal(
    tail=[(120, 175, 215), (160, 205, 230), (200, 230, 245), (220, 240, 250)],
    tail_line=(60, 110, 160),
    body_shadow=(50, 95, 145),
    body_main=(140, 200, 230),
    body_chest=(180, 225, 245),
    body_belly=(215, 240, 250),
    sheen=(255, 255, 255, 130),
    wing_main=(85, 145, 210),
    wing_dark=(40, 80, 140),
    wing_tip=(160, 220, 255),
    wing_secondary=(210, 235, 255),
    wing_highlight=(225, 245, 255),
    head_shadow=(60, 110, 160),
    head_main=(150, 210, 240),
    head_cheek=(195, 230, 245),
    head_crown=(220, 240, 250),
    lens_frame=(180, 220, 245),
    lens_body=(15, 25, 50),
    lens_tint=(80, 140, 200, 130),
    lens_glint=(255, 255, 255),
    beak_main=(170, 200, 230),
    beak_dark=(70, 100, 145),
    beak_gloss=(240, 250, 255),
    foot=(70, 100, 145),
)

def build_spectral_frame(angle_deg):
    """Translucent cyan parrot with a soft outer halo — properly ghostly."""
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Soft cyan halo behind everything
    blit_glow(out, 32, 30, 26, (90, 200, 255), alpha=130)
    blit_glow(out, 32, 30, 18, (180, 230, 255), alpha=140)
    # Body in cool palette
    body = _build_parrot_with_palette(angle_deg, P_SPECTRAL)
    body.set_alpha(225)
    out.blit(body, (0, 0))
    return out


# ── V2 — WRAITH  (dark with cyan rim-light, glowing eyes) ────────────────────

P_WRAITH = _pal(
    tail=[(20, 30, 50), (28, 42, 70), (40, 55, 85), (50, 70, 105)],
    tail_line=(10, 18, 32),
    body_shadow=(8, 14, 28),
    body_main=(30, 42, 70),
    body_chest=(45, 60, 90),
    body_belly=(55, 75, 110),
    sheen=(120, 160, 220, 100),
    wing_main=(20, 35, 65),
    wing_dark=(8, 14, 28),
    wing_tip=(45, 70, 110),
    wing_secondary=None,
    wing_highlight=(120, 180, 230),
    head_shadow=(8, 14, 28),
    head_main=(30, 45, 75),
    head_cheek=(50, 70, 100),
    head_crown=(70, 100, 140),
    lens_frame=(80, 140, 200),
    lens_body=(5, 10, 20),
    lens_tint=None,
    lens_glint=None,    # eyes replaced below
    beak_main=(60, 80, 115),
    beak_dark=(20, 30, 50),
    beak_gloss=(140, 180, 220),
    foot=(20, 30, 50),
)

def build_wraith_frame(angle_deg):
    """Dark wraith with cyan rim-light and glowing white eyes."""
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Faint outer halo so the dark body still pops on bright skies
    blit_glow(out, 32, 30, 24, (50, 150, 230), alpha=110)
    body = _build_parrot_with_palette(angle_deg, P_WRAITH)
    out.blit(body, (0, 0))
    # Glowing eye-pupils punched through the lens body
    for ex, ey in ((46, 20), (56, 19)):
        blit_glow(out, ex, ey, 4, (180, 230, 255), alpha=200)
        pygame.draw.circle(out, (235, 250, 255), (ex, ey), 2)
        pygame.draw.circle(out, (255, 255, 255), (ex - 1, ey - 1), 1)
    return out


# ── V3 — ECTOPLASM  (Ghostbusters-style green slime spirit) ─────────────────

P_ECTOPLASM = _pal(
    tail=[(50, 140, 80), (90, 180, 110), (140, 220, 150), (200, 250, 200)],
    tail_line=(30, 90, 50),
    body_shadow=(25, 90, 50),
    body_main=(120, 210, 150),
    body_chest=(170, 235, 185),
    body_belly=(210, 250, 220),
    sheen=(255, 255, 230, 130),
    wing_main=(70, 180, 110),
    wing_dark=(25, 100, 55),
    wing_tip=(170, 240, 170),
    wing_secondary=(220, 255, 200),
    wing_highlight=(240, 255, 220),
    head_shadow=(35, 110, 65),
    head_main=(140, 220, 160),
    head_cheek=(195, 245, 200),
    head_crown=(215, 250, 215),
    lens_frame=(220, 255, 200),
    lens_body=(20, 60, 35),
    lens_tint=(120, 220, 140, 140),
    lens_glint=(255, 255, 220),
    beak_main=(220, 240, 130),
    beak_dark=(110, 140, 50),
    beak_gloss=(255, 255, 200),
    foot=(60, 110, 70),
)

def build_ectoplasm_frame(angle_deg):
    """Glowing green ectoplasm parrot — full hand-drawn detail in slime palette."""
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Bright green outer aura (two layers for depth)
    blit_glow(out, 32, 30, 28, (60, 200, 100), alpha=140)
    blit_glow(out, 32, 30, 18, (160, 250, 180), alpha=150)
    # Body in slime palette
    body = _build_parrot_with_palette(angle_deg, P_ECTOPLASM)
    out.blit(body, (0, 0))
    # A few "drip" highlights below the body
    pygame.draw.circle(out, (180, 250, 200), (24, 47), 2)
    pygame.draw.circle(out, (220, 255, 220), (40, 49), 1)
    pygame.draw.circle(out, (180, 250, 200), (32, 51), 1)
    return out


# ── V4 — BANSHEE  (white-hot bright spirit with streaming trails) ────────────

P_BANSHEE = _pal(
    tail=[(180, 220, 255), (210, 235, 255), (235, 245, 255), (250, 252, 255)],
    tail_line=(100, 160, 220),
    body_shadow=(110, 160, 220),
    body_main=(220, 235, 255),
    body_chest=(240, 248, 255),
    body_belly=(252, 254, 255),
    sheen=(255, 255, 255, 200),
    wing_main=(190, 220, 255),
    wing_dark=(120, 170, 230),
    wing_tip=(245, 250, 255),
    wing_secondary=(250, 252, 255),
    wing_highlight=(255, 255, 255),
    head_shadow=(140, 180, 230),
    head_main=(225, 240, 255),
    head_cheek=(245, 250, 255),
    head_crown=(252, 254, 255),
    lens_frame=(220, 240, 255),
    lens_body=(40, 60, 110),
    lens_tint=(140, 200, 255, 150),
    lens_glint=(255, 255, 255),
    beak_main=(220, 235, 255),
    beak_dark=(120, 170, 230),
    beak_gloss=(255, 255, 255),
    foot=(140, 180, 230),
)

def build_banshee_frame(angle_deg):
    """White-hot apparition with trailing wisps — looks like it's streaming."""
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Wide outer aura
    blit_glow(out, 32, 30, 28, (130, 200, 255), alpha=180)
    blit_glow(out, 32, 30, 22, (200, 230, 255), alpha=170)
    # Streaming trail wisps behind the body (curving toward the tail)
    for i, (x, y, r, a) in enumerate([
            (10, 36, 4, 90), (4, 32, 3, 70), (8, 42, 3, 70),
            (16, 46, 2, 80), (2, 38, 2, 60)]):
        blit_glow(out, x, y, r, (200, 230, 255), alpha=a)
    # Body in bright bone-white palette
    body = _build_parrot_with_palette(angle_deg, P_BANSHEE)
    out.blit(body, (0, 0))
    # Inner bright core highlight near the chest
    blit_glow(out, 30, 30, 8, (255, 255, 255), alpha=120)
    return out


# ── V5 — POSSESSED  (corrupted parrot, ashen + glowing red eyes) ─────────────

P_POSSESSED = _pal(
    tail=[(60, 30, 30), (80, 40, 40), (100, 55, 50), (120, 70, 60)],
    tail_line=(35, 15, 18),
    body_shadow=(35, 15, 20),
    body_main=(95, 55, 55),
    body_chest=(125, 75, 70),
    body_belly=(140, 95, 85),
    sheen=(190, 150, 140, 100),
    wing_main=(50, 30, 60),
    wing_dark=(20, 12, 30),
    wing_tip=(110, 40, 50),
    wing_secondary=(155, 60, 60),
    wing_highlight=(200, 110, 110),
    head_shadow=(40, 18, 22),
    head_main=(105, 60, 60),
    head_cheek=(140, 80, 75),
    head_crown=(155, 95, 90),
    lens_frame=(110, 70, 70),
    lens_body=(10, 5, 5),
    lens_tint=None,
    lens_glint=None,    # eyes replaced below — glowing red
    beak_main=(150, 110, 70),
    beak_dark=(60, 35, 20),
    beak_gloss=(220, 180, 130),
    foot=(35, 18, 18),
)

def build_possessed_frame(angle_deg):
    """Corrupted parrot — ashen reds, glowing red eyes, dark crimson aura."""
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    # Dark crimson aura (low intensity — the menace is in the eyes, not the glow)
    blit_glow(out, 32, 30, 24, (120, 20, 40), alpha=110)
    body = _build_parrot_with_palette(angle_deg, P_POSSESSED)
    out.blit(body, (0, 0))
    # Glowing red eyes punched through the lenses
    for ex, ey in ((46, 20), (56, 19)):
        blit_glow(out, ex, ey, 5, (255, 60, 50), alpha=220)
        pygame.draw.circle(out, (255, 200, 180), (ex, ey), 2)
        pygame.draw.circle(out, (255, 250, 240), (ex - 1, ey - 1), 1)
    return out


# ── Frame builder ────────────────────────────────────────────────────────────

def build_ghost_variant_frames(build_fn) -> list:
    """Return 4 outlined ghost frames (one per wing angle) for the variant."""
    return [_add_outline(build_fn(a)) for a in _WING_ANGLES]


# ── Registry ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("SPECTRAL",   build_spectral_frame),
    ("WRAITH",     build_wraith_frame),
    ("ECTOPLASM",  build_ectoplasm_frame),
    ("BANSHEE",    build_banshee_frame),
    ("POSSESSED",  build_possessed_frame),
]

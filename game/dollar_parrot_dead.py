"""Dead-Pip variants for the on-death cross-fade overlay.

Three palettes ship side-by-side, cycled via F8 dev-key:
  B. CHARTREUSE KO       — ship lead. Bare-head X-eyes, slack tongue,
                           fallen aviators tumbling next to the body.
                           Hot chartreuse palette; no aura.
  E. NIGHT-VAPOR DARK    — legacy alt: glowing toxic pupils + green aura.
  C. WITHERED BRUISE     — legacy alt: eggplant + chartreuse, slim X.

E's aura scales with the cross-fade `t` so the bird never reads
"haunted while still alive" during the early fade frames; B has no aura
to scale.
"""
import pygame

from game.parrot import SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import blit_glow


LENS_L = (46, 20)
LENS_R = (56, 19)
BEAK_BOTTOM = (58, 28)
TOXIC_AURA = (90, 220, 80)


# ── PALETTE E — NIGHT-VAPOR DARK (ship lead) ────────────────────────────────

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
    lens_glint=None,
    beak_main=(85, 95, 60),
    beak_dark=(35, 40, 25),
    beak_gloss=(160, 190, 110),
    foot=(20, 28, 22),
)


def build_nightvapor_dead(angle_deg, aura_scale=1.0):
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    aura_alpha = max(0, min(255, int(110 * aura_scale)))
    if aura_alpha > 0:
        blit_glow(out, 32, 30, 24, TOXIC_AURA, alpha=aura_alpha)
    body = _build_parrot_with_palette(angle_deg, P_NIGHTVAPOR)
    out.blit(body, (0, 0))
    for ex, ey in (LENS_L, LENS_R):
        blit_glow(out, ex, ey, 5, (180, 230, 80), alpha=220)
        pygame.draw.circle(out, (210, 245, 110), (ex, ey), 2)
        pygame.draw.circle(out, (245, 255, 200), (ex - 1, ey - 1), 1)
    return out


# ── PALETTE B — CHARTREUSE ECTOPLASM (alternate) ────────────────────────────

P_CHARTREUSE = _pal(
    tail=[(110, 140, 25), (150, 175, 35), (185, 205, 50), (215, 225, 75)],
    tail_line=(70, 90, 20),
    body_shadow=(85, 105, 25),
    body_main=(190, 220, 70),
    body_chest=(210, 230, 95),
    body_belly=(225, 235, 130),
    sheen=(245, 250, 180, 120),
    wing_main=(140, 165, 35),
    wing_dark=(65, 85, 15),
    wing_tip=(210, 225, 70),
    wing_secondary=(230, 235, 110),
    wing_highlight=(240, 240, 160),
    head_shadow=(90, 110, 30),
    head_main=(195, 220, 75),
    head_cheek=(215, 230, 100),
    head_crown=(225, 235, 130),
    lens_frame=(70, 90, 20),
    lens_body=(10, 18, 8),
    lens_tint=None,
    lens_glint=None,
    beak_main=(190, 180, 60),
    beak_dark=(105, 95, 20),
    beak_gloss=(230, 225, 140),
    foot=(70, 85, 20),
)


def _draw_b_x_eyes(body):
    """Bold cartoon X-eyes inked on the bare chartreuse head. Far eye
    reach ±3 (foreshortened 3/4-pose), near eye ±4. Warm-white highlight
    on each X's upper-left so it reads as inked rather than smudged."""
    ink = (20, 25, 15)
    glint = (245, 245, 200)
    fx, fy = LENS_L
    pygame.draw.line(body, ink, (fx - 3, fy - 3), (fx + 3, fy + 3), 2)
    pygame.draw.line(body, ink, (fx - 3, fy + 3), (fx + 3, fy - 3), 2)
    pygame.draw.line(body, glint, (fx - 3, fy - 4), (fx - 1, fy - 2), 1)
    pygame.draw.line(body, glint, (fx - 3, fy + 2), (fx - 1, fy), 1)
    nx, ny = LENS_R
    pygame.draw.line(body, ink, (nx - 4, ny - 4), (nx + 4, ny + 4), 2)
    pygame.draw.line(body, ink, (nx - 4, ny + 4), (nx + 4, ny - 4), 2)
    pygame.draw.line(body, glint, (nx - 4, ny - 5), (nx - 1, ny - 2), 1)
    pygame.draw.line(body, glint, (nx - 4, ny + 3), (nx - 1, ny), 1)


def _draw_b_tongue(body):
    """Slack 2×6 px red tongue dropping from the lower beak — comic-KO
    cue that pairs with the X-eyes."""
    ax, ay = BEAK_BOTTOM
    x = ax - 1
    rect = pygame.Rect(x, ay - 1, 2, 6)
    pygame.draw.rect(body, (180, 50, 50), rect)
    pygame.draw.line(body, (0, 0, 0), (rect.x, rect.bottom - 1),
                     (rect.right - 1, rect.bottom - 1), 1)
    pygame.draw.line(body, (0, 0, 0), (rect.right - 1, rect.y),
                     (rect.right - 1, rect.bottom - 1), 1)
    pygame.draw.line(body, (220, 90, 90), (rect.x, rect.y),
                     (rect.x, rect.y + 2), 1)


def _draw_b_fallen_aviators(out, center=(54, 53)):
    """Tilted dropped-aviators silhouette tumbling beside the body. Drawn
    at native scale (16×8 raw, ~18×14 rotated) and tucked into the bottom-
    right corner so it doesn't overlap the wing/tail."""
    frame = (70, 90, 20)
    lens = (12, 12, 16)
    raw = pygame.Surface((16, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(raw, (0, 0, 0, 90), (1, 5, 14, 3))
    pygame.draw.circle(raw, frame, (3, 3), 2)
    pygame.draw.circle(raw, frame, (13, 3), 2)
    pygame.draw.circle(raw, lens, (3, 3), 1)
    pygame.draw.circle(raw, lens, (13, 3), 1)
    pygame.draw.line(raw, frame, (5, 3), (11, 3), 1)
    rot = pygame.transform.rotate(raw, -30)
    rect = rot.get_rect(center=center)
    out.blit(rot, rect.topleft)


def build_chartreuse_dead(angle_deg, aura_scale=1.0):
    """B · CHARTREUSE KO — comic-KO read with shades knocked off. No
    aura. Bold X-eyes on bare chartreuse head, slack tongue. The
    tumbling-aviators detail was removed at user request — the
    gradual cross-fade carries the read by itself. `aura_scale`
    accepted for signature parity with the other dead-Pip builders;
    ignored here."""
    out = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    body = _build_parrot_with_palette(angle_deg, P_CHARTREUSE, draw_lenses=False)
    _draw_b_x_eyes(body)
    _draw_b_tongue(body)
    out.blit(body, (0, 0))
    return out


# ── PALETTE C — WITHERED BRUISE (alternate) ─────────────────────────────────

def _dim(rgb, k=0.85):
    return tuple(max(0, min(255, int(c * k))) for c in rgb)


P_BRUISE = _pal(
    tail=[(80, 50, 95), (110, 75, 105), (155, 145, 90), (190, 200, 100)],
    tail_line=(50, 28, 65),
    body_shadow=(55, 30, 75),
    body_main=(110, 90, 110),
    body_chest=_dim((150, 145, 105)),
    body_belly=_dim((180, 190, 110)),
    sheen=(200, 200, 140, 80),
    wing_main=(70, 45, 90),
    wing_dark=(35, 18, 55),
    wing_tip=(160, 170, 80),
    wing_secondary=(195, 200, 95),
    wing_highlight=(215, 220, 130),
    head_shadow=(60, 35, 80),
    head_main=(115, 95, 115),
    head_cheek=(150, 140, 105),
    head_crown=(175, 185, 110),
    lens_frame=(95, 60, 115),
    lens_body=(170, 180, 100),
    lens_tint=None,
    lens_glint=None,
    beak_main=(135, 120, 80),
    beak_dark=(60, 40, 30),
    beak_gloss=(190, 185, 120),
    foot=(50, 28, 65),
)


def build_bruise_dead(angle_deg, aura_scale=1.0):
    body = _build_parrot_with_palette(angle_deg, P_BRUISE)
    x_ink = (95, 60, 115)
    for cx, cy in (LENS_L, LENS_R):
        pygame.draw.line(body, x_ink, (cx - 3, cy - 3), (cx + 3, cy + 3), 1)
        pygame.draw.line(body, x_ink, (cx - 3, cy + 3), (cx + 3, cy - 3), 1)
    return body


# ── Registry ────────────────────────────────────────────────────────────────

PALETTE_KEYS = ("B", "E", "C")

PALETTE_LABELS = {
    "B": "CHARTREUSE KO",
    "E": "NIGHT-VAPOR",
    "C": "WITHERED BRUISE",
}

_BUILDERS = {
    "B": build_chartreuse_dead,
    "E": build_nightvapor_dead,
    "C": build_bruise_dead,
}


def build_dead_variant_frames(palette_key, aura_scale=1.0):
    """4 outlined dead-Pip frames (one per wing angle) for a given palette."""
    build_fn = _BUILDERS[palette_key]
    return [_add_outline(build_fn(a, aura_scale=aura_scale)) for a in _WING_ANGLES]

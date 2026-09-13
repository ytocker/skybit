"""Treasure Box — OPEN-CHEST sprite, round-1 candidate exploration.

The closed W4 walnut-and-brass sprite (currently in `game/treasure_box.py
:_build_closed`) is approved and stays. Only the OPEN-MOMENT frame
(`_build_open`) needs revising — round-1's "bland gold strip in a small
gap" failed the EUREKA-TREASURE read. This sheet renders five distinctly
different open-moment directions on the same W4 identity so the user
can pick from real visuals rather than text.

Sheet layout — 3 cols x 2 rows.

  REF  Closed W4 (in-air)                — the silhouette the player
                                            sees a frame earlier.
  O1   Cinematic frame                   — 45deg back-rotated lid +
                                            coin stack + gold halo.
  O2   Lid blown off + light pillar      — detached lid floating high,
                                            vertical bright pillar from
                                            the open body.
  O3   Starburst halo                    — 12-ray cream/gold/white fan
                                            BEHIND the chest, arcade
                                            JACKPOT read.
  O4   Spilling coin pile  (B2 port)     — proven round-2 recipe: dark
                                            void interior + back coins +
                                            5 spilling over the lip +
                                            1 leap-out coin above the lid.
  O5   Crown emerges                     — gold 3-point crown with red
                                            velvet arch + RGB gems rising
                                            from inside the body.

Output: docs/treasure_box/open_chest_options.png  (doc-only; not shipped)
"""
from __future__ import annotations

import math
import os
import sys

# Headless render — both build targets reuse this same Pygame surface API,
# but this tool is desktop-only doc tooling so the dummy drivers are safe.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(THIS_DIR)
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, THIS_DIR)

pygame.init()
pygame.display.set_mode((1, 1))

# ── Reuse the production W4 builder + helpers ───────────────────────────────
# The runtime module already factors out every primitive we need (body,
# curved lid, brass bands, brass star, lock plate, lid strap, unifiers,
# vgrad rect, supersample constants). This tool re-uses them verbatim so
# the OPEN candidates remain pixel-identical W4 walnut/brass — they are
# five takes on W4's OPENING, not five different chests.
from game.treasure_box import (  # noqa: E402  (deferred until pygame init)
    PICKUP_W,
    PICKUP_H,
    SS,
    INK,
    CREAM,
    WALNUT_HI,
    WALNUT_MID,
    WALNUT_LO,
    WALNUT_GRAIN,
    BRASS_HI,
    BRASS_MID,
    BRASS_LO,
    BRASS_INK,
    GOLD_INK,
    GLOW_HI,
    GLOW_LO,
    LID_GRAIN,
    _new_big,
    _common_layout,
    _chest_body,
    _curved_lid,
    _brass_bands_and_grain,
    _brass_star,
    _brass_lock_plate,
    _lid_strap,
    _apply_unifiers,
    _smoothscale,
    _vgrad_rect,
    _build_closed,
    _build_open as _build_open_round1,
    _lerp,
)

# `_gold_coin` and the dawn-sparkle swatch belong to the parent design
# tool so the cell idiom matches the existing treasure_box docs sheets.
import importlib.util  # noqa: E402

_parent_spec = importlib.util.spec_from_file_location(
    "rtbo_parent",
    os.path.join(THIS_DIR, "render_treasure_box_options.py"),
)
_parent_mod = importlib.util.module_from_spec(_parent_spec)
_parent_spec.loader.exec_module(_parent_mod)
_gold_coin = _parent_mod._gold_coin
_dawn_sparkle_swatch = _parent_mod._dawn_sparkle_swatch


# ── Shared open-state primitives ────────────────────────────────────────────
# Interior void — used by O1/O2/O4/O5 so the inside of the open body
# reads as shadow, not as more walnut. Same recipe as B2's dark inner
# rectangle in the parent tool, retuned for the W4 darker walnut.
INNER_HI = (40, 22, 14)
INNER_LO = (10, 6, 4)

# Premixed gold-glow halo colours for soft additive blits.
HALO_CORE = (255, 232, 158)
HALO_RING = (255, 196, 96)


def _inner_void(big, body, ink):
    """Dark inset inside the body so coins / crown / light read against
    a shadow rather than getting lost on the walnut gradient."""
    inner = pygame.Rect(body.left + int(body.width * 0.10),
                        body.top + int(body.height * 0.04),
                        body.width - int(body.width * 0.20),
                        int(body.height * 0.55))
    _vgrad_rect(big, inner, INNER_HI, INNER_LO,
                radius=max(2, inner.width // 16))
    pygame.draw.rect(big, INK, inner,
                     max(1, ink // 2),
                     border_radius=max(2, inner.width // 16))
    return inner


def _rotated_lid_surface(lid_rect, angle_deg, ink, with_strap=True):
    """Build the W4 curved lid on its own SRCALPHA surface and rotate it.
    The rotated surface is returned along with its (un-rotated) bottom-
    centre point in local coords so the caller can pin it to a hinge."""
    pad = max(8, ink * 4)
    surf_w = lid_rect.width + pad * 2
    surf_h = int(lid_rect.height * 1.85) + pad * 2
    surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    local = pygame.Rect(pad, surf_h - pad - lid_rect.height,
                        lid_rect.width, lid_rect.height)
    _curved_lid(surf, local, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO,
                grain=True, sheen=True)
    if with_strap:
        _lid_strap(surf, local, ink)
    rot = pygame.transform.rotate(surf, angle_deg)
    # Track the original midbottom (in the un-rotated frame) so the
    # caller can pin the rotated lid back to a hinge point.
    return rot, (pad + lid_rect.width // 2, surf_h - pad)


def _gold_halo(big, cx, cy, r, layers=6, max_alpha=140):
    """Stacked translucent discs — a soft gold halo behind a focal
    element. Concentric so the alpha-add reads as a glow rather than
    a hard ring."""
    halo = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    hcx, hcy = halo.get_width() // 2, halo.get_height() // 2
    for k in range(layers):
        t = k / max(1, layers - 1)
        rr = int(r * (1.6 - t * 0.7))
        col = _lerp(HALO_RING, HALO_CORE, t)
        a = int(max_alpha * (1 - t * 0.7))
        pygame.draw.circle(halo, (*col, a), (hcx, hcy), rr)
    big.blit(halo, halo.get_rect(center=(cx, cy)))


# ── Builders ────────────────────────────────────────────────────────────────

def build_o1_cinematic():
    """O1 — Cinematic frame.

    Lid rotated ~45deg backward on a rear hinge; inside the body a 3-coin
    stack sits on a bright gold-glow halo; brass star anchors the front."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO)
    _brass_bands_and_grain(big, body, ink)
    inner = _inner_void(big, body, ink)

    # Bright halo first so the coin stack catches a rim of warm gold.
    halo_cx = inner.centerx
    halo_cy = inner.top + int(inner.height * 0.55)
    _gold_halo(big, halo_cx, halo_cy,
               max(SS * 4, int(inner.width * 0.55)),
               layers=7, max_alpha=170)

    # 3 stacked gold coin discs — rear (small), mid, front (largest).
    coin_r = max(4, int(inner.height * 0.20))
    stack_cx = inner.centerx
    stack_base_y = inner.bottom - int(inner.height * 0.12)
    for k, (dx, dy, rs) in enumerate(((-2, 0, 0.95),
                                       (1, -int(coin_r * 0.9), 1.00),
                                       (-1, -int(coin_r * 1.7), 0.90))):
        _gold_coin(big, stack_cx + dx, stack_base_y + dy,
                   int(coin_r * rs), ink)

    # Lid rotated 45deg backward on a hinge near the body's back-top
    # corner. Drawn after the coin pile so the lid pivots above it.
    rot, (mb_x, mb_y) = _rotated_lid_surface(lid, 45, ink, with_strap=True)
    hinge = (body.left + int(lid.width * 0.18),
             body.top - int(lid.height * 0.06))
    big.blit(rot, rot.get_rect(midbottom=hinge))

    # Brass lock plate stays on the body's front face (clasp gone — it
    # left with the lid).
    _brass_lock_plate(big, body, ink, with_clasp=False)
    _apply_unifiers(big, body, lid)
    return _smoothscale(big)


def build_o2_light_pillar():
    """O2 — Lid blown off + light pillar.

    Lid fully detached, floating ~50% body-height ABOVE the body with a
    ~15deg tilt and semi-transparent (alpha ~180); a vertical bright-gold
    pillar shoots up from the open body, fading toward the top of the
    icon; 3 coins visible inside the chest; brass lock + star stay on
    the body front."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO)
    _brass_bands_and_grain(big, body, ink)
    inner = _inner_void(big, body, ink)

    # Vertical light pillar — a tall narrow alpha-tapered band rising
    # from the body's open top. Drawn BEFORE the lid so the lid (and its
    # alpha) sit on top of the pillar's bottom segment.
    pillar_w = int(body.width * 0.55)
    pillar_top = max(0, body.top - int(PICKUP_H * SS * 0.65))
    pillar_bot = inner.top + int(inner.height * 0.30)
    pillar = pygame.Surface((pillar_w, pillar_bot - pillar_top),
                            pygame.SRCALPHA)
    for y in range(pillar.get_height()):
        t = y / max(1, pillar.get_height() - 1)
        # Bright at the body opening, fading toward the top of the cell.
        a = int(220 * (1 - (1 - t) ** 1.6))
        col = _lerp(GLOW_HI, HALO_RING, 1 - t)
        # Inner core line — brighter, narrower.
        pygame.draw.line(pillar, (*col, a),
                         (0, y), (pillar.get_width(), y))
    # Soft horizontal edge fade so the pillar feathers at its sides.
    feather = pygame.Surface(pillar.get_size(), pygame.SRCALPHA)
    feather.fill((255, 255, 255, 255))
    edge = max(2, pillar.get_width() // 6)
    for ex in range(edge):
        a = int(255 * (ex / max(1, edge)))
        pygame.draw.line(feather, (255, 255, 255, a),
                         (ex, 0), (ex, pillar.get_height()), 1)
        pygame.draw.line(feather, (255, 255, 255, a),
                         (pillar.get_width() - 1 - ex, 0),
                         (pillar.get_width() - 1 - ex,
                          pillar.get_height()), 1)
    pillar.blit(feather, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(pillar,
             (body.centerx - pillar_w // 2, pillar_top))

    # 3 coins inside the body, against the void.
    coin_r = max(4, int(inner.height * 0.18))
    for (ox, oy, rs) in ((-0.28, -0.08, 0.95),
                         (0.06, -0.18, 1.05),
                         (0.30, -0.02, 0.90)):
        _gold_coin(big,
                   inner.centerx + int(inner.width * ox),
                   inner.centery + int(inner.height * oy),
                   int(coin_r * rs), ink)

    # Lid floats well above the body, tilted ~15deg, alpha ~180. Built on
    # its own surface so we can alpha + rotate before blitting.
    rot, _ = _rotated_lid_surface(lid, 15, ink, with_strap=True)
    rot.set_alpha(180)
    lift_above = int(body.height * 0.55)
    lift_target = (body.centerx, body.top - lift_above)
    big.blit(rot, rot.get_rect(midbottom=lift_target))

    # Brass lock + star stay where the lid lifted from — the clasp is
    # gone because it travelled with the lid.
    _brass_lock_plate(big, body, ink, with_clasp=False)
    _apply_unifiers(big, body, lid)
    return _smoothscale(big)


def build_o3_starburst():
    """O3 — Starburst halo.

    12-ray cream/gold/white fan BEHIND the chest (drawn first), rays
    extending past the chest by ~50% on every side. Lid tilted ~25deg
    back; 3 coins visible inside. Reads as arcade JACKPOT."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Starburst FIRST so it sits underneath the chest silhouette.
    burst_cx = body.centerx
    burst_cy = (lid.top + body.bottom) // 2
    burst_outer = int(max(body.width, body.height) * 0.95)
    burst_inner = int(burst_outer * 0.34)

    rays = 12
    pts = []
    # Alternating outer / inner vertices around 12 rays — even index =
    # outer point (= the spike tip), odd = inner valley.
    for i in range(rays * 2):
        ang = -math.pi / 2 + i * math.pi / rays
        r = burst_outer if i % 2 == 0 else burst_inner
        pts.append((burst_cx + math.cos(ang) * r,
                    burst_cy + math.sin(ang) * r))
    # Cream outer fill.
    pygame.draw.polygon(big, CREAM, pts)
    pygame.draw.polygon(big, GOLD_INK, pts, max(2, ink - 1))
    # Inner-shrunk polygon in warm gold for a 2-tone spoke read.
    inner_pts = [(burst_cx + (p[0] - burst_cx) * 0.70,
                  burst_cy + (p[1] - burst_cy) * 0.70)
                 for p in pts]
    pygame.draw.polygon(big, GLOW_HI, inner_pts)
    pygame.draw.polygon(big, GOLD_INK, inner_pts, max(1, ink // 2))
    # Bright cream core disc — the chest sits on top of this so the
    # immediate halo behind the body reads as bright sunlight.
    pygame.draw.circle(big, (255, 250, 224),
                       (burst_cx, burst_cy),
                       int(burst_inner * 0.92))

    # Chest body + bands.
    _chest_body(big, body, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO)
    _brass_bands_and_grain(big, body, ink)
    inner = _inner_void(big, body, ink)

    # 3 coins inside the open body, slightly stacked toward the front.
    coin_r = max(4, int(inner.height * 0.20))
    for (ox, oy, rs) in ((-0.22, 0.04, 0.95),
                         (0.10, -0.06, 1.05),
                         (0.32, 0.10, 0.90)):
        _gold_coin(big,
                   inner.centerx + int(inner.width * ox),
                   inner.centery + int(inner.height * oy),
                   int(coin_r * rs), ink)

    # Lid tilted 25deg back on a rear-corner hinge.
    rot, _ = _rotated_lid_surface(lid, 25, ink, with_strap=True)
    hinge = (body.left + int(lid.width * 0.20),
             body.top - int(lid.height * 0.04))
    big.blit(rot, rot.get_rect(midbottom=hinge))

    _brass_lock_plate(big, body, ink, with_clasp=False)
    _apply_unifiers(big, body, lid)
    return _smoothscale(big)


def build_o4_spilling_coins():
    """O4 — Spilling coin pile (port of B2).

    Proven round-2 recipe: dark interior void, 3 coins inside, 5 coins
    spilling over the front lip (breaking the silhouette), 1 LARGER coin
    floating above the open lid. Lid rotated ~28deg back. W4 walnut +
    brass palette replaces B2's original wood for identity preservation."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO)
    _brass_bands_and_grain(big, body, ink)
    # Custom inner void — B2's recipe uses a shallower inset than
    # `_inner_void`'s default so the spill coins overlap the front lip.
    inner = pygame.Rect(body.left + int(body.width * 0.10),
                        body.top + int(body.height * 0.04),
                        body.width - int(body.width * 0.20),
                        int(body.height * 0.40))
    _vgrad_rect(big, inner, INNER_HI, INNER_LO,
                radius=max(2, inner.width // 16))
    pygame.draw.rect(big, INK, inner,
                     max(1, ink // 2),
                     border_radius=max(2, inner.width // 16))

    # Lid rotated 28deg back on a rear hinge — drawn BEFORE coins so the
    # leap-out coin sits in front of the lid silhouette.
    rot, _ = _rotated_lid_surface(lid, 28, ink, with_strap=True)
    hinge = (body.left + int(lid.width * 0.18),
             body.top - int(lid.height * 0.10))
    big.blit(rot, rot.get_rect(midbottom=hinge))

    pile_cy = body.top + int(body.height * 0.55)
    coin_r0 = int(body.height * 0.18)
    # Back row — three coins inside the void, partially behind the front lip.
    for (ox, oy, rs) in ((-0.28, -0.20, 1.0),
                         (0.08, -0.26, 1.0),
                         (0.32, -0.10, 0.9)):
        _gold_coin(big,
                   body.centerx + int(body.width * ox),
                   pile_cy + int(body.height * oy),
                   max(3, int(coin_r0 * rs)), ink)
    # Front spill — 5 coins overlapping the body's front edge to break
    # the silhouette so the spill reads as motion, not a sticker.
    for (ox, oy, rs) in ((-0.36, 0.18, 1.05),
                         (-0.10, 0.30, 1.10),
                         (0.18, 0.32, 1.00),
                         (0.40, 0.20, 0.95),
                         (-0.22, 0.40, 0.90)):
        _gold_coin(big,
                   body.centerx + int(body.width * ox),
                   pile_cy + int(body.height * oy),
                   max(3, int(coin_r0 * rs)), ink)
    # ONE larger leap-out coin floating above the open lid — captures the
    # "treasure jumping out" beat.
    _gold_coin(big,
               body.centerx + int(body.width * 0.12),
               pile_cy + int(body.height * -0.92),
               max(4, int(coin_r0 * 1.10)), ink)

    _brass_lock_plate(big, body, ink, with_clasp=False)
    _apply_unifiers(big, body, lid)
    return _smoothscale(big)


def build_o5_crown():
    """O5 — Crown emerges.

    Lid tilted ~30deg back. A stylised gold 3-point crown rises out of
    the body — half inside the body, half visible above the body line.
    The crown carries a red velvet arch + 3 small gem dots (red/blue/
    green). Soft gold halo behind the crown."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO)
    _brass_bands_and_grain(big, body, ink)
    inner = _inner_void(big, body, ink)

    # Halo behind the crown — drawn before the crown so it sits as a
    # warm aura around it. Bigger than the coin-stack halo in O1.
    halo_cx = body.centerx
    halo_cy = body.top - int(body.height * 0.05)
    _gold_halo(big, halo_cx, halo_cy,
               int(body.height * 0.85),
               layers=7, max_alpha=160)

    # Crown geometry — base is anchored INSIDE the body so the bottom
    # half is hidden by the inner void's front lip, top half breaks out
    # above the body's top line.
    crown_w = int(body.width * 0.60)
    crown_h = int(body.height * 0.95)
    crown_cx = body.centerx
    # Tip of the centre peak sits above the body's top by ~12% of body
    # height — this is the silhouette-breaking moment.
    crown_top_y = body.top - int(body.height * 0.18)
    crown_base_y = body.top + int(body.height * 0.40)

    # Three-peak crown silhouette — symmetric, centre peak tallest.
    side_peak_dx = crown_w // 3
    side_peak_y = crown_top_y + int(crown_h * 0.25)
    cpts = [
        (crown_cx - crown_w // 2, crown_base_y),
        (crown_cx - crown_w // 2, crown_base_y - int(crown_h * 0.42)),
        (crown_cx - side_peak_dx, side_peak_y),
        (crown_cx - crown_w // 6, crown_base_y - int(crown_h * 0.55)),
        (crown_cx, crown_top_y),
        (crown_cx + crown_w // 6, crown_base_y - int(crown_h * 0.55)),
        (crown_cx + side_peak_dx, side_peak_y),
        (crown_cx + crown_w // 2, crown_base_y - int(crown_h * 0.42)),
        (crown_cx + crown_w // 2, crown_base_y),
    ]
    # Two-tone gold so the crown reads dimensionally: bright top half,
    # darker base band for solidity.
    pygame.draw.polygon(big, BRASS_HI, cpts)
    pygame.draw.polygon(big, BRASS_LO,
                        [(crown_cx - crown_w // 2,
                          crown_base_y - int(crown_h * 0.18)),
                         (crown_cx + crown_w // 2,
                          crown_base_y - int(crown_h * 0.18)),
                         (crown_cx + crown_w // 2, crown_base_y),
                         (crown_cx - crown_w // 2, crown_base_y)])
    pygame.draw.polygon(big, BRASS_INK, cpts, max(1, ink - 1))

    # Red velvet arch — a thick red curve spanning between the centre
    # spike and the two side peaks, suggesting an imperial cap interior.
    arch_left = (crown_cx - side_peak_dx, side_peak_y)
    arch_right = (crown_cx + side_peak_dx, side_peak_y)
    arch_apex = (crown_cx, crown_top_y + int(crown_h * 0.20))
    arch_bot = (crown_cx, crown_base_y - int(crown_h * 0.20))
    arch_pts = [
        arch_left,
        arch_apex,
        arch_right,
        (crown_cx + side_peak_dx // 2, arch_bot[1]),
        arch_bot,
        (crown_cx - side_peak_dx // 2, arch_bot[1]),
    ]
    pygame.draw.polygon(big, (152, 28, 36), arch_pts)
    pygame.draw.polygon(big, (96, 14, 24), arch_pts, max(1, ink // 2))
    # A pin-glint near the arch's top so the velvet reads as glossy fabric.
    glint = (crown_cx - side_peak_dx // 3,
             arch_apex[1] + int(crown_h * 0.05))
    pygame.draw.circle(big, (220, 110, 110), glint,
                       max(1, int(SS * 0.6)))

    # 3 small gem dots on the crown's front base band — RED / BLUE / GREEN.
    gem_y = crown_base_y - int(crown_h * 0.08)
    gem_r = max(2, int(SS * 0.9))
    for (gx, col) in (
        (crown_cx - int(crown_w * 0.28), (236, 64, 80)),     # ruby
        (crown_cx,                       (96, 152, 240)),    # sapphire
        (crown_cx + int(crown_w * 0.28), (96, 200, 132)),    # emerald
    ):
        # Bright outer ring + saturated centre + dark rim for legibility.
        pygame.draw.circle(big, (255, 250, 220), (gx, gem_y), gem_r + 1)
        pygame.draw.circle(big, col, (gx, gem_y), gem_r)
        pygame.draw.circle(big, BRASS_INK, (gx, gem_y), gem_r,
                           max(1, ink // 3))

    # Lid tilted 30deg back — drawn after the crown so the lid sits
    # behind the centre spike for the silhouette break.
    rot, _ = _rotated_lid_surface(lid, 30, ink, with_strap=True)
    hinge = (body.left + int(lid.width * 0.20),
             body.top - int(lid.height * 0.06))
    big.blit(rot, rot.get_rect(midbottom=hinge))

    _brass_lock_plate(big, body, ink, with_clasp=False)
    _apply_unifiers(big, body, lid)
    return _smoothscale(big)


# Closed reference uses the production builder directly so the user sees
# the EXACT in-air sprite they already approved.
def build_ref_closed():
    return _build_closed()


CANDIDATES = [
    ("REF", "Closed W4 (in-air)",         build_ref_closed),
    ("O1",  "Cinematic frame",            build_o1_cinematic),
    ("O2",  "Lid blown off + light pillar", build_o2_light_pillar),
    ("O3",  "Starburst halo",             build_o3_starburst),
    ("O4",  "Spilling coin pile (B2 port)", build_o4_spilling_coins),
    ("O5",  "Crown emerges",              build_o5_crown),
]


# Canonical float-bob phase so each candidate sits on its swatch like a
# real in-flight pickup. Matches the parent design tool's constant.
BOB_PULSE = 1.15


def main():
    out_dir = os.path.join(REPO_ROOT, "docs", "treasure_box")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "open_chest_options.png")

    bob = int(round(math.sin(BOB_PULSE * 0.8) * 2))

    cell_w, cell_h = 320, 340
    cols = 3
    rows = 2
    pad = 16
    header_h = 96
    cap_h = 34

    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * pad
    sheet_h = header_h + rows * (cell_h + cap_h) + (rows - 1) * pad + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 30))

    def font(sz, bold=False):
        return pygame.font.SysFont("Arial", sz, bold=bold)

    title = font(26, bold=True).render(
        "TREASURE BOX — OPEN-CHEST OPTIONS — round 1 (5 directions)",
        True, (240, 240, 246))
    sheet.blit(title, (pad, pad))
    sub = font(14).render(
        "REF = approved closed W4 in-air sprite for comparison.  "
        "O1–O5 = five distinct PEAK-MOMENT open frames on the same W4 identity.",
        True, (170, 178, 192))
    sheet.blit(sub, (pad, pad + 32))
    sub2 = font(13).render(
        "Left half of each cell = real pickup ~56x46 px (float-bobbed); "
        "right half = 3x zoom.  Dawn/sunrise sky + sparkle backdrop.",
        True, (200, 180, 150))
    sheet.blit(sub2, (pad, pad + 54))

    for idx, (tag, name, fn) in enumerate(CANDIDATES):
        row = idx // cols
        col = idx % cols
        x = pad + col * (cell_w + pad)
        y = header_h + pad + row * (cell_h + cap_h + pad)

        swatch = _dawn_sparkle_swatch(cell_w, cell_h, seed=idx + 11)
        sheet.blit(swatch, (x, y))
        pygame.draw.rect(sheet, (60, 66, 84), (x, y, cell_w, cell_h), 1)

        icon = fn()

        # Real pickup on the left half.
        true_cx = x + cell_w // 4 - PICKUP_W // 2
        true_cy = y + cell_h // 2 - PICKUP_H // 2 + bob
        sheet.blit(icon, (true_cx, true_cy))
        pygame.draw.rect(sheet, (255, 255, 255),
                         (true_cx - 3, true_cy - bob - 3,
                          PICKUP_W + 6, PICKUP_H + 6), 1)
        lbl = font(12).render(f"real pickup ~{PICKUP_W}x{PICKUP_H} px",
                              True, (210, 220, 235))
        sheet.blit(lbl, (x + 10, y + cell_h - 24))

        # 3x zoom on the right half.
        zoom = pygame.transform.smoothscale(
            icon, (PICKUP_W * 3, PICKUP_H * 3))
        zx = x + cell_w - PICKUP_W * 3 - 18
        zy = y + cell_h // 2 - (PICKUP_H * 3) // 2
        sheet.blit(zoom, (zx, zy))
        zl = font(12).render("3x zoom", True, (210, 220, 235))
        sheet.blit(zl, (zx + PICKUP_W * 3 - 56, zy - 18))

        cap = font(16, bold=True).render(f"{tag}  {name}", True,
                                         (245, 240, 230))
        sheet.blit(cap, (x + 8, y + cell_h + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()

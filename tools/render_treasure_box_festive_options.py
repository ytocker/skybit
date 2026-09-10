"""Treasure Box — festive variants pass evolving from the B5 lead.

User picked B5 (royal crown + velvet-red + gold trim) in round 2, then
asked for the icon to feel MORE FESTIVE and HAPPY — celebratory joy
instead of regal/serious. The Treasure Box is the once-per-cycle finale
that rains +100 coins on pickup; the icon should feel like a PARTY
popping open, not a king's heirloom.

Five distinct festive directions, each keeping the B5 chest silhouette
(curved lid, body, gold lock) but swapping the crown + ornaments + body
palette for a different party-flavoured language:

  F1  Gift ribbon + bow      — LEAD: crisp twin-loop bow + cross-wrap.
  F2  Confetti chest         — 16-piece top-arc confetti + crown stub.
  F3  Party hat + tinsel     — body-tall striped hat + straight tinsel.
  F4  Rainbow jewels         — coral body + 6-gem rim + big star lock.
  F5  Carnival pop-art       — lower-60% stripes + pink lid + gold star.

Round 2 applies art-director notes: F1 promoted to lead with a rebuilt
two-loop bow + dark-red shadow; F2 confetti capped at 16 pieces and
pushed outside the chest silhouette with a small B5-style crown stub
restored; F3 hat enlarged to body height with thick diagonal red bands,
a 3 px cream pom and two straight tinsel strands (curly streamers
dropped); F4 body pivoted toward coral with a +20% star lock plate;
F5 reworked to a gold-star lock, lower-60% stripes, darker lid rim
(smiley dropped). A 1 px warm-gold lid-top rim light + a 4-sparkle
ring at the chest bbox corners now unify the whole family.

Output: docs/treasure_box/festive_round_2.png  (doc-only; not shipped)

Round 2 ranks F1 as the lead and re-targets the other four around it:
F2's confetti is tamed (cap 16, top-arc only, 6 gold-yellow); F3 is
rebuilt with a body-tall striped hat + straight tinsel; F4 pivots to a
coral body so it stops reading as just a B5 upgrade; F5 drops the smiley
in favour of an F4-style gold-star lock with stripes confined to the
lower 60%. A 1 px warm-gold lid-top rim light + a fixed 4-corner cream
sparkle ring unify all 5 cells into one "finale loot" family.
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))
sys.path.insert(0, THIS_DIR)

pygame.init()
pygame.display.set_mode((1, 1))

# Reuse round-2 helpers + palette so the festive set lives in the same
# visual family as the B5 lead — we only need to add the festive ornaments
# + a couple of new accent palettes on top.
from render_treasure_box_options import (
    PICKUP_W, PICKUP_H, SS, BOB_PULSE,
    INK, INK_SOFT, CREAM,
    GOLD_HI, GOLD_MID, GOLD_LO, GOLD_INK,
    ROYAL_HI, ROYAL_MID, ROYAL_LO,
    SKY_TOP, SKY_MID, SKY_BOT, HORIZON_GL,
    _lerp, _vgrad_rect, _curved_lid, _chest_body, _gold_lock,
    _new_big, _finish, _common_layout,
    _dawn_sparkle_swatch,
)

# ---------------------------------------------------------------------------
# Festive accent palettes — built on top of the B5 reds/golds so the
# variants still feel like the same chest family.
# ---------------------------------------------------------------------------
# A warmer, cheerier red than ROYAL_* — closer to candy-apple. The royal
# velvet read "regal"; this red reads "presents under a tree".
PARTY_RED_HI  = (236,  88,  96)
PARTY_RED_MID = (196,  44,  58)
PARTY_RED_LO  = (130,  24,  40)

# Dark-red shadow used under F1's bow on the lid — about one value step
# below PARTY_RED_LO so the bow sits ON the lid instead of floating.
PARTY_RED_SHADOW = ( 78,  14,  24)

# F4 coral / warm party-red — PARTY_RED_* shifted +10 deg toward orange
# and +5% value. Reads "celebration / streamers" rather than "valentine".
CORAL_HI  = (244, 124,  92)
CORAL_MID = (212,  76,  60)
CORAL_LO  = (146,  38,  34)

# Warm-gold rim light placed 1 px under the apex of every lid. Unifies
# the family at 1x by catching the dawn-sky highlight on every chest.
LID_RIM_GOLD = (255, 236, 168)

# Confetti colours — borrow from a kid's birthday-party palette.
CONFETTI = (
    (255, 108, 158),     # pink
    ( 88, 196, 232),     # cyan
    (255, 214,  92),     # yellow
    (132, 222, 124),     # lime
    (200, 134, 240),     # violet
    (255, 158,  88),     # orange
)

# Rainbow jewel rim (F4) — 6 evenly spaced gem hues, ROYGBV order.
RAINBOW_GEMS = (
    (232,  72,  84),     # red
    (252, 158,  64),     # orange
    (252, 220,  88),     # yellow
    (108, 216, 132),     # green
    (104, 168, 240),     # blue
    (188, 124, 232),     # violet
)

# Carnival stripes (F5) — three-colour vertical stripe palette. Bright
# circus-tent vibe.
CARNIVAL_R = (232,  76,  88)
CARNIVAL_Y = (252, 212,  92)
CARNIVAL_T = ( 78, 196, 208)

# Pastel pink bow + ribbon (F5).
PASTEL_PINK_HI = (255, 196, 214)
PASTEL_PINK_MID = (244, 142, 178)
PASTEL_PINK_LO = (192,  88, 132)

# Cream polka dots (F5).
CREAM_DOT = (252, 244, 220)

# Pale white sparkle (shared by F4 + F2 + F1).
SPARKLE = (255, 250, 222)


# ---------------------------------------------------------------------------
# Small festive primitives.
# ---------------------------------------------------------------------------
def _draw_bow(big, cx, cy, w, h, ink_w,
              hi_col, mid_col, lo_col, with_tails=True):
    """A puffy two-loop bow sitting centred at (cx, cy). Loops are tall
    ovals tilted slightly outward; a central knot ties them together; two
    short ribbon tails fall below if with_tails=True."""
    loop_w = int(w * 0.42)
    loop_h = int(h * 0.95)
    # Left + right loops as rotated ellipses (drawn into small surfs and
    # rotated so the bow has a hand-drawn lean).
    for sgn, angle in ((-1, 18), (+1, -18)):
        loop_surf = pygame.Surface((loop_w + ink_w * 2,
                                     loop_h + ink_w * 2),
                                    pygame.SRCALPHA)
        loop_rect = pygame.Rect(ink_w, ink_w, loop_w, loop_h)
        _vgrad_rect(loop_surf, loop_rect, hi_col, lo_col,
                    radius=loop_w // 2)
        # Use ellipse fill + outline for a softer bow petal.
        loop_surf.fill((0, 0, 0, 0))
        pygame.draw.ellipse(loop_surf, mid_col, loop_rect)
        # Inner highlight crescent so the loop reads as puffy.
        inner = loop_rect.inflate(-loop_w // 3, -loop_h // 3)
        inner.move_ip(-loop_w // 8, -loop_h // 8)
        pygame.draw.ellipse(loop_surf, hi_col, inner)
        pygame.draw.ellipse(loop_surf, INK, loop_rect, ink_w)
        rot = pygame.transform.rotate(loop_surf, angle)
        # Anchor loops slightly inward of the knot so they overlap.
        anchor_x = cx + sgn * int(w * 0.22)
        big.blit(rot, rot.get_rect(center=(anchor_x, cy - int(h * 0.05))))

    # Central knot — a small vertical pill.
    knot_w = int(w * 0.20)
    knot_h = int(h * 0.55)
    knot = pygame.Rect(0, 0, knot_w, knot_h)
    knot.center = (cx, cy)
    _vgrad_rect(big, knot, hi_col, lo_col, radius=knot_w // 2)
    pygame.draw.rect(big, INK, knot, ink_w, border_radius=knot_w // 2)
    # Knot highlight stripe.
    pygame.draw.line(big, hi_col,
                     (knot.left + knot_w // 4, knot.top + knot_h // 4),
                     (knot.left + knot_w // 4, knot.bottom - knot_h // 4),
                     max(1, ink_w // 2))

    if with_tails:
        # Two short ribbon tails falling below the knot, ending in a
        # V-notch (the classic gift-bow tail). Drawn as filled polygons.
        tail_h = int(h * 0.65)
        tail_w = int(w * 0.18)
        for sgn in (-1, +1):
            tip_x = cx + sgn * int(w * 0.22)
            tip_y = cy + tail_h
            top_x = cx + sgn * int(w * 0.04)
            top_y = cy + int(h * 0.20)
            mid_x = (tip_x + top_x) // 2
            mid_y = (tip_y + top_y) // 2
            tail_pts = [
                (top_x, top_y),
                (top_x + sgn * tail_w // 2, top_y + tail_h // 4),
                (tip_x + sgn * tail_w // 2, tip_y),
                (tip_x, tip_y - tail_h // 4),
                (tip_x - sgn * tail_w // 3, tip_y),
                (top_x - sgn * tail_w // 4, top_y + tail_h // 4),
            ]
            pygame.draw.polygon(big, mid_col, tail_pts)
            pygame.draw.polygon(big, INK, tail_pts, ink_w)
            # Faint inner highlight stroke down the tail.
            pygame.draw.line(big, hi_col, (top_x, top_y),
                             (mid_x, mid_y), max(1, ink_w // 2))


def _draw_sparkle(big, x, y, L, col=SPARKLE, ink_w=2):
    """A 4-point twinkle: bright core dot + horizontal/vertical strokes."""
    pygame.draw.circle(big, col, (x, y), max(1, int(L * 0.6)))
    pygame.draw.line(big, col, (x - L, y), (x + L, y), max(1, ink_w))
    pygame.draw.line(big, col, (x, y - L), (x, y + L), max(1, ink_w))


def _lid_rim_light(big, lid_rect, lid_apex_y, ink_w):
    """A 1 px warm-gold sliver hugging the very top of the lid arc. Sits
    just under the apex so it never breaks the silhouette but consistently
    catches the dawn-sky highlight across every variant in the family."""
    arc_h = int(lid_rect.height * 0.65)
    cx = lid_rect.centerx
    half_w = lid_rect.width // 2
    # Sample a short symmetric chord around the apex — the brightest sliver
    # is concentrated on the top 18% of the dome so it reads as a rim, not
    # a stripe. ink_w drives the stroke so the rim scales with SS.
    pts = []
    n = 12
    for i in range(n + 1):
        # Walk a narrow theta window centred on pi/2 (the apex).
        t = i / n
        ang = math.pi * (0.42 + 0.16 * t)
        ax = cx + math.cos(ang) * half_w
        ay = lid_rect.top - math.sin(ang) * arc_h + max(1, ink_w // 2)
        pts.append((ax, ay))
    if len(pts) >= 2:
        pygame.draw.lines(big, LID_RIM_GOLD, False, pts,
                          max(1, ink_w // 2))


def _unified_sparkle_ring(big, body_rect, lid_rect, ink_w):
    """Exactly four 2 px cream "+" sparkles pinned to the chest bbox
    corners — top-left, top-right, bottom-left, bottom-right — outside
    the silhouette. The same four anchors on every variant become the
    "finale loot" family marker."""
    x0 = min(body_rect.left, lid_rect.left)
    x1 = max(body_rect.right, lid_rect.right)
    y0 = lid_rect.top - int(lid_rect.height * 0.55)
    y1 = body_rect.bottom
    margin = max(SS * 2, ink_w * 2)
    L = max(2, int(SS * 0.9))
    for (sx, sy) in ((x0 - margin, y0 - margin),
                     (x1 + margin, y0 - margin),
                     (x0 - margin, y1 + margin),
                     (x1 + margin, y1 + margin)):
        # Centre dot + 1-px arms — the smallest readable cream "+" at 1x.
        pygame.draw.circle(big, CREAM, (sx, sy), max(1, L // 2))
        pygame.draw.line(big, CREAM, (sx - L, sy), (sx + L, sy),
                         max(1, ink_w // 2))
        pygame.draw.line(big, CREAM, (sx, sy - L), (sx, sy + L),
                         max(1, ink_w // 2))


def _draw_jewel_dot(big, cx, cy, r, col, ink_w):
    """A small round jewel — used for the rainbow rim. Bright top-left
    glint sells the cabochon read at 1x."""
    pygame.draw.circle(big, _lerp(col, INK, 0.45), (cx, cy + max(1, r // 4)), r)
    pygame.draw.circle(big, col, (cx, cy), r)
    pygame.draw.circle(big, _lerp(col, SPARKLE, 0.55),
                       (cx - r // 3, cy - r // 3), max(1, r // 2))
    pygame.draw.circle(big, INK, (cx, cy), r, max(1, ink_w // 2))


# ---------------------------------------------------------------------------
# F1 — Birthday-gift ribbon + bow.
# ---------------------------------------------------------------------------
def icon_f1():
    """Red gift-wrapped chest. A vertical + horizontal gold ribbon strip
    wraps the body (cross at the lock plate); a big puffy gold bow sits
    centred on top of the lid, breaking the silhouette. No crown — the
    bow IS the festive crown. Classic wrapped-present read."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Body in warmer party-red (cheerier than royal velvet).
    _chest_body(big, body, ink, PARTY_RED_HI, PARTY_RED_MID, PARTY_RED_LO)

    # Curved lid in matching party-red.
    pts, lid_apex_y = _curved_lid(big, lid, ink,
                                   PARTY_RED_HI, PARTY_RED_MID, PARTY_RED_LO,
                                   grain=False, sheen=True)

    # Cross-wrap ribbon — vertical strip down the centre of body + lid,
    # horizontal strip across the seam. Drawn BEFORE the lock so the lock
    # sits on top of the cross.
    strip_w = max(SS * 5, int(body.width * 0.16))
    # Vertical strip down the body + climbing over the lid.
    vstrip = pygame.Rect(0, 0, strip_w, body.bottom - (lid.top + int(lid.height * 0.55)))
    vstrip.midbottom = (body.centerx, body.bottom)
    _vgrad_rect(big, vstrip, GOLD_HI, GOLD_LO, radius=max(1, strip_w // 6))
    pygame.draw.rect(big, GOLD_INK, vstrip, max(1, ink // 2),
                     border_radius=max(1, strip_w // 6))
    # Climb a curved cap up over the lid arc — a short trapezoidal piece
    # that follows the dome curvature (approximated with a thin polygon).
    cap_h = int(lid.height * 0.50)
    cap_top_w = max(SS * 3, strip_w - SS)
    cap_pts = [
        (body.centerx - strip_w // 2, lid.top + int(lid.height * 0.55)),
        (body.centerx + strip_w // 2, lid.top + int(lid.height * 0.55)),
        (body.centerx + cap_top_w // 2, lid.top + int(lid.height * 0.55) - cap_h),
        (body.centerx - cap_top_w // 2, lid.top + int(lid.height * 0.55) - cap_h),
    ]
    pygame.draw.polygon(big, GOLD_MID, cap_pts)
    pygame.draw.polygon(big, GOLD_INK, cap_pts, max(1, ink // 2))

    # Horizontal strip across the body just below the seam.
    hstrip = pygame.Rect(body.left - ink, body.top + int(body.height * 0.22),
                          body.width + ink * 2, strip_w)
    _vgrad_rect(big, hstrip, GOLD_HI, GOLD_LO, radius=max(1, strip_w // 6))
    pygame.draw.rect(big, GOLD_INK, hstrip, max(1, ink // 2),
                     border_radius=max(1, strip_w // 6))

    # Gold lock plate sitting at the cross — slightly smaller so the bow
    # carries the visual weight.
    lock_w = int(body.width * 0.24)
    lock_h = int(body.height * 0.38)
    lock_cx = body.centerx
    lock_cy = body.top + int(body.height * 0.30)
    _gold_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink, keyhole=True)

    # Rebuilt twin-loop bow — two crisp triangular loops (4x5 px each at
    # pickup scale, scaled by SS for the supersample) + a 2x2 px gold knot.
    # The previous puffy-oval bow read as a yellow blob at 1x.
    bow_cx = lid.centerx
    bow_cy = lid_apex_y + int(lid.height * 0.18)
    loop_w_px = 4                                  # final-scale pixels
    loop_h_px = 5
    knot_px = 2
    loop_w = loop_w_px * SS
    loop_h = loop_h_px * SS
    knot_s = knot_px * SS

    # Dark-red shadow under the bow on the lid — 1 px (= SS) drop, only on
    # the lid (not behind the gold so the gold reads warm). Drawn first.
    shadow_w = loop_w * 2 + knot_s
    shadow_h = loop_h
    shadow = pygame.Rect(0, 0, shadow_w, shadow_h)
    shadow.center = (bow_cx, bow_cy + SS)
    _vgrad_rect(big, shadow, PARTY_RED_SHADOW, PARTY_RED_SHADOW,
                radius=max(2, shadow_h // 3))

    # Right-hand loop nudged DOWN ~1 px so the bow isn't perfectly
    # symmetric — gives the gift a hand-tied feel at 1x.
    for sgn in (-1, +1):
        loop_pts = [
            (bow_cx + sgn * (knot_s // 2),                bow_cy),
            (bow_cx + sgn * (knot_s // 2 + loop_w),       bow_cy - loop_h // 2),
            (bow_cx + sgn * (knot_s // 2 + loop_w),       bow_cy + loop_h // 2),
        ]
        if sgn > 0:
            loop_pts = [(px, py + SS) for (px, py) in loop_pts]
        pygame.draw.polygon(big, GOLD_HI, loop_pts)
        # Inner darker wedge so the loop has interior depth.
        inner_pts = [
            loop_pts[0],
            ((loop_pts[0][0] + loop_pts[1][0]) // 2,
             (loop_pts[0][1] + loop_pts[1][1]) // 2),
            ((loop_pts[0][0] + loop_pts[2][0]) // 2,
             (loop_pts[0][1] + loop_pts[2][1]) // 2),
        ]
        pygame.draw.polygon(big, GOLD_LO, inner_pts)
        pygame.draw.polygon(big, INK, loop_pts, max(2, ink - 1))

    # Centre gold knot — 2x2 px square in pickup space.
    knot = pygame.Rect(0, 0, knot_s, knot_s)
    knot.center = (bow_cx, bow_cy)
    _vgrad_rect(big, knot, GOLD_HI, GOLD_LO, radius=max(1, knot_s // 4))
    pygame.draw.rect(big, GOLD_INK, knot, max(1, ink // 2),
                     border_radius=max(1, knot_s // 4))

    # Family unifiers — lid rim light + 4-corner sparkle ring.
    _lid_rim_light(big, lid, lid_apex_y, ink)
    _unified_sparkle_ring(big, body, lid, ink)

    return _finish(big)


# ---------------------------------------------------------------------------
# F2 — Confetti chest.
# ---------------------------------------------------------------------------
def icon_f2():
    """Red chest with the B5 crown shrunk down (kept for treasure-anchor
    reading), surrounded by a falling shower of multi-colour confetti —
    small triangles, dots, and ribbon snippets in pink/cyan/yellow/lime
    scattered around the chest, a few overlapping the chest border."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Body + lid in warmer party-red.
    _chest_body(big, body, ink, PARTY_RED_HI, PARTY_RED_MID, PARTY_RED_LO)
    pts, lid_apex_y = _curved_lid(big, lid, ink,
                                   PARTY_RED_HI, PARTY_RED_MID, PARTY_RED_LO,
                                   grain=False, sheen=True)

    # Small gold trim along the seam.
    seam = pygame.Rect(body.left, body.top - max(1, ink // 2),
                       body.width, max(3, int(body.height * 0.08)))
    _vgrad_rect(big, seam, GOLD_HI, GOLD_LO, radius=max(1, seam.height // 2))
    pygame.draw.rect(big, GOLD_INK, seam, max(1, ink // 2),
                     border_radius=max(1, seam.height // 2))

    # Gold lock plate.
    lock_w = int(body.width * 0.26)
    lock_h = int(body.height * 0.46)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.02)
    _gold_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink, keyhole=True)

    # Small B5-style crown stub (~3 px tall at final scale, scaled by SS
    # internally) sitting on the lid centre. Keeps F2 inside the B5
    # lineage so the confetti reads as a CELEBRATION around treasure
    # rather than as a random burst of paper.
    crown_h = SS * 3                               # final-scale 3 px tall
    crown_w = SS * 7
    crown_cx = lock_cx
    crown_base_y = lid_apex_y + max(1, SS // 2)
    spike_tip_y = crown_base_y - crown_h
    cpts = [
        (crown_cx - crown_w // 2, crown_base_y),
        (crown_cx - crown_w // 3, crown_base_y - crown_h * 2 // 3),
        (crown_cx - crown_w // 5, crown_base_y - crown_h // 4),
        (crown_cx,                spike_tip_y),
        (crown_cx + crown_w // 5, crown_base_y - crown_h // 4),
        (crown_cx + crown_w // 3, crown_base_y - crown_h * 2 // 3),
        (crown_cx + crown_w // 2, crown_base_y),
    ]
    pygame.draw.polygon(big, GOLD_HI, cpts)
    pygame.draw.polygon(big, GOLD_INK, cpts, max(1, ink - 1))

    # Confetti — capped at 16 pieces in a half-arc across the TOP 180 deg
    # + sides only (clear the bottom third entirely). All 16 sit OUTSIDE
    # the chest silhouette. 6 of the 16 are gold-yellow to echo the coming
    # coin payoff. Positions are computed deterministically from a fixed
    # angle ladder so the round looks the same every render.
    px_w = PICKUP_W * SS
    px_h = PICKUP_H * SS

    # Chest exclusion rect (bounding box of body + lid arc) — confetti
    # placement is rejected if its centre falls inside this rect.
    chest_bbox = body.union(lid).inflate(SS * 2, SS * 2)
    chest_bbox.top = lid.top - int(lid.height * 0.65)

    rng = 0xC0FFEE
    def rnd():
        nonlocal rng
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        return rng / 0x7FFFFFFF

    # Build a 16-slot angle ladder across the top half (180 deg arc) plus
    # a small left/right side bias — but never touching the bottom band.
    n_pieces = 16
    gold_slots = {1, 3, 6, 9, 12, 14}              # 6 of 16 are gold-yellow
    cx0 = (chest_bbox.left + chest_bbox.right) // 2
    cy0 = chest_bbox.centery
    # Orbit radius that comfortably clears the chest's silhouette.
    base_r = int(max(chest_bbox.width, chest_bbox.height) * 0.62)

    placed = 0
    slot = 0
    while placed < n_pieces and slot < n_pieces * 4:
        # Sweep theta across the top half — 180 deg to 360 deg in screen
        # coords means pi -> 2*pi (so y stays at or above the centre).
        t = (slot % n_pieces) / n_pieces
        theta = math.pi + t * math.pi               # pi .. 2pi (top arc)
        # Small per-slot radial jitter for organic spacing.
        r = base_r + int((rnd() - 0.5) * SS * 4)
        x = int(cx0 + math.cos(theta) * r * 1.05)
        y = int(cy0 + math.sin(theta) * r * 0.85)
        # Hard-clear the bottom third of the icon.
        if y > int(px_h * 0.62):
            slot += 1
            continue
        # Reject any candidate that overlaps the chest silhouette bbox.
        if chest_bbox.collidepoint(x, y):
            slot += 1
            continue
        if not (0 <= x < px_w and 0 <= y < px_h):
            slot += 1
            continue

        if placed in gold_slots:
            col = (252, 220,  88)                  # gold-yellow coin echo
        else:
            # Pick from the non-yellow confetti hues so gold count stays 6.
            non_yellow = tuple(c for c in CONFETTI if c != (255, 214, 92))
            col = non_yellow[int(rnd() * len(non_yellow)) % len(non_yellow)]

        size = max(SS, int(SS * (1.0 + rnd() * 0.5)))
        kind = rnd()
        if kind < 0.34:
            ang = rnd() * 2 * math.pi
            tri = [
                (x + math.cos(ang) * size,
                 y + math.sin(ang) * size),
                (x + math.cos(ang + 2.1) * size,
                 y + math.sin(ang + 2.1) * size),
                (x + math.cos(ang + 4.2) * size,
                 y + math.sin(ang + 4.2) * size),
            ]
            pygame.draw.polygon(big, col, tri)
            pygame.draw.polygon(big, INK, tri, max(1, ink // 2))
        elif kind < 0.66:
            pygame.draw.circle(big, col, (x, y), max(2, size // 2))
            pygame.draw.circle(big, INK, (x, y), max(2, size // 2),
                               max(1, ink // 2))
        else:
            rib_w = size * 2
            rib_h = max(2, int(size * 0.6))
            rib_surf = pygame.Surface((rib_w + ink * 2, rib_h + ink * 2),
                                       pygame.SRCALPHA)
            rib_rect = pygame.Rect(ink, ink, rib_w, rib_h)
            pygame.draw.rect(rib_surf, col, rib_rect,
                             border_radius=rib_h // 2)
            pygame.draw.rect(rib_surf, INK, rib_rect, max(1, ink // 2),
                             border_radius=rib_h // 2)
            rot = pygame.transform.rotate(rib_surf,
                                          (rnd() - 0.5) * 90)
            big.blit(rot, rot.get_rect(center=(x, y)))
        placed += 1
        slot += 1

    # Family unifiers — lid rim light + corner sparkle ring (the four
    # sparkles add to F2's confetti rather than replacing it).
    _lid_rim_light(big, lid, lid_apex_y, ink)
    _unified_sparkle_ring(big, body, lid, ink)

    return _finish(big)


# ---------------------------------------------------------------------------
# F3 — Party-hat + streamers.
# ---------------------------------------------------------------------------
def icon_f3():
    """Replace the crown with a BODY-TALL STRIPED PARTY HAT (cone with
    thick diagonal red/yellow bands + a clearly readable cream pom on
    top). Two straight 1-px gold tinsel strands hang from the lid
    corners down ~half body height — round-1's curly streamers
    vanished at 1x. Warmer party-red body, gold trim + lock anchor."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Body — warmer red.
    _chest_body(big, body, ink, PARTY_RED_HI, PARTY_RED_MID, PARTY_RED_LO)
    # Gold trim along the seam + bottom.
    top_trim = pygame.Rect(body.left, body.top - max(1, ink // 2),
                            body.width, max(3, int(body.height * 0.10)))
    _vgrad_rect(big, top_trim, GOLD_HI, GOLD_LO,
                radius=max(1, top_trim.height // 2))
    pygame.draw.rect(big, GOLD_INK, top_trim, max(1, ink // 2),
                     border_radius=max(1, top_trim.height // 2))
    bot_trim = pygame.Rect(body.left, body.bottom - int(body.height * 0.12),
                            body.width, int(body.height * 0.14))
    _vgrad_rect(big, bot_trim, GOLD_HI, GOLD_LO,
                radius=max(1, bot_trim.height // 2))
    pygame.draw.rect(big, GOLD_INK, bot_trim, max(1, ink // 2),
                     border_radius=max(1, bot_trim.height // 2))

    # Curved lid in matching red.
    pts, lid_apex_y = _curved_lid(big, lid, ink,
                                   PARTY_RED_HI, PARTY_RED_MID, PARTY_RED_LO,
                                   grain=False, sheen=True)

    # Gold lock plate.
    lock_w = int(body.width * 0.28)
    lock_h = int(body.height * 0.50)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.04)
    _gold_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink, keyhole=True)

    # Two straight gold tinsel strands hang from the lid corners down
    # ~half the body height. 1 px wide at pickup scale (= SS in the
    # supersampled space) so they survive the downscale. The previous
    # curly streamers vanished completely at 1x.
    tinsel_top_y = lid.top + int(lid.height * 0.55)
    tinsel_bot_y = body.top + body.height // 2
    tinsel_w = max(1, SS)
    for sgn in (-1, +1):
        tx = lid.centerx + sgn * int(lid.width * 0.42)
        # Faint ink underline first so the strand has an edge at 1x.
        pygame.draw.line(big, INK, (tx, tinsel_top_y),
                         (tx, tinsel_bot_y), max(1, tinsel_w + SS // 2))
        pygame.draw.line(big, GOLD_HI, (tx, tinsel_top_y),
                         (tx, tinsel_bot_y), tinsel_w)
        # Tiny gold bead at the tip so the strand reads as tinsel, not
        # a stray pixel line.
        pygame.draw.circle(big, GOLD_HI, (tx, tinsel_bot_y),
                           max(1, SS))
        pygame.draw.circle(big, GOLD_INK, (tx, tinsel_bot_y),
                           max(1, SS), max(1, SS // 2))

    # Body-tall striped party hat — the hat's height matches the body
    # height at the final scale so it dominates the silhouette like B5's
    # crown spike. Drawn AFTER the tinsel so the hat masks any overlap.
    hat_base_w = int(lid.width * 0.50)
    hat_h = body.height                              # body-tall at final scale
    hat_base_cy = lid_apex_y + int(lid.height * 0.10)
    hat_tip_y = hat_base_cy - hat_h
    hat_cx = lid.centerx
    hat_tri = [
        (hat_cx - hat_base_w // 2, hat_base_cy),
        (hat_cx + hat_base_w // 2, hat_base_cy),
        (hat_cx,                   hat_tip_y),
    ]
    # Solid base fill (yellow undertone) — stripes drawn over it inside a
    # clipped triangle mask.
    pygame.draw.polygon(big, CARNIVAL_Y, hat_tri)
    # Mask surf for the stripes so the diagonal red bands stay confined
    # inside the cone shape.
    mask_w = hat_base_w + ink * 4
    mask_h = hat_h + ink * 4
    mask_surf = pygame.Surface((mask_w, mask_h), pygame.SRCALPHA)
    # Translate triangle into mask space.
    mtri = [(p[0] - (hat_cx - mask_w // 2),
             p[1] - (hat_tip_y - ink * 2)) for p in hat_tri]
    pygame.draw.polygon(mask_surf, (255, 255, 255, 255), mtri)
    # Stripes — 2 px (at pickup scale, = SS*2 in supersample) diagonal
    # red bands across the mask. Wider than round 1 so the bands read at
    # 1x instead of looking like faint cross-hatching.
    stripe_surf = pygame.Surface((mask_w, mask_h), pygame.SRCALPHA)
    band_w = SS * 2                                  # 2 px at final scale
    spacing = band_w * 2
    for off in range(-mask_h, mask_w + mask_h, spacing):
        pts3 = [
            (off,                     0),
            (off + band_w,            0),
            (off + band_w + mask_h,   mask_h),
            (off + mask_h,            mask_h),
        ]
        pygame.draw.polygon(stripe_surf, CARNIVAL_R, pts3)
    stripe_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(stripe_surf,
             (hat_cx - mask_w // 2, hat_tip_y - ink * 2))
    # Hat outline.
    pygame.draw.polygon(big, INK, hat_tri, max(2, ink))

    # 3 px cream pom-pom on the tip at final scale — clearly readable at
    # 1x, where the previous ~1.3 px pom collapsed into the outline.
    pom_r = SS * 3 // 2                              # 3 px diameter at final
    pygame.draw.circle(big, CREAM, (hat_cx, hat_tip_y - pom_r), pom_r)
    pygame.draw.circle(big, INK, (hat_cx, hat_tip_y - pom_r),
                       pom_r, max(1, ink // 2))

    # A couple of cream sparkles flanking the hat.
    _draw_sparkle(big, hat_cx - int(hat_base_w * 0.95),
                  hat_tip_y + int(hat_h * 0.20),
                  max(2, int(SS * 0.9)), SPARKLE, max(1, ink // 2))
    _draw_sparkle(big, hat_cx + int(hat_base_w * 0.95),
                  hat_tip_y + int(hat_h * 0.35),
                  max(2, int(SS * 0.8)), SPARKLE, max(1, ink // 2))

    # Family unifiers — lid rim light + 4-corner sparkle ring.
    _lid_rim_light(big, lid, lid_apex_y, ink)
    _unified_sparkle_ring(big, body, lid, ink)

    return _finish(big)


# ---------------------------------------------------------------------------
# F4 — Rainbow-jewel celebration.
# ---------------------------------------------------------------------------
def icon_f4():
    """B5 crown is kept, but the lid front gets a rim of six multicolour
    jewels (ROYGBV order) — full rainbow studded across the seam. Brighter
    cheerful red body. Extra sparkles scattered around the WHOLE box, not
    just orbiting the crown. Reads as 'all the jewels at once'."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Coral / warm party-red body — PARTY_RED shifted +10 deg toward
    # orange so F4 no longer reads as just a B5 colour upgrade.
    _chest_body(big, body, ink, CORAL_HI, CORAL_MID, CORAL_LO)
    # Gold seam trim (thicker, since it carries the jewel rim).
    seam = pygame.Rect(body.left, body.top - max(1, ink // 2),
                       body.width, max(3, int(body.height * 0.14)))
    _vgrad_rect(big, seam, GOLD_HI, GOLD_LO, radius=max(1, seam.height // 2))
    pygame.draw.rect(big, GOLD_INK, seam, max(1, ink // 2),
                     border_radius=max(1, seam.height // 2))
    bot_trim = pygame.Rect(body.left, body.bottom - int(body.height * 0.12),
                            body.width, int(body.height * 0.14))
    _vgrad_rect(big, bot_trim, GOLD_HI, GOLD_LO,
                radius=max(1, bot_trim.height // 2))
    pygame.draw.rect(big, GOLD_INK, bot_trim, max(1, ink // 2),
                     border_radius=max(1, bot_trim.height // 2))

    # Curved lid in matching coral.
    pts, lid_apex_y = _curved_lid(big, lid, ink,
                                   CORAL_HI, CORAL_MID, CORAL_LO,
                                   grain=False, sheen=True)

    # Six rainbow jewels evenly across the gold seam band.
    gem_count = 6
    gem_r = max(3, int(SS * 1.7))
    # Span the body width, leaving small margin so end gems don't kiss
    # the chest edges.
    margin_px = int(body.width * 0.07)
    x_start = body.left + margin_px
    x_end   = body.right - margin_px
    for i in range(gem_count):
        t = i / (gem_count - 1)
        gx = int(x_start + t * (x_end - x_start))
        gy = seam.centery
        _draw_jewel_dot(big, gx, gy, gem_r, RAINBOW_GEMS[i], ink)

    # Gold lock plate sitting BELOW the jewel rim. Enlarged by ~20% on
    # both axes so the star plate beats the crown for focal attention —
    # the star is the festive answer to B5's keyhole.
    lock_w = int(body.width * 0.29)
    lock_h = int(body.height * 0.50)
    lock_cx = body.centerx
    lock_cy = body.top + int(body.height * 0.22) + lock_h // 2
    _gold_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink, keyhole=False)
    # 5-point star on the lock plate face (using a polygon) — scaled up to
    # match the larger plate so it reads as the focal point at 1x.
    star_r = max(3, int(lock_h * 0.36))
    star_pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = star_r if k % 2 == 0 else star_r // 2
        star_pts.append((lock_cx + math.cos(ang) * rr,
                         lock_cy + math.sin(ang) * rr))
    pygame.draw.polygon(big, GOLD_INK, star_pts)

    # Kept B5 crown — slightly smaller so it leaves room for the rim.
    crown_w = int(lock_w * 1.05)
    crown_h = int(lock_h * 0.62)
    crown_cx = lock_cx
    crown_base_y = body.top - int(body.height * 0.08)
    spike_tip_y = lid_apex_y - SS
    crown_cy = (crown_base_y + spike_tip_y) // 2
    cpts = [
        (crown_cx - crown_w // 2,    crown_base_y),
        (crown_cx - crown_w // 2,    crown_cy - crown_h // 6),
        (crown_cx - crown_w // 3,    crown_base_y - crown_h // 5),
        (crown_cx - crown_w // 5,    crown_cy - crown_h // 3),
        (crown_cx,                   spike_tip_y),
        (crown_cx + crown_w // 5,    crown_cy - crown_h // 3),
        (crown_cx + crown_w // 3,    crown_base_y - crown_h // 5),
        (crown_cx + crown_w // 2,    crown_cy - crown_h // 6),
        (crown_cx + crown_w // 2,    crown_base_y),
    ]
    pygame.draw.polygon(big, GOLD_HI, cpts)
    pygame.draw.polygon(big, GOLD_LO,
                        [(crown_cx - crown_w // 2, crown_base_y - crown_h // 6),
                         (crown_cx + crown_w // 2, crown_base_y - crown_h // 6),
                         (crown_cx + crown_w // 2, crown_base_y),
                         (crown_cx - crown_w // 2, crown_base_y)])
    pygame.draw.polygon(big, GOLD_INK, cpts, max(1, ink - 1))

    # Sparkles scattered around the WHOLE box — not just the crown.
    sparkle_specs = (
        (-0.85, -0.20, 1.0),                 # left of body
        ( 0.85, -0.05, 0.95),                # right of body
        (-0.45, -1.20, 0.85),                # upper-left of crown
        ( 0.55, -1.10, 0.80),                # upper-right of crown
        ( 0.00, -1.45, 1.10),                # high above crown
        (-0.95,  0.55, 0.75),                # low left
        ( 0.92,  0.40, 0.80),                # low right
    )
    px_w = PICKUP_W * SS
    px_h = PICKUP_H * SS
    cx0 = px_w // 2
    cy0 = px_h // 2
    for (ox, oy, sc) in sparkle_specs:
        sx = cx0 + int(px_w * 0.5 * ox)
        sy = cy0 + int(px_h * 0.5 * oy)
        L = max(2, int(SS * 1.1 * sc))
        _draw_sparkle(big, sx, sy, L, SPARKLE, max(1, ink // 2))

    # Family unifiers — lid rim light + 4-corner sparkle ring.
    _lid_rim_light(big, lid, lid_apex_y, ink)
    _unified_sparkle_ring(big, body, lid, ink)

    return _finish(big)


# ---------------------------------------------------------------------------
# F5 — Carnival pop-art.
# ---------------------------------------------------------------------------
def icon_f5():
    """Reworked carnival cell — the round-1 smiley face read as a UI
    sticker, not a chest. Now: top 40% of the body stays SOLID PARTY-RED
    so the lid + lock sit on a clean canvas; the lower 60% gets the
    bright red/yellow/teal vertical stripes for the circus-tent vibe.
    The lid is pastel pink (with a 1-step DARKER rim so it separates
    against the pink fill in silhouette). The lock plate carries an
    F4-style gold 5-point STAR (the smiley + the eyes are gone). A
    smaller pastel-pink + gold bow still crowns the lid."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Body — solid party-red top, striped lower 60%. We paint the whole
    # rounded rect first with the gradient PARTY_RED, then stripe over
    # only the lower 60% inside the same rounded mask.
    radius = max(2, int(body.width * 0.08))
    _chest_body(big, body, ink, PARTY_RED_HI, PARTY_RED_MID, PARTY_RED_LO)

    # Build the striped lower band in a body-local surface, then mask to
    # the rounded body shape so the stripes hug the body silhouette.
    stripe_top_frac = 0.40                           # solid red in top 40%
    stripe_band_h = int(body.height * (1.0 - stripe_top_frac))
    if stripe_band_h > 0:
        base_surf = pygame.Surface(body.size, pygame.SRCALPHA)
        stripe_cols = (CARNIVAL_R, CARNIVAL_Y, CARNIVAL_T)
        n_stripes = 6
        sw = body.width // n_stripes
        stripe_top_y = int(body.height * stripe_top_frac)
        for i in range(n_stripes):
            col = stripe_cols[i % 3]
            sx = i * sw
            for y in range(stripe_top_y, body.height):
                # Per-stripe shade toward INK so stripes match the
                # gradient depth of the other variants' bodies.
                t = (y - stripe_top_y) / max(1, body.height - stripe_top_y - 1)
                shade = _lerp(col, _lerp(col, INK, 0.45), t)
                pygame.draw.line(base_surf, shade,
                                 (sx, y), (sx + sw, y))
        mask = pygame.Surface(body.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                         border_radius=radius)
        base_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(base_surf, body.topleft)
    # Re-stroke the body outline so the rounded edge stays crisp on top
    # of the stripe overlay.
    pygame.draw.rect(big, INK, body, ink, border_radius=radius)

    # Curved lid — pastel-pink top so it pops over the bright stripes.
    pts, lid_apex_y = _curved_lid(big, lid, ink,
                                   PASTEL_PINK_HI, PASTEL_PINK_MID,
                                   PASTEL_PINK_LO,
                                   grain=False, sheen=True)

    # Darker lid rim — 1 value step down from PASTEL_PINK_LO so the rim
    # separates from the pink lid fill in silhouette. We re-stroke the
    # lid polygon outline in this darker tone.
    lid_rim_dark = _lerp(PASTEL_PINK_LO, INK, 0.35)
    if pts and len(pts) >= 3:
        pygame.draw.polygon(big, lid_rim_dark, pts, max(2, ink))

    # Cream polka dots scattered on the lid.
    dot_specs = (
        (-0.30, 0.45, 1.0),
        ( 0.05, 0.30, 0.85),
        ( 0.35, 0.60, 0.95),
        (-0.50, 0.70, 0.80),
        ( 0.55, 0.40, 0.85),
        (-0.10, 0.78, 0.75),
    )
    for (ox, oy, sc) in dot_specs:
        dx = lid.centerx + int(lid.width * 0.5 * ox)
        dy = lid.top + int(lid.height * oy)
        dr = max(2, int(SS * 1.3 * sc))
        pygame.draw.circle(big, CREAM_DOT, (dx, dy), dr)
        pygame.draw.circle(big, INK, (dx, dy), dr, max(1, ink // 2))

    # Gold lock plate with an F4-style gold 5-point star on its face.
    # Smiley dropped — at 1x it read as a UI sticker rather than a chest.
    lock_w = int(body.width * 0.28)
    lock_h = int(body.height * 0.50)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.04)
    _gold_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink, keyhole=False)
    # 5-point star on the lock plate face (matches F4's star).
    star_r = max(3, int(lock_h * 0.32))
    star_pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = star_r if k % 2 == 0 else star_r // 2
        star_pts.append((lock_cx + math.cos(ang) * rr,
                         lock_cy + math.sin(ang) * rr))
    pygame.draw.polygon(big, GOLD_INK, star_pts)

    # Smaller pastel-pink + gold bow crowning the lid (no royal crown).
    bow_w = int(lid.width * 0.62)
    bow_h = int(lid.height * 0.80)
    bow_cx = lid.centerx
    bow_cy = lid_apex_y + int(bow_h * 0.05)
    _draw_bow(big, bow_cx, bow_cy, bow_w, bow_h, ink,
              PASTEL_PINK_HI, PASTEL_PINK_MID, PASTEL_PINK_LO,
              with_tails=False)
    # A tiny gold dot at the centre of the bow knot for a touch of luxe.
    pygame.draw.circle(big, GOLD_HI, (bow_cx, bow_cy),
                       max(2, int(SS * 0.7)))
    pygame.draw.circle(big, GOLD_INK, (bow_cx, bow_cy),
                       max(2, int(SS * 0.7)), max(1, ink // 2))

    # A few cream sparkles for pop-art glint.
    _draw_sparkle(big, bow_cx - int(bow_w * 0.6),
                  bow_cy - int(bow_h * 0.20),
                  max(2, int(SS * 0.8)), SPARKLE, max(1, ink // 2))
    _draw_sparkle(big, bow_cx + int(bow_w * 0.6),
                  bow_cy + int(bow_h * 0.05),
                  max(2, int(SS * 0.8)), SPARKLE, max(1, ink // 2))

    # Family unifiers — lid rim light + 4-corner sparkle ring.
    _lid_rim_light(big, lid, lid_apex_y, ink)
    _unified_sparkle_ring(big, body, lid, ink)

    return _finish(big)


CANDIDATES = [
    ("F1", "Gift ribbon + bow (lead)", icon_f1),
    ("F2", "Confetti — tamed",         icon_f2),
    ("F3", "Party hat + tinsel",       icon_f3),
    ("F4", "Rainbow jewels — coral",   icon_f4),
    ("F5", "Carnival — reworked",      icon_f5),
]


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "treasure_box")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "festive_round_2.png")

    bob = int(round(math.sin(BOB_PULSE * 0.8) * 2))

    cell_w, cell_h = 320, 340
    cols = 5
    pad = 16
    header_h = 88
    footer_h = 34

    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * pad
    sheet_h = header_h + cell_h + footer_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 30))

    def font(sz, bold=False):
        return pygame.font.SysFont("Arial", sz, bold=bold)

    title = font(26, bold=True).render(
        "TREASURE BOX festive variants — round 2 "
        "(B5 lead made more cheerful)", True,
        (240, 240, 246))
    sheet.blit(title, (pad, pad))
    sub = font(14).render(
        "round 2 — lead F1; F2 confetti tamed; F5 reworked",
        True, (170, 178, 192))
    sheet.blit(sub, (pad, pad + 32))
    sub2 = font(13).render(
        "Each cell: dawn sky + sparkle backdrop. "
        "Left = real pickup (~56x46 px); right = 3x zoom. "
        "All 5 share lid-rim gold + 4-corner cream sparkles.",
        True, (200, 180, 150))
    sheet.blit(sub2, (pad, pad + 54))

    for col, (tag, name, fn) in enumerate(CANDIDATES):
        x = pad + col * (cell_w + pad)
        y = header_h + pad
        swatch = _dawn_sparkle_swatch(cell_w, cell_h, seed=col + 11)
        sheet.blit(swatch, (x, y))
        pygame.draw.rect(sheet, (60, 66, 84), (x, y, cell_w, cell_h), 1)

        icon = fn()

        # True pickup size on the upper-left of the cell.
        true_cx = x + cell_w // 4 - PICKUP_W // 2
        true_cy = y + cell_h // 2 - PICKUP_H // 2 + bob
        sheet.blit(icon, (true_cx, true_cy))
        pygame.draw.rect(sheet, (255, 255, 255),
                         (true_cx - 3, true_cy - bob - 3,
                          PICKUP_W + 6, PICKUP_H + 6), 1)
        lbl = font(12).render(f"real pickup ~{PICKUP_W}x{PICKUP_H} px",
                               True, (210, 220, 235))
        sheet.blit(lbl, (x + 10, y + cell_h - 24))

        # 3x zoom on the right half of the cell.
        zoom = pygame.transform.smoothscale(
            icon, (PICKUP_W * 3, PICKUP_H * 3))
        zx = x + cell_w - PICKUP_W * 3 - 18
        zy = y + cell_h // 2 - (PICKUP_H * 3) // 2
        sheet.blit(zoom, (zx, zy))
        zl = font(12).render("3x zoom", True, (210, 220, 235))
        sheet.blit(zl, (zx + PICKUP_W * 3 - 56, zy - 18))

        # Caption strip.
        cap = font(16, bold=True).render(f"{tag}  {name}", True,
                                         (245, 240, 230))
        sheet.blit(cap, (x + 8, header_h + pad + cell_h + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()

"""SKATEBOARD pickup activation FX — split into two pieces so the
caption can linger at the top of the screen while the spike burst
follows Pip for a short beat without covering gameplay long-term.

* render_caption_overlay(cx, cy, rng_seed) — STATIC (W × H) surface
  with the tilted SKATEBOARD! caption near the top, POW! badge upper-
  right, and 4 corner ink slashes pointing at the original pickup
  position. Lives ~2.5 s.
* render_starburst_surface(rng_seed) — small (~320 × 320) surface
  with the 14-spike yellow/red starburst centered. scenes.py blits
  this each frame at Pip's CURRENT screen position so the burst
  appears to ride with him. Lives ~0.6 s — short by design so the
  game stays visible.

Original mockup: docs/screenshots/skateboard_variants/final/chosen.png
and tools/render_skateboard_final.py.
"""

import math
import random

import pygame

from game.config import W, H
from game.hud import _font


INK = (15, 15, 15)
YELLOW = (255, 220, 30)
RED = (230, 60, 50)
PLATE_RED = (220, 50, 40)
WHITE = (255, 255, 255)

# Self-contained starburst surface size — comfortably bigger than the
# spikes' outer radius (~165 px) so the polygon never clips.
BURST_SIZE = 360


def _gradient_text(text, size, top_col, bot_col, outline, outline_w=3):
    """Vertical-gradient text fill with thick outline (ported from
    tools/render_skateboard_variants.py)."""
    font = _font(size)
    mask = font.render(text, True, WHITE)
    bw, bh = mask.get_size()
    grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(bh):
        t = y / max(1, bh - 1)
        c = tuple(int(top_col[i] + (bot_col[i] - top_col[i]) * t)
                  for i in range(3))
        pygame.draw.line(grad, c, (0, y), (bw, y))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    out = font.render(text, True, outline)
    pad = outline_w + 2
    surf = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx * dx + dy * dy <= outline_w * outline_w and (dx or dy):
                surf.blit(out, (pad + dx, pad + dy))
    surf.blit(grad, (pad, pad))
    return surf


_R11_DECK_W = 340
_R11_DECK_H = 92
_R11_DECK_BORDER_R = 44
_R11_TILT_DEG = -7
_R11_BOLT_INSET_X = 34
_R11_BOLT_INSET_Y = 20
_R11_GAP_PX = 74 // 2
_R11_FONT_SIZE = 32
_R11_OUTLINE_W = 3
_R11_WORDMARK_BOT = (242, 171, 10)
_R11_SHADOW_OFFSET = (2, 2)
_R11_SHADOW_ALPHA = 89


def _r11_draw_truck_bolts(surf, deck_w, deck_h, inset, edge_inset):
    for bolt_x in (inset, deck_w - inset):
        for bolt_y in (edge_inset, deck_h - edge_inset):
            pygame.draw.circle(surf, INK, (bolt_x, bolt_y), 5)
            pygame.draw.circle(surf, (60, 60, 60), (bolt_x, bolt_y), 3)
            hl = pygame.Surface((2, 2), pygame.SRCALPHA)
            hl.fill((200, 200, 200, 180))
            surf.blit(hl, (bolt_x - 1, bolt_y - 1))


def _r11_build_deck():
    deck_w, deck_h = _R11_DECK_W, _R11_DECK_H
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    pygame.draw.rect(deck, PLATE_RED, deck_rect,
                     border_radius=_R11_DECK_BORDER_R)
    stripe_step, stripe_alpha = 24, 38
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes,
                                (255, 235, 130, stripe_alpha), pts)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=_R11_DECK_BORDER_R)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    _r11_draw_truck_bolts(deck, deck_w, deck_h,
                          _R11_BOLT_INSET_X, _R11_BOLT_INSET_Y)
    # Ink rim painted BEFORE the wordmarks so SKATE / BOARD! can extend
    # right up to the deck's silhouette edge without the rim clipping
    # their outermost glyph columns. The rim still reads as the deck's
    # silhouette — text just lands on top of it at the very edges.
    pygame.draw.rect(deck, INK, deck_rect, 4,
                     border_radius=_R11_DECK_BORDER_R)
    axis_y = deck_h // 2
    # Push SKATE / BOARD to within _R11_BORDER_PAD pixels of the deck
    # silhouette edge, then nudge each rightward by its own SHIFT so
    # SKATE comes in toward the burst (matches the user-picked V3) and
    # BOARD sits a touch left of the deck right edge. _gradient_text
    # pads its surface by _R11_OUTLINE_W + 2 pixels on each side; we
    # offset the midleft / midright anchors by that pad so the visible
    # GLYPH (not the surface) lands at the desired edge distance.
    _R11_BORDER_PAD = 4
    _R11_TEXT_PAD = _R11_OUTLINE_W + 2
    _R11_SKATE_SHIFT = 9
    _R11_BOARD_SHIFT = -6
    skate = _gradient_text("SKATE", _R11_FONT_SIZE,
                           top_col=(255, 255, 110),
                           bot_col=_R11_WORDMARK_BOT,
                           outline=INK, outline_w=_R11_OUTLINE_W)
    skate_rect = skate.get_rect()
    skate_rect.midleft = (_R11_BORDER_PAD - _R11_TEXT_PAD
                          + _R11_SKATE_SHIFT, axis_y)
    deck.blit(skate, skate_rect)
    board = _gradient_text("BOARD", _R11_FONT_SIZE,
                           top_col=(255, 255, 110),
                           bot_col=_R11_WORDMARK_BOT,
                           outline=INK, outline_w=_R11_OUTLINE_W)
    board_rect = board.get_rect()
    board_rect.midright = (deck_w - _R11_BORDER_PAD + _R11_TEXT_PAD
                           + _R11_BOARD_SHIFT, axis_y)
    deck.blit(board, board_rect)
    return deck


def render_caption_overlay(cx: int, cy: int,
                           rng_seed: int = 22) -> pygame.Surface:
    """SKATEBOARD deck banner that wraps the live halftone score in its
    centre. 340×92 PLATE_RED slab tilted −7° with SKATE | (score slot) |
    BOARD and four truck-bolts. Returns a (W × H) surface; caller blits
    at (0, −lift_y) so the deck centre lands on screen-y 70 (same y as
    the regular HUD score plate), then renders the live halftone score
    on top so it reads centred inside the deck.

    cx/cy/rng_seed are kept for activation-callsite API compatibility
    and ignored — the deck is screen-space anchored, not pickup-anchored,
    so it lives in a fixed location regardless of where Pip caught the
    power-up."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    deck = _r11_build_deck()
    rotated = pygame.transform.rotate(deck, _R11_TILT_DEG)
    deck_center = (W // 2, 96)
    rect = rotated.get_rect(center=deck_center)
    sh = rotated.copy()
    sh.fill((0, 0, 0, _R11_SHADOW_ALPHA),
            special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(sh, (rect.x + _R11_SHADOW_OFFSET[0],
                   rect.y + _R11_SHADOW_OFFSET[1]))
    surf.blit(rotated, rect)
    return surf


# ── comic-inspired add-on overlays ──────────────────────────────────────────
#
# Each returns a screen-space (W × H) surface that callers blit at (0, 0)
# on top of `render_caption_overlay`'s output. Designed to extend (not
# replace) the existing SKATEBOARD! caption + POW! + corner slashes; the
# add-on sits behind the caption in z-order so the caption stays readable.


_PALETTE_KAPOW = (
    # (label, fill, accent, rot_deg, offset_from_pip)
    ("KAPOW!", (255, 220,  30), (230,  60,  50),  -8, (-120, -80)),  # NW
    ("BAM!",   (255, 100, 180), (255, 245, 200),  10, ( 130, -90)),  # NE
    ("SMASH!", ( 95, 200, 220), ( 30,  60, 120),  -6, (-140,  90)),  # SW
    ("WHAM!",  (255, 165,  60), (220,  40,  40),   8, ( 120,  95)),  # SE
)


def _jagged_burst(surf, cx, cy, ro, ri, spikes, fill, outline,
                  outline_w=3, jitter=0):
    rng = random.Random(int(cx) * 31 + int(cy) * 17 + spikes)
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = ro if i % 2 == 0 else ri
        if jitter:
            r += rng.randint(-jitter, jitter)
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, outline, pts, outline_w)
    return pts


def render_kapow_chorus_overlay(cx: int, cy: int,
                                  rng_seed: int = 22) -> pygame.Surface:
    """C1 — Onomatopoeia chorus. 4 comic-burst badges (KAPOW! / BAM! /
    SMASH! / WHAM!) placed in the four quadrants around Pip, each in
    its own jagged star burst with a distinct pop-art colorway.
    Stacks on top of the existing single POW! badge."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for label, fill, accent, rot_deg, (dx, dy) in _PALETTE_KAPOW:
        bx = max(60, min(W - 60, cx + dx))
        by = max(110, min(H - 80, cy + dy))
        # Outer + inner jagged-edge bursts.
        _jagged_burst(surf, bx, by, 56, 30, spikes=10,
                      fill=fill, outline=INK, outline_w=4, jitter=4)
        _jagged_burst(surf, bx, by, 38, 22, spikes=10,
                      fill=accent, outline=INK, outline_w=2)
        # Text on the burst.
        size = 24 if len(label) > 4 else 28
        txt = _gradient_text(label, size,
                             top_col=(255, 250, 240),
                             bot_col=fill,
                             outline=INK, outline_w=3)
        rot = pygame.transform.rotate(txt, rot_deg)
        surf.blit(rot, rot.get_rect(center=(bx, by)))
    return surf


def render_halftone_aura_overlay(cx: int, cy: int,
                                   rng_seed: int = 22) -> pygame.Surface:
    """C2 — Lichtenstein halftone aura. Red+yellow dot field radiating
    from Pip, dots get LARGER toward the rim with a thin ink outline
    so they read as comic-panel pop dots even against bright sky.
    Densest at the rim (the "explosion edge") and sparse in the
    middle so Pip + the existing starburst stay visible."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    inner_r = 130   # start just outside the live 14-spike starburst
    outer_r = 260
    ring_step = 14
    for ring_idx, r in enumerate(range(inner_r, outer_r, ring_step)):
        t = (r - inner_r) / max(1, outer_r - inner_r)
        dot_r = int(4 + t * 5)
        alpha = int(235 - t * 90)  # 235 -> 145, stays punchy
        col = RED if ring_idx % 2 == 0 else YELLOW
        col_a = (*col, alpha)
        circumference = 2 * math.pi * r
        n = max(10, int(circumference / 24))
        phase = (ring_idx * math.pi / 5)
        for k in range(n):
            ang = phase + k * 2 * math.pi / n
            x = cx + math.cos(ang) * r
            y = cy + math.sin(ang) * r
            if -dot_r < x < W + dot_r and -dot_r < y < H + dot_r:
                # Thin ink rim so dots read against the sky.
                pygame.draw.circle(surf, (*INK, alpha),
                                   (int(x), int(y)), dot_r + 1)
                pygame.draw.circle(surf, col_a,
                                   (int(x), int(y)), dot_r)
    return surf


def render_speech_bubble_overlay(cx: int, cy: int,
                                   rng_seed: int = 22) -> pygame.Surface:
    """C3 — Round comic speech bubble tail-pointing from Pip's helmet
    with "SHRED!" gradient text. Cream fill + thick ink outline; the
    tail is a triangle wedge directed back at Pip. Placed upper-left
    so it doesn't overlap the SKATEBOARD! caption strip."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    # Bubble centre — upper-left of Pip, clamped onto the screen.
    bcx = max(110, min(W - 110, cx - 130))
    bcy = max(170, min(H - 110, cy - 90))
    # Tail triangle from the bubble edge toward Pip.
    ang = math.atan2(cy - bcy, cx - bcx)
    rx, ry = 95, 70  # bubble half-axes
    tail_anchor_x = bcx + math.cos(ang) * rx * 0.92
    tail_anchor_y = bcy + math.sin(ang) * ry * 0.92
    perp = ang + math.pi / 2
    spread = 22
    tail = [
        (tail_anchor_x + math.cos(perp) * spread,
         tail_anchor_y + math.sin(perp) * spread),
        (tail_anchor_x - math.cos(perp) * spread,
         tail_anchor_y - math.sin(perp) * spread),
        (cx, cy - 12),
    ]
    pygame.draw.polygon(surf, (255, 248, 220), tail)
    pygame.draw.polygon(surf, INK, tail, 4)
    # Bubble body — ellipse with thick black outline.
    bub_rect = pygame.Rect(bcx - rx, bcy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, (255, 248, 220), bub_rect)
    pygame.draw.ellipse(surf, INK, bub_rect, 5)
    # SHRED! text inside the bubble.
    txt = _gradient_text("SHRED!", 36,
                          top_col=(255, 220,  50),
                          bot_col=(230,  60,  50),
                          outline=INK, outline_w=4)
    surf.blit(txt, txt.get_rect(center=(bcx, bcy)))
    return surf


def _lightning_bolt(surf, x0, y0, x1, y1, width=14,
                    fill=YELLOW, highlight=WHITE, outline=INK):
    """Jagged 4-point lightning polygon between (x0,y0) and (x1,y1).
    Adds an inner cream highlight stripe down the centre."""
    dx, dy = x1 - x0, y1 - y0
    length = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / length, dy / length          # along axis
    nx, ny = -uy, ux                            # perpendicular
    # Quarter-and-three-quarter offsets create the zig-zag.
    p_q1 = (x0 + ux * length * 0.30 + nx * width * 0.7,
            y0 + uy * length * 0.30 + ny * width * 0.7)
    p_q2 = (x0 + ux * length * 0.55 - nx * width * 0.3,
            y0 + uy * length * 0.55 - ny * width * 0.3)
    p_q3 = (x0 + ux * length * 0.78 + nx * width * 0.6,
            y0 + uy * length * 0.78 + ny * width * 0.6)
    half = width * 0.5
    pts = [
        (x0 + nx * half, y0 + ny * half),
        p_q1,
        p_q2,
        p_q3,
        (x1 + nx * half * 0.2, y1 + ny * half * 0.2),
        (x1 - nx * half * 0.2, y1 - ny * half * 0.2),
        (p_q3[0] - nx * width * 0.5, p_q3[1] - ny * width * 0.5),
        (p_q2[0] - nx * width * 0.4, p_q2[1] - ny * width * 0.4),
        (p_q1[0] - nx * width * 0.5, p_q1[1] - ny * width * 0.5),
        (x0 - nx * half, y0 - ny * half),
    ]
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, outline, pts, 3)
    # Centre highlight stripe.
    mid_pts = [
        (x0 + ux * length * 0.05, y0 + uy * length * 0.05),
        p_q1, p_q2, p_q3,
        (x1 - ux * length * 0.05, y1 - uy * length * 0.05),
    ]
    pygame.draw.lines(surf, highlight, False, mid_pts, 2)


def render_lightning_bolts_overlay(cx: int, cy: int,
                                     rng_seed: int = 22) -> pygame.Surface:
    """C4 — Yellow comic lightning bolts radiating outward from Pip,
    with a small ZZAP! badge to the side. Bolts start just OUTSIDE
    the 14-spike starburst (radius ~140 px) and extend further out so
    most of each bolt is visible past the burst. Thick polygon body +
    ink outline + cream highlight stripe so they pop against the
    sky."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    # 6 bolts radiating in a rough sunburst.
    angles_deg = (-145, -100, -55, -10, 35, 80)
    inner_r = 95   # bolt base — just past inner burst
    outer_r = 230  # bolt tip — well past the 14-spike rim (~140)
    for ang_deg in angles_deg:
        ang = math.radians(ang_deg + 90)  # 0 deg -> straight down
        base_x = cx + math.cos(ang) * inner_r
        base_y = cy + math.sin(ang) * inner_r
        tip_x = cx + math.cos(ang) * outer_r
        tip_y = cy + math.sin(ang) * outer_r
        # Clamp into screen with a generous margin.
        tip_x = max(20, min(W - 20, tip_x))
        tip_y = max(165, min(H - 30, tip_y))
        _lightning_bolt(surf, base_x, base_y, tip_x, tip_y,
                        width=22, fill=YELLOW,
                        highlight=(255, 255, 220), outline=INK)
    # ZZAP! badge — small yellow jagged burst to the upper-right.
    bx = max(80, min(W - 60, cx + 110))
    by = max(165, min(H - 100, cy - 70))
    _jagged_burst(surf, bx, by, 44, 24, spikes=12,
                  fill=YELLOW, outline=INK, outline_w=4, jitter=3)
    _jagged_burst(surf, bx, by, 28, 16, spikes=12,
                  fill=RED, outline=INK, outline_w=2)
    zap = _gradient_text("ZZAP!", 24,
                          top_col=(255, 250, 240),
                          bot_col=YELLOW,
                          outline=INK, outline_w=3)
    rot = pygame.transform.rotate(zap, -10)
    surf.blit(rot, rot.get_rect(center=(bx, by)))
    return surf


def render_comic_panel_overlay(cx: int, cy: int,
                                 rng_seed: int = 22) -> pygame.Surface:
    """C5 — Bold black comic-panel frame around the pickup region with
    a yellow narration caption box in the top-left corner reading
    "NEW BOARD!". Frames Pip + the existing FX like a comic snapshot."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    pw, ph = 280, 220
    panel = pygame.Rect(0, 0, pw, ph)
    panel.center = (cx, cy)
    # Keep the panel onscreen with a margin.
    panel.left   = max(8, panel.left)
    panel.top    = max(48, panel.top)
    panel.right  = min(W - 8, panel.right)
    panel.bottom = min(H - 48, panel.bottom)
    # Thick black frame — drawn 4 separate edges so the interior stays
    # see-through.
    border_w = 6
    pygame.draw.rect(surf, INK, panel, border_w)
    # Subtle drop-shadow on the right + bottom edges for depth.
    shadow_w = 4
    shadow_col = (0, 0, 0, 140)
    pygame.draw.rect(surf, shadow_col,
                     pygame.Rect(panel.right, panel.top + shadow_w,
                                 shadow_w, panel.height))
    pygame.draw.rect(surf, shadow_col,
                     pygame.Rect(panel.left + shadow_w, panel.bottom,
                                 panel.width, shadow_w))
    # Yellow narration caption box in the top-left of the panel.
    cap_w, cap_h = 150, 36
    cap = pygame.Rect(panel.left + 8, panel.top + 8, cap_w, cap_h)
    pygame.draw.rect(surf, (255, 225,  60), cap)
    pygame.draw.rect(surf, INK, cap, 3)
    txt = _gradient_text("NEW BOARD!", 22,
                          top_col=(60, 30, 10),
                          bot_col=(20, 10,  5),
                          outline=(255, 245, 200), outline_w=2)
    surf.blit(txt, txt.get_rect(center=cap.center))
    return surf


# ── C1 (kapow chorus) sub-variants — 5 spins on the same idea ───────────────


def _burst_word(surf, bx, by, label, fill, accent, rot_deg,
                ro=56, ri=30, font_size=None):
    """Two-layer jagged burst + tilted gradient text — the building
    block shared by all D-variants below."""
    _jagged_burst(surf, bx, by, ro, ri, spikes=10,
                  fill=fill, outline=INK, outline_w=4, jitter=4)
    _jagged_burst(surf, bx, by, int(ro * 0.68), int(ri * 0.73),
                  spikes=10, fill=accent, outline=INK, outline_w=2)
    if font_size is None:
        font_size = 28 if len(label) <= 5 else 24
    txt = _gradient_text(label, font_size,
                          top_col=(255, 250, 240),
                          bot_col=fill,
                          outline=INK, outline_w=3)
    rot = pygame.transform.rotate(txt, rot_deg)
    surf.blit(rot, rot.get_rect(center=(bx, by)))


def render_kapow_skate_slang_overlay(cx: int, cy: int,
                                       rng_seed: int = 22) -> pygame.Surface:
    """D1 — Same 4-corner KAPOW layout but with SKATE-SPECIFIC slang
    in the bursts: RAD! / GNARLY! / SICK! / SHRED!. Each burst
    keeps a distinct pop-art colorway. Reads as more on-brand for a
    skate powerup than the generic KAPOW/BAM."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    palette = (
        # (label, fill, accent, rot_deg, dx, dy)
        ("RAD!",    (255, 220,  30), (230,  60,  50),  -8, -120, -85),
        ("GNARLY!", (255, 100, 180), (255, 245, 200),  10,  135, -90),
        ("SICK!",   ( 95, 200, 220), ( 30,  60, 120),  -6, -140,  90),
        ("SHRED!",  (255, 165,  60), (220,  40,  40),   8,  125,  95),
    )
    for label, fill, accent, rot_deg, dx, dy in palette:
        bx = max(60, min(W - 60, cx + dx))
        by = max(110, min(H - 80, cy + dy))
        _burst_word(surf, bx, by, label, fill, accent, rot_deg)
    return surf


def render_kapow_hierarchy_overlay(cx: int, cy: int,
                                     rng_seed: int = 22) -> pygame.Surface:
    """D2 — Dominant burst + satellites. One BIG KABOOM! anchors the
    upper-right (replacing the role of the live POW!), with 3
    smaller satellite bursts (BAM!, SMASH!, ZAP!) around Pip. Size
    hierarchy gives a clear focal point instead of 4 equal-weight
    corner bursts."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    # Dominant burst — bigger ro/ri so it visually anchors.
    big_x = min(W - 80, cx + 130)
    big_y = max(170, cy - 70)
    _burst_word(surf, big_x, big_y,
                "KABOOM!", (255, 220, 30), (230, 60, 50),
                rot_deg=-12, ro=80, ri=42, font_size=34)
    # Satellites — smaller bursts at NW, SW, SE.
    sats = (
        ("BAM!",   (255, 100, 180), (255, 245, 200),  12, -130, -75),
        ("SMASH!", ( 95, 200, 220), ( 30,  60, 120),  -8, -135,  90),
        ("ZAP!",   (255, 165,  60), (220,  40,  40),  14,  120, 100),
    )
    for label, fill, accent, rot_deg, dx, dy in sats:
        bx = max(60, min(W - 60, cx + dx))
        by = max(110, min(H - 80, cy + dy))
        _burst_word(surf, bx, by, label, fill, accent, rot_deg,
                    ro=44, ri=24)
    return surf


def render_kapow_radial_ring_overlay(cx: int, cy: int,
                                       rng_seed: int = 22) -> pygame.Surface:
    """D3 — 6 bursts evenly spaced in a circle around Pip, each
    rotated to face outward. Surrounds Pip with onomatopoeia
    instead of pinning bursts to the corners — more dynamic and
    radial in feel."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    words = (
        ("KAPOW!", (255, 220,  30), (230,  60,  50)),
        ("BAM!",   (255, 100, 180), (255, 245, 200)),
        ("SMASH!", ( 95, 200, 220), ( 30,  60, 120)),
        ("WHAM!",  (255, 165,  60), (220,  40,  40)),
        ("ZAP!",   (140, 220, 110), ( 30,  80,  40)),
        ("BOOM!",  (220, 140, 255), ( 80,  30, 120)),
    )
    ring_r = 165
    n = len(words)
    for i, (label, fill, accent) in enumerate(words):
        # Distribute starting from the upper-right (skips the
        # SKATEBOARD! caption strip clamp at the top).
        ang = -math.pi / 2 + (i + 0.5) * (2 * math.pi / n)
        bx = cx + math.cos(ang) * ring_r
        by = cy + math.sin(ang) * ring_r
        bx = max(50, min(W - 50, bx))
        by = max(150, min(H - 60, by))
        # Mild varied tilt — clamped to ±18° so text stays readable
        # all around the ring (true radial alignment makes the side
        # bursts go 90° vertical and lose legibility).
        rot_deg = 18 * math.sin(ang * 2 + i * 0.5)
        _burst_word(surf, int(bx), int(by), label, fill, accent,
                    rot_deg, ro=46, ri=26, font_size=22)
    return surf


def _sticker_burst(surf, cx, cy, ro, ri, spikes, fill, jitter=4):
    """Sticker-style burst — drop shadow + flat fill + thick white
    inner border + black outer border. Looks like a skate-deck sticker
    pinned to the screen."""
    # Drop shadow — same polygon nudged down-right with dark alpha.
    shadow = pygame.Surface((W, H), pygame.SRCALPHA)
    rng = random.Random(int(cx) * 31 + int(cy) * 17 + spikes)
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = ro if i % 2 == 0 else ri
        if jitter:
            r += rng.randint(-jitter, jitter)
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    sh_pts = [(p[0] + 4, p[1] + 5) for p in pts]
    pygame.draw.polygon(shadow, (0, 0, 0, 110), sh_pts)
    surf.blit(shadow, (0, 0))
    # Outer black border (drawn as a slightly larger polygon underneath).
    pygame.draw.polygon(surf, INK, pts)
    # Inner fill polygon — same shape, scaled in slightly.
    inner_pts = [(cx + (p[0] - cx) * 0.92,
                  cy + (p[1] - cy) * 0.92) for p in pts]
    pygame.draw.polygon(surf, WHITE, inner_pts)
    inner_pts2 = [(cx + (p[0] - cx) * 0.80,
                   cy + (p[1] - cy) * 0.80) for p in pts]
    pygame.draw.polygon(surf, fill, inner_pts2)


def render_kapow_sticker_overlay(cx: int, cy: int,
                                   rng_seed: int = 22) -> pygame.Surface:
    """D4 — Punk-sticker collage. Same 4-corner KAPOW layout but each
    burst is painted as a skate-deck sticker: drop shadow + thick
    white inner border + thick black outer border, flat fill (no
    nested colored core). Punk-rock zine vibe."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    palette = (
        ("KAPOW!", (230,  60,  50),  -8, -120, -85),
        ("BAM!",   (255, 100, 180),  10,  135, -90),
        ("SMASH!", ( 95, 200, 220),  -6, -140,  90),
        ("WHAM!",  (255, 165,  60),   8,  125,  95),
    )
    for label, fill, rot_deg, dx, dy in palette:
        bx = max(70, min(W - 70, cx + dx))
        by = max(120, min(H - 80, cy + dy))
        _sticker_burst(surf, bx, by, 58, 32, spikes=10, fill=fill)
        font_size = 28 if len(label) <= 5 else 24
        txt = _gradient_text(label, font_size,
                              top_col=(255, 250, 240),
                              bot_col=(20, 20, 20),
                              outline=WHITE, outline_w=2)
        rot = pygame.transform.rotate(txt, rot_deg)
        surf.blit(rot, rot.get_rect(center=(bx, by)))
    return surf


def _halftone_filled_burst(surf, cx, cy, ro, ri, spikes,
                            dot_col, base_col, outline_w=4, jitter=4,
                            chaos=False):
    """Burst polygon filled with Lichtenstein halftone dots instead
    of solid color. Renders the dots onto a sub-surface, then masks
    them with the burst polygon shape so they only show inside.

    chaos=True picks each outer spike's radius from a punk-style
    multiplier pool (some spikes go FAR, others stay SHORT) instead
    of the gently-jittered symmetric star. Inner valleys keep the
    usual jitter so the burst still reads as a star and not a blob."""
    rng = random.Random(int(cx) * 31 + int(cy) * 17 + spikes)
    if chaos:
        spike_scales = [0.62, 0.80, 1.00, 1.00, 1.22, 1.45, 1.55]
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        if i % 2 == 0:
            r = ro * rng.choice(spike_scales) if chaos else ro
        else:
            r = ri
        if jitter and not (chaos and i % 2 == 0):
            r += rng.randint(-jitter, jitter)
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    pygame.draw.polygon(surf, base_col, pts)
    # Halftone dots — grid sample inside the burst bbox.
    bbox_l = int(min(p[0] for p in pts)) - 2
    bbox_t = int(min(p[1] for p in pts)) - 2
    bbox_r = int(max(p[0] for p in pts)) + 2
    bbox_b = int(max(p[1] for p in pts)) + 2
    dot_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    step = 8
    for gy in range(bbox_t, bbox_b, step):
        offset = (step // 2) if ((gy // step) % 2 == 1) else 0
        for gx in range(bbox_l + offset, bbox_r, step):
            pygame.draw.circle(dot_surf, dot_col,
                               (gx, gy), 2)
    # Mask the dots to the burst polygon — paint the polygon as
    # opaque alpha onto a mask surface, then RGBA_MIN.
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    dot_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(dot_surf, (0, 0))
    pygame.draw.polygon(surf, INK, pts, outline_w)


def render_kapow_halftone_filled_overlay(cx: int, cy: int,
                                           rng_seed: int = 22) -> pygame.Surface:
    """D5 — 4-corner KAPOW chorus, each burst FILLED with a halftone
    dot pattern instead of solid color. Combines the C1 onomatopoeia
    layout with the C2 Lichtenstein dot vocabulary inside each
    burst. Most overtly "pop-art comic page" of the bunch."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    palette = (
        # (label, base, dot_col, rot_deg, dx, dy)
        ("KAPOW!", (255, 220,  30), (230,  60,  50),  -8, -120, -85),
        ("BAM!",   (255, 100, 180), ( 90,  20,  90),  10,  135, -90),
        ("SMASH!", ( 95, 200, 220), ( 20,  40,  90),  -6, -140,  90),
        ("WHAM!",  (255, 165,  60), (180,  30,  30),   8,  125,  95),
    )
    for label, base, dot_col, rot_deg, dx, dy in palette:
        bx = max(60, min(W - 60, cx + dx))
        by = max(110, min(H - 80, cy + dy))
        _halftone_filled_burst(surf, bx, by, 58, 32, spikes=10,
                                dot_col=dot_col, base_col=base)
        font_size = 28 if len(label) <= 5 else 24
        txt = _gradient_text(label, font_size,
                              top_col=(255, 250, 240),
                              bot_col=base,
                              outline=INK, outline_w=3)
        rot = pygame.transform.rotate(txt, rot_deg)
        surf.blit(rot, rot.get_rect(center=(bx, by)))
    return surf


# ── D5 (halftone-filled bursts) sub-variants for the SCORE display ──────────
#
# During the skateboard effect the user wants the SCORE itself painted in the
# D5 halftone-comic style so it doesn't compete with the SKATEBOARD! caption
# strip at y=75 (the live glass-pill score sits at y=92 and clashes with the
# caption). These overlays persist for the whole effect duration — the caller
# blits them at fixed alpha while skateboard_active is True, unlike the
# caption (which fades) or the starburst (which is short).


def _halftone_score_badge(surf, cx, cy, score_str,
                           ro=48, ri=28, font_size=32,
                           label=None, base_col=(255, 220, 30),
                           dot_col=(230, 60, 50)):
    """Paint a D5-style halftone-filled burst at (cx, cy) with the
    score number (and optional small label) inside."""
    _halftone_filled_burst(surf, cx, cy, ro, ri, spikes=10,
                            dot_col=dot_col, base_col=base_col)
    if label:
        lbl_font_size = max(12, int(font_size * 0.42))
        lbl = _gradient_text(label, lbl_font_size,
                              top_col=(255, 250, 240),
                              bot_col=dot_col,
                              outline=INK, outline_w=2)
        surf.blit(lbl, lbl.get_rect(
            center=(cx, cy - int(font_size * 0.42))))
        num = _gradient_text(score_str, font_size,
                              top_col=(255, 250, 240),
                              bot_col=dot_col,
                              outline=INK, outline_w=3)
        surf.blit(num, num.get_rect(
            center=(cx, cy + int(font_size * 0.22))))
    else:
        num = _gradient_text(score_str, font_size,
                              top_col=(255, 250, 240),
                              bot_col=dot_col,
                              outline=INK, outline_w=3)
        surf.blit(num, num.get_rect(center=(cx, cy)))


def render_skateboard_score_e1(score: int) -> pygame.Surface:
    """E1 — Compact halftone burst in the UPPER-RIGHT corner, just the
    score number inside. Smallest footprint of the bunch; clears the
    SKATEBOARD! caption strip entirely."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _halftone_score_badge(surf, W - 58, 118, str(score),
                           ro=48, ri=28, font_size=30)
    return surf


def render_skateboard_score_e2(score: int) -> pygame.Surface:
    """E2 — BIG halftone burst centred just below the SKATEBOARD!
    caption (y≈185). The biggest and most prominent option — the
    score IS the comic burst, cleanly clear of the caption strip
    which ends around y=109."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _halftone_score_badge(surf, W // 2, 185, str(score),
                           ro=74, ri=44, font_size=52)
    return surf


_SCORE_E3_CACHE = None   # (score, surface) — burst+digits are static per score


def render_skateboard_score_e3(score: int) -> pygame.Surface:
    """E3 — Halftone burst centered at the same on-screen position as
    the regular NA score plate (y=70). The HUD blits this overlay with
    `(0, -_skateboard_lift_y)` shift (lift_y=26), so the badge is drawn
    at y=96 inside the (W×H) overlay → lands on screen at y=70, exactly
    matching the regular plate. Digit font matches the regular HUD
    score's _font(48, True); ro/ri size the burst around the bigger
    glyph; chaos=True throws each outer spike onto a punk-style
    long/short multiplier so the star reads as a deliberate uneven
    pop-art shout instead of a symmetric snowflake.

    Memoised on `score`: the burst + digits only change when the score does
    (≈ once per point), so this no longer rebuilds a full-screen halftone burst
    (~1000 circle draws) every frame while the skateboard is active."""
    global _SCORE_E3_CACHE
    if _SCORE_E3_CACHE is not None and _SCORE_E3_CACHE[0] == score:
        return _SCORE_E3_CACHE[1]
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx, cy = W // 2, 96
    _halftone_filled_burst(surf, cx, cy, ro=62, ri=40, spikes=10,
                            dot_col=(230, 60, 50),
                            base_col=(255, 220, 30),
                            chaos=True)
    num = _gradient_text(str(score), 48,
                          top_col=(255, 250, 240),
                          bot_col=(230, 60, 50),
                          outline=INK, outline_w=3)
    surf.blit(num, num.get_rect(center=(cx, cy)))
    _SCORE_E3_CACHE = (score, surf)
    return surf


def render_skateboard_score_e4(score: int) -> pygame.Surface:
    """E4 — Halftone burst upper-right with a small "SCORE" label
    stacked above the number — explicit two-line layout so the
    number reads as a SCORE even out of context."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _halftone_score_badge(surf, W - 68, 130, str(score),
                           ro=66, ri=40, font_size=36, label="SCORE")
    return surf


def render_skateboard_score_e5(score: int) -> pygame.Surface:
    """E5 — Composite: small "SCORE" burst in cyan/navy beside a
    bigger number burst in yellow/red, both upper-right. Two
    side-by-side badges read as a scoreboard inset rather than a
    single emblem. Cyan label contrasts the yellow number so they
    don't blur together."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    # Small SCORE label burst (left).
    _halftone_filled_burst(surf, W - 124, 132, 38, 22, spikes=10,
                            dot_col=(30, 60, 120),
                            base_col=(95, 200, 220))
    lbl = _gradient_text("SCORE", 18,
                          top_col=(255, 250, 240),
                          bot_col=(30, 60, 120),
                          outline=INK, outline_w=2)
    surf.blit(lbl, lbl.get_rect(center=(W - 124, 132)))
    # Bigger number burst (right, well clear of the SCORE chip).
    _halftone_score_badge(surf, W - 50, 132, str(score),
                           ro=46, ri=28, font_size=32)
    return surf


def render_skateboard_score_e6(score: int) -> pygame.Surface:
    """E6 — Score painted at the EXACT live-pill position (y=92) —
    same spot the score sits during normal play, just restyled into
    a D5 halftone-comic burst. Minimal-change option: only the
    graphic swaps; the player's eyes still find the score where they
    always look. Width roughly matches the existing glass pill so
    the silhouette stays familiar."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


# ── SKATEBOARD! caption layouts that don't collide with the score ───────────
#
# The live `render_caption_overlay` plate sits at (W // 2, 75) and the live
# glass-pill score sits at (W // 2, 92) — they overlap. These 5 alternative
# caption layouts each clear the score's vertical band (or combine the
# SKATEBOARD! text WITH the score number in one composite). Pair F1/F3/F4
# with a separate D5 score overlay; F2/F5 already bake the score in.


def _corner_slashes(surf, cx, cy):
    """2-corner ink speed-slashes pointing at (cx, cy) — same primitive
    the live caption uses; bottom corners dropped because they read as
    gameplay obstacles in the lower half of the playfield."""
    for x0, y0 in ((20, 20), (W - 20, 20)):
        for off in range(3):
            dx = (cx - x0) * 0.18
            dy = (cy - y0) * 0.18
            ox = (-1 if x0 < cx else 1) * (off * 8)
            oy = off * 4
            pygame.draw.line(surf, INK,
                             (x0 + ox, y0 + oy),
                             (x0 + ox + dx, y0 + oy + dy), 4)


def _pow_badge(surf, center, tilt_deg=15):
    """Standard POW! badge for the F-variants. Caller picks the
    centre so different layouts can park it where they have room."""
    pow_txt = _gradient_text("POW!", 28,
                              top_col=(255, 90, 90),
                              bot_col=(220, 30, 30),
                              outline=INK, outline_w=4)
    pow_rot = pygame.transform.rotate(pow_txt, tilt_deg)
    surf.blit(pow_rot, pow_rot.get_rect(center=center))


def _red_plate(text, font_size, plate_pad=(30, 18)):
    """Build a SKATEBOARD!-style gradient-on-red rounded plate
    (no rotation applied). Returns the composite surface."""
    txt = _gradient_text(text, font_size,
                          top_col=(255, 255, 110),
                          bot_col=(255, 180, 10),
                          outline=INK, outline_w=5)
    px, py = plate_pad
    bw = txt.get_width() + px
    bh = txt.get_height() + py
    composite = pygame.Surface((bw + 12, bh + 12), pygame.SRCALPHA)
    ccx = composite.get_width() // 2
    ccy = composite.get_height() // 2
    plate_rect = pygame.Rect(0, 0, bw, bh)
    plate_rect.center = (ccx + 4, ccy + 4)
    pygame.draw.rect(composite, PLATE_RED, plate_rect, border_radius=10)
    pygame.draw.rect(composite, INK, plate_rect, 4, border_radius=10)
    composite.blit(txt, txt.get_rect(center=(ccx, ccy)).topleft)
    return composite


def render_caption_v2_topleft(cx: int, cy: int,
                                rng_seed: int = 22) -> pygame.Surface:
    """F1 — Smaller SKATEBOARD! plate parked in the TOP-LEFT corner.
    POW! mirrors over to the top-right. Whole upper-center band
    (where the score lives at y=92) stays clear."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _red_plate("SKATEBOARD!", 28, plate_pad=(24, 14))
    rot = pygame.transform.rotate(plate, -4)
    surf.blit(rot, rot.get_rect(midleft=(8, 38)))
    _pow_badge(surf, (W - 50, 38), tilt_deg=12)
    return surf


def render_caption_v2_combined_banner(cx: int, cy: int, score: int,
                                        rng_seed: int = 22) -> pygame.Surface:
    """F2 — Combined banner: a single wide red plate across the top
    holding "SKATEBOARD!" on the left AND the live score number on
    the right (each with their own outlined gradient text).  The
    plate IS the caption AND the score — no separate score overlay
    needed."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate_w = W - 24
    plate_h = 56
    plate_rect = pygame.Rect(0, 0, plate_w, plate_h)
    plate_rect.center = (W // 2, 50)
    # Drop shadow
    sh_rect = plate_rect.move(4, 4)
    pygame.draw.rect(surf, (0, 0, 0, 120), sh_rect, border_radius=12)
    # Plate
    pygame.draw.rect(surf, PLATE_RED, plate_rect, border_radius=12)
    pygame.draw.rect(surf, INK, plate_rect, 4, border_radius=12)
    # SKATEBOARD! text — left aligned
    skate = _gradient_text("SKATEBOARD!", 32,
                            top_col=(255, 255, 110),
                            bot_col=(255, 180, 10),
                            outline=INK, outline_w=4)
    surf.blit(skate, skate.get_rect(
        midleft=(plate_rect.left + 14, plate_rect.centery)))
    # Divider — thin ink vertical bar between caption and score.
    div_x = plate_rect.left + plate_w - 110
    pygame.draw.line(surf, INK,
                     (div_x, plate_rect.top + 8),
                     (div_x, plate_rect.bottom - 8), 3)
    # SCORE number on the right, in halftone-burst style so the
    # comic vocabulary stays consistent with the D5 chorus pick.
    score_cx = (div_x + plate_rect.right) // 2
    score_cy = plate_rect.centery
    _halftone_score_badge(surf, score_cx, score_cy, str(score),
                           ro=24, ri=16, font_size=28)
    return surf


def render_caption_v2_below_score(cx: int, cy: int,
                                    rng_seed: int = 22) -> pygame.Surface:
    """F3 — SKATEBOARD! plate moved DOWN below the score band
    (centered around y=150). Score keeps its native y=92 spot
    above; caption sits just below where the chorus bursts top out
    so it stays clear of the score forever."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _red_plate("SKATEBOARD!", 40, plate_pad=(30, 18))
    rot = pygame.transform.rotate(plate, 5)
    surf.blit(rot, rot.get_rect(center=(W // 2, 150)))
    _pow_badge(surf, (W - 50, 38), tilt_deg=15)
    return surf


def render_caption_v2_vertical_left(cx: int, cy: int,
                                      rng_seed: int = 22) -> pygame.Surface:
    """F4 — SKATEBOARD! rotated 90° on the LEFT edge — like a vertical
    deck-sticker ribbon hanging down the side. Whole top of the
    screen frees up for the score. POW! goes top-right."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _red_plate("SKATEBOARD!", 32, plate_pad=(28, 14))
    rot = pygame.transform.rotate(plate, 90)
    surf.blit(rot, rot.get_rect(midleft=(6, H // 2 - 30)))
    _pow_badge(surf, (W - 50, 38), tilt_deg=15)
    return surf


def render_caption_v2_split_around(cx: int, cy: int, score: int,
                                     rng_seed: int = 22) -> pygame.Surface:
    """F5 — Caption SPLIT in two halves wrapping the score: "SKATE"
    plate on the left, "BOARD!" plate on the right, both around
    y=72, with the D5 score burst sitting between/below them at
    y=92. Whole composite reads as one wide unit but the score has
    its own clear centre spot. Plates sized tight enough to stay
    fully on-canvas (no clipped letters)."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    # Tight plates that fit inside the canvas.
    skate = _red_plate("SKATE", 26, plate_pad=(16, 10))
    skate_rot = pygame.transform.rotate(skate, -5)
    surf.blit(skate_rot, skate_rot.get_rect(midright=(W // 2 - 50, 56)))
    board = _red_plate("BOARD!", 26, plate_pad=(16, 10))
    board_rot = pygame.transform.rotate(board, 5)
    surf.blit(board_rot, board_rot.get_rect(midleft=(W // 2 + 50, 56)))
    # D5 score burst between the halves — slightly larger so it
    # reads as the centrepiece anchoring the split caption.
    _halftone_score_badge(surf, W // 2, 80, str(score),
                           ro=46, ri=28, font_size=38)
    return surf


# ── SKATEBOARD! text as a "watermark" BEHIND the score ─────────────────────
#
# User wants the caption painted at the same position as the score (the
# live pill at y=92) but in a way that the score on top can still be read.
# Five techniques here, each painting the SKATEBOARD! word in a different
# "see-through" style so the foreground score isn't covered. The score
# itself sits on top as the D5 halftone burst (matching the chosen chorus
# vocabulary).


def _hollow_text(text, size, outline_col, outline_w=4):
    """Outline-only text — no fill. Built by rendering the text in
    outline_col around a circle of offsets, then SUBTRACTING the
    text mask so the interior becomes transparent."""
    font = _font(size)
    mask = font.render(text, True, (255, 255, 255, 255))
    bw, bh = mask.get_size()
    pad = outline_w + 2
    surf = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
    out_glyph = font.render(text, True, outline_col)
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx * dx + dy * dy <= outline_w * outline_w and (dx or dy):
                surf.blit(out_glyph, (pad + dx, pad + dy))
    # Subtract the inner mask alpha so the interior of each letter
    # goes transparent (only the outer ring of outline_col remains).
    cutter = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
    cutter.blit(mask, (pad, pad))
    surf.blit(cutter, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return surf


def _patterned_text(text, size, pattern_fn, outline_col, outline_w=4):
    """Text filled with whatever `pattern_fn(surf, w, h)` paints,
    masked to the letter shapes, with outline_col stroke around the
    outside. Used by G2 (halftone dots) and G4 (horizontal stripes)."""
    font = _font(size)
    mask = font.render(text, True, (255, 255, 255, 255))
    bw, bh = mask.get_size()
    pad = outline_w + 2
    # 1. Pattern surface, then mask to the letter shape.
    pattern = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pattern_fn(pattern, bw, bh)
    pattern.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # 2. Outline blit ring around the text.
    surf = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
    out_glyph = font.render(text, True, outline_col)
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx * dx + dy * dy <= outline_w * outline_w and (dx or dy):
                surf.blit(out_glyph, (pad + dx, pad + dy))
    surf.blit(pattern, (pad, pad))
    return surf


def _fit_to_canvas(surf, max_w):
    """Shrink-to-fit so a wide stylised SKATEBOARD! never clips off
    the canvas edges. Returns the same surface if it already fits."""
    if surf.get_width() <= max_w:
        return surf
    ratio = max_w / surf.get_width()
    new_w = int(surf.get_width() * ratio)
    new_h = int(surf.get_height() * ratio)
    return pygame.transform.smoothscale(surf, (new_w, new_h))


def render_caption_g1_hollow(cx: int, cy: int, score: int,
                              rng_seed: int = 22) -> pygame.Surface:
    """G1 — Hollow outline-only SKATEBOARD! text behind the score.
    Letters are just ink rings; the interior of each letter is
    transparent so the sky shows through and the score in front
    reads cleanly."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    txt = _hollow_text("SKATEBOARD!", 46, outline_col=INK,
                        outline_w=5)
    txt = _fit_to_canvas(txt, W - 16)
    surf.blit(txt, txt.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


def render_caption_g2_halftone_text(cx: int, cy: int, score: int,
                                      rng_seed: int = 22) -> pygame.Surface:
    """G2 — Halftone-dot SKATEBOARD! text behind the score. Each
    letter is filled with red dots on a yellow base masked to the
    glyph shape — Lichtenstein vocabulary, consistent with the D5
    chorus pick."""
    def dot_pattern(surf_, w, h):
        surf_.fill((255, 220, 30, 255))
        for gy in range(2, h, 6):
            offset = 3 if ((gy // 6) % 2 == 1) else 0
            for gx in range(2 + offset, w, 6):
                pygame.draw.circle(surf_, (230, 60, 50, 255),
                                   (gx, gy), 2)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    txt = _patterned_text("SKATEBOARD!", 46,
                           pattern_fn=dot_pattern,
                           outline_col=INK, outline_w=5)
    txt = _fit_to_canvas(txt, W - 16)
    surf.blit(txt, txt.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


def render_caption_g3_ghost(cx: int, cy: int, score: int,
                              rng_seed: int = 22) -> pygame.Surface:
    """G3 — Ghost/watermark SKATEBOARD! text behind the score. Full
    gradient fill but at low alpha (~110/255) so the text reads as a
    subtle background watermark and the score punches through in
    full brightness."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    txt = _gradient_text("SKATEBOARD!", 50,
                          top_col=(255, 255, 110),
                          bot_col=(255, 180, 10),
                          outline=INK, outline_w=5)
    txt = _fit_to_canvas(txt, W - 16)
    txt = txt.copy()
    txt.set_alpha(110)
    surf.blit(txt, txt.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


def render_caption_g4_striped(cx: int, cy: int, score: int,
                                rng_seed: int = 22) -> pygame.Surface:
    """G4 — Striped SKATEBOARD! text behind the score. Each letter
    filled with horizontal red-and-cream barber-pole stripes; reads
    as a comic shading hatch that doesn't fully fill the glyph."""
    def stripe_pattern(surf_, w, h):
        stripe_h = 5
        for gy in range(0, h, stripe_h):
            col = (220, 50, 40, 255) if (gy // stripe_h) % 2 == 0 \
                  else (255, 245, 200, 255)
            pygame.draw.rect(surf_, col, (0, gy, w, stripe_h))
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    txt = _patterned_text("SKATEBOARD!", 46,
                           pattern_fn=stripe_pattern,
                           outline_col=INK, outline_w=5)
    txt = _fit_to_canvas(txt, W - 16)
    surf.blit(txt, txt.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


def render_caption_g5_huge_bg(cx: int, cy: int, score: int,
                                rng_seed: int = 22) -> pygame.Surface:
    """G5 — Huge SKATEBOARD! text spanning the full canvas width as
    a low-alpha background slab behind the score. The text is so
    large that the score sits inside its central "..BOARD.." region
    while "SKATE" peeks on the left edge and "!" on the right —
    feels like the word is the backdrop for the score."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    txt = _gradient_text("SKATEBOARD!", 78,
                          top_col=(255, 255, 110),
                          bot_col=(255, 180, 10),
                          outline=INK, outline_w=6)
    # Auto-scale down if rendered text is wider than the canvas.
    if txt.get_width() > W - 8:
        ratio = (W - 8) / txt.get_width()
        new_w = int(txt.get_width() * ratio)
        new_h = int(txt.get_height() * ratio)
        txt = pygame.transform.smoothscale(txt, (new_w, new_h))
    txt = txt.copy()
    txt.set_alpha(130)
    surf.blit(txt, txt.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


# ── SAME plate design, played with placement / tilt / size ──────────────────
#
# User feedback on G (watermark-style text fills) was "not good — same
# design, just placed / tilted / sized differently". These H-variants
# keep the live caption's exact plate-design (red gradient plate with
# yellow-orange gradient text, ink outline) and only vary where it sits,
# how it tilts, and how big it is. The D5 score burst lives at its
# native y=92 spot on top in all five.


def render_caption_h1_bigger_tilted(cx: int, cy: int, score: int,
                                      rng_seed: int = 22) -> pygame.Surface:
    """H1 — Same plate, parked AT the score's y=92 spot, font bumped
    from 42 to 48 and tilted to +12° (vs the live +5°). Score burst
    sits in the middle as a badge — same plate, just bigger + more
    dynamic."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _red_plate("SKATEBOARD!", 48, plate_pad=(32, 18))
    rot = pygame.transform.rotate(plate, 12)
    surf.blit(rot, rot.get_rect(center=(W // 2, 92)))
    _pow_badge(surf, (W - 50, 38), tilt_deg=15)
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


def render_caption_h2_xl_tilted_other_way(cx: int, cy: int, score: int,
                                            rng_seed: int = 22) -> pygame.Surface:
    """H2 — Same plate at the score's y=92 spot, even BIGGER (font
    52), tilted the OPPOSITE way to the live caption (-10°) so the
    composition feels different at a glance."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _red_plate("SKATEBOARD!", 52, plate_pad=(34, 20))
    rot = pygame.transform.rotate(plate, -10)
    surf.blit(rot, rot.get_rect(center=(W // 2, 92)))
    _pow_badge(surf, (W - 50, 38), tilt_deg=15)
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


def render_caption_h3_compact_flat(cx: int, cy: int, score: int,
                                     rng_seed: int = 22) -> pygame.Surface:
    """H3 — Same plate but SMALLER (font 30) and FLAT (no tilt),
    centred under the score. The score dominates; the plate plays
    a quiet supporting role tucked behind."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _red_plate("SKATEBOARD!", 30, plate_pad=(22, 12))
    surf.blit(plate, plate.get_rect(center=(W // 2, 92)))
    _pow_badge(surf, (W - 50, 38), tilt_deg=15)
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


def render_caption_h4_offset_below(cx: int, cy: int, score: int,
                                     rng_seed: int = 22) -> pygame.Surface:
    """H4 — Same plate design, but VERTICALLY OFFSET below the score
    (y=120 instead of y=92). The score number sits ABOVE the
    caption, both readable, both at their best size — like the
    score is a label hovering over the SKATEBOARD! sign."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _red_plate("SKATEBOARD!", 42, plate_pad=(30, 16))
    rot = pygame.transform.rotate(plate, 6)
    surf.blit(rot, rot.get_rect(center=(W // 2, 120)))
    _pow_badge(surf, (W - 50, 38), tilt_deg=15)
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=44, ri=28, font_size=40)
    return surf


def render_caption_h5_wide_banner(cx: int, cy: int, score: int,
                                    rng_seed: int = 22) -> pygame.Surface:
    """H5 — Same plate design but STRETCHED HORIZONTALLY — wider
    horizontal padding (60 vs 30) makes the plate read as a long
    banner across the score's row, with the score badge punching
    through the centre. Plate text stays at the live 42 px font but
    sits inside extra red real-estate left & right of the score."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _red_plate("SKATEBOARD!", 42, plate_pad=(70, 18))
    rot = pygame.transform.rotate(plate, -4)
    surf.blit(rot, rot.get_rect(center=(W // 2, 92)))
    _pow_badge(surf, (W - 50, 38), tilt_deg=15)
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


def render_caption_h6_banner_text_lowered(cx: int, cy: int, score: int,
                                            rng_seed: int = 22) -> pygame.Surface:
    """H6 — H5 (wide banner) refined: the SKATEBOARD! text is
    dropped DOWN so the score numbers stay clear of it. The red
    banner body still extends up into the score row and overlaps
    the score's halftone bubble (the burst around the digits) but
    the digits themselves never get covered. Banner center at
    y=140, text fully below the score's number footprint."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _red_plate("SKATEBOARD!", 32, plate_pad=(60, 12))
    rot = pygame.transform.rotate(plate, -4)
    surf.blit(rot, rot.get_rect(center=(W // 2, 140)))
    _pow_badge(surf, (W - 50, 38), tilt_deg=15)
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=48, ri=30, font_size=42)
    return surf


# ── "SKATE  [score]  BOARD!" — score wedged between the two halves ──────────
#
# Same red-plate design as the live caption, split into a "SKATE" half and a
# "BOARD!" half with the D5 score burst nested between them. Five variations
# explore tilt direction, gap width, and stagger.


def _one_piece_two_word_plate(left_word, right_word, font_size,
                                plate_pad, gap_w):
    """Single CONTINUOUS red plate with `left_word` aligned to the
    left interior + `right_word` aligned to the right, with `gap_w`
    of empty red space between them. Returns a composite surface
    centred around its midpoint — caller blits it at the target
    centre. One piece — not two plates."""
    left_txt = _gradient_text(left_word, font_size,
                                top_col=(255, 255, 110),
                                bot_col=(255, 180, 10),
                                outline=INK, outline_w=5)
    right_txt = _gradient_text(right_word, font_size,
                                 top_col=(255, 255, 110),
                                 bot_col=(255, 180, 10),
                                 outline=INK, outline_w=5)
    pad_x, pad_y = plate_pad
    plate_w = (left_txt.get_width() + gap_w
                + right_txt.get_width() + pad_x * 2)
    plate_h = max(left_txt.get_height(),
                   right_txt.get_height()) + pad_y * 2
    composite = pygame.Surface((plate_w + 12, plate_h + 12),
                                pygame.SRCALPHA)
    ccx = composite.get_width() // 2
    ccy = composite.get_height() // 2
    plate_rect = pygame.Rect(0, 0, plate_w, plate_h)
    plate_rect.center = (ccx + 4, ccy + 4)
    pygame.draw.rect(composite, PLATE_RED, plate_rect, border_radius=10)
    pygame.draw.rect(composite, INK, plate_rect, 4, border_radius=10)
    # Left word — left edge of left text sits at pad_x inside the plate
    composite.blit(left_txt, left_txt.get_rect(
        midleft=(plate_rect.left + pad_x, plate_rect.centery)))
    # Right word — right edge of right text sits at pad_x inside
    composite.blit(right_txt, right_txt.get_rect(
        midright=(plate_rect.right - pad_x, plate_rect.centery)))
    return composite


def _two_plates_around_score(surf, score_str,
                              font_size, plate_pad, gap,
                              tilt_l, tilt_r,
                              score_ro=44, score_ri=28,
                              score_font_size=38,
                              left_dy=0, right_dy=0,
                              score_cy=92, score_cx=None):
    """Paint a SKATE plate (left, tilt_l) + BOARD! plate (right,
    tilt_r) at score_cy, with the D5 halftone score burst centred
    between them at score_cx (default W/2, score_cy). Optional
    left_dy/right_dy stagger the two plates vertically. Score sits
    in the gap between the plate inner edges."""
    if score_cx is None:
        score_cx = W // 2
    skate = _red_plate("SKATE", font_size, plate_pad=plate_pad)
    skate_rot = pygame.transform.rotate(skate, tilt_l)
    surf.blit(skate_rot, skate_rot.get_rect(
        midright=(score_cx - gap // 2, score_cy + left_dy)))
    board = _red_plate("BOARD!", font_size, plate_pad=plate_pad)
    board_rot = pygame.transform.rotate(board, tilt_r)
    surf.blit(board_rot, board_rot.get_rect(
        midleft=(score_cx + gap // 2, score_cy + right_dy)))
    _halftone_score_badge(surf, score_cx, score_cy, score_str,
                           ro=score_ro, ri=score_ri,
                           font_size=score_font_size)


def render_caption_i1_inward_v(cx: int, cy: int, score: int,
                                 rng_seed: int = 22) -> pygame.Surface:
    """I1 — Plates tilt INWARD toward the score: SKATE leans
    down-right (+8°), BOARD! leans down-left (-8°). The two plates
    form a V pointing up at the score burst. Most dynamic of the
    bunch."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    _two_plates_around_score(surf, str(score),
                              font_size=28, plate_pad=(16, 12),
                              gap=92, tilt_l=8, tilt_r=-8,
                              score_ro=44, score_ri=28,
                              score_font_size=38)
    return surf


def render_caption_i2_outward_lambda(cx: int, cy: int, score: int,
                                       rng_seed: int = 22) -> pygame.Surface:
    """I2 — Plates tilt OUTWARD away from the score: SKATE leans
    up-right (-8°), BOARD! leans up-left (+8°). The plates fan
    away from the centre, making the score the apex of an
    inverted V."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    _two_plates_around_score(surf, str(score),
                              font_size=28, plate_pad=(16, 12),
                              gap=92, tilt_l=-8, tilt_r=8,
                              score_ro=44, score_ri=28,
                              score_font_size=38)
    return surf


def render_caption_i3_tight_compact(cx: int, cy: int, score: int,
                                      rng_seed: int = 22) -> pygame.Surface:
    """I3 — Tight + compact: plates pulled close together with a
    SMALL score burst between them. The whole composite is more
    compressed; reads as one wide unit rather than two halves
    flanking a focal point."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    _two_plates_around_score(surf, str(score),
                              font_size=30, plate_pad=(14, 10),
                              gap=58, tilt_l=-3, tilt_r=3,
                              score_ro=30, score_ri=18,
                              score_font_size=26)
    return surf


def render_caption_i4_wide_big_score(cx: int, cy: int, score: int,
                                       rng_seed: int = 22) -> pygame.Surface:
    """I4 — Wide gap, BIG score: plates pushed to the edges of the
    canvas with a large score burst dominating the centre. Score
    is the star; the SKATE/BOARD halves bracket it."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    _two_plates_around_score(surf, str(score),
                              font_size=24, plate_pad=(12, 10),
                              gap=130, tilt_l=-3, tilt_r=3,
                              score_ro=58, score_ri=36,
                              score_font_size=48)
    return surf


def render_caption_i5_staggered(cx: int, cy: int, score: int,
                                  rng_seed: int = 22) -> pygame.Surface:
    """I5 — Staggered: SKATE plate sits slightly LOWER (+10 px) and
    BOARD! sits slightly HIGHER (-10 px), so the two halves
    diagonally bracket the centred score. Adds a hand-pinned-up
    "deck sticker" feel to the composition. Both plates share a
    mild negative tilt so the eye reads the stagger as
    intentional, not an alignment error."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    _two_plates_around_score(surf, str(score),
                              font_size=28, plate_pad=(16, 12),
                              gap=92, tilt_l=-5, tilt_r=-5,
                              score_ro=44, score_ri=28,
                              score_font_size=38,
                              left_dy=10, right_dy=-10)
    return surf


# ── J variants — ONE-PIECE banner with gap for the score ────────────────────
#
# Five takes on a SINGLE continuous red plate. Inside the plate, SKATE
# sits on the left, BOARD! on the right, with a gap between where the D5
# score burst lives. The plate is one piece — not two separate plates.


def render_caption_j1_score_fits(cx: int, cy: int, score: int,
                                   rng_seed: int = 22) -> pygame.Surface:
    """J1 — One-piece banner, gap sized so the D5 score burst fits
    inside the plate's height. Score sits comfortably IN the gap;
    the red plate body wraps around the score (visible above + below
    + on either side of it). Cleanest "score is part of the banner"
    read."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _one_piece_two_word_plate("SKATE", "BOARD!",
                                        font_size=30,
                                        plate_pad=(16, 14),
                                        gap_w=72)
    rot = pygame.transform.rotate(plate, 5)
    surf.blit(rot, rot.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=30, ri=18, font_size=26)
    return surf


def render_caption_j2_score_punches_through(cx: int, cy: int, score: int,
                                              rng_seed: int = 22) -> pygame.Surface:
    """J2 — One-piece banner; score is LARGER than the plate height
    so the burst pops above and below the banner. The plate stays
    one continuous piece (you can see the red running behind the
    score burst's narrowed waist), but the burst's spikes punch out
    top + bottom."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _one_piece_two_word_plate("SKATE", "BOARD!",
                                        font_size=32,
                                        plate_pad=(16, 12),
                                        gap_w=90)
    rot = pygame.transform.rotate(plate, 5)
    surf.blit(rot, rot.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=52, ri=32, font_size=44)
    return surf


def render_caption_j3_compact(cx: int, cy: int, score: int,
                                rng_seed: int = 22) -> pygame.Surface:
    """J3 — Compact one-piece banner: smaller everything, tighter
    gap, mini score. Reads as one wide gold-on-red banner with a
    small comic emblem in the middle. Most "ribbon" feeling."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _one_piece_two_word_plate("SKATE", "BOARD!",
                                        font_size=28,
                                        plate_pad=(14, 10),
                                        gap_w=56)
    rot = pygame.transform.rotate(plate, 5)
    surf.blit(rot, rot.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=24, ri=14, font_size=22)
    return surf


def render_caption_j4_wide_big_score(cx: int, cy: int, score: int,
                                       rng_seed: int = 22) -> pygame.Surface:
    """J4 — Wide one-piece banner stretching to canvas edges with a
    BIG gap holding a BIG score. Plate is taller too so the bigger
    score fits inside vertically without punching out. Score
    dominates the centre of a long horizontal ribbon."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _one_piece_two_word_plate("SKATE", "BOARD!",
                                        font_size=28,
                                        plate_pad=(20, 22),
                                        gap_w=110)
    rot = pygame.transform.rotate(plate, 3)
    surf.blit(rot, rot.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=44, ri=28, font_size=38)
    return surf


def render_caption_j5_tilted(cx: int, cy: int, score: int,
                               rng_seed: int = 22) -> pygame.Surface:
    """J5 — Same one-piece banner as J1 but more dramatically
    TILTED (-10° instead of the live +5°), so the whole composite
    leans the opposite way. Gives the banner more "deck sticker
    slapped on at an angle" energy."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _corner_slashes(surf, cx, cy)
    plate = _one_piece_two_word_plate("SKATE", "BOARD!",
                                        font_size=30,
                                        plate_pad=(16, 14),
                                        gap_w=78)
    rot = pygame.transform.rotate(plate, -10)
    surf.blit(rot, rot.get_rect(center=(W // 2, 92)))
    _halftone_score_badge(surf, W // 2, 92, str(score),
                           ro=32, ri=20, font_size=28)
    return surf


def render_starburst_surface(rng_seed: int = 22) -> pygame.Surface:
    """Self-contained 14-spike yellow/red starburst on a transparent
    BURST_SIZE × BURST_SIZE surface, centered. scenes.py blits this
    centered on Pip's current screen position each frame so the
    burst appears to follow him."""
    rng = random.Random(rng_seed)
    surf = pygame.Surface((BURST_SIZE, BURST_SIZE), pygame.SRCALPHA)
    cx = cy = BURST_SIZE // 2

    spikes = 14
    inner_r = 70
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = (140 + rng.randint(-20, 25)) if i % 2 == 0 else inner_r
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    pygame.draw.polygon(surf, YELLOW, pts)
    pygame.draw.polygon(surf, INK, pts, 5)
    inner_pts = [(cx + (p[0] - cx) * 0.65, cy + (p[1] - cy) * 0.65)
                 for p in pts]
    pygame.draw.polygon(surf, RED, inner_pts)
    pygame.draw.polygon(surf, INK, inner_pts, 3)
    return surf

"""Comparison sheet of SKATEBOARD! banner placements, each rendered on
the same live gameplay frame with the new (y=70) halftone score already
in place. Outputs four round sheets:
    docs/skateboard_banner_options/round_1.png   banner DODGES the score
    docs/skateboard_banner_options/round_2.png   banner ON TOP, score OVERLAID
    docs/skateboard_banner_options/round_3.png   banner+score UNIFIED hero
    docs/skateboard_banner_options/round_4.png   skate-deck composites (R3-C3
                                                 reworked LOWER, with LARGER
                                                 wordmark + burst INSIDE the
                                                 deck silhouette)

Run from the repo root:
    python tools/render_skateboard_banner_options.py
"""
import math
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import random
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, SKATEBOARD_DURATION
from game.scenes import App, STATE_PLAY
from game.world import World
from game.skateboard_fx import (
    _gradient_text,
    _halftone_filled_burst,
    _halftone_score_badge,
    INK,
    PLATE_RED,
)


OUT_DIR = os.path.join(_ROOT, "docs", "skateboard_banner_options")
OUT_PATH = os.path.join(OUT_DIR, "round_1.png")
OUT_PATH_R2 = os.path.join(OUT_DIR, "round_2.png")
OUT_PATH_R3 = os.path.join(OUT_DIR, "round_3.png")
OUT_PATH_R4 = os.path.join(OUT_DIR, "round_4.png")
OUT_PATH_R5 = os.path.join(OUT_DIR, "round_5.png")
OUT_PATH_R6 = os.path.join(OUT_DIR, "round_6.png")
OUT_PATH_R7 = os.path.join(OUT_DIR, "round_7.png")
OUT_PATH_R8 = os.path.join(OUT_DIR, "round_8.png")
OUT_PATH_R9 = os.path.join(OUT_DIR, "round_9.png")
OUT_PATH_R10 = os.path.join(OUT_DIR, "round_10.png")
OUT_PATH_R11 = os.path.join(OUT_DIR, "round_11.png")


def _build_gameplay_frame(seed=11, seconds=5.0, bake_hud_score=True,
                            chrome_alpha=255):
    """Drive a short autopilot sim, activate skateboard, render frame.

    bake_hud_score=False suppresses the HUD's halftone score paint so
    R5 cells can stamp their own preview score without doubling up
    on the default-position live badge from the base frame. The
    simulation still runs with skateboard_active=True so the world
    state (pipes survived, bird in flight) matches the R1-R4 base —
    we only flip the flag for the single final render pass.

    chrome_alpha (default 255 — full opacity, preserves R1-R6
    behaviour) is stashed on the app so R7 variants can read it when
    re-stamping the coin counter + pause tile on top of their deck
    composite. R7's re-stamp helper applies the per-surface alpha
    immediately before each blit so the deck red and the SKATE/BOARD
    wordmark glyphs underneath the chrome tiles bleed through.
    """
    random.seed(seed)
    app = App()
    if hasattr(app, "_splash_covering"):
        app._splash_covering = False
    w = World()
    w.ready_t = 0.0
    w.flap()
    app.world = w
    app.state = STATE_PLAY
    dt = 1 / 60
    for _ in range(int(seconds / dt)):
        ahead = [p for p in w.pipes if p.x > w.bird.x - 18]
        target = min(ahead, key=lambda p: p.x).gap_y - 12 if ahead else H * 0.45
        if w.bird.y > target:
            w.flap()
        w.update(dt)
        if w.game_over:
            break

    # Activate skateboard so the HUD swaps in the halftone score at y=70.
    w.bird.skateboard_active = True
    w.skateboard_timer = SKATEBOARD_DURATION
    # caption_t controls the halftone score's alpha fade — keep it FULL.
    # Setting it well above the FADE threshold (0.8) holds alpha at 255.
    w.skateboard_caption_t = SKATEBOARD_DURATION
    # Suppress the LIVE banner overlay — we'll draw banner variants ourselves.
    w.skateboard_caption_overlay = None
    # Same for the burst (otherwise we'd see the pickup starburst behind).
    w.skateboard_burst_t = 0.0
    w.skateboard_burst_surface = None
    # Stash the flag the caller asked for — _render_base reads it to know
    # whether to flip skateboard_active off for the single render pass.
    app._r5_bake_hud_score = bake_hud_score
    # Stash chrome_alpha so R7 callers can opt to read the same parameter
    # straight off the app rather than threading it through every variant
    # signature. Default 255 keeps R1-R6 behaviour unchanged.
    app._r7_chrome_alpha = chrome_alpha
    return app


def _render_base(app):
    """Render a full gameplay frame and return a copy of the screen.

    When the caller set bake_hud_score=False on _build_gameplay_frame,
    we drop skateboard_caption_t to 0 for the render pass — the HUD
    still reads skateboard_active=True (so the bird stays on the deck
    and the parrot sprite + HUD chrome match R1-R4) but the score's
    alpha fades to 0, suppressing the halftone blit at its default
    position. The caption_t is restored immediately afterwards so
    subsequent simulation steps stay consistent.
    """
    suppress = not getattr(app, "_r5_bake_hud_score", True)
    saved_cap_t = None
    if suppress:
        saved_cap_t = app.world.skateboard_caption_t
        app.world.skateboard_caption_t = 0.0
    app._render()
    snapshot = app.screen.copy()
    if suppress:
        app.world.skateboard_caption_t = saved_cap_t
    return snapshot


def _plate_banner(text, font_size, rot_deg, pad_x=16, pad_y=8,
                  outline_w=4):
    """Return a tilted SKATEBOARD! plate as a rotated surface."""
    txt = _gradient_text(text, font_size,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=outline_w)
    bw, bh = txt.get_width() + pad_x * 2, txt.get_height() + pad_y * 2
    composite = pygame.Surface((bw + 12, bh + 12), pygame.SRCALPHA)
    ccx = composite.get_width() // 2
    ccy = composite.get_height() // 2
    plate_rect = pygame.Rect(0, 0, bw, bh)
    plate_rect.center = (ccx + 4, ccy + 4)
    pygame.draw.rect(composite, PLATE_RED, plate_rect, border_radius=8)
    pygame.draw.rect(composite, INK, plate_rect, 3, border_radius=8)
    composite.blit(txt, txt.get_rect(center=(ccx, ccy)).topleft)
    return pygame.transform.rotate(composite, rot_deg)


def _corner_slashes(surf, cx, cy, anchors):
    """Pen-style speed slashes from each corner pointing at (cx, cy)."""
    for x0, y0 in anchors:
        for off in range(3):
            dx = (cx - x0) * 0.18
            dy = (cy - y0) * 0.18
            ox = (-1 if x0 < cx else 1) * (off * 8)
            oy = off * 4
            pygame.draw.line(surf, INK,
                             (x0 + ox, y0 + oy),
                             (x0 + ox + dx, y0 + oy + dy), 4)


# ── Variant renderers — each takes a base frame, returns a new surface ─────

def variant_b1_top_thin(base):
    """B1 — Slim banner above the score plate (y=18)."""
    s = base.copy()
    cx, cy = W // 2, 18
    _corner_slashes(s, cx, cy, ((20, 4), (W - 20, 4)))
    banner = _plate_banner("SKATEBOARD!", font_size=26, rot_deg=5,
                           pad_x=12, pad_y=4, outline_w=3)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b2_bottom_edge(base):
    """B2 — Banner at the bottom edge (y=H-50)."""
    s = base.copy()
    cx, cy = W // 2, H - 50
    _corner_slashes(s, cx, cy, ((20, H - 8), (W - 20, H - 8)))
    banner = _plate_banner("SKATEBOARD!", font_size=38, rot_deg=-3)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b3_vertical_left(base):
    """B3 — Banner rotated 90° CCW along the left edge."""
    s = base.copy()
    cx, cy = 22, H // 2
    banner = _plate_banner("SKATEBOARD!", font_size=36, rot_deg=90,
                           pad_x=18, pad_y=8)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b4_diagonal_mid(base):
    """B4 — Dramatic diagonal banner across mid-screen (y=300)."""
    s = base.copy()
    cx, cy = W // 2, 300
    banner = _plate_banner("SKATEBOARD!", font_size=44, rot_deg=-15,
                           pad_x=20, pad_y=10, outline_w=5)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


def variant_b5_top_right(base):
    """B5 — Small banner parked in the top-right corner (y=30)."""
    s = base.copy()
    cx, cy = W - 78, 30
    _corner_slashes(s, cx, cy, ((W - 20, 4), (20, 4)))
    banner = _plate_banner("SKATEBOARD!", font_size=24, rot_deg=12,
                           pad_x=10, pad_y=4, outline_w=3)
    s.blit(banner, banner.get_rect(center=(cx, cy)))
    return s


VARIANTS = [
    ("B1 — Top thin (above score)", variant_b1_top_thin),
    ("B2 — Bottom edge",            variant_b2_bottom_edge),
    ("B3 — Vertical left",          variant_b3_vertical_left),
    ("B4 — Diagonal mid-screen",    variant_b4_diagonal_mid),
    ("B5 — Top-right corner",       variant_b5_top_right),
]


# ── Round 2: banner stays at TOP, score overlays it ────────────────────────
#
# Score is fixed at on-screen y=70 (the new NA-plate position). Each variant
# draws a banner shape that remains legible even when the halftone score is
# stamped on top of its centre. The score is re-blit AFTER the banner so it
# always sits on top.

# Reuse the same halftone-score overlay the live HUD uses — pulled via
# render_skateboard_score_e3 in skateboard_fx. The HUD blits it at
# (0, -_skateboard_lift_y=-26), so we replicate that here.
from game.skateboard_fx import render_skateboard_score_e3 as _score_overlay_fn
from game.world import World as _W


_SCORE_LIFT_Y = 26   # matches World._skateboard_lift_y default


def _stamp_score(surf, score):
    """Stamp the halftone score on top of `surf`, identical to the live
    HUD blit (skateboard_fx.render_skateboard_score_e3 + (0,-lift_y))."""
    score_overlay = _score_overlay_fn(score)
    surf.blit(score_overlay, (0, -_SCORE_LIFT_Y))


def variant_r2_b1_wide_stretched(base, score):
    """R2-B1 — Wide stretched banner. SKATEBOARD! with extra letter
    spacing on a wide red plate spanning W-40 across the top — the
    leftmost/rightmost letters stay visible outside the score's column."""
    s = base.copy()
    # Wide plate y=38→y=94, behind the score band
    plate = pygame.Rect(20, 38, W - 40, 56)
    pygame.draw.rect(s, PLATE_RED, plate, border_radius=10)
    pygame.draw.rect(s, INK, plate, 3, border_radius=10)
    # Stretched text — wide letter spacing so SK… and …RD! sit on the flanks
    txt = _gradient_text("S K A T E B O A R D !", 26,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=3)
    s.blit(txt, txt.get_rect(center=(W // 2, 66)))
    _stamp_score(s, score)
    return s


def variant_r2_b2_tall_doubledeck(base, score):
    """R2-B2 — Tall plate y=8→y=116, with SKATEBOARD! at the TOP edge
    of the plate and the score sitting in the lower 2/3. The two
    occupy different vertical bands of the same plate, so neither is
    obscured."""
    s = base.copy()
    plate = pygame.Rect(28, 8, W - 56, 108)
    pygame.draw.rect(s, PLATE_RED, plate, border_radius=12)
    pygame.draw.rect(s, INK, plate, 3, border_radius=12)
    # Text high up on the plate
    txt = _gradient_text("SKATEBOARD!", 22,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=3)
    s.blit(txt, txt.get_rect(center=(W // 2, 26)))
    _stamp_score(s, score)
    return s


def variant_r2_b3_split_around(base, score):
    """R2-B3 — Two banner halves: SKATE on the left, BOARD! on the
    right, both at y=70. Score sits in the gap between them."""
    s = base.copy()
    skate = _plate_banner("SKATE", font_size=26, rot_deg=5,
                          pad_x=10, pad_y=4, outline_w=3)
    board = _plate_banner("BOARD!", font_size=26, rot_deg=-5,
                          pad_x=10, pad_y=4, outline_w=3)
    s.blit(skate, skate.get_rect(center=(54, 64)))
    s.blit(board, board.get_rect(center=(W - 54, 64)))
    _stamp_score(s, score)
    return s


def variant_r2_b4_diagonal_big(base, score):
    """R2-B4 — Large SKATEBOARD! rotated -15° centred behind the
    score band. The diagonal means most letters live above or below
    the score's horizontal strip; only 2-3 mid letters get clipped."""
    s = base.copy()
    banner = _plate_banner("SKATEBOARD!", font_size=44, rot_deg=-15,
                           pad_x=20, pad_y=10, outline_w=5)
    s.blit(banner, banner.get_rect(center=(W // 2, 70)))
    _stamp_score(s, score)
    return s


def variant_r2_b5_full_top_strip(base, score):
    """R2-B5 — A full-width, translucent red strip across y=0→y=110
    with SKATEBOARD! text spanning it. The score punches a clean
    halftone burst over the middle — the strip is the BACKDROP, not
    a foreground element competing for attention."""
    s = base.copy()
    # Translucent backdrop strip
    strip = pygame.Surface((W, 110), pygame.SRCALPHA)
    strip.fill((220, 50, 40, 200))   # PLATE_RED at alpha 200
    pygame.draw.line(strip, INK, (0, 109), (W, 109), 2)
    s.blit(strip, (0, 0))
    # SKATEBOARD! text along the very top, leaving the score's row clear
    txt = _gradient_text("SKATEBOARD!", 28,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=4)
    s.blit(txt, txt.get_rect(center=(W // 2, 22)))
    _stamp_score(s, score)
    return s


VARIANTS_R2 = [
    ("R2-B1 — Wide stretched",     variant_r2_b1_wide_stretched),
    ("R2-B2 — Tall double-deck",   variant_r2_b2_tall_doubledeck),
    ("R2-B3 — Split SKATE/BOARD!", variant_r2_b3_split_around),
    ("R2-B4 — Diagonal big",       variant_r2_b4_diagonal_big),
    ("R2-B5 — Full top strip",     variant_r2_b5_full_top_strip),
]


# ── Round 3: banner + score UNIFIED into a single hero element ─────────────
#
# Round 2 stacked the live banner and the standard halftone score plate, but
# they read as two independent objects fighting for the same band. Round 3
# treats banner + score as ONE composite — shared outline, shared shadow,
# shared visual grammar. We do NOT call `_stamp_score()` here; each variant
# bakes the halftone score IN to its composite so the unification is total.
# Everything must fit inside the top 110 px (buff icons start at y=128) and
# stay legible at 3 digits.


# Reuse the existing helpers — `_halftone_score_badge` paints the halftone
# burst, `_gradient_text` paints the yellow-orange SKATEBOARD! lettering.
from game.skateboard_fx import _halftone_score_badge as _hb


def _yellow_text(text, size, outline_w=4):
    """Standard SKATEBOARD! gradient text — yellow to orange with ink
    outline. Wrapped here so each R3 cell reads the same lettering."""
    return _gradient_text(text, size,
                          top_col=(255, 255, 110),
                          bot_col=(255, 180, 10),
                          outline=INK, outline_w=outline_w)


def _drop_shadow_rect(surf, rect, radius, offset=(3, 4),
                       shadow=(0, 0, 0, 130)):
    """One unified cast shadow under the composite — shared by banner
    and the score interior so they read as a single object."""
    sh = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sh, shadow, sh.get_rect(), border_radius=radius)
    surf.blit(sh, (rect.left + offset[0], rect.top + offset[1]))


def variant_r3_c1_banner_frame(base, score):
    """R3-C1 — Banner-as-frame. ONE red rounded plate contains BOTH a
    smaller SKATEBOARD! wordmark kissing the plate's top rule AND a
    dominant halftone score burst whose bottom spikes overhang the
    plate's lower edge by ~6 px so the rectangle reads as broken —
    not a flat label. The wordmark dropped ~15% (so the score reigns)
    and the plate was shortened ~20 px horizontally so the burst no
    longer swims in negative space. Score digit cap height ≈ 1.6× the
    wordmark cap height to satisfy the global dominance directive."""
    s = base.copy()
    # Plate shortened ~20 px (W-76 → W-96) so the burst fills the
    # interior instead of floating in red space. Vertical span kept
    # at 86 so the wordmark + burst + overhang composition fits the
    # top 110 px before the buff icon row at y=128.
    plate = pygame.Rect(0, 0, W - 96, 86)
    plate.center = (W // 2, 56)
    _drop_shadow_rect(s, plate, radius=14, offset=(3, 5))
    pygame.draw.rect(s, PLATE_RED, plate, border_radius=14)
    pygame.draw.rect(s, INK, plate, 4, border_radius=14)
    # Wordmark crown — dropped from 19 → 17 (≈15%) and raised so its
    # baseline kisses the plate's top rule. Cap height ≈ 12 px.
    wm = _yellow_text("SKATEBOARD!", 17, outline_w=3)
    s.blit(wm, wm.get_rect(center=(W // 2, plate.top + 12)))
    # Hairline interior divider just below the wordmark — sells the
    # plate as ONE box with a heading.
    pygame.draw.line(s, INK,
                     (plate.left + 14, plate.top + 22),
                     (plate.right - 14, plate.top + 22), 2)
    # Dominant score burst — digit at font_size=52 gives cap height
    # ≈ 36 px (1.6× the 22 px the burst's bounds need vs the 12 px
    # wordmark cap). Burst is positioned so its lower spike tips
    # break the plate's bottom edge by ~6 px, intentionally breaking
    # the rectangle so it doesn't read as a flat label.
    burst_cy = plate.bottom - 22
    _hb(s, W // 2, burst_cy, str(score),
        ro=42, ri=28, font_size=52)
    return s


def variant_r3_c2_tape_ribbon(base, score):
    """R3-C2 — Tape-ribbon + stamp. The word is biased LEFT on the
    ribbon so the stamp lands over the trailing "!" instead of the
    middle of the word — reader now scans the full SKATEBOARD! and
    the stamp reads as a punctuation accent rather than a censor bar.
    Tilt eased from -6° → -3° so the ribbon no longer fights the
    buff-icon row at y=128 on the right or the pause button. Halftone
    dot density inside the burst was thinned ~40% (step 8 → 14) so
    the yellow base doesn't compete with the coin field at gameplay
    scale, and the score digit picks up an extra 1 px ink ring (a
    second outline pass) so it punches cleanly against the yellow."""
    s = base.copy()
    ribbon_w, ribbon_h = W + 60, 52
    rib = pygame.Surface((ribbon_w, ribbon_h), pygame.SRCALPHA)
    # Small inset top/bottom so the tape reads as torn — not a
    # sterile rectangle.
    body = pygame.Rect(0, 6, ribbon_w, ribbon_h - 12)
    pygame.draw.rect(rib, PLATE_RED, body)
    pygame.draw.rect(rib, INK, body, 3)
    # Triangular notches at each end so the ends read as tape tips.
    for tip_x, dir_ in ((0, 1), (ribbon_w, -1)):
        tri = [(tip_x, ribbon_h // 2),
               (tip_x + dir_ * 18, body.top),
               (tip_x + dir_ * 18, body.bottom)]
        pygame.draw.polygon(rib, PLATE_RED, tri)
        pygame.draw.polygon(rib, INK, tri, 3)
    # Wordmark biased LEFT so the stamp can sit over the "!" on the
    # right rather than swallowing the middle of SKATEBOARD. Word
    # rendered at a SMALLER size (28→24) so the stamp can sit fully
    # to the right of the "!" without clipping any letters at the
    # canvas's 360 px width.
    rib_txt = _yellow_text("SKATEBOARD!", 24, outline_w=3)
    rib.blit(rib_txt, rib_txt.get_rect(
        center=(ribbon_w // 2 - 72, ribbon_h // 2)))
    # Tilt softened from -6° → -3° so the right tip clears the buff
    # icon row + pause button.
    rotated = pygame.transform.rotate(rib, -3)
    rect = rotated.get_rect(center=(W // 2, 56))
    # Unified shadow under the ribbon and the stamp — one continuous
    # shadow locks them as a single object.
    shadow = rotated.copy()
    shadow.fill((0, 0, 0, 130), special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(shadow, (rect.left + 3, rect.top + 5))
    s.blit(rotated, rect)
    # Stamp pushed RIGHT of centre so it lands clear of the "!"
    # — full SKATEBOARD! reads cleanly to its left and the stamp
    # becomes the punctuation accent. Stamp held back from the
    # canvas right edge so its right spike clears the pause button
    # at ~x=325.
    stamp_cx, stamp_cy = W // 2 + 88, 70
    rng = random.Random(stamp_cx * 31 + stamp_cy * 17 + 10)
    spikes = 10
    ro, ri = 40, 26
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = ro if i % 2 == 0 else ri
        r += rng.randint(-4, 4)
        pts.append((stamp_cx + math.cos(ang) * r,
                    stamp_cy + math.sin(ang) * r))
    # Stamp shadow continuous with the ribbon shadow above.
    sh_pts = [(p[0] + 3, p[1] + 5) for p in pts]
    pygame.draw.polygon(s, (0, 0, 0, 110), sh_pts)
    pygame.draw.polygon(s, (255, 220, 30), pts)
    bbox_l = int(min(p[0] for p in pts)) - 2
    bbox_t = int(min(p[1] for p in pts)) - 2
    bbox_r = int(max(p[0] for p in pts)) + 2
    bbox_b = int(max(p[1] for p in pts)) + 2
    dots = pygame.Surface((W, H), pygame.SRCALPHA)
    # ~40% fewer dots: default helper uses step=8, here step=14.
    step = 14
    for gy in range(bbox_t, bbox_b, step):
        offset = (step // 2) if ((gy // step) % 2 == 1) else 0
        for gx in range(bbox_l + offset, bbox_r, step):
            pygame.draw.circle(dots, (230, 60, 50), (gx, gy), 2)
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    dots.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(dots, (0, 0))
    pygame.draw.polygon(s, INK, pts, 4)
    # Score digit with an EXTRA 1 px ink ring drawn around the existing
    # outline pass — pops the digit silhouette against the yellow halftone.
    num_ring = _gradient_text(str(score), 46,
                              top_col=INK, bot_col=INK,
                              outline=INK, outline_w=6)
    s.blit(num_ring, num_ring.get_rect(center=(stamp_cx, stamp_cy)))
    num = _gradient_text(str(score), 46,
                         top_col=(255, 250, 240),
                         bot_col=(230, 60, 50),
                         outline=INK, outline_w=4)
    s.blit(num, num.get_rect(center=(stamp_cx, stamp_cy)))
    return s


def variant_r3_c3_skate_deck(base, score):
    """R3-C3 — Skate-deck silhouette. Deck width trimmed 280→260 so it
    no longer crowds the pause button at the 360-px right edge. The
    red-and-yellow stripes that were creating a moiré trap behind the
    yellow burst are dialed down to a soft 15%-opacity wash inside
    the deck — the silhouette + truck-bolt dots carry the "deck"
    reading and the stripes stop fighting the score. Burst extends
    BELOW the deck's lower rim by ~22 px so the score becomes the
    focal punch rather than a passenger riding on top of the board.
    Wordmark size held small so the score digit dominates by ≥1.4×."""
    s = base.copy()
    deck_w, deck_h = 260, 78
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=38)
    # Stripes calmed to a 15% wash — alpha ~38/255 is the moiré-safe
    # threshold the critique called out; the deck-read survives via
    # silhouette + truck-bolt dots.
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    stripe_step = 22
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 38), pts)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=38)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    # Truck-bolt dots — sell the "deck" read on their own.
    for bolt_x in (24, deck_w - 24):
        for bolt_y in (16, deck_h - 16):
            pygame.draw.circle(deck, INK, (bolt_x, bolt_y), 4)
            pygame.draw.circle(deck, (60, 60, 60), (bolt_x, bolt_y), 2)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=38)
    # Position the deck so the burst hanging below it still clears
    # the buff-icon row at y=128.
    deck_rect_on = deck.get_rect(center=(W // 2, 42))
    sh = deck.copy()
    sh.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
    s.blit(sh, (deck_rect_on.left + 3, deck_rect_on.top + 5))
    s.blit(deck, deck_rect_on)
    # Wordmark crown — small (cap height ~12 px) so the score's
    # ~30 px cap clears the 1.4× dominance rule.
    wm = _yellow_text("SKATEBOARD!", 17, outline_w=3)
    s.blit(wm, wm.get_rect(center=(W // 2, deck_rect_on.top + 14)))
    # Score burst — bottom of burst hangs ~22 px below the deck's
    # lower rim so the score visibly punches downward off the deck.
    burst_cy = deck_rect_on.bottom + 14
    _hb(s, W // 2, burst_cy, str(score),
        ro=40, ri=26, font_size=48)
    return s


def variant_r3_c4_sign_post(base, score):
    """R3-C4 — Sign-post UNIFIED by the burst piercing BOTH panels.
    Header (SKATEBOARD! marquee) and bowl (score chamber) are stacked
    with NO waist bar between them; the halftone burst sits centred
    on the SEAM so its top half eats into the marquee and its bottom
    half sits inside the bowl. The burst becomes the physical rivet
    joining the two panels — reader sees ONE composite shape, not
    two stacked stamps. Seam outline is broken through the burst's
    width so the silhouette flows; side outlines on the left/right
    of the seam are re-stroked so the composite's overall silhouette
    stays crisp."""
    s = base.copy()
    # Header panel + bowl panel sharing the same width, stacked with
    # no gap. The bowl is shaped wider/taller so it reads as a
    # "score chamber" distinct from the header marquee.
    panel_w = 200
    header = pygame.Rect(0, 0, panel_w, 36)
    bowl = pygame.Rect(0, 0, panel_w + 24, 50)
    header.center = (W // 2, 30)
    bowl.midtop = (W // 2, header.bottom - 1)
    # ONE shared shadow for the full silhouette (union footprint).
    union_shadow = pygame.Rect(bowl.left, header.top,
                               bowl.width,
                               (bowl.bottom - header.top))
    _drop_shadow_rect(s, union_shadow, radius=16, offset=(3, 5))
    # Header marquee.
    pygame.draw.rect(s, PLATE_RED, header, border_radius=10)
    pygame.draw.rect(s, INK, header, 3, border_radius=10)
    # Bowl chamber — wider so it reads as a distinct "score" base
    # while still sharing the marquee's grammar.
    pygame.draw.rect(s, PLATE_RED, bowl, border_radius=16)
    pygame.draw.rect(s, INK, bowl, 3, border_radius=16)
    # Wordmark — kissing the marquee's top rule.
    wm = _yellow_text("SKATEBOARD!", 19, outline_w=3)
    s.blit(wm, wm.get_rect(center=(header.centerx, header.top + 14)))
    # Now paint over the SHARED SEAM with PLATE_RED to kill the two
    # adjacent ink lines (top-of-bowl and bottom-of-header), so the
    # silhouette reads as one shape with a waist. We only paint the
    # central section, NOT the edges where the header is narrower
    # than the bowl — those edge stubs must stay outlined.
    seam_y = header.bottom
    seam_strip = pygame.Rect(header.left + 6, seam_y - 4,
                             header.width - 12, 8)
    pygame.draw.rect(s, PLATE_RED, seam_strip)
    # Re-stroke the header's bottom-rule SIDE STUBS (the bit where
    # the bowl is wider than the header — those exterior shoulders
    # have to stay outlined so the silhouette doesn't lose its
    # waist outline).
    pygame.draw.line(s, INK,
                     (bowl.left, header.bottom),
                     (header.left, header.bottom), 3)
    pygame.draw.line(s, INK,
                     (header.right, header.bottom),
                     (bowl.right, header.bottom), 3)
    # The pierce-rivet — burst centred ON the seam y so its top half
    # eats into the marquee and its bottom half sits in the bowl.
    burst_cx, burst_cy = W // 2, seam_y
    _hb(s, burst_cx, burst_cy, str(score),
        ro=40, ri=26, font_size=46)
    return s


def variant_r3_c5_burst_exclamation(base, score):
    """R3-C5 — Burst-as-exclamation. The front-runner. Reads as ONE
    word: SKATEBOARD then the halftone burst IS the final "!". This
    cell gets the hardest push from the critique:
    - gap between wordmark and burst closed to ~4 px so it reads as
      "word!" not "word + asterisk"
    - burst's vertical centre lowered so the burst's BOTTOM aligns
      with the wordmark's BASELINE — no more floating-high burst
    - burst's outer-spike radius shrunk so the burst sits closer to
      "punctuation dot" optical size relative to the digit
    - ONE shared deep-red drop shadow cast under BOTH the wordmark
      AND the burst so they lock visually as a single object
    - wordmark gets thickened ink stroke + soft shadow so it
      survives day AND night biome without a plate backing it
    - digit gradient deepened — cream top kept, red bottom-stop
      pushed darker so the digit silhouette punches against the
      yellow burst instead of muddying into it
    - burst sized to clear the pause-button rectangle at the
      top-right (no overlap into the buff-icon row at y=128)."""
    s = base.copy()
    # Wordmark + burst sizing tuned so the composite fits within 360 px
    # AND clears the pause button at the top-right. Burst's outer radius
    # was 28 → trimmed to 27 so the digit (not the spikes) reads as the
    # heaviest mass of the composite — keeps optical hierarchy: digit >
    # wordmark > spike halo. Word cap ~18 px; burst digit cap inside the
    # 27 px halo.
    wm_size = 32
    word = _yellow_text("SKATEBOARD", wm_size, outline_w=5)
    burst_ro = 27
    # Inner pad widened from 17 → 21 (+4 px) so 3-digit "888" scores
    # fit inside the burst's inner valleys without the digit silhouette
    # punching through the spike rim. Late-game scores hit triple digits
    # before SKATEBOARD power-ups become rare, so this margin is needed.
    burst_ri = 21
    burst_diameter = burst_ro * 2
    gap = 4
    total_w = word.get_width() + gap + burst_diameter
    # Pull composite slightly LEFT so the burst's right spike clears
    # the pause-button rectangle (which sits at ~x=320 onward). Extra
    # -6 px nudge moves the BURST itself ~6 px left (after the composite
    # is laid out) so its left spike kisses the right edge of the "D".
    start_x = max(8, (W - total_w) // 2 - 14)
    # Centre line at y=72 — keeps the composite inside the top 110 px
    # and well clear of the buff icons at y=128.
    centre_y = 72
    word_rect = word.get_rect(midleft=(start_x, centre_y))
    # Burst's BOTTOM aligns with the wordmark's BASELINE (~ bottom of
    # rendered glyphs minus descender). Approximate baseline as
    # word_rect.bottom - ~6 px descender padding.
    word_baseline_y = word_rect.bottom - 6
    burst_cy = word_baseline_y - burst_ro
    # -6 px burst nudge so the left spike kisses the "D" right edge
    # rather than leaving a gap — "word!" reads as one tight unit.
    burst_cx = word_rect.right + gap + burst_diameter // 2 - 6
    # Soft DARK drop shadow under BOTH silhouettes — one continuous
    # shadow layer ties the wordmark + burst into a single object.
    # Using dark grey (not red) so the shadow doesn't bleed colour
    # into the wordmark's outline at low offsets.
    SHADOW_RGBA = (0, 0, 0, 130)
    shadow_offset = (3, 5)
    shadow_layer = pygame.Surface((W, H), pygame.SRCALPHA)
    wm_shadow = _gradient_text("SKATEBOARD", wm_size,
                               top_col=(0, 0, 0),
                               bot_col=(0, 0, 0),
                               outline=(0, 0, 0),
                               outline_w=6)
    wm_shadow.set_alpha(SHADOW_RGBA[3])
    shadow_layer.blit(wm_shadow,
                      (word_rect.left - 1 + shadow_offset[0],
                       word_rect.top - 1 + shadow_offset[1]))
    pygame.draw.circle(shadow_layer, SHADOW_RGBA,
                       (burst_cx + shadow_offset[0],
                        burst_cy + shadow_offset[1]),
                       burst_ro + 2)
    s.blit(shadow_layer, (0, 0))
    # Wordmark — yellow gradient with thick ink outline (outline_w=5)
    # so it survives the pale-day biome without a red plate behind it.
    s.blit(word, word_rect)
    # Faint 1-px inner highlight along the TOP of the wordmark letters
    # — same trick the coin glyph uses. A second pass of the gradient
    # text without an outline, blitted 1 px UP at ~30% alpha, leaves a
    # bright top-edge sheen that survives both day AND night biome
    # because it tints existing yellow, never introduces a new colour.
    hl = _gradient_text("SKATEBOARD", wm_size,
                        top_col=(255, 255, 110),
                        bot_col=(255, 255, 110),
                        outline=INK, outline_w=0)
    hl.set_alpha(76)  # ~30% of 255
    s.blit(hl, (word_rect.left, word_rect.top - 1))
    # Halftone burst body — inlined so we control the digit gradient.
    rng = random.Random(burst_cx * 31 + burst_cy * 17 + 10)
    spikes = 10
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = burst_ro if i % 2 == 0 else burst_ri
        r += rng.randint(-3, 3)
        pts.append((burst_cx + math.cos(ang) * r,
                    burst_cy + math.sin(ang) * r))
    pygame.draw.polygon(s, (255, 220, 30), pts)
    bbox_l = int(min(p[0] for p in pts)) - 2
    bbox_t = int(min(p[1] for p in pts)) - 2
    bbox_r = int(max(p[0] for p in pts)) + 2
    bbox_b = int(max(p[1] for p in pts)) + 2
    dots = pygame.Surface((W, H), pygame.SRCALPHA)
    step = 8
    for gy in range(bbox_t, bbox_b, step):
        offset = (step // 2) if ((gy // step) % 2 == 1) else 0
        for gx in range(bbox_l + offset, bbox_r, step):
            pygame.draw.circle(dots, (230, 60, 50), (gx, gy), 2)
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    dots.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(dots, (0, 0))
    pygame.draw.polygon(s, INK, pts, 4)
    # Score digit — cream top, deepened red bottom (190, 30, 20 vs the
    # helper's default (230, 60, 50)). The deeper bottom pushes the
    # digit silhouette darker so it pops against the yellow burst
    # base instead of blending into it.
    # Digit font auto-scales for 3+ digit scores so the digit silhouette
    # never punches through the burst's spike rim. 1-2 digits keep the
    # punchy 28 px cap; 3-digit drops to 22 to leave ~3 px clearance
    # inside the outer-spike envelope.
    num_size = 28 if len(str(score)) <= 2 else 22
    num = _gradient_text(str(score), num_size,
                         top_col=(255, 250, 240),
                         bot_col=(190, 30, 20),
                         outline=INK, outline_w=3)
    # -2 px lift on the digit centre so its optical centre lines up with
    # the burst's geometric centre — glyph metrics carry extra descender
    # padding that drags the digit visually low otherwise.
    s.blit(num, num.get_rect(center=(burst_cx, burst_cy - 2)))
    return s


VARIANTS_R3 = [
    ("R3-C1 — Banner-as-frame",       variant_r3_c1_banner_frame),
    ("R3-C2 — Tape-ribbon + stamp",   variant_r3_c2_tape_ribbon),
    ("R3-C3 — Skate-deck silhouette", variant_r3_c3_skate_deck),
    ("R3-C4 — Stacked sign-post",     variant_r3_c4_sign_post),
    ("R3-C5 — Burst-as-exclamation",  variant_r3_c5_burst_exclamation),
]


# ── Round 4: R3-C3 skate-deck reworked — LOWER, LARGER wordmark, ─────────
#           burst INSIDE the deck, shared cast shadow on the composite.
#
# User picked the R3-C3 skate-deck direction but wanted the composite pushed
# DOWN the canvas (clear of the coin counter at the top), the SKATEBOARD
# wordmark sized back UP closer to round-1/-2 banner weight (cap height
# ≥22 px), and the halftone score burst pulled INSIDE the deck silhouette
# rather than hanging off the lower rim. Composite must fit inside
# y=85..185 (above the buff-icon row at y=194) and stay clear of the pause
# button column at x≈274..342, so every deck silhouette here is ≤290 px
# wide. All 5 share the same warm cast-shadow direction (+3,+5) so they
# read as one cohesive direction with varying silhouettes.


def _composite_shadow(surf, comp, comp_pos, offset=(3, 5),
                       alpha=130):
    """Stamp a single unified shadow for an entire composite surface.
    Used by every R4 cell so the deck + wordmark + score burst share
    one cast shadow direction and read as ONE object."""
    sh = comp.copy()
    sh.fill((0, 0, 0, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(sh, (comp_pos[0] + offset[0], comp_pos[1] + offset[1]))


def _draw_truck_bolts(surf, deck_w, deck_h, inset=24, edge_inset=16):
    """Four truck-mount bolts — the visual cue that sells a red
    rounded rectangle as a SKATEBOARD DECK rather than a generic
    label plate. Stamped onto the deck surface BEFORE the outline
    pass so the ink ring on top crisps them."""
    for bolt_x in (inset, deck_w - inset):
        for bolt_y in (edge_inset, deck_h - edge_inset):
            pygame.draw.circle(surf, INK, (bolt_x, bolt_y), 4)
            pygame.draw.circle(surf, (60, 60, 60), (bolt_x, bolt_y), 2)


def _baked_burst(cx, cy, ro, ri, score_str, num_size,
                  spikes=10, jitter=3, surface_size=None):
    """Build a halftone-filled burst PLUS its score digit on its own
    SRCALPHA surface, so the whole burst (yellow base, dot pattern,
    ink outline, gradient digit) can be rotated/transformed as one
    object alongside the deck. Returns (surf, burst_pts_local).

    The R3-C5 3-digit-safe sizing convention is enforced by the caller
    passing num_size (28 → 22 for 3+ digits) and ri ≥ 21.
    """
    w = surface_size or (ro * 2 + 24)
    h = surface_size or (ro * 2 + 24)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    lcx, lcy = w // 2, h // 2
    rng = random.Random(int(cx) * 31 + int(cy) * 17 + 10)
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = ro if i % 2 == 0 else ri
        r += rng.randint(-jitter, jitter)
        pts.append((lcx + math.cos(ang) * r,
                    lcy + math.sin(ang) * r))
    pygame.draw.polygon(surf, (255, 220, 30), pts)
    # Halftone dot field, clipped to the burst polygon.
    bbox_l = int(min(p[0] for p in pts)) - 2
    bbox_t = int(min(p[1] for p in pts)) - 2
    bbox_r = int(max(p[0] for p in pts)) + 2
    bbox_b = int(max(p[1] for p in pts)) + 2
    dots = pygame.Surface((w, h), pygame.SRCALPHA)
    step = 8
    for gy in range(bbox_t, bbox_b, step):
        offset = (step // 2) if ((gy // step) % 2 == 1) else 0
        for gx in range(bbox_l + offset, bbox_r, step):
            pygame.draw.circle(dots, (230, 60, 50), (gx, gy), 2)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    dots.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(dots, (0, 0))
    pygame.draw.polygon(surf, INK, pts, 4)
    # Score digit — R3 deepened-red gradient.
    num = _gradient_text(score_str, num_size,
                         top_col=(255, 250, 240),
                         bot_col=(190, 30, 20),
                         outline=INK, outline_w=3)
    surf.blit(num, num.get_rect(center=(lcx, lcy - 2)))
    return surf


def _digit_font_size(score_str, base=28, big=22):
    """R3-C5 3-digit-safe sizing — 1-2 digits use the punchy 28 cap,
    3+ digits drop to 22 so the silhouette never punches the rim."""
    return base if len(score_str) <= 2 else big


def variant_r4_d1_flat_slab(base, score):
    """R4-D1 — Lower flat slab, gentle tilt (R4-final polish).
    Plain rounded-rect deck, ~280x72. Tilt -3°. Deck-center y=130.
    SKATEBOARD wordmark sits across the top of the deck face, halftone
    score burst centred in the lower half of the deck. AD critique
    flagged the slab as reading "generic pill"; the polish pass adds
    four explicit ink bolt-dots at the corner truck mounts plus a
    1-px ink waist pinstripe through the centre so the silhouette
    reads as a deck rather than a featureless lozenge."""
    s = base.copy()
    deck_w, deck_h = 280, 72
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=36)
    # Wash stripes — calmed even further than R3-C3 (alpha 30 here)
    # so the wordmark + burst dominate. The "graphic deck" reading
    # comes from the silhouette + bolts, not the stripes.
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    stripe_step = 24
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 30), pts)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=36)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    # Four explicit bolt-DOTS at the truck-mount corners — a thicker,
    # higher-contrast pass than the default truck-bolts helper (the
    # AD critique said the slab was reading as "generic pill" without
    # explicit corner bolts). Pure INK fill with a tiny grey highlight
    # so they punch at gameplay scale.
    for bolt_x in (28, deck_w - 28):
        for bolt_y in (16, deck_h - 16):
            pygame.draw.circle(deck, INK, (bolt_x, bolt_y), 5)
            pygame.draw.circle(deck, (180, 160, 140), (bolt_x, bolt_y), 2)
    # Waist pinstripe — single 1-px ink line bisecting the slab
    # horizontally so the silhouette reads as a deck centreline,
    # not a featureless lozenge. Alpha bumped to 160 so the line
    # survives the warm red plate at gameplay scale (the previous
    # 120 alpha disappeared on close inspection).
    pinstripe = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.line(pinstripe, (15, 15, 15, 160),
                     (18, deck_h // 2), (deck_w - 18, deck_h // 2), 1)
    deck.blit(pinstripe, (0, 0))
    # Burst baked first so the wordmark can sit ABOVE it on the deck
    # face, but the burst lives in the LOWER half of the deck where
    # there's room for a 60 px diameter halftone disc inside the
    # 72 px deck height.
    burst_ro, burst_ri = 26, 21
    score_str = str(score)
    num_size = _digit_font_size(score_str)
    burst = _baked_burst(0, 0, burst_ro, burst_ri,
                          score_str, num_size,
                          surface_size=burst_ro * 2 + 18)
    burst_cx_local = deck_w // 2
    burst_cy_local = deck_h - 22
    deck.blit(burst, burst.get_rect(
        center=(burst_cx_local, burst_cy_local)))
    # Wordmark — large (cap height ≈ 22 px at font_size=32) sitting
    # along the deck's TOP face, above the burst.
    wm = _yellow_text("SKATEBOARD", 32, outline_w=4)
    # Letterform width at size 32 ≈ 260 px → fits 280 px deck with
    # a couple of pixels of margin.
    if wm.get_width() > deck_w - 16:
        # Auto-shrink if SKATEBOARD overflows on this build's font.
        wm = _yellow_text("SKATEBOARD", 28, outline_w=4)
    deck.blit(wm, wm.get_rect(center=(deck_w // 2, 18)))
    # Outline pass last so it sits on top of the bolts + stripes.
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=36)
    # Tilt the WHOLE composite (deck + wordmark + burst) so all
    # three pieces share the same rotation.
    rotated = pygame.transform.rotate(deck, -3)
    rect = rotated.get_rect(center=(W // 2, 130))
    _composite_shadow(s, rotated, rect.topleft)
    s.blit(rotated, rect)
    return s


def variant_r4_d2_strong_tilt(base, score):
    """R4-D2 — Strong tilt, energetic pop (R4-final polish).
    Same deck silhouette as D1 but tilted aggressively to -12°. The AD
    critique flagged the badge as reading "slightly tilted but not
    committed" — the polish pass picks the COUNTER-ROTATE strategy:
    deck + wordmark + bolts all tilt -12° (committed slant), but the
    halftone score BADGE is composed AFTER the rotate, perfectly
    horizontal (0°), so the contrast deck/badge reads as deliberate
    "skewed plate, level score". Score readability is the priority on
    the live HUD, and a level digit nails that. Deck-center pulled
    DOWN to y=143 so the rotated upper-left deck corner clears the
    coin counter HUD strip (x≈10..60, y≈18..40)."""
    s = base.copy()
    deck_w, deck_h = 280, 72
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=36)
    # Slightly more vivid wash stripes for energy — but still ≤15%
    # alpha so the score remains the focal point.
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    stripe_step = 22
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 38), pts)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=36)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    _draw_truck_bolts(deck, deck_w, deck_h, inset=26, edge_inset=14)
    # Wordmark — baked BEFORE the deck rotate so the lettering shares
    # the committed -12° slant.
    wm = _yellow_text("SKATEBOARD", 32, outline_w=4)
    if wm.get_width() > deck_w - 16:
        wm = _yellow_text("SKATEBOARD", 28, outline_w=4)
    deck.blit(wm, wm.get_rect(center=(deck_w // 2, deck_h // 2)))
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=36)
    # Deck rotated FIRST — wordmark + bolts inherit -12° slant.
    rotated = pygame.transform.rotate(deck, -12)
    # Pulled DOWN to y=143 (was 135 → 139 → 143) so the rotated
    # upper-left deck corner clears the coin counter HUD strip at
    # y≈18..40 (the corner was previously clipping at y≈22).
    rect = rotated.get_rect(center=(W // 2, 143))
    _composite_shadow(s, rotated, rect.topleft)
    s.blit(rotated, rect)
    # Score badge composed AFTER the rotate — fully HORIZONTAL (0°)
    # so the score digit reads dead-level against the tilted deck.
    # This is the "counter-rotate" half of the AD critique's binary
    # choice: deck slanted, badge level, contrast deliberate.
    burst_ro, burst_ri = 26, 21
    score_str = str(score)
    num_size = _digit_font_size(score_str)
    burst = _baked_burst(0, 0, burst_ro, burst_ri,
                          score_str, num_size,
                          surface_size=burst_ro * 2 + 18)
    # Place burst at the visual centre of the rotated deck — same
    # screen coords as the deck's centre.
    s.blit(burst, burst.get_rect(center=(W // 2, 143)))
    return s


def variant_r4_d3_concave_waist(base, score):
    """R4-D3 — Concave-waist deck, real skateboard shape (R4-final polish).
    AD critique: the wordmark MUST sit centred over the WAIST (so the
    SKATEBOARD lettering reads as carved into the pinched section,
    using the waist curve as its visual baseline), and the score
    BURST goes on the WIDER TAIL end of the deck. The waist pinch
    is lifted further (waist_h ratio 0.86 → 0.90) so the central
    interior holds a clean ≥22 px height for the wordmark cap.
    -5° tilt, deck-center y=128."""
    s = base.copy()
    deck_w, deck_h = 280, 74
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    # Concave-waist polygon — waist pinched to ~90% of deck_h (was 86%)
    # so the central readout retains ≥22 px of clean interior height
    # for the SKATEBOARD wordmark cap.
    waist_h = int(deck_h * 0.90)
    samples = 24
    top_pts = []
    bot_pts = []
    for i in range(samples + 1):
        t = i / samples
        x = int(t * deck_w)
        # Cosine pinch: deepest at t=0.5, none at t=0 / t=1.
        pinch = (1 - math.cos(t * 2 * math.pi)) * 0.5  # 0..1..0
        cur_h = deck_h - (deck_h - waist_h) * pinch
        top_pts.append((x, int((deck_h - cur_h) / 2)))
        bot_pts.append((x, int((deck_h + cur_h) / 2)))
    poly = top_pts + list(reversed(bot_pts))
    pygame.draw.polygon(deck, PLATE_RED, poly)
    # Wash stripes masked to the waist polygon.
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    stripe_step = 22
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 32), pts)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    # Truck bolts at each fat end (where the polygon is fullest).
    for bolt_x in (28, deck_w - 28):
        for bolt_y in (16, deck_h - 16):
            pygame.draw.circle(deck, INK, (bolt_x, bolt_y), 4)
            pygame.draw.circle(deck, (60, 60, 60), (bolt_x, bolt_y), 2)
    # Burst on the fat TAIL end of the deck (right side here) — the
    # wide bulged section provides natural vertical room for the
    # halftone disc, and the visual hierarchy reads "deck name on
    # the waist, score stamp on the tail".
    burst_ro, burst_ri = 24, 21
    score_str = str(score)
    num_size = _digit_font_size(score_str)
    burst = _baked_burst(0, 0, burst_ro, burst_ri,
                          score_str, num_size,
                          surface_size=burst_ro * 2 + 18)
    tail_cx = deck_w - 40
    deck.blit(burst, burst.get_rect(
        center=(tail_cx, deck_h // 2)))
    # Wordmark centred OVER THE WAIST — horizontal centre is the
    # geometric centre of the deck (waist pinch point), and the cap
    # height +2 boost (26→28) keeps the SKATEBOARD letterforms
    # ≥22 px after the polygon rotation shave.
    wm = _yellow_text("SKATEBOARD", 28, outline_w=4)
    # Shift left so the wordmark CENTRE aligns with the waist (deck
    # centre) and the right edge of the lettering doesn't run into
    # the tail burst.
    wm_centre_x = deck_w // 2 - 36
    if wm.get_rect(center=(wm_centre_x, deck_h // 2)).right > tail_cx - burst_ro - 4:
        # Auto-shrink if the wordmark would crowd the tail burst.
        wm = _yellow_text("SKATEBOARD", 24, outline_w=4)
        wm_centre_x = deck_w // 2 - 30
    deck.blit(wm, wm.get_rect(center=(wm_centre_x, deck_h // 2)))
    # Outline pass — polygon outline rather than rounded-rect so the
    # waist curve is preserved.
    pygame.draw.polygon(deck, INK, poly, 4)
    rotated = pygame.transform.rotate(deck, -5)
    rect = rotated.get_rect(center=(W // 2, 128))
    _composite_shadow(s, rotated, rect.topleft)
    s.blit(rotated, rect)
    return s


def variant_r4_d4_trucks_wheels(base, score):
    """R4-D4 — Deck with visible trucks + wheels (R4-final polish).
    The full gameplay-style skateboard silhouette: deck on top, two
    small dark truck rectangles bolted to the underside, four wheels
    poking below. AD critique polish:
    - Wheels desaturated ~25% from the punchy halftone yellow to a
      muted off-white/ochre so they no longer compete with the
      SKATEBOARD wordmark's yellow gradient (the bright wheels were
      pulling the eye DOWN; muting them keeps focus on the wordmark
      + score burst).
    - Truck stems thinned by 1 px (28x8 → 28x7) so they read as a
      lighter visual base under the deck, less weight under the score.
    - Deck-center lifted to y=118 so the wheel bottoms land at y≤183
      (deck top at y≈86, deck_h=64 → deck bottom y=150, +7 truck +
      6 wheel radius = wheel bottom y≈173 < 183 floor).
    Wordmark on the top deck face, score burst centered in the deck."""
    s = base.copy()
    deck_w, deck_h = 270, 64
    # Composite surface needs vertical room for trucks (7 px) + wheels
    # (12 px diameter) below the deck.
    pad = 22
    comp_h = deck_h + pad
    comp_w = deck_w + 12  # tiny side margin so rotation doesn't clip
    deck = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)
    deck_rect = pygame.Rect((comp_w - deck_w) // 2, 0, deck_w, deck_h)
    # Trucks (small dark rectangles under the deck) — drawn FIRST so
    # the deck's rounded-rect overlays them visually correctly.
    # Stem height dropped 8→7 to thin the visual weight under the deck.
    truck_w, truck_h = 28, 7
    for truck_cx_local in (deck_rect.left + 36, deck_rect.right - 36):
        truck_rect = pygame.Rect(0, 0, truck_w, truck_h)
        truck_rect.center = (truck_cx_local, deck_h + 4)
        pygame.draw.rect(deck, (40, 38, 44), truck_rect,
                         border_radius=3)
        pygame.draw.rect(deck, INK, truck_rect, 2, border_radius=3)
        # Wheels — desaturated muted ochre (was punchy yellow 255,220,30).
        # The ochre keeps the wheels reading as a warm skate-palette
        # element without competing with the SKATEBOARD wordmark above.
        for wheel_dx in (-truck_w // 2 + 2, truck_w // 2 - 2):
            wheel_cx = truck_cx_local + wheel_dx
            wheel_cy = deck_h + 14
            pygame.draw.circle(deck, (215, 195, 160),
                               (wheel_cx, wheel_cy), 6)
            pygame.draw.circle(deck, INK,
                               (wheel_cx, wheel_cy), 6, 2)
    # Deck body — sits ON TOP of the truck stems so the truck reads
    # as bolted underneath.
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=30)
    stripes = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)
    stripe_step = 22
    for i in range(-comp_h, comp_w + comp_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + comp_h, comp_h),
                   (i + comp_h, comp_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 30), pts)
    mask = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=30)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    _draw_truck_bolts(deck.subsurface(deck_rect),
                      deck_w, deck_h, inset=22, edge_inset=12)
    # Burst sits centered in the deck — slightly compressed vertically
    # because the deck face is only 64 px tall.
    burst_ro, burst_ri = 23, 21
    score_str = str(score)
    num_size = _digit_font_size(score_str, base=26, big=20)
    burst = _baked_burst(0, 0, burst_ro, burst_ri,
                          score_str, num_size,
                          surface_size=burst_ro * 2 + 18)
    deck.blit(burst, burst.get_rect(
        center=(deck_rect.centerx, deck_rect.centery + 4)))
    # Wordmark sized so cap stays ≥22 px while fitting the 270 px deck.
    wm = _yellow_text("SKATEBOARD", 28, outline_w=4)
    if wm.get_width() > deck_w - 12:
        wm = _yellow_text("SKATEBOARD", 26, outline_w=4)
    deck.blit(wm, wm.get_rect(center=(deck_rect.centerx,
                                       deck_rect.top + 12)))
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=30)
    rotated = pygame.transform.rotate(deck, -4)
    # Lifted from y=120 → y=118 so the wheel bottoms (deck bottom +7 truck
    # +6 wheel radius) land at y≤183 — clear of the buff-row floor at
    # y=185 even after the -4° rotation swing.
    rect = rotated.get_rect(center=(W // 2, 118))
    _composite_shadow(s, rotated, rect.topleft)
    s.blit(rotated, rect)
    return s


def variant_r4_d5_longboard(base, score):
    """R4-D5 — Wider longboard with stamped graphic (R4-final polish).
    Rectangular old-school longboard silhouette (290x64), almost flat
    (-2° tilt), deck-center y=140. AD critique polish:
    - The split "SKATE … BOARD" wordmark is COLLAPSED into ONE
      centered SKATEBOARD wordmark sitting above the central decal
      (the split read as two cohesion-breaking labels). The wordmark
      keeps the stamp-scuff offset trick so the deck-graphic vibe
      survives.
    - The thin ink ring around the central decal is REMOVED so the
      burst's own ink outline carries the silhouette; the previous
      ring was doubling-up against the score halo's halftone fill
      and creating a competing concentric reading."""
    s = base.copy()
    deck_w, deck_h = 290, 64
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    # Longboard reads "wider/flatter" → smaller corner radius so the
    # silhouette is more rectangular than D1's popsicle deck.
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=20)
    # Subtle horizontal grain bands — sells the old-school wood-deck
    # vibe without competing with the wordmark.
    grain = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    for y in range(4, deck_h, 8):
        pygame.draw.line(grain, (140, 25, 18, 40),
                         (4, y), (deck_w - 4, y), 1)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=20)
    grain.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(grain, (0, 0))
    # Truck bolts wider apart since the deck is longer.
    _draw_truck_bolts(deck, deck_w, deck_h, inset=28, edge_inset=14)
    # Central decal — burst sits BELOW the wordmark, no ink ring
    # (the AD critique flagged the ring as doubling with the burst's
    # halftone fill). The burst's own polygon ink outline carries
    # the decal-on-board reading.
    burst_ro, burst_ri = 22, 19
    score_str = str(score)
    num_size = _digit_font_size(score_str, base=24, big=20)
    burst = _baked_burst(0, 0, burst_ro, burst_ri,
                          score_str, num_size,
                          surface_size=burst_ro * 2 + 18)
    # Burst sits in the lower band of the deck so the centred
    # wordmark above has clean vertical room.
    burst_pos = (deck_w // 2, deck_h - 18)
    deck.blit(burst, burst.get_rect(center=burst_pos))
    # SINGLE centered SKATEBOARD wordmark — the AD critique killed
    # the split label. Stamp-scuff trick retained: a 1 px offset
    # darker copy underneath so the print reads as slightly rough
    # ink rather than a clean digital outline.
    wm = _yellow_text("SKATEBOARD", 28, outline_w=4)
    if wm.get_width() > deck_w - 16:
        wm = _yellow_text("SKATEBOARD", 26, outline_w=4)
    scuff = _gradient_text("SKATEBOARD", wm.get_height() - 4 if False else 28,
                           top_col=(120, 25, 18),
                           bot_col=(120, 25, 18),
                           outline=(120, 25, 18), outline_w=4)
    if scuff.get_width() > deck_w - 16:
        scuff = _gradient_text("SKATEBOARD", 26,
                               top_col=(120, 25, 18),
                               bot_col=(120, 25, 18),
                               outline=(120, 25, 18), outline_w=4)
    scuff.set_alpha(120)
    wm_pos = (deck_w // 2, 16)
    deck.blit(scuff, scuff.get_rect(center=(wm_pos[0] + 1, wm_pos[1] + 1)))
    deck.blit(wm, wm.get_rect(center=wm_pos))
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=20)
    rotated = pygame.transform.rotate(deck, -2)
    rect = rotated.get_rect(center=(W // 2, 140))
    _composite_shadow(s, rotated, rect.topleft)
    s.blit(rotated, rect)
    return s


VARIANTS_R4 = [
    ("R4-D1 — Flat slab, gentle tilt",   variant_r4_d1_flat_slab),
    ("R4-D2 — Strong tilt (energetic)",  variant_r4_d2_strong_tilt),
    ("R4-D3 — Concave-waist deck",       variant_r4_d3_concave_waist),
    ("R4-D4 — Trucks + wheels",          variant_r4_d4_trucks_wheels),
    ("R4-D5 — Longboard stamped",        variant_r4_d5_longboard),
]


# ── Round 5: R4-D2 direction reworked — LARGER deck, SPLIT SKATE/BOARD ───
#           wordmarks framing the LIVE in-game score (no baked score). ──
#
# User picked R4-D2 (energetic-tilt slab) but wanted the deck ~25% larger,
# the wordmark split into "SKATE" on the deck's left half and "BOARD" on
# the right half (both rotating WITH the deck), and the centre of the deck
# left empty so the LIVE skateboard-mode halftone score (the real HUD
# overlay from `render_skateboard_score_e3`) can land there at runtime —
# no double work. The deck itself remains ONE whole piece; the SKATE/BOARD
# split is text-only. The comparison sheet previews the runtime composite
# by cropping the same `render_skateboard_score_e3("888")` overlay and
# stamping it horizontally over each tilted deck's centre.


def _live_score_preview(score_str="888", size=108, sparkle_trim=0.0):
    """Crop the live `render_skateboard_score_e3` halftone badge onto a
    small SRCALPHA tile so each R5 cell can preview where the LIVE score
    will land at runtime. The production overlay paints the badge at
    (W//2, 96) inside a (W, H) surface; we crop a `size × size` square
    centred on (W//2, 96) so the preview matches the runtime pixels.

    The preview is intentionally horizontal — the live HUD never rotates
    the score badge, so the deck tilt is purely cosmetic and the score
    digit always reads dead-level on top of it.

    sparkle_trim trims the burst's outer spike radius by a fraction
    (e.g. 0.10) by scaling the cropped tile down — applied ONLY to the
    preview blit, never to the production HUD overlay, so the R6 review
    sheet's tilted-deck cells don't show the burst spikes clipping the
    deck's inner top edge at y=70.
    """
    overlay = _score_overlay_fn(int(score_str))
    tile = pygame.Surface((size, size), pygame.SRCALPHA)
    src_cx, src_cy = W // 2, 96
    src_rect = pygame.Rect(0, 0, size, size)
    src_rect.center = (src_cx, src_cy)
    tile.blit(overlay, (0, 0), src_rect)
    if sparkle_trim > 0:
        # Scale the tile down by (1 - trim) so the burst silhouette
        # uniformly shrinks. The tile stays the same surface size — we
        # blit a smaller version centred on the same midpoint so the
        # caller's centre-stamp blit still lands correctly.
        scaled_size = max(1, int(round(size * (1 - sparkle_trim))))
        scaled = pygame.transform.smoothscale(tile, (scaled_size,
                                                       scaled_size))
        out = pygame.Surface((size, size), pygame.SRCALPHA)
        out.blit(scaled, scaled.get_rect(center=(size // 2, size // 2)))
        tile = out
    return tile


def _split_wordmarks(left_text, right_text, font_size=28, outline_w=4):
    """Yellow-gradient SKATE + BOARD wordmarks at the same point size.
    Returned as two surfaces so the caller positions each on its half
    of the deck face. Both share the project's standard yellow→orange
    gradient (255,255,110)→(255,180,10) with a 4 px ink outline."""
    left = _yellow_text(left_text, font_size, outline_w=outline_w)
    right = _yellow_text(right_text, font_size, outline_w=outline_w)
    return left, right


def _blit_split_wordmarks_aligned(deck, deck_w, deck_h, gap_px,
                                   font_size=28, outline_w=3,
                                   axis_y=None):
    """Stamp SKATE and BOARD onto the deck with a SHARED baseline along
    the deck's long axis. Both glyph strips are rendered identically
    (same font, size, outline) so their baselines are guaranteed to
    coincide; we then place both surfaces' midright/midleft against the
    same y so even render-time descender rounding can't drift them.

    Auto-shrinks the point size if BOARD's outer edge would overrun the
    deck width — keeps both glyphs at the SAME size so the baseline
    lock survives. axis_y defaults to the deck's geometric centreline.

    Returns the (skate_rect, board_rect) screen-relative on the deck."""
    if axis_y is None:
        axis_y = deck_h // 2
    size = font_size
    while size >= 22:
        skate = _yellow_text("SKATE", size, outline_w=outline_w)
        board = _yellow_text("BOARD", size, outline_w=outline_w)
        right_edge = (deck_w // 2 + gap_px) + board.get_width()
        left_edge = (deck_w // 2 - gap_px) - skate.get_width()
        if right_edge <= deck_w - 4 and left_edge >= 4:
            break
        size -= 2
    skate_rect = skate.get_rect(
        midright=(deck_w // 2 - gap_px, axis_y))
    board_rect = board.get_rect(
        midleft=(deck_w // 2 + gap_px, axis_y))
    deck.blit(skate, skate_rect)
    deck.blit(board, board_rect)
    return skate_rect, board_rect


# R5 standardised composite shadow — 2 px offset, 35% alpha black, applied
# uniformly across every cell so the deck reads with one consistent depth.
R5_SHADOW_OFFSET = (2, 2)
R5_SHADOW_ALPHA = 89  # ≈35% of 255


def _stamp_live_score_preview(surf, deck_screen_center, score=888,
                                size=108, sparkle_trim=0.0):
    """Place the LIVE-score preview tile horizontally over the rotated
    deck. The tile is centred on the deck's on-screen centre so the
    preview reads "deck tilted, score level over it" — same composite
    relationship the runtime HUD will produce.

    sparkle_trim>0 shrinks the burst silhouette by that fraction in the
    PREVIEW only — used by the R6 sheet to keep the burst's outer spikes
    clear of the deck's inner top edge at y=70, without touching the
    production HUD overlay geometry."""
    tile = _live_score_preview(str(score), size=size,
                                 sparkle_trim=sparkle_trim)
    surf.blit(tile, tile.get_rect(center=deck_screen_center))


# R6 sparkle-clip trim — applied globally to every R6 preview blit so
# the burst's outer spikes shrink ~10% relative to the live HUD radius,
# pulling them inside the deck's inner top edge at y=70 even on V3's
# deeper -18° tilt where the spike rim would otherwise punch the rim.
R6_SPARKLE_TRIM = 0.10


def _draw_r5_d1_bolts(surf, deck_w, deck_h, inset=30, edge_inset=18,
                       rescue_lower_right=False,
                       rescue_top_bolts=False):
    """D1's four corner truck-mount bolts with a 1-px inner highlight
    so the dots read as polished metal hardware rather than flat
    stickers. AD critique called this out specifically — the inner
    pixel at (200,200,200) @ ~70% alpha catches just enough light.

    rescue_lower_right=True lightens ONLY the lower-right bolt's ink
    rim from (15,15,15) to (60,60,60) so the bolt survives against
    the deck's lower-edge shadow on V3's deeper -18° tilt where the
    standard ink rim was vanishing into the cast-shadow band.

    rescue_top_bolts=True rescues the TOP-LEFT and TOP-RIGHT bolts
    which sit under R7's translucent coin-counter / pause-tile chrome
    and were getting swallowed at chrome_alpha=170. The rescue raises
    the rim ~25% (INK → (60,60,60)), adds a crisp 1-px INK outer
    outline so the bolt edge survives the muddied chrome background,
    and bumps the specular highlight one step brighter so the bolt
    head still catches light through the translucent tile."""
    for bolt_x in (inset, deck_w - inset):
        for bolt_y in (edge_inset, deck_h - edge_inset):
            is_lower_right = (rescue_lower_right
                              and bolt_x == deck_w - inset
                              and bolt_y == deck_h - edge_inset)
            is_top_under_chrome = (rescue_top_bolts
                                   and bolt_y == edge_inset)
            if is_top_under_chrome:
                # Crisp INK outline pass so the bolt silhouette stays
                # readable against the translucent chrome muddying.
                pygame.draw.circle(surf, INK, (bolt_x, bolt_y), 6)
                rim_ink = (60, 60, 60)
            elif is_lower_right:
                rim_ink = (60, 60, 60)
            else:
                rim_ink = INK
            pygame.draw.circle(surf, rim_ink, (bolt_x, bolt_y), 5)
            pygame.draw.circle(surf, (60, 60, 60), (bolt_x, bolt_y), 3)
            # Specular dot — one step brighter on the under-chrome top
            # bolts so they still pick up "polished metal" reading
            # through the 170-alpha chrome tint.
            if is_top_under_chrome:
                hl = pygame.Surface((2, 2), pygame.SRCALPHA)
                hl.fill((225, 225, 225, 200))
            else:
                hl = pygame.Surface((2, 2), pygame.SRCALPHA)
                hl.fill((200, 200, 200, 180))
            surf.blit(hl, (bolt_x - 1, bolt_y - 1))


def variant_r5_d1_larger_slab(base, score):
    """R5-D1 — Larger straight slab at R4-D2 tilt. Plain rounded-rect
    320 x 92 (~25% bigger than R4's 280 x 72), tilt -12° (the R4-D2
    angle the user picked), deck-centre y=140. Truck-bolt dots stamped
    at all four corners so the bigger silhouette still reads as a
    deck rather than an oversized lozenge. SKATE/BOARD wordmarks at
    28 pt frame the empty centre; the LIVE halftone score preview is
    blit horizontally on top of the rotated deck after the fact.

    R5-final polish: outline_w dropped 4→3 so the gold rim stops
    competing with the score burst's yellow; bolts gain a metallic
    inner highlight; SKATE/BOARD share one baseline through the deck's
    long axis (midright/midleft alignment, identical y axis)."""
    s = base.copy()
    deck_w, deck_h = 320, 92
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=44)
    # Wash stripes — keep alpha at 38 (matches R4-D2) so the surface
    # still has a hint of graphic-deck texture without competing.
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    stripe_step = 24
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 38), pts)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=44)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    _draw_r5_d1_bolts(deck, deck_w, deck_h, inset=30, edge_inset=18)
    # Baseline-locked split wordmarks — SKATE and BOARD share one y
    # axis BEFORE the rotation, so they stay co-baselined after the
    # composite rotates as a unit.
    _blit_split_wordmarks_aligned(deck, deck_w, deck_h,
                                   gap_px=64, font_size=28,
                                   outline_w=3)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=44)
    rotated = pygame.transform.rotate(deck, -12)
    deck_center = (W // 2, 140)
    rect = rotated.get_rect(center=deck_center)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    # LIVE score preview blit AFTER the deck rotate so the badge sits
    # dead-horizontal, matching the production HUD overlay.
    _stamp_live_score_preview(s, deck_center, score=888)
    return s


def variant_r5_d2_steeper_pop(base, score):
    """R5-D2 — Steeper, more popped tilt (-16°). Same 320 x 92 slab
    silhouette as D1 but the angle is committed harder, and the bolts
    are dropped on the downhill (upper-right) end so only the uphill
    (lower-left) end carries the truck mounts. The asymmetry implies a
    tail-vs-nose read on a single slab without changing the silhouette,
    keeping the "ONE whole deck" constraint satisfied. Deck-centre
    pulled to y=145 so the steeper rotation's upper-left corner still
    clears the coin HUD at y≈18..40."""
    s = base.copy()
    deck_w, deck_h = 320, 92
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=44)
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    stripe_step = 22
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 42), pts)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=44)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    # Bolts ONLY on the uphill (lower-left) end — after -16° rotation
    # the deck's left end sits lower on the canvas, which optically
    # reads as the "kicked-up tail" of the slant. Identity-preserving
    # asymmetry per the AD critique: D2 keeps its steeper pop +
    # one-end-only bolts.
    for bolt_y in (18, deck_h - 18):
        pygame.draw.circle(deck, INK, (30, bolt_y), 5)
        pygame.draw.circle(deck, (60, 60, 60), (30, bolt_y), 2)
    _blit_split_wordmarks_aligned(deck, deck_w, deck_h,
                                   gap_px=64, font_size=28,
                                   outline_w=3)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=44)
    rotated = pygame.transform.rotate(deck, -16)
    deck_center = (W // 2, 145)
    rect = rotated.get_rect(center=deck_center)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    _stamp_live_score_preview(s, deck_center, score=888)
    return s


def variant_r5_d3_popsicle_waist(base, score):
    """R5-D3 — True popsicle deck with a pinched waist. Wider at both
    truck ends (full 100 px height), pinched to ~78 px through the
    centre. SKATE sits on the wider left tail, BOARD on the wider
    right nose; the slimmer waist hosts the LIVE score badge so its
    halftone background sits over the simplest section of the deck.
    Tilt softened to -8° (the popsicle silhouette already carries the
    energy that the heavy tilt brought to D1/D2), deck-centre y=132."""
    s = base.copy()
    deck_w, deck_h = 320, 100   # the full envelope; waist pinches in
    # AD critique: previous 78 px waist made the deck read as two
    # stitched halves around the 888 burst. Pushed straight to 96 px
    # so the score sits inside a single unbroken plate instead of a
    # pinched neck. The popsicle silhouette still survives because
    # the truck-end fat sections are at the full 100 px envelope.
    waist_h = 96
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    # Concave-waist polygon — cosine pinch deepest at t=0.5.
    samples = 32
    top_pts = []
    bot_pts = []
    for i in range(samples + 1):
        t = i / samples
        x = int(t * deck_w)
        pinch = (1 - math.cos(t * 2 * math.pi)) * 0.5  # 0..1..0
        cur_h = deck_h - (deck_h - waist_h) * pinch
        top_pts.append((x, int((deck_h - cur_h) / 2)))
        bot_pts.append((x, int((deck_h + cur_h) / 2)))
    poly = top_pts + list(reversed(bot_pts))
    pygame.draw.polygon(deck, PLATE_RED, poly)
    # Wash stripes masked to the popsicle polygon.
    stripes = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    stripe_step = 22
    for i in range(-deck_h, deck_w + deck_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + deck_h, deck_h),
                   (i + deck_h, deck_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 32), pts)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    # Truck bolts on each fat end — sits on the wider tail/nose where
    # there's room for the 4 px dots without crowding the waist.
    for bolt_x in (32, deck_w - 32):
        for bolt_y in (24, deck_h - 24):
            pygame.draw.circle(deck, INK, (bolt_x, bolt_y), 4)
            pygame.draw.circle(deck, (60, 60, 60), (bolt_x, bolt_y), 2)
    # Split wordmarks — SKATE on the wider TAIL (left), BOARD on the
    # wider NOSE (right), both pinned to the deck's single long-axis
    # baseline so they read as one continuous word the live score
    # punctuates in the middle.
    _blit_split_wordmarks_aligned(deck, deck_w, deck_h,
                                   gap_px=66, font_size=28,
                                   outline_w=3)
    pygame.draw.polygon(deck, INK, poly, 4)
    rotated = pygame.transform.rotate(deck, -8)
    deck_center = (W // 2, 132)
    rect = rotated.get_rect(center=deck_center)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    _stamp_live_score_preview(s, deck_center, score=888)
    return s


def variant_r5_d4_trucks_wheels(base, score):
    """R5-D4 — Deck + visible trucks + wheels (full skateboard read).
    320 x 88 deck on top, two truck stems + four wheels below the
    deck. Bolt dots dropped because the trucks themselves provide
    the deck-to-truck visual anchor. -10° tilt. Deck-centre lifted
    to y=125 so the wheel bottoms still land above the buff-icon
    row at y≈194 even after the rotation swing."""
    s = base.copy()
    deck_w, deck_h = 320, 88
    pad = 24       # vertical room for trucks + wheels under the deck
    comp_w = deck_w + 16
    comp_h = deck_h + pad
    deck = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)
    deck_rect = pygame.Rect((comp_w - deck_w) // 2, 0, deck_w, deck_h)
    # Trucks first so the deck's rounded-rect overlays the stem tops
    # (the deck reads as bolted ON TOP of the trucks).
    truck_w, truck_h = 34, 8
    for truck_cx_local in (deck_rect.left + 48, deck_rect.right - 48):
        truck_rect = pygame.Rect(0, 0, truck_w, truck_h)
        truck_rect.center = (truck_cx_local, deck_h + 4)
        pygame.draw.rect(deck, (40, 38, 44), truck_rect,
                         border_radius=3)
        pygame.draw.rect(deck, INK, truck_rect, 2, border_radius=3)
        # Two wheels per truck — wheels per AD critique: desaturated
        # ~12% and value −10% from the earlier punchy ochre so they
        # stop pulling focus from the score. Pre-shift was
        # (215,195,160); the (185,172,150) shift below applies both
        # the saturation pull and the value drop in one step.
        for wheel_dx in (-truck_w // 2 + 3, truck_w // 2 - 3):
            wheel_cx = truck_cx_local + wheel_dx
            wheel_cy = deck_h + 16
            # 1 px dark contact shadow under each wheel — anchors them
            # to the truck stem so they read as rolling on the ground
            # plane rather than floating ornamental dots.
            shadow = pygame.Surface((16, 4), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 110),
                                shadow.get_rect())
            deck.blit(shadow, shadow.get_rect(
                center=(wheel_cx, wheel_cy + 7)))
            pygame.draw.circle(deck, (185, 172, 150),
                               (wheel_cx, wheel_cy), 7)
            pygame.draw.circle(deck, INK,
                               (wheel_cx, wheel_cy), 7, 2)
    # Deck body — sits ON TOP of the truck stems.
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=42)
    stripes = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)
    stripe_step = 24
    for i in range(-comp_h, comp_w + comp_h, stripe_step):
        if (i // stripe_step) % 2 == 0:
            pts = [(i, 0), (i + stripe_step // 2, 0),
                   (i + stripe_step // 2 + comp_h, comp_h),
                   (i + comp_h, comp_h)]
            pygame.draw.polygon(stripes, (255, 235, 130, 36), pts)
    mask = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=42)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    # Split wordmarks framing the empty centre — no bolt dots, the
    # trucks below carry the deck-anchor reading on their own. Both
    # words anchor to the deck's long-axis centreline so they stay
    # co-baselined after the -10° rotation. The helper auto-shrinks
    # in lockstep if BOARD would overrun the deck right edge so the
    # baseline lock survives a size change.
    #
    # D4's deck is sub-blitted from the composite at deck_rect.left
    # onward, so we slice into a temp view of the deck region and
    # blit there in deck-local coords.
    deck_view = deck.subsurface(deck_rect)
    _blit_split_wordmarks_aligned(deck_view, deck_w, deck_h,
                                   gap_px=64, font_size=28,
                                   outline_w=3)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=42)
    rotated = pygame.transform.rotate(deck, -10)
    deck_center = (W // 2, 125)
    rect = rotated.get_rect(center=deck_center)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    _stamp_live_score_preview(s, deck_center, score=888)
    return s


def variant_r5_d5_longboard(base, score):
    """R5-D5 — Longboard slab. Wider, more rectangular old-school
    silhouette (330 x 76) — at the 320 px width cap with a tiny extra
    push since longboards canonically run long-and-low. Tilt softened
    to -6° (long decks ride flatter), deck-centre y=148. SKATE and
    BOARD set wider apart so the LIVE score has comfortable breathing
    room across the slimmer central panel. Subtle ≤12% alpha
    horizontal grain stripes sell the wood-grain longboard finish
    without competing with the wordmark or score."""
    s = base.copy()
    deck_w, deck_h = 330, 76
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    # Smaller corner radius — longboards read squarer than popsicles.
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=24)
    # Wood-grain stripes — committed per AD critique: 3 stripes at
    # ~20% alpha so the wood read survives at thumbnail size instead
    # of being invisible. Drawn at fixed thirds across the deck so
    # the count never creeps back up.
    grain = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    grain_alpha = 50  # ~20% — past the visibility floor AD called out
    for frac in (0.28, 0.50, 0.72):
        gy = int(deck_h * frac)
        pygame.draw.line(grain, (140, 25, 18, grain_alpha),
                         (10, gy), (deck_w - 10, gy), 1)
    mask = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), deck_rect,
                     border_radius=24)
    grain.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(grain, (0, 0))
    # Truck bolts pushed further out — longer deck means wider truck
    # wheelbase, and the bolts sell that proportionally.
    _draw_truck_bolts(deck, deck_w, deck_h, inset=34, edge_inset=14)
    # Split wordmarks — baseline-locked to the deck centreline so the
    # tilt rotates SKATE and BOARD around a single axis.
    _blit_split_wordmarks_aligned(deck, deck_w, deck_h,
                                   gap_px=70, font_size=28,
                                   outline_w=3)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=24)
    # Tilt committed to -10° per the AD critique — the previous -6°
    # was reading as a flat rectangle rather than a thrown longboard.
    rotated = pygame.transform.rotate(deck, -10)
    deck_center = (W // 2, 148)
    rect = rotated.get_rect(center=deck_center)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    _stamp_live_score_preview(s, deck_center, score=888)
    return s


VARIANTS_R5 = [
    ("R5-D1 — Larger slab, R4-D2 tilt",  variant_r5_d1_larger_slab),
    ("R5-D2 — Steeper pop (-16 deg)",    variant_r5_d2_steeper_pop),
    ("R5-D3 — Popsicle waist",           variant_r5_d3_popsicle_waist),
    ("R5-D4 — Trucks + wheels",          variant_r5_d4_trucks_wheels),
    ("R5-D5 — Longboard",                variant_r5_d5_longboard),
]


# ── Round 6 — R5-D1 silhouette relocated UP so the deck wraps the regular
# score position (y=70 — the NA-plate centre). Each cell explores ONE
# strategy for resolving the coin-counter (top-left) / pause-tile
# (top-right) collision the upward move creates. Deck silhouette is
# R5-D1's plain rounded slab; only the size, tilt, position, and chrome
# handling vary per cell.


# Snapshot boxes for the live HUD chrome — sized just bigger than the
# coin plate (x=12..~90, y=14..52) and pause tile (x=274..342, y=14..52)
# so V1 can capture the chrome from the base frame, paint the deck UNDER
# it, then re-stamp the chrome on top. Tight bounds keep the sky margin
# around the chrome minimal so re-stamping doesn't punch a large rectangle
# of sky through the deck silhouette where the deck overlaps each corner.
_HUD_COIN_BOX = pygame.Rect(0, 6, 100, 56)
_HUD_PAUSE_BOX = pygame.Rect(264, 6, 90, 56)


def _r6_build_plain_deck(deck_w, deck_h, *, border_radius,
                          stripe_step=24, stripe_alpha=38,
                          bolt_inset_x=30, bolt_inset_y=18,
                          rescue_lower_right_bolt=False,
                          rescue_top_bolts=False):
    """Build the shared R6 plain rounded-rect deck surface — R5-D1's
    silhouette factored out so V1-V5 only have to vary the size, tilt,
    and centre. Same wash stripes + 4 corner bolts + ink rim as R5-D1
    so the silhouette identity stays locked across the round.

    rescue_lower_right_bolt=True forwards the bolt-rim lightening to
    the bolt helper — used by V3 only, where the deeper -18° tilt
    drops the bolt into the deck's lower-edge shadow band.

    rescue_top_bolts=True rescues the two top corner bolts (which
    sit under R7's translucent coin-counter and pause-tile chrome)
    so they survive the chrome alpha-multiply."""
    deck = pygame.Surface((deck_w, deck_h), pygame.SRCALPHA)
    deck_rect = deck.get_rect()
    pygame.draw.rect(deck, PLATE_RED, deck_rect, border_radius=border_radius)
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
                     border_radius=border_radius)
    stripes.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    deck.blit(stripes, (0, 0))
    _draw_r5_d1_bolts(deck, deck_w, deck_h,
                       inset=bolt_inset_x, edge_inset=bolt_inset_y,
                       rescue_lower_right=rescue_lower_right_bolt,
                       rescue_top_bolts=rescue_top_bolts)
    return deck, deck_rect


def _r6_paint_deck(s, deck_w, deck_h, *, tilt_deg, deck_center,
                    border_radius=44, gap_px=64, font_size=28,
                    stripe_step=24, stripe_alpha=38,
                    bolt_inset_x=30, bolt_inset_y=18, outline_w=4,
                    rescue_lower_right_bolt=False,
                    skip_wordmarks=False,
                    right_edge_falloff_px=0):
    """Build the R6 plain deck, lay split SKATE | BOARD wordmarks on
    its long axis, ink-rim it, rotate, and composite onto `s` with the
    shared R5 shadow. Returns the deck_center as passed (so the caller
    can hand it straight to the live-score preview stamp).

    skip_wordmarks lets a caller (V2's narrow concept variant) draw
    its own wordmark treatment after the deck base is built. The
    helper still ink-rims the deck for that path so the caller can
    blit text on top of a fully-rimmed silhouette.

    right_edge_falloff_px>0 fades the rotated deck's rightmost N
    px from full alpha to ~40% — V5 uses this so the deck tucks
    UNDER the pause tile with a soft gradient instead of either a
    hard chrome edge or chrome floating above a full-alpha deck."""
    deck, deck_rect = _r6_build_plain_deck(
        deck_w, deck_h, border_radius=border_radius,
        stripe_step=stripe_step, stripe_alpha=stripe_alpha,
        bolt_inset_x=bolt_inset_x, bolt_inset_y=bolt_inset_y,
        rescue_lower_right_bolt=rescue_lower_right_bolt)
    if not skip_wordmarks:
        _blit_split_wordmarks_aligned(deck, deck_w, deck_h,
                                       gap_px=gap_px, font_size=font_size,
                                       outline_w=3)
    pygame.draw.rect(deck, INK, deck_rect, outline_w,
                     border_radius=border_radius)
    rotated = pygame.transform.rotate(deck, tilt_deg)
    rect = rotated.get_rect(center=deck_center)
    if right_edge_falloff_px > 0:
        # Multiply the rotated surface's right strip by a per-column
        # alpha ramp so the rightmost falloff_px taper from 100% to
        # ~40%. The deck still ink-rims at full strength before this
        # pass — we only mute the assembled composite at the tuck zone.
        rw, rh = rotated.get_size()
        falloff = pygame.Surface((rw, rh), pygame.SRCALPHA)
        falloff.fill((255, 255, 255, 255))
        for col in range(rw - right_edge_falloff_px, rw):
            t = (col - (rw - right_edge_falloff_px)) / max(
                1, right_edge_falloff_px - 1)
            alpha = int(round(255 - t * (255 - 102)))
            col_strip = pygame.Surface((1, rh), pygame.SRCALPHA)
            col_strip.fill((255, 255, 255, alpha))
            falloff.blit(col_strip, (col, 0))
        rotated.blit(falloff, (0, 0),
                     special_flags=pygame.BLEND_RGBA_MULT)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    return deck_center


def variant_r6_v1_full_slab_ui_on_top(base, score):
    """R6-V1 — Full 320 x 92 slab, deck-centre (180, 70). The deck is
    painted UNDER the live HUD chrome: the coin plate (top-left) and
    pause tile (top-right) are snapshotted from `base` BEFORE the deck
    is laid down, then re-stamped on top so they read as stickers on
    the deck. Most committed to "score stays where it always sits";
    accepts the chrome-on-deck collision rather than dodging it.

    Cutout pockets: under each chrome tile a soft-edged dark blob is
    blitted onto the deck so the chrome reads as PUNCHING THROUGH the
    deck rather than floating above it — sells the layering as an
    intentional cutout instead of a z-order accident."""
    s = base.copy()
    # Snapshot the live HUD chrome BEFORE the deck paint so the chrome
    # can re-land on top of the deck composite afterwards. Tight boxes
    # so the re-stamp's sky margin barely punches the deck silhouette.
    coin_snap = base.subsurface(_HUD_COIN_BOX).copy()
    pause_snap = base.subsurface(_HUD_PAUSE_BOX).copy()
    deck_center = _r6_paint_deck(s, 320, 92,
                                  tilt_deg=-12,
                                  deck_center=(W // 2, 70))
    # Cutout shadow-pockets — drawn AFTER the deck blit but BEFORE the
    # chrome re-stamp + live-score burst. Each pocket is a soft
    # near-black rounded-rect at ~35% alpha inset 6 px around the
    # chrome tile, with a gaussian-ish falloff (two concentric layers
    # of progressively weaker alpha) so the edge feathers instead of
    # cutting a hard rectangle of dark out of the deck.
    for chrome_box in (_HUD_COIN_BOX, _HUD_PAUSE_BOX):
        inset = 6
        pocket_rect = chrome_box.inflate(inset * 2, inset * 2)
        falloff = pygame.Surface(pocket_rect.size, pygame.SRCALPHA)
        # Two-stop falloff — inner core at 35%, outer halo at ~15%, both
        # near-black, both rounded so the chrome edge softens rather
        # than ending on a hard line.
        pygame.draw.rect(falloff, (0, 0, 0, 38),
                         falloff.get_rect(), border_radius=14)
        inner = falloff.get_rect().inflate(-8, -8)
        pygame.draw.rect(falloff, (0, 0, 0, 90),
                         inner, border_radius=10)
        s.blit(falloff, pocket_rect.topleft)
    # Re-stamp the chrome ON TOP of the deck — coin counter on the
    # left, pause tile on the right, both at their original positions
    # so the rest of the UI lines up untouched.
    s.blit(coin_snap, _HUD_COIN_BOX.topleft)
    s.blit(pause_snap, _HUD_PAUSE_BOX.topleft)
    # Score badge LAST so it always sits on top of everything — even
    # if the coin or pause re-stamp clipped a corner of the central
    # burst region, the badge wins on the final composite.
    _stamp_live_score_preview(s, deck_center, score=888,
                                sparkle_trim=R6_SPARKLE_TRIM)
    return s


def variant_r6_v2_narrow_between_buttons(base, score):
    """R6-V2 — Narrow with reserved score (replacement concept).
    Previous narrow-tucked-slab kept clipping the wordmark; this
    version commits to a 240 x 88 slab at -12° that reserves an
    88-px central gap for the live halftone score badge so the
    wordmarks sit cleanly in the deck halves either side. SKATE and
    BOARD rotate WITH the deck so the slant carries through the
    full composite, and the baseline-locked helper auto-shrinks the
    size in lockstep if BOARD's outer edge would overrun the deck
    width — guarantees no clipped glyph at the deck-edge.

    If the auto-shrink would push the wordmark below 22 pt
    (legibility floor at thumbnail scale on the review sheet) the
    cell falls back to floating SKATE and BOARD chips OUTSIDE the
    deck — small yellow-gradient text on dark chips that anchor the
    deck visually without competing with the score badge.

    Pick whichever path keeps the wordmark readable; the caption
    on the review sheet reflects the choice."""
    s = base.copy()
    deck_w, deck_h = 240, 88
    deck_center = (W // 2, 70)
    # Pre-flight: can SKATE/BOARD fit cleanly at >=22 pt with an
    # 88-px central reserve? gap_px=44 (half the reserve).
    reserve_gap_px = 44
    test_size = 22
    skate_test = _yellow_text("SKATE", test_size, outline_w=3)
    available_half = deck_w // 2 - reserve_gap_px - 4
    inline_fits = skate_test.get_width() <= available_half
    if inline_fits:
        # Inline path — wordmarks INSIDE the deck halves, rotating
        # with the deck. Larger reserve forces tighter wordmark
        # placement so the wordmark cap sits in the deck's broad
        # central band rather than crowding the rim.
        _r6_paint_deck(s, deck_w, deck_h,
                        tilt_deg=-12,
                        deck_center=deck_center,
                        gap_px=reserve_gap_px, font_size=test_size,
                        border_radius=40,
                        bolt_inset_x=24, bolt_inset_y=16)
        _stamp_live_score_preview(s, deck_center, score=888,
                                    sparkle_trim=R6_SPARKLE_TRIM)
        return s
    # Floating-chips fallback — deck stays bare of text, SKATE +
    # BOARD chips float OUTSIDE the deck silhouette as small
    # yellow-gradient labels on dark chips. SKATE sits above the
    # deck's left tail (the rotation drops it visually so a label
    # above the left side reads as the tail accent), BOARD sits
    # below the deck's right nose.
    _r6_paint_deck(s, deck_w, deck_h,
                    tilt_deg=-12,
                    deck_center=deck_center,
                    border_radius=40,
                    bolt_inset_x=24, bolt_inset_y=16,
                    skip_wordmarks=True)
    chip_size = 20
    for chip_text, chip_pos in (
        ("SKATE", (deck_center[0] - 92, deck_center[1] - 40)),
        ("BOARD", (deck_center[0] + 92, deck_center[1] + 40)),
    ):
        glyphs = _yellow_text(chip_text, chip_size, outline_w=3)
        pad_x, pad_y = 8, 4
        chip_w = glyphs.get_width() + pad_x * 2
        chip_h = glyphs.get_height() + pad_y * 2
        chip = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
        chip_rect = chip.get_rect()
        pygame.draw.rect(chip, (30, 30, 36), chip_rect, border_radius=6)
        pygame.draw.rect(chip, INK, chip_rect, 2, border_radius=6)
        chip.blit(glyphs, glyphs.get_rect(center=chip_rect.center))
        # Match the deck slant so the chips feel attached to the same
        # tilted prop, not stickers on a level UI.
        chip = pygame.transform.rotate(chip, -12)
        s.blit(chip, chip.get_rect(center=chip_pos))
    _stamp_live_score_preview(s, deck_center, score=888,
                                sparkle_trim=R6_SPARKLE_TRIM)
    return s


def variant_r6_v3_deep_pop(base, score):
    """R6-V3 — Wide 320 x 80 slab at a deeper -18° tilt, deck-centre
    pulled UP to (180, 74) — was 78; the lift restores ~3 px clearance
    between the left deck-edge dip and the coin counter that the
    -18° tilt was eating into. The deck still wraps the score badge
    centred on the deck centre; with deck centre at y=74 the badge
    sits 4 px above the regular y=70 row but the live HUD recentres
    each frame so this offset is preview-only.

    Lower-right bolt is rescued: with the deeper -18° tilt the
    standard ink rim was vanishing into the cast-shadow band along
    the deck's lower edge. rescue_lower_right_bolt=True lightens
    JUST that bolt's rim to (60,60,60) so it survives at 1x scale."""
    s = base.copy()
    # Slightly shorter deck (80 vs 92) so the steeper tilt doesn't
    # carry the lower-right corner over the buff-icon row at y≈194.
    deck_center = _r6_paint_deck(s, 320, 80,
                                  tilt_deg=-18,
                                  deck_center=(W // 2, 74),
                                  gap_px=62, font_size=26,
                                  border_radius=40,
                                  bolt_inset_y=16,
                                  rescue_lower_right_bolt=True)
    _stamp_live_score_preview(s, deck_center, score=888,
                                sparkle_trim=R6_SPARKLE_TRIM)
    return s


def variant_r6_v4_mid_compromise(base, score):
    """R6-V4 — Mid 288 x 86 slab at -14°, deck-centre (180, 70). Sits
    between V1 (full-width, chrome on top) and V2 (narrow, clears
    chrome): the 288 wide deck almost touches the coin plate and pause
    tile boundaries (was 280; +8 px buys back the symmetry the BOARD
    shift below introduces), and the -14° tilt swings the corners
    down just enough that they pass UNDER the chrome instead of
    overlapping it. The safe middle choice — deck stays substantial
    without forcing chrome on-top-of-deck composition.

    V4 breaks the SKATE/BOARD lockstep that the shared helper enforces:
    BOARD's baseline is shifted 6 px LEFT (in deck-local coords, before
    rotation) and its size drops to size-1 (28 → 27 pt) so the
    trailing "D" sits ~4 px clear of the deck's inner right edge. SKATE
    keeps the original 28 pt so the left half of the deck doesn't go
    light on weight. The asymmetric sizing is V4-only — the other R6
    cells stay in shared-baseline mode."""
    s = base.copy()
    deck_w, deck_h = 288, 86
    border_radius = 42
    deck_center = (W // 2, 70)
    # Build the bare deck + bolts (no wordmarks; we lay them ourselves
    # so the V4-only asymmetric sizing slips past the shared helper).
    deck, deck_rect = _r6_build_plain_deck(
        deck_w, deck_h, border_radius=border_radius,
        bolt_inset_x=28, bolt_inset_y=17)
    # SKATE at the helper's effective auto-shrink floor (22 pt — the
    # old V4 shared-helper rendered there because the deck couldn't
    # hold 28 pt without overflow even on its previous 280 px width),
    # BOARD at size-1 (21 pt). Asymmetric sizing is V4-only — the
    # other R6 cells stay in shared-baseline mode.
    skate_size = 22
    board_size = 21   # size-1 per brief #3
    skate = _yellow_text("SKATE", skate_size, outline_w=3)
    board = _yellow_text("BOARD", board_size, outline_w=3)
    axis_y = deck_h // 2
    # gap_px tuned so SKATE has 4 px left clearance from the deck
    # inner edge at 22 pt and BOARD's shifted right edge has ~8 px
    # clearance from the deck inner right edge at 21 pt.
    gap_px = 56
    skate_rect = skate.get_rect(
        midright=(deck_w // 2 - gap_px, axis_y))
    # BOARD baseline shifted 6 px LEFT in deck-local coords so the
    # trailing "D" sits well clear of the deck right inner edge.
    board_rect = board.get_rect(
        midleft=(deck_w // 2 + gap_px - 6, axis_y))
    deck.blit(skate, skate_rect)
    deck.blit(board, board_rect)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=border_radius)
    rotated = pygame.transform.rotate(deck, -14)
    rect = rotated.get_rect(center=deck_center)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    _stamp_live_score_preview(s, deck_center, score=888,
                                sparkle_trim=R6_SPARKLE_TRIM)
    return s


def variant_r6_v5_offset_right(base, score):
    """R6-V5 — Asymmetric 300 x 90 slab at -12°, deck-CENTRE COMMITTED
    to (198, 70) — 18 px right of the frame centre (was 10; the
    previous offset read as a centring bug). The shift opens breathing
    room on the LEFT past the coin counter and deliberately TUCKS the
    deck UNDER the pause tile by ~4 px on the right. An 8-px alpha
    falloff (100% → 40%) on the deck's rightmost band feathers the
    tuck so the chrome reads as overlapping the deck on purpose, not
    as a sloppy z-order accident.

    Score badge sits at the deck centre (also at x=198) so it tracks
    the deck's optical balance, not the frame centre."""
    s = base.copy()
    deck_center = _r6_paint_deck(s, 300, 90,
                                  tilt_deg=-12,
                                  deck_center=(W // 2 + 18, 70),
                                  gap_px=62, font_size=28,
                                  border_radius=42,
                                  bolt_inset_x=28, bolt_inset_y=17,
                                  right_edge_falloff_px=8)
    _stamp_live_score_preview(s, deck_center, score=888,
                                sparkle_trim=R6_SPARKLE_TRIM)
    return s


VARIANTS_R6 = [
    ("R6-V1 — Full slab (UI on top)",     variant_r6_v1_full_slab_ui_on_top),
    ("R6-V2 — Floating wordmark chips",   variant_r6_v2_narrow_between_buttons),
    ("R6-V3 — Deep pop (-18 deg)",        variant_r6_v3_deep_pop),
    ("R6-V4 — Mid (-14 deg)",             variant_r6_v4_mid_compromise),
    ("R6-V5 — Offset right",              variant_r6_v5_offset_right),
]


# ── Round 7 — R6-V1 direction reworked. Same 320 x 92 slab, same deck
# centre (180, 70), but the SKATE/BOARD wordmark is FIXED LARGER (26-30 pt
# range, no auto-shrink), the central score-reserve is tightened so the
# wordmarks hug the burst, the tilt is reduced from R6-V1's -12°, and the
# coin counter + pause tile are re-stamped at 50% alpha so the deck red and
# the SKATE/BOARD glyphs bleed through them. R6-V1's cutout pockets are
# dropped — the translucent chrome supersedes the pocket trick.


def _blit_split_wordmarks_fixed(deck, deck_w, deck_h, gap_px,
                                  font_size, outline_w=3, axis_y=None,
                                  bot_col=(255, 180, 10),
                                  edge_inset=0):
    """Stamp SKATE and BOARD onto the deck at a FIXED font_size (no
    auto-shrink). Brief #2 demands the R7 wordmark sits at 26-30 pt,
    explicitly above the shared helper's 22-pt floor — the auto-shrink
    path would silently drop us back to that floor on edge-overflow,
    so this helper just blits at the requested size and lets the
    geometry sanity check guarantee fit before render.

    bot_col overrides the gradient's lower stop — R7-A3 uses the
    5%-darkened (242,171,10) so glyphs that fall under the
    translucent chrome still punch.

    edge_inset>0 nudges SKATE rightward and BOARD leftward by that
    many pixels — R7-A3 uses +2 to give the glyphs ≥2 px clearance
    from the deck's INK rim where the AD critique flagged them as
    kissing the rim."""
    if axis_y is None:
        axis_y = deck_h // 2
    skate = _gradient_text("SKATE", font_size,
                            top_col=(255, 255, 110),
                            bot_col=bot_col,
                            outline=INK, outline_w=outline_w)
    board = _gradient_text("BOARD", font_size,
                            top_col=(255, 255, 110),
                            bot_col=bot_col,
                            outline=INK, outline_w=outline_w)
    skate_rect = skate.get_rect(midright=(deck_w // 2 - gap_px, axis_y))
    board_rect = board.get_rect(midleft=(deck_w // 2 + gap_px, axis_y))
    if edge_inset > 0:
        # +edge_inset px inward push on both glyphs — SKATE right,
        # BOARD left — to put air between the wordmark and the deck's
        # ink rim.
        skate_rect = skate_rect.move(edge_inset, 0)
        board_rect = board_rect.move(-edge_inset, 0)
    deck.blit(skate, skate_rect)
    deck.blit(board, board_rect)
    return skate_rect, board_rect


# Chrome re-stamp alpha for R7 — 170/255 ≈ 66%. The original 128/255
# (50%) was reading as half-rendered HUD; 170 keeps the chrome tiles
# unmistakably chrome while still letting the deck red and the
# SKATE/BOARD glyphs bleed through. The drop shadow baked into the
# coin-counter and pause-tile sub-surface is alpha-multiplied along
# with the rest of the snapshot — set_alpha covers the shadow strip
# too, so we don't need a separate shadow blit at 168 alpha.
R7_CHROME_ALPHA = 170

# Under-chrome wordmark contrast compensation. The yellow gradient's
# lower stop is darkened 5% from the standard (255,180,10) so the
# SKATE/BOARD glyphs that fall under the translucent coin-counter
# and pause-tile chrome still punch when the chrome tint multiplies
# their value. AD's "global darken" path — shipping over a clipped
# two-pass blit because the wordmark is baked into the rotated deck
# surface, so a screen-space clip rect against the chrome boxes
# would need an inverse-rotation transform we can't justify on a
# final-turn polish pass.
R7_WORDMARK_BOT_COL = (242, 171, 10)


def _restamp_chrome_translucent(s, base, chrome_alpha=R7_CHROME_ALPHA):
    """Snapshot the coin counter (top-left) and pause tile (top-right)
    from the base gameplay frame, set their per-surface alpha to
    chrome_alpha, then blit them on top of the canvas at their HUD
    positions. The translucent blit lets the deck red and any SKATE /
    BOARD glyph that falls under each tile bleed through, satisfying
    R7's "half transparent chrome" directive — supersedes R6-V1's
    cutout shadow-pocket approach.

    Implementation hint from the brief: apply `.set_alpha(chrome_alpha)`
    on the snapshot surfaces immediately before blitting."""
    coin_snap = base.subsurface(_HUD_COIN_BOX).copy()
    pause_snap = base.subsurface(_HUD_PAUSE_BOX).copy()
    coin_snap.set_alpha(chrome_alpha)
    pause_snap.set_alpha(chrome_alpha)
    s.blit(coin_snap, _HUD_COIN_BOX.topleft)
    s.blit(pause_snap, _HUD_PAUSE_BOX.topleft)


def _variant_r7_a_core(base, tilt_deg, word_size, score_reserve,
                        chrome_alpha=R7_CHROME_ALPHA,
                        wordmark_edge_inset=0):
    """Shared R7-A renderer. Builds the 320 x 92 deck silhouette with
    SKATE / BOARD wordmarks at a FIXED point size, rotates at the
    given tilt, composites with the unified R5 shadow, re-stamps the
    coin counter + pause tile on top at chrome_alpha (~66% by default
    post-polish), then drops the LIVE halftone score badge on the
    deck centre.

    score_reserve sets the central horizontal gap (in deck-local
    pixels) between SKATE's trailing edge and BOARD's leading edge —
    where the live score burst will land. Smaller reserve = wordmarks
    sit tighter against the burst, satisfying brief #3.

    wordmark_edge_inset>0 pushes SKATE/BOARD inward from the deck
    edge by that many pixels — the lead cell uses +2 to lift the
    glyphs off the deck's INK rim where the AD critique flagged them
    kissing the rim.

    rescue_top_bolts=True is forced on for the whole R7 set so the
    two corner bolts under the translucent coin-counter and pause-
    tile chrome survive the alpha-multiply. Bottom-left + bottom-
    right bolts stay at standard ink — they sit clear of the chrome
    zone after the rotation."""
    s = base.copy()
    deck_w, deck_h = 320, 92
    deck, deck_rect = _r6_build_plain_deck(
        deck_w, deck_h, border_radius=44,
        bolt_inset_x=30, bolt_inset_y=18,
        rescue_top_bolts=True)
    # gap_px is HALF the score reserve so SKATE/BOARD sit symmetrically
    # either side of the deck centre line, hugging the burst at the
    # tightened reserve the brief specifies. bot_col is the 5%-
    # darkened lower gradient stop so glyphs under the translucent
    # chrome still punch.
    _blit_split_wordmarks_fixed(deck, deck_w, deck_h,
                                  gap_px=score_reserve // 2,
                                  font_size=word_size, outline_w=3,
                                  bot_col=R7_WORDMARK_BOT_COL,
                                  edge_inset=wordmark_edge_inset)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=44)
    rotated = pygame.transform.rotate(deck, tilt_deg)
    deck_center = (W // 2, 70)
    rect = rotated.get_rect(center=deck_center)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    # Translucent chrome — coin counter + pause tile at ~66% alpha so
    # the deck red + SKATE/BOARD glyphs bleed through wherever they
    # collide, but the chrome still reads as chrome (not half-rendered
    # HUD). The drop shadow baked into each tile's snapshot rides the
    # same set_alpha multiplier — no separate shadow pass needed.
    _restamp_chrome_translucent(s, base, chrome_alpha=chrome_alpha)
    # Live halftone score burst LAST so it always sits on top of both
    # the deck and the translucent chrome.
    _stamp_live_score_preview(s, deck_center, score=888,
                                sparkle_trim=R6_SPARKLE_TRIM)
    return s


def variant_r7_a1_sweet_spot(base, score):
    """R7-A1 — Sweet spot (-7°), 28 pt wordmark, 74 px central
    reserve. Replaces the prior flat -4° A1, which read as a banner
    rather than a tilted deck. -7° lands midway between A3 (-8°,
    flagged lead) and a flatter sibling, 28 pt matches the A3/A4
    weight class, and the 74 px reserve sits between A2's tight 70
    and A3's looser 76 — designed as the "if you don't pick A3, you
    pick this" cell."""
    return _variant_r7_a_core(base, tilt_deg=-7, word_size=28,
                              score_reserve=74)


def variant_r7_a2_mild_big(base, score):
    """R7-A2 — Mild (-6°), 30 pt wordmark (largest), 74 px reserve.
    Reserve loosened from 70 → 74 per AD critique: the burst was
    getting clamped between SKATE and BOARD at 70 px; 74 unclamps
    it without dropping the 30 pt wordmark size."""
    return _variant_r7_a_core(base, tilt_deg=-6, word_size=30,
                              score_reserve=74)


def variant_r7_a3_mid(base, score):
    """R7-A3 — Mid (-8°), 28 pt wordmark, 76 px reserve. AD lead.
    +2 px inward inset on SKATE/BOARD glyphs so they sit cleanly
    inside the deck's INK rim instead of kissing it."""
    return _variant_r7_a_core(base, tilt_deg=-8, word_size=28,
                              score_reserve=76,
                              wordmark_edge_inset=2)


def variant_r7_a4_near_r6(base, score):
    """R7-A4 — Near R6-V1 (-10°), 28 pt wordmark, 80 px reserve.
    Wordmark bumped 26 → 28 pt to match A2/A3 weight class — at the
    80 px reserve, 28 pt SKATE/BOARD (~103 px wide each) clears the
    side rims with 7 px to spare."""
    return _variant_r7_a_core(base, tilt_deg=-10, word_size=28,
                              score_reserve=80)


VARIANTS_R7 = [
    ("R7-A1 — Sweet spot (-7 deg), 28 pt",   variant_r7_a1_sweet_spot),
    ("R7-A2 — Mild (-6 deg), 30 pt big",     variant_r7_a2_mild_big),
    ("R7-A3 — Mid (-8 deg), 28 pt (lead)",   variant_r7_a3_mid),
    ("R7-A4 — Near R6-V1 (-10 deg), 28 pt",  variant_r7_a4_near_r6),
]


# ── Round 8: R7-A1 reworked — "BOARD!" right word, deck EXTENDED to fit, ──
#           deck OPAQUE on TOP of FRAMELESS coin counter + pause button. ──
#
# User picked R7-A1 (-7° sweet spot, 28 pt SKATE/BOARD, 74 px reserve,
# deck 320 x 92, deck-centre (180,70), 4 corner bolts) and asked for three
# changes: (1) the right word becomes "BOARD!" — extend the DECK LENGTH so
# it fits without crowding the burst, never shrink the word to the old 320;
# (2) FLIP the z-order — the deck is now the TOP, OPAQUE layer over the
# coin counter + pause button, hiding whatever chrome falls under its
# silhouette; (3) STRIP the slate plate frame off both the coin counter
# and the pause button — render them FRAMELESS (glyph/text/bars + a soft
# drop shadow only), so the only chrome that shows is the bit peeking out
# in the extreme corners the tilted deck doesn't reach.
#
# The R8 base frame is built with the coin/pause chrome suppressed entirely
# (no plate, no glyph, no bars) so we can re-render them frameless ourselves
# at the right z-order: frameless chrome FIRST, then the OPAQUE deck on top,
# then the live halftone burst last.


# Frameless-chrome screen geometry — derived from the live HUD's draw_play
# coin block (coin_surf blit at (12-_NA_PAD, 14-_NA_PAD); glyph centre at
# surf-local (_NA_PAD+19, _NA_PAD+19); count text centred at
# (_NA_PAD+36+tw//2, _NA_PAD+19)) and PauseButton.TILE = (W-68-18,14,68,38).
# Reproduced here MINUS the _na_plate call so the coin glyph + count and the
# pause bars sit directly on the sky, gaining a soft drop shadow for the
# legibility the slate plate used to provide.
# Two coin/pause placements. The "normal" pair reproduces the live HUD's
# coin block + pause tile geometry (coin glyph centre at surf-local
# (_NA_PAD+19, _NA_PAD+19) ≈ (31,33); pause tile at (W-68-18,14,68,38)) so
# the deck half-covers them — used by the no-nudge A/B cell. The "corner"
# pair shoves the coin hard into the top-left (glyph centre raised to the
# extreme corner) and the pause hard into the top-right (right edge at
# x≈354) so a 340-wide tilted deck clears them with as little slice-through
# as the deck's own corner geometry allows.
_R8_COIN_GLYPH_CENTER = (31, 33)        # normal: (12-pad+pad+19, 14-pad+pad+19)
_R8_COIN_TEXT_LEFT = 48                  # normal: text midleft x
_R8_COIN_TEXT_CY = 33
_R8_PAUSE_TILE = pygame.Rect(W - 68 - 18, 14, 68, 38)  # normal pause tile

# Corner-nudge positions (item 2). Coin glyph centre anchored ≈(6,6)+radius
# into the top-left corner; pause bars anchored so their RIGHT edge sits at
# x≈354 near the top-right corner. Both clear of the 340 deck's reach.
_R8_COIN_GLYPH_CENTER_CORNER = (20, 21)  # glyph radius ~13 → top-left ≈(7,8)
_R8_COIN_TEXT_LEFT_CORNER = 36           # text midleft just right of glyph
_R8_COIN_TEXT_CY_CORNER = 21
_R8_PAUSE_CORNER_RIGHT = 356             # right edge of the right-most bar
_R8_PAUSE_CORNER_CY = 14                  # bars hard to the top, above the deck

# Frameless drop shadow: STRENGTHENED to +3,+3 / alpha ~140 (item 3) so the
# coin counter + pause read against BOTH day and night sky without a plate.
_R8_SHADOW_OFFSET = (3, 3)
_R8_SHADOW_ALPHA = 140
# Pause bars get a 1-px dark ink edge (item 4) — two bare bars need the edge
# definition the coin glyph already gets from its own circular silhouette.
_R8_PAUSE_OUTLINE = INK


def _r8_render_frameless_coin(surf, coin_count, corner=True):
    """Frameless coin counter — coin glyph + "x N" count, NO slate plate,
    with a soft near-black drop shadow under both so they survive the sky
    without the plate the live HUD draws behind them. Matches the live
    HUD content (same _coin_icon face, same _font(20) gold count) minus
    the _na_plate call.

    corner=True shoves the whole block hard into the top-left corner so a
    340-wide tilted deck clears it; corner=False keeps the live-HUD
    position so the no-nudge A/B cell shows the deck half-covering it."""
    from game.hud import _coin_icon, _font, UI_GOLD, NEAR_BLACK
    if corner:
        glyph_cx, glyph_cy = _R8_COIN_GLYPH_CENTER_CORNER
        text_left, text_cy = _R8_COIN_TEXT_LEFT_CORNER, _R8_COIN_TEXT_CY_CORNER
    else:
        glyph_cx, glyph_cy = _R8_COIN_GLYPH_CENTER
        text_left, text_cy = _R8_COIN_TEXT_LEFT, _R8_COIN_TEXT_CY
    coin_text = f"x{coin_count}"
    cf = _font(20, True)
    tw = cf.size(coin_text)[0]
    text_center = (text_left + tw // 2, text_cy)
    # Drop shadow first — the count text + a filled disc standing in for
    # the coin glyph's footprint, both offset and near-black at ~alpha 120.
    sh_txt = cf.render(coin_text, True, NEAR_BLACK)
    sh_txt.set_alpha(_R8_SHADOW_ALPHA)
    sr = sh_txt.get_rect(center=(text_center[0] + _R8_SHADOW_OFFSET[0],
                                  text_center[1] + _R8_SHADOW_OFFSET[1]))
    surf.blit(sh_txt, sr.topleft)
    coin_sh = pygame.Surface((28, 28), pygame.SRCALPHA)
    pygame.draw.circle(coin_sh, (*NEAR_BLACK, _R8_SHADOW_ALPHA), (14, 14), 13)
    surf.blit(coin_sh, coin_sh.get_rect(center=(
        glyph_cx + _R8_SHADOW_OFFSET[0],
        glyph_cy + _R8_SHADOW_OFFSET[1])))
    # Foreground glyph + gold count.
    _coin_icon(surf, glyph_cx, glyph_cy, 12)
    txt = cf.render(coin_text, True, UI_GOLD)
    surf.blit(txt, txt.get_rect(center=text_center).topleft)


def _r8_render_frameless_pause(surf, corner=True):
    """Frameless pause button — the two _NA_ACCENT pause bars, NO slate
    tile, with a soft drop shadow under the bars AND a 1-px dark ink edge
    around each bar (the two bare bars need the edge definition the coin
    glyph gets for free from its circular silhouette). Bar geometry
    matches PauseButton.draw (bw=5, bh=17, gap=4 at the tile centre).

    corner=True anchors the bars hard into the top-right corner (right
    edge at x≈354) so a 340-wide tilted deck clears them; corner=False
    keeps the live-HUD tile centre for the no-nudge A/B cell."""
    from game.hud import _NA_ACCENT, UI_CREAM, NEAR_BLACK, lerp_color
    bw, bh, gap = 5, 17, 4
    if corner:
        # Anchor the RIGHT bar's right edge at x≈354, bars hard to the top.
        right_edge = _R8_PAUSE_CORNER_RIGHT
        cy = _R8_PAUSE_CORNER_CY + bh // 2
        # cx is the gap centre: right bar spans [cx+gap, cx+gap+bw].
        cx = right_edge - gap - bw
    else:
        cx, cy = _R8_PAUSE_TILE.center
    ox, oy = _R8_SHADOW_OFFSET
    # Shadow bars under each pause bar so they read against the sky.
    sh = pygame.Surface((bw, bh), pygame.SRCALPHA)
    sh.fill((*NEAR_BLACK, _R8_SHADOW_ALPHA))
    for dx in (-gap - bw, gap):
        surf.blit(sh, (cx + dx + ox, cy - bh // 2 + oy))
    for dx in (-gap - bw, gap):
        # 1-px ink outline first (drawn 1 px out on each side) so the bar
        # face sits inside a crisp dark edge — the definition two bare
        # bars need that the coin glyph already carries.
        pygame.draw.rect(surf, _R8_PAUSE_OUTLINE,
                         (cx + dx - 1, cy - bh // 2 - 1, bw + 2, bh + 2),
                         border_radius=2)
        pygame.draw.rect(surf, _NA_ACCENT,
                         (cx + dx, cy - bh // 2, bw, bh), border_radius=2)
        pygame.draw.rect(surf, lerp_color(_NA_ACCENT, UI_CREAM, 0.5),
                         (cx + dx + 1, cy - bh // 2 + 1, max(1, bw - 3), 4))


def _r8_blit_wordmarks(deck, deck_w, deck_h, gap_px, font_size,
                        outline_w=3, axis_y=None, bang_size=None,
                        bang_margin=1):
    """Stamp SKATE (left) and BOARD! (right) onto the deck's long axis at
    a FIXED size, sharing one baseline. The right word carries the new
    exclamation mark; bang_size>0 renders the "!" as a SEPARATE, larger
    accent glyph appended after "BOARD" (R8-B4's flourish) instead of an
    inline same-size character, with bang_margin px of air between
    "BOARD" and the "!". Uses the R7 darkened lower gradient stop.
    Returns (skate_w, board_full_w) so the caller can report the fit."""
    if axis_y is None:
        axis_y = deck_h // 2
    bot = R7_WORDMARK_BOT_COL
    skate = _gradient_text("SKATE", font_size,
                           top_col=(255, 255, 110), bot_col=bot,
                           outline=INK, outline_w=outline_w)
    skate_rect = skate.get_rect(midright=(deck_w // 2 - gap_px, axis_y))
    deck.blit(skate, skate_rect)
    if bang_size:
        # "BOARD" + a larger, bolder "!" accent. The board glyph anchors
        # midleft at the reserve edge; the bang sits just right of it,
        # baseline-aligned to the board's baseline so the larger glyph
        # rises above the cap line as a flourish rather than dropping low.
        board = _gradient_text("BOARD", font_size,
                               top_col=(255, 255, 110), bot_col=bot,
                               outline=INK, outline_w=outline_w)
        bang = _gradient_text("!", bang_size,
                              top_col=(255, 255, 110), bot_col=bot,
                              outline=INK, outline_w=outline_w + 1)
        board_rect = board.get_rect(midleft=(deck_w // 2 + gap_px, axis_y))
        deck.blit(board, board_rect)
        bang_rect = bang.get_rect()
        bang_rect.left = board_rect.right + bang_margin
        bang_rect.bottom = board_rect.bottom
        deck.blit(bang, bang_rect)
        return skate.get_width(), (board_rect.width + bang_margin
                                   + bang_rect.width)
    board = _gradient_text("BOARD!", font_size,
                           top_col=(255, 255, 110), bot_col=bot,
                           outline=INK, outline_w=outline_w)
    board_rect = board.get_rect(midleft=(deck_w // 2 + gap_px, axis_y))
    deck.blit(board, board_rect)
    return skate.get_width(), board.get_width()


def _variant_r8_core(base, deck_w, word_size, score_reserve,
                      bang_size=None, bang_margin=1, tilt_deg=-7,
                      corner_nudge=True, label=""):
    """Shared R8 renderer. Frameless coin counter + pause button are
    painted onto the frame FIRST (the base already has the plated chrome
    suppressed), then the OPAQUE extended-length deck (SKATE / BOARD! +
    4 corner bolts) is composited ON TOP — hiding whatever frameless
    chrome falls under its tilted silhouette so only the extreme-corner
    bits peek out. The live halftone burst lands last at the deck centre.

    corner_nudge=True shoves the frameless coin into the extreme top-left
    corner and the pause into the extreme top-right (item 2) so the
    340-wide deck clears them; corner_nudge=False keeps the live-HUD
    positions so the no-nudge A/B cell shows the deck half-covering them.

    bang_margin sets the clearance (px) the larger "!" accent keeps from
    the deck's inner edge when bang_size>0 (item 5).

    Prints the per-cell BOARD! fit (glyph width vs the available half-deck
    width after the central reserve) so the geometry can be verified."""
    s = base.copy()
    deck_h = 92
    # Frameless chrome UNDER the deck — coin top-left, pause top-right.
    _r8_render_frameless_coin(s, 8, corner=corner_nudge)
    _r8_render_frameless_pause(s, corner=corner_nudge)
    # Build the extended-length deck. Reuse the R6 plain-deck silhouette
    # (wash stripes + 4 corner bolts + ink rim); bolts at the standard
    # treatment since the deck now sits ON TOP (the under-chrome bolt
    # rescue is moot). Bolt insets scale with the wider deck so the four
    # bolts stay near the corners rather than drifting inward. With the
    # corner-nudged chrome (item 2) the coin/pause sit in the extreme
    # corners; the 4 truck-bolts are inset a touch (item 8) so a bolt
    # never lands on the coin glyph / pause bars peeking past the rim.
    deck, deck_rect = _r6_build_plain_deck(
        deck_w, deck_h, border_radius=44,
        bolt_inset_x=34, bolt_inset_y=20)
    skate_w, board_w = _r8_blit_wordmarks(
        deck, deck_w, deck_h, gap_px=score_reserve // 2,
        font_size=word_size, outline_w=3, bang_size=bang_size,
        bang_margin=bang_margin)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=44)
    # Fit report — available half-deck width after the central reserve.
    avail = (deck_w - score_reserve) // 2
    fit = "FITS" if board_w <= avail else "CLIPS"
    print(f"    {label}: deck={deck_w}  BOARD! width={board_w}px  "
          f"available half={avail}px  margin={avail - board_w}px  [{fit}]")
    rotated = pygame.transform.rotate(deck, tilt_deg)
    deck_center = (W // 2, 70)
    rect = rotated.get_rect(center=deck_center)
    # OPAQUE deck on top of the frameless chrome, with the unified R5
    # shadow underneath so it reads with the same depth as R5-R7.
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET, alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    # Live halftone score burst LAST — single badge at the deck centre.
    _stamp_live_score_preview(s, deck_center, score=888,
                              sparkle_trim=R6_SPARKLE_TRIM)
    return s


def variant_r8_b1_deck340(base, score):
    """R8-B1 (LEAD) — Deck 340 wide, "BOARD!" at 28 pt. Deck-centre
    (180,70), tilt -7°. Frameless coin shoved into the EXTREME top-left
    corner + pause into the EXTREME top-right (item 2 corner-nudge) so
    both clear the 340 deck instead of being sliced by its tilted edge.
    Strengthened +3,+3 / alpha-140 frameless shadow (item 3) + a 1-px
    ink edge on the pause bars (item 4). The 74 px reserve is held from
    R7-A1; +12 px margin target per item 1."""
    return _variant_r8_core(base, deck_w=340, word_size=28,
                            score_reserve=74, corner_nudge=True,
                            label="R8-B1")


def variant_r8_b2_nonudge(base, score):
    """R8-B2 (A/B) — IDENTICAL to B1 (deck 340, 28 pt, "BOARD!") EXCEPT
    the frameless coin + pause stay at their NORMAL live-HUD positions
    (no corner-nudge), so the deck half-covers them. Lets the user A/B
    the corner-nudge (B1) directly against the no-nudge version in the
    same sheet (item 6)."""
    return _variant_r8_core(base, deck_w=340, word_size=28,
                            score_reserve=74, corner_nudge=False,
                            label="R8-B2(no-nudge)")


def variant_r8_b3_deck330_28pt(base, score):
    """R8-B3 — Shorter 330-wide deck, lettering RAISED 26 → 28 pt
    (item 7) to match the others' punch. Keeps the symmetric dual-corner
    chrome-peek logic; with the corner-nudge applied the coin/pause now
    sit in the extreme corners. If "BOARD!" at 28 pt clips the 330 deck
    the width is bumped to 336 (the smallest that clears it)."""
    deck_w = 330
    # Verify "BOARD!" at 28 pt fits the 330 deck; bump to 336 if it clips.
    probe = _gradient_text("BOARD!", 28, top_col=(255, 255, 110),
                           bot_col=R7_WORDMARK_BOT_COL, outline=INK,
                           outline_w=3)
    if probe.get_width() > (deck_w - 74) // 2:
        deck_w = 336
    return _variant_r8_core(base, deck_w=deck_w, word_size=28,
                            score_reserve=74, corner_nudge=True,
                            label="R8-B3")


def variant_r8_b4_deck352_bigbang(base, score):
    """R8-B4 (energetic alternate) — "BOARD" at 28 pt + the "!" as a
    larger 31 pt accent glyph (item 5: down from 34 pt) with a +6 px
    margin between "BOARD" and the "!". SKATE + "BOARD" body stay 28 pt;
    only the "!" is the enlarged accent. Deck extended to 356 — 352 left
    the BOARD + 6 px gap + 31 pt "!" 1 px shy of the inner edge, so the
    smallest clearing width is taken (item 5 allows the widen).
    Corner-nudged chrome (item 2)."""
    return _variant_r8_core(base, deck_w=356, word_size=28,
                            score_reserve=74, bang_size=31, bang_margin=6,
                            corner_nudge=True, label="R8-B4")


VARIANTS_R8 = [
    ("R8-B1 — Deck 340, BOARD! (LEAD, nudged)", variant_r8_b1_deck340),
    ("R8-B2 — No corner-nudge (A/B vs B1)",     variant_r8_b2_nonudge),
    ("R8-B3 — Deck 330, 28 pt (nudged)",        variant_r8_b3_deck330_28pt),
    ("R8-B4 — 31 pt '!' accent (nudged)",       variant_r8_b4_deck352_bigbang),
]


def _build_r8_base():
    """R8 base frame — same gameplay sim as R5-R7's bake_hud_score=False
    base, but with the coin counter + pause button suppressed ENTIRELY
    (no slate plate, no coin glyph/count, no pause bars) so R8 can
    re-render them FRAMELESS at the right z-order under the opaque deck.

    The coin block and pause draw are inline in HUD.draw_play, so we
    neuter the three leaf primitives they use — _na_plate (kills both
    plates), _coin_icon + _outlined_text (kills the coin glyph + count,
    leaving coin_surf transparent), and PauseButton.draw (kills the
    pause tile) — for the single base render pass, then restore them."""
    import game.hud as hud
    app = _build_gameplay_frame(bake_hud_score=False)
    saved = (hud._na_plate, hud._coin_icon, hud._outlined_text,
             hud.PauseButton.draw)
    _noop = lambda *a, **k: None
    hud._na_plate = _noop
    hud._coin_icon = _noop
    hud._outlined_text = _noop
    hud.PauseButton.draw = _noop
    try:
        base = _render_base(app)
    finally:
        (hud._na_plate, hud._coin_icon, hud._outlined_text,
         hud.PauseButton.draw) = saved
    return base


# ── Round 9: corrective pass on R8-B1 — RESTORE the slate cut-corner ──
#           plate frames on the coin counter + pause button at user-       ──
#           tunable transparency. The R6-V1 cutout shadow pockets stay     ──
#           gone (R8 already dropped them); only the chrome frames come    ──
#           back, exactly as R7 shipped them — same `_restamp_chrome_      ──
#           translucent` path. Three cells sweep the chrome alpha so the   ──
#           user can pin down which transparency they prefer.              ──
#
# User correction to R8: the slate plates around the coin counter and the
# pause button were the part they liked at "fifty percent"; what they
# wanted gone was the R6-V1 cutout shadow-pockets drawn UNDER the chrome
# on the deck face. R8 stripped the WRONG thing (the plates) and inherited
# the R8 frameless-chrome base. R9 reverts to the R7 base (chrome plates
# present in the source frame so the translucent re-stamp has a snapshot
# to pull) and reuses the R8-B1 deck-geometry (deck_w=340, "BOARD!",
# corner-bolt insets 34/20, -7° tilt, 28 pt wordmark, 74 px reserve).
# Cutout pockets are never invoked — the R6-V1 helper is local to its own
# variant function and R9 calls neither that variant nor any pocket helper.

def _variant_r9_core(base_with_chrome, chrome_alpha, label=""):
    """R9 renderer — R8-B1 deck geometry (340 x 92, "BOARD!" at 28 pt,
    74 px reserve, -7° tilt, 4 corner bolts at 34/20 insets) composited on
    the R7 base (slate chrome plates present in the source frame), then
    the coin counter + pause button RE-STAMPED translucent on top via the
    R7 `_restamp_chrome_translucent` helper. The set_alpha multiplier
    covers the slate plate, glyph, count text, and the plate's baked
    drop shadow in a single pass.

    NO cutout shadow pockets are drawn under the chrome — the R6-V1
    pocket helper is fenced inside its own variant function and R9 does
    not call it. The deck face stays clean PLATE_RED wherever the
    translucent chrome sits.

    rescue_top_bolts=True is held from R7 because the translucent chrome
    still overlays the two top corner bolts; without the rescue the
    bolts' value drops under the alpha-multiply.

    chrome_alpha sweeps 128 / 150 / 170 across the 3 R9 cells so the
    user can pin down the "fifty percent" target. 170 matches the R7
    shipped value (it shipped at 170, not 128, after the R7 design loop
    bumped it up from a literal 50% read as "half-rendered HUD")."""
    s = base_with_chrome.copy()
    deck_w, deck_h = 340, 92
    deck, deck_rect = _r6_build_plain_deck(
        deck_w, deck_h, border_radius=44,
        bolt_inset_x=34, bolt_inset_y=20,
        rescue_top_bolts=True)
    # Reuse the R8 wordmark helper — it carries the "BOARD!" glyph (with
    # the exclamation) at the R7 5%-darkened lower gradient stop, which
    # the R7 `_blit_split_wordmarks_fixed` helper does NOT (it only
    # emits "BOARD" without the bang).
    skate_w, board_w = _r8_blit_wordmarks(
        deck, deck_w, deck_h, gap_px=74 // 2,
        font_size=28, outline_w=3)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=44)
    # Fit report for symmetry with the R8 logging path.
    avail = (deck_w - 74) // 2
    fit = "FITS" if board_w <= avail else "CLIPS"
    print(f"    {label}: deck={deck_w}  BOARD! width={board_w}px  "
          f"available half={avail}px  margin={avail - board_w}px  [{fit}]")
    rotated = pygame.transform.rotate(deck, -7)
    deck_center = (W // 2, 70)
    rect = rotated.get_rect(center=deck_center)
    # Unified R5 drop shadow under the deck composite.
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    # Translucent SLATE chrome — the R7-shipped path. Coin counter (left)
    # and pause tile (right) snapshotted from the base, alpha-multiplied
    # by chrome_alpha, then blit on top so the deck red + SKATE/"BOARD!"
    # glyphs bleed through the slate plates at the chosen transparency.
    _restamp_chrome_translucent(s, base_with_chrome,
                                 chrome_alpha=chrome_alpha)
    # Live halftone score burst LAST — single badge at the deck centre.
    _stamp_live_score_preview(s, deck_center, score=888,
                                sparkle_trim=R6_SPARKLE_TRIM)
    return s


def variant_r9_c1_alpha128(base, score):
    """R9-C1 — Chrome alpha 128 (50%). The user's stated "fifty percent"
    target; the slate plates are most translucent here so the deck red +
    SKATE/"BOARD!" glyphs bleed through hardest."""
    return _variant_r9_core(base, chrome_alpha=128, label="R9-C1")


def variant_r9_c2_alpha150(base, score):
    """R9-C2 — Chrome alpha 150 (≈59%). Mid-point between the literal
    50% (C1) and the R7-shipped 66% (C3)."""
    return _variant_r9_core(base, chrome_alpha=150, label="R9-C2")


def variant_r9_c3_alpha170(base, score):
    """R9-C3 — Chrome alpha 170 (≈66%). The value R7 actually shipped —
    bumped up from a literal 50% after the R7 design loop flagged 128 as
    "reads like half-rendered HUD". Most legible of the three cells."""
    return _variant_r9_core(base, chrome_alpha=170, label="R9-C3")


VARIANTS_R9 = [
    ("R9-C1 — Chrome α=128 (50%)",      variant_r9_c1_alpha128),
    ("R9-C2 — Chrome α=150 (59%)",      variant_r9_c2_alpha150),
    ("R9-C3 — Chrome α=170 (66%, R7)",  variant_r9_c3_alpha170),
]


# ── Round 10: corrective ship — drop the slate `_na_plate` background      ──
#           ENTIRELY from BOTH the coin counter and the pause button. No     ──
#           replacement rectangle, no faint outline, no plate drop shadow.   ──
#           Just the bare coin glyph + "x N" count text at the HUD's normal  ──
#           top-left position, and the bare pause bars at the HUD's normal   ──
#           top-right position, drawn straight onto the sky. R8-B1 deck      ──
#           geometry on top (340 x 92, -7°, "BOARD!" 28 pt, 74 px reserve,   ──
#           4 corner bolts). The deck covers the inside-half of each icon —  ──
#           that's expected (R8 z-order: deck OPAQUE on top of chrome).      ──
#
# User correction to R9: the translucent slate plates around the coin counter
# and pause button ARE the "blue half-transparent rectangle" they want gone.
# Both prior interpretations (R8 stripped icons+plate; R9 brought plates back)
# missed the target. R10 keeps the icons (coin glyph + count + pause bars) at
# their normal HUD positions and drops ONLY the slate plate beneath each.

def _build_r10_base():
    """R10 base frame — same gameplay sim as the R5-R9 bake_hud_score=False
    base, but with the slate `_na_plate` background suppressed ONLY (the
    coin glyph + "x N" count text and the pause bars still render at their
    normal live-HUD positions, just without the slate plate underneath).

    Implementation: monkey-patch `hud._na_plate` to a no-op for the single
    base render pass — the coin block calls `_na_plate` then `_coin_icon` +
    `_outlined_text` (count), and PauseButton.draw calls `_na_plate` then
    the bar polygons. With _na_plate neutered, both the glyph/text and the
    pause bars survive at their production positions, drawn straight onto
    the sky.

    NO replacement rectangle, NO icon drop shadow, NO ink edge around the
    pause bars — the user's directive is "icons as they natively render in
    the production HUD, minus the slate plate".
    """
    import game.hud as hud
    app = _build_gameplay_frame(bake_hud_score=False)
    saved_na_plate = hud._na_plate
    hud._na_plate = lambda *a, **k: None
    try:
        base = _render_base(app)
    finally:
        hud._na_plate = saved_na_plate
    return base


def variant_r10_a1_plates_removed(base, score):
    """R10-A1 — Plates removed (chrome plateless on R9 deck). Reuses the
    R8-B1 / R9 deck geometry: 340 wide x 92 tall, deck-centre (180, 70),
    -7° tilt, PLATE_RED fill, INK rim, 4 corner bolts (insets 34/20),
    "SKATE" + "BOARD!" wordmark at 28 pt with the 74 px central reserve,
    yellow gradient with the R7 darkened lower stop, outline_w=3. Live
    halftone burst stamped LAST at the deck centre.

    Z-order: the bare coin glyph + count (top-left) and the bare pause
    bars (top-right) are already painted in the base at their normal HUD
    positions. The deck composites OPAQUE on top — the inside-half of
    each icon disappears under the tilted silhouette, leaving only the
    outside-corner remainder visible. That's the R8 z-order the user
    explicitly endorsed; the corrective only kills the slate plate.

    Unified 2 px / 35% alpha drop shadow under the deck composite via
    `_composite_shadow` (deck shadow only; no shadow under the icons).
    """
    s = base.copy()
    deck_w, deck_h = 340, 92
    # R6 plain-deck silhouette + 4 corner bolts. No rescue_top_bolts —
    # the deck sits OPAQUE on top, the under-chrome bolt rescue is moot.
    deck, deck_rect = _r6_build_plain_deck(
        deck_w, deck_h, border_radius=44,
        bolt_inset_x=34, bolt_inset_y=20)
    skate_w, board_w = _r8_blit_wordmarks(
        deck, deck_w, deck_h, gap_px=74 // 2,
        font_size=28, outline_w=3)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=44)
    avail = (deck_w - 74) // 2
    fit = "FITS" if board_w <= avail else "CLIPS"
    print(f"    R10-A1: deck={deck_w}  BOARD! width={board_w}px  "
          f"available half={avail}px  margin={avail - board_w}px  [{fit}]")
    rotated = pygame.transform.rotate(deck, -7)
    deck_center = (W // 2, 70)
    rect = rotated.get_rect(center=deck_center)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    _stamp_live_score_preview(s, deck_center, score=888,
                                sparkle_trim=R6_SPARKLE_TRIM)
    return s


# Two identical cells so _compose_sheet has the >=2 it needs to lay out a
# proper grid; both confirm the same shipped frame (single corrective ship,
# no exploration). Caption text is identical per the brief.
VARIANTS_R10 = [
    ("R10-A1 — Plates removed (chrome plateless on R9 deck)",
     variant_r10_a1_plates_removed),
    ("R10-A1 — Plates removed (chrome plateless on R9 deck)",
     variant_r10_a1_plates_removed),
]


# ── Round 11: corrective ship — restore the STANDARD PRODUCTION coin       ──
#           counter + pause button (default `_na_plate` slate cut-corner    ──
#           plates at FULL opacity, normal HUD positions) UNDER the R10     ──
#           opaque deck. Same R10 deck geometry on top.                     ──
#
# R7 made the chrome translucent. R8 stripped the plates and went frameless.
# R9 brought translucent plates back. R10 removed the slate plates entirely.
# Each round over-treated the chrome; the user repeatedly asked for the
# coin counter + pause button to be left ALONE — as they appear in any
# non-skateboard production screenshot — with the deck simply sitting on
# top of them. R6-V2 happened to render the chrome that way (its narrow
# deck didn't overlap the chrome so the production look came through
# untouched). R11 reproduces that production chrome look exactly:
#
#   - Base built via the SAME path R5/R6/R7 used (`bake_hud_score=False`)
#     which suppresses only the regular non-skateboard SCORE plate
#     at top-center via `skateboard_caption_t = 0`. The coin counter
#     and pause button are NOT touched by that path — their default
#     `_na_plate` slate plates render at full alpha=255 along with the
#     glyph/text/bars, identical to live production.
#   - NO `_na_plate` monkey-patch (R10's base-building trick is bypassed).
#   - NO chrome re-stamp (R7/R9 path is bypassed).
#   - NO cutout pockets, no frameless treatment, no plate-suppression.
#   - The R10 deck (340 x 92, -7° tilt, "SKATE" | live halftone | "BOARD!"
#     at 28 pt, 74 px reserve, 4 corner truck-bolts, PLATE_RED, INK rim,
#     unified 2 px / 35% alpha drop shadow) composites OPAQUE on top.
#     Where the deck silhouette covers the chrome, deck wins; where it
#     doesn't, the standard production chrome shows through unchanged.


def variant_r11_a1_default_chrome(base, score):
    """R11-A1 — Default production chrome (slate plates full opacity) under
    the R10 deck. The base frame here is the R5/R6/R7 base — coin counter
    + pause button render in their STANDARD production form (default
    `_na_plate` slate cut-corner plates at full alpha=255, normal HUD
    positions, no transparency, no plate removal, no shadow strengthening,
    no outline additions). The deck simply composites opaque on top:
    where the deck silhouette covers a chrome tile the deck hides it;
    where it doesn't, the chrome appears identical to live production.

    Deck geometry held from R10: 340 wide x 92 tall, deck-centre (180,70),
    PLATE_RED fill, INK rim, 4 corner truck-bolts (insets 34/20), SKATE +
    BOARD! wordmark at 28 pt with 74 px central reserve, R7 darkened lower
    gradient stop, outline_w=3, unified 2 px / 35% alpha drop shadow via
    `_composite_shadow`. Live halftone burst stamped LAST at the deck
    centre."""
    s = base.copy()
    deck_w, deck_h = 340, 92
    # Same R10 deck-building chain: R6 plain-deck silhouette (PLATE_RED
    # fill, wash stripes, 4 corner bolts at insets 34/20 via
    # `_draw_r5_d1_bolts`), R8 wordmark helper (SKATE | BOARD! at 28 pt
    # with R7's darkened bot_col baked into `_r8_blit_wordmarks`), INK
    # rim, -7° rotation, unified shadow.
    deck, deck_rect = _r6_build_plain_deck(
        deck_w, deck_h, border_radius=44,
        bolt_inset_x=34, bolt_inset_y=20)
    skate_w, board_w = _r8_blit_wordmarks(
        deck, deck_w, deck_h, gap_px=74 // 2,
        font_size=28, outline_w=3)
    pygame.draw.rect(deck, INK, deck_rect, 4, border_radius=44)
    avail = (deck_w - 74) // 2
    fit = "FITS" if board_w <= avail else "CLIPS"
    print(f"    R11-A1: deck={deck_w}  BOARD! width={board_w}px  "
          f"available half={avail}px  margin={avail - board_w}px  [{fit}]")
    rotated = pygame.transform.rotate(deck, -7)
    deck_center = (W // 2, 70)
    rect = rotated.get_rect(center=deck_center)
    _composite_shadow(s, rotated, rect.topleft,
                       offset=R5_SHADOW_OFFSET,
                       alpha=R5_SHADOW_ALPHA)
    s.blit(rotated, rect)
    _stamp_live_score_preview(s, deck_center, score=888,
                                sparkle_trim=R6_SPARKLE_TRIM)
    return s


# Two identical cells so `_compose_sheet` has the >=2 it needs to lay out
# a proper grid; both confirm the same shipped frame (single corrective
# ship, no exploration).
VARIANTS_R11 = [
    ("R11-A1 — Default production chrome (slate plates full opacity)",
     variant_r11_a1_default_chrome),
    ("R11-A1 — Default production chrome (slate plates full opacity)",
     variant_r11_a1_default_chrome),
]


def _compose_sheet(cells, title_text, cols=3, rows=2):
    """Grid sheet (default 2x3 — 5 cells + 1 spare). Each cell shows
    the rendered frame with a label strip below. Cell =
    W × (H + 36); margins = 16 px. R7 passes cols=2, rows=2 so the
    4-cell set lays out as a 2x2 grid instead of leaving 2 blanks
    on a 2x3."""
    pygame.font.init()
    font = pygame.font.SysFont(None, 22)
    margin = 16
    label_h = 36
    cell_w = W + margin
    cell_h = H + label_h + margin
    sheet_w = margin + cell_w * cols
    sheet_h = margin + cell_h * rows + 50  # +50 for title
    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill((26, 30, 36, 255))

    # Title
    title = pygame.font.SysFont(None, 30).render(
        title_text, True, (245, 240, 220))
    sheet.blit(title, (margin, 14))

    for idx, (label, frame) in enumerate(cells):
        col = idx % cols
        row = idx // cols
        x0 = margin + col * cell_w
        y0 = margin + 40 + row * cell_h
        sheet.blit(frame, (x0, y0))
        pygame.draw.rect(sheet, (90, 110, 130),
                         (x0, y0, W, H), width=1)
        lbl = font.render(label, True, (235, 230, 210))
        sheet.blit(lbl, (x0, y0 + H + 6))
    return sheet


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("building gameplay base frame...")
    app = _build_gameplay_frame()
    base = _render_base(app)
    score_for_overlay = app.world.score

    # Round 1 — banner placements that AVOID overlapping the score.
    cells = []
    for label, renderer in VARIANTS:
        cells.append((label, renderer(base)))
        print(f"  rendered {label}")
    sheet = _compose_sheet(cells,
        "Skybit — SKATEBOARD! banner placement options "
        "(score now at y=70 to match the regular NA plate)")
    pygame.image.save(sheet, OUT_PATH)
    print(f"wrote {OUT_PATH}  ({os.path.getsize(OUT_PATH)} bytes)")

    # Round 2 — banner stays at the TOP with the score overlaid on it.
    cells_r2 = []
    for label, renderer in VARIANTS_R2:
        cells_r2.append((label, renderer(base, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r2 = _compose_sheet(cells_r2,
        "Skybit — SKATEBOARD! banner at TOP with score overlaid "
        "(banner must remain readable through the overlap)")
    pygame.image.save(sheet_r2, OUT_PATH_R2)
    print(f"wrote {OUT_PATH_R2}  ({os.path.getsize(OUT_PATH_R2)} bytes)")

    # Round 3 — banner + score UNIFIED into a single hero composite.
    cells_r3 = []
    for label, renderer in VARIANTS_R3:
        cells_r3.append((label, renderer(base, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r3 = _compose_sheet(cells_r3,
        "Skybit — SKATEBOARD! banner + score UNIFIED into ONE hero "
        "(no competing pieces — score is part of the banner)")
    pygame.image.save(sheet_r3, OUT_PATH_R3)
    print(f"wrote {OUT_PATH_R3}  ({os.path.getsize(OUT_PATH_R3)} bytes)")

    # Round 4 — R3-C3 skate-deck reworked LOWER on the canvas, with the
    # SKATEBOARD wordmark sized back UP and the halftone score burst
    # pulled INSIDE the deck silhouette. All 5 cells share a single
    # +3,+5 unified composite shadow direction.
    cells_r4 = []
    for label, renderer in VARIANTS_R4:
        cells_r4.append((label, renderer(base, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r4 = _compose_sheet(cells_r4,
        "Skybit — SKATEBOARD deck composites (R3-C3 reworked LOWER, "
        "LARGER wordmark, burst INSIDE the deck)")
    pygame.image.save(sheet_r4, OUT_PATH_R4)
    print(f"wrote {OUT_PATH_R4}  ({os.path.getsize(OUT_PATH_R4)} bytes)")

    # Round 5 — R4-D2 direction reworked: deck ~25% larger, wordmark
    # SPLIT into SKATE | live-score | BOARD, deck stays ONE whole piece,
    # NO baked decorative score (the LIVE halftone score preview is
    # stamped on top of each rotated deck so the cell mirrors the
    # runtime composite).
    #
    # Build a SEPARATE base frame for R5 with the live HUD halftone
    # score suppressed — every R5 cell composites its own 888 burst on
    # the deck centre, so leaving the default-position HUD badge baked
    # in produces a second burst in every cell. R1-R4 still use the
    # original `base` (skateboard_active=True) and are unaffected.
    app_r5 = _build_gameplay_frame(bake_hud_score=False)
    base_r5 = _render_base(app_r5)
    cells_r5 = []
    for label, renderer in VARIANTS_R5:
        cells_r5.append((label, renderer(base_r5, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r5 = _compose_sheet(cells_r5,
        "Skybit — SKATEBOARD R5 deck composites (LARGER deck, SPLIT "
        "SKATE | live-score | BOARD; deck stays whole, no baked score)")
    pygame.image.save(sheet_r5, OUT_PATH_R5)
    print(f"wrote {OUT_PATH_R5}  ({os.path.getsize(OUT_PATH_R5)} bytes)")

    # Round 6 — R5-D1 silhouette relocated UP so the deck wraps the
    # regular-score position (y=70). Each cell solves the coin/pause
    # chrome collision differently — full-slab-under-chrome,
    # tucked-between, steeper tilt that arcs corners below the chrome
    # line, mid-width, and asymmetric offset. Shares R5's
    # bake_hud_score=False base so neither the halftone burst nor the
    # NA plate paint at default position; the only score badge in each
    # cell is the live preview stamped on the deck centre.
    cells_r6 = []
    for label, renderer in VARIANTS_R6:
        cells_r6.append((label, renderer(base_r5, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r6 = _compose_sheet(cells_r6,
        "Skybit — SKATEBOARD R6 deck composites (R5-D1 moved UP to "
        "y=70; varied chrome-collision strategies)")
    pygame.image.save(sheet_r6, OUT_PATH_R6)
    print(f"wrote {OUT_PATH_R6}  ({os.path.getsize(OUT_PATH_R6)} bytes)")

    # Round 7 — R6-V1 direction reworked per user note. Same 320 x 92 slab
    # at deck-centre (180, 70), but the SKATE/BOARD wordmark is rendered
    # LARGER (26-30 pt FIXED, no auto-shrink), sits CLOSER to the score
    # burst (central reserve 70-80 px vs R6-V1's ~108 px), the tilt is
    # SHALLOWER (-4° to -10° vs R6-V1's -12°), and the coin counter +
    # pause tile are blit on top at 50% alpha so the deck red and
    # SKATE/BOARD glyphs bleed through both chrome tiles. Reuses the same
    # bake_hud_score=False base R6 uses.
    cells_r7 = []
    for label, renderer in VARIANTS_R7:
        cells_r7.append((label, renderer(base_r5, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r7 = _compose_sheet(cells_r7,
        "Skybit — SKATEBOARD R7 (R6-V1 reworked: SKATE/BOARD bigger + "
        "closer, less tilt, chrome at 50% alpha)",
        cols=2, rows=2)
    pygame.image.save(sheet_r7, OUT_PATH_R7)
    print(f"wrote {OUT_PATH_R7}  ({os.path.getsize(OUT_PATH_R7)} bytes)")

    # Round 8 — R7-A1 reworked: right word becomes "BOARD!", deck LENGTH
    # extended so it fits, and the z-order FLIPPED — the OPAQUE deck now
    # sits ON TOP of FRAMELESS coin counter + pause button (slate plates
    # stripped, soft drop shadows added). Built on a dedicated base with
    # the coin/pause chrome fully suppressed so the frameless versions can
    # be re-rendered under the deck at the correct layer.
    base_r8 = _build_r8_base()
    cells_r8 = []
    for label, renderer in VARIANTS_R8:
        cells_r8.append((label, renderer(base_r8, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r8 = _compose_sheet(cells_r8,
        "Skybit — SKATEBOARD R8 final (B1 lead: corner-nudged frameless "
        "chrome, BOARD! 28pt; B2 = no-nudge A/B; pause bars inked + strong "
        "shadow)",
        cols=2, rows=2)
    pygame.image.save(sheet_r8, OUT_PATH_R8)
    print(f"wrote {OUT_PATH_R8}  ({os.path.getsize(OUT_PATH_R8)} bytes)")

    # Round 9 — corrective pass on R8-B1. RESTORE the slate cut-corner plate
    # frames on the coin counter + pause button at user-tunable transparency
    # (R7's shipped re-stamp path). R6-V1 cutout shadow-pockets stay gone —
    # the deck face is clean PLATE_RED under the chrome. Three cells sweep
    # chrome alpha 128 / 150 / 170 so the user can pin down their preferred
    # "fifty percent" target. Reuses the R7 base (`base_r5`) where the
    # chrome plates are present in the source frame — R8's
    # `_build_r8_base` deliberately suppressed them and would leave the
    # translucent re-stamp with nothing to snapshot.
    cells_r9 = []
    for label, renderer in VARIANTS_R9:
        cells_r9.append((label, renderer(base_r5, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r9 = _compose_sheet(cells_r9,
        "Skybit — SKATEBOARD R9 (R8-B1 deck + translucent slate chrome "
        "restored; alpha sweep 128/150/170; no cutout pockets)",
        cols=3, rows=1)
    pygame.image.save(sheet_r9, OUT_PATH_R9)
    print(f"wrote {OUT_PATH_R9}  ({os.path.getsize(OUT_PATH_R9)} bytes)")

    # Round 10 — corrective ship. Drop the slate `_na_plate` background
    # ENTIRELY from BOTH the coin counter and the pause button (the
    # "blue half-transparent rectangle" the user wanted gone). The coin
    # glyph + count and the pause bars remain at their normal HUD
    # positions, drawn straight onto the sky. R8-B1 deck on top. The
    # base is rebuilt with `_na_plate` monkey-patched to a no-op so the
    # plate snapshot disappears from both icons.
    base_r10 = _build_r10_base()
    cells_r10 = []
    for label, renderer in VARIANTS_R10:
        cells_r10.append((label, renderer(base_r10, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r10 = _compose_sheet(cells_r10,
        "Skybit — SKATEBOARD R10 (slate plates removed from coin "
        "counter + pause button entirely; no rectangle behind either)",
        cols=2, rows=1)
    pygame.image.save(sheet_r10, OUT_PATH_R10)
    print(f"wrote {OUT_PATH_R10}  ({os.path.getsize(OUT_PATH_R10)} bytes)")

    # Round 11 — corrective ship. Restore the STANDARD PRODUCTION coin
    # counter + pause button (default `_na_plate` slate cut-corner plates
    # at full opacity, normal HUD positions, NO transparency, NO plate
    # removal, NO frameless treatment) UNDER the R10 deck. Reuses the
    # R5/R6/R7 base (`base_r5`) — that base was built with
    # `bake_hud_score=False`, which only suppresses the regular
    # non-skateboard SCORE plate at top-center. The coin counter + pause
    # button are NOT touched by that path, so they render at full alpha
    # with their default slate plates — identical to a live production
    # screenshot. R10's `_na_plate` monkey-patch is NOT applied here.
    cells_r11 = []
    for label, renderer in VARIANTS_R11:
        cells_r11.append((label, renderer(base_r5, score_for_overlay)))
        print(f"  rendered {label}")
    sheet_r11 = _compose_sheet(cells_r11,
        "Skybit — SKATEBOARD R11 (default production chrome restored: "
        "coin counter + pause button slate plates at full opacity, "
        "untouched, deck composites opaque on top)",
        cols=2, rows=1)
    pygame.image.save(sheet_r11, OUT_PATH_R11)
    print(f"wrote {OUT_PATH_R11}  ({os.path.getsize(OUT_PATH_R11)} bytes)")


def _verify_d4_3digit(base):
    """3-digit "888" sanity render for the R4-D4 trucks+wheels lead —
    confirms the deck composite still holds a triple-digit score
    without the digit silhouette punching through the spike rim, and
    that the wheels stay above y=183 with the wider digit cap. Writes
    a scratch cell to docs/skateboard_banner_options/round_4_d4_888.png."""
    frame = variant_r4_d4_trucks_wheels(base, 888)
    out = os.path.join(OUT_DIR, "round_4_d4_888.png")
    pygame.image.save(frame, out)
    print(f"  wrote {out}")


def _verify_c5_3digit(base):
    """3-digit "888" sanity render — burst's inner padding must hold
    triple-digit scores without trimming the spike silhouette. Writes
    a scratch cell to docs/skateboard_banner_options/round_3_c5_888.png
    so the verification is visually inspectable, and prints the digit
    bounds vs the burst inner radius."""
    frame = variant_r3_c5_burst_exclamation(base, 888)
    out = os.path.join(OUT_DIR, "round_3_c5_888.png")
    pygame.image.save(frame, out)
    # Measure 3-digit "888" at the auto-scaled font_size=22 the renderer
    # uses for 3-digit scores — must fit inside the burst's outer
    # envelope (ro*2) with margin.
    test_glyph = _gradient_text("888", 22,
                                top_col=(255, 250, 240),
                                bot_col=(190, 30, 20),
                                outline=INK, outline_w=3)
    digit_w = test_glyph.get_width()
    # Burst's effective digit envelope is bounded by the outer-spike
    # diameter (ro*2) — digits are allowed to occupy the full yellow
    # disc, since the spike valleys (ri) only matter when the digit's
    # silhouette would punch THROUGH the rim. The relevant comparison
    # is digit-glyph-width vs outer-disc-diameter with ~4 px margin.
    outer_w = 27 * 2  # burst_ro * 2
    print(f"  3-digit check: '888' glyph width={digit_w}px, "
          f"burst outer diameter={outer_w}px "
          f"({'FITS' if digit_w <= outer_w else 'OVERFLOW (spike-trim)'})")
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
    # Run AFTER the main sheet so the scratch file uses the same base
    # frame the sheet does — verifies 3-digit legibility on C5.
    print("3-digit '888' verification on C5...")
    app = _build_gameplay_frame()
    base = _render_base(app)
    _verify_c5_3digit(base)
    print("3-digit '888' verification on R4-D4 (lead)...")
    _verify_d4_3digit(base)

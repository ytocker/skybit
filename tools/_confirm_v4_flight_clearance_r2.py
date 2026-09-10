#!/usr/bin/env python3
"""
flight-clearance confirm_purchase_v4 round 2 render.
All five art-director notes addressed:
  1. Warm backlit cabochon + brighter interior so item reads at 1x
  2. Gold rim ring + outer bloom (Rule 1). Bloom placed BEFORE disc so disc
     covers centre — only the outer halo around the perimeter shows.
     BLEND_ADD ignores source alpha; intensity lives in RGB magnitude only,
     so colour values must be kept small to avoid white blowout.
  3. Disc enlarged ~30% and lifted close to LEGENDARY banner
  4. Stamp replaced by bold diagonal ribbon; disc drawn on top (disc wins)
  5. Enhanced perforations, corner clip marks, stub notches
"""
import os, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, drop_shadow, bevel_rim, top_sheen, soft_glow,
    plain_text, price_chip, chip_body_stops, chip_body,
    _glyph_base, font, m, SS,
    GOLD_A_STOPS, GOLD_A_RIM_DARK as GOLD_RIM_DK, GOLD_A_RIM_BRIGHT as GOLD_RIM_BR,
)
from game.hud import _font
from game.draw import lerp_color

# Patch gloss_sweep so additive intensity lives in RGB magnitude, not alpha —
# prevents white blowout on gold ticket stock.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed

# ── palette ───────────────────────────────────────────────────────────────────
pal = {"gem": (255, 202, 104), "glow": (255, 168, 58), "deep": (150, 92, 22)}

STOCK_WARM = [(0.0, (224, 178, 62)), (0.42, (196, 148, 44)), (1.0, (152, 102, 24))]
STOCK_COLD = [(0.0, (130, 136, 158)), (0.50, (104, 110, 132)), (1.0, (70, 74, 96))]

# Brighter warm-amber cabochon interior — backlit so the item reads at 1× size.
# The store default is near-black; these values make the disc interior glow
# without washing the thumbnail's mid-tones.
CABO_LO_WARM = (110, 88, 40)
CABO_HI_WARM = (64, 50, 24)
CABO_LO_COLD = (84, 86, 126)
CABO_HI_COLD = (48, 50, 84)

POP_W, POP_H = 232, 292
CX = POP_W // 2
CARD_RAD = 15
# Disc enlarged ~30% and lifted to close dead space below LEGENDARY banner.
R_DISC  = 57     # was 44 in r1
CY_DISC = 116    # was 148 in r1 (lifted ~32 logical px)

DEMO_SKIN = "skin_jet_fighter"   # 12,000-coin legendary — matches the dialog price


# =============================================================================
# Local drawing primitives
# =============================================================================

def _confirm_chip(surf, cx, cy, h, affordable):
    """CONFIRM action button — same chip family DNA as the price chip."""
    text = "CONFIRM"
    f = font(h * 0.46 / SS)
    nw = _glyph_base(text, f, m(1.4)).get_width()
    pad = m(20)
    w = nw + pad * 2
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    if affordable:
        chip_body_stops(surf, r, h // 2, GOLD_A_STOPS, GOLD_RIM_DK, GOLD_RIM_BR,
                        gloss=64, gamma=1.04)
        col, kl = (54, 30, 4), None
    else:
        chip_body(surf, r, h // 2, (92, 98, 122), (50, 54, 76),
                  (14, 16, 28), (162, 170, 196), gloss=44)
        col, kl = (196, 202, 224), (20, 24, 40)
    plain_text(surf, text, f, r.center, col, shadow_a=0,
               tracking=m(1.4), weight=m(1.0), keyline=kl, kw=m(0.7))
    return r


def _perf_row(surf, y, x0, x1, ink):
    """Enhanced punched-hole perforation: slightly larger dots than r1, with
    a dark shadow ring around each to read crisper against gold stock."""
    dot_r = max(2, m(2.4))
    step  = m(6.5)
    x = x0 + m(3)
    while x <= x1 - m(3):
        pygame.draw.circle(surf, (0, 0, 0, 100), (x, y), dot_r + m(0.7))
        pygame.draw.circle(surf, ink, (x, y), dot_r)
        x += step


def _corner_clips(surf, body, ink_rgba):
    """Right-angle bracket marks at all four ticket corners — the printed-
    registration-mark affordance that sells the physical boarding-pass read."""
    clip = m(10)
    corners = [
        (body.x + m(3),     body.y + m(3),       1,  1),
        (body.right - m(3), body.y + m(3),       -1,  1),
        (body.x + m(3),     body.bottom - m(3),   1, -1),
        (body.right - m(3), body.bottom - m(3),  -1, -1),
    ]
    for bx, by, sx, sy in corners:
        pts = [(bx, by + sy * clip), (bx, by), (bx + sx * clip, by)]
        pygame.draw.lines(surf, ink_rgba, False, pts, max(1, m(1.2)))


def _diagonal_ribbon(big, cx, cy, body_w, affordable):
    """Bold filled diagonal band at -20° spanning the full ticket width.
    Drawn BEFORE the disc so the medallion wins at every crossing point —
    the ribbon appears to pass behind the disc, emerging on both sides."""
    if affordable:
        mid_col  = (124, 34, 10)
        edge_col = (162, 52, 18)
        text_col = (255, 216, 128)
        stripe_a = (240, 178, 88, 88)
    else:
        mid_col  = (55, 60, 88)
        edge_col = (78, 84, 118)
        text_col = (185, 192, 224)
        stripe_a = (158, 166, 208, 72)

    h_band = m(38)
    # Wide enough that after -20° rotation the band still runs edge to edge.
    w_band = int(body_w * 1.5)

    r_surf = pygame.Surface((w_band, h_band), pygame.SRCALPHA)
    for y in range(h_band):
        t = abs(2.0 * y / h_band - 1.0)
        col = lerp_color(mid_col, edge_col, t ** 0.55)
        pygame.draw.line(r_surf, (*col, 222), (0, y), (w_band - 1, y))

    pygame.draw.line(r_surf, stripe_a, (0, m(1)),        (w_band-1, m(1)),
                     max(1, m(1.6)))
    pygame.draw.line(r_surf, stripe_a, (0, h_band-m(2)), (w_band-1, h_band-m(2)),
                     max(1, m(1.6)))

    fb = font(13)
    plain_text(r_surf, "SKY CAPTAIN", fb, (w_band // 2, h_band // 2),
               text_col, shadow_a=90, tracking=m(1.8), weight=m(1.3))

    rot = pygame.transform.rotate(r_surf, -20)
    rr = rot.get_rect(center=(cx, cy))
    big.blit(rot, rr.topleft)


def _outer_rim_bloom(big, cx, cy, disc_r, color, layers=9, glow_px=None):
    """Additive outer bloom that only glows in the annular zone OUTSIDE the
    disc rim.  BLEND_ADD ignores source alpha — intensity lives in the RGB
    values.  Drawing (0,0,0,0) in the inner disc region on the source surface
    means BLEND_ADD adds 0 there, leaving the disc interior untouched."""
    if glow_px is None:
        glow_px = m(22)
    for i in range(layers, 0, -1):
        expand = int(glow_px * (layers - i + 0.5) / layers)
        outer_r = disc_r + expand + 1
        # inner cutoff = disc rim: disc covers all interior after being drawn
        inner_r = disc_r

        frac  = (layers - i) / max(1, layers - 1)
        scale = (1 - frac) ** 1.5
        col   = tuple(max(0, min(255, int(c * scale))) for c in color)
        if max(col) == 0:
            continue

        # SRCALPHA surface: fill with zeros, draw outer ring in col,
        # then zero inner disc area — BLEND_ADD adds 0 inside = no-op.
        s = pygame.Surface((outer_r * 2 + 4, outer_r * 2 + 4), pygame.SRCALPHA)
        s.fill((0, 0, 0, 0))
        oc = outer_r + 2
        pygame.draw.circle(s, col, (oc, oc), outer_r)
        if inner_r > 0:
            pygame.draw.circle(s, (0, 0, 0, 0), (oc, oc), inner_r)
        big.blit(s, (cx - oc, cy - oc), special_flags=pygame.BLEND_ADD)


def _legendary_header(big, body, affordable):
    """Dominant LEGENDARY banner — the first element the eye lands on.
    Larger than r1, with a warm bright keyline and an ornamental rule +
    diamond endpoints framing the top zone."""
    leg_col = (50, 28, 4)        if affordable else (212, 218, 236)
    leg_kl  = (255, 226, 152)    if affordable else (40, 44, 64)

    # Track sz separately from lf.get_height() — pygame font height != requested
    # size (internal leading makes it larger), so lf.get_height()/SS would drift
    # upward and the shrink loop would grow without bound.
    txt = "LEGENDARY"
    sz  = 34
    lf  = font(sz)
    while _glyph_base(txt, lf, m(1.2)).get_width() > body.w - m(14) and sz > 8:
        sz -= 1
        lf  = font(sz)

    cy_leg = body.y + m(22)
    plain_text(big, txt, lf, (CX * SS, cy_leg), leg_col,
               shadow_a=110 if affordable else 60,
               tracking=m(1.2), weight=m(1.5), keyline=leg_kl, kw=m(1.0))

    # Ornamental rule with small diamond endpoints beneath the banner
    rule_y = body.y + m(40)
    r_col  = (*((90, 54, 10) if affordable else (82, 88, 114)), 168)
    pygame.draw.line(big, r_col,
                     (body.x + m(18), rule_y), (body.right - m(18), rule_y),
                     max(1, m(1)))
    d = m(3)
    for rx in (body.x + m(18), body.right - m(18)):
        pygame.draw.polygon(big, r_col,
                            [(rx, rule_y - d), (rx + d, rule_y),
                             (rx, rule_y + d), (rx - d, rule_y)])


# =============================================================================
# Full popup render
# =============================================================================

def render_popup(affordable):
    big  = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    body = pygame.Rect(m(8), m(8), POP_W * SS - m(16), POP_H * SS - m(16))
    rad  = m(CARD_RAD)

    # ── ticket body ───────────────────────────────────────────────────────────
    drop_shadow(big, body, rad, blur=m(7), alpha=155, dy=m(4))
    stops = STOCK_WARM if affordable else STOCK_COLD
    big.blit(vgrad_stops(body.w, body.h, rad, stops, 255, gamma=1.12), body.topleft)
    top_sheen(big, body, rad, m(28), peak=52 if affordable else 28)

    edge_dk = (58, 34, 6)      if affordable else (20, 22, 36)
    edge_br = (255, 240, 190)  if affordable else (184, 192, 216)
    pygame.draw.rect(big, edge_dk, body, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, body, rad, edge_dk, (*edge_br, 230), w=max(1, m(1.8)))

    # Inner tray keyline
    tray = body.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*edge_br, 55), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))

    # Corner clip marks — sell the "real physical ticket" affordance
    _corner_clips(big, body, (*edge_dk, 120))

    # ── LEGENDARY banner (dominant first read) ────────────────────────────────
    _legendary_header(big, body, affordable)

    # ── Outer rim bloom: applied BEFORE disc so disc covers interior ──────────
    # BLEND_ADD ignores source alpha; only RGB magnitude drives intensity.
    # Keeping values like (22,14,3) means at most ~9×22=198 added near the rim,
    # which on the warm ticket stock (~200 R) capped to 255 = hot gold not white.
    cx_dev = CX * SS
    cy_dev = m(CY_DISC)
    if affordable:
        bloom_col = (22, 14, 3)    # warm gold tint
    else:
        bloom_col = (11, 13, 20)   # cool blue tint
    _outer_rim_bloom(big, cx_dev, cy_dev, m(R_DISC), bloom_col,
                     layers=9, glow_px=m(22))

    # ── diagonal ribbon BEFORE disc so disc wins the crossing ─────────────────
    _diagonal_ribbon(big, cx_dev, cy_dev, body.w, affordable)

    # ── medallion disc ────────────────────────────────────────────────────────
    # Warm ambient fill behind disc — any transparent thumbnail area glows amber.
    bg_col = (185, 140, 54) if affordable else (92, 96, 136)
    pygame.draw.circle(big, bg_col, (cx_dev, cy_dev), m(R_DISC))

    # Brighter warmer cabochon interior — backlit dome so the item reads at 1×
    cabo_lo = CABO_LO_WARM if affordable else CABO_LO_COLD
    cabo_hi = CABO_HI_WARM if affordable else CABO_HI_COLD
    sc.cabochon(big, cx_dev, cy_dev, m(R_DISC), cabo_lo, cabo_hi)

    # Thumbnail — modest additive lift to fight the dark cabochon tones without
    # blowing out bright skins (e.g. white-faced kitsune would saturate at +50).
    try:
        t       = sc.thumb(DEMO_SKIN, int(m(R_DISC) * 1.52))
        boosted = t.copy()
        boosted.fill((22, 18, 6, 0), special_flags=pygame.BLEND_RGB_ADD)
        r_t = boosted.get_rect(center=(cx_dev, cy_dev))
        big.blit(sc._rim_light(boosted), r_t.topleft, special_flags=pygame.BLEND_ADD)
        big.blit(boosted, r_t)
    except Exception:
        pygame.draw.circle(big, (*pal["gem"], 255), (cx_dev, cy_dev),
                           int(m(R_DISC) * 0.68))

    # Glass dome overlay
    sc.cabochon_glass(big, cx_dev, cy_dev, m(R_DISC), tint=pal["gem"])

    # Cool desaturating veil for can't-afford
    if not affordable:
        vr   = m(R_DISC) + m(4)
        veil = pygame.Surface((vr * 2, vr * 2), pygame.SRCALPHA)
        pygame.draw.circle(veil, (38, 42, 68, 148), (vr, vr), m(R_DISC))
        big.blit(veil, (cx_dev - vr, cy_dev - vr))

    # ── Crisp warm-gold rim ring AFTER glass (direct draw, non-additive) ─────
    # This is Rule 1: the perimeter ring MUST glow in the rarity tier colour.
    # Direct solid draw so the ring sits on top of the glass bezel cleanly.
    if affordable:
        ring_col = (255, 215, 85)
        ring_mid = (230, 168, 40)
        ring_dk  = (100, 62, 12)
    else:
        ring_col = (150, 158, 200)
        ring_mid = (110, 118, 160)
        ring_dk  = (46, 52, 84)

    # Outer glow ring (slightly outside disc radius)
    ring_w = max(3, m(3.2))
    pygame.draw.circle(big, ring_col, (cx_dev, cy_dev),
                       m(R_DISC) + ring_w // 2 + m(1), ring_w)
    # Subtle mid-tone ring just inside
    pygame.draw.circle(big, ring_mid, (cx_dev, cy_dev),
                       m(R_DISC) - m(1), max(1, m(1.5)))
    # Dark inner seat keyline
    pygame.draw.circle(big, ring_dk, (cx_dev, cy_dev),
                       m(R_DISC) - m(2.5), max(1, m(1)))

    # ── stub: enhanced perforations + corner notches + price + confirm ────────
    stub_y   = body.y + m(198)
    perf_ink = (44, 26, 6) if affordable else (24, 26, 42)
    _perf_row(big, stub_y, body.x + m(14), body.right - m(14), perf_ink)
    # Flanking semicircle notch cut-outs at stub edge (boarding pass tear mark)
    pygame.draw.circle(big, (0, 0, 0, 0), (body.x,     stub_y), m(5))
    pygame.draw.circle(big, (0, 0, 0, 0), (body.right, stub_y), m(5))

    price_chip(big, cx_dev, body.y + m(228), "12,000", m(21), affordable=affordable)
    _confirm_chip(big, cx_dev, body.y + m(258), m(23), affordable)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# =============================================================================
# Compose two-state review canvas (affordable left, can't-afford right)
# =============================================================================
CANVAS_W, CANVAS_H = 512, 388
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((8, 8, 20))

lab = _font(15, True)
for i, (aff, tag) in enumerate([(True, "AFFORDABLE"), (False, "CAN'T AFFORD")]):
    pop = render_popup(aff)
    half_cx = CANVAS_W // 4 + i * (CANVAS_W // 2)
    px = half_cx - POP_W // 2
    py = (CANVAS_H - POP_H) // 2 + 8
    canvas.blit(pop, (px, py))
    t = lab.render(tag, True, (210, 214, 230))
    canvas.blit(t, t.get_rect(center=(half_cx, py - 13)))

out = "/home/user/skybit/docs/confirm_purchase_v4/flight-clearance/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())

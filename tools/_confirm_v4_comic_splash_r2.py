"""confirm-purchase v4 -- COMIC-SPLASH round 2.

Addresses all five art-director notes from round 1 review:
  1. Caption chip plate darkened ~18% — it recedes behind LEGENDARY.
  2. Burst background is now pure amber/orange in affordable state (no purple/violet).
  3. Cold-state disc is fully grey/neutral (sat < 0.12) — grey glass body + true
     luminance desaturation of the thumbnail via surfarray (review-only; no numpy
     in the live game path).
  4. Bold solid 4px outer keyline around the whole popup card (comic panel border).
  5. Dark value moat strip across the top so LEGENDARY arcs read over the burst.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import numpy as np
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (cabochon, cabochon_glass, blit_thumb,
    vgrad_stops, soft_glow, CABO_LO, CABO_HI, m, SS, lerp_stops)
from game.hud import _font
from game.draw import lerp_color


# Apply gloss-sweep monkey-patch per the technical spec so the chip crown sheen
# is a controlled additive value (RGB magnitude) rather than blowing alpha white.
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

# FIX 2: Burst stops are now pure warm amber/orange — no purple or violet.
# Deep dark-amber core fades outward to bright golden-orange rim so the energy
# reads "fire" not "night", matching the LEGENDARY warm gold identity.
BURST_WARM = [
    (0.00, (28, 14,  4)),   # very deep amber-brown core
    (0.35, (82, 46, 12)),   # mid warm amber-brown
    (0.68, (204, 132, 40)), # bright amber
    (1.00, (252, 208, 94)), # pale gold rim
]
# Cold state: fully desaturated slate — no hue shift.
BURST_COLD = [
    (0.00, (16, 18, 20)),   # near-neutral near-black core
    (0.42, (42, 46, 50)),   # neutral dark slate
    (0.72, (90, 96, 102)),  # mid neutral grey
    (1.00, (146, 154, 160)),# pale grey rim
]

# LEGENDARY gradient fills (top->bottom): warm gold vs dulled pewter.
TITLE_WARM = ((255, 236, 168), (222, 158, 54))
TITLE_COLD = ((178, 182, 196), (108, 112, 130))
TITLE_KEY  = (40, 20, 4)
COLD_KEY   = (22, 24, 34)

# Supersample the whole popup then ONE smoothscale down -> crisp inked edges.
S = 3


def _mm(v):
    return int(round(v * S))


def _font_s(size, bold=True):
    return _font(max(1, int(round(size * S))), bold)


# ── item disc ─────────────────────────────────────────────────────────────────
# FIX 3: Cold disc uses grey glass body and a true luminance desaturation of
# the thumbnail so the disc reads sat < 0.12 in the can't-afford panel.
def _desaturate_surf(surf):
    """Replace every pixel's RGB with its luminance (BT.601 weights) so the
    surface reads fully grey. Alpha channel is preserved. Review-only helper —
    the live game never needs this path, so numpy is acceptable here."""
    # Work on a copy so the original thumb cache stays untouched.
    out = surf.copy()
    arr3 = pygame.surfarray.array3d(out)  # shape (w, h, 3), uint8
    lum  = (arr3[:, :, 0].astype(np.float32) * 0.299 +
            arr3[:, :, 1].astype(np.float32) * 0.587 +
            arr3[:, :, 2].astype(np.float32) * 0.114).clip(0, 255).astype(np.uint8)
    arr3[:, :, 0] = lum
    arr3[:, :, 1] = lum
    arr3[:, :, 2] = lum
    pygame.surfarray.blit_array(out, arr3)
    return out


def _disc(r, affordable=True):
    DS = r * 2 + _mm(40)
    ss = pygame.Surface((DS, DS), pygame.SRCALPHA)
    cx = cy = DS // 2

    if affordable:
        glass_lo   = CABO_LO        # canonical indigo-blue glass
        glass_hi   = CABO_HI
        ring_col   = pal["gem"]     # warm gold ring
        glass_tint = pal["gem"]
    else:
        # Fully neutral grey so the disc carries zero hue bias in the cold panel.
        glass_lo   = (48, 48, 48)
        glass_hi   = (15, 15, 15)
        ring_col   = (155, 155, 155)
        glass_tint = (170, 170, 170)

    cabochon(ss, cx, cy, r, glass_lo, glass_hi, ring=ring_col, ring_a=50)

    try:
        from game import store_cards as _sc
        from game.store_cards import thumb as _thumb
        raw = _thumb("skin_classic", int(r * 1.5))
        if not affordable:
            # True luminance desaturation so sat < 0.12 (thumbnail has vivid parrot hues).
            raw = _desaturate_surf(raw)
        t_r = raw.get_rect(center=(cx, cy))
        ss.blit(raw, t_r.topleft)
    except Exception:
        pygame.draw.circle(ss, (*ring_col, 255), (cx, cy), int(r * 0.7))

    cabochon_glass(ss, cx, cy, r, tint=glass_tint)
    return ss, cx, cy


# ── irregular inked border ─────────────────────────────────────────────────────
def _border_pts(w, h, inset):
    """Comic-panel keyline: rectangle perimeter sampled at sparse points, each
    nudged by a small deterministic perpendicular jitter for a hand-inked feel."""
    import random
    rng = random.Random(41)
    jit = _mm(4)
    x0, y0, x1, y1 = inset, inset, w - inset, h - inset
    pts = []

    def edge(ax, ay, bx, by, nx, ny, n):
        for i in range(n):
            t = i / n
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t
            j = rng.uniform(-jit, jit)
            pts.append((x + nx * j, y + ny * j))

    edge(x0, y0, x1, y0,  0, -1, 7)
    edge(x1, y0, x1, y1,  1,  0, 8)
    edge(x1, y1, x0, y1,  0,  1, 7)
    edge(x0, y1, x0, y0, -1,  0, 8)
    return pts


# ── radial sky-burst ground + speed lines ─────────────────────────────────────
def _burst(w, h, cx, cy, maxr, stops):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    step = max(2, _mm(2))
    for r in range(int(maxr), 0, -step):
        t = r / maxr
        c = lerp_stops(stops, t)
        pygame.draw.circle(surf, (*c, 255), (int(cx), int(cy)), r)
    return surf


def _speed_lines(surf, cx, cy, r_start, maxr, stops, n=40):
    seg = _mm(7)
    for k in range(n):
        ang = 2 * math.pi * k / n + 0.06
        dx, dy = math.cos(ang), math.sin(ang)
        r = r_start
        while r < maxr:
            r2 = min(maxr, r + seg)
            t = ((r + r2) * 0.5) / maxr
            base = lerp_stops(stops, t)
            col = tuple(int(c * 0.60) for c in base)
            pygame.draw.line(surf, (*col, 255),
                             (cx + dx * r, cy + dy * r),
                             (cx + dx * r2, cy + dy * r2), max(1, _mm(1.3)))
            r = r2


# ── FIX 5: dark value moat behind LEGENDARY ───────────────────────────────────
def _moat_strip(surf, w, h):
    """Dark vertical gradient across the top of the popup so burst spokes behind
    LEGENDARY are always a dark backing — the text never reads against a pale spoke.
    Fades cleanly from near-opaque at the crown to transparent below the text band."""
    moat_h = _mm(115)
    moat = pygame.Surface((w, moat_h), pygame.SRCALPHA)
    for y in range(moat_h):
        # gentle ease so the transition into the open burst isn't a hard line
        a = int(168 * (1 - y / moat_h) ** 0.85)
        if a <= 0:
            continue
        pygame.draw.line(moat, (0, 0, 0, a), (0, y), (w - 1, y))
    surf.blit(moat, (0, 0))


# ── arced LEGENDARY title ──────────────────────────────────────────────────────
def _compose_letter(ch, f, top, bot, keyline, kw):
    g = f.render(ch, True, (255, 255, 255))
    w, hh = g.get_size()
    pad = kw * 2 + _mm(3)
    out = pygame.Surface((w + pad * 2, hh + pad * 2), pygame.SRCALPHA)
    kl = g.copy()
    kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for a in range(0, 360, 30):
        dx = int(round(kw * math.cos(math.radians(a))))
        dy = int(round(kw * math.sin(math.radians(a))))
        out.blit(kl, (pad + dx, pad + dy))
    grad = pygame.Surface((w, hh), pygame.SRCALPHA)
    for y in range(hh):
        c = lerp_color(top, bot, y / max(1, hh - 1))
        pygame.draw.line(grad, (*c, 255), (0, y), (w, y))
    grad.blit(g, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(grad, (pad, pad))
    return out


def _arc_title(surf, text, cx, cy_o, radius, f, top, bot, keyline, kw):
    widths = [f.size(ch)[0] for ch in text]
    gap    = _mm(2)
    extents = [(w + gap) / radius for w in widths]
    total   = sum(extents)
    cur     = -math.pi / 2 - total / 2
    for ch, w, e in zip(text, widths, extents):
        ca   = cur + e / 2
        cur += e
        px   = cx + radius * math.cos(ca)
        py   = cy_o + radius * math.sin(ca)
        letter = _compose_letter(ch, f, top, bot, keyline, kw)
        rot    = -(math.degrees(ca) + 90)
        letter = pygame.transform.rotate(letter, rot)
        surf.blit(letter, letter.get_rect(center=(px, py)))


# ── starburst caption chip ─────────────────────────────────────────────────────
def _starburst(surf, cx, cy, rx_out, ry_out, rx_in, ry_in, pts, color, keyline):
    poly = []
    for i in range(pts * 2):
        rx = rx_out if i % 2 == 0 else rx_in
        ry = ry_out if i % 2 == 0 else ry_in
        a  = math.pi * i / pts - math.pi / 2
        poly.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    sh = [(x + _mm(2), y + _mm(3)) for x, y in poly]
    pygame.draw.polygon(surf, (0, 0, 0, 150), sh)
    pygame.draw.polygon(surf, color, poly)
    pygame.draw.polygon(surf, keyline, poly, width=max(1, _mm(1.6)))


def _coin(surf, cx, cy, r, rim):
    body = vgrad_stops(r * 2, r * 2, r, sc.GOLD_A_STOPS, 255, gamma=1.05)
    surf.blit(body, (cx - r, cy - r))
    pygame.draw.circle(surf, rim, (cx, cy), r, max(1, _mm(1.2)))
    f = _font_s(r * 0.9 / S, True)
    g = f.render("$", True, sc.GOLD_A_NUM)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _flat_text(surf, txt, f, center, fill, keyline, kw):
    g  = f.render(txt, True, (255, 255, 255))
    kl = g.copy()
    kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r  = g.get_rect(center=center)
    for a in range(0, 360, 45):
        dx = int(round(kw * math.cos(math.radians(a))))
        dy = int(round(kw * math.sin(math.radians(a))))
        surf.blit(kl, (r.x + dx, r.y + dy))
    img = g.copy()
    img.fill((*fill, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, r)


# FIX 1: caption chip plate darkened ~18% across every colour variable.
# The chip delivers price information — it must recede behind LEGENDARY and disc.
def _caption(surf, cx, cy, affordable, price):
    if affordable:
        # Starburst: was (250, 196, 92) → darkened ~18% → (205, 161, 75)
        burst_c  = (205, 161, 75, 255)
        burst_k  = (56, 30, 6)
        # Pill plate: was (30,24,16)/(14,11,8) → ~18% darker
        pill_top = (25, 20, 13)
        pill_bot = (12,  9,  7)
        # Rim: was (236,202,116) → (194,166,95)
        rim      = (194, 166, 95)
        price_col   = (255, 232, 158)
        num_col     = (52, 30, 6)
        confirm_col = (255, 236, 168)
        confirm_key = TITLE_KEY
    else:
        # Starburst: was (150,156,176) → (123,128,144)
        burst_c  = (123, 128, 144, 255)
        burst_k  = (34, 38, 52)
        # Pill plate: was (26,28,40)/(14,15,24) → ~18% darker
        pill_top = (21, 23, 33)
        pill_bot = (11, 12, 20)
        # Rim: was (150,158,182) → (123,130,149)
        rim      = (123, 130, 149)
        price_col   = (214, 220, 234)
        num_col     = (30, 34, 48)
        confirm_col = (196, 202, 220)
        confirm_key = COLD_KEY

    _starburst(surf, cx, cy, _mm(90), _mm(42), _mm(68), _mm(30), 13,
               burst_c, burst_k)

    pw, ph = _mm(122), _mm(46)
    r    = pygame.Rect(cx - pw // 2, cy - ph // 2, pw, ph)
    body = vgrad_stops(pw, ph, ph // 2, [(0.0, pill_top), (1.0, pill_bot)], 255)
    surf.blit(body, r.topleft)
    sc.gloss_sweep(surf, r, ph // 2, peak=46)
    pygame.draw.rect(surf, (4, 4, 10), r, width=max(1, _mm(2)), border_radius=ph // 2)
    pygame.draw.rect(surf, rim, r.inflate(-_mm(3), -_mm(3)),
                     width=max(1, _mm(1.4)), border_radius=ph // 2)

    fnum  = _font_s(15, True)
    label = f"{price:,}"
    coin_r = _mm(11)
    nw     = fnum.size(label)[0]
    inner  = coin_r * 2 + _mm(6) + nw
    x      = cx - inner // 2
    _coin(surf, x + coin_r, r.y + ph // 2, coin_r,
          num_col if not affordable else (120, 74, 14))
    _flat_text(surf, label, fnum,
               (x + coin_r * 2 + _mm(6) + nw // 2, r.y + ph // 2),
               price_col, (10, 8, 4) if affordable else (10, 12, 20), _mm(1))

    fc   = _font_s(11.5, True)
    word = "CONFIRM" if affordable else "NOT ENOUGH"
    _flat_text(surf, word, fc, (cx, cy + _mm(30)), confirm_col, confirm_key, _mm(1.3))


# ── popup ─────────────────────────────────────────────────────────────────────
POP_W, POP_H = 236, 312


def _popup(affordable):
    w, h = POP_W * S, POP_H * S
    surf  = pygame.Surface((w, h), pygame.SRCALPHA)

    disc_cx, disc_cy = w // 2, int(h * 0.545)
    disc_r = _mm(52)
    maxr   = math.hypot(w, h)
    stops  = BURST_WARM if affordable else BURST_COLD

    # burst ground + speed spokes, clipped to the inked border polygon.
    ground = _burst(w, h, disc_cx, disc_cy, maxr, stops)
    _speed_lines(ground, disc_cx, disc_cy, disc_r + _mm(6), maxr, stops, n=40)

    inset = _mm(7)
    pts   = _border_pts(w, h, inset)
    mask  = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    ground.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(ground, (0, 0))

    # FIX 5: dark value moat behind the LEGENDARY band (top ~35% of the popup).
    _moat_strip(surf, w, h)

    # arced LEGENDARY across the top — the first read, punchy and dominant.
    title_top, title_bot = (TITLE_WARM if affordable else TITLE_COLD)
    tkey   = TITLE_KEY if affordable else COLD_KEY
    ftitle = _font_s(30, True)
    _arc_title(surf, "LEGENDARY", disc_cx, _mm(44) + _mm(150), _mm(150),
               ftitle, title_top, title_bot, tkey, _mm(2.4))

    # item disc dead-centre with a warm rarity-ring glow (affordable only).
    if affordable:
        soft_glow(surf, disc_cx, disc_cy, disc_r + _mm(10), pal["glow"], 24, layers=8)
    disc, dcx, dcy = _disc(disc_r, affordable=affordable)
    surf.blit(disc, (disc_cx - dcx, disc_cy - dcy))

    # starburst price / CONFIRM caption chip at the foot.
    _caption(surf, disc_cx, int(h * 0.84), affordable, 4800)

    # Inked comic polygon keyline (slight jitter for hand-drawn feel).
    pygame.draw.polygon(surf, (6, 5, 12), pts, width=max(1, _mm(5)))
    pygame.draw.polygon(surf, (2, 2, 6),  pts, width=max(1, _mm(1.4)))

    # FIX 4: solid 4px outer rect keyline so the card reads as a defined comic
    # panel border — clean and unambiguous against any background.
    pygame.draw.rect(surf, (18, 14, 8), (0, 0, w, h), width=_mm(4))

    return pygame.transform.smoothscale(surf, (POP_W, POP_H))


# ── review sheet ──────────────────────────────────────────────────────────────
def main():
    W, H = 500, 380
    sheet = pygame.Surface((W, H))
    sheet.fill((8, 8, 20))

    for i, aff in enumerate((True, False)):
        pop    = _popup(aff)
        half_x = i * (W // 2)
        px     = half_x + (W // 2 - POP_W) // 2
        py     = (H - POP_H) // 2
        sheet.blit(pop, (px, py))
        lbl = _font(14, True)
        cap = "AFFORDABLE" if aff else "CAN'T AFFORD"
        g   = lbl.render(cap, True, (232, 224, 210))
        sheet.blit(g, g.get_rect(center=(half_x + W // 4, 20)))

    out = "/home/user/skybit/docs/confirm_purchase_v4/comic-splash/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({W}x{H})")


if __name__ == "__main__":
    main()

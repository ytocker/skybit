"""confirm-purchase v4 -- COMIC-SPLASH round 1.

A comic-book action-splash confirm popup: irregular inked keyline border, a
radial sky-burst ground with darkening speed-line spokes firing off the item
disc, a heavy arced LEGENDARY title dominating the top, the glass item disc
dead-centre with a warm rarity ring, and a starburst price/CONFIRM caption chip
at the foot. Two states: affordable (warm burst, lit) vs can't-afford (cold,
dulled). Review-only render -> docs/confirm_purchase_v4/comic-splash/round_1.png.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (cabochon, cabochon_glass, blit_thumb,
    vgrad_stops, soft_glow, CABO_LO, CABO_HI, m, SS, lerp_stops)
from game.hud import _font
from game.draw import lerp_color


# The gloss-sweep fix from the brief: the shipped store gloss_sweep tints toward
# white; here we want a value-controlled additive crown sheen for the caption chip.
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

# radial burst ramps: deep indigo core -> warm gold-amber rim (affordable),
# cold slate core -> pale grey rim (can't-afford).
BURST_WARM = [(0.00, (34, 26, 82)), (0.40, (86, 54, 96)),
              (0.72, (196, 122, 42)), (1.00, (242, 188, 84))]
BURST_COLD = [(0.00, (18, 20, 40)), (0.42, (44, 50, 74)),
              (0.72, (92, 100, 126)), (1.00, (150, 158, 182))]

# LEGENDARY fills (top->bottom gradient), warm gold vs dulled pewter.
TITLE_WARM = ((255, 236, 168), (222, 158, 54))
TITLE_COLD = ((178, 182, 196), (108, 112, 130))
TITLE_KEY = (40, 20, 4)
COLD_KEY = (22, 24, 34)

# Supersample the whole popup, then ONE smoothscale down -> crisp inked edges.
S = 3


def _mm(v):
    return int(round(v * S))


def _font_s(size, bold=True):
    return _font(max(1, int(round(size * S))), bold)


# ── item disc (per the brief helper, scaled to S) ─────────────────────────────
def _disc(r):
    DS = r * 2 + _mm(40)
    ss = pygame.Surface((DS, DS), pygame.SRCALPHA)
    cx = cy = DS // 2
    cabochon(ss, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        blit_thumb(ss, "skin_classic", cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(ss, (*pal["gem"], 255), (cx, cy), int(r * 0.7))
    cabochon_glass(ss, cx, cy, r, tint=pal["gem"])
    return ss, cx, cy


# ── irregular inked border ────────────────────────────────────────────────────
def _border_pts(w, h, inset):
    """A comic-panel keyline: a rectangle whose perimeter is sampled at a handful
    of points, each nudged by a small deterministic perpendicular jitter so the
    edge reads hand-inked, not machine-straight."""
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

    edge(x0, y0, x1, y0, 0, -1, 7)   # top   (outward normal up)
    edge(x1, y0, x1, y1, 1, 0, 8)    # right
    edge(x1, y1, x0, y1, 0, 1, 7)    # bottom
    edge(x0, y1, x0, y0, -1, 0, 8)   # left
    return pts


# ── radial sky-burst ground + speed lines ────────────────────────────────────
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


# ── arced LEGENDARY title ─────────────────────────────────────────────────────
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
    gap = _mm(2)
    extents = [(w + gap) / radius for w in widths]
    total = sum(extents)
    cur = -math.pi / 2 - total / 2
    for ch, w, e in zip(text, widths, extents):
        ca = cur + e / 2
        cur += e
        px = cx + radius * math.cos(ca)
        py = cy_o + radius * math.sin(ca)
        letter = _compose_letter(ch, f, top, bot, keyline, kw)
        rot = -(math.degrees(ca) + 90)
        letter = pygame.transform.rotate(letter, rot)
        surf.blit(letter, letter.get_rect(center=(px, py)))


# ── starburst caption chip ────────────────────────────────────────────────────
def _starburst(surf, cx, cy, rx_out, ry_out, rx_in, ry_in, pts, color, keyline):
    poly = []
    for i in range(pts * 2):
        rx = rx_out if i % 2 == 0 else rx_in
        ry = ry_out if i % 2 == 0 else ry_in
        a = math.pi * i / pts - math.pi / 2
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
    g = f.render(txt, True, (255, 255, 255))
    kl = g.copy()
    kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = g.get_rect(center=center)
    for a in range(0, 360, 45):
        dx = int(round(kw * math.cos(math.radians(a))))
        dy = int(round(kw * math.sin(math.radians(a))))
        surf.blit(kl, (r.x + dx, r.y + dy))
    img = g.copy()
    img.fill((*fill, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, r)


def _caption(surf, cx, cy, affordable, price):
    if affordable:
        burst_c = (250, 196, 92, 255)
        burst_k = (56, 30, 6)
        pill_top, pill_bot = (30, 24, 16), (14, 11, 8)
        rim = (236, 202, 116)
        price_col = (255, 232, 158)
        num_col = (52, 30, 6)
        confirm_col = (255, 236, 168)
        confirm_key = TITLE_KEY
    else:
        burst_c = (150, 156, 176, 255)
        burst_k = (34, 38, 52)
        pill_top, pill_bot = (26, 28, 40), (14, 15, 24)
        rim = (150, 158, 182)
        price_col = (214, 220, 234)
        num_col = (30, 34, 48)
        confirm_col = (196, 202, 220)
        confirm_key = COLD_KEY

    _starburst(surf, cx, cy, _mm(90), _mm(42), _mm(68), _mm(30), 13,
               burst_c, burst_k)

    pw, ph = _mm(122), _mm(46)
    r = pygame.Rect(cx - pw // 2, cy - ph // 2, pw, ph)
    body = vgrad_stops(pw, ph, ph // 2, [(0.0, pill_top), (1.0, pill_bot)], 255)
    surf.blit(body, r.topleft)
    sc.gloss_sweep(surf, r, ph // 2, peak=46)
    pygame.draw.rect(surf, (4, 4, 10), r, width=max(1, _mm(2)), border_radius=ph // 2)
    pygame.draw.rect(surf, rim, r.inflate(-_mm(3), -_mm(3)),
                     width=max(1, _mm(1.4)), border_radius=ph // 2)

    fnum = _font_s(15, True)
    label = f"{price:,}"
    coin_r = _mm(11)
    nw = fnum.size(label)[0]
    inner = coin_r * 2 + _mm(6) + nw
    x = cx - inner // 2
    _coin(surf, x + coin_r, r.y + ph // 2, coin_r, num_col if not affordable else (120, 74, 14))
    _flat_text(surf, label, fnum, (x + coin_r * 2 + _mm(6) + nw // 2, r.y + ph // 2),
               price_col, (10, 8, 4) if affordable else (10, 12, 20), _mm(1))

    fc = _font_s(11.5, True)
    word = "CONFIRM" if affordable else "NOT ENOUGH"
    _flat_text(surf, word, fc, (cx, cy + _mm(30)), confirm_col, confirm_key, _mm(1.3))


# ── popup ─────────────────────────────────────────────────────────────────────
POP_W, POP_H = 236, 312


def _popup(affordable):
    w, h = POP_W * S, POP_H * S
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    disc_cx, disc_cy = w // 2, int(h * 0.545)
    disc_r = _mm(52)
    maxr = math.hypot(w, h)
    stops = BURST_WARM if affordable else BURST_COLD

    # burst ground + speed spokes, clipped to the inked border polygon.
    ground = _burst(w, h, disc_cx, disc_cy, maxr, stops)
    _speed_lines(ground, disc_cx, disc_cy, disc_r + _mm(6), maxr, stops, n=40)

    inset = _mm(7)
    pts = _border_pts(w, h, inset)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    ground.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(ground, (0, 0))

    # arced LEGENDARY across the top — the first read.
    title_top, title_bot = (TITLE_WARM if affordable else TITLE_COLD)
    tkey = TITLE_KEY if affordable else COLD_KEY
    ftitle = _font_s(30, True)
    _arc_title(surf, "LEGENDARY", disc_cx, _mm(44) + _mm(150), _mm(150),
               ftitle, title_top, title_bot, tkey, _mm(2.4))

    # item disc dead-centre with a warm rarity-ring glow.
    if affordable:
        soft_glow(surf, disc_cx, disc_cy, disc_r + _mm(10), pal["glow"], 24, layers=8)
    disc, dcx, dcy = _disc(disc_r)
    surf.blit(disc, (disc_cx - dcx, disc_cy - dcy))
    if not affordable:
        dull = pygame.Surface((disc_r * 2 + _mm(6),) * 2, pygame.SRCALPHA)
        pygame.draw.circle(dull, (66, 70, 86, 150),
                           (disc_r + _mm(3), disc_r + _mm(3)), disc_r)
        surf.blit(dull, (disc_cx - disc_r - _mm(3), disc_cy - disc_r - _mm(3)))

    # starburst price / CONFIRM caption chip at the foot.
    _caption(surf, disc_cx, int(h * 0.84), affordable, 4800)

    # heavy inked keyline last so it caps every layer.
    pygame.draw.polygon(surf, (6, 5, 12), pts, width=max(1, _mm(5)))
    pygame.draw.polygon(surf, (2, 2, 6), pts, width=max(1, _mm(1.4)))

    return pygame.transform.smoothscale(surf, (POP_W, POP_H))


# ── sheet ─────────────────────────────────────────────────────────────────────
def main():
    W, H = 500, 380
    sheet = pygame.Surface((W, H))
    sheet.fill((8, 8, 20))

    for i, aff in enumerate((True, False)):
        pop = _popup(aff)
        half_x = i * (W // 2)
        px = half_x + (W // 2 - POP_W) // 2
        py = (H - POP_H) // 2
        sheet.blit(pop, (px, py))
        lbl = _font(14, True)
        cap = "AFFORDABLE" if aff else "CAN'T AFFORD"
        g = lbl.render(cap, True, (232, 224, 210))
        sheet.blit(g, g.get_rect(center=(half_x + W // 4, 20)))

    out = "/home/user/skybit/docs/confirm_purchase_v4/comic-splash/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({W}x{H})")


if __name__ == "__main__":
    main()

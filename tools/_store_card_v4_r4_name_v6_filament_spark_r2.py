import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import math, sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game import store_catalog
from game.hud import _font
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, _glyph_base, _stamp_bold,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36

# 8-neighborhood, used to find stroke-edge pixels AND to derive the outward
# surface normal (sum of the directions that point into empty space) so a fleck
# can be shed OFF the contour into the surrounding cream halo band.
_NB8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


_SPARKS_ON = True  # toggled off by the 1x validation harness to diff the fleck pass


def _name_filament_spark(big, name, cx, cy, max_w):
    import random
    sz = 13.5
    f = font(sz)
    while sum(f.size(c)[0] for c in name) > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)

    advances = [f.size(c)[0] for c in name]
    total_w = sum(advances)
    x0 = cx - total_w // 2

    # PASS 1: Standard per-glyph filament halo (baseline, normal-alpha)
    RINGS = [
        (m(6), (218, 208, 182), 90),   # champagne atmospheric
        (m(3), (250, 244, 225), 150),  # ivory mid
        (m(1), (255, 255, 252), 210),  # warm-white hot-core rim
    ]
    x = x0
    for char, adv in zip(name, advances):
        tile = _stamp_bold(_glyph_base(char, f, 0), m(0.8))
        tw, th = tile.get_size()
        gx = x + adv // 2 - tw // 2
        gy = cy - th // 2
        for radius, col, alpha in RINGS:
            tinted = tile.copy()
            tinted.fill((*col, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            steps = max(16, radius * 4)
            for i in range(steps):
                angle = 2 * math.pi * i / steps
                ox = int(round(math.cos(angle) * radius))
                oy = int(round(math.sin(angle) * radius))
                big.blit(tinted, (gx + ox, gy + oy))
        x += adv

    # PASS 2: Shed a few bright, DETACHED flecks off each glyph's stroke edges.
    # A fleck is not a highlight on the rim (that reads as the halo, not a
    # particle) — it is a hot speck that has left the contour. So each spark is
    # (a) pure white to separate it from the (255,255,252) hot-rim tint, (b)
    # nudged 1-3 logical px OUTWARD along the surface normal into the cream halo
    # band, (c) ringed by a dark navy disc so it sits against a darker surround,
    # and (d) given a solid m(1) core so it survives the 0.5 downscale as a
    # discrete point instead of averaging away sub-pixel. Few, punchy flecks:
    # more dots only means more that vanish. Everything stays inside each glyph's
    # advance-width x-span so the dark inter-glyph gaps are never contaminated.
    rng = random.Random(hash(name) & 0xFFFFFFFF)  # seeded by name, stable per render
    if not _SPARKS_ON:
        plain_text(big, name, f, (cx, cy), (250, 244, 225), shadow_a=0,
                   weight=m(0.8), keyline=(8, 8, 20), kw=m(0.5))
        return
    W, H = big.get_size()
    core_w = max(2, m(1))       # 2px solid core -> one bright ship-pixel after downscale
    ring_r = m(1.5)             # navy separation disc radius

    x = x0
    for char, adv in zip(name, advances):
        tile = _stamp_bold(_glyph_base(char, f, 0), m(0.8))
        tw, th = tile.get_size()
        gx = x + adv // 2 - tw // 2
        gy = cy - th // 2

        # Collect every stroke-edge pixel plus its outward normal.
        candidates = []
        for py in range(th):
            for px in range(tw):
                if tile.get_at((px, py)).a < 30:
                    continue
                ndx = ndy = 0
                is_edge = False
                for dx, dy in _NB8:
                    nx, ny = px + dx, py + dy
                    empty = not (0 <= nx < tw and 0 <= ny < th) or tile.get_at((nx, ny)).a < 30
                    if empty:
                        is_edge = True
                        ndx += dx
                        ndy += dy
                if not is_edge:
                    continue
                nl = math.hypot(ndx, ndy)
                if nl == 0:
                    continue
                candidates.append((px, py, ndx / nl, ndy / nl))

        # Pick only 3-6 well-spread flecks per glyph.
        rng.shuffle(candidates)
        target = rng.randint(3, 6)
        # x-span the fleck must stay within so inter-glyph gaps stay dark.
        lo_x = x + core_w
        hi_x = x + adv - core_w
        if hi_x < lo_x:
            lo_x = hi_x = x + adv // 2
        chosen = []
        for px, py, nx_, ny_ in candidates:
            if len(chosen) >= target:
                break
            dist = m(1) + rng.random() * m(2)          # 1-3 logical px outward
            sx = gx + px + int(round(nx_ * dist))
            sy = gy + py + int(round(ny_ * dist))
            sx = max(lo_x, min(hi_x, sx))
            sy = max(ring_r + 1, min(H - ring_r - 1, sy))
            if any(abs(sx - ox) + abs(sy - oy) < m(3) for ox, oy in chosen):
                continue
            chosen.append((sx, sy))

        for sx, sy in chosen:
            # Navy separation disc (normal alpha) darkens the cream halo so the
            # fleck reads as detached from the stroke, not part of the glow.
            navy = pygame.Surface((ring_r * 2 + 2, ring_r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(navy, (12, 11, 28, 165), (ring_r + 1, ring_r + 1), ring_r)
            big.blit(navy, (sx - ring_r - 1, sy - ring_r - 1))
            # Additive white: faint bloom + a solid 2px core that downscales to a
            # single discrete sparkle pixel.
            soft_glow(big, sx, sy, m(1.5), (255, 255, 255), 85, layers=3)
            core = pygame.Surface((core_w, core_w), pygame.SRCALPHA)
            core.fill((255, 255, 255, 255))
            big.blit(core, (sx - core_w // 2, sy - core_w // 2), special_flags=pygame.BLEND_ADD)

        x += adv

    # PASS 3: Crisp ivory body last
    plain_text(big, name, f, (cx, cy), (250, 244, 225), shadow_a=0,
               weight=m(0.8), keyline=(8, 8, 20), kw=m(0.5))


def _neutral_band(big, rect, plinth_top, rad):
    ph = rect.bottom - plinth_top
    band = vgrad_stops(rect.w, ph, 0, [(0.0, (28, 24, 44)), (1.0, (14, 12, 26))], 255)
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h), border_radius=rad)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))
    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(seam, (*CARD_RING_BRIGHT, 80),
                     (rect.left, plinth_top - max(1, m(1))),
                     (rect.right - 1, plinth_top - max(1, m(1))), max(1, m(1)))
    big.blit(seam, (0, 0))
    pygame.draw.line(big, (6, 5, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))


def _simple_price(big, cx, cy, price, pal):
    f   = font(9.0)
    txt = f"{price}"
    nw  = _glyph_base(txt, f, 0).get_width()
    ar  = nw // 2 + m(6)
    rimbox = pygame.Rect(cx - ar, cy - ar, ar * 2, ar * 2)
    arc = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(arc, (*CARD_RING_BRIGHT, 140), rimbox,
                    math.radians(60), math.radians(210), max(1, m(1)))
    big.blit(arc, (0, 0))
    plain_text(big, txt, f, (cx, cy), lerp_color(pal["gem"], WHITE, 0.25),
               shadow_a=0, weight=m(0.9))


def render_card(sid):
    pal   = RARITY.get(_rarity(sid), MYSTERY)
    name  = store_catalog.name(sid)
    price = store_catalog.cost(sid)
    big   = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect  = pygame.Rect(m(_INSET), m(_INSET), CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad   = m(CARD_RAD)
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235), w=max(1, m(2.0)))
    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)
    _neutral_band(big, rect, plinth_top, rad)
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3), pal["gem"], pal["deep"])
    _simple_price(big, rect.right - m(23), rect.y + m(48), price, pal)
    _name_filament_spark(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
    return big


VARIANTS = [("RARE", "skin_tophat"), ("EPIC", "skin_prism"), ("LEGENDARY", "skin_kitsune")]
PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN, GUTTER, HEADER_H, FOOTER_H = 10, 8, 26, 22


def render_sheet():
    sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
    sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((8, 8, 20))
    hfont = _font(20, True)
    ffont = _font(18, True)
    htxt = hfont.render("store_card_v4_r4_name_v6 — filament-spark — round 2", True, (236, 232, 214))
    sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
    panel_y = MARGIN + HEADER_H
    for i, (tier, sid) in enumerate(VARIANTS):
        px = MARGIN + i * (PANEL_W + GUTTER)
        sheet.blit(render_card(sid), (px, panel_y))
        ftxt = ffont.render(tier, True, (218, 214, 200))
        sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                          panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
    return sheet


if __name__ == "__main__":
    sheet = render_sheet()
    out = "/home/user/skybit/docs/store_card_v4_r4_name_v6/filament-spark/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())

"""Round-1 render sheet for the `denomination-badge` store-card price redesign.

Fuses the crest tier gem and the price into ONE heraldic emblem at the card's
top-right: the faceted tier gem is the CROWN (drawn untouched by draw_card),
and a dark shield PLINTH is struck beneath it carrying the price in coin-metal
relief. The plinth RIM — not the gem — carries affordability (warm gold when the
player can pay, cold steel when locked), so the tier hue is never overloaded to
mean two things at once. Equipped swaps the numerals for a mint check.

Implemented as a monkey-patch of store_cards.state_chip: draw_card already lays
the crest gem down first, so the patch just reconstructs the badge anchor from
the chip position, casts one shared shadow under gem+plinth, and struck the
plinth on top. The default bottom price chip is skipped entirely.

Review-only tooling — never imported by the game.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game import store_data
from game.draw import lerp_color, WHITE

from game.hud import _font as hud_font


# ── plinth palette ────────────────────────────────────────────────────────────
# DARK enamel body so bright coin-metal numerals read as POSITIVE relief.
PLINTH_TOP = (24, 20, 34)
PLINTH_BOT = (14, 12, 22)
PLINTH_KEYLINE = (6, 6, 14)

# Rim = the affordability channel. Gem hue stays free to mean tier alone.
STEEL_TOP = (150, 156, 172)
STEEL_DARK = (60, 64, 80)
EQUIP_RIM_TOP = (120, 225, 150)
EQUIP_RIM_DARK = (40, 100, 56)

LOCK_NUM = (150, 132, 92)        # desaturated bronze — tarnished, unaffordable
EQUIP_INK = (80, 220, 130)

# The render harness forces affordability so both states appear on one sheet;
# the live patch would leave this None and read the real wallet.
_FORCE_AFFORD = None


def _badge_shadow(surf, gem_cx, gem_cy, gem_r, poly):
    """One soft shadow shared by the whole emblem (gem crown + plinth), offset
    down-right off the card's top-left key light. Drawn as a feathered black
    silhouette of the combined gem disc + plinth so the badge reads as a single
    seated object rather than two stacked stickers."""
    xs = [p[0] for p in poly] + [gem_cx - gem_r, gem_cx + gem_r]
    ys = [p[1] for p in poly] + [gem_cy - gem_r, gem_cy + gem_r]
    blur = sc.m(3)
    pad = blur + sc.m(2)
    minx, miny = int(min(xs)) - pad, int(min(ys)) - pad
    bw = int(max(xs)) - int(min(xs)) + pad * 2
    bh = int(max(ys)) - int(min(ys)) + pad * 2

    sil = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.circle(sil, (0, 0, 0, 255), (gem_cx - minx, gem_cy - miny), gem_r)
    pygame.draw.polygon(sil, (0, 0, 0, 255), [(x - minx, y - miny) for x, y in poly])

    # cheap gaussian-ish feather: stack the silhouette across a small disc of
    # offsets so the interior saturates solid and the rim falls off soft.
    soft = pygame.Surface((bw, bh), pygame.SRCALPHA)
    step = max(1, sc.m(1))
    offs = [(dx, dy)
            for dx in range(-blur, blur + 1, step)
            for dy in range(-blur, blur + 1, step)
            if dx * dx + dy * dy <= blur * blur]
    a = max(6, int(150 / max(1, len(offs) ** 0.5)))
    for dx, dy in offs:
        tmp = sil.copy()
        tmp.set_alpha(a)
        soft.blit(tmp, (dx, dy))
    # Punch the badge footprint back out so only the CAST fringe survives — the
    # gem crown (already drawn) must stay visible, not be buried under its own
    # shadow. The -m(2) shift cancels the +m(2) cast offset below.
    soft.blit(sil, (-sc.m(2), -sc.m(2)), special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(soft, (minx + sc.m(2), miny + sc.m(2)))


def _plinth(surf, poly, miny, maxy, state):
    """Struck the dark shield body + its beveled metal rim. The body gradient is
    identical in every state; only the rim colour changes so the gem's tier hue
    stays the single carrier of rarity."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    minx, maxx = int(min(xs)), int(max(xs))
    lo, hi = int(min(ys)), int(max(ys))
    bw, bh = maxx - minx + 1, hi - lo + 1
    lpoly = [(x - minx, y - lo) for x, y in poly]

    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), lpoly)

    body = sc.vgrad_stops(bw, bh, 0, [(0.0, PLINTH_TOP), (1.0, PLINTH_BOT)],
                          255, gamma=1.05)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # faint top inner sheen gives the flat enamel a little crown curvature.
    sheen = pygame.Surface((bw, bh), pygame.SRCALPHA)
    sh_h = max(1, int(bh * 0.55))
    for y in range(sh_h):
        alpha = int(30 * (1 - y / sh_h) ** 1.6)
        pygame.draw.line(sheen, (255, 255, 255, alpha), (0, y), (bw, y))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(sheen, (0, 0))
    surf.blit(body, (minx, lo))

    if state == "afford":
        rt, rd = sc.GOLD_A_RIM_BRIGHT, sc.GOLD_A_RIM_DARK
    elif state == "equipped":
        rt, rd = EQUIP_RIM_TOP, EQUIP_RIM_DARK
    else:
        rt, rd = STEEL_TOP, STEEL_DARK

    span = max(1, maxy - miny)
    # dark contact keyline defines the silhouette; the colour bevel seats inside.
    pygame.draw.polygon(surf, PLINTH_KEYLINE, poly, max(1, sc.m(2)))
    w = max(1, sc.m(1.4))
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        t = ((a[1] + b[1]) / 2 - miny) / span
        col = lerp_color(rt, rd, max(0.0, min(1.0, t)))
        pygame.draw.line(surf, col, a, b, w)
    # hot top edge (poly[0]->poly[1]) = the struck crown of the bevel.
    pygame.draw.line(surf, lerp_color(rt, WHITE, 0.35), poly[0], poly[1],
                     max(1, sc.m(0.8)))


def _numerals(surf, cx, cy, text, afford):
    """Price in coin-metal relief centred on the plinth — no coin glyph, the
    crowning gem IS the denomination mark. A down-offset dark cast lifts the
    numerals so they read struck-proud, not debossed."""
    f = sc.font(11)
    mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(0.9))
    rr = mask.get_rect(center=(cx, cy))

    cast = mask.copy()
    cast.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    cast.set_alpha(160)
    surf.blit(cast, (rr.x, rr.y + sc.m(1)))

    img = mask.copy()
    if afford:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((*LOCK_NUM, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, rr)


def _check(surf, cx, cy):
    """Mint check struck into the plinth for the equipped state."""
    w = sc.m(7)
    pygame.draw.lines(surf, EQUIP_INK, False,
                      [(cx - w * 0.6, cy + sc.m(0.4)),
                       (cx - w * 0.12, cy + sc.m(3.2)),
                       (cx + w * 0.72, cy - sc.m(4.6))],
                      max(1, sc.m(2.4)))


def my_state_chip(surf, sid, cx, cy, equipped, secret, h, variant=sc.PRICE_VARIANT):
    """Denomination-badge replacement for the default bottom price chip. Draws
    the plinth beneath the already-drawn crest gem and skips the bottom chip.
    The badge anchor is reconstructed from the chip position so it needs no card
    rect: the crest gem sits at (centerx + m(56), y + m(19)) relative to the same
    layout that places this chip at (centerx, y + m(88) - _CHIP_DY)."""
    gem_cx = cx + sc.m(56)
    gem_cy = cy - sc.m(66)
    gem_r = sc.m(sc.GEM_R + 3)

    # shield poly relative to the gem crown, with softened (chamfered) top corners
    w2, top, mid, bot = sc.m(18), sc.m(5), sc.m(20), sc.m(28)
    c = sc.m(2)
    rel = [(-w2 + c, top), (w2 - c, top), (w2, top + c),
           (w2, mid), (0, bot), (-w2, mid), (-w2, top + c)]
    poly = [(gem_cx + dx, gem_cy + dy) for dx, dy in rel]
    miny = gem_cy + top
    maxy = gem_cy + bot

    price = sc._cost(sid)
    if equipped:
        state = "equipped"
    else:
        afford = _FORCE_AFFORD
        if afford is None:
            afford = store_data.balance() >= price
        state = "afford" if afford else "locked"

    _badge_shadow(surf, gem_cx, gem_cy, gem_r, poly)
    _plinth(surf, poly, miny, maxy, state)

    num_cx, num_cy = gem_cx, gem_cy + sc.m(16)
    if state == "equipped":
        _check(surf, num_cx, num_cy)
    else:
        _numerals(surf, num_cx, num_cy, f"{price:,}", state == "afford")
    return pygame.Rect(int(gem_cx - w2), int(miny), int(w2 * 2), int(maxy - miny))


sc.state_chip = my_state_chip   # patch BEFORE any draw_card call


# =============================================================================
# Render sheet
# =============================================================================
def render_card_surf(sid, equipped=False, afford=True):
    """A full 2x-buffer card (324x216) so the sheet can both downscale it to the
    live 162x100 tile AND crop the badge at zoom from the same crisp source."""
    global _FORCE_AFFORD
    _FORCE_AFFORD = afford
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((sc.CARD_W * sc.SS, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                       ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, equipped=equipped, secret=False)
    _FORCE_AFFORD = None
    return surf


def badge_zoom(card_surf, scale=4):
    """4x crop of the top-right badge area: 80x80 logical = 160x160 device px
    from the 2x buffer, upscaled 4x to 640x640 with nearest-neighbour so every
    facet/rim edge is legible for review."""
    cx, cy = 274, 62
    crop = pygame.Surface((160, 160), pygame.SRCALPHA)
    src = pygame.Rect(cx - 80, cy - 80, 160, 160)
    inter = src.clip(card_surf.get_rect())
    if inter.width > 0 and inter.height > 0:
        sub = card_surf.subsurface(inter).copy()
        crop.blit(sub, (inter.x - src.x, inter.y - src.y))
    return pygame.transform.scale(crop, (160 * scale, 160 * scale))


def main():
    out_dir = "/home/user/skybit/docs/store_price_redesign/denomination-badge"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    MUMMY, KITSUNE = "skin_mummy", "skin_kitsune"

    # ── build source card surfaces ──
    specs = [
        (MUMMY,   False, True,  "MUMMY · EPIC · affordable"),
        (MUMMY,   False, False, "MUMMY · EPIC · locked"),
        (KITSUNE, False, True,  "KITSUNE · LEGENDARY · affordable"),
        (KITSUNE, False, False, "KITSUNE · LEGENDARY · locked"),
        (MUMMY,   True,  True,  "MUMMY · EPIC · EQUIPPED"),
    ]
    sources = [(render_card_surf(sid, eq, af), lbl) for sid, eq, af, lbl in specs]

    # ── verify the design claim: gem hue is IDENTICAL afford vs locked; only the
    # plinth rim differs. Probe on the gem table + on the plinth top rim. ──
    afford_k = render_card_surf(KITSUNE, False, True)
    locked_k = render_card_surf(KITSUNE, False, False)
    gem_a = tuple(afford_k.get_at((274, 50)))
    gem_l = tuple(locked_k.get_at((274, 50)))
    rim_a = tuple(afford_k.get_at((274, 61)))
    rim_l = tuple(locked_k.get_at((274, 61)))
    assert gem_a == gem_l, f"gem hue changed with affordability: {gem_a} vs {gem_l}"
    assert max(gem_a[:3]) > 120, f"gem crown buried (too dark): {gem_a}"
    assert rim_a != rim_l, f"plinth rim did not react to affordability: {rim_a}"
    print("gem hue afford/locked (must match):", gem_a, gem_l)
    print("plinth rim afford/locked (must differ):", rim_a, rim_l)

    # ── layout ──
    pad = 30
    gap = 18
    header_h = 46
    card_w, card_h = 162, 108
    label_h = 22

    small = [(pygame.transform.smoothscale(s, (card_w, card_h)), lbl)
             for s, lbl in sources]
    row1_y = header_h + pad
    row1_w = card_w * len(small) + gap * (len(small) - 1)

    # ── zoom row: legendary afford vs locked (the design's core claim) ──
    zooms = [
        (badge_zoom(afford_k), "LEGENDARY badge · affordable  (gold rim)"),
        (badge_zoom(locked_k), "LEGENDARY badge · locked  (gem hue intact, rim → steel)"),
    ]
    zsz = zooms[0][0].get_width()
    row2_y = row1_y + card_h + label_h + gap * 2
    row2_w = zsz * len(zooms) + gap * (len(zooms) - 1)

    content_w = max(row1_w, row2_w)
    canvas_w = pad * 2 + content_w
    canvas_h = row2_y + zsz + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(30, True)
    lf = hud_font(15)

    canvas.blit(hf.render("store price redesign — denomination-badge · round 1",
                          True, (236, 232, 250)), (pad, pad // 2 + 4))

    def put_label(text, cx, y):
        img = lf.render(text, True, (208, 204, 226))
        canvas.blit(img, (cx - img.get_width() // 2, y))

    x = pad + (content_w - row1_w) // 2
    for card, lbl in small:
        canvas.blit(card, (x, row1_y))
        put_label(lbl, x + card_w // 2, row1_y + card_h + 4)
        x += card_w + gap

    x = pad + (content_w - row2_w) // 2
    for zoom, lbl in zooms:
        canvas.blit(zoom, (x, row2_y))
        put_label(lbl, x + zsz // 2, row2_y + zsz + 4)
        x += zsz + gap

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()

"""Round-2 render sheet for the `denomination-badge` store-card price redesign.

Fuses the crest tier gem and the price into ONE heraldic emblem at the card's
top-right: the faceted tier gem is the CROWN (drawn untouched by draw_card),
and a dark shield PLINTH is struck beneath it carrying the price in coin-metal
relief. The plinth RIM — not the gem — carries affordability (warm gold when the
player can pay, cold steel when locked), so the tier hue is never overloaded to
mean two things at once. Equipped swaps the numerals for a mint check.

Round-2 answers the round-1 critique:
  1. WIDER BARREL — the plinth grows to an 80px outer shield (was 72) with the
     straight side-walls carried down to gem_cy+23 before the foot tapers, so
     the inner enamel clears the widest catalog price ("10,500"/"12,000") with
     >=4px each side. 80px is the widest a barrel can be here: the crest gem is
     fixed at x=274 and the card body ends at x=312, so a centred plinth caps at
     72px; nudging the plinth 2px (1x) left of the crown buys the extra width
     while the crown still reads centred. Numerals drop to font(10) to seal it.
  2. SECRET FALLBACK — when the crown is hidden, a faint outline silhouette of
     the gem cut is struck where the crown would sit so the badge shape stays
     legible, and the price still prints in the plinth body.
  3. BRIGHTER LOCK NUMERAL — tarnished bronze lifts ~15% to clear the dark
     enamel with more contrast while holding the warm-bronze hue.
  4. FOOT ANCHOR — a faint reflected-light lip along the card's bottom inner
     edge answers the top-right weight of the badge so the card reads balanced.

Implemented as a monkey-patch of store_cards.state_chip (it receives sid +
secret, which price_chip does not). The badge anchor is reconstructed from the
chip position; draw_card already lays the crest gem down first, so the patch
just casts one shared shadow, strikes the plinth, prints the price, and paints
the foot lip. The default bottom price chip is skipped entirely.

Review-only tooling — never imported by the game.
"""
import math
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

# Round-2: lifted ~15% off round-1's (150,132,92) so tarnished bronze clears the
# dark enamel with more contrast while holding the warm, unaffordable hue.
LOCK_NUM = (175, 155, 108)
EQUIP_INK = (80, 220, 130)

# Neutral, near-invisible silhouette for the secret fallback — no tier hue, so a
# hidden crown gives away nothing about rarity, just shape.
SILHOUETTE = (180, 170, 160, 40)

# Numerals use font(10): the widest catalog price ("10,500"/"12,000") is 67px
# bolded here, and the round-2 80px barrel clears that with ~4.5px each side.
NUM_FONT = 10

# The render harness forces affordability so both states appear on one sheet;
# the live patch would leave this None and read the real wallet.
_FORCE_AFFORD = None
# Set while rendering a secret card so the crest crown is suppressed and the
# badge falls back to its silhouette + price — the case round-2 must define.
_SUPPRESS_GEM = False
# Verification-only toggle to diff the (deliberately faint) secret silhouette.
_SILHOUETTE_ON = True


# ── badge geometry (device px in the 2x author buffer) ────────────────────────
# The crest gem is drawn by draw_card at (rect.right - m(19), rect.y + m(19)),
# which — for the fixed card layout that also seats this chip — is (274, 50) with
# radius m(GEM_R+3). Reconstruct that anchor from the chip position so the badge
# needs no card rect handed in.
def _anchor(cx, cy):
    gem_cx = cx + sc.m(56)
    gem_cy = cy - sc.m(63)           # precise: cy = gem_cy + m(63) in this layout
    gem_r = sc.m(sc.GEM_R + 3)
    # Nudge the plinth 2px (1x) left of the crown: a centred plinth would cap at
    # 72px (gem x=274, body edge x=312), but shifting the barrel left lets it
    # reach 80px while the crown still reads seated at its centre.
    pcx = gem_cx - sc.m(2)
    return gem_cx, gem_cy, gem_r, pcx


def _plinth_poly(pcx, gem_cy):
    """The shield outline, struck around the plinth centre. Straight side-walls
    are carried down to gem_cy+23 (the numeral band) before the foot tapers, so
    the price sits in the full-width barrel, not the taper."""
    w2 = sc.m(20)                    # 80px outer — the widest that clears the body
    top = sc.m(4)
    mid = sc.m(23)                   # straight walls reach here before tapering
    bot = sc.m(28)                   # broad foot point
    c = sc.m(2)                      # chamfered top corners
    rel = [(-w2 + c, top), (w2 - c, top), (w2, top + c),
           (w2, mid), (0, bot), (-w2, mid), (-w2, top + c)]
    poly = [(pcx + dx, gem_cy + dy) for dx, dy in rel]
    return poly, gem_cy + top, gem_cy + bot


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


def _silhouette_gem(surf, cx, cy, r):
    """The secret fallback crown: an outline-only trace of the 8-facet gem cut in
    a neutral, near-invisible ink, struck where the crest crown would sit. Keeps
    the badge's crown+plinth shape legible even when the real gem is masked, and
    gives nothing away about the hidden item's tier."""
    if not _SILHOUETTE_ON:
        return
    n = 8
    rot = -math.pi / 2 - math.pi / n
    girdle = [(cx + r * math.cos(rot + 2 * math.pi * i / n),
               cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    tr = r * 0.46
    table = [(cx + tr * math.cos(rot + 2 * math.pi * i / n),
              cy + tr * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(layer, SILHOUETTE, girdle, max(1, sc.m(1)))
    pygame.draw.polygon(layer, SILHOUETTE, table, max(1, sc.m(0.8)))
    for i in range(n):
        pygame.draw.line(layer, SILHOUETTE, girdle[i], table[i], max(1, sc.m(0.6)))
    surf.blit(layer, (0, 0))


def _plinth(surf, poly, miny, maxy, state):
    """Strike the dark shield body + its beveled metal rim. The body gradient is
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
    f = sc.font(NUM_FONT)
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


def _foot_anchor(surf, cx, cy):
    """A faint reflected-light lip along the card's bottom inner edge — the
    counterweight to the top-right badge so the whole card reads balanced rather
    than top-heavy. The card rect is reconstructed from the chip anchor: the same
    fixed layout that seats this chip puts the body at rect.y = cy - m(82)."""
    body_w = sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET)
    body_h = sc.CARD_H * sc.SS - 2 * sc.m(sc._INSET)
    rx = cx - body_w // 2
    ry = cy - sc.m(82)
    yb = ry + body_h - sc.m(6)
    x0 = rx + sc.m(22)
    w = body_w - 2 * sc.m(22)
    h = sc.m(3)
    lip = pygame.Surface((w, h + sc.m(1)), pygame.SRCALPHA)
    for x in range(w):
        t = x / max(1, w - 1)
        fade = (1 - abs(t * 2 - 1)) ** 1.2           # bright at centre, fades out
        for y in range(h):
            a = int(72 * fade * (1 - y / h))
            if a > 0:
                lip.set_at((x, y), (250, 224, 156, a))
        # a thin dark seat just under the highlight so it reads as a lit lip
        lip.set_at((x, h), (6, 6, 14, int(70 * fade)))
    surf.blit(lip, (x0, yb))


def my_state_chip(surf, sid, cx, cy, equipped, secret, h, variant=sc.PRICE_VARIANT):
    """Denomination-badge replacement for the default bottom price chip. Draws
    the plinth beneath the already-drawn crest gem, the price in coin-metal, a
    secret-fallback silhouette when the crown is masked, and the card foot
    anchor. The default bottom price chip is skipped entirely."""
    gem_cx, gem_cy, gem_r, pcx = _anchor(cx, cy)
    poly, miny, maxy = _plinth_poly(pcx, gem_cy)

    price = sc._cost(sid)
    if equipped:
        state = "equipped"
    else:
        afford = _FORCE_AFFORD
        if afford is None:
            afford = store_data.balance() >= price
        state = "afford" if afford else "locked"

    _foot_anchor(surf, cx, cy)
    _badge_shadow(surf, gem_cx, gem_cy, gem_r, poly)
    _plinth(surf, poly, miny, maxy, state)
    # Secret fallback: with the crown masked, trace the gem cut so the badge's
    # crown+plinth shape still reads. Struck under the numerals, over the plinth.
    if secret:
        _silhouette_gem(surf, gem_cx, gem_cy, gem_r)

    num_cx, num_cy = pcx, gem_cy + sc.m(17)
    if state == "equipped":
        _check(surf, num_cx, num_cy)
    else:
        _numerals(surf, num_cx, num_cy, f"{price:,}", state == "afford")
    w2 = sc.m(20)
    return pygame.Rect(int(pcx - w2), int(miny), int(w2 * 2), int(maxy - miny))


sc.state_chip = my_state_chip   # patch BEFORE any draw_card call

# Suppress the crest crown only while rendering a secret card, so the badge falls
# back to its silhouette (the case round-2 must define). draw_card calls the bare
# module name `facet_gem`, so reassigning it here reroutes that call.
_orig_facet_gem = sc.facet_gem


def _facet_gem_maybe(*args, **kwargs):
    if _SUPPRESS_GEM:
        return
    return _orig_facet_gem(*args, **kwargs)


sc.facet_gem = _facet_gem_maybe


# =============================================================================
# Render sheet
# =============================================================================
def render_card_surf(sid, equipped=False, afford=True, secret=False):
    """A full 2x-buffer card (324x216) so the sheet can both downscale it to the
    live 162x100 tile AND crop the badge at zoom from the same crisp source."""
    global _FORCE_AFFORD, _SUPPRESS_GEM
    _FORCE_AFFORD = afford
    _SUPPRESS_GEM = secret
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((sc.CARD_W * sc.SS, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                       ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, equipped=equipped, secret=secret)
    _FORCE_AFFORD = None
    _SUPPRESS_GEM = False
    return surf


def badge_zoom(card_surf, scale=4):
    """4x crop of the top-right badge area (2x-buffer x=244..322, y=12..94, i.e.
    78x82 logical device px) upscaled with nearest-neighbour so every facet, rim
    edge and numeral is legible for review."""
    src = pygame.Rect(244, 12, 78, 82)
    crop = pygame.Surface((src.w, src.h), pygame.SRCALPHA)
    inter = src.clip(card_surf.get_rect())
    if inter.width > 0 and inter.height > 0:
        sub = card_surf.subsurface(inter).copy()
        crop.blit(sub, (inter.x - src.x, inter.y - src.y))
    return pygame.transform.scale(crop, (src.w * scale, src.h * scale))


# =============================================================================
# Pixel verification (printed to the console; also drives assertions)
# =============================================================================
def verify():
    KITSUNE = "skin_kitsune"
    PARROT_PINATA = "skin_pinata_parrot"       # 10,500 — the widest catalog price
    pcx = 274 - sc.m(2)                        # plinth centre (gem_cx - m(2))
    w2 = sc.m(20)

    # (3) gem hue must be IDENTICAL afford vs locked — only the plinth rim reacts.
    afford_k = render_card_surf(KITSUNE, False, True)
    locked_k = render_card_surf(KITSUNE, False, False)
    gem_a = tuple(afford_k.get_at((274, 50)))
    gem_l = tuple(locked_k.get_at((274, 50)))
    assert gem_a == gem_l, f"gem hue changed with affordability: {gem_a} vs {gem_l}"
    assert max(gem_a[:3]) > 120, f"gem crown buried (too dark): {gem_a}"
    print("gem hue afford/locked (must match):", gem_a, gem_l)

    # (2) rim reacts to affordability (gold vs steel). Probe the LEFT plinth wall
    # BELOW the gem (y=92 > gem bottom 72) so the sample is rim, not crown: scan
    # inward from the body until the first bright rim pixel on each card.
    def first_rim(card, y):
        for x in range(int(pcx - w2 - 4), int(pcx)):
            r, g, b, aa = card.get_at((x, y))
            if aa > 120 and max(r, g, b) > 120:
                return (r, g, b)
        return None
    rim_a = first_rim(afford_k, 92)
    rim_l = first_rim(locked_k, 92)
    assert rim_a is not None and rim_l is not None, "rim not found below gem"
    # gold rim is markedly warmer (r-b) than the cool steel rim.
    warm_a = rim_a[0] - rim_a[2]
    warm_l = rim_l[0] - rim_l[2]
    assert warm_a > warm_l + 20, f"rim did not shift warm→cool: {rim_a} vs {rim_l}"
    print("plinth wall rim afford/locked (gold vs steel):", rim_a, rim_l)

    # (1) widest price clears the inner enamel with >=4px each side. Inner enamel
    # runs pcx ± (w2 - m(2)); measure the true bronze glyph ink extent (AA
    # included) across the numeral band and check the clearance to those edges.
    wide = render_card_surf(PARROT_PINATA, False, False, secret=True)
    num_y = 50 + sc.m(17)                      # gem_cy + m(17)
    inner_l = pcx - (w2 - sc.m(2))
    inner_r = pcx + (w2 - sc.m(2))
    glyph_l = glyph_r = None
    for x in range(int(inner_l - 6), int(inner_r + 6)):
        for y in range(int(num_y - 13), int(num_y + 13)):
            r, g, b, aa = wide.get_at((x, y))
            if aa > 25 and r > b + 8 and r > 90 and g >= b:    # warm bronze ink
                glyph_l = x if glyph_l is None else min(glyph_l, x)
                glyph_r = x if glyph_r is None else max(glyph_r, x)
    left_gap = glyph_l - inner_l
    right_gap = inner_r - glyph_r
    print(f"inner enamel zone x: {inner_l:.0f}..{inner_r:.0f} "
          f"(width {inner_r - inner_l:.0f})")
    print(f"widest '10,500' glyph ink span x: {glyph_l}..{glyph_r} "
          f"(width {glyph_r - glyph_l})")
    print(f"numeral clearance to inner enamel  left: {left_gap:.0f}px  "
          f"right: {right_gap:.0f}px")
    assert left_gap >= 4, f"widest price too close to left edge: {left_gap}px"
    assert right_gap >= 4, f"widest price too close to right edge: {right_gap}px"

    # (2b) locked numerals lifted brighter than round-1's 150 — probe for r>165.
    best_r = 0
    for x in range(int(inner_l), int(inner_r)):
        for y in range(int(num_y - 12), int(num_y + 12)):
            r, g, b, aa = wide.get_at((x, y))
            if aa > 60 and r > b + 15 and g > b:
                best_r = max(best_r, r)
    print("brightest locked bronze r-channel (want >165):", best_r)
    assert best_r > 165, f"locked bronze not lifted: r={best_r}"

    # (4) secret fallback: crest crown suppressed (not the red MYSTERY gem) and a
    # faint silhouette present where the crown would sit. The silhouette is
    # deliberately near-invisible (alpha ~40), so prove it by diffing the crown
    # box against an identical render with the silhouette turned off.
    global _SILHOUETTE_ON
    secret_card = render_card_surf("skin_binky", False, False, secret=True)
    crown_px = tuple(secret_card.get_at((274, 46)))
    assert not (crown_px[0] > 180 and crown_px[1] < 130 and crown_px[2] < 130), \
        f"secret crown still shows the red MYSTERY gem: {crown_px}"
    _SILHOUETTE_ON = False
    bare = render_card_surf("skin_binky", False, False, secret=True)
    _SILHOUETTE_ON = True
    changed = 0
    for x in range(252, 298):
        for y in range(26, 74):
            if secret_card.get_at((x, y)) != bare.get_at((x, y)):
                changed += 1
    assert changed > 60, f"secret silhouette barely renders: {changed} px changed"
    print("secret crown pixel (no red gem):", crown_px,
          " silhouette px lifted:", changed)

    # (4b) foot anchor: a warm lit lip appears along the card's bottom inner edge.
    foot = afford_k
    foot_hit = False
    for x in range(120, 200):
        for y in range(178, 190):
            r, g, b, aa = foot.get_at((x, y))
            if aa > 40 and r > 160 and g > 120 and r > b + 20:
                foot_hit = True
                break
        if foot_hit:
            break
    assert foot_hit, "foot anchor highlight not found"
    print("foot anchor highlight present:", foot_hit)

    print("ALL VERIFICATION CHECKS PASSED")


def main():
    verify()

    out_dir = "/home/user/skybit/docs/store_price_redesign/denomination-badge"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

    MUMMY, KITSUNE, BINKY = "skin_mummy", "skin_kitsune", "skin_binky"

    # ── row 1: five full cards across the state matrix ──
    specs = [
        (MUMMY,   False, True,  False, "MUMMY · EPIC · affordable"),
        (MUMMY,   False, False, False, "MUMMY · EPIC · locked"),
        (MUMMY,   True,  True,  False, "MUMMY · EPIC · EQUIPPED"),
        (KITSUNE, False, True,  False, "KITSUNE · LEGENDARY · affordable"),
        (KITSUNE, False, False, False, "KITSUNE · LEGENDARY · locked"),
    ]
    row1_sources = [(render_card_surf(sid, eq, af, sec), lbl)
                    for sid, eq, af, sec, lbl in specs]

    # ── row 2: the secret card + two 4x badge zooms ──
    secret_card = render_card_surf(BINKY, False, False, secret=True)
    afford_k = render_card_surf(KITSUNE, False, True)
    locked_k = render_card_surf(KITSUNE, False, False)

    # ── layout ──
    pad = 20
    gap = 12
    header_h = 44
    card_w, card_h = 162, 108
    label_h = 20

    small1 = [(pygame.transform.smoothscale(s, (card_w, card_h)), lbl)
              for s, lbl in row1_sources]
    row1_y = header_h + pad
    row1_w = card_w * len(small1) + gap * (len(small1) - 1)

    secret_small = pygame.transform.smoothscale(secret_card, (card_w, card_h))
    zooms = [
        (badge_zoom(afford_k), "LEGENDARY badge · affordable  (gold rim)"),
        (badge_zoom(locked_k), "LEGENDARY badge · locked  (gem hue intact, rim→steel)"),
    ]
    zsz_w, zsz_h = zooms[0][0].get_size()
    row2_h = max(card_h, zsz_h)
    row2_y = row1_y + card_h + label_h + gap * 2
    row2_w = card_w + gap + zsz_w * len(zooms) + gap * (len(zooms) - 1)

    content_w = max(row1_w, row2_w)
    canvas_w = pad * 2 + content_w
    canvas_h = row2_y + row2_h + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(28, True)
    lf = hud_font(14)

    canvas.blit(hf.render("store price redesign — denomination-badge · round 2",
                          True, (236, 232, 250)), (pad, pad // 2 + 2))

    def put_label(text, cx, y):
        img = lf.render(text, True, (208, 204, 226))
        canvas.blit(img, (cx - img.get_width() // 2, y))

    x = pad + (content_w - row1_w) // 2
    for card, lbl in small1:
        canvas.blit(card, (x, row1_y))
        put_label(lbl, x + card_w // 2, row1_y + card_h + 3)
        x += card_w + gap

    x = pad + (content_w - row2_w) // 2
    canvas.blit(secret_small, (x, row2_y + (row2_h - card_h) // 2))
    put_label("BINKY · SECRET  (gem silhouette, price shown)",
              x + card_w // 2, row2_y + (row2_h - card_h) // 2 + card_h + 3)
    x += card_w + gap
    for zoom, lbl in zooms:
        canvas.blit(zoom, (x, row2_y + (row2_h - zsz_h) // 2))
        put_label(lbl, x + zsz_w // 2, row2_y + (row2_h - zsz_h) // 2 + zsz_h + 3)
        x += zsz_w + gap

    pygame.image.save(canvas, out)
    print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")


if __name__ == "__main__":
    main()

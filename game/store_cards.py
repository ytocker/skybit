"""
CONSTELLATION per-item store cards — the jewel-grade card art for the coin
store's category grid.

This is a self-contained runtime port of the art-director-locked CONSTELLATION
card: an indigo body with a crisp dark keyline + gold bevel rim, a neutral gold
inner tray, a glass cabochon thumb disc carrying a tier aura + the real item
thumbnail, a faceted tier gem badge top-right, a notched tier-coloured rarity
ribbon, a cream item name, and a state chip (gold price / green EQUIPPED).
Equipped cards add a restrained gold halo + a 2-step gold frame.

Each card is authored resolution-independently from a supersample factor (SS):
every curve, bevel, gem facet and glyph is drawn oversized onto an SS canvas,
then ONE smoothscale down to the live 162x100 card turns that oversized
geometry into crisp anti-aliased edges — no per-shape AA tricks. Because a card
is STATIC for a given (sid, equipped, masked) state, it is built once and cached
module-level; the store can then blit it every frame for the cost of one blit.

Both build targets safe: pure pygame, no numpy, no mixer, no platform branches,
no filesystem writes.
"""
from __future__ import annotations

import math
import pygame

from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game import parrot
from game import store_catalog
from game import store_data
from game.surprise_box_variants import _draw_qmark


# ── supersample ───────────────────────────────────────────────────────────────
# SS=2 (vs the print sheet's 4): a 2x author canvas still downscales clean in
# game and builds ~4x cheaper, which matters because cards build lazily as pages
# are viewed — including on the slower WASM Python runtime.
SS = 2

# Live per-1x card size — matches the store grid's _CARD_W/_CARD_H so the grid
# metrics in game/store.py are unchanged.
CARD_W = 162
CARD_H = 100

# The card body is inset from the surface edges so the multi-layer drop shadow
# and the equipped gold halo (both of which bleed OUTSIDE the body rect in the
# source) stay inside the returned 162x100 surface instead of being clipped.
_INSET = 4


def m(v):
    """Logical px -> device px. Keeps geometry authored at the 1x card scale."""
    return int(round(v * SS))


def mf(v):
    return v * SS             # float variant for sub-pixel math


def font(size):
    """Project bold font at supersample size so glyph edges resolve crisp."""
    return _font(max(1, int(round(size * SS))), True)


def _stamp_bold(base, weight):
    """Faux-bold: composite the glyph onto itself at a RING of offsets one
    `weight` out (8 compass points) so strokes grow ~`weight` px evenly on all
    sides without filling counters solid. The project ships only the Bold ttf,
    so authored 'thicker' is this multi-stamp at SS where the fractional growth
    survives the downscale."""
    weight = max(0, min(m(0.5), int(round(weight * 0.42))))
    if weight <= 0:
        return base
    w, h = base.get_size()
    pad = weight + m(1)
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    ring = [(-weight, 0), (weight, 0), (0, -weight), (0, weight)]
    d = max(1, int(round(weight * 0.71)))
    ring += [(-d, -d), (d, -d), (-d, d), (d, d)]
    for dx, dy in ring:
        out.blit(base, (pad + dx, pad + dy))
    out.blit(base, (pad, pad))                     # center on top, crisp core
    return out


# ── catalog adapters ──────────────────────────────────────────────────────────
def _cost(sid):
    return store_catalog.cost(sid) if store_catalog.exists(sid) else 0


def _rarity(sid):
    return store_catalog.rarity(sid)


def _name(sid):
    return store_catalog.name(sid) if store_catalog.exists(sid) else "DEFAULT"


def _is_secret(sid):
    try:
        return store_catalog.is_secret(sid)
    except Exception:
        return False


# ── palette (CONSTELLATION DNA) ───────────────────────────────────────────────
GOLD = _GOLD_BRIGHT
GOLD_PALE = _GOLD_PALE
GOLD_DEEP = _GOLD_DEEP

RARITY = {
    "common":    {"gem": (214, 206, 230), "glow": (180, 174, 214), "deep": (78, 74, 112)},
    "rare":      {"gem": (108, 188, 252), "glow": (74, 158, 248),  "deep": (24, 78, 142)},
    "epic":      {"gem": (194, 122, 248), "glow": (172, 94, 244),  "deep": (80, 34, 126)},
    "legendary": {"gem": (255, 202, 104), "glow": (255, 168, 58),  "deep": (150, 92, 22)},
}
MYSTERY = {"gem": (244, 96, 96), "glow": (236, 64, 64), "deep": (120, 22, 26)}

CARD_T = (28, 30, 70)
CARD_B = (12, 13, 38)
CABO_LO = (22, 24, 50)
CABO_HI = (6, 7, 20)
CARD_RING_DEEP = (58, 48, 22)
CARD_RING_BRIGHT = (236, 202, 116)
NAME_COL = (246, 240, 216)
CREAM = (246, 244, 232)

# ── Canonical GOLD RAMP A — the ONE gold for every gold FILL ──────────────────
GOLD_A_STOPS = [
    (0.00, (244, 192, 88)),
    (0.32, (228, 162, 56)),
    (0.66, (196, 124, 34)),
    (1.00, (150, 92, 18)),
]
GOLD_A_RIM_DARK = (86, 50, 8)
GOLD_A_RIM_BRIGHT = (255, 240, 190)
# Price chip gets its OWN deeper amber ramp so it never reads white on the dark
# card body (white is a poor price background).
PRICE_STOPS = [
    (0.00, (236, 176, 72)),
    (0.45, (204, 132, 42)),
    (1.00, (150, 90, 18)),
]
PRICE_RIM_DARK = (78, 44, 8)
PRICE_RIM_BRIGHT = (255, 226, 150)
GOLD_A_NUM = (52, 28, 4)
GOLD_A_COIN_RIM = (120, 74, 14)
GOLD_A_GAMMA = 1.06
GOLD_A_TOP = GOLD_A_STOPS[0][1]
GOLD_A_BOT = GOLD_A_STOPS[-1][1]


# =============================================================================
# Low-level primitives — all SS-aware. They take device-px coords.
# =============================================================================

def lerp_stops(stops, t):
    """Sample a piecewise-linear colour ramp at t in [0,1]. Lets the ONE gold
    ramp be authored as an N-stop ramp while staying a single continuous
    gradient — never a two-tone splice."""
    t = max(0.0, min(1.0, t))
    n = len(stops)
    seg = 0
    while seg < n - 2 and t > stops[seg + 1][0]:
        seg += 1
    t0, c0 = stops[seg]
    t1, c1 = stops[seg + 1]
    local = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
    return lerp_color(c0, c1, max(0.0, min(1.0, local)))


_vgrad_cache: dict = {}


def vgrad_stops(w, h, radius, stops, alpha=255, gamma=1.0):
    """Vertical rounded-rect filled by a continuous multi-stop ramp (one smooth
    gradient top->bottom). The single path every GOLD-FILL flows through so the
    card has exactly ONE gold."""
    key = (w, h, radius, tuple(stops), alpha, gamma)
    hit = _vgrad_cache.get(key)
    if hit is not None:
        return hit
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = (y / max(1, h - 1)) ** gamma
        c = lerp_stops(stops, t)
        pygame.draw.line(body, (*c, alpha), (0, y), (w - 1, y))
    if radius > 0:
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _vgrad_cache[key] = body
    return body


def vgrad(w, h, radius, top, bot, alpha=255, gamma=1.0):
    """Two-stop convenience over vgrad_stops (non-gold panels: card body)."""
    return vgrad_stops(w, h, radius, [(0.0, top), (1.0, bot)], alpha, gamma)


def gold_a_fill(w, h, radius, alpha=255):
    """The canonical Ramp-A gold rounded-rect fill — the ONE gold for every gold
    surface."""
    return vgrad_stops(w, h, radius, GOLD_A_STOPS, alpha, gamma=GOLD_A_GAMMA)


def multistop_v(w, h, stops, alpha=255):
    """Vertical multi-stop gradient (list of (t, color)); fills full surface."""
    surf = pygame.Surface((w, h))
    n = len(stops)
    for y in range(h):
        f = y / max(1, h - 1)
        seg = 0
        while seg < n - 2 and f > stops[seg + 1][0]:
            seg += 1
        t0, c0 = stops[seg]
        t1, c1 = stops[seg + 1]
        local = 0.0 if t1 == t0 else (f - t0) / (t1 - t0)
        pygame.draw.line(surf, lerp_color(c0, c1, max(0.0, min(1.0, local))),
                         (0, y), (w - 1, y))
    return surf


def soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=8):
    """Additive feathered glow — many layers so the falloff is smooth at SS."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.8)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def _alpha_aura(surf, cx, cy, radius, color, peak=27, layers=15):
    """Feathered halo via normal alpha-carry blits — survives compositing in
    transparent headroom above the card where BLEND_ADD would leave alpha=0."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        if r <= 0:
            continue
        a = int(peak * (1 - (i - 1) / layers) ** 1.6)
        if a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1))


_shadow_cache: dict = {}


def drop_shadow(surf, rect, radius, blur, alpha, dy):
    """Multi-layer blurred outer shadow, offset down (top-left light source)."""
    key = (rect.w, rect.h, radius, blur, alpha, dy)
    shadow = _shadow_cache.get(key)
    if shadow is None:
        sw = rect.w + blur * 2
        sh = rect.h + blur * 2 + abs(dy)
        shadow = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ox, oy = blur, blur
        for i in range(blur, 0, -1):
            a = int(alpha * (i / blur) ** 1.7 / blur * 2.4)
            if a <= 0:
                continue
            r = pygame.Rect(ox - i, oy - i + dy, rect.w + 2 * i, rect.h + 2 * i)
            s = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(), border_radius=radius + i)
            shadow.blit(s, r.topleft)
        _shadow_cache[key] = shadow
    surf.blit(shadow, (rect.x - blur, rect.y - blur))


def _glyph_base(txt, font_obj, tracking):
    """White glyph master at SS, with optional letter tracking."""
    if tracking:
        widths = [font_obj.size(ch)[0] for ch in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        hh = font_obj.get_height()
        base = pygame.Surface((max(1, total), hh), pygame.SRCALPHA)
        x = 0
        for ch, wch in zip(txt, widths):
            base.blit(font_obj.render(ch, True, WHITE), (x, 0))
            x += wch + tracking
        return base
    return font_obj.render(txt, True, WHITE)


def plain_text(surf, txt, font_obj, center, color, shadow_a=150, tracking=0,
               weight=None, keyline=None, kw=None):
    """Solid-colour type, faux-bolded for weight, with an optional crisp dark
    keyline so labels read heavy + sharp against the dark card ground."""
    base = _glyph_base(txt, font_obj, tracking)
    if weight is None:
        weight = m(0.8)
    base = _stamp_bold(base, weight)
    img = base.copy()
    img.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = img.get_rect(center=center)
    if shadow_a:
        sh = base.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow_a)
        surf.blit(sh, (r.x, r.y + m(1.5)))
    if keyline:
        p = kw if kw is not None else m(1)
        kl = base.copy()
        kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 45):
            dx = int(round(p * math.cos(math.radians(ang))))
            dy = int(round(p * math.sin(math.radians(ang))))
            surf.blit(kl, (r.x + dx, r.y + dy))
    surf.blit(img, r)
    return r


def coin_glyph(surf, cx, cy, r, rim=GOLD_A_COIN_RIM):
    """The EXACT in-game coin (entities._get_coin_face) smoothscaled to the
    requested radius — so the store coin is identical to the one the player
    collects in play."""
    from game.entities import _get_coin_face
    face = _get_coin_face()
    d = max(2, int(r * 2))
    img = pygame.transform.smoothscale(face, (d, d))
    surf.blit(img, img.get_rect(center=(cx, cy)))


def facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """The ONE locked gem cut for all 5 tiers: an 8-FACET BRILLIANT. An
    octagonal girdle with 8 crown facets radiating to an octagonal table,
    value-stepped by clock position off ONE top-left light. A dark seat well, a
    girdle keyline, and a SINGLE hot top-left specular pip. Tier colour is the
    gem's own hue; mystery owns red so it clearly claims NO tier."""
    body = base
    t_table = lerp_color(body, WHITE, 0.34)        # flat top, brightest
    t_hi = lerp_color(body, WHITE, 0.55)            # lit top-left crown
    t_sh = lerp_color(body, deep, 0.5)              # shaded crown
    t_dk = lerp_color(deep, NEAR_BLACK, 0.32)       # bottom-right, darkest
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)       # girdle keyline

    # dark seat well so it reads on any ground
    seat = pygame.Surface((r * 2 + m(10), r * 2 + m(10)), pygame.SRCALPHA)
    sc = r + m(5)
    pygame.draw.circle(seat, (0, 0, 0, 175), (sc, sc), r + m(4))
    pygame.draw.circle(seat, (*GOLD_DEEP, 115), (sc, sc), r + m(4), max(1, m(0.8)))
    surf.blit(seat, (cx - sc, cy - sc))

    n = 8
    rot = -math.pi / 2 - math.pi / n               # flat-ish top, point up-left
    girdle = [(cx + r * math.cos(rot + 2 * math.pi * i / n),
               cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    tr = r * 0.46
    table = [(cx + tr * math.cos(rot + 2 * math.pi * i / n),
              cy + tr * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    lx, ly = -0.7071, -0.7071                       # top-left light unit vector
    for i in range(n):
        a = girdle[i]
        b = girdle[(i + 1) % n]
        ta = table[i]
        tb = table[(i + 1) % n]
        mx = (a[0] + b[0]) / 2 - cx
        my = (a[1] + b[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        d = (mx / ml) * lx + (my / ml) * ly         # -1 (away) .. 1 (toward light)
        f = (d + 1) / 2                              # 0 dark .. 1 lit
        col = lerp_color(lerp_color(t_dk, t_sh, min(1.0, f * 2)),
                         t_hi, max(0.0, (f - 0.5) * 2))
        pygame.draw.polygon(surf, col, [a, b, tb, ta])
    pygame.draw.polygon(surf, t_table, table)
    pygame.draw.polygon(surf, t_key, girdle, width=max(1, m(0.6)))
    for i in range(n):
        pygame.draw.line(surf, (*t_key, 190), girdle[i], table[i], max(1, m(0.4)))
    # the single hot specular pip upper-left of the table
    pr = max(1, int(r * 0.24))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 250), (pr + m(1), pr + m(1)), pr)
    surf.blit(pip, (cx - pr - int(r * 0.26), cy - pr - int(r * 0.26)),
              special_flags=pygame.BLEND_ADD)


# Canonical cabochon = winning variant C dome (lighter, more crystalline glass)
# with the LOCKED specular fix: the top-left specular is a THIN translucent
# crescent, NOT an opaque white slab that eats the parrot. The skin reads
# THROUGH it and out-pops the frame via a +20% rim-light contrast.
CABO_C_LO = (30, 33, 64)      # variant C glass body: airier, lets pale skins read
CABO_C_HI = (9, 11, 30)
CABO_SPEC_A = 150             # ~59% — a translucent sheen, not a glow/slab
CABO_RIM_BOOST = 34           # content out-pops frame
CABO_RIM_ALPHA = 180          # +~20% rim-light contrast


_cabochon_cache: dict = {}


def cabochon(surf, cx, cy, r, glass_lo=CABO_C_LO, glass_hi=CABO_C_HI,
             ring=GOLD_DEEP, ring_a=120):
    """The domed glass WELL the skin sits inside (drawn BEFORE the thumbnail):
    a radial dome (lit-ish centre, deepening to near-black rim) plus a gentle
    inner vignette so contents settle into the well. The translucent dome
    overlay + bezel land later via cabochon_glass()."""
    key = (r, glass_lo, glass_hi)
    disc = _cabochon_cache.get(key)
    if disc is None:
        pad = m(4)
        disc = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
        c = r + pad
        # radial domed glass body
        for i in range(r, 0, -1):
            col = lerp_color(glass_lo, glass_hi, (i / r) ** 1.28)
            pygame.draw.circle(disc, (*col, 255), (c, c), i)
        # gentle inner vignette so contents settle into the well
        vig = pygame.Surface(disc.get_size(), pygame.SRCALPHA)
        for i in range(r, int(r * 0.78), -1):
            a = int(42 * (1 - (i - r * 0.78) / (r * 0.22)))
            pygame.draw.circle(vig, (0, 0, 0, max(0, a)), (c, c), i, max(1, m(0.6)))
        disc.blit(vig, (0, 0))
        _cabochon_cache[key] = disc
    c = r + m(4)
    surf.blit(disc, (cx - c, cy - c))


def cabochon_glass(surf, cx, cy, r, tint=(240, 234, 252)):
    """The translucent glass dome OVERLAY drawn ON TOP of the thumbnail:
    refraction arc bottom-right, a THIN translucent crescent specular top-left,
    a 1px light edge, and the card-ring gold bezel. Call after the thumbnail so
    the macaw sits UNDER glass and reads through the sheen."""
    pad = m(4)
    over = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    # faint bottom-right refraction arc — kept low so it darkens the lower rim
    # without veiling the skin.
    arc = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    for k in range(m(5)):
        a = int(56 * (1 - k / m(5)))
        pygame.draw.arc(arc, (8, 10, 26, a),
                        (c - r + k, c - r + k, (r - k) * 2, (r - k) * 2),
                        math.radians(248), math.radians(342), max(1, m(1)))
    amask = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(amask, (255, 255, 255, 255), (c, c), r - m(1))
    arc.blit(amask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    over.blit(arc, (0, 0))
    # a THIN top-left crescent specular: a lit disc MINUS an offset disc so only
    # the arc hugging the upper-left rim survives, hard-masked to a SLIM band so
    # it never becomes an opaque slab. The skin reads through it.
    spec = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    sr = int(r * 0.74)
    pygame.draw.circle(spec, (255, 255, 255, CABO_SPEC_A),
                       (c - int(r * 0.20), c - int(r * 0.20)), sr)
    cut = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    cut.fill((255, 255, 255, 255))
    pygame.draw.circle(cut, (0, 0, 0, 0),
                       (c + int(r * 0.10), c + int(r * 0.10)), int(r * 0.84))
    spec.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    smask = pygame.Surface(over.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (c, c), r - m(2))
    spec.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    over.blit(spec, (0, 0), special_flags=pygame.BLEND_ADD)
    surf.blit(over, (cx - c, cy - c))
    # thin polished gold bezel = the CARD-RING gold lane (one gold for dome bezel
    # + card frame): dark contact keyline outermost, a fine warm-gold rim, an
    # inner pale glint.
    pygame.draw.circle(surf, (0, 0, 0, 190), (cx, cy), r, max(1, m(1.4)))
    pygame.draw.circle(surf, (*CARD_RING_BRIGHT, 230), (cx, cy), r - m(0.9),
                       max(1, m(1.2)))
    pygame.draw.circle(surf, (246, 220, 140, 150), (cx, cy), r - m(1.8),
                       max(1, m(0.7)))
    # bright glass kiss on the upper-left rim arc only
    edge = pygame.Surface((r * 2 + m(4), r * 2 + m(4)), pygame.SRCALPHA)
    ec = r + m(2)
    pygame.draw.arc(edge, (255, 255, 255, 120),
                    (ec - r + m(1), ec - r + m(1), r * 2 - m(2), r * 2 - m(2)),
                    math.radians(108), math.radians(192), max(1, m(1)))
    surf.blit(edge, (cx - ec, cy - ec), special_flags=pygame.BLEND_ADD)


def bevel_rim(surf, rect, radius, deep, bright, w):
    """Fine emboss: a dark outer keyline + a bright top-left inner stroke."""
    pygame.draw.rect(surf, deep, rect, width=w, border_radius=radius)
    inner = rect.inflate(-w, -w)
    br = bright if len(bright) == 4 else (*bright, 220)
    # bright stroke biased to top + left edges (the lit rim)
    hl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(hl, br, inner.move(-rect.x, -rect.y),
                     width=max(1, w // 2), border_radius=max(1, radius - w))
    grad = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.h):
        a = int(255 * (1 - y / rect.h) ** 1.4)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (rect.w, y))
    hl.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hl, rect.topleft)


_sheen_cache: dict = {}
_ao_cache: dict = {}


def top_sheen(surf, rect, radius, h, peak=46):
    """Glossy top highlight across the upper portion of a panel."""
    key = (rect.w, h, radius, peak)
    sheen = _sheen_cache.get(key)
    if sheen is None:
        sheen = pygame.Surface((rect.w, h), pygame.SRCALPHA)
        for y in range(h):
            pygame.draw.line(sheen, (255, 255, 255, int(peak * (1 - y / h) ** 1.3)),
                             (0, y), (rect.w, y))
        sm = pygame.Surface((rect.w, h), pygame.SRCALPHA)
        pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(),
                         border_top_left_radius=radius, border_top_right_radius=radius)
        sheen.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        _sheen_cache[key] = sheen
    surf.blit(sheen, rect.topleft)


def contact_shadow(surf, rect, radius, depth, alpha=90):
    """Inner ambient-occlusion shadow hugging the bottom + right inner edges."""
    key = (rect.w, rect.h, radius, depth, alpha)
    ao = _ao_cache.get(key)
    if ao is None:
        ao = pygame.Surface(rect.size, pygame.SRCALPHA)
        for i in range(depth):
            a = int(alpha * (1 - i / depth))
            pygame.draw.rect(ao, (0, 0, 0, a),
                             (i, i, rect.w - 2 * i, rect.h - 2 * i),
                             width=max(1, m(0.8)), border_radius=max(1, radius - i))
        # keep only bottom-right via a triangular mask
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255),
                            [(rect.w, 0), (rect.w, rect.h), (0, rect.h)])
        ao.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        _ao_cache[key] = ao
    surf.blit(ao, rect.topleft)


# ── thumbnail cache (rendered at SS box so it stays crisp) ────────────────────
_thumb_cache = {}


def _punch_contrast(img, boost=CABO_RIM_BOOST):
    """Lift the skin's value separation from the dark dome WITHOUT inventing
    detail: a flat additive brighten across the silhouette so the macaw's
    mids/highlights gain range against the near-black well. Alpha is untouched
    (BLEND_RGB_ADD), so the silhouette edge stays clean."""
    out = img.copy()
    out.fill((boost, boost, boost, 0), special_flags=pygame.BLEND_RGB_ADD)
    return out


def _rim_light(img, color=(255, 248, 220), alpha=CABO_RIM_ALPHA, off=None):
    """Crisp top-left rim light so the silhouette pops off the dome: the alpha
    mask nudged up-left, minus the body, tinted bright = a contour highlight."""
    w, h = img.get_size()
    if off is None:
        off = max(1, m(0.6))
    rim = pygame.Surface((w, h), pygame.SRCALPHA)
    # silhouette tinted bright
    sil = img.copy()
    sil.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(sil, (-off, -off))
    # subtract the body so only the protruding top-left edge survives
    cut = img.copy()
    cut.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    rim.set_alpha(alpha)
    return rim


def thumb(sid, box_px):
    key = (sid, box_px)
    out = _thumb_cache.get(key)
    if out is None:
        src = parrot.get_skin_icon(sid) or parrot.get_skin_frame_hi(sid)
        bb = src.get_bounding_rect()
        if bb.width > 0 and bb.height > 0:
            src = src.subsurface(bb).copy()
        sw, sh = src.get_size()
        s = box_px / max(sw, sh)
        scaled = pygame.transform.smoothscale(
            src, (max(1, int(sw * s)), max(1, int(sh * s))))
        out = _punch_contrast(scaled)
        _thumb_cache[key] = out
    return out


def blit_thumb(surf, sid, cx, cy, box_px):
    """Place the (contrast-lifted) skin with a crisp top-left rim light so it
    reads as the lit hero inside the dome, not a flat sticker."""
    t = thumb(sid, box_px)
    r = t.get_rect(center=(cx, cy))
    surf.blit(_rim_light(t), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(t, r.topleft)


# =============================================================================
# Layout metrics (logical px; flow through m())
# =============================================================================
CARD_RAD = 17
R_DISC = 20
CY_DISC = 34
Y_NAME = 63
Y_CHIP = 84
GEM_R = 8

# v5 item-card calibration — locked by exploration
_DOME_R  = 62   # dome radius (device px); box proportional at 1.5×
_BOX_PX  = 104  # item thumbnail box in device px
_ITEM_DY = -2   # 1 logical px below dome centre (shifted 4 lx down from original)
_DOME_DY = 10   # 5 logical px: dome+item shifted down from CY_DISC
_RIBN_DY =  5   # lozenge ribbon 5 device px above the m(55) baseline
_CHIP_DY =  6   # price chip 3 logical px above the m(88) baseline


# ── chip family ───────────────────────────────────────────────────────────────
_gloss_cache: dict = {}


def gloss_sweep(surf, rect, radius, peak=120):
    """A specular sheen that eases smoothly over the FULL button height — bright
    at the crown, tapering to nothing at the foot — so the body reads as ONE
    gradual gradient."""
    key = (rect.w, rect.h, radius, peak)
    sweep = _gloss_cache.get(key)
    if sweep is None:
        sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
        h = max(1, rect.h)
        for y in range(h):
            a = int(peak * (1 - y / h) ** 2.4)
            pygame.draw.line(sweep, (255, 255, 255, a), (0, y), (rect.w, y))
        sm = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
        sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        _gloss_cache[key] = sweep
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


def chip_body_stops(surf, r, radius, stops, rim_dark, rim_bright, gloss=120,
                    gamma=1.05):
    """The ONE chip-body finish shared across the whole chip family, fed by a
    continuous gradient ramp: drop shadow, single smooth gradient fill, one
    gloss sweep, bottom-right AO, then the DOUBLE rim — a dark outer keyline
    UNDER a bright top-left bevel (the canonical defined edge)."""
    drop_shadow(surf, r, radius, blur=m(4), alpha=110, dy=m(2))
    surf.blit(vgrad_stops(r.w, r.h, radius, stops, 255, gamma=gamma), r.topleft)
    gloss_sweep(surf, r, radius, peak=gloss)
    contact_shadow(surf, r, radius, m(3), alpha=80)
    # dark contact keyline first so the bright bevel sits inside a defined edge
    pygame.draw.rect(surf, rim_dark, r, width=max(1, m(1.6)), border_radius=radius)
    bevel_rim(surf, r, radius, rim_dark, (*rim_bright, 235), w=max(1, m(1.5)))


def chip_body(surf, r, radius, top, bot, rim_dark, rim_bright, gloss=120,
              gamma=1.05):
    """Two-stop convenience over chip_body_stops (slate locked / cream EQUIP /
    green EQUIPPED states)."""
    chip_body_stops(surf, r, radius, [(0.0, top), (1.0, bot)], rim_dark,
                    rim_bright, gloss=gloss, gamma=gamma)


# 4-stop coin-metal gradient for the sovereign numeral glyphs
_SOVEREIGN_NUM_STOPS = [
    (0.0,  (255, 240, 180)),
    (0.35, (246, 206, 110)),
    (0.7,  (214, 158,  58)),
    (1.0,  (168, 116,  36)),
]


def _gloss_corrected(surf, rect, radius, peak):
    """BLEND_ADD-safe gloss sweep: draws (a,a,a,255) so the additive amount
    actually follows the curve instead of blowing a near-black body to white."""
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        a = int(peak * (1 - y / h) ** 2.4)
        pygame.draw.line(sweep, (a, a, a, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


def _dark_chip_body(surf, r, radius, stops, rim_dark, rim_bright, gloss=14,
                    gamma=1.04):
    """chip_body_stops for near-black enamel bodies — uses the corrected gloss
    so BLEND_ADD doesn't blow the dark field to white."""
    drop_shadow(surf, r, radius, blur=m(4), alpha=110, dy=m(2))
    surf.blit(vgrad_stops(r.w, r.h, radius, stops, 255, gamma=gamma), r.topleft)
    _gloss_corrected(surf, r, radius, peak=gloss)
    contact_shadow(surf, r, radius, m(3), alpha=80)
    pygame.draw.rect(surf, rim_dark, r, width=max(1, m(1.6)), border_radius=radius)
    bevel_rim(surf, r, radius, rim_dark, (*rim_bright, 235), w=max(1, m(1.5)))


_TAG_W, _TAG_H, _TAG_TILT = 81, 94, -7


def _tag_full(text):
    digits = ''.join(c for c in text if c.isdigit())
    return str(int(digits)) if digits else text


def _tag_price_glyph(text):
    for fs in range(16, 7, -1):
        raw = _stamp_bold(_glyph_base(text, font(fs), 0), m(1.0))
        crushed = pygame.transform.smoothscale(
            raw, (max(1, int(raw.get_width() * 0.86)), raw.get_height()))
        if crushed.get_width() <= 71:
            return crushed
    return crushed


def _tag_draw_price(face, text, affordable):
    """Brushwork sumi ledger: heavy max-bold amount, burnt-copper 'G' token above,
    wedge-taper finishing stroke for the rule. All solid fills — value and
    stroke-weight contrast carry the tag at 5-8px final scale."""
    cx = _TAG_W // 2
    ink = (40, 30, 26) if affordable else (40, 40, 52)
    rule_col_solid = (56, 42, 30) if affordable else (40, 40, 52)

    amt_mask = _tag_price_glyph(text)
    cy_amount = int(_TAG_H * 0.52)
    amt_r = amt_mask.get_rect(center=(cx, cy_amount))
    amt_fill = amt_mask.copy()
    amt_fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(amt_fill, amt_r)
    amt_h = amt_mask.get_height()

    rule_y = cy_amount + amt_h // 2 + m(2)
    rule_w = min(amt_mask.get_width() + m(4), _TAG_W - m(8))
    rule_x = _TAG_W // 2 - rule_w // 2
    peak_h = max(3, m(3))
    min_h  = max(1, m(1))
    pts = [
        (rule_x,          rule_y),
        (rule_x + rule_w, rule_y + (peak_h - min_h) // 2),
        (rule_x + rule_w, rule_y + (peak_h + min_h) // 2),
        (rule_x,          rule_y + peak_h),
    ]
    pygame.draw.polygon(face, rule_col_solid, pts)


def _tag_rot_point(px, py, center):
    th = math.radians(_TAG_TILT)
    dx, dy = px - _TAG_W / 2, py - _TAG_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _tag_draw_check(face):
    """Angular-drop handwritten tick. Steep short left arm, long gentle right arm.
    Near-black ink only. w=8 at SS=2."""
    cx = _TAG_W // 2
    cy = int(_TAG_H * 0.52)
    vx = cx - 2 - 8
    vy = cy + 8 + 9
    vertex = (vx, vy)
    l_arm  = (vx + int(-6  * 1.25), vy + int(-18 * 1.25))
    r_arm  = (vx + int( 28 * 1.25), vy + int(-28 * 1.25))
    w = 8
    ink    = (28, 20, 16)
    shadow = (20, 14, 10, 80)

    pygame.draw.line(face, shadow, (l_arm[0]+1, l_arm[1]+1), (vertex[0]+1, vertex[1]+1), w + 2)
    pygame.draw.circle(face, shadow, (l_arm[0]+1, l_arm[1]+1), (w + 2) // 2)
    pygame.draw.line(face, shadow, (vertex[0]+1, vertex[1]+1), (r_arm[0]+1, r_arm[1]+1), w + 1)
    pygame.draw.circle(face, shadow, (r_arm[0]+1, r_arm[1]+1), (w + 1) // 2)

    pygame.draw.line(face, ink, l_arm, vertex, w)
    pygame.draw.circle(face, ink, l_arm, w // 2)
    pygame.draw.circle(face, ink, vertex, w // 2 + 1)
    pygame.draw.line(face, ink, vertex, r_arm, w)
    pygame.draw.circle(face, ink, r_arm, w // 2)


def price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    """Brushwork sumi hang-tag price chip. Cream swing-tag face; the price
    numeral is struck in heavy ink-brush weight with a wedge-taper finishing
    stroke. Locked state tarnishes to cool grey. Tag tilts -7° on a cord."""
    text = _tag_full(text)
    rad = m(3)
    grommet = (30, 13)

    face = pygame.Surface((_TAG_W, _TAG_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, _TAG_W, _TAG_H)

    if affordable:
        body = vgrad_stops(_TAG_W, _TAG_H, rad,
                           [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                           255, gamma=1.04)
        face.blit(body, (0, 0))
        bevel_rim(face, brect, rad, (80, 52, 12, 200),
                  (255, 240, 190, 200), w=max(1, m(1.2)))
        ring_col = (110, 80, 30)
    else:
        body = vgrad_stops(_TAG_W, _TAG_H, rad,
                           [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))],
                           255, gamma=1.02)
        face.blit(body, (0, 0))
        bevel_rim(face, brect, rad, (54, 58, 74, 200),
                  (214, 218, 232, 200), w=max(1, m(1.2)))
        ring_col = (60, 64, 80)

    _tag_draw_price(face, text, affordable)

    pygame.draw.circle(face, (0, 0, 0, 0), grommet, m(5))
    pygame.draw.circle(face, ring_col, grommet, m(5) + 1, width=max(1, m(1)))

    rot = pygame.transform.rotate(face, _TAG_TILT)
    cord = (190, 165, 115) if affordable else (155, 160, 175)
    # Fixed layout on the 324×200 SS surface — same anchor used by all review
    # scripts so the tag lands identically here and in offline render tools.
    tag_center = (44, 60)
    knot       = (22, 13)
    gx, gy = _tag_rot_point(*grommet, tag_center)
    lw = m(1.5)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] - 1, knot[1] - 1), lw)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] + 2, knot[1] + 2), lw)
    surf.blit(rot, rot.get_rect(center=tag_center))
    pygame.draw.circle(surf, cord, knot, m(1.5))
    pygame.draw.circle(surf, (min(cord[0]+30,255), min(cord[1]+30,255),
                              min(cord[2]+30,255)), knot, max(1, m(0.6)))


def _draw_hang_tag(surf, cx, cy, draw_face_fn=None):
    """Shared geometry for the owned/equipped hang-tag chip. Draws cord, knot,
    cream face with bevel, and grommet. Calls draw_face_fn(face) if provided."""
    rad     = m(3)
    grommet = (30, 13)

    face  = pygame.Surface((_TAG_W, _TAG_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, _TAG_W, _TAG_H)
    body  = vgrad_stops(_TAG_W, _TAG_H, rad,
                        [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                        255, gamma=1.04)
    face.blit(body, (0, 0))
    bevel_rim(face, brect, rad, (80, 52, 12, 200),
              (255, 240, 190, 200), w=max(1, m(1.2)))

    if draw_face_fn is not None:
        draw_face_fn(face)

    pygame.draw.circle(face, (0, 0, 0, 0), grommet, m(5))
    pygame.draw.circle(face, (110, 80, 30), grommet, m(5) + 1, width=max(1, m(1)))

    rot  = pygame.transform.rotate(face, _TAG_TILT)
    cord = (190, 165, 115)
    tag_center = (44, 60)
    knot       = (22, 13)
    gx, gy = _tag_rot_point(*grommet, tag_center)
    lw = m(1.5)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] - 1, knot[1] - 1), lw)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] + 2, knot[1] + 2), lw)
    surf.blit(rot, rot.get_rect(center=tag_center))
    pygame.draw.circle(surf, cord, knot, m(1.5))
    pygame.draw.circle(surf, (min(cord[0]+30,255), min(cord[1]+30,255),
                              min(cord[2]+30,255)), knot, max(1, m(0.6)))


def check_tag_chip(surf, cx, cy, h):
    """Equipped hang-tag: cream face with the ✓ angular-drop mark."""
    _draw_hang_tag(surf, cx, cy, draw_face_fn=_tag_draw_check)


def owned_tag_chip(surf, cx, cy, h):
    """Owned hang-tag: same ✓ tag as equipped but no regalia frame on the card body."""
    _draw_hang_tag(surf, cx, cy, draw_face_fn=_tag_draw_check)


def status_chip(surf, cx, cy, text, h, kind="equip"):
    """EQUIP / EQUIPPED chips — same dark-enamel sovereign body as the price
    chip so all three states read as one product family at a glance.
    EQUIPPED: dark green enamel, bright mint struck rim, checkmark + label.
    EQUIP (owned, not active): dark warm-pewter enamel, aged silver rim."""
    f   = font(h * 0.48 / SS)
    nw  = _glyph_base(text, f, 0).get_width() + m(2)
    pad = m(15)
    rad = h // 2

    if kind == "equipped":
        ckw  = m(14)
        gapc = m(7)
        w    = pad + ckw + gapc + nw + pad
        r    = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        _dark_chip_body(surf, r, rad,
                        [(0.0, (18, 32, 24)), (1.0, (12, 22, 16))],
                        (8, 32, 16), (40, 100, 56), gloss=14, gamma=1.04)
        bevel_rim(surf, r, rad, (20, 88, 44, 235), (100, 230, 148, 220), w=2)
        ink = (80, 220, 130)
        ck  = r.x + pad
        pygame.draw.lines(surf, ink, False,
                          [(ck, cy + m(1)), (ck + m(5), cy + m(6)),
                           (ck + ckw, cy - m(7))], max(1, m(2.8)))
        plain_text(surf, text, f, (ck + ckw + gapc + nw // 2, cy),
                   ink, shadow_a=0, weight=m(0.9))
    else:  # equip — owned, not active
        w = pad * 2 + nw
        r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        _dark_chip_body(surf, r, rad,
                        [(0.0, (28, 24, 36)), (1.0, (20, 16, 28))],
                        (40, 36, 52), (90, 84, 72), gloss=14, gamma=1.04)
        bevel_rim(surf, r, rad, (80, 72, 52, 210), (190, 182, 152, 200), w=2)
        plain_text(surf, text, f, r.center,
                   (180, 170, 140), shadow_a=0, weight=m(0.9))
    return r


# The default price-chip colour used across the live store screen.
PRICE_VARIANT = 1


def state_chip(surf, sid, cx, cy, equipped, secret, h, owned=False,
               variant=PRICE_VARIANT):
    """Actionable state line — three branches:
      equipped=True  → ✓ hang-tag + regalia frame (frame drawn by draw_card)
      owned=True     → ✓ hang-tag, no regalia frame
      else           → price hang-tag (affordability-tinted)"""
    if equipped:
        return check_tag_chip(surf, cx, cy, h)
    if owned:
        return owned_tag_chip(surf, cx, cy, h)
    price = _cost(sid)
    return price_chip(surf, cx, cy, f"{price:,}", h, variant=variant,
                      affordable=store_data.balance() >= price)


def _draw_regalia_frame(surf, body, rad):
    """Constant-lit inner gold track — the approved equipped border treatment.
    Two concentric gold beads separated by a flat dark valley."""
    OUTER  = (236, 202, 116)
    VALLEY = (9, 9, 22)
    INNER  = (255, 240, 190)
    KEY    = (46, 38, 18)
    GLINT  = (255, 248, 224)

    def bead(inset, w, col):
        r = body.inflate(-2 * inset, -2 * inset)
        s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, 255), r, width=w,
                         border_radius=max(1, rad - inset))
        surf.blit(s, (0, 0))

    bead(inset=2,  w=m(3),           col=OUTER)
    bead(inset=8,  w=m(1.4),         col=VALLEY)
    bead(inset=10, w=m(2),           col=INNER)
    bead(inset=13, w=max(1, m(0.6)), col=KEY)

    track = body.inflate(-20, -20)
    leg = m(7)
    corners = [
        (track.left,  track.top,     1,  1),
        (track.right, track.top,    -1,  1),
        (track.left,  track.bottom,  1, -1),
        (track.right, track.bottom, -1, -1),
    ]
    for cxp, cyp, sx, sy in corners:
        pygame.draw.polygon(surf, INNER, [
            (cxp, cyp), (cxp + sx * leg, cyp), (cxp, cyp + sy * leg)])
    for cxp, cyp, sx, sy in corners[:2]:
        pygame.draw.line(surf, GLINT, (cxp, cyp), (cxp + sx * leg, cyp),
                         max(1, m(0.8)))


# ── card ──────────────────────────────────────────────────────────────────────
def _name_on(surf, name, cx, cy, max_w):
    """Item name in cream with a tight dark keyline, auto-shrunk to fit."""
    sz = 15.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 9:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), (250, 248, 240), shadow_a=160,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def _ribbon(surf, tier_word, cx, cy, max_w, pal):
    """A tier-coloured banner with notched ends carrying the tier word (the
    rarity read for the crest layout). No bright gold keyline — just the tier
    gradient + a dark defined edge."""
    f = font(8.5)
    tw = _glyph_base(tier_word, f, m(1.4)).get_width()
    pad = m(12)
    w = min(max_w, tw + pad * 2)
    h = m(15)
    notch = m(5)
    x0, y0 = cx - w // 2, cy - h // 2
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0, [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                       255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    surf.blit(sh, (x0, y0 + m(2)))
    surf.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (4, 5, 16), abspoly, width=max(1, m(1.4)))
    plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26), shadow_a=0,
               tracking=m(1.4), weight=m(0.7))


def _draw_card_v4_ref(surf, sid, rect, equipped, secret, variant=PRICE_VARIANT):
    """v4 production card draw — preserved as a reference only.
    Not called by any production code path; use draw_card() instead."""
    pal = MYSTERY if secret else RARITY[_rarity(sid)]
    rad = m(CARD_RAD)
    drop_shadow(surf, rect, rad, blur=m(8), alpha=160, dy=m(4))
    surf.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
              rect.topleft)
    top_sheen(surf, rect, rad, m(30), peak=62)
    contact_shadow(surf, rect, rad, m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(surf, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(surf, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)
    orig_r = m(R_DISC)
    cx, cy = rect.centerx, rect.y + m(CY_DISC)
    soft_glow(surf, cx, cy, orig_r + m(3), pal["glow"], 30, layers=8)
    cabochon(surf, cx, cy, orig_r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(surf, cx, cy, orig_r + m(6), CREAM, NEAR_BLACK, thick=m(2))
        name = "???"
    else:
        blit_thumb(surf, sid, cx, cy, orig_r * 1.5)
        name = _name(sid)
    cabochon_glass(surf, cx, cy, orig_r, tint=pal["gem"])
    facet_gem(surf, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"], mystery=secret)
    tier_word = "MYSTERY" if secret else _rarity(sid).upper()
    _ribbon(surf, tier_word, cx, rect.y + m(55), rect.w - m(34), pal)
    _name_on(surf, name, cx, rect.y + m(72), rect.w - m(26))
    state_chip(surf, sid, cx, rect.y + m(88), equipped, secret, m(20),
               variant=variant)


def _ribbon_lozenge(surf, tier_word, cx, cy, max_w, pal):
    """Lozenge tier banner — outward pointed ends, shorter than the original
    notched hex."""
    f = font(8.5)
    tw = _glyph_base(tier_word, f, m(1.4)).get_width()
    pad = m(14)
    w = min(max_w, tw + pad * 2)
    h = m(12)
    pt = h // 2
    x0, y0 = cx - w // 2, cy - h // 2
    poly = [(0, h // 2), (pt, 0), (w - pt, 0),
            (w, h // 2), (w - pt, h), (pt, h)]
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0, [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                       255, gamma=1.08)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    surf.blit(sh, (x0, y0 + m(2)))
    surf.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (4, 5, 16), abspoly, width=max(1, m(1.4)))
    plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26), shadow_a=0,
               tracking=m(1.4), weight=m(0.7))


def draw_card(surf, sid, rect, equipped, secret, owned=False, variant=PRICE_VARIANT):
    """The full CONSTELLATION card drawn into `rect` on `surf` (both in device
    px). `secret` masks the thumbnail to ??? + a red mystery gem."""
    pal = MYSTERY if secret else RARITY[_rarity(sid)]
    rad = m(CARD_RAD)
    # DEPTH STACK: soft multi-layer drop shadow (top-left light => offset down)
    drop_shadow(surf, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # body gradient + glossy top sheen + bevel rim + bottom-right contact AO.
    surf.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
              rect.topleft)
    top_sheen(surf, rect, rad, m(30), peak=62)
    contact_shadow(surf, rect, rad, m(9), alpha=120)
    # crisp dark outer keyline UNDER the bright bevel so the card edge is clearly
    # defined against the dark sky.
    from .store_design import DESIGN as _sd     # late: avoids circular import
    if _sd is None:
        pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
        bevel_rim(surf, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
                  w=max(1, m(2.45)))
        # RARITY CREST: a notched tier RIBBON + a faceted tier GEM rank badge
        # top-right. Neutral gold inner tray; obsidian body + gold edge survive.
        tray = rect.inflate(-m(7), -m(7))
        trad = rad - m(4)
        pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                         width=max(1, m(1)), border_radius=trad + m(1))
        pygame.draw.rect(surf, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                         border_radius=trad)
    else:
        _sd["card_frame"](surf, rect, rad)

    # BAND A — cabochon (dome + rim-lit hero) with a soft tier aura
    cx, cy = rect.centerx, rect.y + m(CY_DISC) + _DOME_DY
    soft_glow(surf, cx, cy, _DOME_R + m(3), pal["glow"], 30, layers=8)
    cabochon(surf, cx, cy, _DOME_R, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(surf, cx, cy, _DOME_R + m(6), CREAM, NEAR_BLACK, thick=m(2))
        name = "???"
    else:
        name = _name(sid)
    cabochon_glass(surf, cx, cy, _DOME_R, tint=pal["gem"])
    if not secret:
        blit_thumb(surf, sid, cx, cy - _ITEM_DY, _BOX_PX)

    # CREST GEM — a larger faceted tier gem in the top-right corner.
    facet_gem(surf, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"], mystery=secret)

    # rarity RIBBON (tier word) -> name -> chip, each in its own clear lane.
    tier_word = "MYSTERY" if secret else _rarity(sid).upper()
    _ribbon_lozenge(surf, tier_word, cx, rect.y + m(67) - _RIBN_DY, rect.w - m(34), pal)
    _name_on(surf, name, cx, rect.y + m(78), rect.w - m(26))
    if equipped:
        _draw_regalia_frame(surf, rect, m(CARD_RAD))
    state_chip(surf, sid, cx, rect.y + m(88) - _CHIP_DY, equipped, secret, m(20),
               owned=owned, variant=variant)



# =============================================================================
# Public API — supersample once, cache the per-1x card surface.
# =============================================================================
_card_cache: dict = {}


def render_card(sid: str, *, equipped: bool, owned: bool) -> pygame.Surface:
    """Return a 162x100 per-1x CONSTELLATION card for `sid`. A secret item shows
    ??? + a masked red gem until owned. The price chip's affordability tint reads
    the player's real wallet (store_data.balance). The result is cached by
    (sid, equipped, secret_masked); repeat calls return the SAME surface."""
    secret_masked = _is_secret(sid) and not owned
    key = (sid, bool(equipped), bool(owned), secret_masked)
    cached = _card_cache.get(key)
    if cached is not None:
        return cached

    # Author oversized, then ONE smoothscale down turns the geometry crisp. The
    # body is inset from the surface edges so the drop shadow + equipped halo
    # (both bleed OUTSIDE the body rect) land inside the 162x100 result rather
    # than being clipped — the visible body itself stays fully on-surface.
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    draw_card(big, sid, rect, equipped, secret_masked, owned=owned)
    card = pygame.transform.smoothscale(big, (CARD_W, CARD_H))
    _card_cache[key] = card
    return card


def clear_cache() -> None:
    """Drop every cached card surface. Call when equip/ownership/balance changes
    so affordability tints + the EQUIPPED state re-render on the next build."""
    _card_cache.clear()

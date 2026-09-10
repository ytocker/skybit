"""
Coin-store landing — the LAGOON STILT-MARKET hub.

The store opens onto a tropical over-water stilt-village at golden hour:
seven thatched market huts on wooden stilts rise out of a glittering gold
lagoon, each previewing its category's REAL in-game item in a glass dome,
with palms + hazy islets framing the scene and Pip banking through the upper
sky. The sky eases UP into the same indigo+gold nebula the category grids
open into, so tapping a stall dissolves cohesively into the existing
CONSTELLATION store.

The locked round_4 look was authored resolution-independently from a
supersample factor: every hut, stilt, plank, glint and glyph is drawn
oversized, then ONE smoothscale down turns the geometry into crisp AA edges.
That whole scene is STATIC, so the runtime builds it ONCE into a
module-level cache and blits it per frame; only the live coin balance (which
changes as runs bank coins) is redrawn on top each frame.

The CONSTELLATION primitives are vendored here verbatim rather than imported
from the docs prototype tree, because that tree is NOT bundled into the
shipped game — only main.py / inject_theme.py / game/ ship. Vendoring keeps
the hub a pure-pygame, single-DNA module that works on both build targets.

Both build targets safe: pure pygame, no numpy, no mixer, no filesystem
writes, no desktop/browser-only API.
"""
import math
import random

import pygame

from game.config import W, H
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _RED_OUTLINE
from game import parrot
from game import store_catalog


# ── supersample ───────────────────────────────────────────────────────────────
# SS=2 (vs the doc's SS=4 PNG export): a 720x1280 build smoothscaled to 360x640
# still reads clean in-game but is ~4x cheaper to build — the one-time build
# also runs on the slower pygbag/WASM Python at store-open, so a tunable factor
# keeps that pause short.
SS = 2
DW, DH = W * SS, H * SS


def m(v):
    """Logical px -> device px. Keeps geometry authored at 360x640 scale."""
    return int(round(v * SS))


def font(size):
    """Project bold font at supersample size so glyph edges resolve crisp."""
    return _font(max(1, int(round(size * SS))), True)


# Canonical CONSTELLATION gold lane names, re-pointed at the in-game hud palette
# so the hub's chrome shares the store's one gold.
GOLD = _GOLD_BRIGHT
GOLD_PALE = _GOLD_PALE
GOLD_DEEP = _GOLD_DEEP
# Canonical GOLD RAMP A — the ONE gold for every gold FILL (balance number,
# label type). A single smooth vertical ramp; its endpoints feed gradient_text.
GOLD_A_STOPS = [
    (0.00, (244, 192, 88)),
    (0.32, (228, 162, 56)),
    (0.66, (196, 124, 34)),
    (1.00, (150, 92, 18)),
]
GOLD_A_TOP = GOLD_A_STOPS[0][1]
GOLD_A_BOT = GOLD_A_STOPS[-1][1]

# Cabochon glass-well body tones (variant C: airier glass that lets pale skins
# read) so the dome bezel + card-ring share one gold lane.
CABO_LO = (22, 24, 50)
CABO_HI = (6, 7, 20)
CABO_C_LO = (30, 33, 64)
CABO_C_HI = (9, 11, 30)
CABO_SPEC_A = 150
CABO_RIM_BOOST = 34
CABO_RIM_ALPHA = 180
CARD_RING_BRIGHT = (236, 202, 116)


# =============================================================================
# Vendored CONSTELLATION primitives — all SS-aware, taking device-px coords.
# Copied from the locked store DNA so the hub needs no docs/ import.
# =============================================================================
def lerp_stops(stops, t):
    """Sample a piecewise-linear colour ramp at t in [0,1] as ONE continuous
    gradient (never a two-tone splice)."""
    t = max(0.0, min(1.0, t))
    n = len(stops)
    seg = 0
    while seg < n - 2 and t > stops[seg + 1][0]:
        seg += 1
    t0, c0 = stops[seg]
    t1, c1 = stops[seg + 1]
    local = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
    return lerp_color(c0, c1, max(0.0, min(1.0, local)))


def vgrad_stops(w, h, radius, stops, alpha=255, gamma=1.0):
    """Vertical rounded-rect filled by a continuous multi-stop ramp."""
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = (y / max(1, h - 1)) ** gamma
        c = lerp_stops(stops, t)
        pygame.draw.line(body, (*c, alpha), (0, y), (w - 1, y))
    if radius > 0:
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def vgrad(w, h, radius, top, bot, alpha=255, gamma=1.0):
    """Two-stop convenience over vgrad_stops (non-gold panels)."""
    return vgrad_stops(w, h, radius, [(0.0, top), (1.0, bot)], alpha, gamma)


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


def capped_glow(surf, cx, cy, radius, color, peak_alpha, layers=10):
    """A feathered glow whose rings composite with BLEND_RGBA_MAX so overlapping
    centres take the STRONGEST ring alpha instead of SUMMING. soft_glow's additive
    stack is a white-out engine here — warm rings summed every channel past 255
    into pure white where auras + coin glows + the gold dome all overlapped. MAX
    caps a glow at one opaque pass of its OWN colour, so a gold bloom stays gold
    and can never reach white."""
    tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.8)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        tmp.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_RGBA_MAX)
    surf.blit(tmp, (0, 0))


def drop_shadow(surf, rect, radius, blur, alpha, dy):
    """Multi-layer blurred outer shadow, offset down (top-left light source)."""
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 1.7 / blur * 2.4)
        if a <= 0:
            continue
        r = pygame.Rect(rect.x - i, rect.y - i + dy, rect.w + 2 * i, rect.h + 2 * i)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(), border_radius=radius + i)
        surf.blit(s, r.topleft)


def contact_shadow(surf, rect, radius, depth, alpha=90):
    """Inner ambient-occlusion shadow hugging the bottom + right inner edges."""
    ao = pygame.Surface(rect.size, pygame.SRCALPHA)
    for i in range(depth):
        a = int(alpha * (1 - i / depth))
        pygame.draw.rect(ao, (0, 0, 0, a),
                         (i, i, rect.w - 2 * i, rect.h - 2 * i),
                         width=max(1, m(0.8)), border_radius=max(1, radius - i))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(rect.w, 0), (rect.w, rect.h), (0, rect.h)])
    ao.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(ao, rect.topleft)


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


def _stamp_bold(base, weight):
    """Faux-bold: composite the glyph onto itself at a RING of offsets one
    `weight` out so strokes grow evenly without filling counters solid. The
    project ships only the Bold ttf, so authored 'thicker' is this multi-stamp
    at SS where the fractional growth survives the downscale."""
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
    out.blit(base, (pad, pad))
    return out


def gradient_text(surf, txt, font_obj, center, top, bot,
                  outline=None, ox=None, shadow=True, tracking=0, glow=None,
                  weight=None, keyline=None, kw=None):
    """Gradient-filled type, faux-bolded for weight, with a crisp dark keyline
    so type reads heavy + sharp at the downscaled target."""
    base = _glyph_base(txt, font_obj, tracking)
    if weight is None:
        weight = m(0.9)
    base = _stamp_bold(base, weight)
    w, hh = base.get_size()
    grad = pygame.Surface((w, hh), pygame.SRCALPHA)
    for y in range(hh):
        pygame.draw.line(grad, lerp_color(top, bot, y / max(1, hh - 1)),
                         (0, y), (w, y))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = base.get_rect(center=center)
    if shadow:
        sh = base.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(150)
        surf.blit(sh, (r.x + m(0.5), r.y + m(2)))
    if outline:
        p = ox if ox is not None else m(1.5)
        out = base.copy()
        out.fill((*outline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 30):
            dx = int(round(p * math.cos(math.radians(ang))))
            dy = int(round(p * math.sin(math.radians(ang))))
            surf.blit(out, (r.x + dx, r.y + dy))
    if keyline:
        p = kw if kw is not None else m(1)
        kl = base.copy()
        kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 45):
            dx = int(round(p * math.cos(math.radians(ang))))
            dy = int(round(p * math.sin(math.radians(ang))))
            surf.blit(kl, (r.x + dx, r.y + dy))
    surf.blit(grad, r.topleft)
    return r


def plain_text(surf, txt, font_obj, center, color, shadow_a=150, tracking=0,
               weight=None, keyline=None, kw=None):
    """Solid-colour type, faux-bolded for weight, with an optional crisp dark
    keyline so labels read heavy + sharp against the dark store ground."""
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


def coin_glyph(surf, cx, cy, r):
    """The EXACT in-game coin smoothscaled to the requested radius, so the store
    coin is identical to the one the player collects in play."""
    from game.entities import _get_coin_face
    face = _get_coin_face()
    d = max(2, int(r * 2))
    img = pygame.transform.smoothscale(face, (d, d))
    surf.blit(img, img.get_rect(center=(cx, cy)))


def title_wordmark(surf, txt, center, size, tracking):
    """The standard Skybit menu title: a solid gold fill + red outline + a soft
    near-black drop shadow (the gold-on-red wordmark used across the menus)."""
    f = font(size)
    base = _stamp_bold(_glyph_base(txt, f, tracking), m(1.1))
    r = base.get_rect(center=center)
    out = base.copy()
    out.fill((*_RED_OUTLINE, 255), special_flags=pygame.BLEND_RGBA_MULT)
    px = m(2)
    for ox, oy in ((-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh = base.copy()
    sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(170)
    surf.blit(sh, (r.x + m(2), r.y + m(3)))
    gold = base.copy()
    gold.fill((*GOLD, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(gold, r.topleft)
    return r


def gold_rule(surf, x0, x1, y, gold, peak=170, thick=None):
    """Hairline gold rule that fades to nothing at both ends."""
    thick = thick if thick is not None else max(1, m(1))
    w = x1 - x0
    line = pygame.Surface((w, thick + m(2)), pygame.SRCALPHA)
    for sx in range(w):
        hx = abs(sx - w / 2) / (w / 2)
        a = int(peak * (1.0 - hx ** 1.6))
        if a <= 0:
            continue
        for ty in range(thick):
            line.set_at((sx, m(1) + ty), (*gold, a))
    surf.blit(line, (x0, y - thick // 2))


def bevel_rim(surf, rect, radius, deep, bright, w):
    """Fine emboss: a dark outer keyline + a bright top-left inner stroke."""
    pygame.draw.rect(surf, deep, rect, width=w, border_radius=radius)
    inner = rect.inflate(-w, -w)
    br = bright if len(bright) == 4 else (*bright, 220)
    hl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(hl, br, inner.move(-rect.x, -rect.y),
                     width=max(1, w // 2), border_radius=max(1, radius - w))
    grad = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.h):
        a = int(255 * (1 - y / rect.h) ** 1.4)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (rect.w, y))
    hl.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hl, rect.topleft)


def top_sheen(surf, rect, radius, h, peak=46):
    """Glossy top highlight across the upper portion of a panel."""
    sheen = pygame.Surface((rect.w, h), pygame.SRCALPHA)
    for y in range(h):
        pygame.draw.line(sheen, (255, 255, 255, int(peak * (1 - y / h) ** 1.3)),
                         (0, y), (rect.w, y))
    sm = pygame.Surface((rect.w, h), pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(),
                     border_top_left_radius=radius, border_top_right_radius=radius)
    sheen.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, rect.topleft)


def cabochon(surf, cx, cy, r, glass_lo=CABO_C_LO, glass_hi=CABO_C_HI):
    """The domed glass WELL the thumbnail sits inside: a radial dome (lit-ish
    centre deepening to near-black rim) plus a gentle inner vignette so contents
    settle into the well, not float on a flat disc."""
    pad = m(4)
    disc = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    for i in range(r, 0, -1):
        col = lerp_color(glass_lo, glass_hi, (i / r) ** 1.28)
        pygame.draw.circle(disc, (*col, 255), (c, c), i)
    vig = pygame.Surface(disc.get_size(), pygame.SRCALPHA)
    for i in range(r, int(r * 0.78), -1):
        a = int(42 * (1 - (i - r * 0.78) / (r * 0.22)))
        pygame.draw.circle(vig, (0, 0, 0, max(0, a)), (c, c), i, max(1, m(0.6)))
    disc.blit(vig, (0, 0))
    surf.blit(disc, (cx - c, cy - c))


def cabochon_glass(surf, cx, cy, r, tint=(240, 234, 252)):
    """The translucent glass dome OVERLAY drawn ON TOP of the thumbnail:
    refraction arc bottom-right, a THIN translucent crescent specular top-left,
    a light edge, and the card-ring gold bezel — so the macaw sits UNDER glass
    and reads through the sheen."""
    pad = m(4)
    over = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
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
    pygame.draw.circle(surf, (0, 0, 0, 190), (cx, cy), r, max(1, m(1.4)))
    pygame.draw.circle(surf, (*CARD_RING_BRIGHT, 230), (cx, cy), r - m(0.9),
                       max(1, m(1.2)))
    pygame.draw.circle(surf, (246, 220, 140, 150), (cx, cy), r - m(1.8),
                       max(1, m(0.7)))
    edge = pygame.Surface((r * 2 + m(4), r * 2 + m(4)), pygame.SRCALPHA)
    ec = r + m(2)
    pygame.draw.arc(edge, (255, 255, 255, 120),
                    (ec - r + m(1), ec - r + m(1), r * 2 - m(2), r * 2 - m(2)),
                    math.radians(108), math.radians(192), max(1, m(1)))
    surf.blit(edge, (cx - ec, cy - ec), special_flags=pygame.BLEND_ADD)


def _punch_contrast(img, boost=CABO_RIM_BOOST):
    """Lift the skin's value separation from the dark dome WITHOUT inventing
    detail: a flat additive brighten across the silhouette so the macaw's
    mids/highlights gain range against the near-black well. Alpha is untouched
    so the silhouette edge stays clean."""
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
    sil = img.copy()
    sil.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(sil, (-off, -off))
    cut = img.copy()
    cut.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rim.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    rim.set_alpha(alpha)
    return rim


def downscale(device_surf):
    """Smoothscale the SS build to the final 360x640 target — the ONE pass that
    turns oversized geometry into crisp anti-aliased edges."""
    return pygame.transform.smoothscale(device_surf, (W, H))


# =============================================================================
# Palette — golden-hour lagoon easing UP to the indigo+gold jewel nebula apex.
# The apex stops are the CONSTELLATION BG anchors so the sky reads as the SAME
# sky the stall screens open into.
# =============================================================================
SKY_STOPS = [
    (0.00, (10, 11, 40)),
    (0.16, (24, 22, 70)),
    (0.34, (62, 46, 104)),
    (0.50, (150, 96, 120)),
    (0.66, (236, 150, 96)),
    (0.78, (255, 196, 112)),
    (0.86, (255, 214, 140)),
]
SUN_HALO = (255, 176, 88)

WATER_STOPS = [
    (0.00, (236, 176, 96)),
    (0.18, (206, 142, 96)),
    (0.40, (96, 96, 120)),
    (0.72, (32, 52, 78)),
    (1.00, (16, 30, 54)),
]
GLITTER = (255, 232, 178)

THATCH_HI = (214, 168, 104)
THATCH_LO = (118, 78, 38)
THATCH_EDGE = (74, 46, 22)
WOOD_HI = (198, 150, 96)
WOOD_MID = (150, 104, 60)
WOOD_LO = (92, 60, 32)
WOOD_EDGE = (54, 33, 16)
AWN_RED = (212, 56, 50)
AWN_RED_D = (150, 30, 32)
AWN_CREAM = (244, 232, 206)
AWN_CREAM_D = (206, 188, 158)
STALL_DARK = (30, 24, 34)
LABEL_KEY = (40, 22, 14)
PALM_FROND = (44, 92, 64)
PALM_FROND_HI = (86, 142, 92)
ISLET = (58, 56, 96)

REFL_HUT = (52, 48, 62)
REFL_THATCH = (78, 60, 54)


# Stall -> hut binding. Seven groups, each shows its category's REAL preview
# thumbnail in a glass cabochon. Keys here ARE the public stall_rects keys.
STALLS = [
    ("costume", "COSTUMES"),
    ("parrot",  "PARROTS"),
    ("animal",  "ANIMALS"),
    ("shoes",   "SHOES"),
    ("hats",    "HATS"),
    ("shades",  "SHADES"),
    ("parcels", "PARCELS"),
]
LABELS = {g: lbl for g, lbl in STALLS}

# Two-tier village arrangement so all 7 huts read at 360px without overlap.
#   group, cx fraction, deck_y fraction, scale, hero
LAYOUT = [
    ("shoes",    0.155, 0.572, 0.80, False),
    ("animal",   0.500, 0.548, 0.80, False),
    ("hats",     0.845, 0.572, 0.80, False),
    ("parrot",   0.142, 0.788, 0.92, False),
    ("costume",  0.858, 0.788, 0.92, False),
    ("shades",   0.500, 0.704, 0.86, False),
    ("parcels",  0.500, 0.862, 0.96, True),
]


# Which specific catalog item each stall dome showcases.
_STALL_HERO_ITEM = {
    "parrot":  "skin_lorikeet",
    "parcels": "parcel_postmark",
}


def _group_thumb(group):
    """REAL in-game preview for a stall: the icon/first-frame of its hero item.

    SHADES' first catalog id is NO SHADES (a bare-eyed parrot, no icon), so for
    SHADES we skip to the first shades id that owns a real eyewear icon.
    Returns (surface, letterbox) — letterbox flags aspect-extreme items so the
    placer contains them in the dome rather than blowing past the glass."""
    ids = store_catalog.ids_of_group(group)
    sid = _STALL_HERO_ITEM.get(group, ids[0])
    src = None
    if group == "shades":
        for cand in ids:
            ic = parrot.get_skin_icon(cand)
            if ic is not None:
                src, sid = ic, cand
                break
    if src is None:
        src = parrot.get_skin_icon(sid) or parrot.get_skin_frame(sid, 1, 0.0)
    bb = src.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        src = src.subsurface(bb).copy()
    w, h = src.get_size()
    letterbox = max(w, h) / max(1, min(w, h)) > 1.7
    return src, letterbox


# =============================================================================
# Background — golden-hour sky, low sun, emerging stars, distant islets, palms.
# =============================================================================
def _draw_palm(surf, base_x, base_y, height, flip, seed):
    """A silhouetted-but-lit coconut palm: a curved trunk + a crown of long
    drooping fronds, rim-lit on the top-left sun side, framing the lagoon."""
    rnd = random.Random(seed)
    sign = -1 if flip else 1
    segs = 9
    px, py = base_x, base_y
    pts_l, pts_r = [], []
    for i in range(segs + 1):
        t = i / segs
        lean = sign * math.sin(t * 1.3) * height * 0.22
        x = base_x + lean
        y = base_y - t * height
        wdt = m(9) * (1.0 - t * 0.55)
        pts_l.append((x - wdt, y))
        pts_r.append((x + wdt, y))
        px, py = x, y
    trunk = pts_l + pts_r[::-1]
    pygame.draw.polygon(surf, WOOD_LO, trunk)
    pygame.draw.lines(surf, lerp_color(WOOD_LO, SUN_HALO, 0.4), False, pts_l,
                      max(1, m(1.6)))
    crown_x, crown_y = px, py
    n_fronds = 9
    for k in range(n_fronds):
        a0 = math.radians(200 + k * (140 / (n_fronds - 1)))
        length = height * rnd.uniform(0.42, 0.60)
        droop = rnd.uniform(0.5, 0.95)
        midx = crown_x + math.cos(a0) * length * 0.5
        midy = crown_y + math.sin(a0) * length * 0.5 - length * 0.12
        endx = crown_x + math.cos(a0) * length
        endy = crown_y + math.sin(a0) * length + length * droop * 0.5
        spine = []
        for s in range(11):
            tt = s / 10
            xx = (1 - tt) ** 2 * crown_x + 2 * (1 - tt) * tt * midx + tt ** 2 * endx
            yy = (1 - tt) ** 2 * crown_y + 2 * (1 - tt) * tt * midy + tt ** 2 * endy
            spine.append((xx, yy))
        lit = a0 < math.radians(270)
        col = PALM_FROND_HI if lit else PALM_FROND
        for s in range(1, len(spine)):
            x1, y1 = spine[s - 1]
            x2, y2 = spine[s]
            dx, dy = x2 - x1, y2 - y1
            nrm = math.hypot(dx, dy) or 1
            ox, oy = -dy / nrm, dx / nrm
            spread = m(7) * (1 - s / len(spine)) + m(3)
            pygame.draw.polygon(surf, col, [
                (x1, y1), (x2 + ox * spread, y2 + oy * spread),
                (x2, y2), (x2 - ox * spread, y2 - oy * spread)])
        pygame.draw.lines(surf, lerp_color(col, NEAR_BLACK, 0.35), False, spine,
                          max(1, m(1.0)))
    for _ in range(3):
        cx = crown_x + rnd.randint(-m(6), m(6))
        cy = crown_y + rnd.randint(m(2), m(8))
        pygame.draw.circle(surf, (78, 54, 30), (int(cx), int(cy)), m(4))
        pygame.draw.circle(surf, (120, 88, 52), (int(cx - m(1)), int(cy - m(1))), m(2))


def _build_static_sky():
    """The whole behind-the-water backdrop: multi-stop golden-hour->nebula sky,
    a raked low sun + halo, a sparse field of emerging stars confined to the
    indigo apex, hazy violet islets on the waterline, and two framing palms."""
    sky = pygame.Surface((DW, DH))
    sky.blit(multistop_v(DW, DH, SKY_STOPS), (0, 0))

    sx, sy = int(DW * 0.26), int(DH * 0.300)
    halo_r = m(120)
    halo = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
    for i in range(halo_r, 0, -1):
        t = i / halo_r
        a = int(150 * (1.0 - t) ** 2.2)
        pygame.draw.circle(halo, (255, 158, 88, a), (halo_r, halo_r), i)
    sky.blit(halo, (sx - halo_r, sy - halo_r))
    disc_r = m(46)
    sun_disc = pygame.Surface((disc_r * 2, disc_r * 2), pygame.SRCALPHA)
    sun_stops = [
        (0.00, (255, 222, 150)),
        (0.45, (255, 200, 116)),
        (0.78, (255, 174, 96)),
        (1.00, (242, 150, 80)),
    ]
    for i in range(disc_r, 0, -1):
        t = i / disc_r
        for k in range(len(sun_stops) - 1):
            t0, c0 = sun_stops[k]
            t1, c1 = sun_stops[k + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
                col = tuple(int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
                break
        else:
            col = sun_stops[-1][1]
        pygame.draw.circle(sun_disc, (*col, 255), (disc_r, disc_r), i)
    sky.blit(sun_disc, (sx - disc_r, sy - disc_r))

    rnd = random.Random(417)
    stars = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for _ in range(120):
        x = rnd.randint(0, DW)
        yf = rnd.uniform(0.0, 0.42)
        y = int(yf * DH)
        fade = max(0.0, 1.0 - yf / 0.42)
        r = m(rnd.uniform(0.4, 1.5))
        a = int(rnd.randint(40, 170) * fade)
        if a <= 0:
            continue
        tint = rnd.choice([(255, 252, 240), (224, 224, 255), (255, 236, 200)])
        pygame.draw.circle(stars, (*tint, a), (x, y), max(1, int(r)))
    for _ in range(9):
        x = rnd.randint(m(20), DW - m(20))
        y = int(rnd.uniform(0.04, 0.30) * DH)
        L = m(rnd.uniform(3, 5.5))
        a = rnd.randint(90, 160)
        col = (255, 244, 210, a)
        pygame.draw.line(stars, col, (x - L, y), (x + L, y), max(1, m(0.7)))
        pygame.draw.line(stars, col, (x, y - L), (x, y + L), max(1, m(0.7)))
    pygame.draw.circle(stars, (0, 0, 0, 0), (sx, sy), int(disc_r * 1.35))
    sky.blit(stars, (0, 0), special_flags=pygame.BLEND_ADD)

    scrim = pygame.Surface((DW, DH), pygame.SRCALPHA)
    s0, s1 = 0.36, 0.50
    for y in range(int(s0 * DH), int(s1 * DH)):
        t = (y - s0 * DH) / ((s1 - s0) * DH)
        a = int(78 * max(0.0, math.sin(t * math.pi)) ** 0.9)
        pygame.draw.line(scrim, (40, 38, 78, a), (0, y), (DW, y))
    sky.blit(scrim, (0, 0))

    horizon = int(DH * 0.485)
    for ix, iw, ih, tone in ((0.10, 0.22, 0.030, 0.55),
                             (0.40, 0.30, 0.044, 0.70),
                             (0.74, 0.26, 0.034, 0.50),
                             (0.92, 0.18, 0.024, 0.40)):
        cx = int(DW * ix)
        hw = int(DW * iw * 0.5)
        hh = int(DH * ih)
        col = lerp_color(ISLET, SKY_STOPS[4][1], 1.0 - tone)
        pts = [(cx - hw, horizon)]
        n = 8
        for k in range(n + 1):
            t = k / n
            x = cx - hw + int(2 * hw * t)
            bump = math.sin(t * math.pi) * hh * (0.6 + 0.4 * math.sin(t * 9 + ix * 20))
            pts.append((x, horizon - int(bump)))
        pts.append((cx + hw, horizon))
        pygame.draw.polygon(sky, col, pts)
        veil = pygame.Surface((DW, DH), pygame.SRCALPHA)
        pygame.draw.polygon(veil, (*SKY_STOPS[4][1], 70), pts)
        sky.blit(veil, (0, 0))

    _draw_palm(sky, int(DW * 0.045), int(DH * 0.50), m(150), flip=False, seed=2)
    _draw_palm(sky, int(DW * 0.965), int(DH * 0.505), m(168), flip=True, seed=7)
    return sky


# =============================================================================
# Lagoon water — glitter band + soft hut reflections.
# =============================================================================
def draw_water(surf):
    """The gold lagoon: a multi-stop water gradient from a hot horizon down to a
    cool deep trough, a tapering gold sun-glitter band under the sun, and a field
    of horizontal wavelets that get sparser + dimmer with depth."""
    horizon = int(DH * 0.485)
    water_h = DH - horizon
    band = vgrad_stops(DW, water_h, 0, WATER_STOPS, 255)
    surf.blit(band, (0, horizon))

    sun_x = int(DW * 0.26)
    rnd = random.Random(91)
    glit = pygame.Surface((DW, water_h), pygame.SRCALPHA)
    rows = 56
    for i in range(rows):
        t = i / rows
        y = int(t * water_h)
        spread = m(20) + t * m(120)
        depth_fade = (1.0 - t) ** 0.8
        n = int(4 + t * 9)
        for _ in range(n):
            gx = sun_x + rnd.uniform(-spread, spread)
            falloff = max(0.0, 1.0 - abs(gx - sun_x) / (spread + 1))
            a = int(190 * falloff * depth_fade)
            if a <= 0:
                continue
            ln = m(rnd.uniform(2.5, 8)) * (0.5 + t)
            yy = y + rnd.randint(-m(2), m(2))
            pygame.draw.line(glit, (*GLITTER, a),
                             (gx - ln, yy), (gx + ln, yy), max(1, m(1.0)))
    surf.blit(glit, (0, horizon), special_flags=pygame.BLEND_ADD)

    waves = pygame.Surface((DW, water_h), pygame.SRCALPHA)
    for i in range(40):
        t = i / 40
        y = int(t * water_h)
        a = int(46 * (1.0 - t * 0.7))
        col = lerp_color(WATER_STOPS[0][1], WHITE, 0.3)
        seg = m(rnd.uniform(20, 70))
        x = rnd.randint(0, DW)
        for _ in range(rnd.randint(2, 5)):
            pygame.draw.line(waves, (*col, a), (x, y), (x + seg, y), max(1, m(0.8)))
            x += seg + m(rnd.uniform(30, 90))
            if x > DW:
                break
    surf.blit(waves, (0, horizon), special_flags=pygame.BLEND_ADD)
    return horizon


def hut_reflection(surf, cx, deck_y, width, scale, horizon):
    """A NATURAL water reflection of a hut: a cool, desaturated, low-alpha echo
    of the roof + body that fades with depth and is broken up by horizontal
    ripple gaps + a subtle wobble — like real dusk water, never a coloured aura.
    NORMAL blend (darkens the water it sits on), never additive."""
    refl_h = int(m(120) * scale)
    if refl_h <= 0 or deck_y < horizon:
        return
    col = pygame.Surface((width, refl_h), pygame.SRCALPHA)
    half = width / 2
    for y in range(refl_h):
        t = y / refl_h
        tone = lerp_color(REFL_THATCH, REFL_HUT, min(1.0, t * 1.7))
        depth = (1.0 - t) ** 1.5
        ripple = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(y / m(5.0)))
        a = int(46 * depth * ripple)
        if a <= 0:
            continue
        wob = math.sin(y / m(13.0)) * m(4) * (1.0 - t)
        taper = half * (0.94 - 0.30 * t)
        x0 = half + wob - taper
        x1 = half + wob + taper
        pygame.draw.line(col, (*tone, a), (x0, y), (x1, y))
    surf.blit(col, (int(cx - half), deck_y))


# =============================================================================
# Stilt hut — the market stall as an over-water thatched hut.
# =============================================================================
def draw_stilts(surf, cx, deck_y, half_w, post_len, ring_scale=1.0):
    """The wooden posts the hut stands on, driven into the lagoon: four legs with
    cross-bracing, lit top-left, each with a contact ripple where it meets the
    water + a short submerged reflection. `ring_scale` widens the contact rings
    for NEARER huts as a depth cue."""
    legs_x = [cx - half_w + m(6), cx - half_w + m(20),
              cx + half_w - m(20), cx + half_w - m(6)]
    water_y = deck_y + int(post_len * 0.74)
    foot_y = deck_y + post_len
    post_w = m(7)
    for i, lx in enumerate(legs_x):
        body = vgrad(post_w, foot_y - deck_y, 0, WOOD_HI, WOOD_LO)
        surf.blit(body, (lx - post_w // 2, deck_y))
        pygame.draw.rect(surf, WOOD_EDGE,
                         (lx - post_w // 2, deck_y, post_w, foot_y - deck_y),
                         width=max(1, m(1)))
        pygame.draw.line(surf, lerp_color(WOOD_HI, WHITE, 0.3),
                         (lx - post_w // 2 + m(1), deck_y),
                         (lx - post_w // 2 + m(1), foot_y), max(1, m(1)))
        rr = int(m(15) * ring_scale)
        rip = pygame.Surface((rr * 2 + m(2), rr + m(2)), pygame.SRCALPHA)
        rc = (rr + m(1), (rr + m(2)) // 2)
        rings = ((1.00, 30, 0.9), (0.74, 52, 1.0), (0.50, 78, 1.2), (0.30, 96, 1.3))
        for fr, a, th in rings:
            ew = int(rr * 2 * fr)
            eh = int(rr * fr)
            if ew <= 2 or eh <= 1:
                continue
            tone = lerp_color((150, 178, 196), (96, 130, 158), 1.0 - fr)
            pygame.draw.ellipse(rip, (*tone, a),
                                (rc[0] - ew // 2, rc[1] - eh // 2, ew, eh),
                                max(1, m(th)))
        pygame.draw.arc(rip, (*lerp_color((200, 214, 222), GLITTER, 0.35), 150),
                        (rc[0] - rr + m(3), rc[1] - rr // 2, rr * 2 - m(6), rr),
                        math.radians(150), math.radians(250), max(1, m(1.4)))
        surf.blit(rip, (lx - rc[0], water_y - rc[1]))
        sub = vgrad(post_w, m(14), 0, WOOD_LO, WOOD_EDGE, alpha=110)
        surf.blit(sub, (lx - post_w // 2, water_y), special_flags=pygame.BLEND_ADD)
    for a, b in ((legs_x[0], legs_x[1]), (legs_x[2], legs_x[3])):
        my = (deck_y + foot_y) // 2
        pygame.draw.line(surf, WOOD_MID, (a, deck_y + m(6)), (b, my + m(6)), max(1, m(3)))
        pygame.draw.line(surf, WOOD_MID, (a, my + m(6)), (b, deck_y + m(6)), max(1, m(3)))
    pygame.draw.line(surf, WOOD_LO, (legs_x[1], deck_y + m(10)),
                     (legs_x[2], deck_y + m(10)), max(1, m(3)))


def draw_plank(surf, x0, y0, x1, y1, width):
    """A little boardwalk plank linking two huts: a foreshortened timber strip
    with plank seams + a dark contact AO underneath."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    quad = [(x0 + nx * width / 2, y0 + ny * width / 2),
            (x1 + nx * width / 2, y1 + ny * width / 2),
            (x1 - nx * width / 2, y1 - ny * width / 2),
            (x0 - nx * width / 2, y0 - ny * width / 2)]
    sh = [(px, py + m(5)) for px, py in quad]
    shs = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(shs, (0, 0, 0, 90), sh)
    surf.blit(shs, (0, 0))
    pygame.draw.polygon(surf, WOOD_MID, quad)
    pygame.draw.polygon(surf, WOOD_EDGE, quad, width=max(1, m(1.4)))
    for s in range(1, 6):
        t = s / 6
        ax = x0 + dx * t + nx * width / 2
        ay = y0 + dy * t + ny * width / 2
        bx = x0 + dx * t - nx * width / 2
        by = y0 + dy * t - ny * width / 2
        pygame.draw.line(surf, WOOD_LO, (ax, ay), (bx, by), max(1, m(1)))
    pygame.draw.line(surf, WOOD_HI, quad[0], quad[1], max(1, m(1.4)))


def _draw_parcel_padding(surf, cx, cy, dome_r):
    """A padded-mailer body painted behind the real envelope icon so PARCELS
    reads as a THICK 3D package, not a flat card: a rounded warm-kraft block with
    a BULGED lower edge, a lit top sheen, and a dark seated contour."""
    KRAFT_HI = (196, 158, 108)
    KRAFT = (168, 130, 84)
    KRAFT_LO = (118, 88, 54)
    bw = int(dome_r * 1.34)
    bh = int(dome_r * 1.42)
    rect = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)
    rad = int(dome_r * 0.28)
    sh = rect.inflate(m(4), m(4)); sh.move_ip(0, m(2))
    pygame.draw.rect(surf, (14, 10, 6, 160), sh, border_radius=rad)
    surf.blit(vgrad(rect.w, rect.h, rad, KRAFT_HI, KRAFT_LO), rect.topleft)
    belly = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    by = int(rect.h * 0.52)
    pygame.draw.ellipse(belly, (*KRAFT, 150),
                        (int(rect.w * 0.06), by,
                         int(rect.w * 0.88), rect.h - by + int(rect.h * 0.20)))
    surf.blit(belly, rect.topleft)
    top_sheen(surf, rect, rad, rect.h // 3, peak=60)
    pygame.draw.rect(surf, (40, 26, 14), rect, width=max(1, m(1.4)),
                     border_radius=rad)


def _place_thumb(surf, group, cx, cy, dome_r, hero):
    """Drop the category's REAL preview into the dome, contained (letterboxed)
    so aspect-extreme items sit fully inside the glass. PARCELS previews its
    first real item (the kraft padded mailer) as a peer stall."""
    src, letterbox = _group_thumb(group)
    w, h = src.get_size()
    box = dome_r * (1.62 if letterbox else 1.84)
    if group == "parcels":
        box *= 0.86
        _draw_parcel_padding(surf, cx, cy, dome_r)
    s = box / max(w, h)
    img = pygame.transform.smoothscale(
        src, (max(1, int(w * s)), max(1, int(h * s))))
    img = _punch_contrast(img)
    r = img.get_rect(center=(cx, cy))
    if group == "shades":
        surf.blit(_rim_light(img, color=(255, 224, 150), alpha=210),
                  r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(_rim_light(img), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)


def _hut_label(surf, label, cx, cy, scale):
    """A small carved-timber name board on the roof carrying the category in
    bold gradient gold with a dark keyline — the canonical defined-edge label."""
    f = font(11 * scale)
    tw = _glyph_base(label, f, m(0.6)).get_width()
    pad = int(m(12) * scale)
    bw = tw + pad * 2
    bh = int(m(20) * scale)
    r = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)
    rad = bh // 2
    surf.blit(vgrad(r.w, r.h, rad, (44, 30, 18), (24, 15, 8)), r.topleft)
    rim_d, rim_b = (60, 38, 14), (*GOLD_PALE, 230)
    top_sheen(surf, r, rad, bh // 2, peak=46)
    pygame.draw.rect(surf, (0, 0, 0, 180), r, width=max(1, m(1.4)),
                     border_radius=rad)
    bevel_rim(surf, r, rad, rim_d, rim_b, w=max(1, m(1.2)))
    gradient_text(surf, label, f, r.center, GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(1.0 * scale), keyline=LABEL_KEY, kw=m(1.0), shadow=False,
                  tracking=m(0.6))


def draw_hut(surf, cx, deck_y, scale, group, label):
    """One stilt-market hut, drawn back-to-front so it reads as a solid lit
    object over water: thatched roof carrying a bold gold-keyline name board
    just above the awning -> striped macaw-red/cream awning -> a shaded stall
    interior carrying a glass cabochon with the category's REAL preview
    thumbnail centred in the opening."""
    half_w = int(m(58) * scale)
    body_h = int(m(64) * scale)
    roof_h = int(m(40) * scale)
    eave = int(m(10) * scale)

    body_top = deck_y - body_h
    roof_apex_y = body_top - roof_h

    soft_glow(surf, cx, deck_y, half_w + eave, (0, 0, 0), 110, layers=6)

    body_rect = pygame.Rect(cx - half_w, body_top, half_w * 2, body_h)
    surf.blit(vgrad(body_rect.w, body_rect.h, 0,
                    lerp_color(STALL_DARK, WOOD_MID, 0.25), STALL_DARK),
              body_rect.topleft)
    for px in (body_rect.left, body_rect.right - m(8)):
        pygame.draw.rect(surf, WOOD_LO, (px, body_top, m(8), body_h))
        pygame.draw.line(surf, WOOD_HI, (px + m(1), body_top),
                         (px + m(1), deck_y), max(1, m(1)))

    rl = (cx - half_w - eave, body_top)
    rr = (cx + half_w + eave, body_top)
    apex = (cx, roof_apex_y)
    shs = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(shs, (0, 0, 0, 80),
                        [(rl[0], rl[1] + m(6)), (rr[0], rr[1] + m(6)),
                         (apex[0], apex[1] + m(6))])
    surf.blit(shs, (0, 0))
    courses = 9
    for i in range(courses):
        t0 = i / courses
        t1 = (i + 1) / courses
        y_lo = body_top - (body_top - roof_apex_y) * t0
        y_hi = body_top - (body_top - roof_apex_y) * t1
        xl0 = rl[0] + (apex[0] - rl[0]) * t0
        xr0 = rr[0] + (apex[0] - rr[0]) * t0
        xl1 = rl[0] + (apex[0] - rl[0]) * t1
        xr1 = rr[0] + (apex[0] - rr[0]) * t1
        col = lerp_color(THATCH_LO, THATCH_HI, 1.0 - t0)
        pygame.draw.polygon(surf, col, [(xl0, y_lo), (xr0, y_lo),
                                        (xr1, y_hi), (xl1, y_hi)])
        fringe_n = 18
        for fdx in range(fringe_n):
            ft = fdx / fringe_n
            fx = xl0 + (xr0 - xl0) * ft
            drop = m(3) * scale * (0.5 + 0.5 * math.sin(fdx * 2.3 + i))
            pygame.draw.line(surf, lerp_color(col, THATCH_EDGE, 0.5),
                             (fx, y_lo), (fx, y_lo + drop), max(1, m(0.8)))
    lit = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(lit, (*lerp_color(THATCH_HI, WHITE, 0.25), 90),
                        [rl, apex, (cx, body_top)])
    surf.blit(lit, (0, 0))
    pygame.draw.line(surf, THATCH_EDGE, rl, apex, max(1, m(1.6)))
    pygame.draw.line(surf, THATCH_EDGE, rr, apex, max(1, m(1.6)))
    pygame.draw.line(surf, lerp_color(THATCH_HI, WHITE, 0.4),
                     rl, apex, max(1, m(1.0)))
    pygame.draw.circle(surf, THATCH_EDGE, apex, m(4))
    pygame.draw.circle(surf, THATCH_HI, (apex[0] - m(1), apex[1] - m(1)), m(2))

    awn_y = body_top
    awn_h = int(m(15) * scale)
    stripe_w = max(m(8), int((half_w * 2) / 9))
    awn_surf = pygame.Surface((half_w * 2, awn_h), pygame.SRCALPHA)
    n_str = int((half_w * 2) // stripe_w) + 1
    for s in range(n_str):
        c_top = AWN_RED if s % 2 == 0 else AWN_CREAM
        c_bot = AWN_RED_D if s % 2 == 0 else AWN_CREAM_D
        sx = s * stripe_w
        col = vgrad(stripe_w, awn_h, 0, c_top, c_bot)
        awn_surf.blit(col, (sx, 0))
    mask = pygame.Surface((half_w * 2, awn_h), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    scallop_r = stripe_w // 2
    for s in range(n_str + 1):
        cxs = s * stripe_w
        pygame.draw.circle(mask, (0, 0, 0, 0), (cxs, awn_h), scallop_r)
    awn_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(awn_surf, (cx - half_w, awn_y))
    pygame.draw.line(surf, (0, 0, 0, 120), (cx - half_w, awn_y),
                     (cx + half_w, awn_y), max(1, m(1)))

    deck_rect = pygame.Rect(cx - half_w - m(4), deck_y - m(8),
                            half_w * 2 + m(8), m(10))
    surf.blit(vgrad(deck_rect.w, deck_rect.h, 0, WOOD_HI, WOOD_LO),
              deck_rect.topleft)
    pygame.draw.rect(surf, WOOD_EDGE, deck_rect, width=max(1, m(1)))
    for s in range(1, 8):
        sx = deck_rect.left + deck_rect.w * s // 8
        pygame.draw.line(surf, WOOD_LO, (sx, deck_rect.top),
                         (sx, deck_rect.bottom), max(1, m(0.8)))

    # The three open categories carry the chosen stall-front designs (their own
    # item presentation each, one shared awning-red sign); every other category
    # keeps the stock cabochon + name-board front until it opens.
    from game import stall_fronts
    if group in stall_fronts.ITEM:
        ctx = dict(cx=cx, deck_y=deck_y, body_top=body_top, body_h=body_h,
                   half_w=half_w, eave=eave, roof_apex_y=roof_apex_y,
                   scale=scale, group=group, label=label)
        stall_fronts.draw_item(surf, ctx)
        stall_fronts.draw_sign(surf, ctx)
        return half_w, roof_apex_y

    dome_r = max(m(24), int(m(28) * scale))
    dome_cx = cx
    # centre of the visible opening (below the awning, above the deck lip),
    # not of the raw body — the awning eats the top of the stall interior.
    dome_cy = body_top + int(body_h * 0.55)
    capped_glow(surf, dome_cx, dome_cy, dome_r + m(6), GOLD, 34, layers=8)
    if group == "shades":
        cabochon(surf, dome_cx, dome_cy, dome_r, (96, 104, 134), (44, 50, 78))
    else:
        cabochon(surf, dome_cx, dome_cy, dome_r, CABO_LO, CABO_HI)
    _place_thumb(surf, group, dome_cx, dome_cy, dome_r, False)
    cabochon_glass(surf, dome_cx, dome_cy, dome_r, tint=(240, 224, 196))

    # name board rides the lower roof, its bottom edge resting on the awning
    # line, so the opening below stays free for the preview dome.
    _hut_label(surf, label, cx, body_top - int(m(10) * scale), scale)

    return half_w, roof_apex_y


# =============================================================================
# Pip — a small macaw banking through the upper sky over the village.
# =============================================================================
def draw_pip(surf, px, py):
    """Pip as a tasteful DISTANT FLYER in the upper sky — banking between the sun
    and the village, scaled down, given the wings-up flap frame + a soft warm rim
    catch from the low sun so he separates from the sky without glowing."""
    pip = parrot.get_parrot(0, 5.0)
    pw, ph = pip.get_size()
    target = m(34)
    s = target / max(pw, ph)
    pip = pygame.transform.smoothscale(pip, (int(pw * s), int(ph * s)))
    pr = pip.get_rect(center=(px, py))
    capped_glow(surf, px, py, m(13), (255, 196, 120), 34, layers=6)
    surf.blit(pip, pr.topleft)


# =============================================================================
# Header chrome — STORE wordmark + balance capsule shell + TAP A STALL hint.
# The balance VALUE is NOT baked (it changes as coins bank); it is redrawn live
# in LagoonHub.render. Everything else here goes into the cached base.
# =============================================================================
def _tap_hint(surf, cx, cy):
    """The TAP A STALL call-to-action on its own faint gold-ruled chip: a low-
    alpha recessed pill, a hairline gold rim, bright gradient-gold type flanked
    by short gold rules."""
    f = font(11)
    tw = _glyph_base("TAP  A  STALL", f, m(3)).get_width()
    pad = m(20)
    w = tw + pad * 2
    h = m(26)
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    rad = h // 2
    chip = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(chip, (18, 14, 10, 150), chip.get_rect(), border_radius=rad)
    surf.blit(chip, r.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 150), r, width=max(1, m(1.2)),
                     border_radius=rad)
    pygame.draw.rect(surf, (*GOLD, 150), r.inflate(-m(1.2), -m(1.2)),
                     width=max(1, m(1)), border_radius=rad)
    gold_rule(surf, r.x + m(8), r.x + m(8) + m(16), cy, GOLD_PALE, peak=235,
              thick=m(1.6))
    gold_rule(surf, r.right - m(8) - m(16), r.right - m(8), cy, GOLD_PALE,
              peak=235, thick=m(1.6))
    gradient_text(surf, "TAP  A  STALL", f, (cx, cy), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(0.9), keyline=(40, 22, 12), kw=m(0.9), shadow=False,
                  tracking=m(3))


# The balance capsule geometry must agree between the baked shell and the live
# number, so its metrics are derived from ONE shared helper. Both the bake path
# (shell, no number) and render() (number only) call this so the live digits
# land exactly where the recessed capsule expects them.
def _balance_capsule_layout(cx, y, balance):
    val = f"{balance:,}"
    vf = font(25)
    vw = _glyph_base(val, vf, 0).get_width() + m(2)
    coin_d, gapc, padl, padr = m(28), m(18), m(15), m(22)
    w = padl + coin_d + gapc + vw + padr
    h = m(44)
    cap = pygame.Rect(cx - w // 2, y - h // 2, w, h)
    return val, vf, vw, coin_d, gapc, padl, cap, h


def _balance_capsule_shell(surf, cx, y):
    """The recessed gold capsule WITHOUT its number: the static shell that bakes
    into the cached base. A worst-case-width value sizes it so the capsule is
    wide enough for any plausible balance the live number redraws into."""
    # A 6-digit reference width keeps the baked shell from reflowing under the
    # live number, which is only ever as wide as the running wallet total.
    _, _, _, coin_d, gapc, padl, cap, h = _balance_capsule_layout(cx, y, 999999)
    drop_shadow(surf, cap, h // 2, blur=m(6), alpha=130, dy=m(3))
    surf.blit(vgrad(cap.w, cap.h, h // 2, (58, 42, 22), (22, 15, 8), 255, gamma=1.1),
              cap.topleft)
    top_sheen(surf, cap, h // 2, m(16), peak=50)
    contact_shadow(surf, cap, h // 2, m(5), alpha=110)
    pygame.draw.rect(surf, (0, 0, 0, 200), cap, width=max(1, m(1.8)),
                     border_radius=h // 2)
    bevel_rim(surf, cap, h // 2, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD_PALE, 240), w=max(1, m(1.8)))


def _draw_header_static(surf):
    """The STORE wordmark, the balance capsule SHELL (no number), and the
    TAP-A-STALL CTA on a soft darkening band — everything baked except the live
    balance number, which render() draws on top."""
    band = pygame.Surface((DW, m(126)), pygame.SRCALPHA)
    for y in range(m(126)):
        a = int(150 * (1 - y / m(126)) ** 1.25)
        pygame.draw.line(band, (10, 10, 34, a), (0, y), (DW, y))
    surf.blit(band, (0, 0))
    pygame.draw.rect(surf, (*GOLD, 60), (m(3), m(3), DW - m(6), DH - m(6)),
                     width=max(1, m(1)), border_radius=m(12))
    title_wordmark(surf, "STORE", (DW // 2, m(38)), 42, tracking=m(4))
    _balance_capsule_shell(surf, DW // 2, m(92))


# =============================================================================
# Static base compose — the whole village over the lagoon, built once at SS.
# =============================================================================
# Launch gating: these category stalls render SHUT (bamboo blind) and are made
# non-clickable in StoreScene._handle_hub_tap. Emptying this set restores the
# all-open 7-stall hub — the full open design is kept intact for the future.
CLOSED_GROUPS = frozenset({"animal", "shoes", "hats", "shades"})


def _render_static_device():
    """The full lagoon scene at device resolution: sky, water, planks, huts (back
    -to-front), Pip, header shell, vignette. Returns the SS surface; the caller
    downscales it once to 360x640."""
    surf = pygame.Surface((DW, DH))
    surf.blit(_build_static_sky(), (0, 0))
    horizon = draw_water(surf)

    huts = []
    for group, fx, fy, scale, hero in LAYOUT:
        cx = int(DW * fx)
        deck_y = int(DH * fy)
        huts.append(dict(group=group, label=LABELS[group], cx=cx, deck_y=deck_y,
                         scale=scale, hero=hero))

    order = sorted(range(len(huts)), key=lambda i: huts[i]["deck_y"])

    plank_links = [(0, 3), (1, 5), (2, 4), (3, 5), (4, 5), (5, 6)]
    for a, b in plank_links:
        ha, hb = huts[a], huts[b]
        draw_plank(surf, ha["cx"], ha["deck_y"] - m(2),
                   hb["cx"], hb["deck_y"] - m(2), int(m(16)))

    for i in order:
        h = huts[i]
        half_w = int(m(58) * h["scale"])
        hut_reflection(surf, h["cx"], h["deck_y"], int(half_w * 1.7),
                       h["scale"], horizon)
        post_len = max(m(26), int(m(70) * h["scale"]))
        depth_t = max(0.0, min(1.0, (h["deck_y"] / DH - 0.55) / 0.31))
        ring_scale = 1.0 + 0.45 * depth_t
        draw_stilts(surf, h["cx"], h["deck_y"], half_w, post_len, ring_scale)
        if h["group"] in CLOSED_GROUPS:
            # Launch subset: only COSTUMES/PARROTS/PARCELS open. Shut stalls get a
            # rolled bamboo blind (no awning/dome/label) — anonymous, non-clickable.
            from game.store_hub_closed import draw_hut_closed
            draw_hut_closed(surf, h["cx"], h["deck_y"], h["scale"])
        else:
            draw_hut(surf, h["cx"], h["deck_y"], h["scale"], h["group"], h["label"])

    draw_pip(surf, int(DW * 0.50), int(DH * 0.285))

    _draw_header_static(surf)

    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(DH):
        f = y / DH
        a = 0
        if f < 0.10:
            a += int(70 * (1 - f / 0.10) ** 1.4)
        pygame.draw.line(vig, (8, 6, 24, a), (0, y), (DW, y))
    surf.blit(vig, (0, 0))
    side = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for x in range(DW):
        d = abs(x - DW / 2) / (DW / 2)
        a = int(48 * d ** 2.4)
        pygame.draw.line(side, (8, 6, 24, a), (x, 0), (x, DH))
    surf.blit(side, (0, 0))
    return surf


# The whole lagoon is a STATIC scene, so it is rendered ONCE and cached at
# module scope: a fresh StoreScene is created on every store entry, so per-
# instance building would re-pay the SS-build cost each open (and that build
# also runs on slower pygbag/WASM Python). Module-level caching pays it once
# for the process lifetime.
_BASE = None         # the cached 360x640 static lagoon
_STALL_RECTS = None  # group -> pygame.Rect tap targets in 360x640 device coords


def _stall_rects_360():
    """Generous, tappable rects covering each hut's body/awning footprint in
    final 360x640 coords. Derived from each hut's cx/deck_y/half_w/body span in
    LAYOUT, then divided down from device px. Biased a touch wider + taller than
    the visible body so a thumb-tap on a phone reliably lands inside the stall;
    rows are split at their vertical midpoints so neighbouring tiers don't
    overlap a tap into the wrong stall."""
    rects = {}
    for group, fx, fy, scale, hero in LAYOUT:
        cx = W * fx
        deck_y = H * fy
        half_w = 58 * scale
        body_h = 64 * scale
        roof_h = 40 * scale
        # cover the awning + body + dome down to the deck, plus the roof apex,
        # widened slightly past the eaves for an easy target.
        left = cx - (half_w + 12)
        right = cx + (half_w + 12)
        top = deck_y - (body_h + roof_h)
        bottom = deck_y + 6
        # clamp into the canvas and avoid swallowing the header chrome band.
        top = max(top, 96)
        left = max(0, left)
        right = min(W, right)
        bottom = min(H, bottom)
        rects[group] = pygame.Rect(int(left), int(top),
                                   int(right - left), int(bottom - top))
    return rects


class LagoonHub:
    """The store's lagoon stilt-market landing. Construction triggers (or reuses)
    the module-level cached static base; render() blits that base then draws the
    live coin balance on top. The StoreScene owns chrome/input — this only paints
    the lagoon + baked header + live balance and exposes per-stall tap rects."""

    # Which stalls are shut (baked closed + non-clickable). Exposed here so the
    # StoreScene tap handler can gate on it without importing the module const.
    CLOSED_GROUPS = CLOSED_GROUPS

    def __init__(self) -> None:
        global _BASE, _STALL_RECTS
        if _BASE is None:
            _BASE = downscale(_render_static_device())
            _STALL_RECTS = _stall_rects_360()
        self.stall_rects = _STALL_RECTS

    def render(self, surf: pygame.Surface, balance: int, t: float = 0.0) -> None:
        surf.blit(_BASE, (0, 0))
        self._draw_live_balance(surf, balance)

    def _draw_live_balance(self, surf, balance):
        """The live gold balance — coin glyph + comma-grouped gradient-gold
        number — drawn into the baked capsule shell, centred as a group so any
        balance reads centred in the worst-case-width shell. Drawn directly at
        360x640 (no SS) since it is the one per-frame element; the SS shell
        behind it carries the crisp bezel. The 1x font size (25) matches the SS
        bake (font(25) at SS, downscaled) so the live digits read the same
        height as the baked header would have."""
        cx, y = W // 2, 92
        val = f"{balance:,}"
        vf = _font(25, True)
        vw = vf.render(val, True, WHITE).get_width() + 1
        coin_d, gapc = 28, 18
        # centre the coin + number as one group in the capsule (the shell is
        # baked wide enough for a 6-digit balance, so a shorter number sits
        # centred rather than left-shoved).
        group_w = coin_d + gapc + vw
        x = cx - group_w // 2
        coin_glyph(surf, x + coin_d // 2, y, coin_d // 2)
        x += coin_d + gapc
        _gradient_text_1x(surf, val, vf, (x + vw // 2, y),
                          GOLD_A_TOP, GOLD_A_BOT)


def _gradient_text_1x(surf, txt, font_obj, center, top, bot):
    """Gradient-gold number at the final 360x640 resolution (the live balance is
    the only per-frame glyph, so it skips the SS path): a vertical gold ramp
    masked through the glyph, with a dark keyline + drop shadow so it reads heavy
    against the recessed capsule — matching the baked header's number treatment."""
    base = font_obj.render(txt, True, WHITE)
    w, hh = base.get_size()
    grad = pygame.Surface((w, hh), pygame.SRCALPHA)
    for yy in range(hh):
        pygame.draw.line(grad, lerp_color(top, bot, yy / max(1, hh - 1)),
                         (0, yy), (w, yy))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = base.get_rect(center=center)
    sh = base.copy()
    sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(150)
    surf.blit(sh, (r.x, r.y + 2))
    kl = base.copy()
    kl.fill((96, 56, 12, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        surf.blit(kl, (r.x + dx, r.y + dy))
    surf.blit(grad, r.topleft)

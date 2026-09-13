"""Explore premium redesigns of the hero score medallion (_score_emblem).

Standalone gallery generator — does NOT touch game/hud.py. Renders the
current live emblem plus 5 distinct candidate directions onto one review
sheet so the art-director can judge fine detail AND true 1x legibility.

Each medallion is composited at SS x the target radius then smoothscaled
down (the card-frame trick) so bevels / reeding / guilloche don't pixel
-step at r=56. Palette + fonts are imported straight from game.hud so the
explorations read like the shipped game.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game.draw import lerp_color, NEAR_BLACK, WHITE, UI_CREAM
from game.hud import (
    _score_emblem as live_score_emblem,
    _font,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _GOLD_MUTED,
    _PANEL_DARK, _PANEL_LIGHTER,
    _SCARLET_TOP, _SCARLET_BOT, _RED_OUTLINE,
)

# Supersample factor — composite big, smoothscale down for clean curves.
SS = 4

# Extra gold tones derived from the palette for richer metal ramps. Kept
# local to the explorations so the candidates can model a real bevel
# without leaking new constants into the game.
_GOLD_DARK   = (120,  82,  14)   # deepest shadow of a gold relief
_GOLD_SHADOW = ( 84,  56,  10)   # rim cavity / under-bevel
_ENAMEL_HI   = (255, 248, 230)


# ── small procedural metal helpers ───────────────────────────────────────────

def _radial_metal(size, center, inner_col, outer_col, rr):
    """Domed radial fill — bright centre fading to a darker edge, used for
    the medallion field so it reads as a slightly convex minted face."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = center
    for i in range(rr, 0, -1):
        t = 1.0 - i / rr
        col = lerp_color(inner_col, outer_col, t)
        pygame.draw.circle(surf, col, (cx, cy), i)
    return surf


def _angular_sheen(surf, center, rr, base, hi, lo, lobes=2, phase=-math.pi / 4):
    """Overlay a soft angular brushed-metal sheen so a flat gold ring
    catches light like polished metal — bright toward the light, dim
    opposite. Drawn as thin wedges blended over `surf`."""
    cx, cy = center
    steps = 360
    for k in range(steps):
        a = k / steps * math.tau
        # Two specular lobes (top-left + bottom-right) like a coin under
        # a single key light.
        s = 0.5 + 0.5 * math.cos((a - phase) * lobes)
        col = lerp_color(lo, hi, s)
        x2 = cx + math.cos(a) * rr
        y2 = cy + math.sin(a) * rr
        pygame.draw.line(surf, col, (cx, cy), (x2, y2), 3)


def _beveled_ring(surf, center, r_out, r_in, light=_GOLD_PALE,
                  mid=_GOLD_BRIGHT, shadow=_GOLD_DARK):
    """A raised metal ring with a directional bevel: bright on the
    top-left arc, dark on the bottom-right — matching the card-frame
    bevel language (light TL / dark BR)."""
    cx, cy = center
    band = max(1, r_out - r_in)
    for i in range(r_out, r_in - 1, -1):
        # cross-section ramp: outer & inner edges darker, crest bright
        t = (i - r_in) / max(1, band)
        crest = 1.0 - abs(t - 0.5) * 2.0  # 0..1..0 across the band
        ring_col = lerp_color(shadow, light, 0.35 + 0.65 * crest)
        # Per-angle directional light over the crest.
        steps = 240
        for k in range(steps):
            a = k / steps * math.tau
            lit = 0.5 + 0.5 * math.cos(a + math.pi * 0.75)  # bright TL
            col = lerp_color(shadow, ring_col, 0.45 + 0.55 * lit)
            x = cx + math.cos(a) * i
            y = cy + math.sin(a) * i
            surf.set_at((int(x), int(y)), col)


def _reeded_edge(surf, center, r_out, r_in, n=120,
                 light=_GOLD_PALE, dark=_GOLD_SHADOW):
    """Milled / reeded coin edge — alternating bright/dark radial teeth."""
    cx, cy = center
    for k in range(n):
        a = k / n * math.tau
        col = light if k % 2 == 0 else dark
        x1 = cx + math.cos(a) * r_in
        y1 = cy + math.sin(a) * r_in
        x2 = cx + math.cos(a) * r_out
        y2 = cy + math.sin(a) * r_out
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), 3)


def _gold_value(surf, center, value, size, relief=True):
    """The hero numeral with a chiselled bas-relief look — dark engraved
    underside + bright top facet so it reads as struck into the metal."""
    f = _font(size, True)
    s_val = str(value)
    # Engraved shadow (down-right) + cut highlight (up-left) + face.
    base = f.render(s_val, True, _GOLD_BRIGHT)
    rect = base.get_rect(center=center)
    if relief:
        dk = f.render(s_val, True, _GOLD_SHADOW)
        hi = f.render(s_val, True, _GOLD_PALE)
        off = max(1, size // 22)
        surf.blit(dk, (rect.x + off, rect.y + off))
        surf.blit(hi, (rect.x - off, rect.y - off))
    surf.blit(base, rect.topleft)


def _label_text(surf, center, label, size, col=_GOLD_PALE, alpha=235):
    f = _font(size, True)
    img = f.render(label, True, col)
    img.set_alpha(alpha)
    surf.blit(img, img.get_rect(center=center))


def _make(r):
    """Allocate an oversize SRCALPHA canvas to draw a medallion of target
    radius r. Returns (surf, R, cx, cy) where R = r*SS."""
    R = r * SS
    pad = int(R * 0.10)
    size = R * 2 + pad * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    return surf, R, size // 2, size // 2


def _finish(surf, r):
    """Smoothscale the supersampled medallion down to its true diameter."""
    target = int(r * 2 + r * 0.10 * 2 / SS * SS)
    d = surf.get_width() // SS
    return pygame.transform.smoothscale(surf, (d, d))


# ── Candidate 1: Minted Sovereign (raised beveled rim + reeded edge + dome) ──

def cand_minted(r, value, label):
    surf, R, cx, cy = _make(r)
    # Reeded milled edge under the rim.
    _reeded_edge(surf, (cx, cy), R, int(R * 0.93), n=150)
    # Raised beveled outer rim (light TL / dark BR).
    _beveled_ring(surf, (cx, cy), int(R * 0.95), int(R * 0.80))
    # Domed interior field — warm gold, slightly convex, offset light.
    field_r = int(R * 0.80)
    dome = _radial_metal(R * 2, (R - int(R * 0.18), R - int(R * 0.18)),
                         (255, 236, 178), (150, 104, 26), field_r)
    surf.blit(dome, (cx - R, cy - R))
    # Subtle inner step ring (the recessed field lip).
    pygame.draw.circle(surf, _GOLD_SHADOW, (cx, cy), field_r, max(2, R // 90))
    pygame.draw.circle(surf, _GOLD_PALE, (cx, cy),
                       field_r - max(2, R // 90), max(1, R // 140))
    out = _finish(surf, r)
    # Bas-relief text struck on the warm dome — dark engraving reads well.
    cx2 = out.get_width() // 2
    _label_text(out, (cx2, cx2 - int(r * 0.44)), label, max(8, int(r * 0.22)),
                col=_GOLD_DARK, alpha=255)
    _value_struck(out, (cx2, cx2 + int(r * 0.12)), value, max(16, int(r * 0.60)))
    return out


def _value_struck(surf, center, value, size):
    """Numeral struck INTO bright metal — engraved dark with a thin lower
    highlight catching light at the cut's bottom lip."""
    f = _font(size, True)
    s_val = str(value)
    rect = f.render(s_val, True, _GOLD_DARK).get_rect(center=center)
    hi = f.render(s_val, True, (255, 245, 215))
    dk = f.render(s_val, True, (70, 44, 8))
    off = max(1, size // 20)
    surf.blit(hi, (rect.x, rect.y + off))      # light bottom lip of the cut
    surf.blit(dk, rect.topleft)                # engraved face


# ── Candidate 2: Guilloché Dial (rosette engraving behind the value) ─────────

def cand_guilloche(r, value, label):
    surf, R, cx, cy = _make(r)
    # Navy field.
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), R)
    field_r = int(R * 0.84)
    # Rosette guilloche — overlapping epicycloid loops in fine gold lines.
    petals = 18
    loop_r = field_r * 0.50
    off_r = field_r * 0.34
    lw = max(1, R // 150)
    for p in range(petals):
        base_a = p / petals * math.tau
        ccx = cx + math.cos(base_a) * off_r
        ccy = cy + math.sin(base_a) * off_r
        pts = []
        for k in range(49):
            a = k / 48 * math.tau
            x = ccx + math.cos(a) * loop_r
            y = ccy + math.sin(a) * loop_r
            d = math.hypot(x - cx, y - cy)
            if d <= field_r:
                pts.append((x, y))
        if len(pts) > 1:
            shade = lerp_color(_GOLD_DEEP, _GOLD_PALE,
                               0.3 + 0.4 * (p % 2))
            pygame.draw.lines(surf, shade, False, pts, lw)
    # Concentric fine rings over the rosette for the watch-dial feel.
    for k in range(6):
        rr = int(field_r * (0.30 + k * 0.10))
        a = 70 if k % 2 else 110
        ring = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*_GOLD_PALE, a), (R, R), rr, lw)
        surf.blit(ring, (cx - R, cy - R))
    # Polished multi-ply rim: gold / scarlet pinstripe / gold bevel.
    _beveled_ring(surf, (cx, cy), R, int(R * 0.90))
    pygame.draw.circle(surf, _SCARLET_TOP, (cx, cy), int(R * 0.875),
                       max(2, R // 80))
    pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), int(R * 0.84),
                       max(1, R // 130))
    # Vignette so the centre value sits clear of the engraving.
    vig = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    for i in range(int(field_r * 0.62), 0, -1):
        a = int(150 * (1 - i / (field_r * 0.62)))
        pygame.draw.circle(vig, (*_PANEL_DARK, a), (R, R), i)
    surf.blit(vig, (cx - R, cy - R))
    out = _finish(surf, r)
    cx2 = out.get_width() // 2
    _label_text(out, (cx2, cx2 - int(r * 0.50)), label, max(8, int(r * 0.21)))
    _gold_value(out, (cx2, cx2 + int(r * 0.10)), value, max(16, int(r * 0.58)))
    return out


# ── Candidate 3: Laurel Crest (two gold laurel branches framing value) ───────

def _laurel_branch(surf, base, tip, leaves, side, col_hi, col_lo, scale):
    """Draw one sweeping laurel branch from `base` toward `tip` with leaf
    pairs. `side` = +1 / -1 mirrors leaf direction."""
    bx, by = base
    tx, ty = tip
    # Curved stem via a quadratic-ish arc using midpoint bow.
    mx = (bx + tx) / 2 + side * scale * 6
    my = (by + ty) / 2
    stem = []
    for k in range(31):
        t = k / 30
        x = (1 - t) ** 2 * bx + 2 * (1 - t) * t * mx + t * t * tx
        y = (1 - t) ** 2 * by + 2 * (1 - t) * t * my + t * t * ty
        stem.append((x, y))
    pygame.draw.lines(surf, col_lo, False, stem, max(2, int(scale * 2)))
    # Leaves along the stem.
    for i in range(1, leaves + 1):
        t = i / (leaves + 1)
        idx = int(t * (len(stem) - 1))
        sx, sy = stem[idx]
        # leaf direction roughly tangent rotated outward
        nx, ny = stem[min(idx + 1, len(stem) - 1)]
        dx, dy = nx - sx, ny - sy
        dl = math.hypot(dx, dy) or 1
        dx, dy = dx / dl, dy / dl
        # outward normal
        ox, oy = -dy * side, dx * side
        leaf_len = scale * (10 + 6 * math.sin(t * math.pi))
        lw_ = scale * 4
        ex = sx + (dx * 0.4 + ox) * leaf_len
        ey = sy + (dy * 0.4 + oy) * leaf_len
        # leaf as a slim diamond
        midx, midy = (sx + ex) / 2, (sy + ey) / 2
        perpx, perpy = -(ey - sy), (ex - sx)
        pl = math.hypot(perpx, perpy) or 1
        perpx, perpy = perpx / pl * lw_, perpy / pl * lw_
        leaf = [(sx, sy), (midx + perpx, midy + perpy),
                (ex, ey), (midx - perpx, midy - perpy)]
        pygame.draw.polygon(surf, col_hi, leaf)
        pygame.draw.polygon(surf, col_lo, leaf, max(1, int(scale)))


def cand_laurel(r, value, label):
    surf, R, cx, cy = _make(r)
    # Domed gold field with a warm radial glow.
    field = _radial_metal(R * 2, (R, R - int(R * 0.10)),
                          (44, 30, 92), (10, 6, 34), int(R * 0.93))
    surf.blit(field, (cx - R, cy - R))
    # Clean double rim.
    _beveled_ring(surf, (cx, cy), R, int(R * 0.91))
    pygame.draw.circle(surf, _SCARLET_TOP, (cx, cy), int(R * 0.885),
                       max(1, R // 110))
    # Two laurel branches sweeping up the sides.
    sc = R / 56.0
    base_y = cy + int(R * 0.66)
    tip_y = cy - int(R * 0.40)
    span = int(R * 0.60)
    _laurel_branch(surf, (cx - span, base_y), (cx - int(R * 0.18), tip_y),
                   6, -1, _GOLD_BRIGHT, _GOLD_DEEP, sc)
    _laurel_branch(surf, (cx + span, base_y), (cx + int(R * 0.18), tip_y),
                   6, +1, _GOLD_BRIGHT, _GOLD_DEEP, sc)
    # Small scarlet cabochon where branches meet at the bottom.
    gem_r = int(R * 0.10)
    pygame.draw.circle(surf, _SCARLET_BOT, (cx, base_y), gem_r)
    pygame.draw.circle(surf, _SCARLET_TOP, (cx, base_y), gem_r, 0)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, base_y), gem_r, max(1, R // 90))
    pygame.draw.circle(surf, _ENAMEL_HI, (cx - gem_r // 3, base_y - gem_r // 3),
                       max(1, gem_r // 3))
    out = _finish(surf, r)
    cx2 = out.get_width() // 2
    _label_text(out, (cx2, cx2 - int(r * 0.46)), label, max(8, int(r * 0.21)))
    _gold_value(out, (cx2, cx2 + int(r * 0.06)), value, max(16, int(r * 0.62)))
    return out


# ── Candidate 4: Enamel Badge (deep-scarlet enamel band carries label) ───────

def cand_enamel(r, value, label):
    surf, R, cx, cy = _make(r)
    # Outer polished gold ring (beveled).
    _beveled_ring(surf, (cx, cy), R, int(R * 0.86))
    # Deep scarlet enamel band (glossy: top-lit gradient + thin highlight).
    band_out = int(R * 0.86)
    band_in = int(R * 0.66)
    for i in range(band_out, band_in - 1, -1):
        t = (i - band_in) / max(1, band_out - band_in)
        # vertical-ish gloss: brighter near the top of the band
        col = lerp_color(_SCARLET_BOT, _SCARLET_TOP, t)
        pygame.draw.circle(surf, col, (cx, cy), i, 1)
    # Specular sweep on the upper-left of the enamel band.
    gloss = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    mid = (band_out + band_in) // 2
    for k in range(360):
        a = k / 360 * math.tau
        s = max(0.0, math.cos(a + math.pi * 0.7))
        if s > 0:
            col = (*_ENAMEL_HI, int(120 * s ** 2))
            x = R + math.cos(a) * mid
            y = R + math.sin(a) * mid
            pygame.draw.circle(gloss, col, (int(x), int(y)),
                               max(2, (band_out - band_in) // 2 - 2))
    surf.blit(gloss, (cx - R, cy - R))
    # Gold hairlines bordering the enamel band.
    pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), band_out, max(1, R // 110))
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), band_in, max(2, R // 90))
    pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), band_in - max(2, R // 90),
                       max(1, R // 140))
    # Inner navy field (slightly domed) for the value.
    field = _radial_metal(R * 2, (R, R - int(R * 0.12)),
                          (40, 28, 86), (8, 5, 30), band_in - max(2, R // 90))
    surf.blit(field, (cx - R, cy - R))
    # Curved label text following the top of the enamel band.
    _arc_text(surf, (cx, cy), label, (band_out + band_in) // 2,
              max(9, int(R * 0.17)), _GOLD_PALE, top=True)
    # Two small gold stars flanking the bottom of the band.
    for sgn in (-1, 1):
        sx = cx + sgn * (band_out + band_in) // 2 * math.sin(math.radians(0))
    _star(surf, (cx, cy + (band_out + band_in) // 2), int(R * 0.07), _GOLD_PALE)
    out = _finish(surf, r)
    cx2 = out.get_width() // 2
    _gold_value(out, (cx2, cx2 + int(r * 0.04)), value, max(16, int(r * 0.56)))
    return out


def _star(surf, center, rr, col):
    cx, cy = center
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rad = rr if k % 2 == 0 else rr * 0.42
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    pygame.draw.polygon(surf, col, pts)


def _arc_text(surf, center, text, radius, size, col, top=True):
    """Render `text` along a circular arc (banner curve), centred at the
    top (or bottom) of the ring."""
    cx, cy = center
    f = _font(size, True)
    glyphs = [f.render(ch, True, col) for ch in text]
    widths = [g.get_width() for g in glyphs]
    total = sum(widths)
    # angular span proportional to arc length
    span = total / radius
    start = -math.pi / 2 - span / 2 if top else math.pi / 2 + span / 2
    acc = 0.0
    for g, w in zip(glyphs, widths):
        frac = (acc + w / 2) / radius
        a = start + frac if top else start - frac
        gx = cx + math.cos(a) * radius
        gy = cy + math.sin(a) * radius
        rot = math.degrees(-(a + math.pi / 2)) if top else math.degrees(-(a - math.pi / 2))
        rg = pygame.transform.rotate(g, rot)
        surf.blit(rg, rg.get_rect(center=(gx, gy)))
        acc += w


# ── Candidate 5: Sunburst Proof (radial brushed-metal striations) ────────────

def cand_sunburst(r, value, label):
    surf, R, cx, cy = _make(r)
    field_r = int(R * 0.86)
    # Sunburst: alternating fine radial wedges (light/shadow) from centre.
    rays = 144
    for k in range(rays):
        a0 = k / rays * math.tau
        a1 = (k + 1) / rays * math.tau
        # angular specular: bright toward top-left key light
        lit = 0.5 + 0.5 * math.cos(a0 + math.pi * 0.75)
        base = lerp_color((26, 18, 60), (250, 224, 150), lit)
        col = lerp_color(base, _GOLD_DEEP, 0.25) if k % 2 else base
        pts = [(cx, cy),
               (cx + math.cos(a0) * field_r, cy + math.sin(a0) * field_r),
               (cx + math.cos(a1) * field_r, cy + math.sin(a1) * field_r)]
        pygame.draw.polygon(surf, col, pts)
    # Central polished hub so the value sits on a clean disc.
    hub_r = int(field_r * 0.52)
    hub = _radial_metal(R * 2, (R - int(R * 0.10), R - int(R * 0.10)),
                        (255, 238, 184), (148, 102, 24), hub_r)
    surf.blit(hub, (cx - R, cy - R))
    pygame.draw.circle(surf, _GOLD_SHADOW, (cx, cy), hub_r, max(2, R // 90))
    pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), hub_r - max(2, R // 90),
                       max(1, R // 150))
    # Multi-ply polished rim w/ scarlet pinstripe.
    _beveled_ring(surf, (cx, cy), R, int(R * 0.90))
    pygame.draw.circle(surf, _SCARLET_TOP, (cx, cy), int(R * 0.875),
                       max(2, R // 80))
    pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), int(R * 0.86),
                       max(1, R // 140))
    out = _finish(surf, r)
    cx2 = out.get_width() // 2
    # Label rides on the gold sunburst above the hub.
    _label_text(out, (cx2, cx2 - int(r * 0.40)), label, max(8, int(r * 0.20)),
                col=_GOLD_DARK, alpha=255)
    _value_struck(out, (cx2, cx2 + int(r * 0.12)), value, max(16, int(r * 0.56)))
    return out


CANDIDATES = [
    ("Minted Sovereign", cand_minted,
     "Raised beveled rim + reeded edge, domed gold field, struck numeral"),
    ("Guilloche Dial", cand_guilloche,
     "Rosette guilloche engraving on navy + multi-ply rim w/ scarlet pinstripe"),
    ("Laurel Crest", cand_laurel,
     "Two gold laurel branches framing the value + scarlet cabochon"),
    ("Enamel Badge", cand_enamel,
     "Deep-scarlet enamel band carrying curved label, glossy jewel-badge"),
    ("Sunburst Proof", cand_sunburst,
     "Radiating brushed-metal striations + polished hub, proof-coin look"),
]


# ── backdrop matching the dimmed pause overlay ───────────────────────────────

def _backdrop(w, h):
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        col = lerp_color((18, 12, 46), (8, 5, 26), t)
        pygame.draw.line(surf, col, (0, y), (w, y))
    return surf


def _panel(w, h, x, y):
    """A dimmed navy field tile to drop a medallion onto, like the overlay."""
    s = pygame.Surface((w, h))
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = lerp_color((22, 15, 54), (11, 7, 34), t)
        pygame.draw.line(s, col, (0, yy), (w, yy))
    return s


# ── build the review sheet ───────────────────────────────────────────────────

def build():
    cols = 3
    rows = 2
    tile_w = 430
    tile_h = 470
    margin = 28
    header_h = 96
    sheet_w = cols * tile_w + (cols + 1) * margin
    sheet_h = header_h + rows * tile_h + (rows + 1) * margin

    sheet = _backdrop(sheet_w, sheet_h)

    title = _font(46, True).render("SCORE MEDALLION — ROUND 1", True, _GOLD_BRIGHT)
    sheet.blit(title, (margin, 24))
    sub = _font(20, True).render(
        "current reference + 5 premium directions  |  detail @r=72  +  native strip r=56 & r=72  |  1-digit & 3-digit",
        True, UI_CREAM)
    sub.set_alpha(210)
    sheet.blit(sub, (margin, 70))

    # First tile = current live emblem; then the 5 candidates.
    tiles = [("CURRENT (before)", None, "live _score_emblem — flat navy ring, laurel ticks")]
    tiles += CANDIDATES

    for idx, (name, fn, desc) in enumerate(tiles):
        col = idx % cols
        row = idx // cols
        tx = margin + col * (tile_w + margin)
        ty = header_h + margin + row * (tile_h + margin)

        tile = _panel(tile_w, tile_h, tx, ty)

        # Tile name plate.
        nm = _font(26, True).render(name, True, _GOLD_BRIGHT)
        tile.blit(nm, (16, 12))
        dl = _font(13, True).render(desc, True, UI_CREAM)
        dl.set_alpha(195)
        tile.blit(dl, (16, 46))

        # --- big detail render at r=72, value "47" ---
        big_r = 72
        if fn is None:
            big = pygame.Surface((big_r * 2 + 12, big_r * 2 + 12), pygame.SRCALPHA)
            live_score_emblem(big, big_r + 6, big_r + 6, big_r, "S C O R E", "47")
        else:
            big = fn(big_r, "47", "S C O R E")
        # detail panel background circle so it's not floating on a seam
        bx = tile_w // 2
        by = 70 + big.get_height() // 2
        tile.blit(big, (bx - big.get_width() // 2, by - big.get_height() // 2))

        # --- native-size strip: r=56 "47", r=72 "47", r=72 "128" ---
        strip_y = by + big.get_height() // 2 + 22
        lbl = _font(14, True).render("NATIVE 1x:", True, UI_CREAM)
        lbl.set_alpha(200)
        tile.blit(lbl, (16, strip_y - 4))

        sy = strip_y + 22
        specs = [(56, "47"), (72, "47"), (72, "128")]
        # lay the three out across the tile width
        gap = 8
        total = sum(s[0] * 2 for s in specs) + gap * (len(specs) - 1)
        sx = (tile_w - total) // 2
        for rr, val in specs:
            if fn is None:
                em = pygame.Surface((rr * 2 + 12, rr * 2 + 12), pygame.SRCALPHA)
                live_score_emblem(em, rr + 6, rr + 6, rr, "S C O R E", val)
            else:
                em = fn(rr, val, "S C O R E")
            tile.blit(em, (sx, sy + (144 - em.get_height()) // 2))
            # tiny caption under each
            cap = _font(11, True).render(f"r={rr} \"{val}\"", True, UI_CREAM)
            cap.set_alpha(180)
            tile.blit(cap, cap.get_rect(center=(sx + rr, sy + 150)))
            sx += rr * 2 + gap

        sheet.blit(tile, (tx, ty))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "score_emblem_redesign")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.abspath(os.path.join(out_dir, "round_1.png"))
    pygame.image.save(sheet, out_path)
    print(out_path)


if __name__ == "__main__":
    build()

"""Round 2 of the hero score medallion redesign — refine the ENAMEL BADGE
lead and graft the directional ring bevel from MINTED SOVEREIGN.

Standalone gallery generator — does NOT touch game/hud.py. The retired
round-1 directions (Guilloche, Sunburst, Laurel, full Minted) are NOT
re-explored here. This sheet shows the refined Enamel lead plus two minor
proportion variants, each beside the CURRENT live emblem, so the
art-director can lock ring px / band width / label offset.

Every medallion is composited at SS x its target radius then smoothscaled
down (the card-frame trick) so the bevel + enamel band stay clean and
anti-aliased at the small pause-screen size. Palette + fonts are imported
straight from game.hud so the explorations read like the shipped game.
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
# Matches the card-frame convention so the bevel doesn't pixel-step at r=56.
SS = 4

# Extra gold tones derived from the palette for a believable directional
# bevel ramp (light top-left → dark bottom-right). Kept local to the
# explorations so the candidate can model real metal without leaking new
# constants into the game.
_GOLD_DARK   = (120,  82,  14)   # deepest shadow of a gold relief
_GOLD_SHADOW = ( 84,  56,  10)   # rim cavity / under-bevel
_ENAMEL_HI   = (255, 248, 230)   # gloss highlight on the enamel band

# Navy field tones — a slightly domed dark navy so the value reads on a
# lit interior, not a flat hole. Brighter centre, deep edge.
_FIELD_HI    = (40, 28, 86)
_FIELD_LO    = (8,  5, 30)


# ── supersampled canvas helpers (the card-frame trick) ───────────────────────

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
    d = surf.get_width() // SS
    return pygame.transform.smoothscale(surf, (d, d))


# ── directional beveled ring (grafted from MINTED SOVEREIGN) ─────────────────

def _beveled_ring(surf, center, r_out, r_in,
                  light=_GOLD_PALE, mid=_GOLD_BRIGHT, shadow=_GOLD_DARK):
    """A raised metal ring with a directional convex bevel: bright on the
    top-left arc, dark on the bottom-right. The cross-section rolls
    dark→bright→dark across the band so it reads as a rounded roll of gold,
    not a flat stripe. Built as gap-free concentric arcs (one filled annulus
    sub-band per radius, gradient-tinted by both the convex cross-section and
    the angular key light). Center stays untouched — this is a RING, never a
    dome — and there is NO reeded edge, which frays at the small size. Clean
    anti-aliasing comes from the SS→smoothscale step."""
    cx, cy = center
    band = max(1, r_out - r_in)
    # Light direction points to the top-left in screen coords (y grows down).
    light_dir = math.atan2(-0.8, -1.0)
    # Per-angle directional sweep is painted as fine radial spokes so the
    # annulus fills completely with no set_at gaps. Two passes: a base
    # convex ramp by radius, then the angular key-light spokes on top.
    # 1) base convex cross-section (purely radial).
    for i in range(r_out, r_in - 1, -1):
        t = (i - r_in) / band
        crest = 1.0 - abs(t - 0.5) * 2.0
        col = lerp_color(shadow, mid, 0.30 + 0.70 * crest)
        pygame.draw.circle(surf, col, (cx, cy), i, 2)
    # 2) angular key light, modulated by the convex crest so highlights ride
    #    the roll. Drawn as radial spokes spanning the band.
    spokes = max(360, int(r_out * 8))
    for k in range(spokes):
        a = k / spokes * math.tau
        ca, sa = math.cos(a), math.sin(a)
        lit = 0.5 + 0.5 * math.cos(a - light_dir)
        # outer edge dark, crest bright, inner edge mid — sampled at 3 stops.
        for frac, crest in ((0.06, 0.25), (0.5, 1.0), (0.94, 0.45)):
            i = r_in + band * frac
            base = lerp_color(shadow, mid, 0.30 + 0.70 * crest)
            col = lerp_color(base, light, (0.20 + 0.80 * lit ** 1.4) * crest)
            seg = max(1, int(band * 0.22))
            x1 = cx + ca * (i - seg)
            y1 = cy + sa * (i - seg)
            x2 = cx + ca * (i + seg)
            y2 = cy + sa * (i + seg)
            pygame.draw.line(surf, col, (x1, y1), (x2, y2), 2)
    # Crisp seams at the outer + inner edges so the roll reads contained.
    pygame.draw.circle(surf, _GOLD_SHADOW, (cx, cy), r_out, max(1, SS // 2))
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), r_in, max(1, SS // 2))


# ── scarlet enamel band ──────────────────────────────────────────────────────

def _enamel_band(surf, center, R, band_out, band_in):
    """Glossy deep-scarlet enamel band between the gold ring and the navy
    field. Vertical-ish gradient (lighter toward the top) using the game's
    own scarlet, with ONE soft gloss arc on the upper-left matching the
    ring's light direction — no busy reflections."""
    cx, cy = center
    band = max(1, band_out - band_in)
    # Solid scarlet base first so no navy/red gaps show through the spokes.
    pygame.draw.circle(surf, _SCARLET_BOT, (cx, cy), band_out)
    # Vertical gloss gradient painted as gap-free radial spokes: the top of
    # the band catches more light (brighter scarlet) than the bottom.
    spokes = max(360, int(band_out * 8))
    for k in range(spokes):
        a = k / spokes * math.tau
        vy = math.sin(a)              # -1 at top, +1 at bottom
        t = 0.5 - 0.5 * vy            # 1 at top, 0 at bottom
        col = lerp_color(_SCARLET_BOT, _SCARLET_TOP, 0.25 + 0.75 * t)
        ca, sa = math.cos(a), math.sin(a)
        x1 = cx + ca * band_in
        y1 = cy + sa * band_in
        x2 = cx + ca * band_out
        y2 = cy + sa * band_out
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), 2)
    # Single soft gloss sweep, upper-left, matching the ring key light.
    gloss = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    mid = (band_out + band_in) // 2
    thick = max(2, band // 2 - SS)
    for k in range(360):
        a = k / 360 * math.tau
        s = max(0.0, math.cos(a + math.pi * 0.72))
        if s > 0:
            col = (*_ENAMEL_HI, int(110 * s ** 2.2))
            x = R + math.cos(a) * mid
            y = R + math.sin(a) * mid
            pygame.draw.circle(gloss, col, (int(x), int(y)), thick)
    surf.blit(gloss, (cx - R, cy - R))
    # Gold hairlines bordering the enamel band (crisp jeweller's bezel).
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), band_in, max(1, SS))


# ── navy field + lit dome ────────────────────────────────────────────────────

def _navy_field(surf, center, R, field_r):
    """Slightly domed dark-navy interior so the gold value sits on a lit
    surface (key light top-left, like the ring) rather than a flat black
    hole. The disc itself is perfectly centered; only the highlight is
    offset up-left so the dome agrees with the medallion's key light."""
    cx, cy = center
    # Base navy disc — centered, deep edge → mid navy by radius.
    for i in range(field_r, 0, -1):
        t = 1.0 - i / field_r
        col = lerp_color(_FIELD_HI, _FIELD_LO, t)
        pygame.draw.circle(surf, col, (cx, cy), i)
    # Soft directional sheen: a faint up-left highlight blob on the dome.
    sheen = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    lx = R - int(R * 0.18)
    ly = R - int(R * 0.22)
    blob_r = int(field_r * 0.72)
    for i in range(blob_r, 0, -1):
        a = int(26 * (1 - i / blob_r))
        pygame.draw.circle(sheen, (110, 92, 180, a), (lx, ly), i)
    surf.blit(sheen, (cx - R, cy - R))
    # Thin inner gold lip catches the field edge.
    pygame.draw.circle(surf, _GOLD_PALE, (cx, cy), field_r, max(1, SS // 2))


# ── curved gold label sitting INSIDE the navy field ──────────────────────────

def _arc_label(surf, center, text, radius, size, top=True):
    """Render `text` along a circular arc, gold caps with a 1px navy halo
    behind each glyph so it holds against the navy field at r=56. Gold-on
    -navy only — never dark-on-gold."""
    cx, cy = center
    f = _font(size, True)
    glyphs = [f.render(ch, True, _GOLD_PALE) for ch in text]
    halos = [f.render(ch, True, _PANEL_DARK) for ch in text]
    widths = [g.get_width() for g in glyphs]
    total = sum(widths)
    span = total / radius
    start = -math.pi / 2 - span / 2 if top else math.pi / 2 + span / 2
    acc = 0.0
    halo_off = max(1, SS)  # 1px at native scale after the SS smoothscale
    for g, hl, w in zip(glyphs, halos, widths):
        frac = (acc + w / 2) / radius
        a = start + frac if top else start - frac
        gx = cx + math.cos(a) * radius
        gy = cy + math.sin(a) * radius
        rot = (math.degrees(-(a + math.pi / 2)) if top
               else math.degrees(-(a - math.pi / 2)))
        rg = pygame.transform.rotate(g, rot)
        rh = pygame.transform.rotate(hl, rot)
        rect = rg.get_rect(center=(gx, gy))
        # 4-way navy halo for readability against the field.
        for ox, oy in ((-halo_off, 0), (halo_off, 0),
                       (0, -halo_off), (0, halo_off)):
            surf.blit(rh, (rect.x + ox, rect.y + oy))
        surf.blit(rg, rect.topleft)
        acc += w


# ── crisp centered brand star at 6 o'clock ───────────────────────────────────

def _brand_star(surf, center, rr):
    """A deliberate, crisp 5-point gold star — a brand mark, not a speck.
    Filled gold with a thin deep-gold edge so it survives the downscale."""
    cx, cy = center
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rad = rr if k % 2 == 0 else rr * 0.44
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    pygame.draw.polygon(surf, _GOLD_PALE, pts)
    pygame.draw.polygon(surf, _GOLD_DEEP, pts, max(1, SS // 2))


# ── the hero numeral: gold-on-navy, brightest element ────────────────────────

def _gold_value(surf, center, value, size, max_w=None):
    """Bright gold numeral with a subtle bottom-right navy shadow + top-left
    pale facet so it reads as the brightest, raised element on the field.
    For 3-digit values, tighten inter-digit tracking instead of shrinking
    the glyphs so '128' keeps stroke clearance from the inner ring."""
    cx, cy = center
    s_val = str(value)
    f = _font(size, True)
    if len(s_val) >= 3:
        # Tighten tracking: render glyph by glyph with reduced advance so a
        # 3-digit value stays the same cap height yet fits inside the field.
        glyphs = [(ch, f.render(ch, True, _GOLD_BRIGHT),
                   f.render(ch, True, _PANEL_DARK),
                   f.render(ch, True, _GOLD_PALE)) for ch in s_val]
        track = -int(size * 0.10)  # squeeze digits together
        adv = [g[1].get_width() + track for g in glyphs]
        total = sum(g[1].get_width() for g in glyphs) + track * (len(glyphs) - 1)
        x = cx - total // 2
        off = max(1, size // 20)
        for (ch, base, dk, hi), a in zip(glyphs, adv):
            r = base.get_rect()
            r.x = x
            r.centery = cy
            surf.blit(dk, (r.x + off, r.y + off))
            surf.blit(hi, (r.x - off, r.y - off))
            surf.blit(base, r.topleft)
            x += a
    else:
        base = f.render(s_val, True, _GOLD_BRIGHT)
        dk = f.render(s_val, True, _PANEL_DARK)
        hi = f.render(s_val, True, _GOLD_PALE)
        rect = base.get_rect(center=center)
        off = max(1, size // 20)
        surf.blit(dk, (rect.x + off, rect.y + off))
        surf.blit(hi, (rect.x - off, rect.y - off))
        surf.blit(base, rect.topleft)


# ── the refined ENAMEL BADGE (parametric, for proportion variants) ───────────

def enamel(r, value, label,
           ring_pct=0.14, band_pct=0.12,
           label_off=0.07, value_off=0.05, star=True):
    """Refined Enamel Badge medallion.

    ring_pct   : gold ring width as a fraction of r (outer roll)
    band_pct   : scarlet enamel band width as a fraction of r
    label_off  : how far DOWN from the top of the field the curved label
                 sits, as a fraction of r (keeps it off the inner ring)
    value_off  : value baseline nudge below the geometric center (fraction r)
    star       : draw the crisp 6 o'clock brand star
    """
    surf, R, cx, cy = _make(r)

    r_out = R                                   # outer edge of the gold ring
    band_out = int(R * (1.0 - ring_pct))        # ring inner / band outer
    band_in = int(band_out - R * band_pct)      # band inner / field outer
    field_r = band_in

    # Painter's order, outer→inner: the scarlet band lays a full disc, the
    # navy field then masks its center, and the gold ring caps the outer
    # edge — so each layer cleanly defines the next boundary with no bleed.
    # 1) scarlet enamel band (full scarlet disc to band_out + top-lit gloss).
    _enamel_band(surf, (cx, cy), R, band_out, band_in)
    # 2) navy field masks the band's center, leaving the scarlet as a band.
    _navy_field(surf, (cx, cy), R, field_r)
    # 3) directional beveled gold ring caps the outer edge (light TL→dark BR).
    _beveled_ring(surf, (cx, cy), r_out, band_out)

    out = _finish(surf, r)
    cx2 = out.get_width() // 2

    # Curved label sits INSIDE the navy field, pushed down off the inner
    # gold lip by label_off so the caps never graze the band/ring at r=56.
    fr = field_r // SS
    cap = max(8, int(r * 0.16))
    label_radius = fr - int(r * label_off) - cap // 2
    _arc_label(out, (cx2, cx2), label, label_radius, cap, top=True)

    # Brand star at 6 o'clock (crisp, centered) — or dropped.
    if star:
        star_r = max(3, int(r * 0.075))
        _brand_star(out, (cx2, cx2 + fr - star_r - int(r * 0.04)), star_r)

    # Hero value — brightest element, optically centered with the label.
    _gold_value(out, (cx2, cx2 + int(r * value_off)), value,
                max(15, int(r * 0.56)))
    return out


# ── variants ─────────────────────────────────────────────────────────────────
# Each is the same refined Enamel lead with one proportion knob moved, so the
# art-director can lock ring px / band width / label offset.

def _ring_px(r, pct):
    return round(r * pct)


VARIANTS = [
    ("V_A  LEAD",
     lambda r, v, l: enamel(r, v, l, ring_pct=0.14, band_pct=0.12,
                            label_off=0.07, value_off=0.05, star=True),
     lambda r: f"ring {_ring_px(r,0.14)}px  band 12%r  label +7%r  star on"),
    ("V_B  WIDE BAND",
     lambda r, v, l: enamel(r, v, l, ring_pct=0.13, band_pct=0.14,
                            label_off=0.07, value_off=0.05, star=True),
     lambda r: f"ring {_ring_px(r,0.13)}px  band 14%r  label +7%r  star on"),
    ("V_C  THIN RING",
     lambda r, v, l: enamel(r, v, l, ring_pct=0.11, band_pct=0.12,
                            label_off=0.08, value_off=0.05, star=False),
     lambda r: f"ring {_ring_px(r,0.11)}px  band 12%r  label +8%r  star off"),
]


# ── backdrop matching the dimmed pause overlay ───────────────────────────────

def _backdrop(w, h):
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        col = lerp_color((18, 12, 46), (8, 5, 26), t)
        pygame.draw.line(surf, col, (0, y), (w, y))
    return surf


def _panel(w, h):
    s = pygame.Surface((w, h))
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = lerp_color((22, 15, 54), (11, 7, 34), t)
        pygame.draw.line(s, col, (0, yy), (w, yy))
    return s


def _grayscale(surf):
    """Value-only copy for the accessibility contrast check. Luminance so
    the scarlet collapses to mid-grey (decorative) and the gold value/label
    must still separate from the navy field on luminance alone."""
    return pygame.transform.grayscale(surf)


def _live(r, value):
    em = pygame.Surface((r * 2 + 12, r * 2 + 12), pygame.SRCALPHA)
    live_score_emblem(em, r + 6, r + 6, r, "S C O R E", value)
    return em


# ── build the review sheet ───────────────────────────────────────────────────

def build():
    # One row per item: CURRENT first, then the 3 Enamel variants.
    rows = [("CURRENT (live _score_emblem)", None,
             lambda r: "flat matte ring + laurel ticks + label on inner ring")]
    rows += VARIANTS

    margin = 26
    header_h = 110
    row_h = 250
    # Columns inside a row: [detail r=72] [native strip] [grayscale chip]
    detail_w = 210
    strip_w = 470
    gray_w = 150
    row_w = detail_w + strip_w + gray_w + margin * 4

    sheet_w = row_w + margin * 2
    sheet_h = header_h + len(rows) * (row_h + margin) + margin

    sheet = _backdrop(sheet_w, sheet_h)

    title = _font(40, True).render("SCORE MEDALLION — ROUND 2  (Enamel refined + Minted bevel)",
                                   True, _GOLD_BRIGHT)
    sheet.blit(title, (margin, 22))
    sub = _font(18, True).render(
        "detail @r=72  |  true 1x strip: r=56 \"47\" (judge here) · r=72 \"47\" · r=72 \"128\"  |  grayscale value-contrast chip @r=56",
        True, UI_CREAM)
    sub.set_alpha(210)
    sheet.blit(sub, (margin, 66))
    sub2 = _font(16, True).render(
        "gold-on-navy value + curved gold label inside navy field  ·  directional bevel light TL / dark BR  ·  one gloss arc on the scarlet band",
        True, UI_CREAM)
    sub2.set_alpha(170)
    sheet.blit(sub2, (margin, 88))

    for ridx, (name, fn, descfn) in enumerate(rows):
        ty = header_h + margin + ridx * (row_h + margin)
        tile = _panel(row_w, row_h)

        nm = _font(24, True).render(name, True, _GOLD_BRIGHT)
        tile.blit(nm, (16, 12))
        dl = _font(14, True).render(descfn(72), True, UI_CREAM)
        dl.set_alpha(195)
        tile.blit(dl, (16, 42))

        # --- column 1: big detail at r=72 "47" ---
        big_r = 72
        big = _live(big_r, "47") if fn is None else fn(big_r, "47", "S C O R E")
        col1_cx = margin + detail_w // 2
        col1_cy = 70 + row_h // 2 - 30
        tile.blit(big, (col1_cx - big.get_width() // 2,
                        col1_cy - big.get_height() // 2))
        cap = _font(12, True).render("detail r=72", True, UI_CREAM)
        cap.set_alpha(180)
        tile.blit(cap, cap.get_rect(center=(col1_cx, col1_cy + big_r + 22)))

        # --- column 2: native 1x strip ---
        strip_x0 = margin * 2 + detail_w
        lbl = _font(14, True).render("NATIVE 1x", True, UI_CREAM)
        lbl.set_alpha(200)
        tile.blit(lbl, (strip_x0, 78))
        specs = [(56, "47"), (72, "47"), (72, "128")]
        gap = 18
        total = sum(s[0] * 2 for s in specs) + gap * (len(specs) - 1)
        sx = strip_x0 + (strip_w - total) // 2
        sy = 78 + 30
        band_h = 72 * 2
        for rr, val in specs:
            em = _live(rr, val) if fn is None else fn(rr, val, "S C O R E")
            tile.blit(em, (sx, sy + (band_h - em.get_height()) // 2))
            cap = _font(12, True).render(f'r={rr} "{val}"', True, UI_CREAM)
            cap.set_alpha(185)
            tile.blit(cap, cap.get_rect(center=(sx + rr, sy + band_h + 14)))
            sx += rr * 2 + gap

        # --- column 3: grayscale value-contrast chip at r=56 "47" ---
        g_r = 56
        chip = _live(g_r, "47") if fn is None else fn(g_r, "47", "S C O R E")
        gray = _grayscale(chip)
        gx0 = margin * 3 + detail_w + strip_w
        glbl = _font(14, True).render("VALUE-ONLY", True, UI_CREAM)
        glbl.set_alpha(200)
        tile.blit(glbl, (gx0 + (gray_w - glbl.get_width()) // 2, 78))
        gcx = gx0 + gray_w // 2
        gcy = 78 + 30 + g_r + 6
        tile.blit(gray, (gcx - gray.get_width() // 2,
                         gcy - gray.get_height() // 2))
        gcap = _font(12, True).render("grayscale r=56", True, UI_CREAM)
        gcap.set_alpha(180)
        tile.blit(gcap, gcap.get_rect(center=(gcx, gcy + g_r + 16)))

        sheet.blit(tile, (margin, ty))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "score_emblem_redesign")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.abspath(os.path.join(out_dir, "round_2.png"))
    pygame.image.save(sheet, out_path)
    print(out_path)


if __name__ == "__main__":
    build()

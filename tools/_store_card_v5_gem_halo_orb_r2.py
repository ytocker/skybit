"""halo-orb gem badge exploration — round 2 render.

Revises round-1 on all art-director notes:
  P0 — rarity ladder replaced with sparkle ARM COUNT (4/4/6/8 arms for
       common/rare/epic/legendary) so it reads in greyscale; BLEND_ADD on
       the sparkle removed; explicit tier-gf lookup replaces luminance formula.
  P1 — directional shadow crescent on the lower-right makes the sphere read
       as truly 3-D; specular hotspot shifted slightly off the shadow centre;
       sparkle arm length shrunk from 0.5r to 0.32r.
  P2 — halo ring now contrast-seated on a 1px inner dark ring at 0.89r so
       it has something to push against; specular radius varies by tier via
       the (0.18 + 0.10*gf) formula instead of fixed.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font as hud_font

RARITY_TIERS = [
    ("common",    (214, 206, 230), (78,  74, 112)),
    ("rare",      (108, 188, 252), (24,  78, 142)),
    ("epic",      (194, 122, 248), (80,  34, 126)),
    ("legendary", (255, 202, 104), (150, 92,  22)),
]
SID_PRIMARY   = "skin_mummy"    # EPIC
SID_SECONDARY = "skin_kitsune"  # LEGENDARY
CARD_W = sc.CARD_W * sc.SS   # 324
GEM_R  = sc.m(sc.GEM_R + 3)  # 22 device px


def _tier_gf(base):
    # Explicit lookup so common/rare/epic/legendary each map to a specific
    # factor used for glow intensity, halo alpha, and specular radius —
    # NOT for sparkle alpha (which BLEND_ADD would clamp to white anyway).
    if base == (214, 206, 230): return 0.55
    if base == (108, 188, 252): return 0.70
    if base == (194, 122, 248): return 0.85
    if base == (255, 202, 104): return 1.00
    return 0.85   # mystery / fallback → epic-class brightness


def _is_legendary(base):
    # Only the top tier earns a second sparkle. Detected by the warm-gold hue
    # rather than threading tier metadata through the locked signature.
    return base[0] > 230 and base[1] > 170 and base[2] < 150


def _sparkle_config(gf, r):
    """Return (list-of-axis-angles-degrees, arm_length) for this tier.

    The number of axes is the greyscale-readable rarity cue: 2 axes = 4-arm
    cross (common/rare), 3 axes = 6-arm star (epic), 4 axes = 8-arm star
    (legendary). Rare gets a slight length bump to separate it visually from
    common despite the same arm count.
    """
    base_len = int(r * 0.32)
    if gf <= 0.60:                        # common — 4-arm cross
        return [0, 90], base_len
    if gf <= 0.75:                        # rare — 4-arm cross, slightly longer
        return [0, 90], int(r * 0.38)
    if gf <= 0.90:                        # epic — 6-arm star (three 60°-spaced axes)
        return [0, 60, 120], base_len
    # legendary — 8-arm star (four 45°-spaced axes)
    return [0, 45, 90, 135], base_len


def _draw_arms(dst, ox, oy, angles_deg, arm_len, color, aw):
    # Each angle is a full axis: one line segment spanning both arm tips.
    for a_deg in angles_deg:
        a = math.radians(a_deg)
        dx, dy = math.cos(a) * arm_len, math.sin(a) * arm_len
        pygame.draw.line(dst, color,
                         (int(ox - dx), int(oy - dy)),
                         (int(ox + dx), int(oy + dy)), aw)


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """halo-orb: glowing spherical orb badge. Directional shading with a
    lower-right shadow crescent (3-D read), tier-varying specular radius, a
    halo ring contrast-seated on a dark inner band, and a sparkle burst whose
    ARM COUNT is the countable rarity ladder (4 / 4 / 6 / 8 for common /
    rare / epic / legendary) so it survives greyscale."""
    if mystery:
        # Mystery claims no tier — visually distinct red.
        base, deep = (232, 74, 74), (120, 20, 20)
    gf = _tier_gf(base)

    hi   = lerp_color(base, WHITE, 0.5)
    lo   = lerp_color(base, deep, 0.6)
    # ~2× darker rim so the lit centre and shadowed edge have real contrast.
    dark = lerp_color(deep, NEAR_BLACK, 0.5)

    # --- Layer 0: outer glow — tight footprint via hard radius cap -----------
    gr = int(r * 1.1)
    peak = min(60, int(60 * gf))
    glow = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
    layers = 10
    for i in range(layers, 0, -1):
        rr = int(gr * i / layers)
        a  = int(peak * (1 - i / layers))
        if rr > 0 and a > 0:
            pygame.draw.circle(glow, (*hi, a), (gr, gr), rr)
    surf.blit(glow, (cx - gr, cy - gr), special_flags=pygame.BLEND_ADD)

    # --- Layer 1: orb body — concentric rings from the offset lit centre -----
    # Highlight centre is upper-left; the 15% rim band transitions sharply
    # toward 'dark' (50% toward black) to push contrast at the terminator.
    hcx, hcy = cx - int(0.3 * r), cy - int(0.3 * r)
    for rr in range(r, 0, -1):
        d   = min(1.0, (rr + math.hypot(cx - hcx, cy - hcy)) / r)
        col = lerp_color(hi, lo, d)
        if rr > r * 0.85:
            k   = (rr - r * 0.85) / (r * 0.15)
            col = lerp_color(col, dark, min(1.0, k * 1.5))   # sharper than r1
        pygame.draw.circle(surf, col, (hcx, hcy), rr)

    # --- Layer 2: directional shadow crescent — lower-right 3-D depth --------
    # A filled dark circle offset toward lower-right, composited at alpha 120,
    # creates a visible terminator crescent that makes the sphere look convex.
    shadow_col = lerp_color(deep, NEAR_BLACK, 0.5)
    shadow = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    scr_x = r + 2 + int(0.2 * r)   # offset within the surface → cx+0.2r world
    scr_y = r + 2 + int(0.2 * r)
    pygame.draw.circle(shadow, (*shadow_col, 120),
                       (scr_x, scr_y), int(0.6 * r))
    surf.blit(shadow, (cx - r - 2, cy - r - 2))

    # --- Layer 3: rim ring — crisp dark seat against any background ----------
    pygame.draw.circle(surf, dark, (cx, cy), r, max(1, sc.m(2)))

    # --- Layer 4: halo — bright ring contrast-seated on a dark inner band ----
    # The 0.89r dark ring gives the 0.90r bright halo something to push against
    # instead of fading into the body colour at identical saturation.
    halo_buf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(halo_buf, (*dark, 200), (r + 2, r + 2),
                       int(r * 0.89), max(1, sc.m(1)))
    surf.blit(halo_buf, (cx - r - 2, cy - r - 2))

    halo_col = lerp_color(hi, WHITE, 0.3)
    halo_buf2 = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(halo_buf2, (*halo_col, int(110 * gf)), (r + 2, r + 2),
                       int(r * 0.9), max(1, sc.m(1)))
    surf.blit(halo_buf2, (cx - r - 2, cy - r - 2))

    # --- Layer 5: specular — radius varies by tier (common=small, leg=large) -
    # Using a circle instead of an ellipse keeps the glint round and clean.
    spec_r = max(3, int(r * (0.18 + 0.10 * gf)))
    spec   = pygame.Surface((spec_r * 2 + 2, spec_r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(spec, (255, 255, 255, 210), (spec_r + 1, spec_r + 1), spec_r)
    sp_cx, sp_cy = cx - int(0.35 * r), cy - int(0.35 * r)
    surf.blit(spec, (sp_cx - spec_r - 1, sp_cy - spec_r - 1),
              special_flags=pygame.BLEND_ADD)

    # --- Layer 6: sparkle — ARM COUNT is the rarity ladder -------------------
    # Centre shifted off the specular so burst and glint read as two distinct
    # elements rather than one blob. Drawn directly (no BLEND_ADD) so the white
    # lines stay white and alpha-correct on any surface type.
    arm_angles, arm_len = _sparkle_config(gf, r)
    aw    = max(2, sc.m(1))
    bx    = cx - int(0.2 * r)    # sparkle centre, offset from specular (sp_cx)
    by    = cy - int(0.2 * r)
    _draw_arms(surf, bx, by, arm_angles, arm_len, WHITE, aw)

    if _is_legendary(base):
        # Second smaller 4-arm sparkle lower-right — signature legendary tell.
        sec_cx = cx + int(0.35 * r)
        sec_cy = cy + int(0.32 * r)
        _draw_arms(surf, sec_cx, sec_cy, [0, 90], int(arm_len * 0.6), WHITE, aw)


sc.facet_gem = my_facet_gem   # monkey-patch before any draw_card call


def render_card(sid):
    ch   = sc.CARD_H * sc.SS
    surf = pygame.Surface((CARD_W, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       CARD_W - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, False, False, sc.PRICE_VARIANT)
    return surf


def render_gem(base, deep):
    pad = GEM_R + 4
    g   = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    my_facet_gem(g, pad, pad, GEM_R, base, deep, mystery=False)
    return g


def main():
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge/halo-orb"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

    margin   = 24
    gap      = 20
    header_h = 40

    card_a = render_card(SID_PRIMARY)      # epic
    card_b = render_card(SID_SECONDARY)    # legendary
    cw, chh = card_a.get_size()

    row1_y = header_h + margin
    row1_h = chh

    # Row 2 — each tier gem at 8× scale
    gems = [render_gem(b, d) for _, b, d in RARITY_TIERS]
    gw       = gems[0].get_width() * 8
    label_h  = 22
    strip_gap = 28
    row2_y   = row1_y + row1_h + margin + 20
    row2_h   = gw + label_h

    total_gw = gw * 4 + strip_gap * 3
    canvas_w = max(margin * 2 + cw * 2 + gap, margin * 2 + total_gw)
    canvas_h = row2_y + row2_h + margin

    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    canvas.fill((8, 8, 20, 255))

    # Header
    hf  = hud_font(26)
    htx = hf.render("gem badge — halo-orb r2", True, (236, 236, 248))
    canvas.blit(htx, (margin, margin // 2 + 4))

    # Row 1 — full cards
    row1_x = (canvas_w - (cw * 2 + gap)) // 2
    canvas.blit(card_a, (row1_x, row1_y))
    canvas.blit(card_b, (row1_x + cw + gap, row1_y))

    lf = hud_font(18)
    for label, x in (("EPIC — skin_mummy",      row1_x),
                     ("LEGENDARY — skin_kitsune", row1_x + cw + gap)):
        tx = lf.render(label, True, (200, 200, 220))
        canvas.blit(tx, (x + (cw - tx.get_width()) // 2, row1_y - 20))

    # Row 2 — gem strip at 8× zoom
    row2_x = (canvas_w - total_gw) // 2
    sf = hud_font(18)
    for i, ((name, _, _), gem) in enumerate(zip(RARITY_TIERS, gems)):
        big = pygame.transform.scale(gem, (gem.get_width() * 8, gem.get_height() * 8))
        gx  = row2_x + i * (gw + strip_gap)
        canvas.blit(big, (gx, row2_y))
        tx = sf.render(name, True, (206, 206, 226))
        canvas.blit(tx, (gx + (gw - tx.get_width()) // 2, row2_y + gw + 4))

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()

"""arched-niche card concept — a cathedral/tombstone aperture replacing the
circular cabochon dome.

The character frame becomes a gold-bezeled ARCHED NICHE: a rounded-rect base
capped by a semicircular crown. This is the only size direction whose silhouette
is fully distinct from the circle/ellipse family — a vertical, throne-like alcove
that simultaneously GROWS the hero (a taller aperture, head rising into the crown)
and the gold RIM (a larger, more architectural frame around the skin).

Build per card: let the standard CONSTELLATION card render with the dome/glass/
aura AND the default ribbon+name suppressed, so draw_card only lays down the
frame, crest gem and price chip. Then paint the niche into the dome's place — a
tombstone silhouette filled with the dome's own glass gradient (CABO_C_LO -> HI
radial), the hero clipped to that silhouette, a glass sheen, and a 3-layer gold
bezel (dark contact keyline -> warm gold band -> pale glint). Finally the tier
ribbon returns demoted to a slim SILL-PLATE under the niche base, with the item
name dropped just beneath it; the price chip is unchanged.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
import math
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font
from game.draw import lerp_color, NEAR_BLACK, WHITE

sd.load()

SID = "skin_mummy"
CARD_W_SS, CARD_H_SS = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324 x 200
inset = sc.m(sc._INSET)
rect_ss = pygame.Rect(inset, inset, CARD_W_SS - 2 * inset, CARD_H_SS - 2 * inset)

# BLEND_ADD reads RGB magnitude directly (source alpha is ignored), so the
# alpha-driven gloss sweep draw_card runs on the price chip silently blows it to
# white. Route the sweep through the RGB channels instead.
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


# ── niche geometry (device px on the 324x200 supersample card) ────────────────
# Crown radius == half the aperture width, so the semicircle sits cleanly on the
# jambs. The apex lifts toward the tray top so the hero's head reads INSIDE the
# crown; the sill sits low, just above the demoted tier lane.
CX = 162
ARCH_W = 120
CROWN_R = ARCH_W // 2         # 60 — semicircular crown
SHOULDER_Y = 90               # springing line where crown meets the jambs
SILL_Y = 150                  # niche base
BASE_H = SILL_Y - SHOULDER_Y  # 60 — rectangular base height
APEX_Y = SHOULDER_Y - CROWN_R # 30 — crown apex
HERO_PX = 104                 # grows from the dome's 84
HERO_CY = 90                  # centred so the head rises into the crown


def _niche_mask():
    """Tombstone silhouette as an alpha mask: the rectangular base UNIONed with
    the crown circle (its lower half falls inside the rect, so the union is one
    clean rounded-top alcove)."""
    mask = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (CX - CROWN_R, SHOULDER_Y, ARCH_W, BASE_H))
    pygame.draw.circle(mask, (255, 255, 255, 255), (CX, SHOULDER_Y), CROWN_R)
    return mask


def _arch_outline(surf, cx, crown_r, half_w, shoulder_y, sill_y, color, width):
    """One pass of the arch path: crown as a top half-circle arc, two vertical
    jambs, and the sill line. Stacking passes at shrinking radius reads as a
    keyline -> gold -> glint bezel."""
    pygame.draw.arc(surf, color, (cx - crown_r, shoulder_y - crown_r,
                                  crown_r * 2, crown_r * 2), 0.0, math.pi, width)
    pygame.draw.line(surf, color, (cx - half_w, shoulder_y), (cx - half_w, sill_y), width)
    pygame.draw.line(surf, color, (cx + half_w, shoulder_y), (cx + half_w, sill_y), width)
    pygame.draw.line(surf, color, (cx - half_w, sill_y), (cx + half_w, sill_y), width)


def draw_arch_niche_on(surf):
    mask = _niche_mask()

    # radial glass body: lit-ish centre deepening to a near-black rim — the exact
    # cabochon dome ramp, so the niche reads as the same material as the old well.
    mid_y = (APEX_Y + SILL_Y) // 2
    maxr = int(math.hypot(CROWN_R, (SILL_Y - APEX_Y) / 2)) + sc.m(2)
    body = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    for i in range(maxr, 0, -1):
        col = lerp_color(sc.CABO_C_LO, sc.CABO_C_HI, (i / maxr) ** 1.28)
        pygame.draw.circle(body, (*col, 255), (CX, mid_y), i)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, (0, 0))

    # soft tier aura hugging the alcove so it sits in a pool of light like the dome
    glow = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    for i in range(maxr + sc.m(6), 0, -sc.m(1) or 1):
        a = int(26 * (i / (maxr + sc.m(6))))
        pygame.draw.circle(glow, (150, 120, 60, a), (CX, mid_y), i)
    surf.blit(glow, (0, 0))

    # hero clipped to the silhouette so the skin fills the alcove
    hero = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.blit_thumb(hero, SID, CX, HERO_CY, HERO_PX)
    hero.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hero, (0, 0))

    # thin top-left specular so the glass dome-front still reads over the niche
    spec = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    pygame.draw.circle(spec, (255, 255, 255, 48),
                       (CX - CROWN_R // 3, SHOULDER_Y - CROWN_R // 2),
                       int(CROWN_R * 0.72))
    spec.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(spec, (0, 0), special_flags=pygame.BLEND_ADD)

    # gold bezel — dark contact keyline outermost, warm-gold band, pale glint.
    _arch_outline(surf, CX, CROWN_R, CROWN_R, SHOULDER_Y, SILL_Y,
                  (0, 0, 0, 200), max(1, sc.m(2.0)))
    _arch_outline(surf, CX, CROWN_R - sc.m(1), CROWN_R - sc.m(1), SHOULDER_Y,
                  SILL_Y - sc.m(1), (*sc.CARD_RING_BRIGHT, 235), max(1, sc.m(1.6)))
    _arch_outline(surf, CX, CROWN_R - sc.m(2.4), CROWN_R - sc.m(2.4), SHOULDER_Y,
                  SILL_Y - sc.m(2.4), (246, 220, 140, 160), max(1, sc.m(0.8)))

    # bright glass kiss on the upper-left crown arc only
    kiss = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    pygame.draw.arc(kiss, (255, 255, 255, 130),
                    (CX - CROWN_R + sc.m(1), SHOULDER_Y - CROWN_R + sc.m(1),
                     CROWN_R * 2 - sc.m(2), CROWN_R * 2 - sc.m(2)),
                    math.radians(108), math.radians(184), max(1, sc.m(1)))
    surf.blit(kiss, (0, 0), special_flags=pygame.BLEND_ADD)


def _sill_plate(surf, tier_word, cx, cy, max_w, pal):
    """Tier ribbon demoted to a slim architectural sill-plate seated under the
    niche base — a low tier-gradient bar edged in the bezel's gold, so it reads
    as the alcove's stone sill rather than a floating banner."""
    f = sc.font(8.5)
    tw = sc._glyph_base(tier_word, f, sc.m(1.4)).get_width()
    pad = sc.m(12)
    w = min(max_w, tw + pad * 2)
    h = sc.m(8)
    rad = h // 2
    x0, y0 = cx - w // 2, cy - h // 2
    top = lerp_color(pal["gem"], WHITE, 0.1)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    bar = sc.vgrad_stops(w, h, rad, [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                         255, gamma=1.08)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), (0, 0, w, h), border_radius=rad)
    surf.blit(sh, (x0, y0 + sc.m(2)))
    surf.blit(bar, (x0, y0))
    pygame.draw.rect(surf, (4, 5, 16), (x0, y0, w, h),
                     width=max(1, sc.m(1.4)), border_radius=rad)
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 185),
                     (x0 + sc.m(1), y0 + sc.m(1), w - sc.m(2), h - sc.m(2)),
                     width=max(1, sc.m(1)), border_radius=rad)
    sc.plain_text(surf, tier_word, f, (cx, cy), (14, 12, 26), shadow_a=0,
                  tracking=sc.m(1.4), weight=sc.m(0.7))


def render_baseline():
    sc._card_cache.clear()
    surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.draw_card(surf, SID, rect_ss, equipped=False, secret=False)
    return surf


def render_concept():
    """The full card with the dome swapped for the arched niche and the tier lane
    demoted to a sill-plate."""
    sc._card_cache.clear()

    # suppress the circular dome stack AND the default ribbon/name so draw_card
    # only lays down the frame, crest gem and price chip; the niche and its
    # relocated lane are painted afterward.
    saved = (sc.cabochon, sc.cabochon_glass, sc.soft_glow, sc.blit_thumb,
             sc._ribbon_lozenge, sc._name_on)
    sc.cabochon = lambda *a, **k: None
    sc.cabochon_glass = lambda *a, **k: None
    sc.soft_glow = lambda *a, **k: None
    sc.blit_thumb = lambda *a, **k: None
    sc._ribbon_lozenge = lambda *a, **k: None
    sc._name_on = lambda *a, **k: None

    surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.draw_card(surf, SID, rect_ss, equipped=False, secret=False)

    (sc.cabochon, sc.cabochon_glass, sc.soft_glow, sc.blit_thumb,
     sc._ribbon_lozenge, sc._name_on) = saved
    sc._card_cache.clear()

    draw_arch_niche_on(surf)

    pal = sc.RARITY[sc._rarity(SID)]
    _sill_plate(surf, sc._rarity(SID).upper(), CX, SILL_Y, rect_ss.w - sc.m(34), pal)
    sc._name_on(surf, sc._name(SID), CX, rect_ss.y + sc.m(77), rect_ss.w - sc.m(26))
    return surf


# ── render ────────────────────────────────────────────────────────────────────
baseline_ss = render_baseline()
concept_ss = render_concept()

# ── comparison sheet: baseline | concept at 2x, plus a 1x row ─────────────────
GAP, PAD, LABEL_H, HEADER_H = 8, 16, 28, 44
sheet_w = PAD * 2 + 2 * CARD_W_SS + GAP
sheet_h = PAD + HEADER_H + LABEL_H + CARD_H_SS + GAP + LABEL_H + sc.CARD_H + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

fl = hud_font(13)
fh = hud_font(17)

title = fh.render("store_card_size  ·  arched-niche  ·  round 1", True, (240, 224, 180))
sheet.blit(title, (PAD, 12))
sub = hud_font(11).render(
    "cathedral/tombstone aperture: rounded-rect base + semicircular gold crown "
    "replaces the circular dome", True, (150, 156, 178))
sheet.blit(sub, (PAD, 30))

panels = [("BASELINE  ·  circular dome", baseline_ss),
          ("CONCEPT  ·  arched niche", concept_ss)]
for i, (lbl_text, surf) in enumerate(panels):
    x = PAD + i * (CARD_W_SS + GAP)
    lbl = fl.render(lbl_text, True, (210, 206, 190))
    sheet.blit(lbl, (x + CARD_W_SS // 2 - lbl.get_width() // 2, PAD + HEADER_H))
    sheet.blit(surf, (x, PAD + HEADER_H + LABEL_H))

y1x = PAD + HEADER_H + LABEL_H + CARD_H_SS + GAP + LABEL_H
row_lbl = fl.render("at 1x  (162x100 final size)", True, (180, 180, 200))
sheet.blit(row_lbl, (PAD, y1x - LABEL_H + 4))
for i, (_, surf) in enumerate(panels):
    x = PAD + i * (CARD_W_SS + GAP) + (CARD_W_SS - sc.CARD_W) // 2
    small = pygame.transform.smoothscale(surf, (sc.CARD_W, sc.CARD_H))
    sheet.blit(small, (x, y1x))

out = "docs/store_card_size/arched_niche/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")

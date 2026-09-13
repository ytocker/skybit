import os, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (cabochon, cabochon_glass, blit_thumb, facet_gem,
    chip_body_stops, vgrad_stops, vgrad, soft_glow, drop_shadow, bevel_rim,
    top_sheen, plain_text, _ribbon, _name_on, price_chip, coin_glyph,
    CARD_T, CARD_B, CABO_LO, CABO_HI, CARD_RING_DEEP, CARD_RING_BRIGHT, m, SS)
from game.hud import _font
from game.draw import lerp_color


# The stock additive gloss clips to a white slab once a chip is blown up to
# popup scale; this eased version stays a translucent sheen instead.
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
GOLD_STOPS = [(0.00, (244, 192, 88)), (0.32, (228, 162, 56)),
              (0.66, (196, 124, 34)), (1.00, (150, 92, 18))]
# Greyed CLASS band for the can't-afford ticket: the light has drained cold.
GREY_STOPS = [(0.00, (150, 154, 168)), (0.42, (108, 112, 128)),
              (1.00, (60, 64, 82))]
# Panel body lifted so the whole ticket reads as ONE silhouette above the scrim,
# yet still darker than the CLASS band (its brightest large area).
BODY_TOP = (40, 34, 62)
BODY_BOT = (24, 20, 40)

CARD_RAD = 16
POP_W, POP_H = 200, 290
SEAM_Y = 208          # dashed perforation line, near the bottom
NOTCH_R = 7           # punched-hole notch cut into each side edge at the seam


def _disc(r=85):
    """The item cabochon: domed glass well carrying the real skin under a gold
    bezel. Authored oversized then downscaled by the caller for a crisp dome."""
    DS = r * 2 + 40
    ss = pygame.Surface((DS, DS), pygame.SRCALPHA)
    cx = cy = DS // 2
    cabochon(ss, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=22)
    try:
        blit_thumb(ss, "skin_classic", cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(ss, (*pal["gem"], 255), (cx, cy), int(r * 0.7))
    cabochon_glass(ss, cx, cy, r, tint=pal["gem"])
    return pygame.transform.smoothscale(ss, (r * 2, r * 2))


_DISC_SRC = _disc(85)


def _fit_font(word, size, max_w, tracking, bold=True):
    f = _font(int(round(size)), bold)
    from game.store_cards import _glyph_base
    while _glyph_base(word, f, tracking).get_width() > max_w and size > 9:
        size -= 1
        f = _font(int(round(size)), bold)
    return f


def _class_band(dst, rect, affordable):
    """Full-width CLASS band: the ticket's brightest large area. Gold when
    affordable, drained-cold when not. Carries a small CLASS caption and the
    large tier value LEGENDARY."""
    stops = GOLD_STOPS if affordable else GREY_STOPS
    band = vgrad_stops(rect.w, rect.h, 0, stops, 255, gamma=1.05)
    dst.blit(band, rect.topleft)
    top_sheen(dst, rect, 0, int(rect.h * 0.5), peak=40 if affordable else 26)
    # a hot foot-lip so the band reads as an emitting field, not a flat swatch;
    # small colour under BLEND_ADD keeps it from blowing white.
    lip = pygame.Surface((rect.w, 5), pygame.SRCALPHA)
    lipc = (255, 226, 152) if affordable else (150, 156, 172)
    for y in range(5):
        pygame.draw.line(lip, (*lipc, int(140 * (y / 4))), (0, y), (rect.w, y))
    dst.blit(lip, (rect.x, rect.bottom - 5), special_flags=pygame.BLEND_ADD)
    # dark contact line under the lip so the band edge is defined
    pygame.draw.line(dst, (60, 36, 8) if affordable else (30, 32, 42),
                     (rect.x, rect.bottom), (rect.right, rect.bottom), 1)

    cap_col = (58, 34, 8) if affordable else (36, 38, 50)
    plain_text(dst, "CLASS", _font(9, True), (rect.x + 22, rect.y + 12),
               cap_col, shadow_a=0, tracking=2, weight=m(0.4))
    # a thin rule under the caption — a boarding-pass field divider
    pygame.draw.line(dst, (*cap_col, 160), (rect.x + 9, rect.y + 20),
                     (rect.x + 55, rect.y + 20), 1)
    # tiny airline tag top-right reinforces the boarding-pass identity
    plain_text(dst, "SKYBIT AIR", _font(7, True), (rect.right - 34, rect.y + 12),
               cap_col, shadow_a=0, tracking=1, weight=m(0.3))

    word = "LEGENDARY"
    f = _fit_font(word, 20, rect.w - 26, 1)
    if affordable:
        # deep glyph fill + thin bright keyline => >=4.5:1 on the gold band
        plain_text(dst, word, f, (rect.centerx, rect.y + 33), (18, 12, 4),
                   shadow_a=0, tracking=1, weight=m(0.9),
                   keyline=(255, 232, 172), kw=m(0.5))
    else:
        plain_text(dst, word, f, (rect.centerx, rect.y + 33), (20, 22, 32),
                   shadow_a=0, tracking=1, weight=m(0.9),
                   keyline=(168, 172, 188), kw=m(0.5))


def _perforation(dst, y, affordable):
    """The ticket's perforation seam — the signature element: a run of engraved
    dashes between two punched-hole notches, with a faint emboss so it reads as
    a real tear line pressed into the stock."""
    dash, gap = 5, 4
    x = NOTCH_R + 4
    end = POP_W - NOTCH_R - 4
    base = (14, 12, 26)
    hi = (66, 60, 92) if affordable else (58, 60, 78)
    while x < end:
        x2 = min(x + dash, end)
        # engraved: a dark groove with a 1px light lip on its lower edge
        pygame.draw.line(dst, base, (x, y), (x2, y), 2)
        pygame.draw.line(dst, hi, (x, y + 1), (x2, y + 1), 1)
        x += dash + gap


def _confirm_button(dst, rect, radius, affordable):
    """Primary CONFIRM. Gold when affordable with a dark-espresso label for a
    legible >=4.5:1; a muted disabled slate with a light label otherwise."""
    drop_shadow(dst, rect, radius, blur=5, alpha=120, dy=2)
    if affordable:
        dst.blit(vgrad_stops(rect.w, rect.h, radius, GOLD_STOPS, 255, gamma=1.05),
                 rect.topleft)
        top_sheen(dst, rect, radius, int(rect.h * 0.45), peak=46)
        pygame.draw.rect(dst, (86, 50, 8), rect, width=2, border_radius=radius)
        bevel_rim(dst, rect, radius, (86, 50, 8), (255, 240, 190, 235), w=2)
        tc, key = (40, 20, 8), (255, 240, 196)
    else:
        dst.blit(vgrad_stops(rect.w, rect.h, radius,
                 [(0.0, (92, 96, 114)), (1.0, (50, 54, 70))], 255), rect.topleft)
        pygame.draw.rect(dst, (18, 20, 30), rect, width=2, border_radius=radius)
        bevel_rim(dst, rect, radius, (18, 20, 30), (146, 154, 174, 200), w=2)
        tc, key = (214, 220, 234), None
    plain_text(dst, "CONFIRM", _font(14, True), rect.center, tc, shadow_a=0,
               tracking=1, weight=m(0.7),
               keyline=key, kw=m(0.5) if key else None)


def _cancel_ghost(dst, center):
    """CANCEL as smaller ghost text below the primary — near-white with a crisp
    1px dark outline so it stays legible on the dark stub."""
    plain_text(dst, "CANCEL", _font(11, True), center, (234, 228, 216),
               shadow_a=0, tracking=1, weight=m(0.4),
               keyline=(10, 8, 18), kw=m(0.5))


def build_popup(affordable):
    pop = pygame.Surface((POP_W, POP_H), pygame.SRCALPHA)
    cx = POP_W // 2

    # lifted body panel => the whole ticket is one silhouette above the scrim
    pop.blit(vgrad(POP_W, POP_H, CARD_RAD, BODY_TOP, BODY_BOT, 255, gamma=1.12),
             (0, 0))

    # CLASS band across the full top (square here; the silhouette clip rounds it)
    band = pygame.Rect(0, 0, POP_W, 48)
    _class_band(pop, band, affordable)

    disc_cy = 118
    disc_diam = 106
    disc_r = disc_diam // 2

    # disc halo — MUST NOT outshine the CLASS band. Muted warm, low peak_alpha.
    if affordable:
        soft_glow(pop, cx, disc_cy, disc_r + 6, (60, 45, 20), 14, layers=6)
    else:
        soft_glow(pop, cx, disc_cy, disc_r + 6, (40, 54, 86), 30, layers=6)

    disc = pygame.transform.smoothscale(_DISC_SRC, (disc_diam, disc_diam))
    pop.blit(disc, disc.get_rect(center=(cx, disc_cy)))
    if not affordable:
        cold = pygame.Surface((disc_diam, disc_diam), pygame.SRCALPHA)
        pygame.draw.circle(cold, (58, 84, 140, 96),
                           (disc_r, disc_r), disc_r)
        pop.blit(cold, cold.get_rect(center=(cx, disc_cy)))

    # item name field
    _name_on(pop, "CLASSIC MACAW", cx, 186, POP_W - 40)

    # perforation seam + punched notches (cut into the mask below)
    _perforation(pop, SEAM_Y, affordable)

    # ── STUB BAND ──────────────────────────────────────────────────────────
    # FARE field on the left
    fcol = (250, 214, 138) if affordable else (198, 204, 220)
    plain_text(pop, "FARE", _font(8, True), (34, 232), fcol, shadow_a=0,
               tracking=2, weight=m(0.4))
    coin_glyph(pop, 24, 256, 9)
    numcol = (250, 224, 158) if affordable else (206, 212, 226)
    plain_text(pop, "12,000", _font(13, True), (72, 256), numcol,
               shadow_a=0, weight=m(0.8), keyline=(10, 8, 18), kw=m(0.5))

    # primary CONFIRM (wide) + CANCEL ghost beneath it, on the right
    btn = pygame.Rect(104, 232, 88, 30)
    _confirm_button(pop, btn, 15, affordable)
    _cancel_ghost(pop, (btn.centerx, 278))

    # inner tray keyline + card bevel + dark outer keyline, inside silhouette
    pygame.draw.rect(pop, (*CARD_RING_BRIGHT, 60),
                     pygame.Rect(4, 4, POP_W - 8, POP_H - 8), width=1,
                     border_radius=CARD_RAD - 3)
    pygame.draw.rect(pop, (4, 5, 16), pop.get_rect(), width=2,
                     border_radius=CARD_RAD)
    bevel_rim(pop, pop.get_rect(), CARD_RAD, CARD_RING_DEEP,
              (*CARD_RING_BRIGHT, 220), w=2)

    # dark ring around each notch so the punched hole reads finished, THEN cut
    for nx in (0, POP_W):
        pygame.draw.circle(pop, (8, 8, 18), (nx, SEAM_Y), NOTCH_R + 2)

    # clip to the rounded silhouette AND punch the two seam notches transparent
    mask = pygame.Surface((POP_W, POP_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=CARD_RAD)
    pygame.draw.circle(mask, (0, 0, 0, 0), (0, SEAM_Y), NOTCH_R)
    pygame.draw.circle(mask, (0, 0, 0, 0), (POP_W, SEAM_Y), NOTCH_R)
    pop.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return pop


# ── showcase canvas ─────────────────────────────────────────────────────────
CW, CH = 500, 360
canvas = pygame.Surface((CW, CH))
canvas.fill((8, 8, 20))

title_f = _font(15, True)
tsurf = title_f.render("BOARDING-PASS  ·  confirm purchase v3  ·  round 2", True,
                       (150, 150, 170))
canvas.blit(tsurf, tsurf.get_rect(center=(CW // 2, 18)))

py = 38
for px, aff, cap in ((48, True, "AFFORDABLE"), (252, False, "CAN'T AFFORD")):
    rect = pygame.Rect(px, py, POP_W, POP_H)
    drop_shadow(canvas, rect, CARD_RAD, blur=14, alpha=150, dy=6)
    # only the band bloom past the card edge survives on the scrim; kept dim so
    # the CLASS band stays the brightest large area, not the scrim halo.
    if aff:
        soft_glow(canvas, rect.centerx, rect.y + 18, 108, (26, 16, 5), 46,
                  layers=5)
    pop = build_popup(aff)
    canvas.blit(pop, rect.topleft)
    cs = _font(12, True).render(cap, True,
                                (190, 190, 205) if aff else (150, 152, 168))
    canvas.blit(cs, cs.get_rect(center=(rect.centerx, rect.bottom + 16)))

out = "/home/user/skybit/docs/confirm_purchase_v3/boarding-pass/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())

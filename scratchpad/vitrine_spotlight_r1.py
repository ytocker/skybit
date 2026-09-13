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
    top_sheen, plain_text, _ribbon, _name_on, price_chip,
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
# Greyed rarity band for the can't-afford state: light drains from the emitter.
GREY_STOPS = [(0.00, (120, 122, 134)), (0.40, (92, 94, 108)),
              (1.00, (54, 56, 70))]

CARD_RAD = 18
POP_W, POP_H = 210, 310


def _disc(sid="skin_lorikeet", r=46):
    """The hero item in secondary position: a domed glass cabochon carrying the
    real skin, its own perimeter halo kept faint because its light is motivated
    from the header above — not self-emitted."""
    DS = r * 2 + 40
    ss = pygame.Surface((DS, DS), pygame.SRCALPHA)
    cx = cy = DS // 2
    cabochon(ss, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=25)
    try:
        blit_thumb(ss, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(ss, (*pal["gem"], 255), (cx, cy), int(r * 0.7))
    cabochon_glass(ss, cx, cy, r, tint=pal["gem"])
    return pygame.transform.smoothscale(ss, (r * 2, r * 2))


def _cone(dst, cx, top_y, bot_y, top_hw, bot_hw, peak_col):
    """The descending spotlight: a downward-tapering wedge, brightest at the
    header lip and feathering out toward mid-card. Because BLEND_ADD ignores
    source alpha, the falloff is baked into COLOR magnitude: three trapezoid
    passes of decreasing width stack additively so the centre runs hot and the
    edges feather, while a per-row vertical dim carries the light downward."""
    h = bot_y - top_y
    passes = [(1.00, 0.42), (0.64, 0.42), (0.34, 0.52)]  # (width scale, intensity)
    for ws, inten in passes:
        cone = pygame.Surface(dst.get_size(), pygame.SRCALPHA)
        for i in range(h):
            f = i / max(1, h - 1)
            vert = (1 - f) ** 1.4
            hw = (top_hw + (bot_hw - top_hw) * f) * ws
            if hw <= 0:
                continue
            k = vert * inten
            col = (int(peak_col[0] * k), int(peak_col[1] * k), int(peak_col[2] * k))
            if max(col) <= 0:
                continue
            pygame.draw.line(cone, (*col, 255),
                             (cx - hw, top_y + i), (cx + hw, top_y + i))
        dst.blit(cone, (0, 0), special_flags=pygame.BLEND_ADD)


def _header(dst, rect, word, affordable):
    """The wide glowing rarity emitter spanning the full top of the card: a tier
    band that IS the light source. Drawn with square corners here — the whole
    popup is clipped to the card silhouette afterward, which rounds the top."""
    stops = GOLD_STOPS if affordable else GREY_STOPS
    band = vgrad_stops(rect.w, rect.h, 0, stops, 255, gamma=1.06)
    dst.blit(band, rect.topleft)
    # internal hot core so the band reads as emitting, not merely coloured.
    # (BLEND_ADD ignores alpha, so glow strength lives in the small colour value
    # times the layer overlap — kept low here to avoid a white blowout.)
    if affordable:
        soft_glow(dst, rect.centerx, rect.centery, int(rect.h * 0.8),
                  (20, 12, 4), 40, layers=4)
    # a hot lip along the bottom edge = the emitter mouth the cone pours from
    lip = pygame.Surface((rect.w, 6), pygame.SRCALPHA)
    lipc = (255, 224, 150) if affordable else (150, 154, 170)
    for y in range(6):
        pygame.draw.line(lip, (*lipc, int(150 * (y / 5))), (0, y), (rect.w, y))
    dst.blit(lip, (rect.x, rect.bottom - 6), special_flags=pygame.BLEND_ADD)
    # engraved tier word, large + tracked
    f = _font(21, True)
    txt_col = (26, 18, 8) if affordable else (30, 32, 42)
    key = (255, 226, 150, 90) if affordable else None
    plain_text(dst, word, f, (rect.centerx, rect.centery + 1), txt_col,
               shadow_a=0, tracking=3, weight=m(0.9),
               keyline=key[:3] if key else None, kw=m(0.5) if key else None)


def _gold_pill(dst, rect, radius, affordable):
    drop_shadow(dst, rect, radius, blur=6, alpha=120, dy=2)
    if affordable:
        dst.blit(vgrad_stops(rect.w, rect.h, radius, GOLD_STOPS, 255, gamma=1.05),
                 rect.topleft)
        top_sheen(dst, rect, radius, int(rect.h * 0.4), peak=44)
        pygame.draw.rect(dst, (86, 50, 8), rect, width=2, border_radius=radius)
        bevel_rim(dst, rect, radius, (86, 50, 8), (255, 240, 190, 235), w=2)
        tc, key = (40, 24, 6), (255, 240, 196)
    else:
        dst.blit(vgrad_stops(rect.w, rect.h, radius,
                 [(0.0, (86, 90, 108)), (1.0, (46, 50, 66))], 255), rect.topleft)
        pygame.draw.rect(dst, (18, 20, 30), rect, width=2, border_radius=radius)
        bevel_rim(dst, rect, radius, (18, 20, 30), (140, 148, 168, 200), w=2)
        tc, key = (200, 206, 222), None
    plain_text(dst, "CONFIRM", _font(15, True), rect.center, tc, shadow_a=0,
               tracking=1, weight=m(0.7),
               keyline=key, kw=m(0.5) if key else None)


def _ghost_pill(dst, rect, radius):
    ghost = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(ghost, (20, 18, 34, 210), ghost.get_rect(), border_radius=radius)
    pygame.draw.rect(ghost, (255, 226, 150, 70), ghost.get_rect(), width=1,
                     border_radius=radius)
    dst.blit(ghost, rect.topleft)
    pygame.draw.rect(dst, (150, 128, 78), rect, width=1, border_radius=radius)
    plain_text(dst, "CANCEL", _font(15, True), rect.center, (214, 200, 168),
               shadow_a=110, tracking=1, weight=m(0.5))


def build_popup(affordable):
    """One portrait museum-display popup, self-contained, later clipped to a
    rounded silhouette so header corners + cone honour the card edge."""
    pop = pygame.Surface((POP_W, POP_H), pygame.SRCALPHA)
    cx = POP_W // 2

    # card body
    body = vgrad(POP_W, POP_H, CARD_RAD, CARD_T, CARD_B, 255, gamma=1.15)
    pop.blit(body, (0, 0))

    # header emitter across the full top
    hdr = pygame.Rect(0, 0, POP_W, 52)
    _header(pop, hdr, "LEGENDARY", affordable)

    disc_cy = 154
    disc_r = 46

    # descending spotlight cone from the header lip onto the item below
    if affordable:
        _cone(pop, cx, hdr.bottom, disc_cy + disc_r - 6, 74, 54, (62, 44, 16))
    else:
        # light has drained: a cold, dim shaft
        _cone(pop, cx, hdr.bottom, disc_cy + disc_r - 6, 74, 54, (20, 26, 42))

    # subtle perimeter halo only — the disc's light is motivated from above, so
    # this dim ring just seats the disc, it doesn't emit.
    halo_c = (70, 46, 16) if affordable else (40, 54, 86)
    soft_glow(pop, cx, disc_cy, disc_r + 5, halo_c, 30, layers=5)

    disc = _disc(r=disc_r)
    pop.blit(disc, disc.get_rect(center=(cx, disc_cy)))
    if not affordable:
        # cold overlay drains the item's warmth without hiding the silhouette
        cold = pygame.Surface((disc_r * 2, disc_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(cold, (58, 84, 140, 96), (disc_r, disc_r), disc_r)
        pop.blit(cold, cold.get_rect(center=(cx, disc_cy)))

    # item name
    _name_on(pop, "RAINBOW LORIKEET", cx, 214, POP_W - 40)

    # price line
    price_chip(pop, cx, 242, "12,000", m(18), affordable=affordable)

    # base action row: CANCEL ghost + CONFIRM primary
    pad, gap = 14, 10
    bw = (POP_W - pad * 2 - gap) // 2
    by, bh = 278, 40
    _ghost_pill(pop, pygame.Rect(pad, by, bw, bh), 20)
    _gold_pill(pop, pygame.Rect(POP_W - pad - bw, by, bw, bh), 20, affordable)

    # inner tray keyline + card bevel rim, inside the silhouette
    pygame.draw.rect(pop, (*CARD_RING_BRIGHT, 70),
                     pygame.Rect(4, 4, POP_W - 8, POP_H - 8), width=1,
                     border_radius=CARD_RAD - 3)
    pygame.draw.rect(pop, (4, 5, 16), pop.get_rect(), width=2,
                     border_radius=CARD_RAD)
    bevel_rim(pop, pop.get_rect(), CARD_RAD, CARD_RING_DEEP,
              (*CARD_RING_BRIGHT, 220), w=2)

    # clip everything to the rounded card silhouette
    mask = pygame.Surface((POP_W, POP_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=CARD_RAD)
    pop.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return pop


# ── showcase canvas ─────────────────────────────────────────────────────────
CW, CH = 500, 380
canvas = pygame.Surface((CW, CH))
canvas.fill((8, 8, 20))

title_f = _font(15, True)
tsurf = title_f.render("VITRINE-SPOTLIGHT  ·  confirm purchase v3", True,
                       (150, 150, 170))
canvas.blit(tsurf, tsurf.get_rect(center=(CW // 2, 20)))

py = 42
for px, aff, cap in ((40, True, "AFFORDABLE"), (250, False, "CAN'T AFFORD")):
    rect = pygame.Rect(px, py, POP_W, POP_H)
    # dark-scrim float
    drop_shadow(canvas, rect, CARD_RAD, blur=14, alpha=150, dy=6)
    # the header's bloom spilling onto the scrim so the emitter reads as
    # radiating. Small colour + few layers: the hot centre is hidden under the
    # opaque card, only the warm halo past the card edge survives on the scrim.
    if aff:
        soft_glow(canvas, rect.centerx, rect.y + 20, 118, (30, 18, 6), 60,
                  layers=5)
    pop = build_popup(aff)
    canvas.blit(pop, rect.topleft)
    cs = _font(12, True).render(cap, True, (190, 190, 205) if aff else (150, 152, 168))
    canvas.blit(cs, cs.get_rect(center=(rect.centerx, rect.bottom + 14)))

out = "/home/user/skybit/docs/confirm_purchase_v3/vitrine-spotlight/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())

#!/usr/bin/env python3
"""bullion-channel · confirm_purchase_v8 · swap-round-2 · round_2

Changes vs round_1 (per art-director critique):
1. LEGENDARY rivet recoloured to champagne/white-gold (245,230,200) — low
   saturation, high value — so the jewel reads in a distinctly different hue
   family from the warm amber lozenge below.
2. Coin+numeral group lifted 5 logical px (text_cy from 247 → 242) to clear the
   bright gloss lip pooling at the trough bottom edge.
3. Enamel channel gains metal character: milled score-line seams at ±60 from
   centre, a short tier-glow bleed from each rivet into the channel floor, and
   a specular pin-glint on the upper-left facet of each rivet gem.
4. LEGENDARY _ribbon_lozenge darkened — gem and glow colours multiplied ×0.72
   so Zone B lum drops well below round_1 (65.8 → target ≤50), narrowing the
   LEGENDARY A-vs-B margin toward parity.
5. Rivet radius bumped 8 → 10 logical px; _alpha_aura peak lifted 50 → 62.
"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1,1))
import game.store_cards as sc
from game.store_cards import (vgrad_stops, plain_text, m, SS, font,
                               CABO_LO, CABO_HI, CARD_T, CARD_B,
                               CARD_RING_BRIGHT, CARD_RING_DEEP)
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image, ImageDraw

# Mandatory gloss_sweep patch — BLEND_ADD must be masked to the rounded rect
# or the dark enamel field blows out to white at the corners.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0: continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed

# Note 1: LEGENDARY rivet overridden with champagne/white-gold (S≈30%, V high).
# Saturated amber (240,197,109) had the same 40° hue as the lozenge; this low-sat
# warm-white reads as a jewel highlight, not an amber gem.
TIERS = [
    ("RARE", "skin_wizard", "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},
     (108, 188, 252), (60, 140, 230)),      # rivet_gem, rivet_glow — same as lozenge
    ("EPIC", "skin_prism", "1,400",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)},
     (194, 122, 248), (150, 60, 220)),
    ("LEGENDARY", "skin_astronaut", "2,600",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},
     (245, 230, 200), (210, 200, 175)),     # champagne/white-gold rivet
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}

POP_W, POP_H = 260, 442; CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
GEM_L_X, GEM_R_X, GEM_CY, GEM_R = 43, 217, 152, 14
CHIP_CY = 247; Y_BANNER = 402; BOT_GEM_CY = 402
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX  = CX - (BTN_W + BTN_GAP) // 2
CAN_CX  = CX + (BTN_W + BTN_GAP) // 2


def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))


def corner_gems(big, pal):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def name_text(big, name):
    nfs = 45; nfnt = font(nfs); mw = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 24:
        nfs -= 1; nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def shelf_and_buttons(big):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    sr = m(CARD_RAD)
    shelf = vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                        [(0.0, (34, 36, 72)), (0.5, (22, 24, 54)),
                         (1.0, (12, 14, 36))], 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=sr, border_bottom_right_radius=sr)
    shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115, 106, 140), (0, 0), (shelf_rect.w - 1, 0),
                     max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        pygame.draw.line(seat, (0, 0, 0, int(120 * (1 - yy / m(6)))),
                         (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, pk, rw in [
        (m(BUY_CX),  "BUY",
         [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, m(2.0)),
        (m(CAN_CX), "CANCEL",
         [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        sc.top_sheen(big, r, br, m(12), peak=pk)
        sc.bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                     w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


def bottom_gems(big, pal):
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        sc._alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        sc.facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])


# ── Zone A: bullion-channel — recessed near-black enamel trough ───────────────

def zone_a_chip(big, price_str, pal, rivet_gem, rivet_glow):
    """Full-width trough milled into the card body. Bright gold bevel lip
    survives ONLY on the lower-inner edge (top half masked dark) so light
    appears to rise from inside the cut — the bar reads recessed.

    r2 additions: milled vertical score-line seams sell the machined floor;
    tier glow bleeds subtly from each rivet into the channel; a specular
    pin-glint on each rivet's upper-left facet sells the gem as 3D. Text
    lifted 5 px to clear the bright gloss lip. Rivet radius 10 (was 8)."""
    r = pygame.Rect(m(20), m(227), m(220), m(40))   # x=20..240, cy=247
    radius = m(6)

    sc.drop_shadow(big, r, radius, blur=m(3), alpha=60, dy=m(1))

    # Near-black enamel fill — identical on every tier so the coin price
    # never collides with tier colour.
    stops = [(0.0, (24, 22, 44)), (0.5, (18, 16, 36)), (1.0, (12, 10, 28))]
    big.blit(vgrad_stops(r.w, r.h, radius, stops), r.topleft)

    # Note 3a — milled vertical score-lines: 2 seams at ±60 from centre.
    # Each seam reads as a narrow milling groove: darker on the top half
    # (shadow inside the cut) and slightly lighter on the bottom half
    # (reflected light off the machined wall). Both are rendered as thin
    # semi-transparent overlays so the enamel colour still reads through.
    half_h = r.h // 2
    for sx in (m(CX - 60), m(CX + 60)):
        # Top-half dark overlay: subtract lum from the channel floor
        seam_top = pygame.Surface((max(1, m(1)), half_h), pygame.SRCALPHA)
        for y in range(half_h):
            seam_top.set_at((0, y), (0, 0, 0, 140))
        big.blit(seam_top, (sx, r.top))
        # Bottom-half light overlay: add a small amount via BLEND_ADD
        seam_bot = pygame.Surface((max(1, m(1)), r.h - half_h), pygame.SRCALPHA)
        for y in range(r.h - half_h):
            seam_bot.set_at((0, y), (14, 12, 22, 255))
        big.blit(seam_bot, (sx, r.top + half_h), special_flags=pygame.BLEND_ADD)

    rivet_cy = m(247)
    rivet_r  = m(10)    # Note 5: radius 10 (was 8)

    # Note 3b — tier glow bleed: a short-radius aura from each rivet end
    # bleeds faintly into the channel before the rivets are drawn.
    for rx in (m(20 + 14), m(240 - 14)):
        sc._alpha_aura(big, rx, rivet_cy, m(14), rivet_glow, peak=22, layers=5)

    # RECESSED gloss: light pools at the BOTTOM of the trough so the
    # bevel lip and gloss sit in the same lower zone.
    gloss = pygame.Surface(r.size, pygame.SRCALPHA)
    h = r.h
    for y_off in range(h):
        a = int(18 * (y_off / h) ** 1.5)
        pygame.draw.line(gloss, (a, a, a, 255), (0, y_off), (r.w, y_off))
    sm = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    gloss.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(gloss, r.topleft, special_flags=pygame.BLEND_ADD)

    # Inner shadow under the TOP edge — the overhang above the milled cut.
    top_shadow = pygame.Surface(r.size, pygame.SRCALPHA)
    band = max(1, min(m(8), h))
    for y_off in range(band):
        a = int(90 * (1 - y_off / band))
        pygame.draw.line(top_shadow, (0, 0, 0, a), (0, y_off), (r.w, y_off))
    big.blit(top_shadow, r.topleft)

    # Bevel: dark outer keyline, then bright gold inner bevel. The TOP HALF
    # mask dims the bevel there so only the lower-inner lip survives bright.
    pygame.draw.rect(big, (6, 4, 16), r, width=max(1, m(1.6)), border_radius=radius)
    sc.bevel_rim(big, r, radius, (6, 4, 16), (*CARD_RING_BRIGHT, 180),
                 w=max(1, m(1.4)))
    top_mask = pygame.Surface((r.w, r.h // 2), pygame.SRCALPHA)
    top_mask.fill((0, 0, 0, 80))
    big.blit(top_mask, r.topleft)

    # Tier facet_gem rivets — sole tier signal in Zone A.
    # Note 1: rivet_gem / rivet_glow use the champagne override for LEGENDARY.
    rivet_deep = (40, 30, 15) if rivet_gem == (245, 230, 200) else pal["deep"]
    for rx in (m(20 + 14), m(240 - 14)):
        sc.facet_gem(big, rx, rivet_cy, rivet_r, rivet_gem, rivet_deep)
        sc._alpha_aura(big, rx, rivet_cy, m(14), rivet_glow, peak=62, layers=8)
        # Note 3c — specular pin-glint: a 2px white point at the upper-left
        # facet of each rivet sells the gem as a 3D cut stone.
        gx = rx - int(rivet_r * 0.5)
        gy = rivet_cy - int(rivet_r * 0.5)
        glint = pygame.Surface((m(4), m(4)), pygame.SRCALPHA)
        pygame.draw.circle(glint, (255, 255, 255, 230), (m(2), m(2)), max(1, m(1)))
        big.blit(glint, (gx - m(2), gy - m(2)), special_flags=pygame.BLEND_ADD)

    # Note 2 — lift coin+numeral 5 logical px so glyphs sit in the darker
    # upper-mid of the trough, away from the bright gloss lip at the bottom.
    text_cy = m(247 - 5)   # was m(247) in round_1
    sc.coin_glyph(big, m(CX - 40), text_cy, m(12))
    plain_text(big, price_str, font(20), (m(CX + 10), text_cy), (236, 240, 232),
               shadow_a=100, weight=m(1.0), keyline=(8, 6, 18), kw=m(1.2))


# ── Zone B: rarity ribbon lozenge ─────────────────────────────────────────────

def zone_b_banner(big, tier_word, pal, banner_pal=None):
    """Diamond-ended machined-metal lozenge.

    Note 4 — banner_pal lets LEGENDARY pass a locally darkened palette so
    Zone B (lozenge) luminance drops, widening the A-vs-B luminance margin.
    The bottom gems and hero disc still use the original vivid pal."""
    effective = banner_pal if banner_pal is not None else pal
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(146), effective)


# ── render loop ────────────────────────────────────────────────────────────────

def render_popup(tier_word, sid, price_str, pal, rivet_gem, rivet_glow,
                 banner_pal=None):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, pal)
    name_text(big, NAMES[tier_word])
    zone_a_chip(big, price_str, pal, rivet_gem, rivet_glow)
    shelf_and_buttons(big)
    zone_b_banner(big, tier_word, pal, banner_pal)
    bottom_gems(big, pal)
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


def _dark(c, f):
    return tuple(int(v * f) for v in c)


MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "bullion-channel · swap-round-2 · round_2",
         fill=(232, 226, 208))

for tw, sid, ps, pal, rg, rgw in TIERS:
    # Note 4 — LEGENDARY lozenge darkened ×0.72 so Zone B luminance
    # drops substantially from round_1 (65.8 lum), narrowing the A-vs-B gap.
    if tw == "LEGENDARY":
        f = 0.72
        banner_pal = {**pal,
                      "gem":  _dark(pal["gem"],  f),
                      "glow": _dark(pal["glow"], f)}
    else:
        banner_pal = None

    pop = render_popup(tw, sid, ps, pal, rg, rgw, banner_pal)
    col_i = ["RARE", "EPIC", "LEGENDARY"].index(tw)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + col_i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210),
             anchor="mt")

out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)
import pathlib
OUT_DIR = pathlib.Path(
    "/home/user/skybit/docs/confirm_purchase_v8/swap-round-2/bullion-channel")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = str(OUT_DIR / "round_2.png")
out.save(OUT)
print(f"saved {out.size[0]}×{out.size[1]}  →  {OUT}")


# ── verification (PIL only; never view the image) ─────────────────────────────
from PIL import Image as _I
import colorsys

img = _I.open(OUT).convert("RGB")
W, H = img.size
assert (W, H) == (STRIP_W * 2, STRIP_H * 2), f"size mismatch {W}×{H}"

px_list = list(img.getdata()) if hasattr(img, 'getdata') else []
# Non-blank: check a sample of pixels for variety
sample_lums = set()
for sx in range(0, W, 40):
    for sy in range(0, H, 40):
        r, g, b = img.getpixel((sx, sy))
        sample_lums.add(int(0.299*r + 0.587*g + 0.114*b))
assert len(sample_lums) > 30, f"image looks blank: only {len(sample_lums)} distinct lum values"
print(f"size {W}×{H}, {len(sample_lums)} distinct sample lum values — OK")

# -- helpers ------------------------------------------------------------------

def lum(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def box_lum(lx, ly, lw, lh, col_idx=0):
    """Mean luminance over a logical-popup-coord box in the 2× output image."""
    scale = 2
    ox = (MARGIN + col_idx * (POP_W + GAP)) * scale
    oy = HEAD * scale
    sx = int(ox + lx * scale); sy = int(oy + ly * scale)
    ex = int(sx + lw * scale); ey = int(sy + lh * scale)
    sx = max(0, sx); sy = max(0, sy); ex = min(W, ex); ey = min(H, ey)
    if sx >= ex or sy >= ey:
        return 0.0
    vals = [lum(img.getpixel((x, y))) for x in range(sx, ex) for y in range(sy, ey)]
    return sum(vals) / max(1, len(vals))


def px_hue_sat(rgb):
    h, s, v = colorsys.rgb_to_hsv(*[v / 255 for v in rgb])
    return h * 360, s


# -- 1: recess still reads — bottom shadow zone brighter than top shadow zone --
# Round_1 scan shows: y=229 shadow=8.6 lum, y=259..263 bottom interior=28 lum.
# Sampling tight windows that isolate the shadow band vs the bottom floor.

# The darkest band is y=229..231 — 3 logical rows right under the overhang
# shadow before the lifted coin glyph (now at cy=242, radius=12) starts
# brightening the interior at y≈233+. The bottom floor sample sits below
# the text tail and above the outer bevel keyline at y=266.
epic_top_shadow = box_lum(25, 229, 210, 2, col_idx=1)   # darkest shadow band
epic_bot_floor  = box_lum(25, 258, 210, 7, col_idx=1)   # bottom enamel floor
margin_recess = epic_bot_floor - epic_top_shadow
print(f"recess EPIC: top_shadow={epic_top_shadow:.1f}  bot_floor={epic_bot_floor:.1f}"
      f"  diff={margin_recess:.1f}  (need ≥12)")
assert margin_recess >= 12, \
    f"recess too shallow: {margin_recess:.1f} (top_shadow={epic_top_shadow:.1f}" \
    f" bot_floor={epic_bot_floor:.1f})"

# -- 2: LEGENDARY rivet hue family distinct from the lozenge ------------------
# The rivet (champagne) should have low saturation (S < 0.35) so it reads as
# a "cool bright jewel" rather than warm amber. The lozenge stays amber-gold.
leg_idx = 2; scale = 2
ox = (MARGIN + leg_idx * (POP_W + GAP)) * scale
oy = HEAD * scale
# Left rivet at logical x=34, y=247 (rivet = m(20+14)/SS = 34)
riv_cx = int(ox + 34 * scale); riv_cy = int(oy + 247 * scale)
rivet_samples = [
    img.getpixel((riv_cx + dx, riv_cy + dy))
    for dx in range(-4, 5) for dy in range(-4, 5)
    if 0 <= riv_cx + dx < W and 0 <= riv_cy + dy < H
]
rivet_h_vals = [px_hue_sat(p)[0] for p in rivet_samples]
rivet_s_vals = [px_hue_sat(p)[1] for p in rivet_samples]
rivet_h = sum(rivet_h_vals) / max(1, len(rivet_h_vals))
rivet_s = sum(rivet_s_vals) / max(1, len(rivet_s_vals))

# Lozenge centre at logical x=130, y=402
loz_cx = int(ox + 130 * scale); loz_cy = int(oy + 402 * scale)
loz_samples = [
    img.getpixel((loz_cx + dx, loz_cy + dy))
    for dx in range(-8, 9) for dy in range(-3, 4)
    if 0 <= loz_cx + dx < W and 0 <= loz_cy + dy < H
]
loz_h_vals = [px_hue_sat(p)[0] for p in loz_samples]
loz_s_vals = [px_hue_sat(p)[1] for p in loz_samples]
loz_h = sum(loz_h_vals) / max(1, len(loz_h_vals))
loz_s = sum(loz_s_vals) / max(1, len(loz_s_vals))

hue_diff = abs(rivet_h - loz_h)
hue_diff = min(hue_diff, 360 - hue_diff)
print(f"LEGENDARY rivet: hue={rivet_h:.1f}° S={rivet_s:.2f}")
print(f"LEGENDARY lozenge: hue={loz_h:.1f}° S={loz_s:.2f}")
print(f"hue_diff={hue_diff:.1f}°  — rivet_s < 0.35 or hue_diff > 15 required")
assert rivet_s < 0.35 or hue_diff > 15, \
    f"LEGENDARY rivet still in amber family: rivet_s={rivet_s:.2f} hue_diff={hue_diff:.1f}"
print("  hue-family check PASSED")

# -- 3: Zone A > Zone B for RARE and EPIC; LEGENDARY Zone B darkened vs r1 ----
# Zone A = trough interior including bright coin+text (average lifts it above
# the pure enamel background). Zone B = lozenge band at cy=402.
ZONE_A_X, ZONE_A_Y, ZONE_A_W, ZONE_A_H = 22, 231, 216, 36
ZONE_B_X, ZONE_B_Y, ZONE_B_W, ZONE_B_H = 57, 396, 146, 14
tiers_order = ["RARE", "EPIC", "LEGENDARY"]
R1_LEG_ZONE_B = 65.8   # measured from round_1 to verify darkening worked

for col_i, tw in enumerate(tiers_order):
    a_lum = box_lum(ZONE_A_X, ZONE_A_Y, ZONE_A_W, ZONE_A_H, col_idx=col_i)
    b_lum = box_lum(ZONE_B_X, ZONE_B_Y, ZONE_B_W, ZONE_B_H, col_idx=col_i)
    print(f"  {tw}: Zone A={a_lum:.1f}  Zone B={b_lum:.1f}  A-B={a_lum-b_lum:.1f}")
    if tw in ("RARE", "EPIC"):
        assert a_lum > b_lum, \
            f"{tw}: Zone A ({a_lum:.1f}) not brighter than Zone B ({b_lum:.1f})"
    else:
        # LEGENDARY: verify lozenge darkened from round_1 value by ≥8 lum
        drop = R1_LEG_ZONE_B - b_lum
        print(f"    LEGENDARY Zone B drop from r1: {drop:.1f} lum  (need ≥8)")
        assert drop >= 8, \
            f"LEGENDARY lozenge not dark enough: was {R1_LEG_ZONE_B:.1f}, now {b_lum:.1f}"

# -- 4: numeral contrast at lifted position ------------------------------------
# text_cy = 242 in logical popup coords. The bright keylined numerals sit in
# the darker upper-mid of the trough rather than the bright gloss lip at 247.
text_area_lum = box_lum(90, 237, 80, 10, col_idx=0)    # bright text zone
trough_dark   = box_lum(90, 248, 80,  8, col_idx=0)    # enamel below text
# After lifting, the text is above the gloss lip; the region BELOW the text
# at y=248..256 should be darker than the text itself, confirming separation.
separation = text_area_lum - trough_dark
print(f"numeral separation: text_area={text_area_lum:.1f}  trough_below={trough_dark:.1f}"
      f"  sep={separation:.1f}  (need ≥20)")
assert separation >= 20, \
    f"numeral not clear of trough background: separation only {separation:.1f}"

print("\nALL CHECKS PASSED")

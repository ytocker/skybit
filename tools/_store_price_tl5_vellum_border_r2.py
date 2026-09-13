"""tl5 vellum-border hang-tag — round 2 exploration.

Cream hang-tag with NO ruling line. A gold rule runs around the whole face
perimeter (premium gift-tag language); the price sits large in an open field
across the lower 2/3. Gold border + gold grommet + gold ribbon read as one
cohesive gold language. Review-only render — never wired into the game.

Round 2: border weight bumped so a full pixel survives the 2x->1x downscale,
grommet highlight tightened to a clean crescent, specular pip made real,
price gradient skewed darker/bronze, cord committed to a satin ribbon.
"""

import os, sys, math as _math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()


# ── shared helpers ──────────────────────────────────────────────────────────
def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _grommet(face, gx, gy, r_out, r_bore, r_void, col_metal, col_hi, col_shadow, col_bore):
    # Solid discs throughout — the bore is a dark disc, never a transparent
    # punch-out, so nothing behind the tag bleeds through the eyelet.
    pygame.draw.circle(face, col_metal, (gx, gy), r_out)
    # Tight UL highlight crescent (120°→200°) reads as a crisp lit edge instead
    # of a muddy half-disc fan.
    pts_hi = [(gx, gy)]
    for a in range(120, 201, 4):
        pts_hi.append((int(gx + r_out * _math.cos(_math.radians(a))),
                       int(gy + r_out * _math.sin(_math.radians(a)))))
    if len(pts_hi) >= 3:
        pygame.draw.polygon(face, col_hi, pts_hi)
    # Stronger LR shadow wedge (290°→360°) grounds the opposite rim.
    pts_sh = [(gx, gy)]
    for a in range(290, 361, 4):
        pts_sh.append((int(gx + r_out * _math.cos(_math.radians(a % 360))),
                       int(gy + r_out * _math.sin(_math.radians(a % 360)))))
    if len(pts_sh) >= 3:
        pygame.draw.polygon(face, col_shadow, pts_sh)
    pygame.draw.circle(face, col_metal, (gx, gy), r_out, max(1, sc.m(1.5)))
    pygame.draw.circle(face, col_bore, (gx, gy), r_bore)
    pygame.draw.circle(face, (*col_hi[:3], 120), (gx, gy), r_bore, 1)
    pygame.draw.circle(face, col_bore, (gx, gy), r_bore - 1, 1)


def _draw_price(face, text, center, col_key, col_fill_stops=None, col_fill_flat=None, fs=16):
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
    r = mask.get_rect(center=center)
    key = mask.copy()
    key.fill((*col_key, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = sc.m(1)
    for ang in [0, 90, 180, 270]:
        face.blit(key, (r.x + int(p*_math.cos(_math.radians(ang))),
                        r.y + int(p*_math.sin(_math.radians(ang)))))
    img = mask.copy()
    if col_fill_stops:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0, col_fill_stops, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((*col_fill_flat, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


# ── tag geometry ────────────────────────────────────────────────────────────
FACE_W, FACE_H = 68, 82
TILT = -7
TAG_CENTER = (44, 60)
KNOT = (22, 13)
GX, GY = 28, 12


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    face = pygame.Surface((sc.m(FACE_W), sc.m(FACE_H)), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, sc.m(FACE_W), sc.m(FACE_H))

    # ── body ────────────────────────────────────────────────────────────────
    if affordable:
        body = sc.vgrad_stops(sc.m(FACE_W), sc.m(FACE_H), 0,
                              [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))], 255, 1.0)
    else:
        body = sc.vgrad_stops(sc.m(FACE_W), sc.m(FACE_H), 0,
                              [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))], 255, 1.0)
    face.blit(body, (0, 0))
    # Rounded-rect clip so the paper stock keeps a soft tag silhouette.
    mask_surf = pygame.Surface((sc.m(FACE_W), sc.m(FACE_H)), pygame.SRCALPHA)
    pygame.draw.rect(mask_surf, (255, 255, 255, 255), brect, border_radius=sc.m(3))
    face.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.bevel_rim(face, brect, sc.m(3),
                 (80, 52, 12, 200) if affordable else (48, 52, 64, 200),
                 (255, 240, 190, 200) if affordable else (160, 164, 180, 200),
                 w=max(1, sc.m(1.2)))

    # ── gold perimeter border ─────────────────────────────────────────────────
    # A single rule at 2px in the 2x face (= 1px at 1x) survives smoothscale;
    # the r1 two 1px lines averaged out to nothing after the downscale.
    FW, FH = sc.m(FACE_W), sc.m(FACE_H)
    border_w = max(2, sc.m(1))
    gold_b = (194, 152, 48) if affordable else (78, 82, 96)
    gold_b2 = (232, 206, 148) if affordable else (120, 124, 140)
    pygame.draw.rect(face, gold_b,
                     pygame.Rect(4, 4, FW - 8, FH - 8), border_w,
                     border_radius=max(1, sc.m(2)))
    # Inner hairline accent, lighter, one step in.
    pygame.draw.rect(face, gold_b2,
                     pygame.Rect(7, 7, FW - 14, FH - 14), max(2, sc.m(1)),
                     border_radius=max(1, sc.m(1)))

    # ── grommet ──────────────────────────────────────────────────────────────
    if affordable:
        _grommet(face, sc.m(GX), sc.m(GY), sc.m(6.5), sc.m(3), sc.m(2),
                 (194, 152, 48), (244, 212, 88), (60, 38, 8), (20, 14, 4))
        # Real specular pip on the mid-metal of the upper rim; warm white so it
        # pops off the (244,212,88) highlight rather than blending into it.
        pygame.draw.circle(face, (255, 252, 220),
                           (sc.m(GX) - sc.m(2), sc.m(GY) - sc.m(3)), max(1, sc.m(1.0)))
    else:
        _grommet(face, sc.m(GX), sc.m(GY), sc.m(6.5), sc.m(3), sc.m(2),
                 (78, 82, 96), (130, 134, 150), (28, 30, 38), (12, 14, 20))
        pygame.draw.circle(face, (200, 204, 220),
                           (sc.m(GX) - sc.m(2), sc.m(GY) - sc.m(3)), max(1, sc.m(1.0)))

    # ── price — large, open field, lower 2/3 ─────────────────────────────────
    price_center = (sc.m(FACE_W//2), sc.m(56))
    if affordable:
        # Skewed darker/bronze so the top of each glyph keeps contrast against
        # the cream body instead of fading to gold-on-cream.
        _draw_price(face, text, price_center,
                    col_key=(76, 44, 8),
                    col_fill_stops=[(0.0, (196, 148, 40)), (0.25, (180, 132, 32)),
                                    (0.6, (136, 84, 16)), (1.0, (76, 44, 8))],
                    fs=16)
    else:
        _draw_price(face, text, price_center,
                    col_key=(60, 64, 80), col_fill_flat=(148, 152, 168), fs=16)

    # ── rotate + blit ────────────────────────────────────────────────────────
    rotated = pygame.transform.rotate(face, -TILT)
    cx2, cy2 = sc.m(TAG_CENTER[0]), sc.m(TAG_CENTER[1])
    surf.blit(rotated, (cx2 - rotated.get_width()//2, cy2 - rotated.get_height()//2))

    # ── satin ribbon cord ────────────────────────────────────────────────────
    fw2, fh2 = sc.m(FACE_W), sc.m(FACE_H)
    gx_world = cx2 + (sc.m(GX) - fw2/2) * _math.cos(_math.radians(TILT)) - (sc.m(GY) - fh2/2) * _math.sin(_math.radians(TILT))
    gy_world = cy2 + (sc.m(GX) - fw2/2) * _math.sin(_math.radians(TILT)) + (sc.m(GY) - fh2/2) * _math.cos(_math.radians(TILT))

    knot = (sc.m(KNOT[0]), sc.m(KNOT[1]))
    if affordable:
        # Committed satin ribbon: dark edge + wide gold body + bright center
        # highlight line for the sheen.
        pygame.draw.line(surf, (140, 108, 32), (int(gx_world), int(gy_world)),
                         (int(knot[0]), int(knot[1])), max(3, sc.m(2)) + 2)
        pygame.draw.line(surf, (194, 152, 48), (int(gx_world), int(gy_world)),
                         (int(knot[0]), int(knot[1])), max(3, sc.m(2)))
        pygame.draw.line(surf, (244, 212, 88), (int(gx_world), int(gy_world)),
                         (int(knot[0]), int(knot[1])), max(1, sc.m(0.6)))
    else:
        pygame.draw.line(surf, (78, 82, 96), (int(gx_world), int(gy_world)),
                         (int(knot[0]), int(knot[1])), max(3, sc.m(2)))
    pygame.draw.circle(surf, (194, 152, 48) if affordable else (78, 82, 96),
                       (int(knot[0]), int(knot[1])), sc.m(1.5))


sc.price_chip = my_price_chip


# ── render sheet ────────────────────────────────────────────────────────────
def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W*sc.SS-2*inset, sc.CARD_H*sc.SS-2*inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def crop2x(sid, affordable):
    big = pygame.Surface((sc.CARD_W*sc.SS, sc.CARD_H*sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W*sc.SS-2*inset, sc.CARD_H*sc.SS-2*inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False,
                 variant=sc.PRICE_VARIANT if affordable else "locked")
    return pygame.transform.smoothscale(big.subsurface(pygame.Rect(0, 0, sc.m(80), sc.m(100))), (160, 200))


hf = hud_font(9, True); smf = hud_font(7)
BG = (8, 8, 20); CW, CH = sc.CARD_W, sc.CARD_H
PAD, GAP, HDR = 20, 12, 40

cards = [render_card_1x("skin_mummy", True), render_card_1x("skin_mummy", False),
         render_card_1x("skin_kitsune", True), render_card_1x("skin_kitsune", False)]
crops = [crop2x("skin_mummy", True), crop2x("skin_mummy", False)]
W = PAD*2 + CW*4 + GAP*3; H = HDR + 20 + CH + GAP + 200 + PAD
canvas = pygame.Surface((W, H)); canvas.fill(BG)
ht = hf.render("VELLUM-BORDER — tl5 hang-tag round 2", True, (255, 220, 80))
canvas.blit(ht, (W//2 - ht.get_width()//2, (HDR-ht.get_height())//2))
labels = ["mummy aff", "mummy lock", "kitsune aff", "kitsune lock"]
for i, (card, lbl) in enumerate(zip(cards, labels)):
    x = PAD + i*(CW+GAP)
    canvas.blit(card, (x, HDR+20))
    lt = smf.render(lbl, True, (180, 176, 200))
    canvas.blit(lt, (x + CW//2 - lt.get_width()//2, HDR+2))
for i, crop in enumerate(crops):
    canvas.blit(crop, (PAD + i*(160+GAP), HDR+20+CH+GAP))

out = "docs/store_price_tl5/vellum_border/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")

# ── verify the border survives at 1x ──────────────────────────────────────────
from PIL import Image
im = Image.open(out).convert("RGB")
print("PIL size:", im.size)

# Scan the left edge of the first 1x card (mummy aff) for gold border pixels.
card_x0 = PAD
card_y0 = HDR + 20
gold_hits = []
for yy in range(card_y0, card_y0 + CH):
    for xx in range(card_x0 + 3, card_x0 + 9):
        r, g, b = im.getpixel((xx, yy))
        if r > 150 and g > 80 and b < 100:
            gold_hits.append((xx, yy, (r, g, b)))
if gold_hits:
    print(f"BORDER OK: {len(gold_hits)} gold px in left edge x=3..8; sample {gold_hits[len(gold_hits)//2]}")
    print("verify PASS")
else:
    print("BORDER MISSING: no gold px found in x=3..8 of mummy-aff card")
    print("verify FAIL")

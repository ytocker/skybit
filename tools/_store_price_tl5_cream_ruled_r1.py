"""tl5 `cream-ruled` hang-tag — round 1 render harness.

Purest merge of the tl2 hang-tag (r2) and tl4 brass-classic (r2): a restrained
cream body ruled by a single mahogany line, a boutique cartouche, and a
dark-gold boutique pin. Headless render only — writes a review sheet under docs/.
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


def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits: return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _rot_point(px, py, fw, fh, center, angle_deg):
    th = _math.radians(angle_deg)
    dx, dy = px - fw/2, py - fh/2
    rx = dx*_math.cos(th) + dy*_math.sin(th)
    ry = -dx*_math.sin(th) + dy*_math.cos(th)
    return (center[0]+rx, center[1]+ry)


def _grommet(face, gx, gy, r_out, r_bore, r_void, col_metal, col_hi, col_shadow, col_bore):
    # Bore is a SOLID dark disc — never a transparent punch, which would bleed
    # the violet page backdrop through the eyelet.
    pygame.draw.circle(face, col_metal, (gx, gy), r_out)
    pts_hi = [(gx, gy)]
    for a in range(120, 221, 6):
        pts_hi.append((int(gx + r_out * _math.cos(_math.radians(a))),
                       int(gy + r_out * _math.sin(_math.radians(a)))))
    if len(pts_hi) >= 3:
        pygame.draw.polygon(face, col_hi, pts_hi)
    pts_sh = [(gx, gy)]
    for a in range(300, 401, 6):
        pts_sh.append((int(gx + r_out * _math.cos(_math.radians(a % 360))),
                       int(gy + r_out * _math.sin(_math.radians(a % 360)))))
    if len(pts_sh) >= 3:
        pygame.draw.polygon(face, col_shadow, pts_sh)
    pygame.draw.circle(face, col_metal, (gx, gy), r_out, max(1, sc.m(1.5)))
    pygame.draw.circle(face, col_bore, (gx, gy), r_bore)
    pygame.draw.circle(face, (*col_hi[:3], 120), (gx, gy), r_bore, 1)
    pygame.draw.circle(face, col_bore, (gx, gy), r_bore - 1, 1)


def _cord(surf, p0, p1, col_a, col_b, seg_dp, lw):
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]
    n = max(1, int(_math.hypot(dx, dy) / seg_dp))
    for i in range(n):
        t0, t1 = i/n, (i+1)/n
        x0, y0 = p0[0]+dx*t0, p0[1]+dy*t0
        x1, y1 = p0[0]+dx*t1, p0[1]+dy*t1
        pygame.draw.line(surf, col_a if i%2==0 else col_b,
                         (int(x0),int(y0)), (int(x1),int(y1)), lw)


def _draw_price(face, text, center, col_key, col_fill_stops=None, col_fill_flat=None, fs=13):
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
        img.blit(grad, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((*col_fill_flat, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


FACE_W, FACE_H = 68, 82
TILT = -7
TAG_CENTER = (44, 60)
KNOT = (22, 13)
GX, GY = 28, 12   # grommet face-local


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    face = pygame.Surface((sc.m(FACE_W), sc.m(FACE_H)), pygame.SRCALPHA)

    # ── body gradient (painted first; the real bevel_rim only strokes rims) ──
    if affordable:
        body = sc.vgrad_stops(sc.m(FACE_W), sc.m(FACE_H), 0,
                              [(0.0,(248,238,210)),(1.0,(224,204,166))], 255, 1.0)
    else:
        body = sc.vgrad_stops(sc.m(FACE_W), sc.m(FACE_H), 0,
                              [(0.0,(156,160,176)),(1.0,(88,92,112))], 255, 1.0)
    brect = pygame.Rect(0, 0, sc.m(FACE_W), sc.m(FACE_H))
    # rounded-rect alpha mask so body corners agree with the bevel rim radius
    mask = pygame.Surface(brect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255,255,255,255), mask.get_rect(), border_radius=sc.m(3))
    body = body.copy()
    body.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(body, (0,0))
    sc.bevel_rim(face, brect, sc.m(3),
                 (80,52,12,200) if affordable else (48,52,64,200),
                 (255,240,190,200) if affordable else (160,164,180,200),
                 max(1, sc.m(1.2)))

    # inner border
    inset = brect.inflate(-sc.m(3), -sc.m(3))
    pygame.draw.rect(face, (196,178,148) if affordable else (120,124,140), inset, 1, border_radius=sc.m(2))

    # ── ruling line ────────────────────────────────────────────────────────
    rule_y = sc.m(38)
    pygame.draw.line(face, (120,72,16) if affordable else (88,92,108),
                     (sc.m(3), rule_y), (sc.m(FACE_W)-sc.m(3), rule_y), max(1, sc.m(1)))

    # ── cartouche ──────────────────────────────────────────────────────────
    cart = pygame.Rect(sc.m(4), sc.m(40), sc.m(FACE_W-8), sc.m(38))
    pygame.draw.rect(face, (200,176,132) if affordable else (128,132,148), cart, border_radius=sc.m(1))
    pygame.draw.rect(face, (168,142,104) if affordable else (100,104,120), cart, 1, border_radius=sc.m(1))

    # ── grommet ────────────────────────────────────────────────────────────
    if affordable:
        _grommet(face, sc.m(GX), sc.m(GY), sc.m(6.5), sc.m(3), sc.m(2),
                 (194,152,48), (244,212,88), (60,38,8), (20,14,4))
        pygame.draw.circle(face, (255,248,200),
                           (sc.m(GX)-sc.m(3), sc.m(GY)-sc.m(3)), max(1, sc.m(0.6)))
    else:
        _grommet(face, sc.m(GX), sc.m(GY), sc.m(6.5), sc.m(3), sc.m(2),
                 (78,82,96), (130,134,150), (28,30,38), (12,14,20))
        pygame.draw.circle(face, (180,184,200),
                           (sc.m(GX)-sc.m(3), sc.m(GY)-sc.m(3)), max(1, sc.m(0.6)))

    # ── price ──────────────────────────────────────────────────────────────
    price_center = (sc.m(FACE_W//2), sc.m(59))
    if affordable:
        _draw_price(face, text, price_center,
                    col_key=(76,44,8),
                    col_fill_stops=[(0.0,(224,176,64)),(0.35,(190,144,40)),(0.7,(136,84,16)),(1.0,(76,44,8))],
                    fs=15)
    else:
        _draw_price(face, text, price_center,
                    col_key=(60,64,80), col_fill_flat=(148,152,168), fs=15)

    # ── rotate + blit ──────────────────────────────────────────────────────
    rotated = pygame.transform.rotate(face, -TILT)
    cx2, cy2 = sc.m(TAG_CENTER[0]), sc.m(TAG_CENTER[1])
    surf.blit(rotated, (cx2 - rotated.get_width()//2, cy2 - rotated.get_height()//2))

    # ── cord ───────────────────────────────────────────────────────────────
    fw2, fh2 = sc.m(FACE_W), sc.m(FACE_H)
    gx_world = cx2 + (sc.m(GX) - fw2/2) * _math.cos(_math.radians(TILT)) - (sc.m(GY) - fh2/2) * _math.sin(_math.radians(TILT))
    gy_world = cy2 + (sc.m(GX) - fw2/2) * _math.sin(_math.radians(TILT)) + (sc.m(GY) - fh2/2) * _math.cos(_math.radians(TILT))

    knot = (sc.m(KNOT[0]), sc.m(KNOT[1]))
    col_a = (210,178,118) if affordable else (140,144,158)
    col_b = (150,118,70) if affordable else (100,104,118)
    _cord(surf, (gx_world, gy_world), knot, col_a, col_b, sc.m(3), sc.m(2))
    # knot nub
    pygame.draw.circle(surf, col_a, (int(knot[0]), int(knot[1])), sc.m(2))
    pygame.draw.circle(surf, (min(255,col_a[0]+40), min(255,col_a[1]+40), min(255,col_a[2]+40)),
                       (int(knot[0])-sc.m(1), int(knot[1])-sc.m(1)), max(1, sc.m(0.8)))


sc.price_chip = my_price_chip


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
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=sc.PRICE_VARIANT if affordable else "locked")
    crop = big.subsurface(pygame.Rect(0, 0, sc.m(80), sc.m(100)))
    return pygame.transform.smoothscale(crop, (160, 200))


hf = hud_font(9, True)
smf = hud_font(7)
BG = (8,8,20); CW, CH = sc.CARD_W, sc.CARD_H
PAD, GAP, HDR, LBL = 20, 12, 40, 20

cards = [
    render_card_1x("skin_mummy", True),  render_card_1x("skin_mummy", False),
    render_card_1x("skin_kitsune", True), render_card_1x("skin_kitsune", False),
]
crops = [crop2x("skin_mummy", True), crop2x("skin_mummy", False)]

W = PAD*2 + CW*4 + GAP*3
H = HDR + LBL + CH + GAP + 200 + PAD
canvas = pygame.Surface((W, H)); canvas.fill(BG)
ht = hf.render("CREAM-RULED — tl5 hang-tag round 1", True, (255,220,80))
canvas.blit(ht, (W//2 - ht.get_width()//2, (HDR-ht.get_height())//2))
labels = ["mummy aff", "mummy lock", "kitsune aff", "kitsune lock"]
for i, (card, lbl) in enumerate(zip(cards, labels)):
    x = PAD + i*(CW+GAP); y = HDR+LBL
    canvas.blit(card, (x, y))
    lt = smf.render(lbl, True, (180,176,200))
    canvas.blit(lt, (x + CW//2 - lt.get_width()//2, HDR+2))
for i, crop in enumerate(crops):
    x = PAD + i*(160+GAP); y = HDR+LBL+CH+GAP
    canvas.blit(crop, (x, y))

out = "docs/store_price_tl5/cream_ruled/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")

from PIL import Image
img = Image.open(out).convert("RGB")
print("PIL size:", img.size)
# The gold pin sits on the tilted tag near the upper-left of card 0; scan that
# window for warm metal pixels (R high, B low) to confirm the grommet renders.
found = False
for yy in range(HDR+LBL+20, HDR+LBL+50):
    for xx in range(PAD+40, PAD+72):
        r, g, b = img.getpixel((xx, yy))
        if r > 150 and r - b > 60 and g > 90:
            found = True; break
    if found: break
assert found, "grommet gold not visible in card 0"
print("verify PASS")

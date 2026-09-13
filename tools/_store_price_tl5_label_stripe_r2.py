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


def _grommet(face, gx, gy, r_out, r_bore, r_void, col_metal, col_hi, col_shadow, col_bore):
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


def _cord2(surf, p0, p1, col_a, col_b, lw):
    """Two parallel twisted strands with a gentle catenary sag between them."""
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]
    length = _math.hypot(dx, dy)
    if length < 1: return
    nx, ny = -dy/length, dx/length
    off = max(1, lw//2)
    n = max(3, int(length/sc.m(3)))
    for i in range(n):
        t0, t1 = i/n, (i+1)/n
        # Sag droops the cord mid-span so it reads as slack twine, not a wire.
        sag = _math.sin(_math.pi * (t0+t1)/2) * sc.m(2)
        for strand, (col, sign) in enumerate([(col_a, 1), (col_b, -1)]):
            sx0 = p0[0] + dx*t0 + nx*off*sign
            sy0 = p0[1] + dy*t0 + ny*off*sign + sag*0.7
            sx1 = p0[0] + dx*t1 + nx*off*sign
            sy1 = p0[1] + dy*t1 + ny*off*sign + sag
            # Alternate the two twine tones along the run for a twisted look.
            pygame.draw.line(surf, col_a if (i+strand)%2==0 else col_b,
                             (int(sx0),int(sy0)), (int(sx1),int(sy1)), max(1,off))


def _draw_price(target, text, center, col_key, col_fill_flat=None, fs=14):
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
    r = mask.get_rect(center=center)
    key = mask.copy()
    key.fill((*col_key, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = sc.m(1.5)
    for ang in [0, 90, 180, 270]:
        target.blit(key, (r.x + int(p*_math.cos(_math.radians(ang))),
                          r.y + int(p*_math.sin(_math.radians(ang)))))
    img = mask.copy()
    img.fill((*col_fill_flat, 255), special_flags=pygame.BLEND_RGBA_MULT)
    target.blit(img, r)


FACE_W, FACE_H = 68, 82
TILT = -7
TAG_CENTER = (44, 60)
KNOT = (22, 13)
GX, GY = 28, 12


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    face = pygame.Surface((sc.m(FACE_W), sc.m(FACE_H)), pygame.SRCALPHA)

    # ── body ──────────────────────────────────────────────────────────────
    if affordable:
        body = sc.vgrad_stops(sc.m(FACE_W), sc.m(FACE_H), 0,
                              [(0.0,(248,238,210)),(1.0,(224,204,166))], 255, 1.0)
    else:
        body = sc.vgrad_stops(sc.m(FACE_W), sc.m(FACE_H), 0,
                              [(0.0,(156,160,176)),(1.0,(88,92,112))], 255, 1.0)
    brect = pygame.Rect(0, 0, sc.m(FACE_W), sc.m(FACE_H))
    # This branch's bevel_rim only strokes the rim, so the body gradient has to
    # be laid down first; then emboss its edge with a dark keyline + lit rim.
    face.blit(body, (0, 0))
    sc.bevel_rim(face, brect, sc.m(3),
                 (80,52,12,200) if affordable else (48,52,64,200),
                 (255,240,190,200) if affordable else (160,164,180,200),
                 max(1, sc.m(1.2)))

    # inner border
    inset = brect.inflate(-sc.m(3), -sc.m(3))
    pygame.draw.rect(face, (196,178,148) if affordable else (120,124,140), inset, 1, border_radius=sc.m(2))

    # ── label panel ───────────────────────────────────────────────────────
    # Pulled well inside the tag so cream shows on all four sides — the label
    # reads as a paper sticker affixed to the tag, not as the tag face itself.
    label_rect = pygame.Rect(sc.m(6), sc.m(38), sc.m(FACE_W-12), sc.m(FACE_H-48))

    # Warm drop shadow peeking out bottom-right anchors the paper above the body.
    shadow_surf = pygame.Surface((label_rect.w, label_rect.h), pygame.SRCALPHA)
    shadow_surf.fill((130,100,60,100) if affordable else (40,44,56,110))
    face.blit(shadow_surf, (label_rect.x+sc.m(2), label_rect.y+sc.m(2)))

    # Draw the sticker on its own surface so it can carry a slight cockeyed tilt.
    lw, lh = label_rect.w, label_rect.h
    label_surf = pygame.Surface((lw, lh), pygame.SRCALPHA)
    lrect = pygame.Rect(0, 0, lw, lh)
    if affordable:
        pygame.draw.rect(label_surf, (252,248,240), lrect, border_radius=sc.m(1))
        pygame.draw.rect(label_surf, (180,148,80), lrect, 1, border_radius=sc.m(1))
    else:
        pygame.draw.rect(label_surf, (206,206,214), lrect, border_radius=sc.m(1))
        pygame.draw.rect(label_surf, (128,130,145), lrect, 1, border_radius=sc.m(1))
    # Light catches the top lip of an affixed sticker; the base sits in shadow.
    pygame.draw.line(label_surf, (255,253,248), (sc.m(1), 0), (lw-sc.m(1)-1, 0), 1)
    pygame.draw.line(label_surf, (140,112,72) if affordable else (96,98,110),
                     (sc.m(1), lh-1), (lw-sc.m(1)-1, lh-1), 1)

    # ── price on label ─────────────────────────────────────────────────────
    if affordable:
        _draw_price(label_surf, text, (lw//2, lh//2),
                    col_key=(16,8,2), col_fill_flat=(44,22,8), fs=14)
    else:
        _draw_price(label_surf, text, (lw//2, lh//2),
                    col_key=(80,84,100), col_fill_flat=(96,100,116), fs=14)

    # A hair of rotation sells the "stuck on by hand" paper look.
    rotated_label = pygame.transform.rotate(label_surf, 2)
    face.blit(rotated_label, rotated_label.get_rect(center=(sc.m(FACE_W//2), sc.m(57))))

    # ── grommet ────────────────────────────────────────────────────────────
    if affordable:
        _grommet(face, sc.m(GX), sc.m(GY), sc.m(6.5), sc.m(3), sc.m(2),
                 (194,152,48), (244,212,88), (60,38,8), (20,14,4))
        # Specular pip nudged onto mid-metal (off the bright arc) and brightened.
        pygame.draw.circle(face, (255,255,244),
                           (sc.m(GX)-sc.m(2), sc.m(GY)-sc.m(2)), max(1, sc.m(0.9)))
    else:
        _grommet(face, sc.m(GX), sc.m(GY), sc.m(6.5), sc.m(3), sc.m(2),
                 (78,82,96), (130,134,150), (28,30,38), (12,14,20))
        pygame.draw.circle(face, (210,214,228),
                           (sc.m(GX)-sc.m(2), sc.m(GY)-sc.m(2)), max(1, sc.m(0.9)))

    # ── rotate + blit ──────────────────────────────────────────────────────
    rotated = pygame.transform.rotate(face, -TILT)
    cx2, cy2 = sc.m(TAG_CENTER[0]), sc.m(TAG_CENTER[1])
    surf.blit(rotated, (cx2 - rotated.get_width()//2, cy2 - rotated.get_height()//2))

    # ── cord ───────────────────────────────────────────────────────────────
    fw2, fh2 = sc.m(FACE_W), sc.m(FACE_H)
    gx_world = cx2 + (sc.m(GX) - fw2/2) * _math.cos(_math.radians(TILT)) - (sc.m(GY) - fh2/2) * _math.sin(_math.radians(TILT))
    gy_world = cy2 + (sc.m(GX) - fw2/2) * _math.sin(_math.radians(TILT)) + (sc.m(GY) - fh2/2) * _math.cos(_math.radians(TILT))

    knot = (sc.m(KNOT[0]), sc.m(KNOT[1]))
    col_a = (205,185,148) if affordable else (140,144,158)
    col_b = (165,148,110) if affordable else (100,104,118)
    _cord2(surf, (gx_world, gy_world), knot, col_a, col_b, sc.m(3))
    pygame.draw.circle(surf, col_a, (int(knot[0]), int(knot[1])), sc.m(2))


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
    sc.draw_card(big, sid, rect, equipped=False, secret=False,
                 variant=sc.PRICE_VARIANT if affordable else "locked")
    crop = big.subsurface(pygame.Rect(0, 0, sc.m(80), sc.m(100)))
    return pygame.transform.smoothscale(crop, (160, 200))


hf = hud_font(9, True); smf = hud_font(7)
BG = (8,8,20); CW, CH = sc.CARD_W, sc.CARD_H
PAD, GAP, HDR = 20, 12, 40

cards = [render_card_1x("skin_mummy", True), render_card_1x("skin_mummy", False),
         render_card_1x("skin_kitsune", True), render_card_1x("skin_kitsune", False)]
crops = [crop2x("skin_mummy", True), crop2x("skin_mummy", False)]

W = PAD*2 + CW*4 + GAP*3
H = HDR + 20 + CH + GAP + 200 + PAD
canvas = pygame.Surface((W, H)); canvas.fill(BG)
ht = hf.render("LABEL-STRIPE — tl5 hang-tag round 2", True, (255,220,80))
canvas.blit(ht, (W//2 - ht.get_width()//2, (HDR-ht.get_height())//2))
labels = ["mummy aff", "mummy lock", "kitsune aff", "kitsune lock"]
for i, (card, lbl) in enumerate(zip(cards, labels)):
    x = PAD + i*(CW+GAP)
    canvas.blit(card, (x, HDR+20))
    lt = smf.render(lbl, True, (180,176,200))
    canvas.blit(lt, (x + CW//2 - lt.get_width()//2, HDR+2))
for i, crop in enumerate(crops):
    canvas.blit(crop, (PAD + i*(160+GAP), HDR+20+CH+GAP))

out = "docs/store_price_tl5/label_stripe/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")

from PIL import Image
img = Image.open(out)
print("PIL size:", img.size)
print("verify PASS")

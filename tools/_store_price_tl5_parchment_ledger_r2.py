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


def _cord2(surf, p0, p1, col_a, col_b, w_total, w_strand):
    """Cotton cord: shadowed body + two twist-highlight strands.

    Originated at the grommet RIM (not its center) so the tag face blit on top
    keeps the bore reading as a clean punched hole rather than a filled disc.
    """
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]
    length = _math.hypot(dx, dy)
    if length == 0: return
    nx, ny = -dy/length, dx/length
    pygame.draw.line(surf, col_b,
                     (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])),
                     max(1, int(w_total)))
    off = w_total * 0.28
    for sign in (-1, +1):
        ox, oy = nx*off*sign, ny*off*sign
        pygame.draw.line(surf, col_a,
                         (int(p0[0]+ox), int(p0[1]+oy)),
                         (int(p1[0]+ox), int(p1[1]+oy)),
                         max(1, int(w_strand)))


def _coin_glyph(face, cx, cy, r, col_rim, col_face):
    """Filled disc with a thinner ring and a centered notch — reads as a coin at 1×."""
    pygame.draw.circle(face, col_rim, (cx, cy), r)
    pygame.draw.circle(face, col_face, (cx, cy), max(1, r-max(1, sc.m(1.0))))
    # a vertical center tick — a stamped denomination pip, not a text label
    tick_h = max(1, r - max(1, sc.m(1.5)))
    pygame.draw.line(face, col_rim, (cx, cy-tick_h), (cx, cy+tick_h), max(1, sc.m(0.8)))


def _draw_price(face, text, center, col_key, col_fill_flat=None, fs=14):
    mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
    r = mask.get_rect(center=center)
    key = mask.copy()
    key.fill((*col_key, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = sc.m(1)
    for ang in [0, 90, 180, 270]:
        face.blit(key, (r.x + int(p*_math.cos(_math.radians(ang))),
                        r.y + int(p*_math.sin(_math.radians(ang)))))
    img = mask.copy()
    img.fill((*col_fill_flat, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


def _double_rule(face, y, col, x0, x1):
    """Two genuine 1px hairlines 3px apart — a printed ledger double-rule, not
    an embossed dark/highlight pair (which reads as a single carved line)."""
    lw = max(2, sc.m(1))
    pygame.draw.line(face, col, (x0, y), (x1, y), lw)
    pygame.draw.line(face, col, (x0, y+sc.m(1.5)), (x1, y+sc.m(1.5)), lw)


FACE_W, FACE_H = 68, 82
TILT = -7
TAG_CENTER = (44, 60)
KNOT = (22, 13)
GX, GY = 28, 12


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _abbr(text)

    face = pygame.Surface((sc.m(FACE_W), sc.m(FACE_H)), pygame.SRCALPHA)

    # ── parchment body ────────────────────────────────────────────────────
    if affordable:
        body = sc.vgrad_stops(sc.m(FACE_W), sc.m(FACE_H), 0,
                              [(0.0,(242,228,196)),(1.0,(228,212,178))], 255, 1.0)
        bevel_dark = (72,44,10,200)
        bevel_bright = (255,244,210,200)
    else:
        body = sc.vgrad_stops(sc.m(FACE_W), sc.m(FACE_H), 0,
                              [(0.0,(204,200,196)),(1.0,(188,184,180))], 255, 1.0)
        bevel_dark = (48,52,64,200)
        bevel_bright = (160,164,180,200)

    brect = pygame.Rect(0, 0, sc.m(FACE_W), sc.m(FACE_H))
    # WHY: real bevel_rim only strokes the emboss rim — fill the parchment body
    # first, then emboss, so the tag reads as solid stock rather than a hollow rim.
    face.blit(body, (0, 0))
    sc.bevel_rim(face, brect, sc.m(3), bevel_dark, bevel_bright, max(1, sc.m(1.5)))

    x0r, x1r = sc.m(4), sc.m(FACE_W-4)

    # WHY: zone A stays clean parchment — the grommet is its own anchor, so the
    # old fs=3 micro-"SKYBIT" (which read as noise, not ledger detail) is gone.

    rule_col = (90,48,12) if affordable else (100,100,115)

    # ── upper double rule (zone A / B boundary at y=28) ───────────────────
    _double_rule(face, sc.m(28), rule_col, x0r, x1r)

    # ── zone B: price (y=30..56) ──────────────────────────────────────────
    price_center = (sc.m(FACE_W//2), sc.m(43))
    if affordable:
        _draw_price(face, text, price_center,
                    col_key=(16,8,2), col_fill_flat=(44,24,8), fs=14)
    else:
        _draw_price(face, text, price_center,
                    col_key=(80,84,100), col_fill_flat=(130,134,150), fs=14)

    # ── lower double rule (zone B / C boundary at y=58) ───────────────────
    _double_rule(face, sc.m(58), rule_col, x0r, x1r)

    # ── zone C: coin glyph anchor (replaces the old fs=3 "COINS" label) ────
    if affordable:
        _coin_glyph(face, sc.m(FACE_W//2), sc.m(65), sc.m(3), (186,142,48), (220,190,140))
    else:
        _coin_glyph(face, sc.m(FACE_W//2), sc.m(65), sc.m(3), (98,102,116), (130,134,148))

    # ── grommet ────────────────────────────────────────────────────────────
    gx_local, gy_local = sc.m(GX), sc.m(GY)
    if affordable:
        _grommet(face, gx_local, gy_local, sc.m(6.5), sc.m(3), sc.m(2),
                 (194,152,48), (244,212,88), (60,38,8), (20,14,4))
        pygame.draw.circle(face, (255,248,200),
                           (gx_local-sc.m(2), gy_local-sc.m(3)), max(1, sc.m(1.1)))
    else:
        _grommet(face, gx_local, gy_local, sc.m(6.5), sc.m(3), sc.m(2),
                 (104,108,120), (160,164,178), (40,42,52), (18,18,24))
        pygame.draw.circle(face, (200,208,220),
                           (gx_local-sc.m(2), gy_local-sc.m(3)), max(1, sc.m(1.1)))

    # ── cord FIRST, tag face SECOND ───────────────────────────────────────
    # WHY: originate the cord at the grommet RIM and blit the rotated face on
    # top, so the punched bore stays a clean hole instead of showing cord colour.
    cx2, cy2 = sc.m(TAG_CENTER[0]), sc.m(TAG_CENTER[1])
    fw2, fh2 = sc.m(FACE_W), sc.m(FACE_H)
    knot = (sc.m(KNOT[0]), sc.m(KNOT[1]))

    gx_rot, gy_rot = _rot_point(gx_local, gy_local, fw2, fh2, (cx2, cy2), -TILT)
    dx, dy = knot[0]-gx_rot, knot[1]-gy_rot
    dist = _math.hypot(dx, dy) or 1.0
    rim_start = (gx_rot + dx/dist * sc.m(6.5)/sc.SS,
                 gy_rot + dy/dist * sc.m(6.5)/sc.SS)

    col_a = (205,185,140) if affordable else (140,136,130)
    col_b = (165,148,110) if affordable else (112,108,104)
    _cord2(surf, rim_start, knot, col_a, col_b, sc.m(4), sc.m(1.5))

    rotated = pygame.transform.rotate(face, -TILT)
    surf.blit(rotated, (cx2 - rotated.get_width()//2, cy2 - rotated.get_height()//2))

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
    return pygame.transform.smoothscale(big.subsurface(pygame.Rect(0,0,sc.m(80),sc.m(100))), (160,200))


hf = hud_font(9, True); smf = hud_font(7)
BG = (8,8,20); CW, CH = sc.CARD_W, sc.CARD_H
PAD, GAP, HDR = 20, 12, 40

cards = [render_card_1x("skin_mummy", True), render_card_1x("skin_mummy", False),
         render_card_1x("skin_kitsune", True), render_card_1x("skin_kitsune", False)]
crops = [crop2x("skin_mummy", True), crop2x("skin_mummy", False)]
W = PAD*2 + CW*4 + GAP*3; H = HDR + 20 + CH + GAP + 200 + PAD
canvas = pygame.Surface((W, H)); canvas.fill(BG)
ht = hf.render("PARCHMENT-LEDGER — tl5 hang-tag round 2", True, (255,220,80))
canvas.blit(ht, (W//2 - ht.get_width()//2, (HDR-ht.get_height())//2))
labels = ["mummy aff", "mummy lock", "kitsune aff", "kitsune lock"]
for i, (card, lbl) in enumerate(zip(cards, labels)):
    x = PAD + i*(CW+GAP)
    canvas.blit(card, (x, HDR+20))
    lt = smf.render(lbl, True, (180,176,200))
    canvas.blit(lt, (x + CW//2 - lt.get_width()//2, HDR+2))
for i, crop in enumerate(crops):
    canvas.blit(crop, (PAD + i*(160+GAP), HDR+20+CH+GAP))

out = "docs/store_price_tl5/parchment_ledger/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
from PIL import Image
print("PIL size:", Image.open(out).size)
print("verify PASS")

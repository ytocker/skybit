"""Round-1 exploration render for the `tag-rivet` top-left price badge.

A true swing-tag (rounded-rect enamel body, NOT the hexagonal corner-shield):
tilted, hung from a punched eyelet by a short string that runs up to the card
corner. Numerals in coin-metal, rotated with the body. Review-only sheet — not
wired into the live card path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")
import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()
m = sc.m


def _taper_string(surf, p0, p1, col, w, a0, a1, steps=16):
    """String drawn as short segments so its alpha can taper along the length
    (bright at the eyelet, fading toward the card corner)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    for i in range(steps):
        t0, t1 = i / steps, (i + 1) / steps
        a = int(a0 + (a1 - a0) * t0)
        pygame.draw.line(surf, (*col, a),
                         (p0[0] + dx * t0, p0[1] + dy * t0),
                         (p0[0] + dx * t1, p0[1] + dy * t1), w)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Tag-rivet: a rounded-rect swing tag pinned to the card's top-left corner.
    Everything is authored unrotated, then the whole body (numerals included) is
    rotated once so the type stays welded to the tag face; the eyelet + string
    are painted last, directly at the rotated corner."""
    badge_cx = m(25)          # 50 in the 2x buffer
    badge_cy = m(25)          # 50 in the 2x buffer
    affordable = (variant != "locked")

    body_w, body_h = 40, 30
    rad = m(4)                # 8
    ang = 18                  # positive -> CCW in pygame == our -18 deg tilt
    padr = 16                 # slack around the body so rotation isn't clipped

    if affordable:
        top_c, bot_c = (26, 20, 32), (18, 14, 24)
        rim_dark = (60, 44, 18, 220)
        rim_bright = (230, 200, 130, 200)
        eye_out, eye_hi, eye_lo = (170, 166, 156), (210, 206, 196), (90, 86, 76)
        str_col = (140, 130, 100)
    else:
        top_c, bot_c = (14, 15, 28), (10, 11, 22)
        rim_dark = (52, 40, 20, 210)
        rim_bright = (150, 132, 96, 180)
        eye_out, eye_hi, eye_lo = (150, 146, 136), (186, 182, 172), (96, 92, 82)
        str_col = (100, 96, 84)

    # ── unrotated tag face ────────────────────────────────────────────────
    tw, th = body_w + padr * 2, body_h + padr * 2
    tag = pygame.Surface((tw, th), pygame.SRCALPHA)
    brect = pygame.Rect(padr, padr, body_w, body_h)

    tag.blit(sc.vgrad_stops(body_w, body_h, rad, [(0.0, top_c), (1.0, bot_c)],
                            255, gamma=1.04), (padr, padr))

    # top-left gloss ellipse — a faint enamel sheen catching the corner light
    gloss = pygame.Surface((body_w, body_h), pygame.SRCALPHA)
    pygame.draw.ellipse(gloss, (255, 255, 255, 18),
                        (0, 0, int(body_w * 0.72), int(body_h * 0.66)))
    clip = pygame.Surface((body_w, body_h), pygame.SRCALPHA)
    pygame.draw.rect(clip, (255, 255, 255, 255), clip.get_rect(), border_radius=rad)
    gloss.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    tag.blit(gloss, (padr, padr), special_flags=pygame.BLEND_ADD)

    # V-notch on the right short edge so the silhouette reads as a tag, not a pill
    notch = pygame.Surface((tw, th), pygame.SRCALPHA)
    notch.fill((255, 255, 255, 255))
    ex, my_ = padr + body_w, padr + body_h // 2
    pygame.draw.polygon(notch, (0, 0, 0, 0),
                        [(ex, my_ - 6), (ex, my_ + 6), (ex - 7, my_)])
    tag.blit(notch, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # rim: dark keyline under a top-left bright bevel
    sc.bevel_rim(tag, brect, rad, rim_dark, rim_bright, w=max(1, m(1)))

    # numerals — coin-metal (affordable) / dim gold (locked), fit to the face
    f = sc.font(9)
    ncx, ncy = padr + body_w // 2, padr + body_h // 2
    if affordable:
        mask = sc._stamp_bold(sc._glyph_base(text, f, 0), m(1.0))
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        base = sc._stamp_bold(sc._glyph_base(text, f, 0), m(1.0))
        img = base.copy()
        img.fill((150, 132, 92, 255), special_flags=pygame.BLEND_RGBA_MULT)
    # keep the price inside the tag face regardless of digit count
    maxw = body_w - m(3)
    if img.get_width() > maxw:
        s = maxw / img.get_width()
        img = pygame.transform.smoothscale(
            img, (maxw, max(1, int(img.get_height() * s))))
    tag.blit(img, img.get_rect(center=(ncx, ncy)))

    # ── rotate the whole face once, blit centered on the badge zone ───────
    rot = pygame.transform.rotate(tag, ang)
    surf.blit(rot, rot.get_rect(center=(badge_cx, badge_cy)).topleft)

    # rotated position of the (unrotated) top-left body corner. pygame rotate is
    # CCW-visual; y-down maps a center-relative vector (vx,vy) to
    #   (vx*cos + vy*sin, -vx*sin + vy*cos)
    a = math.radians(ang)
    vx, vy = padr - tw / 2, padr - th / 2
    corner = (badge_cx + vx * math.cos(a) + vy * math.sin(a),
              badge_cy - vx * math.sin(a) + vy * math.cos(a))
    # nudge the eyelet a touch onto the face so the ring sits on the tag
    tocx, tocy = badge_cx - corner[0], badge_cy - corner[1]
    tl = math.hypot(tocx, tocy) or 1
    eyelet = (corner[0] + 4 * tocx / tl, corner[1] + 4 * tocy / tl)
    anchor = (m(12.5), m(10))   # ~ card top-left corner in device px

    # string first (two strands), eyelet ring over its base
    perp = (-(anchor[1] - eyelet[1]), anchor[0] - eyelet[0])
    pl = math.hypot(*perp) or 1
    ox, oy = 1.6 * perp[0] / pl, 1.6 * perp[1] / pl
    for sgn in (-1, 1):
        _taper_string(surf, (eyelet[0] + sgn * ox, eyelet[1] + sgn * oy),
                      (anchor[0] + sgn * ox, anchor[1] + sgn * oy),
                      str_col, max(1, m(1)), 120, 20)

    # eyelet — pewter ring (r5 outer, r3 clear) with a beveled edge
    er = 6
    es = pygame.Surface((er * 2 + 2, er * 2 + 2), pygame.SRCALPHA)
    c = (er + 1, er + 1)
    pygame.draw.circle(es, eye_out, c, 5, width=2)
    rc = pygame.Rect(c[0] - 5, c[1] - 5, 10, 10)
    pygame.draw.arc(es, eye_hi, rc, math.radians(45), math.radians(225), 1)
    pygame.draw.arc(es, eye_lo, rc, math.radians(225), math.radians(405), 1)
    surf.blit(es, es.get_rect(center=eyelet).topleft)


sc.price_chip = my_price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── pixel verification ────────────────────────────────────────────────────
_va = render_card_1x("skin_mummy", True)
_vl = render_card_1x("skin_mummy", False)
pa, pl = _va.get_at((25, 25)), _vl.get_at((25, 25))
# (25,25) sits on the tag's coin-metal numeral; (17,20) lands on dark enamel.
ea = _va.get_at((17, 20))
bg = _va.get_at((110, 20))     # card body, clear of the corner tag
print("verify (25,25) numeral:", tuple(pa), " locked:", tuple(pl))
print("verify (17,20) enamel:", tuple(ea), " card body (110,20):", tuple(bg))
assert tuple(pa) != tuple(pl), "affordable/locked identical at (25,25)"
assert tuple(ea) != tuple(bg), "badge enamel indistinguishable from card body"


# ── review sheet ───────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)

row1 = [
    ("skin_mummy", True, "MUMMY EPIC"),
    ("skin_mummy", False, "MUMMY EPIC (locked)"),
    ("skin_kitsune", True, "KITSUNE LEGENDARY"),
    ("skin_kitsune", False, "KITSUNE LEGENDARY (locked)"),
]
cards1 = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in row1]

crop_sz, zoom = 64, 256
crops = [
    (pygame.transform.scale(_va.subsurface((0, 0, crop_sz, crop_sz)),
                            (zoom, zoom)), "4x zoom — mummy affordable"),
    (pygame.transform.scale(_vl.subsurface((0, 0, crop_sz, crop_sz)),
                            (zoom, zoom)), "4x zoom — mummy locked"),
]

row1_w = 4 * sc.CARD_W + 3 * GAP
row2_w = 2 * zoom + GAP
sheet_w = PAD * 2 + max(row1_w, row2_w)
sheet_h = (PAD + HEADER_H + (sc.CARD_H + LABEL_H) + GAP
           + (zoom + LABEL_H) + PAD)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(22)
fl = hud_font(13)
sheet.blit(fh.render("TAG-RIVET  —  top-left swing-tag price badge  —  round 1",
                     True, (240, 224, 180)), (PAD, PAD // 2))


def _label(text, x, y, w):
    img = fl.render(text, True, (190, 196, 210))
    sheet.blit(img, (x + (w - img.get_width()) // 2, y))


y0 = PAD + HEADER_H
x = PAD
for card, lbl in cards1:
    sheet.blit(card, (x, y0))
    _label(lbl, x, y0 + sc.CARD_H + 3, sc.CARD_W)
    x += sc.CARD_W + GAP

y1 = y0 + sc.CARD_H + LABEL_H + GAP
x = PAD
for crop, lbl in crops:
    sheet.blit(crop, (x, y1))
    _label(lbl, x, y1 + zoom + 3, zoom)
    x += zoom + GAP

out = "/home/user/skybit/docs/store_price_tl_badges/tag-rivet/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")

"""Round-2 exploration render for the `tag-rivet` top-left price badge.

A true swing-tag (rounded-rect enamel body, NOT the hexagonal corner-shield):
tilted, hung from a punched rivet by a single tapered string that runs up to the
card corner. Numerals in coin-metal, rotated with the body. Review-only sheet —
not wired into the live card path.

Round-2 addresses the art-director notes: deeper V-notch + full-perimeter
keyline, a solid pewter rivet (survives smoothscale where the r3 ring blurred to
nothing), one tapered string with a knot nub, a gentler 12 deg hang, a
hue-and-value-distinct locked state, and abbreviated price text.
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
    (bright at the rivet, fading toward the card corner)."""
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
    rotated once so the type stays welded to the tag face; the rivet + string are
    painted last, directly at the rotated corner."""

    def _abbr(text):
        # A rotated tag has little face width; long prices smear, so compact them
        # (1200 -> "1.2k", 3000 -> "3k") before they ever hit the glyph mask.
        digits = ''.join(c for c in text if c.isdigit())
        if not digits:
            return text
        v = int(digits)
        if v >= 1000:
            frac = (v % 1000) // 100
            return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
        return str(v)
    text = _abbr(text)

    badge_cx = m(25)          # 50 in the 2x buffer
    badge_cy = m(25)          # 50 in the 2x buffer
    affordable = (variant != "locked")

    body_w, body_h = 40, 30
    rad = m(4)                # 8
    ang = 12                  # positive -> CCW in pygame == our -12 deg tilt
    padr = 16                 # slack around the body so rotation isn't clipped

    if affordable:
        top_c, bot_c = (26, 20, 32), (18, 14, 24)
        rim_dark = (60, 44, 18, 220)
        rim_bright = (230, 200, 130, 200)
        key_col = (220, 190, 120, 200)
        str_col = (140, 130, 100)
    else:
        # Locked reads cool + dark by value AND neutral-grey by hue, so the state
        # flip is unmistakable next to the warm affordable tag.
        top_c, bot_c = (12, 12, 18), (8, 9, 14)
        rim_dark = (52, 40, 20, 210)
        rim_bright = (150, 132, 96, 180)
        key_col = (150, 148, 158, 180)
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

    # V-notch on the right short edge so the silhouette reads as a tag, not a
    # pill — cut deep (14px) so it survives the 2x -> 1x smoothscale.
    notch = pygame.Surface((tw, th), pygame.SRCALPHA)
    notch.fill((255, 255, 255, 255))
    ex, my_ = padr + body_w, padr + body_h // 2
    pygame.draw.polygon(notch, (0, 0, 0, 0),
                        [(ex, my_ - 6), (ex, my_ + 6), (ex - 14, my_)])
    tag.blit(notch, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # rim: dark keyline under a top-left bright bevel …
    sc.bevel_rim(tag, brect, rad, rim_dark, rim_bright, w=max(1, m(1)))
    # … then a continuous 1px bright keyline on ALL four rounded sides so the tag
    # separates from the card body on every edge, not just the lit corner.
    pygame.draw.rect(tag, key_col, brect, width=1, border_radius=rad)

    # numerals — coin-metal (affordable) / neutral grey (locked), fit to the face
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
        img.fill((138, 134, 130, 255), special_flags=pygame.BLEND_RGBA_MULT)
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
    # nudge the rivet a touch onto the face so it sits on the tag
    tocx, tocy = badge_cx - corner[0], badge_cy - corner[1]
    tl = math.hypot(tocx, tocy) or 1
    eyelet = (corner[0] + 4 * tocx / tl, corner[1] + 4 * tocy / tl)
    anchor = (m(12), m(9))      # ~ card top-left corner in device px

    # single tapered string, bright at the rivet -> faint at the corner, capped
    # with a knot nub where it ties off into the card body
    _taper_string(surf, eyelet, anchor, str_col, 2, 200, 40)
    pygame.draw.circle(surf, str_col, anchor, 2)

    # solid pewter rivet — a hollow r3 ring blurred to nothing at 1x, so this is
    # a filled high-contrast dot inside a 1px dark ring instead.
    eye_i = (int(round(eyelet[0])), int(round(eyelet[1])))
    pygame.draw.circle(surf, (60, 56, 50), eye_i, 5, 1)
    pygame.draw.circle(surf, (210, 206, 196), eye_i, 4)


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


def _num_r(card):
    """Peak red channel over the numeral strokes on the tag face. The enamel
    sheen and the bright keyline are near-white/light on both states, so pixels
    whose darkest channel is bright are skipped — what's left is the coin-metal
    (warm, blue-starved) vs. neutral-grey glyph fill the hue flip must separate."""
    best = 0
    for yy in range(22, 29):
        for xx in range(23, 32):
            r, g, b = card.get_at((xx, yy))[:3]
            if min(r, g, b) > 170:      # gloss / keyline highlight, not a glyph
                continue
            best = max(best, r)
    return best


ra, rl = _num_r(_va), _num_r(_vl)
bg = _va.get_at((110, 20))     # card body, clear of the corner tag
print("verify numeral peak-R affordable:", ra, " locked:", rl,
      " delta:", ra - rl)
print("verify card body (110,20):", tuple(bg))
assert ra - rl > 40, f"affordable/locked numerals not hue-distinct (dR={ra-rl})"


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
sheet.blit(fh.render("TAG-RIVET  —  top-left swing-tag price badge  —  round 2",
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

out = "/home/user/skybit/docs/store_price_tl_badges/tag-rivet/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")

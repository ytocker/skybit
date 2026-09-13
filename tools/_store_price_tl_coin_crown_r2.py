"""Round-2 render sheet for the `coin-crown` store-card price badge.

The price badge IS a struck round COIN at the card's top-left corner: a warm
sovereign disc whose milled/reeded RIM (short radial ticks) makes it read
unmistakably as a coin — not a gem — with the price numerals as the struck field
that dominates the interior. Affordability is carried by the coin metal itself:
warm sovereign gold when the player can pay, tarnished pewter-gold when locked.
A minimal 3-stud crownlet on the top of the coin is the only flourish.

Round-2 changes over round_1 (art-director notes):
  * Dark-ink keyline struck BEHIND the gold numerals so the price stops being
    gold-on-gold and reads with real contrast.
  * Prices abbreviated ("1,100" -> "1.1k") so 5-char numbers fit the disc big.
  * Reeding coarsened from ~40 to 14 ticks (each barely legible at 1x) and the
    crownlet promoted to 3 fat studs so both survive the 2x downscale.
  * Coin silhouette broken away from the gem sibling: the top 3 tick positions
    are notched blank AND the body hue is pushed to warm amber (not gold-gem).
  * Locked numeral pushed to cool grey to widen the state gap on the pewter body.

Implemented as a monkey-patch of store_cards.price_chip: the coin is struck at a
FIXED top-left anchor (50,50 in the 2x author buffer) rather than the passed
bottom-chip centre, so the price migrates to the corner medallion and the default
bottom chip is skipped. Review-only tooling — never imported by the game.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font

sd.load()


# ── coin-crown palette ────────────────────────────────────────────────────────
# Warm AMBER struck-coin field — pushed off the gold-gem hue so the badge reads
# as sovereign metal, never a purple-tinted EPIC gem body.
BODY_AFFORD = [(0.0, (240, 200, 100)), (1.0, (190, 150, 60))]
BODY_LOCKED = [(0.0, (150, 140, 104)), (1.0, (112, 100, 70))]

# Reeded ticks + keyline + bevel + crownlet. Locked drops to a single dim pewter.
REED_AFFORD = (168, 124, 52)
KEY_AFFORD = (110, 80, 30)
BEVEL_AFFORD = (255, 246, 210, 235)
CROWN_AFFORD = (196, 152, 72)

REED_LOCKED = (120, 108, 78)
KEY_LOCKED = (74, 68, 50)
BEVEL_LOCKED = (200, 190, 160, 175)
CROWN_LOCKED = (120, 108, 78)

# Dark ink struck under the numerals so gold sits on a defined edge, not on gold.
NUM_INK = (60, 40, 10, 255)

# Locked numeral = cool grey so the price separates from the warm pewter field.
LOCK_NUM = (130, 120, 90)


def _coin_gloss(surf, cx, cy, r, peak):
    """A soft top-left specular on the struck field. Authored as rgb=alpha discs
    (so a plain RGB add follows the falloff instead of blowing the metal white),
    then multiplied by the coin mask so the add can't leak past the rim."""
    d = r * 2
    gloss = pygame.Surface((d, d), pygame.SRCALPHA)
    gx, gy = int(r * 0.60), int(r * 0.52)
    layers = 12
    for k in range(layers, 0, -1):
        rr = int(r * 0.98 * k / layers)
        a = int(peak * (1 - (k - 1) / layers) ** 1.8)
        if rr <= 0 or a <= 0:
            continue
        pygame.draw.circle(gloss, (a, a, a, 255), (gx, gy), rr)
    cmask = pygame.Surface((d, d), pygame.SRCALPHA)
    cmask.fill((0, 0, 0, 255))
    pygame.draw.circle(cmask, (255, 255, 255, 255), (r, r), r)
    gloss.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(gloss, (cx - r, cy - r), special_flags=pygame.BLEND_ADD)


def _reeded_rim(surf, cx, cy, r, tick_col, n=14, notch=True):
    """Milled/reeded edge: 14 coarse radial ticks (r-6 -> r in the 2x buffer, so
    each is ~3px wide at 1x — just legible) stepped around the circumference. The
    top 3 tick positions are notched blank to break the pure-circle silhouette so
    the disc reads as a struck COIN, not a gem."""
    r_in = r - sc.m(3)
    top = -math.pi / 2
    skip = {0, 1, n - 1} if notch else set()      # tick 0 lands at top; skip it + neighbours
    for i in range(n):
        if i in skip:
            continue
        ang = top + 2 * math.pi * i / n
        c, s = math.cos(ang), math.sin(ang)
        pygame.draw.line(surf, tick_col,
                         (cx + r_in * c, cy + r_in * s),
                         (cx + r * c, cy + r * s), max(1, sc.m(1.5)))


def _crownlet(surf, cx, cy, r, col):
    """Minimal 3-stud crown seated just below the notched top of the coin — fat
    studs (radius m(2)) so the one decorative flourish survives the downscale."""
    top = -math.pi / 2
    rr = r * 0.72
    for da in (-0.34, 0.0, 0.34):
        ang = top + da
        px = int(round(cx + rr * math.cos(ang)))
        py = int(round(cy + rr * math.sin(ang)))
        pygame.draw.circle(surf, col, (px, py), sc.m(2))


def _numerals(surf, cx, cy, text, affordable, r):
    """Large price numerals as the struck field — font(11), sovereign-gradient
    fill when affordable / cool grey when locked. A dark-ink copy is struck one
    px down-right BEHIND the numerals so gold-on-gold gains a defined struck edge
    and the price is clearly legible. Anything wider than the clear inner field
    is scaled to fit so the numerals dominate without touching the reeded band."""
    digits = sum(ch.isdigit() for ch in text)
    size = 11 if digits <= 2 else 9.5
    track = -sc.m(0.75) if digits >= 3 else 0
    f = sc.font(size)
    mask = sc._stamp_bold(sc._glyph_base(text, f, track), sc.m(1.0))

    max_w, max_h = 2 * (r - 6), 2 * (r - 8)
    w, h = mask.get_size()
    scale = min(max_w / w, max_h / h, 1.0)
    if scale < 1.0:
        mask = pygame.transform.smoothscale(mask, (max(1, int(w * scale)),
                                                    max(1, int(h * scale))))

    if affordable:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img = mask.copy()
        img.fill((*LOCK_NUM, 255), special_flags=pygame.BLEND_RGBA_MULT)

    # dark struck edge one px down-right BEHIND the numerals so they never sit
    # gold-on-gold — the fix that makes the price legible
    ink = mask.copy()
    ink.fill(NUM_INK, special_flags=pygame.BLEND_RGBA_MULT)
    rect = img.get_rect(center=(cx, cy))
    surf.blit(ink, ink.get_rect(center=(cx + sc.m(1), cy + sc.m(1))))
    surf.blit(img, rect)


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    def _abbr(txt):
        digits = ''.join(c for c in txt if c.isdigit())
        if not digits:
            return txt
        v = int(digits)
        if v >= 1000:
            frac = (v % 1000) // 100
            return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
        return str(v)

    text = _abbr(text)

    badge_cx = sc.m(25)                     # = 50 in the 2x buffer
    badge_cy = sc.m(25)                     # = 50 in the 2x buffer
    badge_r = sc.m(11)                      # = 22
    affordable = (variant != "locked")

    body = BODY_AFFORD if affordable else BODY_LOCKED
    reed = REED_AFFORD if affordable else REED_LOCKED
    key = KEY_AFFORD if affordable else KEY_LOCKED
    bevel = BEVEL_AFFORD if affordable else BEVEL_LOCKED
    crown = CROWN_AFFORD if affordable else CROWN_LOCKED

    # soft seat shadow so the coin reads as an object pressed onto the card
    sh = pygame.Surface((badge_r * 2 + sc.m(6), badge_r * 2 + sc.m(6)),
                        pygame.SRCALPHA)
    for i in range(sc.m(3), 0, -1):
        a = int(90 * (i / sc.m(3)) ** 1.6 / sc.m(3) * 2.2)
        pygame.draw.circle(sh, (0, 0, 0, a),
                           (sh.get_width() // 2, sh.get_height() // 2),
                           badge_r + i)
    surf.blit(sh, (badge_cx - sh.get_width() // 2 + sc.m(1),
                   badge_cy - sh.get_height() // 2 + sc.m(1)))

    # struck body — one continuous vertical metal gradient masked to the disc
    disc = sc.vgrad_stops(badge_r * 2, badge_r * 2, badge_r, body, 255, gamma=1.05)
    surf.blit(disc, (badge_cx - badge_r, badge_cy - badge_r))
    _coin_gloss(surf, badge_cx, badge_cy, badge_r, peak=72 if affordable else 34)

    # numerals dominate the interior, struck BEFORE the rim so the reeding frames
    _numerals(surf, badge_cx, badge_cy + sc.m(0.5), text, affordable, badge_r)

    # milled edge + defined keyline + top-left bright bevel + crownlet flourish
    _reeded_rim(surf, badge_cx, badge_cy, badge_r, reed)
    pygame.draw.circle(surf, key, (badge_cx, badge_cy), badge_r, max(1, sc.m(0.8)))
    arc = pygame.Rect(badge_cx - badge_r + 1, badge_cy - badge_r + 1,
                      2 * (badge_r - 1), 2 * (badge_r - 1))
    pygame.draw.arc(surf, bevel, arc, math.pi * 0.52, math.pi * 1.12,
                    max(1, sc.m(1)))
    _crownlet(surf, badge_cx, badge_cy, badge_r, crown)

    # keep the API contract: return a rect for the migrated coin footprint
    return pygame.Rect(badge_cx - badge_r, badge_cy - badge_r,
                       badge_r * 2, badge_r * 2)


sc.price_chip = my_price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── pixel verification (fail loud before saving a broken sheet) ───────────────
def _verify():
    aff = render_card_1x("skin_mummy", affordable=True)
    lock = render_card_1x("skin_mummy", affordable=False)
    # sample the LEFT coin body/reed (radius ~9px at 1x) — numerals never reach
    # there, so the check stays stable across abbreviation changes
    ca = aff.get_at((16, 25))
    cl = lock.get_at((16, 25))
    assert ca[0] > 150 and (ca[0], ca[1], ca[2]) != (8, 8, 20), \
        f"affordable badge body not warm: {tuple(ca)}"
    assert (ca[0], ca[1], ca[2]) != (cl[0], cl[1], cl[2]), \
        f"locked body did not differ from affordable: {tuple(ca)} vs {tuple(cl)}"
    print(f"verify OK  afford_body={tuple(ca)}  locked_body={tuple(cl)}")


# ── sheet ─────────────────────────────────────────────────────────────────────
def _label(surf, txt, x, y, size=14, col=(210, 214, 230)):
    f = pygame.font.Font(None, size)
    surf.blit(f.render(txt, True, col), (x, y))


def build_sheet():
    BG = (8, 8, 20)
    PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
    CW, CH = sc.CARD_W, sc.CARD_H
    ZW = 256

    row1 = [
        ("skin_mummy", True, "MUMMY EPIC · afford"),
        ("skin_mummy", False, "MUMMY EPIC · locked"),
        ("skin_kitsune", True, "KITSUNE LEG · afford"),
        ("skin_kitsune", False, "KITSUNE LEG · locked"),
    ]
    row1_w = 4 * CW + 3 * GAP
    row2_w = 2 * ZW + GAP
    content_w = max(row1_w, row2_w)
    canvas_w = content_w + 2 * PAD
    canvas_h = (PAD + HEADER_H + LABEL_H + CH + GAP + LABEL_H + ZW + PAD)

    sheet = pygame.Surface((canvas_w, canvas_h))
    sheet.fill(BG)
    _label(sheet, "coin-crown — round 2 — top-left struck-coin price badge",
           PAD, PAD, size=22, col=(240, 200, 100))

    # row 1 — full cards
    y_label1 = PAD + HEADER_H
    y_card1 = y_label1 + LABEL_H
    x0 = PAD + (content_w - row1_w) // 2
    for i, (sid, aff, cap) in enumerate(row1):
        x = x0 + i * (CW + GAP)
        _label(sheet, cap, x, y_label1)
        sheet.blit(render_card_1x(sid, affordable=aff), (x, y_card1))

    # row 2 — 4x zoom crops of the top-left badge area (x 0..64, y 0..64 in 1x)
    y_label2 = y_card1 + CH + GAP
    y_crop2 = y_label2 + LABEL_H
    crops = [
        (render_card_1x("skin_mummy", affordable=True), "4× badge · afford"),
        (render_card_1x("skin_mummy", affordable=False), "4× badge · locked"),
    ]
    x0b = PAD + (content_w - row2_w) // 2
    for i, (card, cap) in enumerate(crops):
        x = x0b + i * (ZW + GAP)
        crop = card.subsurface(pygame.Rect(0, 0, 64, 64)).copy()
        sheet.blit(pygame.transform.smoothscale(crop, (ZW, ZW)), (x, y_crop2))
        _label(sheet, cap, x, y_label2)

    return sheet


def main():
    _verify()
    sheet = build_sheet()
    out = "/home/user/skybit/docs/store_price_tl_badges/coin-crown/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    w, h = sheet.get_size()
    print(f"saved {w}x{h} → {out}")


if __name__ == "__main__":
    main()

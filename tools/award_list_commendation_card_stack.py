"""commendation-card-stack — the unlock notice as a premium gilt CARD STACK.

Three full-width navy commendation plates stack vertically, each a flat 2-D
graphic inset (NOT a volumetric trophy shelf): a `rounded_rect_grad` navy plate
wearing a BRIGHT gold hairline DOUBLE-rule frame, a subtle inner bevel, and a
darker recessed inner well so the value reads deep. Per card: the real
`draw_badge` seated in a left circular gold-ringed medallion socket, NAME (gold
bold) over DESCRIPTION (pale) to its right, and a small gold corner-ribbon tab.

The premium read comes from restraint + value depth, not chrome: a thin
double-rule keeps the gilt elegant rather than gaudy, and the NEWEST (top) card
is the focal — slightly larger, a brighter rim, a soft `blit_glow` halo, and a
drop-shadow gap below it as if it just landed on the stack. Scratch tooling
only; game/ is untouched.
"""
import os
import math
import pygame

from tools.unlock_notice_common import demo_varied_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, rounded_rect_grad, lerp_color
from game.hud import (_font, _outlined_text, _pill_btn, _draw_overlay_stars,
                      _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _PANEL_DARK,
                      _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H

ids = demo_varied_ids(3)
items = [(ach.BY_ID[i].icon_key, ach.BY_ID[i].title, ach.BY_ID[i].desc)
         for i in ids]

# Card value palette — a genuine navy range so the plate has minted depth
# rather than flat-web uniformity: a lit upper plate, a shadowed base, and a
# darker recessed inner well the badge + text sit inside.
_PLATE_TOP   = (30, 22, 70)     # lit top of the navy plate
_PLATE_BOT   = (13, 8, 40)      # shadowed base
_WELL_TOP    = (18, 12, 50)     # recessed inner well, lit edge
_WELL_BOT    = (8, 4, 28)       # recessed inner well, shadowed base
_RULE_BRIGHT = (255, 224, 150)  # outer hairline of the gilt double-rule
_RULE_DEEP   = (150, 104, 26)   # inner hairline of the gilt double-rule
_BEVEL_HI    = (70, 54, 130)    # inner bevel catch-light (upper-left)
_BEVEL_LO    = (6, 3, 22)       # inner bevel shadow (lower-right)


def _backdrop():
    """Deep-night field with a soft top-down vignette + a scatter of twinkles —
    the same gold-on-navy night the menus live in, so the stack reads as part of
    the game rather than a default web sheet."""
    surf = pygame.Surface((W, H))
    # Vertical night gradient, slightly lifted in the upper third where the
    # headline sits so the title has a touch more air around it.
    top = (16, 10, 44)
    mid = (10, 5, 30)
    bot = (5, 2, 18)
    for y in range(H):
        t = y / (H - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(surf, c, (0, y), (W - 1, y))
    # A dim, optional summary "ghost" — a faint centred plaque outline low on the
    # field so the player feels the run summary waiting behind the notice.
    ghost = pygame.Rect(40, H - 86, W - 80, 56)
    gs = pygame.Surface(ghost.size, pygame.SRCALPHA)
    pygame.draw.rect(gs, (*_PANEL_LIGHTER, 40), (0, 0, ghost.w, ghost.h),
                     border_radius=14)
    pygame.draw.rect(gs, (*_GOLD_DEEP, 50), (0, 0, ghost.w, ghost.h),
                     width=1, border_radius=14)
    surf.blit(gs, ghost.topleft)
    # Twinkle field (deterministic), denser up top behind the headline.
    stars = []
    rng = 1234567
    for i in range(46):
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        x = rng % W
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        y = (rng % (H * 7 // 10))
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        r = 1 + (rng % 2)
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        ph = (rng % 628) / 100.0
        stars.append((x, y, r, ph))
    _draw_overlay_stars(surf, stars, 0.6)
    return surf


def _corner_ribbon(surf, rect, bright):
    """A small gilt corner-ribbon tab hanging from inside the card's top-right —
    a flat heraldic ribbon flag (swallowtail notch + a fold shadow at the top)
    so the plate reads as an awarded commendation, not a generic web card. Tucked
    a few px inside the gilt frame so it never floats detached off the edge."""
    w = 18
    h = 26
    x = rect.right - w - 14
    y = rect.top + 1
    hi = _GOLD_PALE if bright else _GOLD_BRIGHT
    lo = _GOLD_DEEP
    # ribbon body with a swallowtail bottom notch
    body = [
        (x, y), (x + w, y),
        (x + w, y + h),
        (x + w // 2, y + h - 7),
        (x, y + h),
    ]
    pygame.draw.polygon(surf, lo, body)
    # lit left face — the fold catching the upper-left light
    face = [
        (x, y), (x + w * 2 // 3, y),
        (x + w * 2 // 3, y + h - 5),
        (x + w // 2, y + h - 9),
        (x, y + h - 2),
    ]
    pygame.draw.polygon(surf, hi, face)
    pygame.draw.polygon(surf, _RULE_DEEP, body, 1)
    # a single engraved pip on the ribbon
    pygame.draw.circle(surf, lo, (x + w // 2, y + 10), 2)


def _card(surf, rect, icon_key, name, desc, newest=False):
    """One flat 2-D gilt commendation plate. Construction, outside-in:
    drop-shadow gap, soft halo (newest only), navy plate gradient, gilt
    DOUBLE-rule frame, inner bevel, recessed inner well, then the medallion
    socket + text + corner ribbon."""
    # Drop-shadow gap beneath the card so each plate reads as a separate inset
    # sitting on the stack; deeper + offset more on the newest, lifted card.
    sh_off = 12 if newest else 5
    sh_a = 170 if newest else 90
    sh = pygame.Surface((rect.w + 12, rect.h + 12), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, sh_a), (6, 6, rect.w, rect.h),
                     border_radius=16)
    sh = pygame.transform.smoothscale(
        pygame.transform.smoothscale(sh, ((rect.w + 12) // 2, (rect.h + 12) // 2)),
        (rect.w + 12, rect.h + 12))
    surf.blit(sh, (rect.x - 6, rect.y - 6 + sh_off))

    if newest:
        # Soft warm halo hugging the BASE of the freshest plate — the "it just
        # landed" heat pooling where it meets the stack. Pushed below the card
        # centre + kept low-alpha so it reads as a landing bloom, never a sun
        # disc washing up over the headline.
        blit_glow(surf, rect.centerx, rect.bottom + 6,
                  int(rect.w * 0.26), (255, 190, 92), 34)

    radius = 16
    # Navy plate with real top-lit / base-shadow value depth.
    plate_top = lerp_color(_PLATE_TOP, _GOLD_DEEP, 0.05) if newest else _PLATE_TOP
    rounded_rect_grad(surf, rect, radius, plate_top, _PLATE_BOT)

    # Gilt DOUBLE-rule frame: a bright outer hairline + a deep inner hairline a
    # couple px in, the restrained two-line gold edge that reads premium. The
    # newest card's outer rule runs brighter + a touch thicker.
    out_w = 2 if newest else 1
    pygame.draw.rect(surf, _RULE_BRIGHT if newest else _GOLD_BRIGHT,
                     rect, width=out_w, border_radius=radius)
    inner = rect.inflate(-6, -6)
    pygame.draw.rect(surf, _RULE_DEEP, inner, width=1,
                     border_radius=max(4, radius - 4))

    # Inner bevel: a single upper-left catch-light arc + lower-right shadow arc
    # just inside the frame, so the plate face reads slightly raised (struck),
    # not a flat fill.
    bev = rect.inflate(-3, -3)
    pygame.draw.arc(surf, _BEVEL_HI, bev, math.radians(40), math.radians(210),
                    2)
    pygame.draw.arc(surf, _BEVEL_LO, bev, math.radians(210), math.radians(400),
                    2)

    # Recessed inner WELL — a darker sunk panel the badge + text sit inside, so
    # the card has a clear figure/ground depth instead of one flat tone.
    well = pygame.Rect(rect.x + 10, rect.y + 10, rect.w - 20, rect.h - 20)
    rounded_rect_grad(surf, well, 11, _WELL_TOP, _WELL_BOT)
    # thin dark recess keyline + a faint lit top edge on the well lip
    pygame.draw.rect(surf, _BEVEL_LO, well, width=1, border_radius=11)
    pygame.draw.line(surf, (*_BEVEL_HI, 0) if False else _BEVEL_HI,
                     (well.x + 6, well.y + 1), (well.right - 6, well.y + 1), 1)

    # Left medallion SOCKET — a circular gold-ringed seat the badge drops into,
    # so the badge reads as set INTO the plate, not pasted on top.
    sock_d = rect.h - 26
    sock_cx = rect.x + 18 + sock_d // 2
    sock_cy = rect.centery
    # sunk socket disc
    pygame.draw.circle(surf, _WELL_BOT, (sock_cx, sock_cy), sock_d // 2 + 3)
    pygame.draw.circle(surf, (4, 2, 16), (sock_cx, sock_cy),
                       sock_d // 2 + 3, 2)
    # gold socket ring (double hairline echoing the frame)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (sock_cx, sock_cy),
                       sock_d // 2 + 2, 2)
    pygame.draw.circle(surf, _GOLD_DEEP, (sock_cx, sock_cy),
                       sock_d // 2 + 5, 1)
    badge_d = sock_d
    brect = pygame.Rect(0, 0, badge_d, badge_d)
    brect.center = (sock_cx, sock_cy)
    a = ach.BY_ID[ids[items.index((icon_key, name, desc))]]
    draw_badge(surf, icon_key, brect, True, a.hidden)

    # NAME (gold bold) over DESCRIPTION (pale, smaller), right of the socket.
    text_x = sock_cx + sock_d // 2 + 14
    name_size = 19 if newest else 18
    nf = _font(name_size, True)
    # engrave the name: deep shadow + gold face
    nsh = nf.render(name, True, _PANEL_DARK)
    nimg = nf.render(name, True, _GOLD_PALE if newest else _GOLD_BRIGHT)
    name_y = rect.centery - 13
    surf.blit(nsh, (text_x + 1, name_y + 1))
    surf.blit(nimg, (text_x, name_y))
    # hairline gold underline rule tying name to its description column —
    # sized to the name width so it reads as an accent under the title, not a
    # divider spanning the whole card.
    rule_w = nimg.get_width() + 6
    ry = name_y + nimg.get_height() + 3
    pygame.draw.line(surf, _GOLD_DEEP, (text_x, ry), (text_x + rule_w, ry), 1)
    df = _font(12, True)
    dimg = df.render(desc, True, (198, 188, 220))
    surf.blit(dimg, (text_x, ry + 5))

    _corner_ribbon(surf, rect, newest)


def _headline(surf):
    """Centred gold-outlined headline + a thin gold underline-rule split around
    a small '×3' count chip, so the player instantly reads 'three at once'. The
    rule + chip share one baseline so the title group reads as a single
    engraved crest rather than three stacked elements."""
    cy = 40
    # Sized to clear the 360px frame with margin so EARNED! never kisses the edge.
    _outlined_text(surf, "ACHIEVEMENT EARNED!", (W // 2, cy), 19,
                   shadow_offset=(2, 3))

    # "x3" count chip — a gilt pill centred on the rule baseline; the underline
    # rule runs out to either side of it like a heraldic divider.
    chip_f = _font(13, True)
    label = "x%d" % len(items)
    cimg = chip_f.render(label, True, _NIGHT_DEEP)
    cw = cimg.get_width() + 14
    ch = cimg.get_height() + 5
    ry = cy + 18
    chip = pygame.Rect(0, 0, cw, ch)
    chip.center = (W // 2, ry)

    rule_half = 92
    gap = cw // 2 + 7
    for sgn in (-1, 1):
        x0 = W // 2 + sgn * gap
        x1 = W // 2 + sgn * rule_half
        pygame.draw.line(surf, _GOLD_DEEP, (x0, ry), (x1, ry), 2)
        pygame.draw.line(surf, _GOLD_PALE, (x0, ry - 1), (x1, ry - 1), 1)
        # a small diamond finial closing each rule end
        pygame.draw.polygon(surf, _GOLD_BRIGHT,
                            [(x1, ry - 3), (x1 + sgn * 4, ry), (x1, ry + 3),
                             (x1 - sgn * 4, ry)])

    rounded_rect_grad(surf, chip, ch // 2, _GOLD_PALE, _GOLD_BRIGHT)
    pygame.draw.rect(surf, _GOLD_DEEP, chip, width=1, border_radius=ch // 2)
    surf.blit(cimg, cimg.get_rect(center=chip.center))


def _compose(out_name):
    surf = _backdrop()
    _headline(surf)

    # Three full-width cards stacked vertically. The NEWEST (top) is slightly
    # larger; the gaps let each drop-shadow read.
    cw = 330
    top_y = 84
    gap = 14
    big_h = 116          # newest, lifted card
    h = 104              # the two settled cards below
    # Newest first (top), then the two it landed on.
    rects = []
    y = top_y
    for k in range(3):
        ch = big_h if k == 0 else h
        # newest sits a hair wider so it visibly overhangs the stack
        cwk = cw if k != 0 else cw
        rx = (W - cwk) // 2
        rects.append((pygame.Rect(rx, y, cwk, ch), k == 0))
        y += ch + gap

    for (rect, newest), (icon, name, desc) in zip(rects, items):
        _card(surf, rect, icon, name, desc, newest=newest)

    # TAP-to-continue: centred gold primary pill handing off to the summary.
    _pill_btn(surf, (W // 2, H - 40), "TAP TO CONTINUE", size=17,
              primary=True, wide=True)

    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice", "award_list",
                       "commendation-card-stack")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, out_name)
    pygame.image.save(surf, path)
    return path


if __name__ == "__main__":
    print(_compose("round_1.png"))

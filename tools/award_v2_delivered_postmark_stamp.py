"""Mockup: the `delivered-postmark-stamp` award-interstitial concept — an ink
POSTMARK thunks down at a jaunty angle and FRAMES the hero medallion, like a
sorting-office cancel stamp hitting your dispatch the instant it's commended.

The design intent the still must sell: the GOLD BADGE stays the brightest, hero
object with a CLEAN, untouched face; the postmark is a SEMI-TRANSPARENT
desaturated-navy stamp struck across the badge's lower RIM and the surrounding
NAVY at ~-12°, so it FRAMES the medallion rather than burying it — earned +
delivered in the same beat without muddying the gold. The impact frame: radial
ink-spatter in the navy, a double-ring shock, and a faint descent-smear ghost.
Multiplicity = a "+1" overstrike serial + a 2-unlock line.

Scratch tooling only — nothing here is imported by the game; `game/` untouched.
"""
import os
import math
import random
import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, lerp_color
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H
from game.entities import Particle, PoofGrain


# Desaturated NAVY-BLACK ink for the whole stamp — deliberately NOT scarlet, so
# the postmark never fights the gold for the eye. A real cancellation stamp is
# greasy black; a faint cool tint keeps it sitting in the navy world.
_INK_DEEP = (16, 18, 34)
_INK_MID  = (30, 34, 58)
_INK_DRY  = (52, 58, 88)   # the patchy, under-inked edges of a hand stamp


def _radial_vignette(surf, cx, cy, inner_r, outer_r, edge_col):
    """Deep-navy vignette that darkens toward the corners and pulls the eye to
    the medallion. Painted big-to-small so each smaller (more central) ring is
    LESS opaque — the centre stays clear, the corners go near-black. Cheap and
    identical on both build targets (no per-pixel surface locks)."""
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    maxd = math.hypot(max(cx, W - cx), max(cy, H - cy))
    step = 2
    for r in range(int(maxd), 0, -step):
        t = max(0.0, (r - inner_r) / max(1, outer_r - inner_r))
        a = int(252 * min(1.0, t) ** 1.25)
        if a <= 0:
            continue
        pygame.draw.circle(vig, (*edge_col, a), (cx, cy), r, step + 1)
    surf.blit(vig, (0, 0))


def _arced_text(stamp, txt, cx, cy, radius, size, color, top=True,
                spread_deg=150.0, alpha=255):
    """Lay each glyph on its own small surface, rotate it tangent to the rim,
    and place it around the circle. SHORT + LARGE so it stays legible at 1× —
    a full ring of tiny type would read as noise at 360px. ``top`` arcs the
    word across the upper rim reading left-to-right; otherwise the lower rim."""
    f = _font(size, True)
    n = len(txt)
    if n == 0:
        return
    spread = math.radians(spread_deg)
    # centre the word on 12 o'clock (top) or 6 o'clock (bottom).
    base = -math.pi / 2 if top else math.pi / 2
    step = spread / max(1, n - 1)
    start = base - spread / 2
    for i, ch in enumerate(txt):
        ang = start + step * i
        glyph = f.render(ch, True, color)
        if alpha < 255:
            glyph.set_alpha(alpha)
        # baseline faces the centre: top text rotates so it reads upright along
        # the top; bottom text flips 180° so it reads upright along the bottom.
        rot = -math.degrees(ang) - 90 if top else -math.degrees(ang) + 90
        g = pygame.transform.rotate(glyph, rot)
        gx = cx + math.cos(ang) * radius
        gy = cy + math.sin(ang) * radius
        # a faint pale halo behind each glyph so the dark ink reads against the
        # dim run-summary ghost — the page the stamp is printed on.
        halo = _font(size, True).render(ch, True, (235, 232, 245))
        halo.set_alpha(70)
        halo = pygame.transform.rotate(halo, rot)
        stamp.blit(halo, halo.get_rect(center=(gx, gy)))
        stamp.blit(g, g.get_rect(center=(gx, gy)))


def _build_postmark(R, badge_r=None):
    """Render the postmark onto its OWN square SRCALPHA surface so it can be
    rotated as one rigid stamp and blitted semi-transparent. The stamp is built
    to FRAME a badge — its rim text + cancel banner live on the LOWER half so,
    when struck low over the medallion, the badge FACE stays clear of ink.

    Construction = a real cancellation stamp: concentric ink rings, SHORT bold
    arced text on the lower rim, a hard cancel banner across the lower third
    carrying "DELIVERED ★ COMMENDED", and date dots. Drawn with a patchy,
    slightly-broken line so it reads as INK on paper, not vector.

    ``badge_r`` (if given, in stamp-surface px) marks the protected medallion
    disc so any ink that would fall on the badge's bright upper face is erased —
    the gold stays the single brightest object."""
    S = R * 2
    stamp = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = cy = R

    rim_r = int(R * 0.92)

    # ── concentric ink rings (the classic double rim) — drawn in arc segments
    # with tiny gaps so the ring looks INKED BY HAND, never a clean CAD circle.
    def inked_ring(radius, width, col, gaps=22, jitter=2):
        seg = math.tau / gaps
        for k in range(gaps):
            a0 = k * seg + random.uniform(0.02, 0.05)
            a1 = (k + 1) * seg - random.uniform(0.02, 0.06)
            rr = radius + random.randint(-jitter, jitter)
            rect = pygame.Rect(cx - rr, cy - rr, rr * 2, rr * 2)
            pygame.draw.arc(stamp, col, rect, a0, a1, width)

    inked_ring(rim_r, 4, _INK_MID, gaps=26, jitter=1)
    inked_ring(int(R * 0.86), 2, _INK_DEEP, gaps=30, jitter=1)

    # ── arced rim text: SHORT + LARGE, high contrast against the navy page. Both
    # words ride the LOWER rim so they wrap UNDER the badge, never across its
    # face. A pale halo behind each glyph lifts the ink off the dim summary. ──
    _arced_text(stamp, "COURIER'S COMMENDATION", cx, cy, int(R * 0.80), 15,
                _INK_DEEP, top=False, spread_deg=176)
    # star separators flanking the lower rim text (≈4 & 8 o'clock)
    for ang in (math.radians(34), math.radians(146)):
        sx = cx + math.cos(ang) * int(R * 0.80)
        sy = cy + math.sin(ang) * int(R * 0.80)
        _ink_star(stamp, sx, sy, 7, _INK_DEEP)

    # ── the cancel banner: a horizontal ink bar carrying the short, bold
    # payload, struck across the LOWER THIRD so it lands on the badge rim + the
    # navy below, NOT across the glyph/face. Type is knocked OUT of the banner
    # so anything bright behind it shows through the words. ──
    bar_h = int(R * 0.40)
    bar_w = int(R * 1.62)
    bar_cy = cy + int(R * 0.66)        # push the banner down off the face
    band = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
    for y in range(bar_h):
        edge = abs(y - bar_h / 2) / (bar_h / 2)           # 0 mid → 1 edge
        a = int(214 * (1.0 - 0.22 * edge))
        if random.random() < 0.05:                        # dry-out gaps
            a = int(a * 0.45)
        pygame.draw.line(band, (*_INK_MID, a), (0, y), (bar_w, y))
    # keyline top & bottom for crisp typographic snap
    pygame.draw.line(band, _INK_DEEP, (0, 0), (bar_w, 0), 2)
    pygame.draw.line(band, _INK_DEEP, (0, bar_h - 1), (bar_w, bar_h - 1), 2)
    # punch "DELIVERED" + star + "COMMENDED" OUT of the banner.
    bf = _font(19, True)
    word = bf.render("DELIVERED", True, (255, 255, 255))
    band.blit(word, word.get_rect(center=(bar_w // 2 - 20, bar_h // 2)),
              special_flags=pygame.BLEND_RGBA_SUB)
    cf = _font(10, True)
    cw = cf.render("COMMENDED", True, (255, 255, 255))
    band.blit(cw, cw.get_rect(center=(bar_w // 2 + 54, bar_h // 2)),
              special_flags=pygame.BLEND_RGBA_SUB)
    _knock_star_local(band, bar_w // 2 + 40, bar_h // 2, 6)
    stamp.blit(band, (cx - bar_w // 2, bar_cy - bar_h // 2))

    # date-stamp dots flanking the banner ends, like a postmark's day/month
    for dx in (-bar_w // 2 + 6, bar_w // 2 - 6):
        pygame.draw.circle(stamp, _INK_DEEP, (cx + dx, bar_cy), 3)

    # ── PROTECT THE FACE: erase any ink that fell on the badge's bright upper
    # disc, so the gold medallion reads CLEAN and the stamp only ever frames it
    # from the rim + navy. Subtractive on the stamp's own alpha. ──
    if badge_r:
        guard = pygame.Surface((S, S), pygame.SRCALPHA)
        # protect the whole face + most of the rim; only the very bottom edge
        # catches ink, so the cancel banner reads as struck BELOW the medallion.
        pygame.draw.circle(guard, (255, 255, 255, 255), (cx, cy - int(R * 0.04)),
                           int(badge_r * 1.02))
        stamp.blit(guard, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    return stamp


def _ink_star(surf, x, y, r, col):
    """A small 4-point ink star (rim separator) — drawn as two crossed spokes
    plus a centre dot, matte ink (no glow)."""
    pygame.draw.line(surf, col, (x - r, y), (x + r, y), 2)
    pygame.draw.line(surf, col, (x, y - r), (x, y + r), 2)
    pygame.draw.line(surf, col, (x - r * 0.6, y - r * 0.6),
                     (x + r * 0.6, y + r * 0.6), 1)
    pygame.draw.line(surf, col, (x - r * 0.6, y + r * 0.6),
                     (x + r * 0.6, y - r * 0.6), 1)
    pygame.draw.circle(surf, col, (int(x), int(y)), 2)


def _knock_star_local(surf, x, y, r):
    """A 4-point star knocked OUT of the ink banner (subtractive on the banner's
    own alpha), so the bright badge shows through — a real cancel-mark star."""
    star = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = r + 2
    pts = []
    for i in range(8):
        ang = math.pi / 2 + i * math.pi / 4
        rad = r if i % 2 == 0 else r * 0.40
        pts.append((c + math.cos(ang) * rad, c - math.sin(ang) * rad))
    pygame.draw.polygon(star, (255, 255, 255, 255), pts)
    surf.blit(star, (int(x - c), int(y - c)), special_flags=pygame.BLEND_RGBA_SUB)


def _gold_text(surf, txt, center, size):
    """Gold engraved title: navy drop shadow under a top-lit gold fill with a
    pale upper sheen — matches the menu's gold-on-navy engraving."""
    f = _font(size, True)
    sh = f.render(txt, True, _NIGHT_DEEP)
    sh.set_alpha(200)
    surf.blit(sh, sh.get_rect(center=(center[0] + 2, center[1] + 3)))
    body = f.render(txt, True, _GOLD_BRIGHT)
    r = body.get_rect(center=center)
    surf.blit(body, r)
    sheen = f.render(txt, True, _GOLD_PALE)
    sheen.set_alpha(120)
    surf.blit(sheen, (r.x, r.y - 1))
    return r


def _shock_ring(surf, cx, cy, r, width, col, alpha):
    """A thin expanding shock ring from the impact — additive light, so it
    blooms outward from where the stamp struck without a hard edge."""
    ring = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.circle(ring, (*col, alpha), (cx, cy), r, width)
    surf.blit(ring, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def build():
    random.seed(7)   # deterministic ink texture for a stable review still
    ids = demo_ids(2)
    a0 = ach.BY_ID[ids[0]]

    surf = pygame.Surface((W, H))

    # ── 1. Dim run-summary ghost under everything: the ceremony sits in front
    # of the score it's about to hand back to. ──
    base = render_backdrop().copy()
    base.set_alpha(20)
    surf.fill(_NIGHT_DEEP)
    surf.blit(base, (0, 0))

    cx, cy = W // 2, int(H * 0.44)

    # ── 2. Vignette + low wash to pin focus on the strike zone. ──
    _radial_vignette(surf, cx, cy, inner_r=58, outer_r=int(H * 0.42),
                     edge_col=_NIGHT_DEEP)
    low = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(low, (*_PANEL_DARK, 130), (0, int(H * 0.70), W, H))
    surf.blit(low, (0, 0))

    R = 60                 # medallion radius → ~120px badge (the anchor)
    PR = int(R * 1.40)     # postmark radius — frames the badge from rim + navy
    # the badge disc, in postmark-surface pixels — used as the face guard so the
    # stamp's ink is erased off the bright medallion.
    BADGE_R_IN_STAMP = R

    # ── 3. Warm halo + the HERO badge first, so the stamp lands ON it. The gold
    # stays the brightest object in frame; everything else is navy ink. ──
    blit_glow(surf, cx, cy, int(R * 1.40), (255, 196, 96), 70)
    blit_glow(surf, cx, cy, int(R * 1.00), (255, 222, 142), 95)
    badge_rect = pygame.Rect(cx - R, cy - R, R * 2, R * 2)
    draw_badge(surf, a0.icon_key, badge_rect, True, False)

    # ── 4. MULTIPLICITY: a SECOND, fainter stamp already landed a touch higher
    # & off-angle (the run popped two unlocks) — the overstrike serial reads
    # "+1" on the live stamp. This faint ghost sells the stack. ──
    ghost = _build_postmark(PR, badge_r=BADGE_R_IN_STAMP)
    ghost = pygame.transform.rotozoom(ghost, 18, 1.0)
    ghost.set_alpha(60)
    gr = ghost.get_rect(center=(cx + 16, cy + 4))
    surf.blit(ghost, gr)

    # ── 5. DESCENT SMEAR: a faint motion-ghost of the live stamp a few px above
    # its final rest, streaked, so the strike reads as kinetic (it just hit). ──
    smear_src = _build_postmark(PR, badge_r=BADGE_R_IN_STAMP)
    smear = pygame.transform.rotozoom(smear_src, 12, 1.0)
    for dy, a in ((-26, 24), (-16, 36), (-8, 54)):
        gh = smear.copy()
        gh.set_alpha(a)
        surf.blit(gh, gh.get_rect(center=(cx, cy + dy)))

    # ── 6. THE LIVE POSTMARK — slammed down at ~-12°, SEMI-TRANSPARENT, FRAMING
    # the gold from its lower rim + the navy. The face guard keeps the medallion
    # itself clean, so the two read as one struck unit without muddying the gold.
    stamp = _build_postmark(PR, badge_r=BADGE_R_IN_STAMP)
    stamp = pygame.transform.rotozoom(stamp, 12, 1.0)   # +12 visual = jaunty CCW
    stamp.set_alpha(200)
    surf.blit(stamp, stamp.get_rect(center=(cx, cy)))

    # ── 6b. RE-ASSERT THE HERO: the badge face is already clear of ink, but a
    # crisp re-blit of the FULL medallion + a warm core glow guarantees the gold
    # is unmistakably the single brightest, highest-contrast object in frame. ──
    blit_glow(surf, cx, cy, int(R * 0.78), (255, 224, 152), 88)
    draw_badge(surf, a0.icon_key, badge_rect, True, False)

    # ── 7. IMPACT: a double shock ring + radial ink-spatter flung from the
    # strike point. Dark specks are drawn directly (additive black = invisible),
    # bright dust uses Particle/PoofGrain for the few catch-light flecks. ──
    _shock_ring(surf, cx, cy, int(PR * 1.02), 3, (210, 200, 235), 90)
    _shock_ring(surf, cx, cy, int(PR * 1.20), 2, (160, 150, 200), 55)

    # flung ink: matte navy specks radiating out, denser near the rim, with a
    # few long "thrown" streaks — the splat of a stamp hitting wet ink.
    spatter = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(90):
        ang = random.uniform(0, math.tau)
        d = PR * random.uniform(0.96, 1.55)
        x = cx + math.cos(ang) * d
        y = cy + math.sin(ang) * d
        rr = random.choice((1, 1, 2, 2, 3))
        col = random.choice((_INK_DEEP, _INK_MID, _INK_DRY))
        a = random.randint(120, 220)
        pygame.draw.circle(spatter, (*col, a), (int(x), int(y)), rr)
        # occasional thrown streak trailing back toward the centre
        if rr >= 2 and random.random() < 0.45:
            x2 = cx + math.cos(ang) * (d - random.uniform(6, 16))
            y2 = cy + math.sin(ang) * (d - random.uniform(6, 16))
            pygame.draw.line(spatter, (*col, int(a * 0.7)),
                             (x, y), (x2, y2), 1)
    surf.blit(spatter, (0, 0))

    # a handful of bright impact flecks (the gold dust knocked loose) — additive
    impact = []
    for _ in range(26):
        ang = random.uniform(0, math.tau)
        sp = random.uniform(120, 320)
        impact.append(Particle(cx, cy, math.cos(ang) * sp, math.sin(ang) * sp,
                               life=0.5, r=random.uniform(1.5, 3.0),
                               color=(255, 224, 150), gravity=0))
        impact.append(PoofGrain(cx, cy, math.cos(ang) * sp * 0.6,
                                math.sin(ang) * sp * 0.6, life=0.6,
                                size=random.uniform(1.5, 2.5),
                                color=(255, 240, 200)))
    # advance them a few frames so they sit out at the rim, not piled at centre
    for p in impact:
        for _ in range(7):
            p.update(1 / 60)
        p.draw(surf)

    # ── 8. SERIAL OVERSTRIKE: the "+1" inked at the lower-right of the live
    # stamp — the postmark's own little count of how many landed this run. ──
    serf = _font(20, True)
    sx, sy = cx + int(PR * 0.62), cy + int(PR * 0.60)
    # tiny ink chip behind it so the serial reads as PART of the stamp
    chip = pygame.Surface((34, 24), pygame.SRCALPHA)
    pygame.draw.rect(chip, (*_INK_DEEP, 210), (0, 0, 34, 24), border_radius=5)
    chip = pygame.transform.rotozoom(chip, 12, 1.0)
    surf.blit(chip, chip.get_rect(center=(sx, sy)))
    serial = serf.render("+1", True, (240, 238, 250))
    serial = pygame.transform.rotozoom(serial, 12, 1.0)
    surf.blit(serial, serial.get_rect(center=(sx, sy)))

    # ── 9. Gold title block beneath — kept in the _GOLD_* family so the badge's
    # commendation, not the ink, owns the warm light. ──
    ty = cy + PR + 40
    _gold_text(surf, "COMMENDATION EARNED", (cx, ty - 26), 15)
    pygame.draw.line(surf, _GOLD_DEEP, (cx - 96, ty - 13), (cx + 96, ty - 13), 1)
    _gold_text(surf, a0.title.upper(), (cx, ty + 12), 30)
    fdesc = _font(15, True)
    d = fdesc.render(a0.desc, True, (210, 196, 232))
    d.set_alpha(220)
    surf.blit(d, d.get_rect(center=(cx, ty + 40)))

    # multiplicity readout in words: "2 COMMENDATIONS DELIVERED"
    mf = _font(13, True)
    mt = mf.render("2 COMMENDATIONS DELIVERED THIS RUN", True, _GOLD_PALE)
    mt.set_alpha(200)
    surf.blit(mt, mt.get_rect(center=(cx, ty + 62)))

    # ── 10. TAP TO CONTINUE — the skip affordance, pinned bottom. ──
    tap = _font(15, True)
    tt = tap.render("TAP TO CONTINUE", True, _GOLD_BRIGHT)
    pill_w, pill_h = tt.get_width() + 32, 28
    pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
    pygame.draw.rect(pill, (*_PANEL_LIGHTER, 200), (0, 0, pill_w, pill_h),
                     border_radius=14)
    pygame.draw.rect(pill, (*_GOLD_BRIGHT, 150), (0, 0, pill_w, pill_h),
                     width=1, border_radius=14)
    py2 = int(H * 0.93)
    surf.blit(pill, pill.get_rect(center=(cx, py2)))
    surf.blit(tt, tt.get_rect(center=(cx, py2)))

    return surf


def main():
    surf = build()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice",
                       "award_interstitial_v2", "delivered-postmark-stamp")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "round_2.png")
    pygame.image.save(surf, path)
    print(path)


if __name__ == "__main__":
    main()

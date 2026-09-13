"""GRIM SPROUT — chibi Skybit Death boss, take #1 (the tiny reaper-imp).

A roly-poly knee-high BABY reaper dragging a great-scythe FIVE TIMES his height:
menace through comedy of scale. Drawn in the Skybit chibi house style — FLAT
saturated fills, 1-2px hard ink keylines, the dark-core -> fill -> top-left
sheen triad (ported from `_marotte_ruff`), supersampled then smoothscaled for
crisp AA, with a grown 1px silhouette outline so the imp pops on any sky.

The whole identity is the EXTREME prop-to-body ratio (AD guardrail #1): the
blade dwarfs the imp. The scythe stacks TALL and near-VERTICAL above a TINY
imp, so the instant 1x read is "huge blade, tiny baby under it." The straight
SNATH is the tileable vertical PILLAR post; the curved blade is a detachable
GAP-EDGE flourish ONLY, so a top/bottom mirror reads as one matched obstacle
and the blade never bleeds into the tiling body.

Headless review renderer — not shipped. Imports the real game helpers so the
finish matches house style.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame

from game.draw import _shade_c, lerp_color, blit_glow  # noqa: F401
from game.config import PIPE_W

# ── GRIM SPROUT palette ("candy-poison": orchid-violet + mint) ───────────────
HOOD       = (123,  79, 216)   # #7B4FD8 orchid-violet
HOOD_DK    = ( 78,  46, 150)   # #4E2E96 shade
HOOD_HI    = (169, 140, 242)   # #A98CF2 sheen
MINT       = ( 57, 224, 196)   # #39E0C4 belly / trim
MINT_DK    = _shade_c(MINT, -60)
MINT_HI    = _shade_c(MINT, 55)
BONE       = (255, 243, 194)   # #FFF3C2 claws / teeth / cream-bone
BONE_DK    = _shade_c(BONE, -70)
EYE_GOLD   = (255, 225,  74)   # #FFE14A glow-gold pinprick eyes
WOOD       = (176, 122,  58)   # #B07A3A warm-wood snath
WOOD_DK    = _shade_c(WOOD, -55)
WOOD_HI    = _shade_c(WOOD, 55)
BLADE      = (236, 232, 214)   # bone-flat scythe blade
# Spine is darkened well below the day-sky bottom value so the blade keeps its
# silhouette on a bright sky (AD directive #2) instead of melting into it.
BLADE_DK   = _shade_c(BLADE, -120)
BLADE_LIT  = (255, 255, 235)   # 1px lit inner cutting edge
BLADE_RIM  = ( 42, 196, 178)   # mint under-rim along the cutting edge for value pop
INK        = ( 28,  22,  30)   # #1C1620 hard keyline


def _triad_circle(surf, cx, cy, r, col, ss):
    """The house FORM recipe: a dark-core ring, the flat fill, and a ~1/3-radius
    top-left sheen — flat shapes that read sculpted without any gradient. Ported
    straight from `_marotte_ruff` so the imp matches the clown anchor's finish."""
    pygame.draw.circle(surf, _shade_c(col, -55), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), max(2, int(r - ss)))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - r * 0.32), int(cy - r * 0.32)),
                       max(1, int(r * 0.34)))


def _add_outline(src, outline_color=(28, 22, 30, 235)):
    """Grow a 1px dark outline from the alpha mask so the imp keeps a black-shape
    silhouette on any sky (the parrot `_add_outline` recipe)."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _great_blade(surf, bx, by, span, rise, ink_w, ss):
    """The signature GREAT-SCYTHE crescent — long and wide so it dwarfs the imp.
    A true sweeping scythe: from the socket it sweeps UP+LEFT, arcs over the top,
    then curls back DOWN to a hooked point, so the inner cutting edge is a deep
    concave crescent. Bone fill with a heavy ink keyline (load-bearing edge at
    1x), a darkened spine, and a mint under-rim along the cutting edge so the
    blade holds its silhouette against BOTH skies (AD directive #2)."""
    # The cutting edge is a quarter-ellipse sweep from the socket up and over to a
    # hooked tip; the spine rides outside it, the gap between the two being the
    # blade width (broadest at the heel, tapering to the point).
    inner = []     # concave cutting edge
    outer = []     # blunt spine
    n = 34
    for i in range(n):
        t = i / (n - 1.0)
        a = t * (math.pi * 0.62)                  # sweep through ~112 deg of arc
        # Cutting edge: socket at right, arcing up + left over the top.
        ix = bx - span * math.sin(a)
        iy = by - rise * (1 - math.cos(a))
        inner.append((ix, iy))
        # Blade width tapers heel->tip; spine offset outward (up/left) from edge.
        wdt = (1 - t) ** 0.85 * (rise * 0.46) + ss * 1.3
        ox = ix - wdt * math.sin(a + math.pi * 0.18)
        oy = iy - wdt * math.cos(a + math.pi * 0.18)
        outer.append((ox, oy))
    blade = outer + list(reversed(inner))
    pygame.draw.polygon(surf, BLADE, blade)
    pygame.draw.polygon(surf, INK, blade, ink_w)
    pygame.draw.lines(surf, BLADE_DK, False, outer, max(2, int(2.6 * ss)))   # dark spine
    pygame.draw.lines(surf, BLADE_RIM, False, inner, max(2, int(2.2 * ss)))  # mint under-rim
    pygame.draw.lines(surf, BLADE_LIT, False,
                      [(x, y + ss) for x, y in inner], max(1, int(1.4 * ss)))  # lit edge


# ── the imp + his oversized scythe ───────────────────────────────────────────

def build_grim_sprout(scale=1.0, ss=3):
    """Render the imp + great-scythe onto a tight transparent surface, then add a
    grown outline. Coordinates are in supersampled space; the body is sized SMALL
    and the scythe DELIBERATELY tall + near-vertical so the prop-to-body ratio
    reads as roughly 4-5x (AD directive #1).

    Returns a smoothscaled surface whose width fits the splayed blade."""
    # Tall + wide surface: the scythe stacks far above a tiny imp, and the great
    # blade sweeps wide LEFT across the top, so the canvas must hold the crescent
    # in-frame. The imp sits LOW and small; the snath stands nearly upright.
    BW = int(250 * scale * ss)
    BH = int(420 * scale * ss)
    s = pygame.Surface((BW, BH), pygame.SRCALPHA)

    # Tiny imp, anchored low. Body deliberately small vs the prop.
    body_cx = int(BW * 0.55)
    feet_y = int(BH * 0.955)
    hood_r = int(34 * scale * ss)              # small head, but big enough to carry a face
    belly_r = int(20 * scale * ss)

    # ── 1. THE GREAT-SCYTHE (drawn first so the imp's mitts overlap the snath) ──
    # The snath stands NEAR-VERTICAL (only a slight lean), running from the imp's
    # grip all the way to a HIGH socket near the top — the pole alone is far
    # taller than the imp, and the blade dwarfs him again on top of that.
    # Snath nudged ~3px right (in 1x terms) so the near-vertical pole runs cleanly
    # BESIDE the head silhouette rather than kissing the lower-right of the face
    # crescent — the "held beside the head" read (final polish #1).
    snath_top = (int(BW * 0.635), int(BH * 0.205))
    snath_bot = (int(BW * 0.735), feet_y - int(2 * scale * ss))
    sw = int(8 * scale * ss)
    pygame.draw.line(s, WOOD_DK, snath_top, snath_bot, sw + max(2, int(3 * ss)))
    pygame.draw.line(s, WOOD, snath_top, snath_bot, sw)
    # A top-left lit edge running the pole (offset perpendicular to its lean).
    dx, dy = snath_bot[0] - snath_top[0], snath_bot[1] - snath_top[1]
    plen = math.hypot(dx, dy) or 1
    nx, ny = -dy / plen, dx / plen            # pole normal
    off = int(2 * scale * ss)
    pygame.draw.line(s, WOOD_HI,
                     (snath_top[0] - nx * off, snath_top[1] - ny * off),
                     (snath_bot[0] - nx * off, snath_bot[1] - ny * off),
                     max(1, int(2 * ss)))
    # Banded grip wraps where his mitts will close — also the pillar-banding cue.
    for t in (0.70, 0.84):
        bxp = int(snath_top[0] + dx * t)
        byp = int(snath_top[1] + dy * t)
        pygame.draw.circle(s, WOOD_DK, (bxp, byp), max(3, int(6 * scale * ss)))
        pygame.draw.circle(s, BONE, (bxp, byp), max(2, int(4 * scale * ss)))
        pygame.draw.circle(s, BONE_DK, (bxp, byp), max(2, int(4 * scale * ss)),
                           max(1, int(ss)))

    # The BLADE: a great curved bone hook arcing UP + ACROSS from the snath top —
    # sized BIG (span/rise roughly doubled vs r1) so the crescent clearly dwarfs
    # the imp. Heavy ink keyline + dark spine + mint under-rim hold it on any sky.
    bx, by = snath_top[0], snath_top[1] + int(4 * scale * ss)
    _great_blade(s, bx, by,
                 span=int(168 * scale * ss),
                 rise=int(132 * scale * ss),
                 ink_w=max(3, int(3.4 * ss)), ss=ss)
    # Socket collar where the blade meets the snath top (mint trim to tie palette).
    _triad_circle(s, bx, by, int(8 * scale * ss), MINT, ss)
    pygame.draw.circle(s, INK, (int(bx), int(by)), int(8 * scale * ss), max(1, int(ss)))

    # ── 2. STUB FEET poking out the bottom (2 bolder claws each, drops at 1x) ───
    for fs, fx_off in ((-1, -13), (1, 11)):
        fx = body_cx + int(fx_off * scale * ss)
        fy = feet_y
        fr = int(10 * scale * ss)
        _triad_circle(s, fx, fy, fr, HOOD, ss)
        # 2 bolder ink-cored claw stubs per foot (fine 3-claw detail dropped — it
        # was sub-pixel noise at 1x per the critique).
        for k in (-1, 1):
            ca = math.radians(90 + k * 24)
            cx2 = fx + math.cos(ca) * fr * 0.5
            cy2 = fy + fr * 0.65
            tip = (cx2 + math.cos(ca) * fr * 0.7, cy2 + fr * 0.8)
            pygame.draw.line(s, INK, (int(cx2), int(cy2)),
                             (int(tip[0]), int(tip[1])), max(3, int(3.4 * ss)))
            pygame.draw.line(s, BONE, (int(cx2), int(cy2)),
                             (int(tip[0]), int(tip[1])), max(2, int(2.0 * ss)))

    # ── 3. BELLY NUB (mint) overlapping under the hood ──────────────────────────
    belly_cy = feet_y - belly_r - int(5 * scale * ss)
    _triad_circle(s, body_cx, belly_cy, belly_r, MINT, ss)

    # ── 4. THE HOOD — one big orchid lobe flopping forward to a clear droop-tip ─
    hood_cy = belly_cy - belly_r - int(1 * scale * ss)
    _triad_circle(s, body_cx, hood_cy, hood_r, HOOD, ss)
    # The droop: a fat lobe peeling off the hood's TOP and flopping forward to a
    # rounded tip with a mint pom — drawn as a chunky tapered tube so it reads as
    # an oversized floppy hood, not a head lump (AD secondary note).
    curl = []
    cseg = 14
    for i in range(cseg):
        t = i / (cseg - 1)
        # Arc up off the crown then flop forward + down toward the face side.
        ccx = body_cx - hood_r * 0.1 + math.sin(t * math.pi * 0.9) * hood_r * 1.35
        ccy = (hood_cy - hood_r * 0.95) + t * hood_r * 0.55 \
            - math.sin(t * math.pi) * hood_r * 0.30
        rr = hood_r * (0.50 - 0.30 * t)        # tapers to the tip
        curl.append((ccx, ccy, max(2.0, rr)))
    for (ccx, ccy, rr) in curl:
        pygame.draw.circle(s, HOOD_DK, (int(ccx), int(ccy)), max(2, int(rr)))
    for (ccx, ccy, rr) in curl:
        pygame.draw.circle(s, HOOD, (int(ccx), int(ccy)), max(2, int(rr - ss)))
    # Top-left sheen run along the droop's upper edge so it reads as a lit tube.
    for (ccx, ccy, rr) in curl[:cseg // 2]:
        pygame.draw.circle(s, HOOD_HI, (int(ccx - rr * 0.3), int(ccy - rr * 0.3)),
                           max(1, int(rr * 0.34)))
    # Mint pom-bobble at the very droop-tip (charming, ties palette up top).
    ttx, tty, _ = curl[-1]
    _triad_circle(s, ttx, tty, int(6 * scale * ss), MINT, ss)

    # ── 5. THE FACE — a bold dark FACE crescent w/ socket scallops, cute tilted ─
    #        gold eyes + ONE oversized offset fang. The dark shape (not the gold
    #        hue) carries the read in grayscale (AD directive #3 + accessibility).
    fcx, fcy = body_cx, hood_cy + int(4 * scale * ss)
    cav_r = int(hood_r * 0.82)
    cav = pygame.Surface((cav_r * 2 + 6, cav_r * 2 + 6), pygame.SRCALPHA)
    ccx0, ccy0 = cav_r + 3, cav_r + 3
    pygame.draw.circle(cav, INK, (ccx0, ccy0), cav_r)
    # Bulge two round eye-sockets UP into the dark field so the shadow reads as a
    # FACE (sockets + grin), not a flat black bar — these notches are what make
    # the dark crescent legible as a face when shrunk. Sockets sit high so the
    # gold eyes ride near the top of the shadow (cute, eyes-forward).
    sock_dx = int(cav_r * 0.44)
    pygame.draw.circle(cav, INK, (ccx0 - sock_dx, ccy0 - int(cav_r * 0.34)),
                       int(cav_r * 0.42))
    pygame.draw.circle(cav, INK, (ccx0 + sock_dx, ccy0 - int(cav_r * 0.46)),
                       int(cav_r * 0.42))
    # Crop the very top so it sits as a hood-shadow crescent, not a full hole.
    pygame.draw.rect(cav, (0, 0, 0, 0), (0, 0, cav_r * 2 + 6, int(cav_r * 0.42)))
    s.blit(cav, (int(fcx - ccx0), int(fcy - ccy0)))
    # Two glowing gold eyes with a CUTE upward asymmetric tilt: the left eye sits
    # a touch lower + smaller, the right higher + larger, so the read is a cheeky
    # baby, not a symmetric glower. Glow first so the dark socket carries grayscale.
    eyes = (  # (x_frac, y_frac, radius_frac)
        (-0.44, -0.30, 0.28),
        (0.44, -0.42, 0.38),
    )
    for exf, eyf, erf in eyes:
        ex = int(fcx + exf * cav_r)
        ey = int(fcy + eyf * cav_r)
        blit_glow(s, ex, ey, int(7 * scale * ss), EYE_GOLD, 150)
    for exf, eyf, erf in eyes:
        ex = int(fcx + exf * cav_r)
        ey = int(fcy + eyf * cav_r)
        er = max(2, int(erf * cav_r))
        pygame.draw.circle(s, EYE_GOLD, (ex, ey), er)
        pygame.draw.circle(s, (255, 255, 255),
                           (ex - int(er * 0.34), ey - int(er * 0.34)),
                           max(1, int(er * 0.42)))
    # ONE oversized cream FANG offset to the imp's left of center, poking UP over
    # the hood-shadow lip — the scary-cute signature beat, now bold + legible.
    fangx = fcx - int(cav_r * 0.22)
    fangy = fcy + int(cav_r * 0.34)
    fang_w = int(8 * scale * ss)
    fang_h = int(19 * scale * ss)
    fang = [(fangx - fang_w, fangy), (fangx + fang_w, fangy),
            (fangx + int(fang_w * 0.2), fangy - fang_h)]
    pygame.draw.polygon(s, BONE, fang)
    pygame.draw.polygon(s, INK, fang, max(2, int(2.0 * ss)))

    # ── 6. STUB MITT ARMS — one UP (closed fist high), one BRACING low ──────────
    # The pose body-languages "hauling a weapon way too big": a high reach with a
    # closed fist and a low brace, the two mitts deliberately differentiated.
    # High grip dropped a touch down the snath (0.66 -> 0.70) so the closed fist
    # clears the cheek and reads "fist on pole," not "fist on face" (polish #2).
    up_grip = (int(snath_top[0] + dx * 0.70), int(snath_top[1] + dy * 0.70))
    lo_grip = (int(snath_top[0] + dx * 0.84), int(snath_top[1] + dy * 0.84))
    sh_l = (body_cx + int(2 * scale * ss), belly_cy - int(8 * scale * ss))   # up shoulder
    sh_r = (body_cx + int(14 * scale * ss), belly_cy + int(4 * scale * ss))  # low shoulder
    # Upper arm reaches high + thin (a stretch); lower arm is a short fat brace.
    pygame.draw.line(s, HOOD_DK, sh_l, up_grip, int(11 * scale * ss))
    pygame.draw.line(s, HOOD, sh_l, up_grip, int(8 * scale * ss))
    pygame.draw.line(s, HOOD_DK, sh_r, lo_grip, int(15 * scale * ss))
    pygame.draw.line(s, HOOD, sh_r, lo_grip, int(12 * scale * ss))
    # The HIGH mitt is a closed fist (trimmed a hair, 10 -> 9, so it doesn't crowd
    # the cheek); the LOW mitt is a smaller brace pad.
    _triad_circle(s, up_grip[0], up_grip[1], int(9 * scale * ss), BONE, ss)
    pygame.draw.circle(s, INK, up_grip, int(9 * scale * ss), max(1, int(ss)))
    # A knuckle-line on the high fist to read as a clenched grip.
    pygame.draw.line(s, BONE_DK,
                     (up_grip[0] - int(6 * scale * ss), up_grip[1] - int(3 * scale * ss)),
                     (up_grip[0] + int(6 * scale * ss), up_grip[1] - int(3 * scale * ss)),
                     max(1, int(1.6 * ss)))
    _triad_circle(s, lo_grip[0], lo_grip[1], int(7 * scale * ss), BONE, ss)
    pygame.draw.circle(s, INK, lo_grip, int(7 * scale * ss), max(1, int(ss)))

    s = _add_outline(s)
    # Supersample down for crisp AA. Final display size ~ the build / ss.
    fw = max(1, s.get_width() // ss)
    fh = max(1, s.get_height() // ss)
    return pygame.transform.smoothscale(s, (fw, fh))


# ── prop -> pillar mirror: the snath is a tileable vertical post ─────────────

def draw_snath_pillar_cap(surf, cx, top, bot, w, ss, *, flip):
    """The TOP CAP pier: the snath post runs the full height, the curved blade
    rides the GAP-EDGE (inner end) ONLY as a hooked crescent flourishing INTO the
    gap. `flip=True` draws the bottom pier as a vertical mirror so a top/bottom
    pair reads as one matched obstacle. The blade is detachable to the gap-edge so
    the repeatable mid-post (below) tiles cleanly with no blade in it."""
    work = surf
    if flip:
        # Render into a scratch surface flipped vertically so the same blade math
        # lands at the bottom pier's gap-edge.
        h = surf.get_height()
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        draw_snath_pillar_cap(tmp, cx, h - bot, h - top, w, ss, flip=False)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        return

    # Full-height bone-banded wood post, dark-cored + top-left lit edge.
    pygame.draw.line(work, WOOD_DK, (cx, top), (cx, bot), w + max(2, int(3 * ss)))
    pygame.draw.line(work, WOOD, (cx, top), (cx, bot), w)
    pygame.draw.line(work, WOOD_HI, (cx - int(2 * ss), top), (cx - int(2 * ss), bot),
                     max(1, int(2 * ss)))
    # Binding collars band the post (mint + bone) so it reads as a worked snath.
    span = bot - top
    for fr in (0.30, 0.62):
        cy = int(top + span * fr)
        _triad_circle(work, cx, cy, max(4, int(7 * ss)), MINT, ss)
        pygame.draw.circle(work, INK, (cx, cy), max(4, int(7 * ss)), max(1, int(ss)))

    # GAP-EDGE blade flourish at the inner (here TOP) end ONLY — bigger crescent
    # to match the boss, with the same dark-spine + mint under-rim legibility fix.
    gap_y = top
    _great_blade(work, cx, gap_y + int(2 * ss),
                 span=int(96 * ss), rise=int(74 * ss),
                 ink_w=max(3, int(3.0 * ss)), ss=ss)
    _triad_circle(work, cx, gap_y + int(4 * ss), max(4, int(6 * ss)), MINT, ss)


def draw_snath_pillar_mid(surf, cx, top, bot, w, ss):
    """The REPEATABLE MID segment: pure banded post, NO blade — proves the body
    tiles cleanly because the blade is a detachable gap-flourish."""
    pygame.draw.line(surf, WOOD_DK, (cx, top), (cx, bot), w + max(2, int(3 * ss)))
    pygame.draw.line(surf, WOOD, (cx, top), (cx, bot), w)
    pygame.draw.line(surf, WOOD_HI, (cx - int(2 * ss), top), (cx - int(2 * ss), bot),
                     max(1, int(2 * ss)))
    span = bot - top
    for fr in (0.22, 0.5, 0.78):
        cy = int(top + span * fr)
        _triad_circle(surf, cx, cy, max(4, int(7 * ss)), MINT, ss)
        pygame.draw.circle(surf, INK, (cx, cy), max(4, int(7 * ss)), max(1, int(ss)))


# ── sheet composition ────────────────────────────────────────────────────────

def _sky_panel(w, h, night):
    """The game's real biome day/night keyframes, so legibility is judged on the
    actual backdrop the boss must read on."""
    surf = pygame.Surface((w, h))
    if night:
        top, bot = (5, 8, 30), (35, 55, 115)
    else:
        top, bot = (40, 110, 200), (170, 220, 245)
    for y in range(h):
        pygame.draw.line(surf, lerp_color(top, bot, y / h), (0, y), (w, y))
    return surf


def _grayscale(src):
    """A B/W silhouette-legibility check (AD accessibility note): luminance copy
    so the blade + face must read on value alone, not hue."""
    g = src.copy()
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114)
    arr[:, :, 0] = arr[:, :, 1] = arr[:, :, 2] = lum.astype(arr.dtype)
    del arr
    return g


def _label(surf, font, text, x, y):
    sh = font.render(text, True, (0, 0, 0))
    surf.blit(sh, (x + 1, y + 1))
    surf.blit(font.render(text, True, (255, 255, 255)), (x, y))


def main():
    pygame.init()
    ss = 3
    SHEET_W, SHEET_H = 980, 760
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((46, 40, 58))                       # neutral plum-grey board
    font = pygame.font.SysFont("dejavusans", 16, bold=True)
    fbig = pygame.font.SysFont("dejavusans", 22, bold=True)

    _label(sheet, fbig, "GRIM SPROUT  -  baby reaper-imp (take #1)  R3", 20, 14)

    # (a) Showcase boss on a neutral panel.
    panel_w, panel_h = 330, 650
    panel = pygame.Surface((panel_w, panel_h))
    panel.fill((64, 56, 80))
    pygame.draw.rect(panel, (90, 80, 110), panel.get_rect(), 3)
    boss = build_grim_sprout(scale=1.45, ss=ss)
    panel.blit(boss, (panel_w // 2 - boss.get_width() // 2,
                      panel_h // 2 - boss.get_height() // 2 + 6))
    sheet.blit(panel, (20, 52))
    _label(sheet, font, "(a) showcase  -  blade DWARFS the imp", 24, 60)

    # (b) prop -> pillar mirror: a tall vertical PILLAR pair (top cap + repeatable
    # mid) proving the snath tiles and the blade stays at the gap-edge.
    pil_w, pil_h = 170, 600
    pil = pygame.Surface((pil_w * ss, pil_h * ss), pygame.SRCALPHA)
    pil.fill((40, 36, 52))
    pcx = pil_w * ss // 2
    post_w = int(PIPE_W * 0.42 * ss)
    gap_top = int(pil_h * 0.5 * ss)                # where the top pier ends (gap)
    gap_bot = int(pil_h * 0.62 * ss)               # where the bottom pier starts
    draw_snath_pillar_cap(pil, pcx, int(0.04 * pil_h * ss), gap_top, post_w, ss,
                          flip=False)
    draw_snath_pillar_cap(pil, pcx, gap_bot, int(0.96 * pil_h * ss), post_w, ss,
                          flip=True)
    pil = pygame.transform.smoothscale(pil, (pil_w, pil_h))
    sheet.blit(pil, (372, 78))
    _label(sheet, font, "(b) snath -> PILLAR pair", 376, 58)
    _label(sheet, font, "blade = gap-edge only", 376, 686)

    # A standalone repeatable-MID strip beside it, proving the body tiles cleanly.
    mid_w, mid_h = 80, 600
    mid = pygame.Surface((mid_w * ss, mid_h * ss), pygame.SRCALPHA)
    mid.fill((40, 36, 52))
    draw_snath_pillar_mid(mid, mid_w * ss // 2, 0, mid_h * ss, post_w, ss)
    mid = pygame.transform.smoothscale(mid, (mid_w, mid_h))
    sheet.blit(mid, (560, 78))
    _label(sheet, font, "(b') repeat MID", 562, 686)

    # (c) 1x in-game-scale insets on day + night sky + a grayscale check, proving
    # legibility (AD directive #2/#3 + accessibility note).
    inset_w, inset_h = 132, 230
    small_boss = build_grim_sprout(scale=0.62, ss=ss)
    cells = ((False, "DAY"), (True, "NIGHT"))
    for i, (night, name) in enumerate(cells):
        sky = _sky_panel(inset_w, inset_h, night)
        sky.blit(small_boss, (inset_w // 2 - small_boss.get_width() // 2,
                              inset_h // 2 - small_boss.get_height() // 2 + 6))
        pygame.draw.rect(sky, (20, 16, 24), sky.get_rect(), 2)
        x = 672
        y = 80 + i * 250
        sheet.blit(sky, (x, y))
        _label(sheet, font, "(c) 1x  " + name, x + 2, y - 20)

    # B/W silhouette check of the 1x boss (the dark face + blade must still read).
    bw = _grayscale(small_boss)
    bwpanel = pygame.Surface((inset_w, inset_h))
    bwpanel.fill((128, 128, 128))
    bwpanel.blit(bw, (inset_w // 2 - bw.get_width() // 2,
                      inset_h // 2 - bw.get_height() // 2 + 6))
    pygame.draw.rect(bwpanel, (20, 16, 24), bwpanel.get_rect(), 2)
    sheet.blit(bwpanel, (820, 80))
    _label(sheet, font, "(c) 1x  B/W", 822, 60)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_reaper", "grim_sprout")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()

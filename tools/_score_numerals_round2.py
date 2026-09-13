"""Round-2 exploration sheet — the score numeral converged ON Direction D
(embossed raised-gold token), the art-director's lead: the whole glyph IS the
brand yellow so the number reads as one solid gold mass. Five versions all VARY
ON D rather than away from it; C (debossed) is dropped, B is folded into D as a
gradient fill, and A is carried only as the cream-face readability control.

The single highest-impact fix this round is a FIXED-WIDTH dark keyline wrapping
the gold so it separates from BOTH the slate face and the low sandstone wash.
Glyphs are composited on a 4x supersampled scratch and smooth-scaled to native,
so the thin keyline and the 1px capped bevel rim stay crisp. The keyline / bevel
offsets are a constant supersampled-pixel count, so "12" and "1287" share an
identical contour and bevel thickness regardless of digit count (round-1's bevel
implicitly scaled with width).

  D-1  solid gold token + ~1.5px dark keyline, 1px capped highlight rim, 1px drop
  D-2  same token + keyline, gentle vertical gold gradient fill (bright up top)
  D-3  gold core -> dark keyline -> A-style inset menu-yellow outer ring
  A    cream face + inset 2px yellow ring + 1px dark separator (control)
  WC   brushed-foil token: gold core + keyline + a single bright diagonal sheen

Each version is shown at 1 / 12 / 1287 / 999999 over the real DAY backdrop and a
NIGHT strip, plus a PRE-SHRUNK gameplay-scale (~0.4x) row on day + night, and a
day glyph-vs-plate luminance delta readout. Preview only — not shipped.
Output: docs/score_numerals/round_2.png."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game.config import W
from game.hud import _na_plate, _NA_WARM, _NA_SLATE, _NA_SLATE_D, _GOLD_BRIGHT, _font
from game.draw import UI_CREAM, lerp_color

from tools.gen_gameplay_hud_round7 import build_backdrop, NIGHT_TIME

day = build_backdrop(0.0)
night = build_backdrop(NIGHT_TIME)

_SS = 4  # glyph supersample — composite big, smoothscale to native for crisp edges

# Gold-family stops, all anchored on _GOLD_BRIGHT so the whole sheet reads as one
# yellow family with the SKYBIT title / plate rim.
_GOLD_TOP = _GOLD_BRIGHT               # (240,192,64) — flat fill + gradient top
_GOLD_BASE = (200, 150, 40)           # gentle gradient foot (D-2)
_HI_CAP = (255, 236, 170)             # capped 1px top-left highlight rim
_KEY = (12, 9, 7)                     # near-black keyline, darker than _NA_SLATE_D
_SHADE = (118, 74, 18)                # deep amber bottom-right shade bevel
_RING_YEL = _GOLD_BRIGHT               # A-style outer menu-yellow ring

_NA_FONT_SIZE = 46                     # matches the live score plate (hud line 1466)

# Bevel / shadow offsets in NATIVE pixels, scaled up for the supersampled stamp.
# Constant so "12" and "1287" share identical raised feel (locked to weight).
_BEVEL = 1 * _SS
_DROP = 1 * _SS
_KEY_R = 2 * _SS                       # ~1.5px visible keyline at native size


def _gl(txt, color):
    return _font(_NA_FONT_SIZE * _SS, True).render(txt, True, color)


def _stamp_perimeter(dst, glyph, cx, cy, r):
    """Stamp `glyph` on a filled disc of integer offsets of radius `r`. The union
    of offsets is a uniform contour of width ~`r` around the glyph — and because
    `r` is a fixed pixel count (not derived from the glyph width), the keyline /
    ring is the SAME thickness at "12" and "1287"."""
    gr = glyph.get_rect(center=(cx, cy))
    rr = r * r
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if (dx or dy) and dx * dx + dy * dy <= rr:
                dst.blit(glyph, (gr.x + dx, gr.y + dy))


def _grad_face(txt, top, bot):
    """A digit string filled with a vertical top->bottom gradient, masked to the
    glyph alpha so every stroke shares one light direction. Held bright in the
    upper two-thirds; the foot darkens only late so it still reads as one mass."""
    base = _gl(txt, (255, 255, 255))
    w, h = base.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        tt = max(0.0, (t - 0.34) / 0.66)
        pygame.draw.line(grad, lerp_color(top, bot, tt), (0, yy), (w, yy))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return grad


def _composite(surf, center, build):
    """Run `build(scratch, cx, cy)` on a supersampled scratch sized to the plate
    region, then smooth-scale it down and blit centred — keeps the keyline and
    bevel rim crisp at native size."""
    pw, ph = 300, 84
    sw, sh = pw * _SS, ph * _SS
    scratch = pygame.Surface((sw, sh), pygame.SRCALPHA)
    build(scratch, sw // 2, sh // 2)
    small = pygame.transform.smoothscale(scratch, (pw, ph))
    surf.blit(small, (center[0] - pw // 2, center[1] - ph // 2))


def _drop(s, txt, cx, cy, extra_y=0, a=150):
    sh = _gl(txt, _NA_SLATE_D)
    sh.set_alpha(a)
    s.blit(sh, sh.get_rect(center=(cx + _DROP, cy + _DROP + extra_y)))


# ── D-1 — solid gold token + fixed dark keyline ─────────────────────────────
# The whole glyph is _GOLD_BRIGHT (one solid gold mass). A ~1.5px dark keyline
# wraps it so it separates from both the slate face and the low sandstone wash; a
# single 1px capped top-left highlight rim, a 1px amber bottom-right shade and a
# 1px slate drop give it just enough lift to read as a raised token.
def dir_d1(surf, center, txt):
    def build(s, cx, cy):
        _drop(s, txt, cx, cy, extra_y=_BEVEL)
        _stamp_perimeter(s, _gl(txt, _KEY), cx, cy, _KEY_R)
        sh = _gl(txt, _SHADE)
        s.blit(sh, sh.get_rect(center=(cx + _BEVEL, cy + _BEVEL)))
        hi = _gl(txt, _HI_CAP)
        s.blit(hi, hi.get_rect(center=(cx - _BEVEL, cy - _BEVEL)))
        face = _gl(txt, _GOLD_TOP)
        s.blit(face, face.get_rect(center=(cx, cy)))
    _composite(surf, center, build)


# ── D-2 — same token + keyline, gentle vertical gold gradient fill ──────────
def dir_d2(surf, center, txt):
    def build(s, cx, cy):
        _drop(s, txt, cx, cy, extra_y=_BEVEL)
        _stamp_perimeter(s, _gl(txt, _KEY), cx, cy, _KEY_R)
        sh = _gl(txt, _SHADE)
        s.blit(sh, sh.get_rect(center=(cx + _BEVEL, cy + _BEVEL)))
        hi = _gl(txt, _HI_CAP)
        s.blit(hi, hi.get_rect(center=(cx - _BEVEL, cy - _BEVEL)))
        grad = _grad_face(txt, _GOLD_TOP, _GOLD_BASE)
        s.blit(grad, grad.get_rect(center=(cx, cy)))
    _composite(surf, center, build)


# ── D-3 — gold core -> dark keyline -> inset menu-yellow outer ring ─────────
# Best-of-D+A: D-1's solid gold token wrapped in the dark keyline, then an
# A-style menu-yellow outer ring OUTSIDE the dark line. Layering reads
# gold core -> dark keyline -> yellow ring, so the yellow belongs to the NUMBER.
def dir_d3(surf, center, txt):
    def build(s, cx, cy):
        _drop(s, txt, cx, cy, extra_y=_BEVEL, a=140)
        _stamp_perimeter(s, _gl(txt, _RING_YEL), cx, cy, _KEY_R + 2 * _SS)
        _stamp_perimeter(s, _gl(txt, _KEY), cx, cy, _KEY_R)
        sh = _gl(txt, _SHADE)
        s.blit(sh, sh.get_rect(center=(cx + _BEVEL, cy + _BEVEL)))
        hi = _gl(txt, _HI_CAP)
        s.blit(hi, hi.get_rect(center=(cx - _BEVEL, cy - _BEVEL)))
        face = _gl(txt, _GOLD_TOP)
        s.blit(face, face.get_rect(center=(cx, cy)))
    _composite(surf, center, build)


# ── A — cream-face control: inset 2px yellow ring + 1px dark separator ──────
def dir_a(surf, center, txt):
    def build(s, cx, cy):
        _drop(s, txt, cx, cy)
        _stamp_perimeter(s, _gl(txt, _RING_YEL), cx, cy, 4 * _SS)   # 2px ring
        _stamp_perimeter(s, _gl(txt, _KEY), cx, cy, 2 * _SS)        # 1px sep
        face = _gl(txt, UI_CREAM)
        s.blit(face, face.get_rect(center=(cx, cy)))
    _composite(surf, center, build)


# ── WC — brushed-foil token: gold core + keyline + one diagonal sheen sweep ─
# A fresh idea in the gold-brand family: the solid gold token of D-1, but with a
# single bright horizontal-biased sheen band masked to the glyph alpha so it
# catches light like a struck coin, plus the 1px capped rim — foil, not a full
# skeuomorphic bevel.
def dir_wc(surf, center, txt):
    def build(s, cx, cy):
        _drop(s, txt, cx, cy, extra_y=_BEVEL)
        _stamp_perimeter(s, _gl(txt, _KEY), cx, cy, _KEY_R)
        face = _gl(txt, _GOLD_TOP)
        fr = face.get_rect(center=(cx, cy))
        s.blit(face, fr)
        # one bright sheen band high in the glyph, masked to the glyph alpha.
        mask = _gl(txt, (255, 255, 255))
        w, h = mask.get_size()
        sheen = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            t = yy / max(1, h - 1)
            a = int(130 * max(0.0, 1.0 - abs(t - 0.24) / 0.30))
            if a:
                pygame.draw.line(sheen, (*_HI_CAP, a), (0, yy), (w, yy))
        sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        s.blit(sheen, fr)
        hi = _gl(txt, _HI_CAP)
        s.blit(hi, hi.get_rect(center=(cx - _BEVEL, cy - _BEVEL)))
    _composite(surf, center, build)


VARIANTS = [
    ("D-1  solid gold + dark keyline",      dir_d1),
    ("D-2  gold gradient + dark keyline",   dir_d2),
    ("D-3  gold + keyline + yellow ring",   dir_d3),
    ("A    cream face + yellow ring",       dir_a),
    ("WC   brushed-foil gold token",        dir_wc),
]


def _luma(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _plate_rect(score_txt):
    sf = _font(_NA_FONT_SIZE, True)
    sw = max(sf.size("8" * len(score_txt))[0] + 54, 102)
    return pygame.Rect((W - sw) // 2, 42, sw, 56)


def plate_tile(bg, score_txt, drawfn, crop_h):
    surf = bg.copy()
    sp = _plate_rect(score_txt)
    _na_plate(surf, sp, cut=9, round_r=9, inner_warm=_NA_WARM, glow=True)
    drawfn(surf, sp.center, score_txt)
    return surf.subsurface((0, 0, W, crop_h)).copy()


def shrunk_tile(bg, score_txt, drawfn, scale, crop_w, crop_h):
    """Render the plate at full size, crop tight around it, then smooth-scale to
    `scale` — the gameplay-size legibility test the brief asked for, composited
    back onto an honest slice of the same backdrop."""
    surf = bg.copy()
    sp = _plate_rect(score_txt)
    _na_plate(surf, sp, cut=9, round_r=9, inner_warm=_NA_WARM, glow=True)
    drawfn(surf, sp.center, score_txt)
    pad_c = 6
    region = pygame.Rect(sp.x - pad_c, sp.y - pad_c, sp.width + pad_c * 2,
                         sp.height + pad_c * 2)
    region.clamp_ip(pygame.Rect(0, 0, W, bg.get_height()))
    chip = surf.subsurface(region).copy()
    small = pygame.transform.smoothscale(
        chip, (int(region.width * scale), int(region.height * scale)))
    tile = bg.subsurface((0, 0, crop_w, crop_h)).copy()
    tile.blit(small, ((crop_w - small.get_width()) // 2,
                      (crop_h - small.get_height()) // 2))
    return tile


# ── Sheet layout: one wide column per version. ──────────────────────────────
# Per column, stacked: day 1 / day 12 / day 1287 / day 999999, a NIGHT 1287
# strip, then a PRE-SHRUNK gameplay-scale row (day 12 + night 1287 side by side).
pad = 16
top = 64
lab = 22

row_h = 88
night_h = 88
shrink_h = 96
gap = 5

SCORES_DAY = ["1", "12", "1287", "999999"]

col_w = W
cols = len(VARIANTS)
col_block_h = (lab
               + len(SCORES_DAY) * (row_h + gap)
               + 10 + night_h
               + 12 + shrink_h
               + 18)
sheet = pygame.Surface((pad + cols * (col_w + pad), top + col_block_h + pad))
sheet.fill((18, 20, 28))

tf = _font(20, True)
sf2 = _font(13, True)
sf3 = _font(12, True)
sheet.blit(tf.render(
    "Skybit score numerals — Round 2 · converged ON Direction D (raised gold "
    "token). Five versions VARY ON D. Day 1/12/1287/999999 + night strip + "
    "pre-shrunk gameplay-scale row.",
    True, _GOLD_BRIGHT), (pad, 12))
sheet.blit(sf3.render(
    "Plate art is the shipped hud._na_plate (unchanged); only the glyph render "
    "differs. delta = day glyph-light vs plate-body luminance (target >= ~80).",
    True, UI_CREAM), (pad, 38))

# Plate body luminance for the delta readout: the score sits high in the plate,
# so judge against the brightest the body reaches there (_NA_SLATE top stop).
plate_luma = _luma(_NA_SLATE)

for ci, (label, fn) in enumerate(VARIANTS):
    x = pad + ci * (col_w + pad)
    sheet.blit(sf2.render(label, True, UI_CREAM), (x, top - 4))
    y = top + lab
    for s in SCORES_DAY:
        sheet.blit(plate_tile(day, s, fn, row_h), (x, y))
        sheet.blit(sf3.render(f"day · {s}", True, (210, 220, 240)),
                   (x + 6, y + row_h - 16))
        y += row_h + gap
    y += 5
    sheet.blit(plate_tile(night, "1287", fn, night_h), (x, y))
    sheet.blit(sf3.render("night · 1287", True, (190, 200, 255)),
               (x + 6, y + night_h - 16))
    y += night_h + 12
    half = col_w // 2
    sd = shrunk_tile(day, "12", fn, 0.4, half, shrink_h)
    sn = shrunk_tile(night, "1287", fn, 0.4, col_w - half, shrink_h)
    sheet.blit(sd, (x, y))
    sheet.blit(sn, (x + half, y))
    sheet.blit(sf3.render("gameplay 0.4x · day 12", True, (245, 230, 180)),
               (x + 4, y + shrink_h - 15))
    sheet.blit(sf3.render("night 1287", True, (190, 200, 255)),
               (x + half + 4, y + shrink_h - 15))

    sample = {"D-1": _GOLD_TOP, "D-2": _GOLD_TOP, "D-3": _GOLD_TOP,
              "WC": _GOLD_TOP}.get(label.split()[0], UI_CREAM)
    delta = _luma(sample) - plate_luma
    col = (140, 230, 150) if delta >= 80 else (240, 150, 120)
    sheet.blit(sf3.render(f"day d~{delta:.0f}", True, col), (x + col_w - 84, top - 4))

out = os.path.join(_ROOT, "docs", "score_numerals", "round_2.png")
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
for ci, (label, _) in enumerate(VARIANTS):
    name = label.split()[0]
    sample = {"D-1": _GOLD_TOP, "D-2": _GOLD_TOP, "D-3": _GOLD_TOP,
              "WC": _GOLD_TOP}.get(name, UI_CREAM)
    print(f"  legibility {name}: delta={_luma(sample) - plate_luma:.0f}")

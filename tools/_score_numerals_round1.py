"""Exploration sheet — five GENUINELY DISTINCT score-numeral treatments on the
shipped Neon-Arcade slate plate. Plate art is unchanged (hud._na_plate); only
the glyph rendering differs per direction. Each glyph is composited on a
supersampled scratch surface and smooth-scaled down, so bevels / gradients /
keylines stay crisp at native size.

The five directions use five DIFFERENT mechanisms, not five weights of one:
  A  thick menu-yellow ring framing a cream face (dark keyline between)
  B  vertical gold-gradient face (foil sheen) on a crisp dark keyline
  C  DEBOSSED — digit stamped INTO the plate (dark face, yellow lit lower lip)
  D  EMBOSSED — raised solid-yellow token (light top bevel, dark shade bevel)
  E  cream face + dark keyline + a soft menu-yellow GLOW halo (max face width)

Rendered over the real day backdrop, with a generous night strip per direction
so internal contrast is judged in both biomes. Preview only — not shipped.
Output: docs/score_numerals/round_1.png."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game.config import W
from game.hud import _na_plate, _NA_WARM, _GOLD_BRIGHT, _font
from game.draw import UI_CREAM, NEAR_BLACK, lerp_color
from tools.gen_gameplay_hud_round7 import build_backdrop, NIGHT_TIME

day = build_backdrop(0.0)
night = build_backdrop(NIGHT_TIME)

_SS = 4  # glyph supersample — composite big, smoothscale to native for crisp edges

# Gold-family stops, all anchored on _GOLD_BRIGHT so the whole sheet reads as
# one yellow family with the SKYBIT title / plate rim.
_GOLD_HI = (255, 234, 158)            # bright sheen near the top of a digit
_GOLD_LO = (190, 132, 34)             # deep amber at the foot of a digit
_GOLD_DK = (118, 74, 18)             # darkest engraved shade for a raised bevel
_KEY = (14, 11, 9)                    # near-black keyline (a touch warmer than NEAR_BLACK)


def _glyph(txt, color, size):
    return _font(size, True).render(txt, True, color)


def _stamp_ring(scratch, glyph_ss, cx, cy, radius_ss):
    """Stamp a supersampled glyph in a filled disc of offsets — a uniform
    perimeter that becomes a clean ring once the scratch is scaled down."""
    gr = glyph_ss.get_rect(center=(cx, cy))
    rr = radius_ss * radius_ss
    for dx in range(-radius_ss, radius_ss + 1):
        for dy in range(-radius_ss, radius_ss + 1):
            if (dx or dy) and dx * dx + dy * dy <= rr:
                scratch.blit(glyph_ss, (gr.x + dx, gr.y + dy))


def _grad_face_ss(txt, top, bot):
    """A supersampled digit string filled with a vertical top→bottom gradient,
    built by masking a full-height gradient band to the glyph's own alpha so
    every stroke shares one light direction (foil look)."""
    base = _glyph(txt, (255, 255, 255), 46 * _SS)
    w, h = base.get_size()
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        pygame.draw.line(grad, lerp_color(top, bot, t), (0, yy), (w, yy))
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return grad


def _composite(center, build):
    """Run `build(scratch, cx, cy)` on a supersampled scratch the size of the
    plate region, then return the down-scaled surface positioned to blit at the
    plate's centre. Keeps every treatment edge crisp."""
    pw, ph = 220, 84                      # comfortably larger than any plate face
    sw, sh = pw * _SS, ph * _SS
    scratch = pygame.Surface((sw, sh), pygame.SRCALPHA)
    build(scratch, sw // 2, sh // 2)
    small = pygame.transform.smoothscale(scratch, (pw, ph))
    return small, (center[0] - pw // 2, center[1] - ph // 2)


# ── Direction A — thick menu-yellow RING framing a cream face, dark keyline
# between. The yellow perimeter carries the brand and turns each digit into a
# bright bordered shape; the keyline stops the cream and yellow lights melting.
def dir_ring(surf, center, txt):
    def build(s, cx, cy):
        yel = _glyph(txt, _GOLD_BRIGHT, 46 * _SS)
        key = _glyph(txt, _KEY, 46 * _SS)
        face = _glyph(txt, UI_CREAM, 46 * _SS)
        _stamp_ring(s, yel, cx, cy, 5 * _SS)      # thick yellow ring
        _stamp_ring(s, key, cx, cy, 2 * _SS)      # dark separator inside it
        s.blit(face, face.get_rect(center=(cx, cy)))
    small, pos = _composite(center, build)
    surf.blit(small, pos)


# ── Direction B — vertical GOLD-GRADIENT face (bright sheen top → amber foot),
# crisp dark keyline + soft drop. One bright shape, foil sheen, no cream.
def dir_gradient(surf, center, txt):
    def build(s, cx, cy):
        sh = _glyph(txt, _KEY, 46 * _SS)
        sh.set_alpha(150)
        s.blit(sh, sh.get_rect(center=(cx + 2 * _SS, cy + 3 * _SS)))
        _stamp_ring(s, _glyph(txt, _KEY, 46 * _SS), cx, cy, 2 * _SS)  # keyline
        grad = _grad_face_ss(txt, _GOLD_HI, _GOLD_LO)
        s.blit(grad, grad.get_rect(center=(cx, cy)))
    small, pos = _composite(center, build)
    surf.blit(small, pos)


# ── Direction C — DEBOSSED. The digit reads as STAMPED INTO the plate: a dark
# recessed face, a dark shadow-edge along the TOP (light falls from above so the
# top inner wall is in shade), and a menu-yellow LIT lower lip where the same
# light catches the bottom inner wall. Inverse of a raised bevel — tactile and
# unusual, and the yellow lip keeps it in-brand.
def dir_deboss(surf, center, txt):
    def build(s, cx, cy):
        recess = _glyph(txt, (34, 27, 22), 46 * _SS)        # dark recessed face
        top_shadow = _glyph(txt, (6, 5, 4), 46 * _SS)       # in-shade top wall
        lit_lip = _glyph(txt, _GOLD_BRIGHT, 46 * _SS)       # lit bottom lip
        s.blit(lit_lip, lit_lip.get_rect(center=(cx, cy + 2 * _SS)))   # lit lip
        s.blit(top_shadow, top_shadow.get_rect(center=(cx, cy - 2 * _SS)))  # shade
        sheen = _glyph(txt, (96, 70, 40), 46 * _SS)         # faint warm depth
        sheen.set_alpha(130)
        s.blit(sheen, sheen.get_rect(center=(cx + _SS, cy + _SS)))
        s.blit(recess, recess.get_rect(center=(cx, cy)))    # recessed face on top
    small, pos = _composite(center, build)
    surf.blit(small, pos)


# ── Direction D — EMBOSSED. A raised solid menu-yellow token: a bright top-left
# highlight bevel and a dark amber bottom-right shade bevel, plus a soft contact
# shadow, so each digit feels like a physical raised gold piece on the plate.
def dir_emboss(surf, center, txt):
    def build(s, cx, cy):
        contact = _glyph(txt, _KEY, 46 * _SS)
        contact.set_alpha(170)
        s.blit(contact, contact.get_rect(center=(cx + 2 * _SS, cy + 3 * _SS)))
        shade = _glyph(txt, _GOLD_DK, 46 * _SS)             # bottom-right shade
        hi = _glyph(txt, (255, 246, 200), 46 * _SS)         # top-left highlight
        face = _glyph(txt, _GOLD_BRIGHT, 46 * _SS)
        s.blit(shade, shade.get_rect(center=(cx + 2 * _SS, cy + 2 * _SS)))
        s.blit(hi, hi.get_rect(center=(cx - 2 * _SS, cy - 2 * _SS)))
        s.blit(face, face.get_rect(center=(cx, cy)))
    small, pos = _composite(center, build)
    surf.blit(small, pos)


# ── Direction E — cream face + crisp dark keyline + a soft menu-yellow GLOW
# halo bleeding off the edges (echoes the plate-rim glow). Ties the digit to the
# brand WITHOUT thickening the stroke, so it keeps maximum face area at 4 digits.
def dir_glow(surf, center, txt):
    def build(s, cx, cy):
        glow = _glyph(txt, _GOLD_BRIGHT, 46 * _SS)
        for rad, a in ((7 * _SS, 22), (5 * _SS, 34), (3 * _SS, 56)):
            layer = glow.copy()
            layer.set_alpha(a)
            _stamp_ring(s, layer, cx, cy, rad)
        _stamp_ring(s, _glyph(txt, _KEY, 46 * _SS), cx, cy, 2 * _SS)  # keyline
        face = _glyph(txt, UI_CREAM, 46 * _SS)
        s.blit(face, face.get_rect(center=(cx, cy)))
    small, pos = _composite(center, build)
    surf.blit(small, pos)


VARIANTS = [
    ("A  menu-yellow ring + cream face",  dir_ring),
    ("B  vertical gold-gradient face",    dir_gradient),
    ("C  debossed (stamped into plate)",  dir_deboss),
    ("D  embossed raised-gold token",     dir_emboss),
    ("E  cream face + yellow glow halo",  dir_glow),
]
SCORES = ["12", "1287"]


def plate_tile(bg, score_txt, drawfn, crop_h):
    surf = bg.copy()
    sf = _font(46, True)
    sw = max(sf.size("8" * len(score_txt))[0] + 54, 102)
    sp = pygame.Rect((W - sw) // 2, 42, sw, 56)
    _na_plate(surf, sp, cut=9, round_r=9, inner_warm=_NA_WARM, glow=True)
    drawfn(surf, sp.center, score_txt)
    return surf.subsurface((0, 0, W, crop_h)).copy()


# ── Sheet layout: one wide column per direction. Day "12" + day "1287" stacked,
# then a generous night "1287" strip so contrast at width holds in both biomes.
pad = 16
top = 44
lab = 26
day_h = 112
night_h = 100

col_w = W
cols = len(VARIANTS)
col_block_h = lab + day_h + 6 + day_h + 12 + night_h + 22
sheet = pygame.Surface((pad + cols * (col_w + pad), top + col_block_h))
sheet.fill((18, 20, 28))

tf = _font(20, True)
sf2 = _font(13, True)
sheet.blit(tf.render("Skybit score numerals — five DISTINCT directions on the "
                     "shipped slate plate (plate art unchanged; only the glyph "
                     "differs). Day 12 + 1287, plus a night strip.",
                     True, _GOLD_BRIGHT), (pad, 10))

for ci, (label, fn) in enumerate(VARIANTS):
    x = pad + ci * (col_w + pad)
    sheet.blit(sf2.render(label, True, UI_CREAM), (x, top - 2))
    y = top + lab
    sheet.blit(plate_tile(day, "12", fn, day_h), (x, y))
    y += day_h + 6
    sheet.blit(plate_tile(day, "1287", fn, day_h), (x, y))
    y += day_h + 12
    sheet.blit(plate_tile(night, "1287", fn, night_h), (x, y))
    sheet.blit(sf2.render("night · 1287", True, (190, 200, 255)),
               (x + 6, y + night_h - 16))

out = os.path.join(_ROOT, "docs", "score_numerals", "round_1.png")
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

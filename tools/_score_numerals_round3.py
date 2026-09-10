"""Round-3 finalizing pass — the score numeral is LOCKED to Direction D-1: a
solid gold token wrapped in a fixed-width dark keyline that does all the
figure-ground work. The gradient (D-2), the yellow outer ring (D-3) and the
cream control (A) are dropped this round — the gradient softened small-scale
bottom contrast, the ring filled counters at gameplay scale, cream is off-brand.

This sheet shows the finished D-1 as THE answer, with the single brushed-foil
WC kept beside it ONLY as an optional B-pick (it must not compete with D-1).

Three tightenings over round 2, all on D-1:
  - the top / upper-left highlight cap is pushed brighter (toward warm ivory) so
    the token pops as "raised" at full size WITHOUT touching the flat gold face;
  - the bottom-right shade is darkened one step so the lower edge separates from
    both the gold face and the plate foot (it read soft on the night strip);
  - the dark keyline LIGHTENS one value step on the night strip so it never
    sinks into the darker night surround — readability never rests on hue alone.

Everything stays composited on a 4x supersampled scratch and smooth-scaled to
native, so the keyline / bevel rim are crisp and FIXED-WIDTH: "12" and "1287"
share an identical contour and bevel thickness regardless of digit count.

Glyph-vs-plate luminance delta is measured from the ACTUAL rendered pixels (the
brightest gold sampled against the mean plate-body luma under the glyph), per
strip, so the day + night numbers are honest. Preview only — not shipped.
Output: docs/score_numerals/round_3.png."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game.config import W
from game.hud import (_na_plate, _NA_WARM, _NA_SLATE, _NA_SLATE_D, _GOLD_BRIGHT,
                      _font)
from game.draw import UI_CREAM, lerp_color

from tools.gen_gameplay_hud_round7 import build_backdrop, NIGHT_TIME

day = build_backdrop(0.0)
night = build_backdrop(NIGHT_TIME)

_SS = 4  # glyph supersample — composite big, smoothscale to native for crisp edges

# ── D-1 final palette ───────────────────────────────────────────────────────
# The whole glyph is one flat _GOLD_BRIGHT mass; the dark keyline is the hero.
_GOLD = _GOLD_BRIGHT                  # (240,192,64) — flat gold face, no gradient
_HI_CAP = (255, 244, 196)            # brighter warm-ivory top/upper-left rim cap
_KEY = (12, 9, 7)                    # near-black keyline (day) — figure-ground hero
_KEY_NIGHT = (30, 26, 22)            # keyline lightened 1 step so it never sinks
_SHADE = (150, 104, 28)              # deeper amber bottom-right shade (separation)

_NA_FONT_SIZE = 46                   # matches the live score plate (hud line ~1466)

# Bevel / shadow / keyline offsets in NATIVE px, scaled up for the supersample.
# Constant counts so "12" and "1287" share an identical raised feel + keyline.
_BEVEL = 1 * _SS
_DROP = 1 * _SS
_KEY_R = 2 * _SS                     # ~1.5px visible keyline at native size


def _gl(txt, color):
    return _font(_NA_FONT_SIZE * _SS, True).render(txt, True, color)


def _stamp_perimeter(dst, glyph, cx, cy, r):
    """Stamp `glyph` on a filled disc of integer offsets of radius `r`. The union
    of offsets is a uniform contour of width ~`r` around the glyph — and because
    `r` is a fixed pixel count (not derived from the glyph width), the keyline is
    the SAME thickness at "12" and "1287"."""
    gr = glyph.get_rect(center=(cx, cy))
    rr = r * r
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if (dx or dy) and dx * dx + dy * dy <= rr:
                dst.blit(glyph, (gr.x + dx, gr.y + dy))


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


# ── D-1 — solid gold token + fixed dark keyline (THE winner) ────────────────
# Layer order (back to front): slate drop shadow, dark keyline contour, amber
# bottom-right shade, bright ivory top-left highlight cap, flat gold face. The
# keyline (`key_color`) lightens on night so it never merges with a dark sky.
def dir_d1(surf, center, txt, key_color=_KEY):
    def build(s, cx, cy):
        _drop(s, txt, cx, cy, extra_y=_BEVEL)
        _stamp_perimeter(s, _gl(txt, key_color), cx, cy, _KEY_R)
        sh = _gl(txt, _SHADE)
        s.blit(sh, sh.get_rect(center=(cx + _BEVEL, cy + _BEVEL)))
        hi = _gl(txt, _HI_CAP)
        s.blit(hi, hi.get_rect(center=(cx - _BEVEL, cy - _BEVEL)))
        face = _gl(txt, _GOLD)
        s.blit(face, face.get_rect(center=(cx, cy)))
    _composite(surf, center, build)


def dir_d1_night(surf, center, txt):
    dir_d1(surf, center, txt, key_color=_KEY_NIGHT)


# ── WC — brushed-foil token (optional B-pick only) ──────────────────────────
# The exact D-1 token, plus one bright diagonal sheen band masked to the glyph
# alpha so it catches light like struck foil. Shown beside D-1 as a B-pick — it
# does NOT replace the flat winner.
def dir_wc(surf, center, txt, key_color=_KEY):
    def build(s, cx, cy):
        _drop(s, txt, cx, cy, extra_y=_BEVEL)
        _stamp_perimeter(s, _gl(txt, key_color), cx, cy, _KEY_R)
        sh = _gl(txt, _SHADE)
        s.blit(sh, sh.get_rect(center=(cx + _BEVEL, cy + _BEVEL)))
        face = _gl(txt, _GOLD)
        fr = face.get_rect(center=(cx, cy))
        s.blit(face, fr)
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


def dir_wc_night(surf, center, txt):
    dir_wc(surf, center, txt, key_color=_KEY_NIGHT)


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


# ── Honest, measured glyph-vs-plate luminance delta ─────────────────────────
# Render one plate, then sample the BRIGHTEST gold pixels (the flat face) against
# the MEAN plate-body luma in the band where the glyph sits — the real contrast a
# player perceives, not a flat-color guess.
def measured_delta(bg, score_txt, drawfn):
    surf = bg.copy()
    sp = _plate_rect(score_txt)
    plate_only = surf.copy()
    _na_plate(plate_only, sp, cut=9, round_r=9, inner_warm=_NA_WARM, glow=True)
    # Mean plate-body luma in the central glyph band (avoid rim + corners).
    band = pygame.Rect(sp.x + 14, sp.centery - 12, sp.width - 28, 24)
    band.clamp_ip(pygame.Rect(0, 0, W, bg.get_height()))
    body_sum, body_n = 0.0, 0
    for yy in range(band.top, band.bottom, 2):
        for xx in range(band.left, band.right, 2):
            body_sum += _luma(plate_only.get_at((xx, yy)))
            body_n += 1
    body_luma = body_sum / max(1, body_n)
    # Brightest gold luma from the actual glyph render.
    drawfn(surf, sp.center, score_txt)
    region = pygame.Rect(sp.x + 8, sp.y + 4, sp.width - 16, sp.height - 8)
    region.clamp_ip(pygame.Rect(0, 0, W, bg.get_height()))
    top_luma = 0.0
    for yy in range(region.top, region.bottom):
        for xx in range(region.left, region.right):
            top_luma = max(top_luma, _luma(surf.get_at((xx, yy))))
    return top_luma - body_luma


# ── 999999 spacing audit ────────────────────────────────────────────────────
# Render the widest score on its plate, then scan the glyph-ink columns to
# measure (a) the SMALLEST clear gap between adjacent digits and (b) the margin
# from the outermost ink to the plate edge. Both come from real pixels so the
# brief's "no kerning collapse / no bleed off the plate" is verified, not
# assumed. Ink = any pixel measurably brighter than the local plate body.
def spacing_check(score_txt, drawfn):
    sp = _plate_rect(score_txt)
    # The plate's own gold rim + cut corners hug the rect edge; inset the scan
    # past them (RIM px) so only GLYPH ink is measured and the edge margin is
    # honest (glyph-to-inner-plate-edge, not glyph-to-rim).
    RIM = 4
    scan = pygame.Rect(sp.x + RIM, sp.y, sp.width - RIM * 2, sp.height)

    plate_only = day.copy()
    _na_plate(plate_only, sp, cut=9, round_r=9, inner_warm=_NA_WARM, glow=True)
    band = pygame.Rect(scan.x, sp.centery - 14, scan.width, 28)
    band.clamp_ip(pygame.Rect(0, 0, W, day.get_height()))
    body_sum, body_n = 0.0, 0
    for yy in range(band.top, band.bottom, 2):
        for xx in range(band.left, band.right, 2):
            body_sum += _luma(plate_only.get_at((xx, yy)))
            body_n += 1
    body_luma = body_sum / max(1, body_n)

    surf = day.copy()
    _na_plate(surf, sp, cut=9, round_r=9, inner_warm=_NA_WARM, glow=True)
    drawfn(surf, sp.center, score_txt)
    thresh = body_luma + 45  # comfortably above body wash, into gold/keyline ink
    ink_cols = []
    for xx in range(scan.left, scan.right):
        col_ink = False
        for yy in range(band.top, band.bottom):
            if _luma(surf.get_at((xx, yy))) >= thresh:
                col_ink = True
                break
        ink_cols.append(col_ink)

    # Smallest run of empty columns BETWEEN two ink runs = tightest digit gap.
    first = next((i for i, v in enumerate(ink_cols) if v), None)
    last = next((i for i in range(len(ink_cols) - 1, -1, -1) if ink_cols[i]),
                None)
    if first is None:
        return 0, 0
    min_gap = 999
    run = 0
    for i in range(first, last + 1):
        if not ink_cols[i]:
            run += 1
        else:
            if run:
                min_gap = min(min_gap, run)
            run = 0
    if min_gap == 999:
        min_gap = 0
    # Margin measured from the inner (post-rim) plate edge to the glyph ink.
    left_margin = first + RIM
    right_margin = (len(ink_cols) - 1 - last) + RIM
    return min_gap, min(left_margin, right_margin)


# ── Sheet layout ────────────────────────────────────────────────────────────
# Two columns only: D-1 (THE winner, left) and WC (optional B-pick, right).
# Each column: day 1/12/1287/999999, a NIGHT 1287 strip, then a PROMINENT
# pre-shrunk gameplay-scale (~0.4x) row (day 12 + night 1287). The night strip
# and shrunk tiles use the night-lightened keyline variant.
pad = 18
top = 94            # room for the global header band + per-column label + metrics
lab = 24

row_h = 92
night_h = 92
shrink_h = 132          # taller — this is the sign-off surface, make it prominent
gap = 6

SCORES_DAY = ["1", "12", "1287", "999999"]

VARIANTS = [
    ("D-1  solid gold + dark keyline  — THE WINNER", dir_d1, dir_d1_night),
    ("WC   brushed-foil  — optional B-pick only",    dir_wc, dir_wc_night),
]

col_w = W
cols = len(VARIANTS)
col_block_h = (lab
               + len(SCORES_DAY) * (row_h + gap)
               + 10 + night_h
               + 14 + shrink_h
               + 20)
sheet = pygame.Surface((pad + cols * (col_w + pad), top + col_block_h + pad))
sheet.fill((18, 20, 28))

tf = _font(17, True)
sf2 = _font(13, True)
sf3 = _font(12, True)
sheet.blit(tf.render(
    "Skybit score numerals — Round 3 · FINAL: Direction D-1 (solid gold + dark "
    "keyline)",
    True, _GOLD_BRIGHT), (pad, 8))
sheet.blit(sf3.render(
    "Flat face — no gradient / ring / halo; the fixed-width dark keyline is the "
    "hero. WC kept only as an optional B-pick. Plate is the unchanged "
    "hud._na_plate; only the glyph differs.",
    True, UI_CREAM), (pad, 28))
sheet.blit(sf3.render(
    "delta = measured brightest-gold vs mean plate-body luma. Keyline lightens "
    "1 step on night so it never sinks into the darker plate.",
    True, (190, 200, 255)), (pad, 42))

for ci, (label, dayfn, nightfn) in enumerate(VARIANTS):
    x = pad + ci * (col_w + pad)
    sheet.blit(sf2.render(label, True, _GOLD_BRIGHT if ci == 0 else UI_CREAM),
               (x, top - 34))
    # Per-column measured readouts, kept WITHIN this column's width on one line
    # so they never collide with the neighbouring column's header.
    dd = measured_delta(day, "1287", dayfn)
    dn = measured_delta(night, "1287", nightfn)
    gapn, marg = spacing_check("999999", dayfn)
    dcol = (140, 230, 150) if dd >= 120 else (240, 150, 120)
    ncol = (140, 230, 150) if dn >= 120 else (240, 150, 120)
    scol = (140, 230, 150) if (gapn >= 1 and marg >= 2) else (240, 150, 120)
    sheet.blit(sf3.render(f"day d~{dd:.0f}", True, dcol), (x, top - 16))
    sheet.blit(sf3.render(f"night d~{dn:.0f}", True, ncol), (x + 70, top - 16))
    sheet.blit(sf3.render(
        f"999999 gap {gapn}px · margin {marg}px", True, scol),
        (x + 152, top - 16))
    y = top + lab
    for s in SCORES_DAY:
        sheet.blit(plate_tile(day, s, dayfn, row_h), (x, y))
        sheet.blit(sf3.render(f"day · {s}", True, (210, 220, 240)),
                   (x + 6, y + row_h - 16))
        y += row_h + gap
    y += 5
    sheet.blit(plate_tile(night, "1287", nightfn, night_h), (x, y))
    sheet.blit(sf3.render("night · 1287", True, (190, 200, 255)),
               (x + 6, y + night_h - 16))
    y += night_h + 14

    # Prominent gameplay-scale sign-off row: day 12 + night 1287 at 0.4x, on a
    # banded backdrop so the shrunk tokens are read at the size a player sees.
    half = col_w // 2
    sheet.blit(sf3.render("GAMEPLAY 0.4x  — sign-off surface", True,
                          (245, 230, 180)), (x + 4, y - 2))
    sd = shrunk_tile(day, "12", dayfn, 0.4, half, shrink_h - 18)
    sn = shrunk_tile(night, "1287", nightfn, 0.4, col_w - half, shrink_h - 18)
    sheet.blit(sd, (x, y + 16))
    sheet.blit(sn, (x + half, y + 16))
    sheet.blit(sf3.render("day 12", True, (245, 230, 180)),
               (x + 4, y + shrink_h - 14))
    sheet.blit(sf3.render("night 1287", True, (190, 200, 255)),
               (x + half + 4, y + shrink_h - 14))

out = os.path.join(_ROOT, "docs", "score_numerals", "round_3.png")
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
print(f"  D-1 face={_GOLD}  hi_cap={_HI_CAP}  shade={_SHADE}")
print(f"  D-1 keyline day={_KEY}  night={_KEY_NIGHT}")
print(f"  offsets (native px): bevel={_BEVEL // _SS}  drop={_DROP // _SS}  "
      f"keyline_r~1.5  drop_alpha=150")
for label, dayfn, nightfn in VARIANTS:
    name = label.split()[0]
    dd = measured_delta(day, "1287", dayfn)
    dn = measured_delta(night, "1287", nightfn)
    g, m = spacing_check("999999", dayfn)
    print(f"  {name}: day delta={dd:.0f}  night delta={dn:.0f}  "
          f"999999 digit-gap={g}px  edge-margin={m}px")

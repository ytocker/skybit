"""Look-dev sheet for the Skybit BOSS batch-2 "LEYAK-EPIC" set — concept #5 NUKEKUBI.

A prim Japanese court-lady's detached HEAD, hair perfectly pinned, drifting down a
string of paper charms with a polite flame where her neck used to be. Same bodiless-
head DNA as shipped Leyak, but face-mitigated HARD: the warm-powder face mass stays
≤25% of the head; the lacquer-BLACK top-knot + fanned GOLD kanzashi pins + a coral-RED
flame collar own the silhouette and the 32px read. Demure half-lid eyes + a small
bow-mouth carry scary-CUTE — deliberately NO Leyak grin, NO ash tone.

House style this obeys (the warren-clown / Big-Reapy / Pyrecrown / Leyak grammar):
  - CHIBI proportions — one ornate coiffed floating head; NO torso, NO limbs. The
    charm-cord trail is the body.
  - FLAT saturated fills + hard 1-2px ink keyline (28,22,30). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - ELEVATED ("epic"): hero rendered LARGE at SS=6 then smoothscaled — crisp at
    downscale; more geometry, richer triad, stronger make_glow_surface glow than
    the source Leyak.

Accessibility tell: the BLACK-crown / GOLD-fan / CORAL-collar value+hue stack carries
the read independent of the tiny powder face — never hue-only.

Prop -> pillar mirror: the charm-CORD itself is the pillar. One o-fuda paper charm +
one bead-knot per repeat = the tiling PILLAR BODY; a tassel + on-axis warding-bell =
the detachable GAP-EDGE CAP. Naturally vertical + symmetric — clean mirror, no
top-heavy cap.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/leyak_epic/nukekubi/render_nukekubi.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (leyak-epic #5 nukekubi) — hex-exact from the locked brief ──
# Face is the MINOR mass: a warm powder oval. The DOMINANT masses are lacquer-black
# hair + gold pins + coral flame — that black/gold/coral stack (not the face) is what
# survives downscale. Deliberately NO ash tone (clear of shipped Leyak).
FACE        = (236, 212, 196)   # warm powder face fill
FACE_DK     = (186, 156, 142)   # warm shade (dark-core ring / hollows under the brow)
FACE_SHEEN  = (252, 236, 226)   # top-left rim sheen

HAIR        = (34, 28, 38)      # lacquer-black top-knot (DOMINANT mass)
HAIR_DK     = (18, 14, 22)      # near-black dark-core
HAIR_SHEEN  = (96, 86, 104)     # cool lacquer rim-sheen lobe (the wet-lacquer pop)

GOLD        = (228, 184, 84)    # o-fuda trim / bell base gold
GOLD_DK     = (158, 118, 44)    # gold shade
GOLD_SHEEN  = (250, 226, 150)   # gold rim sheen

# The kanzashi pins read a notch BRIGHTER than the shaft o-fuda gold-trim so the
# head wins the top-to-bottom focal hierarchy (same hue, higher value).
PIN_GOLD    = (244, 206, 110)
PIN_GOLD_DK = (176, 132, 52)
PIN_SHEEN   = (255, 240, 184)

# Nudged slightly cooler + deeper than round-1 so the collar holds clear of
# shipped Ifra's coral (238,108,72) at 32px on the warm-blue day sky.
CORAL       = (228, 96, 58)     # coral-RED flame collar (deepened off Ifra's coral)
CORAL_DK    = (162, 56, 36)     # coral shade / flame seams
CORAL_SHEEN = (250, 164, 116)   # coral rim sheen

LIP         = (196, 70, 70)     # small bow-mouth red
PAPER       = (244, 238, 222)   # o-fuda paper charm (brightened — the LIGHT tile beat)
PAPER_DK    = (180, 164, 140)   # paper shade
CORD        = (150, 60, 56)     # dark-red charm cord
CORD_DK     = (104, 38, 38)

INK         = (28, 22, 30)      # the house keyline (epic spec)
WHITE       = (252, 250, 246)


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_d=30, sheen_col=None):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Sculpted volume while staying flat-shaded. `sheen_col` overrides the
    sheen tint (lacquer hair wants a cool-grey sheen, not a lighter black)."""
    pygame.draw.circle(surf, _shade_c(col, -46), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.06))))
    if sheen:
        sc = sheen_col if sheen_col is not None else _shade_c(col, sheen_d)
        pygame.draw.circle(surf, sc,
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.34)))


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot `_add_outline` recipe). Returns a padded surface."""
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


# ── flame lobe (a flat triad tongue of coral fire) ───────────────────────────

def _flame_lobe(surf, cx, base_y, w, h, ss, col, *, point_up=True, lean=0.0):
    """One coral flame tongue as a HARD flat triad shape: a fat rounded base
    tapering to a curled tip. `point_up` flickers up (the collar licks UP toward
    the jaw); flipped it licks down. `lean` splays the tip sideways so a fan of
    tongues opens out instead of stacking. Flat-shaded — a paper-lantern flame,
    not a rendered fire."""
    d = -1.0 if point_up else 1.0

    def _shape(scale, c, dx=0.0, dy=0.0):
        pts = []
        n = 18
        for i in range(n + 1):
            t = i / n
            # Bulge low, neck to a leaning curl-tip high.
            ww = (w * 0.5) * scale * math.sin(t * math.pi) ** 0.7
            yy = d * h * scale * t
            curl = (w * 0.22 + h * lean) * scale * (t * t)   # tip leans/splays
            pts.append((cx + dx + ww + curl, base_y + dy + yy))
        for i in range(n, -1, -1):
            t = i / n
            ww = (w * 0.5) * scale * math.sin(t * math.pi) ** 0.7
            yy = d * h * scale * t
            curl = (w * 0.22 + h * lean) * scale * (t * t)
            pts.append((cx + dx - ww + curl, base_y + dy + yy))
        pygame.draw.polygon(surf, c, [(int(px), int(py)) for px, py in pts])

    _shape(1.00, _shade_c(col, -46))               # dark-core ring
    _shape(0.84, col)                              # flat fill
    _shape(0.40, _shade_c(col, 36), dx=-w * 0.12, dy=d * h * 0.10)  # rim sheen


def _flame_collar(surf, cx, cy, r, ss, *, night=False):
    """The coral-RED flame collar where the neck was: a fanned ring of flame tongues
    licking UP around the jaw, with a warm glow halo. The single brightest warm mass
    — sized to read at 32px as the bottom band of the black/gold/coral stack."""
    glow_r = int(r * (1.5 if night else 1.15))
    gl = make_glow_surface(glow_r, CORAL,
                           alpha_center=190 if night else 120, falloff=2.1)
    surf.blit(gl, (int(cx - glow_r), int(cy - glow_r * 0.4)),
              special_flags=pygame.BLEND_ADD)

    # A WIDE fanned crescent of flame tongues licking up around the jaw — spread
    # along a flat base so the tongues read as a lobed collar band (not a stacked
    # pinecone). Tongues splay outward at the wings + stand tall in the centre.
    n = 9
    for i in range(n):
        t = i / (n - 1)
        s = (t - 0.5) * 2.0                          # -1..1 across the collar
        bx = cx + s * r * 1.05                        # base spread along a flat line
        by = cy + abs(s) * r * 0.30                   # wings ride a touch lower (a smile arc)
        # Tallest in the centre, shorter at the wings — a tidy court flame fan.
        ht = r * (0.92 - 0.46 * abs(s))
        wd = r * (0.34 - 0.10 * abs(s))
        lean = s * 0.30                               # tongues splay outward
        col = CORAL if i % 2 == 0 else _shade_c(CORAL, -10)
        _flame_lobe(surf, bx, by, wd, ht, ss, col, point_up=True, lean=lean)


# ── the kanzashi pin fan (DOMINANT gold radial) ──────────────────────────────

def _kanzashi(surf, cx, cy, r, ss):
    """A fan of FIVE bold gold kanzashi pins radiating from behind the top-knot — the
    wide gold radial that, with the black knot, owns the silhouette. Round 1's 9 thin
    pins fizzed to a dotty fringe at 32px; this drops to 5, fattens each stem, and
    sizes the bloom-heads BIG so the crown reads as ONE ornate jagged gold-tipped
    silhouette (heads fused at the crown outline, not floating on wires)."""
    n = 5
    spread = math.radians(132)
    for i in range(n):
        t = i / (n - 1)
        a = -math.pi / 2 + (t - 0.5) * spread       # fan upward + outward
        length = r * (1.34 if i % 2 == 0 else 1.08)  # alternating long/short
        ex = cx + math.cos(a) * length
        ey = cy + math.sin(a) * length
        # A lacquer-black backing wedge from the knot to each bloom welds the pin
        # bases into the dominant black mass so the heads never float as loose dots.
        perp = a + math.pi / 2
        wx, wy = math.cos(perp) * r * 0.18, math.sin(perp) * r * 0.18
        pygame.draw.polygon(surf, HAIR_DK, [
            (int(cx + wx), int(cy + wy)), (int(cx - wx), int(cy - wy)),
            (int(ex), int(ey))])
        # Pin shaft: FAT triad on a stick — dark-core, gold, bright sheen run.
        pygame.draw.line(surf, PIN_GOLD_DK, (int(cx), int(cy)), (int(ex), int(ey)),
                         max(3, int(4.2 * ss)))
        pygame.draw.line(surf, PIN_GOLD, (int(cx), int(cy)), (int(ex), int(ey)),
                         max(2, int(2.6 * ss)))
        pygame.draw.line(surf, PIN_SHEEN,
                         (int(cx + (ex - cx) * 0.3), int(cy + (ey - cy) * 0.3)),
                         (int(cx + (ex - cx) * 0.85), int(cy + (ey - cy) * 0.85)),
                         max(1, int(1.0 * ss)))
        # BIG gold bloom-head so each pin tip is a clear blob that survives downscale.
        tip_r = r * (0.30 if i % 2 == 0 else 0.24)
        _triad_circle(surf, ex, ey, tip_r, PIN_GOLD, sheen_d=40, sheen_col=PIN_SHEEN)
        # Five-petal dark pips ring the centre so the bloom reads as a kanzashi flower.
        pygame.draw.circle(surf, PIN_GOLD_DK, (int(ex), int(ey)), max(1, int(tip_r * 0.40)))


# ── the top-knot (DOMINANT lacquer-black mass) ───────────────────────────────

def _topknot(surf, cx, cy, r, ss):
    """The tall lacquer-black top-knot mass that dominates the head: a wide swept
    hair base hugging the crown, rising to a bound bun loop up top, with a wet-lacquer
    sheen lobe. Black is the largest single mass in the silhouette."""
    # Swept side wings hugging the crown (frame the small face).
    for s in (-1, 1):
        wing = [
            (cx + s * r * 0.20, cy - r * 0.10),
            (cx + s * r * 1.10, cy - r * 0.34),
            (cx + s * r * 1.18, cy + r * 0.30),
            (cx + s * r * 0.66, cy + r * 0.62),
            (cx + s * r * 0.30, cy + r * 0.40),
        ]
        pygame.draw.polygon(surf, HAIR_DK, [(int(x), int(y)) for x, y in wing])
        inner = [(cx + s * (r * 0.22), cy - r * 0.06),
                 (cx + s * r * 1.02, cy - r * 0.28),
                 (cx + s * r * 1.08, cy + r * 0.26),
                 (cx + s * r * 0.62, cy + r * 0.54),
                 (cx + s * r * 0.32, cy + r * 0.34)]
        pygame.draw.polygon(surf, HAIR, [(int(x), int(y)) for x, y in inner])

    # The tall bound bun loop rising above the crown — the top of the dominant mass.
    bun_cy = cy - r * 0.72
    _triad_circle(surf, cx, bun_cy, r * 0.62, HAIR, sheen_col=HAIR_SHEEN)
    # A narrowed "binding" neck where the knot is tied (an inked cinch + gold band).
    cinch = pygame.Rect(0, 0, int(r * 0.70), int(r * 0.30))
    cinch.center = (int(cx), int(bun_cy + r * 0.50))
    pygame.draw.ellipse(surf, HAIR_DK, cinch)
    pygame.draw.ellipse(surf, GOLD_DK, cinch.inflate(-int(r * 0.06), int(r * 0.04)))
    band = cinch.inflate(-int(r * 0.10), -int(r * 0.10))
    pygame.draw.ellipse(surf, GOLD, band)
    pygame.draw.ellipse(surf, GOLD_SHEEN, band.inflate(-int(r * 0.30), -int(r * 0.12)))

    # Crown base cap so the hairline meets the face cleanly (a low swept fringe).
    base = pygame.Rect(0, 0, int(r * 1.66), int(r * 1.0))
    base.center = (int(cx), int(cy - r * 0.02))
    pygame.draw.ellipse(surf, HAIR, base)
    pygame.draw.ellipse(surf, HAIR_DK, base, max(1, int(1.4 * ss)))
    # Wet-lacquer sheen lobe high on the crown (the elevated triad pop).
    pygame.draw.circle(surf, HAIR_SHEEN,
                       (int(cx - r * 0.28), int(cy - r * 0.42)),
                       max(2, int(r * 0.26)))
    # A second small sheen on the bun loop.
    pygame.draw.circle(surf, _shade_c(HAIR_SHEEN, 12),
                       (int(cx - r * 0.20), int(bun_cy - r * 0.22)),
                       max(2, int(r * 0.16)))


# ── the small powder face (the MINOR mass) ───────────────────────────────────

def _face(surf, cx, cy, r, ss, *, night=False, tell=False):
    """The MINOR powder face: a small warm oval set LOW + tucked under the swept hair
    so its mass stays ≤25% of the head. Demure HALF-LID eyes (thin lacquer arcs over
    soft lids — deliberately NOT bug-eyes), faint blush ovals, a tiny red bow-mouth.
    `night` lifts the powder value so the small face never sinks into a dark sky.
    `tell` bakes a bolder low-res version of the same marks for the 32px read."""
    face = _shade_c(FACE, 14) if night else FACE
    sheen = _shade_c(FACE_SHEEN, 6) if night else FACE_SHEEN

    # The powder oval (taller than wide — a refined court face).
    fw, fh = r * 0.92, r * 1.18
    oval = pygame.Rect(0, 0, int(fw), int(fh))
    oval.center = (int(cx), int(cy))
    pygame.draw.ellipse(surf, _shade_c(face, -42), oval)
    pygame.draw.ellipse(surf, face, oval.inflate(-int(fw * 0.10), -int(fh * 0.10)))
    # Top-left powder sheen (the lit cheekbone).
    pygame.draw.ellipse(surf, sheen,
                        pygame.Rect(int(cx - fw * 0.34), int(cy - fh * 0.30),
                                    int(fw * 0.34), int(fh * 0.30)))

    eye_dx = r * 0.26
    eye_dy = -r * 0.02
    eye_w = r * 0.30

    if tell:
        # 32px tell: two bold dark half-lid bars + a single red bow dot, sized to
        # survive downscale under the dominant black/gold/coral.
        for s in (-1, 1):
            ex = cx + s * eye_dx
            pygame.draw.line(surf, INK, (int(ex - eye_w * 0.5), int(cy + eye_dy)),
                             (int(ex + eye_w * 0.5), int(cy + eye_dy)),
                             max(2, int(2.4 * ss)))
        pygame.draw.circle(surf, LIP, (int(cx), int(cy + r * 0.40)),
                           max(2, int(r * 0.10)))
        return

    # Demure HALF-LID eyes: a soft lid lid-fold, a thin downcast lacquer lash-arc,
    # a sliver of dark eye beneath — calm + lowered, never wide.
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        # Faint warm lid crease above.
        pygame.draw.arc(surf, FACE_DK,
                        pygame.Rect(int(ex - eye_w * 0.5), int(ey - eye_w * 0.5),
                                    int(eye_w), int(eye_w * 0.8)),
                        math.radians(20), math.radians(160), max(1, int(1.2 * ss)))
        # The lash-arc (a downcast half-lid) — the dominant eye mark.
        lash = pygame.Rect(int(ex - eye_w * 0.55), int(ey - eye_w * 0.18),
                           int(eye_w * 1.1), int(eye_w * 0.9))
        pygame.draw.arc(surf, INK, lash, math.radians(195), math.radians(345),
                        max(2, int(2.0 * ss)))
        # A thin dark eye sliver under the lash.
        pygame.draw.arc(surf, _shade_c(INK, 24), lash.move(0, int(eye_w * 0.10)),
                        math.radians(205), math.radians(335), max(1, int(1.4 * ss)))

    # Faint coral blush ovals high on the cheeks.
    for s in (-1, 1):
        bx, by = cx + s * r * 0.30, cy + r * 0.16
        blush = pygame.Surface((int(r * 0.5), int(r * 0.34)), pygame.SRCALPHA)
        pygame.draw.ellipse(blush, (*CORAL_SHEEN, 90), blush.get_rect())
        surf.blit(blush, (int(bx - r * 0.25), int(by - r * 0.17)))

    # Thin straight court brows above the lids.
    for s in (-1, 1):
        ex = cx + s * eye_dx
        pygame.draw.line(surf, _shade_c(INK, 20),
                         (int(ex - eye_w * 0.42), int(cy - r * 0.26)),
                         (int(ex + eye_w * 0.42), int(cy - r * 0.24)),
                         max(1, int(1.6 * ss)))

    # Tiny nose dot.
    pygame.draw.circle(surf, FACE_DK, (int(cx), int(cy + r * 0.18)), max(1, int(ss)))

    # Small red BOW-mouth: a tidy court lip — a narrow upper bow (two gentle humps
    # with a centre cupid dip) over a slightly fuller lower lip, kept SMALL + lifted
    # so it reads demure, the beat that replaces the Leyak grin (never a wide droop).
    my = cy + r * 0.40
    mw = r * 0.20
    upper = [
        (cx - mw, my),
        (cx - mw * 0.50, my - mw * 0.42),
        (cx, my - mw * 0.16),
        (cx + mw * 0.50, my - mw * 0.42),
        (cx + mw, my),
        (cx, my + mw * 0.18),
    ]
    pygame.draw.polygon(surf, _shade_c(LIP, -36), [(int(x), int(y)) for x, y in upper])
    lower = [
        (cx - mw * 0.74, my + mw * 0.06),
        (cx + mw * 0.74, my + mw * 0.06),
        (cx, my + mw * 0.58),
    ]
    pygame.draw.polygon(surf, LIP, [(int(x), int(y)) for x, y in lower])
    # A pale centre highlight on the lower lip (the lit court-lip pop).
    pygame.draw.circle(surf, _shade_c(LIP, 40), (int(cx), int(my + mw * 0.18)),
                       max(1, int(mw * 0.22)))


# ── the charm-cord (creature trail + the pillar body) ────────────────────────

def _ofuda(surf, cx, cy, w, h, ss):
    """One o-fuda paper charm: a vertical paper slip with gold trim + a column of
    glyph ticks. The repeatable PILLAR detail (one per tile)."""
    rect = pygame.Rect(int(cx - w * 0.5), int(cy - h * 0.5), int(w), int(h))
    pygame.draw.rect(surf, PAPER_DK, rect)
    pygame.draw.rect(surf, PAPER, rect.inflate(-int(w * 0.16), -int(h * 0.10)))
    # Top-left paper sheen edge.
    pygame.draw.rect(surf, WHITE, (rect.x + int(w * 0.10), rect.y + int(h * 0.08),
                                   int(w * 0.16), int(h * 0.7)))
    # Gold trim band across the top.
    pygame.draw.rect(surf, GOLD, (rect.x, rect.y, rect.w, int(h * 0.16)))
    pygame.draw.rect(surf, GOLD_SHEEN, (rect.x, rect.y, rect.w, max(1, int(h * 0.05))))
    # A column of glyph ticks down the slip (the warding script).
    n = 4
    for i in range(n):
        gy = rect.y + h * (0.30 + 0.16 * i)
        pygame.draw.line(surf, INK, (int(cx - w * 0.16), int(gy)),
                         (int(cx + w * 0.16), int(gy)), max(1, int(1.4 * ss)))
    pygame.draw.line(surf, _shade_c(INK, 18), (int(cx), int(rect.y + h * 0.26)),
                     (int(cx), int(rect.y + h * 0.86)), max(1, int(1.2 * ss)))


def _bead_knot(surf, cx, cy, r, ss):
    """One bead-knot: a DARK lacquer-black bead with a thin gold cord-band — the second
    repeatable PILLAR detail. Round 1 made it a gold bead that sat too close in value
    to the cream o-fuda and the repeat muddied; making the bead DARK gives each tile a
    clear LIGHT-o-fuda → DARK-bead rhythm so the shaft reads as obvious beads-on-a-cord
    at 1x. The bead is rounder + a touch bigger than the wrap so it carries the dark
    beat of the rhythm."""
    _triad_circle(surf, cx, cy, r, HAIR, sheen_col=HAIR_SHEEN)
    # A single thin gold cord-band cinching the bead (the only gold here — keeps the
    # bead the DARK beat while still tying it to the gold-trim language above).
    band = pygame.Rect(int(cx - r * 1.02), int(cy - r * 0.20), int(r * 2.04), int(r * 0.40))
    pygame.draw.ellipse(surf, GOLD_DK, band)
    pygame.draw.ellipse(surf, GOLD, band.inflate(-int(r * 0.5), -int(r * 0.14)))


def _charm_cord(surf, top_x, top_y, length, hw, ss, *, n_tiles, wave=0.0, phase=0.0,
                cap=True, night=False):
    """The charm-CORD streaming straight DOWN: a thin dark-red cord strung with an
    o-fuda + a bead-knot per tile (the band that TILES for the pillar), tapering as
    it falls. `cap=True` hangs a tassel + warding-bell at the bottom (the gap-edge
    cap business end)."""
    def _x_at(t):
        return top_x + wave * hw * math.sin(t * math.pi * 2.2 + phase) * (0.35 + 0.65 * t)

    # The cord itself — a thin tapering dark-red line.
    pts = []
    steps = 36
    for i in range(steps + 1):
        t = i / steps
        pts.append((_x_at(t), top_y + length * t))
    pygame.draw.lines(surf, CORD_DK, False, [(int(x), int(y)) for x, y in pts],
                      max(2, int(3.0 * ss)))
    pygame.draw.lines(surf, CORD, False, [(int(x), int(y)) for x, y in pts],
                      max(1, int(1.8 * ss)))

    # Per-tile charms: a LIGHT o-fuda high then a DARK bead-knot low, with a bare-cord
    # gap before the next tile so the light-then-dark rhythm + seam read down the trail.
    for i in range(n_tiles):
        t0 = (i + 0.26) / n_tiles
        t1 = (i + 0.62) / n_tiles
        scale = 1.0 - 0.34 * ((i + 0.5) / n_tiles)
        ox, oy = _x_at(t0), top_y + length * t0
        bx, by = _x_at(t1), top_y + length * t1
        _ofuda(surf, ox, oy, hw * 2.1 * scale, hw * 2.6 * scale, ss)
        _bead_knot(surf, bx, by, hw * 0.70 * scale, ss)

    if cap:
        _tassel_bell(surf, _x_at(1.0), top_y + length, hw, ss, point_up=False, night=night)


def _tassel_bell(surf, cx, base_y, hw, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: a gold warding-BELL on-axis with a hanging tassel,
    radiating warm INTO the gap. `point_up` orients the bell toward the gap. Modest
    width — never a top-heavy medallion."""
    d = -1 if point_up else 1
    # Warm glow halo at the bell.
    bell_y = base_y + d * hw * 2.2
    glow_r = int(hw * (3.4 if night else 2.6))
    gl = make_glow_surface(glow_r, GOLD, alpha_center=200 if night else 130, falloff=2.2)
    surf.blit(gl, (int(cx - glow_r), int(bell_y - glow_r)), special_flags=pygame.BLEND_ADD)

    # The warding-bell as an unmistakable BELL silhouette (round 1's dome read as a
    # coin): a tapered shoulder rising to a small crown loop, flaring OUT to a wide
    # lip at the gap-facing mouth — a clear trapezoid-bell beat, plus a vertical seam
    # + clapper so it rhymes with the bead-knots above and never reads as a disc.
    bw, bh = hw * 2.0, hw * 2.4
    shoulder_y = bell_y - d * bh * 0.30
    lip_y = bell_y + d * bh * 0.48
    body = [
        (cx - bw * 0.34, shoulder_y),          # narrow shoulder
        (cx + bw * 0.34, shoulder_y),
        (cx + bw * 0.62, lip_y),               # flares out to the mouth
        (cx - bw * 0.62, lip_y),
    ]
    pygame.draw.polygon(surf, GOLD_DK, [(int(x), int(y)) for x, y in body])
    inner = [
        (cx - bw * 0.26, shoulder_y + d * bh * 0.04),
        (cx + bw * 0.26, shoulder_y + d * bh * 0.04),
        (cx + bw * 0.52, lip_y - d * bh * 0.06),
        (cx - bw * 0.52, lip_y - d * bh * 0.06),
    ]
    pygame.draw.polygon(surf, GOLD, [(int(x), int(y)) for x, y in inner])
    # Rounded crown cap + small suspension loop at the top of the bell.
    pygame.draw.ellipse(surf, GOLD_DK,
                        (int(cx - bw * 0.36), int(shoulder_y - hw * 0.5),
                         int(bw * 0.72), int(hw * 0.8)))
    pygame.draw.circle(surf, GOLD,
                       (int(cx), int(shoulder_y - d * hw * 0.6)), max(2, int(hw * 0.30)))
    pygame.draw.circle(surf, GOLD_DK,
                       (int(cx), int(shoulder_y - d * hw * 0.6)), max(1, int(hw * 0.14)))
    # Flared mouth lip band (a wider rim at the gap-facing edge).
    pygame.draw.ellipse(surf, GOLD_DK,
                        (int(cx - bw * 0.70), int(lip_y - hw * 0.28),
                         int(bw * 1.40), int(hw * 0.7)))
    pygame.draw.ellipse(surf, GOLD,
                        (int(cx - bw * 0.60), int(lip_y - hw * 0.20),
                         int(bw * 1.20), int(hw * 0.46)))
    # A vertical seam down the bell body (the casting line — the bell-reading beat).
    pygame.draw.line(surf, GOLD_DK, (int(cx), int(shoulder_y)),
                     (int(cx), int(lip_y - d * hw * 0.10)), max(1, int(1.4 * ss)))
    # Wet-gold sheen run on the left shoulder.
    pygame.draw.line(surf, GOLD_SHEEN,
                     (int(cx - bw * 0.18), int(shoulder_y + d * bh * 0.06)),
                     (int(cx - bw * 0.40), int(lip_y - d * bh * 0.10)),
                     max(2, int(1.8 * ss)))
    # Clapper / ringing dot hanging at the bell mouth.
    pygame.draw.circle(surf, _shade_c(GOLD_DK, -18),
                       (int(cx), int(lip_y + d * hw * 0.14)), max(2, int(hw * 0.24)))

    # The hanging tassel: a coral cord-bind then a fan of strands, on-axis below the
    # bell (toward the gap). Tassel is the soft creature-derived spill that LIGHTS
    # the gap edge without a heavy cap.
    tass_y = lip_y + d * hw * 0.6
    # Coral bind knot.
    _triad_circle(surf, cx, tass_y, hw * 0.5, CORAL, sheen_d=32)
    n = 7
    for i in range(n):
        t = (i / (n - 1)) - 0.5
        sx = cx + t * hw * 1.5
        ex = cx + t * hw * 2.0
        ey = tass_y + d * hw * (2.4 - abs(t) * 1.2)
        pygame.draw.line(surf, CORAL_DK, (int(sx), int(tass_y)), (int(ex), int(ey)),
                         max(2, int(2.2 * ss)))
        pygame.draw.line(surf, CORAL, (int(sx), int(tass_y)), (int(ex), int(ey)),
                         max(1, int(1.2 * ss)))


# ── the whole creature: head + charm-cord, on one surface ────────────────────

def build_nukekubi(scale=1.0, ss=6, *, night=False, compact=False):
    """The full creature on its own transparent surface: the ornate coiffed court-
    lady head up top (DOMINANT black top-knot + gold kanzashi fan, MINOR powder face,
    coral flame collar), a charm-cord streaming straight down beneath it tipped with a
    tassel + warding-bell. Returns an outlined surface.

    Elevated/epic: rendered at SS=6 then smoothscaled — crisp at downscale.

    `compact` is the GAMEPLAY / 32px-icon variant: the HEAD dominates the vertical
    budget, the cord is cut short, and the face bakes a low-res tell so the icon reads
    'black crown + gold fan + coral band' at 1x — never inverts to a thin cord +
    speck."""
    head_r = int(40 * scale) * ss
    trail_mult = 1.25 if compact else 2.7
    trail_len = int(head_r * trail_mult)
    n_tiles = 2 if compact else 4
    side_pad = int(34 * scale) * ss          # room for the wide kanzashi fan
    top_pad = int(40 * scale) * ss           # room for the tall top-knot + pins
    bot_pad = int(16 * scale) * ss

    head_cx_off = side_pad + head_r + int(8 * scale) * ss
    # The face oval sits LOW; the head "centre" is the face centre so the knot + pins
    # tower above it (the dominant mass is up top, the small face is mid-low).
    head_cy = top_pad + head_r * 1.7

    # The flame collar sits just under the jaw; the cord springs from below it.
    collar_y = head_cy + head_r * 0.86
    trail_top_y = collar_y + head_r * 0.42
    feet_y = trail_top_y + trail_len

    W = int(head_cx_off * 2)
    H = int(feet_y + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # The charm-cord first so the collar/face occlude its springing point.
    hw = head_r * 0.30
    _charm_cord(surf, cx, trail_top_y, trail_len, hw, ss,
                n_tiles=n_tiles, wave=0.6 if compact else 0.9,
                phase=0.5, cap=True, night=night)

    # Kanzashi fan FIRST (behind the knot) so the bun occludes the pin roots.
    _kanzashi(surf, cx, head_cy - head_r * 1.0, head_r, ss)
    # Top-knot (dominant black mass) over the pin roots.
    _topknot(surf, cx, head_cy - head_r * 0.46, head_r, ss)
    # The small powder face, set low + tucked under the swept hair.
    face_r = head_r * 0.62
    face_cy = head_cy + head_r * 0.10
    _face(surf, cx, face_cy, face_r, ss, night=night, tell=compact)
    # A dark ink neck-shadow notch under the chin: round 1 let the powder face mush
    # into the same-value coral collar at 32px. This crisp dark crescent holds the
    # chin/jaw edge so the face stays a clean lozenge sitting ON the collar.
    chin_y = face_cy + face_r * 0.86
    notch = pygame.Rect(int(cx - face_r * 0.70), int(chin_y - face_r * 0.34),
                        int(face_r * 1.40), int(face_r * 0.74))
    pygame.draw.ellipse(surf, INK, notch)
    pygame.draw.ellipse(surf, _shade_c(CORAL_DK, -20),
                        notch.inflate(-int(face_r * 0.18), -int(face_r * 0.22)))
    # Coral flame collar under the jaw (drawn last so flames lick over the chin).
    _flame_collar(surf, cx, collar_y, head_r * 0.74, ss, night=night)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _cord_column(surf, cx, top_y, bot_y, hw, ss):
    """The repeatable PILLAR BODY: the charm-cord as a straight tiling shaft — a thin
    dark-red cord with exactly one o-fuda + one bead-knot per tile (the band that
    mirrors top<->bottom). Drawn vertical (no wave) so it tiles cleanly along the
    post."""
    length = bot_y - top_y
    pygame.draw.line(surf, CORD_DK, (int(cx), int(top_y)), (int(cx), int(bot_y)),
                     max(2, int(3.4 * ss)))
    pygame.draw.line(surf, CORD, (int(cx), int(top_y)), (int(cx), int(bot_y)),
                     max(1, int(2.0 * ss)))
    # One tile = one LIGHT o-fuda then one DARK bead-knot, with a clear bare-cord gap
    # at the seam so the repeat boundary is unmistakable at 1x. o-fuda sits high in the
    # tile, bead low, leaving a visible cord run between successive tiles.
    band = hw * 6.4
    n = max(1, int(length / band))
    band = length / n
    for i in range(n):
        oy = top_y + (i + 0.28) * band
        by = top_y + (i + 0.66) * band
        _ofuda(surf, cx, oy, hw * 2.1, hw * 2.6, ss)
        _bead_knot(surf, cx, by, hw * 0.74, ss)


def _cord_pillar_obstacle(height, ss, *, flip, night=False):
    """One charm-cord PILLAR obstacle: the o-fuda+bead cord fills the post and a
    tassel + warding-bell CAP sits at the GAP-facing edge, radiating INTO the gap.
    `flip=True` is the TOP pillar — cap at the bottom (gap) edge, bell pointing DOWN;
    `flip=False` is the BOTTOM pillar — cap at the TOP (gap) edge, bell pointing UP.
    Both mirror the same tile into a clean vertical charm-pillar lanterned at the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 9 * ss
    cap_band = int(58 * ss)
    if flip:
        _cord_column(surf, cx, 0, bh - cap_band, hw, ss)
        _tassel_bell(surf, cx, bh - cap_band, hw, ss, point_up=False, night=night)
    else:
        _cord_column(surf, cx, cap_band, bh, hw, ss)
        _tassel_bell(surf, cx, cap_band, hw, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    return _add_outline(out)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(245, 240, 230)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot, *, stars=False):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    if stars:
        import random as _r
        rng = _r.Random(77)
        for _ in range(26):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, int(h * 0.7))
            pygame.draw.circle(s, (220, 230, 255), (sx, sy), rng.choice((1, 1, 2)))
    return s


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1180, 780
    sheet = pygame.Surface((SW, SH))
    sheet.fill((58, 58, 62))          # neutral grey bg per brief
    _label(sheet, font,
            "NUKEKUBI  —  leyak-EPIC #5  —  court-lady detached head: black top-knot + gold kanzashi + coral flame-collar  —  round 2", 18, 12)
    _label(sheet, small,
            "epic pipeline: hero SS=6 -> smoothscale (crisp at downscale). Face mass <=25% of head; demure half-lid eyes + bow-mouth (NO grin, NO ash). Black/gold/coral carry the 32px read.",
            18, 32, (212, 212, 216))

    # — Cell A: hero at LARGE showcase scale, on a dusk sky.
    panel = pygame.Rect(18, 56, 360, 600)
    bgA = _sky(panel.w, panel.h, (52, 34, 64), (120, 70, 96), (212, 138, 132))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (150, 110, 110), panel, 2, border_radius=8)
    boss = build_nukekubi(scale=2.0, ss=6)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2, panel.y + 44))
    _label(sheet, font, "(a) HERO  big scale (SS=6)", panel.x + 8, panel.y + 8)
    _label(sheet, small, "5 BOLD pins fused into the crown; tiny powder face on an inked chin notch; coral flame collar",
           panel.x + 8, panel.y + 26, (255, 224, 210))

    # — Cell B: charm-cord as a tileable PILLAR pair at TRUE obstacle scale, MIRRORED,
    #   on NIGHT, plus a 2x zoom on the CAP band proving the tassel+bell lights the gap.
    panelB = pygame.Rect(394, 56, 360, 600)
    bg = _sky(panelB.w, panelB.h, (8, 8, 30), (20, 18, 54), (42, 30, 70), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (150, 110, 110), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE scale (NIGHT)", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "1 o-fuda + 1 bead-knot per repeat; mirrored top<->bottom",
           panelB.x + 8, panelB.y + 26, (255, 224, 210))

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 490
    slice_x = panelB.x + 24
    slice_y = panelB.y + 56
    gap_top = 158
    gap_h = 128
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _cord_pillar_obstacle(top_h, 3, flip=True, night=True)
    bot_pillar = _cord_pillar_obstacle(bot_h, 3, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (220, 190, 190), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x: LIGHT o-fuda -> DARK bead", slice_x - 2, slice_y + slice_h + 6, (235, 210, 205))
    _label(sheet, small, "rhythm w/ seam gap; bell lights gap", slice_x - 2, slice_y + slice_h + 22, (255, 226, 200))

    cap_band = 58
    zw, zh = pw, 170
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 12
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 184
    zy = panelB.y + 110
    zbg = _sky(zw * 2, zh * 2, (8, 8, 30), (16, 14, 46), (30, 22, 60))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (220, 190, 190), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "tassel + warding-bell on-axis", zx - 2, zy + zh * 2 + 6, (255, 226, 200))
    _label(sheet, small, "radiates INTO the gap (no top-heavy cap)", zx - 2, zy + zh * 2 + 22, (255, 226, 200))

    # — Cell C: TRUE 32px gameplay-scale chips on day + night, then a 4x audit.
    panelC = pygame.Rect(770, 56, 392, 600)
    pygame.draw.rect(sheet, (44, 44, 48), panelC, border_radius=8)
    pygame.draw.rect(sheet, (150, 110, 110), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) GAMEPLAY 32px  —  day + night", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "black knot + gold pins + coral collar carry the read, not the face",
           panelC.x + 8, panelC.y + 26, (255, 224, 210))

    # Larger compact preview on day/night so the read is visible.
    boss1x = build_nukekubi(scale=0.70, ss=6, compact=True)
    boss1x_n = build_nukekubi(scale=0.70, ss=6, night=True, compact=True)
    day = _sky(180, 320, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 320, (8, 8, 30), (20, 18, 54), (42, 30, 70), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2, dy + 8))
    sheet.blit(boss1x_n, (panelC.x + 200 + 90 - boss1x_n.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 30, 26))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (255, 226, 200))

    # TRUE 32px chips on day + night sky, shown at 1x (honest at-scale read).
    gy = dy + 332
    _label(sheet, small, "TRUE 32px chips (1x, on sky):", panelC.x + 14, gy - 2, (235, 214, 206))
    icon_src = build_nukekubi(scale=1.0, ss=6, compact=True)
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * (32 / icon_src.get_height()))), 32))
    icon64 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * (64 / icon_src.get_height()))), 64))

    chip_w, chip_h = 110, 96
    daychip = pygame.Rect(panelC.x + 14, gy + 16, chip_w, chip_h)
    nightchip = pygame.Rect(panelC.x + 14 + chip_w + 14, gy + 16, chip_w, chip_h)
    dchipbg = _sky(chip_w, chip_h, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    nchipbg = _sky(chip_w, chip_h, (8, 8, 30), (20, 18, 54), (42, 30, 70), stars=True)
    sheet.blit(dchipbg, daychip.topleft)
    sheet.blit(nchipbg, nightchip.topleft)
    sheet.blit(icon32, (daychip.centerx - icon32.get_width() // 2,
                        daychip.centery - icon32.get_height() // 2))
    icon32n = pygame.transform.smoothscale(
        build_nukekubi(scale=1.0, ss=6, night=True, compact=True),
        icon32.get_size())
    sheet.blit(icon32n, (nightchip.centerx - icon32n.get_width() // 2,
                         nightchip.centery - icon32n.get_height() // 2))
    pygame.draw.rect(sheet, (150, 110, 110), daychip, 1, border_radius=4)
    pygame.draw.rect(sheet, (150, 110, 110), nightchip, 1, border_radius=4)
    _label(sheet, small, "32px DAY", daychip.x + 4, daychip.y + 2, (20, 30, 26))
    _label(sheet, small, "32px NIGHT", nightchip.x + 4, nightchip.y + 2, (255, 226, 200))

    # 4x nearest-neighbour blow-up of the true-32 icon so the stack is auditable.
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    bx = panelC.x + 14
    by = gy + 16 + chip_h + 22
    pygame.draw.rect(sheet, (90, 90, 96),
                     (bx - 4, by - 4, blow.get_width() + 8, blow.get_height() + 8),
                     border_radius=4)
    sheet.blit(blow, (bx, by))
    _label(sheet, small, "4x blow-up of the 32px icon", bx, by + blow.get_height() + 4, (235, 214, 206))
    # 64px mid read beside it.
    mx = bx + blow.get_width() + 26
    pygame.draw.rect(sheet, (90, 90, 96),
                     (mx - 4, by - 4, icon64.get_width() + 8, icon64.get_height() + 8),
                     border_radius=4)
    sheet.blit(icon64, (mx, by))
    _label(sheet, small, "64px", mx, by + icon64.get_height() + 4, (235, 214, 206))

    # — Footer captions.
    _label(sheet, small,
           "STAY: flat saturated fills; hard 1-2px ink keyline (28,22,30); dark-core->flat-fill->top-left rim-sheen triad; 1px grown outline; chibi; scary-CUTE; procedural-only.",
           18, SH - 64, (212, 212, 216))
    _label(sheet, small,
           "ELEVATED: SS=6 supersample + richer triad (wet-lacquer knot sheen, gold pin triad, lobed coral flame, gold-trim o-fuda) + stronger glow than source Leyak.",
           18, SH - 44, (212, 212, 216))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()

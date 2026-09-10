"""Look-dev sheet for the Skybit DEVIL boss — GROUP B take B6 "GLITCHFIEND".

A holographic ARCADE devil: a neon synthwave demon glowing electric, all 80s
laser horns and grid-seam scanlines. The set's ONLY luminous/tech devil and ONLY
neon palette — a modern Skybit wink that stress-tests the house triad against glow.

House style this obeys (the warren-clown / Big-Reapy grammar) — the headline
guardrail for B6 is that glow is an ACCENT, not the construction:
  - CHIBI proportions, but ANGULAR/geometric (faceted polygons, no soft curves).
  - The body is built FLAT-FIRST: a near-black void fill + a hard 1-2px ink
    keyline, then deep-magenta facet planes laid as flat polygons. This is the
    grayscale-legible shape; it reads with the glow stripped.
  - Form via the house triad re-cast for neon: dark-core (void) -> flat magenta
    fill -> top-left rim picked out as a CRISP electric edge (the "sheen" is a
    neon edge-line, not a soft sheen blob).
  - The neon = FLAT bright edge-SHAPES (1-2px cyan/magenta strokes + tube cores)
    with a TIGHT outside BLEND_ADD bloom — crisp tube, not a blurry cloud. Glow
    radius is kept small + falloff steep so it stays house-crisp on a night sky.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask (parrot recipe).
  - SUPERSAMPLE then smoothscale.

Set-wide guardrails honoured: (1) horns are SHARP swept LASER triangles, NOT a
curved ram pair; (2) the palette is electric magenta/cyan + near-black void —
deliberately kept off Baalgoat's warm torch-gold and Pyrecrown's green soul-fire
(no warm flame, no green anywhere). The cocky finger-gun grin + one glitch-doubled
horn keep it scary-CUTE, not occult-grim.

Prop -> pillar mirror: the LIGHT-TRIDENT. The glowing laser-rod with pulsing grid
bands is the tileable PILLAR BODY; the three-prong energy fork is a detachable
gap-edge CAP. Mirrors top<->bottom into a clean neon post with the prongs
flourishing INTO the gap. Distinct from B1's iron pitchfork (this is pure glow
geometry, a wider 3-prong energy spread).

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/render_skybit_devil_glitchfiend.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── "neon synthwave" palette (B6) ────────────────────────────────────────────
# Near-black VOID body so the figure reads as a hard silhouette first (the glow
# is an accent over this, never the construction). Hot-magenta facet fill, with
# electric-cyan as the rim/grid accent. Deliberately NO warm flame-gold (Baalgoat)
# and NO green soul-fire (Pyrecrown) — the set's only electric palette.
VOID        = (18, 14, 30)      # near-black body fill / value anchor
VOID_DK     = (10, 8, 20)       # deepest core / facet shadow
MAGENTA     = (232, 40, 140)    # hot-magenta dominant facet fill
MAGENTA_DK  = (150, 20, 96)     # deep-magenta facet shade
MAGENTA_HOT = (255, 110, 190)   # blown-out magenta edge before white
CYAN        = (56, 224, 232)    # electric-cyan grid + rim accent
CYAN_HOT    = (170, 248, 252)   # cyan tube near-white core
VIOLET      = (132, 60, 220)    # neon-violet secondary facet
LASER_YEL   = (248, 228, 72)    # laser-yellow pinprick eyes (the only warm note)
SHEEN_WHITE = (236, 240, 255)   # white-hot tube highlight

INK         = (28, 22, 30)      # the house keyline


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


def _neon_line(surf, a, b, color, core, ss, *, w=3.0, glow=True, glow_r=None):
    """A CRISP neon tube edge: a tight outside BLEND_ADD bloom (small radius,
    steep falloff so it stays house-crisp not a blurry cloud), then a hard flat
    coloured stroke, then a near-white tube core on top. The glow is the accent;
    the flat stroke is the shape. Used for grid seams, horn edges, prong rails.

    Radius is kept small and falloff steep on purpose: the round-1 sheet bloomed
    into a pink/cyan wash that ate the silhouette, so the bloom must stay a hair-
    line halo hugging the stroke, never a soft cloud spilling across the body."""
    ax, ay = int(a[0]), int(a[1])
    bx, by = int(b[0]), int(b[1])
    if glow:
        gr = int(glow_r if glow_r is not None else max(3, w * 1.5) * ss)
        g = make_glow_surface(gr, color, alpha_center=92, falloff=3.4)
        # Stamp the tight bloom along the segment at a few sample points.
        n = max(2, int(math.hypot(bx - ax, by - ay) / max(1, gr * 0.7)))
        for i in range(n + 1):
            t = i / n
            px = ax + (bx - ax) * t
            py = ay + (by - ay) * t
            surf.blit(g, (int(px - gr - 1), int(py - gr - 1)),
                      special_flags=pygame.BLEND_ADD)
    pygame.draw.line(surf, color, (ax, ay), (bx, by), max(1, int(w * ss)))
    pygame.draw.line(surf, core, (ax, ay), (bx, by), max(1, int(w * 0.42 * ss)))


def _neon_poly_edge(surf, pts, color, core, ss, *, w=2.6):
    """A crisp neon outline around a closed flat facet (tube edge per side)."""
    for i in range(len(pts)):
        _neon_line(surf, pts[i], pts[(i + 1) % len(pts)], color, core, ss,
                   w=w, glow=True)


def _facet(surf, pts, fill, *, ink=True, ss=3):
    """A flat angular facet plane: hard ink keyline + flat fill. The FLAT-FIRST
    construction that carries the grayscale read before any glow is added."""
    ipts = [(int(x), int(y)) for x, y in pts]
    if ink:
        pygame.draw.polygon(surf, INK, ipts)
        # Inset the fill by ~1px so a thin ink keyline shows between facets.
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        inset = [(x + (cx - x) * 0.06, y + (cy - y) * 0.06) for x, y in pts]
        pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in inset])
    else:
        pygame.draw.polygon(surf, fill, ipts)


# ── the angular neon devil head + body ────────────────────────────────────────

def _laser_horn(surf, base_x, base_y, r, ss, *, side, glitch=False):
    """A SHARP swept laser horn: a hard triangular blade sweeping up-and-out (NOT
    a curved ram). Built as a flat near-black facet with a magenta inner plane,
    then a crisp cyan tube along the leading edge. `glitch` draws a faint offset
    duplicate (the buggy-hologram cute beat). Horns are deliberately STRAIGHT/
    angular to dodge the set-wide ram-horn collision."""
    s = side
    # Sweep up and outward, sharp tip. Three points -> a clean angular blade.
    tip = (base_x + s * r * 1.05, base_y - r * 1.9)
    out = (base_x + s * r * 0.92, base_y - r * 0.05)
    inn = (base_x + s * r * 0.18, base_y - r * 0.32)
    pts = [inn, out, tip]
    _facet(surf, pts, VOID, ss=ss)
    # Inner magenta sliver kept SMALL (a lit accent on a near-black blade), so the
    # horn reads as dark with neon piping rather than a solid magenta spike.
    mp = [(base_x + s * r * 0.42, base_y - r * 0.46),
          (base_x + s * r * 0.66, base_y - r * 0.34),
          (base_x + s * r * 0.96, base_y - r * 1.55)]
    _facet(surf, mp, MAGENTA_DK, ink=False, ss=ss)
    # Crisp cyan tube along the leading (outer) edge — the laser read.
    _neon_line(surf, out, tip, CYAN, CYAN_HOT, ss, w=2.4)
    # A magenta tube along the inner edge so the horn glows two-tone.
    _neon_line(surf, inn, tip, MAGENTA_HOT, SHEEN_WHITE, ss, w=2.0)
    if glitch:
        # COMMIT the glitch: a clearly readable cyan ghost-offset of the WHOLE
        # horn blade (both edges, shoved aside + up), not a faint single hairline.
        # This is the buggy-hologram scary-cute beat — it must read as intentional.
        off = s * 9 * ss
        up = 7 * ss
        ghost = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        _neon_line(ghost, (out[0] + off, out[1] - up), (tip[0] + off, tip[1] - up),
                   CYAN, CYAN_HOT, ss, w=2.0, glow=True)
        _neon_line(ghost, (inn[0] + off, inn[1] - up), (tip[0] + off, tip[1] - up),
                   CYAN, CYAN_HOT, ss, w=1.6, glow=True)
        ghost.set_alpha(150)
        surf.blit(ghost, (0, 0))


def _devil_head(surf, cx, cy, r, ss, *, night=False):
    """The angular neon devil head: a faceted near-black diamond-ish skull-plate
    with magenta cheek planes, a cyan grid-seam down the brow, swept laser horns,
    glowing laser-yellow pinprick eyes, and a cocky neon zig-zag grin. Angular
    everywhere — hard polygons, no soft curves — so it reads geometric/tech."""
    # Head silhouette: a hard hexagonal plate (wide brow, tapered angular chin).
    hx = r
    head = [
        (cx - hx * 0.86, cy - r * 0.74),   # upper-left brow
        (cx + hx * 0.86, cy - r * 0.74),   # upper-right brow
        (cx + hx * 0.98, cy - r * 0.04),   # right temple
        (cx + hx * 0.40, cy + r * 1.02),   # lower-right jaw -> chin
        (cx - hx * 0.40, cy + r * 1.02),   # lower-left jaw -> chin
        (cx - hx * 0.98, cy - r * 0.04),   # left temple
    ]
    _facet(surf, head, VOID, ss=ss)

    # VALUE FLIP (the B6 guardrail): the head is a near-black VOID plate first;
    # magenta is confined to ONE narrow lit-side (left) accent wedge — ~30% of
    # the face — so the dark silhouette survives the bright day sky and the
    # glow-strip. The right half stays VOID, the chin a touch of VOID_DK. No
    # full magenta cheeks: that was the round-1 pink blob.
    cheek_l = [(cx - hx * 0.78, cy - r * 0.56), (cx - hx * 0.20, cy - r * 0.34),
               (cx - hx * 0.30, cy + r * 0.40), (cx - hx * 0.84, cy - r * 0.02)]
    _facet(surf, cheek_l, MAGENTA, ink=False, ss=ss)
    # A slim deep-magenta sliver under it keeps the lit side reading as a plane,
    # not a stripe — still a minority of the face area.
    cheek_l2 = [(cx - hx * 0.84, cy - r * 0.02), (cx - hx * 0.30, cy + r * 0.40),
                (cx - hx * 0.36, cy + r * 0.74), (cx - hx * 0.66, cy + r * 0.50)]
    _facet(surf, cheek_l2, MAGENTA_DK, ink=False, ss=ss)
    # The rest of the face stays dark: a VOID_DK shade plane down the right so it
    # reads as faceted volume without adding any bright fill on the shadow side.
    cheek_r = [(cx + hx * 0.10, cy - r * 0.30), (cx + hx * 0.78, cy - r * 0.56),
               (cx + hx * 0.84, cy - r * 0.02), (cx + hx * 0.28, cy + r * 0.70)]
    _facet(surf, cheek_r, VOID_DK, ink=False, ss=ss)

    # Crisp cyan GRID seam — the synthwave scanline tell, now reduced to a single
    # vertical centre seam + ONE horizontal scan-band so it reads as discrete
    # filaments at 1x and never stacks into the round-1 wash.
    _neon_line(surf, (cx, cy - r * 0.66), (cx, cy + r * 0.92), CYAN, CYAN_HOT, ss,
               w=1.6)
    _neon_line(surf, (cx - hx * 0.72, cy - r * 0.04), (cx + hx * 0.72, cy - r * 0.04),
               CYAN, CYAN_HOT, ss, w=1.4)
    # Hard magenta rim-edge up the lit (left) brow only — the neon "rim sheen".
    _neon_line(surf, (cx - hx * 0.86, cy - r * 0.74), (cx - hx * 0.98, cy - r * 0.04),
               MAGENTA_HOT, SHEEN_WHITE, ss, w=2.0)

    # Swept laser horns from the brow corners. RIGHT horn glitch-doubled (cute).
    _laser_horn(surf, cx - hx * 0.62, cy - r * 0.70, r * 0.62, ss, side=-1)
    _laser_horn(surf, cx + hx * 0.62, cy - r * 0.70, r * 0.62, ss, side=1,
                glitch=True)

    # Eyes: angled laser-yellow pinpricks set in dark slot facets — a cocky,
    # narrowed arcade squint (the scary-cute lever). Slanted DOWN-inward = smug.
    eye_dx = r * 0.42
    eye_y = cy - r * 0.06
    for s in (-1, 1):
        ex = cx + s * eye_dx
        slot = [(ex - s * r * 0.26, eye_y - r * 0.04),
                (ex + s * r * 0.22, eye_y - r * 0.20),
                (ex + s * r * 0.20, eye_y + r * 0.10),
                (ex - s * r * 0.24, eye_y + r * 0.14)]
        _facet(surf, slot, VOID_DK, ink=True, ss=ss)
        # Tight laser-yellow glow + hot pinprick (the one warm note, kept tiny).
        g = make_glow_surface(int(r * 0.20), LASER_YEL, alpha_center=160, falloff=3.0)
        surf.blit(g, (int(ex - r * 0.20 - 1), int(eye_y - r * 0.20 - 1)),
                  special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surf, LASER_YEL, (int(ex), int(eye_y)),
                           max(2, int(r * 0.12)))
        pygame.draw.circle(surf, SHEEN_WHITE, (int(ex - s * r * 0.04), int(eye_y - r * 0.04)),
                           max(1, int(r * 0.05)))

    # The cocky grin: a BOLDER, fewer-segment cyan ZIG (angular, not a curve) with
    # one corner cocked sharply up — a smug arcade smirk, not a horror rictus. Set
    # against a dark under-jaw so the high-contrast neon zig carries attitude at 1x.
    gy = cy + r * 0.58
    zig = [(cx - r * 0.40, gy + r * 0.02),
           (cx - r * 0.06, gy + r * 0.18),
           (cx + r * 0.28, gy - r * 0.04),
           (cx + r * 0.52, gy - r * 0.22)]   # last corner cocked sharply up
    for i in range(len(zig) - 1):
        _neon_line(surf, zig[i], zig[i + 1], CYAN_HOT, SHEEN_WHITE, ss, w=2.6)


def _devil_body(surf, cx, neck_y, w, h, ss):
    """The lithe angular body: a faceted near-black chevron torso with a cyan
    CHEVRON-FIN crest at the collar, magenta side planes, and a forked-lightning
    bolt tail. Slim + sharp (opposite mass-language to the heavy takes)."""
    hem_y = neck_y + h
    # Chevron torso silhouette — narrow waist, sharp angular shoulders.
    torso = [
        (cx - w * 0.30, neck_y),
        (cx - w * 0.50, neck_y + h * 0.30),
        (cx - w * 0.26, hem_y),
        (cx + w * 0.26, hem_y),
        (cx + w * 0.50, neck_y + h * 0.30),
        (cx + w * 0.30, neck_y),
    ]
    _facet(surf, torso, VOID, ss=ss)
    # VALUE FLIP: the torso is VOID-dominant. Magenta is one narrow lit wedge down
    # the LEFT front (~30% of the chest), tapering — not a full magenta panel. The
    # rest stays near-black so the chevron silhouette survives day sky + grayscale.
    front = [(cx - w * 0.26, neck_y + ss), (cx - w * 0.02, neck_y + h * 0.16),
             (cx - w * 0.02, hem_y - h * 0.10), (cx - w * 0.22, hem_y - ss)]
    _facet(surf, front, MAGENTA, ink=False, ss=ss)
    # A deep-magenta shade sliver beneath it (third value step, still minority).
    front2 = [(cx - w * 0.22, hem_y - ss), (cx - w * 0.02, hem_y - h * 0.10),
              (cx + w * 0.02, hem_y - ss)]
    _facet(surf, front2, MAGENTA_DK, ink=False, ss=ss)
    # Right side plane kept as VOID_DK shade — dark, no bright fill on the shadow
    # side, so the figure reads dark-with-neon-piping on the bright day sky.
    rside = [(cx + w * 0.02, neck_y + h * 0.16), (cx + w * 0.48, neck_y + h * 0.30),
             (cx + w * 0.24, hem_y - ss), (cx + w * 0.02, hem_y - ss)]
    _facet(surf, rside, VOID_DK, ink=False, ss=ss)

    # Cyan chevron-fin crest at the collar (3 stacked sharp V's) — a sharp tech
    # crest, the body's signature. Flat bright + tight glow.
    for i, sc in enumerate((1.0, 0.66, 0.36)):
        yy = neck_y + h * 0.02 + i * h * 0.085
        _neon_line(surf, (cx - w * 0.30 * sc, yy), (cx, yy + h * 0.10 * sc),
                   CYAN, CYAN_HOT, ss, w=1.8)
        _neon_line(surf, (cx, yy + h * 0.10 * sc), (cx + w * 0.30 * sc, yy),
                   CYAN, CYAN_HOT, ss, w=1.8)

    # Magenta rim-edge down the lit left torso edge (the neon "sheen").
    _neon_line(surf, (cx - w * 0.30, neck_y + h * 0.05),
               (cx - w * 0.26, hem_y - ss), MAGENTA_HOT, SHEEN_WHITE, ss, w=1.8)

    # ONE grid scan-band across the torso (round 1 stacked too many into noise).
    yy = neck_y + h * 0.54
    half = w * 0.30
    _neon_line(surf, (cx - half, yy), (cx + half, yy), CYAN, CYAN_HOT, ss, w=1.4)

    # Stub angular arms (one will rest near the trident; the other a finger-gun).
    for s in (-1, 1):
        ax = cx + s * w * 0.46
        ay = neck_y + h * 0.34
        _neon_line(surf, (cx + s * w * 0.28, neck_y + h * 0.18), (ax, ay),
                   MAGENTA, MAGENTA_HOT, ss, w=3.0)
    # A little cyan "finger-gun" cocked off the right hand (cocky arcade beat).
    fg_x = cx + w * 0.46
    fg_y = neck_y + h * 0.34
    _neon_line(surf, (fg_x, fg_y), (fg_x + w * 0.22, fg_y - h * 0.10),
               CYAN, CYAN_HOT, ss, w=2.0)

    # Forked-LIGHTNING-BOLT tail: a hard zig-zag bolt forking into two prongs at
    # the tip (devil spade reimagined as a glitch bolt). Magenta tube.
    tx, ty = cx + w * 0.20, hem_y - h * 0.04
    bolt = [(tx, ty), (tx + w * 0.30, ty + h * 0.18),
            (tx + w * 0.12, ty + h * 0.30), (tx + w * 0.40, ty + h * 0.50)]
    for i in range(len(bolt) - 1):
        _neon_line(surf, bolt[i], bolt[i + 1], MAGENTA_HOT, SHEEN_WHITE, ss, w=2.4)
    # Two-prong fork at the bolt tip (the devil-tail spade as a split bolt).
    btip = bolt[-1]
    _neon_line(surf, btip, (btip[0] + w * 0.12, btip[1] + h * 0.06),
               CYAN, CYAN_HOT, ss, w=2.0)
    _neon_line(surf, btip, (btip[0] + w * 0.02, btip[1] + h * 0.14),
               CYAN, CYAN_HOT, ss, w=2.0)


def build_glitchfiend(scale=1.0, ss=3, *, night=False):
    """The full boss figure on its own transparent surface. Lithe angular build:
    sharp faceted head with swept laser horns, chevron neon body, bolt tail.
    Returns an outlined surface and its baseline (feet) y for placement."""
    H = int(260 * scale)
    W = int(190 * scale)
    pad = int(80 * scale)
    surf = pygame.Surface(((W + pad * 2) * ss, (H + pad) * ss), pygame.SRCALPHA)
    cx = (W // 2 + pad) * ss

    head_band = int(H * 0.50) * ss
    head_r = head_band * 0.40
    head_cy = int(pad * 0.42) * ss + head_r * 1.4   # leave room for the tall horns
    head_cx = cx

    neck_y = head_cy + head_r * 1.05
    body_w = W * 0.66 * ss
    body_h = int(H * 0.42) * ss

    # The light-trident held upright at the figure's right; rod runs past the feet,
    # the energy prongs rise above the head.
    tx = cx + W * 0.42 * ss
    thw = 6 * ss
    prong_base = head_cy - head_r * 0.4
    feet_y = neck_y + body_h
    _light_rod(surf, tx, prong_base, feet_y + 10 * ss, thw, ss)
    _light_prongs(surf, tx, prong_base, thw, ss, point_up=True)

    _devil_body(surf, head_cx, neck_y, body_w, body_h, ss)
    _devil_head(surf, head_cx, head_cy, head_r, ss, night=night)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallsurf = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallsurf), feet_y / ss


# ── the light-trident prop (and its pillar-tile components) ───────────────────

def _light_rod(surf, cx, top_y, bot_y, hw, ss):
    """The glowing laser-ROD = the tileable PILLAR BODY: a near-black faceted post
    with a bright magenta tube edge each side and PULSING cyan grid BANDS rung
    across it. The bands are bold + few (so 3-4 ring a gameplay pillar and survive
    smoothscale), each a flat cyan bar + tight glow — a synthwave power-conduit.
    No prongs here; the prongs are the detachable top cap."""
    length = bot_y - top_y
    # VALUE FLIP for the rod: it is a DARK VOID post, not a pale white stick. The
    # whole interior stays near-black; only a SLIM lit-side magenta sliver hints at
    # volume. This makes the rod read as a dark conduit distinct from the boss's
    # bright highlights (round 1 read as a white thermometer).
    post = [(cx - hw, top_y), (cx + hw, top_y),
            (cx + hw, bot_y), (cx - hw, bot_y)]
    _facet(surf, post, VOID, ss=ss)
    # A thin lit magenta sliver down the LEFT inner rail only (a minority accent).
    pygame.draw.rect(surf, MAGENTA_DK,
                     (int(cx - hw * 0.86), int(top_y), int(hw * 0.36), int(length)))
    # BOLD magenta tube RAILS down both edges — the conduit's signature piping.
    _neon_line(surf, (cx - hw, top_y), (cx - hw, bot_y), MAGENTA_HOT, SHEEN_WHITE,
               ss, w=2.6)
    _neon_line(surf, (cx + hw, top_y), (cx + hw, bot_y), MAGENTA, MAGENTA_HOT,
               ss, w=2.4)
    # 3-4 BOLD cyan grid bands rung across the dark post — chunky bars (not thin
    # lines) so they survive the 1x downscale and read as discrete pulses. Spaced
    # so a gameplay pillar carries 3-4 of them.
    band_h = max(int(34 * ss), int(hw * 3.6))
    n = max(2, min(4, round(length / band_h)))
    band_h = length / n
    bar_t = max(2, int(3.4 * ss))   # the band's flat fill thickness
    for i in range(n):
        by = top_y + (i + 0.5) * band_h
        # Brightness "pulses" along the rod (a hologram throb) — alternate hot/cool.
        hot = (i % 2 == 0)
        col = CYAN_HOT if hot else CYAN
        core = SHEEN_WHITE if hot else CYAN_HOT
        # Tight glow first, then a BOLD flat cyan bar so the band is a solid rung.
        _neon_line(surf, (cx - hw * 0.92, by), (cx + hw * 0.92, by),
                   col, core, ss, w=3.4, glow_r=int(hw * 1.0))
        pygame.draw.rect(surf, col,
                         (int(cx - hw * 0.92), int(by - bar_t * 0.5),
                          int(hw * 1.84), bar_t))


def _light_prongs(surf, cx, base_y, hw, ss, *, point_up=True):
    """The three-prong ENERGY fork = the detachable PILLAR TOP CAP that rides the
    gap-edge only. Three sharp laser tines (a wider 3-prong spread vs B1's iron
    pitchfork) of pure glow, fanning out then aiming forward, with a bright
    energy-orb caught between them. `point_up` orients the tines away from the rod
    (toward the gap). Mirrors with the rod into a clean neon post."""
    d = -1 if point_up else 1
    # Shorter + thicker tines with a WIDER splay so the trident cap silhouette is
    # unmistakable at 82px (round 1 read as thin spidery legs).
    prong_len = 40 * ss
    spread = hw * 3.4
    tips = []
    # Three tines: centre straight, two flanking ones angled out with conviction.
    for off in (-1, 0, 1):
        bx = cx + off * spread * 0.34
        tipx = cx + off * spread
        tipy = base_y + d * prong_len
        midx = (bx + tipx) * 0.5
        midy = base_y + d * prong_len * 0.5
        # A hard kinked laser tine, drawn THICK so it survives the downscale.
        _neon_line(surf, (bx, base_y), (midx, midy), CYAN, CYAN_HOT, ss, w=3.6)
        _neon_line(surf, (midx, midy), (tipx, tipy), MAGENTA_HOT, SHEEN_WHITE, ss,
                   w=3.6)
        # Sharp tip glint.
        g = make_glow_surface(int(hw * 1.1), CYAN_HOT, alpha_center=140, falloff=3.0)
        surf.blit(g, (int(tipx - hw * 1.1 - 1), int(tipy - hw * 1.1 - 1)),
                  special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surf, SHEEN_WHITE, (int(tipx), int(tipy)),
                           max(1, int(hw * 0.5)))
        tips.append((tipx, tipy))
    # A BOLD cross-brace bar of cyan linking the three bases (the trident's head).
    base_l = cx - spread
    base_r = cx + spread
    _neon_line(surf, (base_l, base_y), (base_r, base_y), CYAN, CYAN_HOT, ss, w=2.8)
    # The caught energy ORB — LARGER + BRIGHTER so it is the cap's focal point.
    orb_x = cx
    orb_y = base_y + d * prong_len * 0.50
    orb_r = hw * 1.5
    g = make_glow_surface(int(orb_r * 1.9), MAGENTA, alpha_center=150, falloff=3.0)
    surf.blit(g, (int(orb_x - orb_r * 1.9 - 1), int(orb_y - orb_r * 1.9 - 1)),
              special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, MAGENTA_HOT, (int(orb_x), int(orb_y)), max(2, int(orb_r)))
    pygame.draw.circle(surf, CYAN_HOT, (int(orb_x), int(orb_y - orb_r * 0.2)),
                       max(1, int(orb_r * 0.55)))
    pygame.draw.circle(surf, SHEEN_WHITE, (int(orb_x), int(orb_y - orb_r * 0.28)),
                       max(1, int(orb_r * 0.26)))


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _trident_pillar_obstacle(height, ss, *, flip):
    """One light-trident PILLAR obstacle: the glowing rod fills the post, the
    three-prong energy cap sits at the gap end. `flip` makes the top pillar's
    prongs point DOWN into the gap; the bottom pillar's point UP — proving the
    prop mirrors top<->bottom into a clean neon post with the prongs flourishing
    INTO the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 9 * ss
    cap_band = int(64 * ss)
    _light_rod(surf, cx, 0, bh - cap_band, hw, ss)
    _light_prongs(surf, cx, bh - cap_band, hw, ss, point_up=False)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    out = _add_outline(out)
    if flip:
        out = pygame.transform.flip(out, False, True)
    return out


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(245, 240, 230)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    return s


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((22, 18, 34))
    _label(sheet, font, "GLITCHFIEND  —  B6  —  neon synthwave devil  —  round 2", 18, 12)
    _label(sheet, small,
            "the holographic ARCADE devil: angular neon body, swept LASER horns, chevron crest, bolt tail, light-TRIDENT",
            18, 32, (190, 170, 220))

    # — Cell A: boss at showcase scale, on a dark synthwave panel.
    panel = pygame.Rect(18, 56, 360, 560)
    pygame.draw.rect(sheet, (16, 12, 26), panel, border_radius=8)
    pygame.draw.rect(sheet, (90, 60, 130), panel, 2, border_radius=8)
    # A faint magenta laser-grid floor in the panel so the synthwave context reads.
    for i in range(1, 10):
        gy = panel.bottom - 18 - i * i * 1.4
        if gy < panel.y + 40:
            break
        pygame.draw.line(sheet, (60, 24, 70), (panel.x + 8, int(gy)),
                         (panel.right - 8, int(gy)), 1)
    boss, _ = build_glitchfiend(scale=1.7, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.bottom - boss.get_height() - 16))
    _label(sheet, font, "(a) BOSS  showcase scale", panel.x + 8, panel.y + 8)

    # — Cell B: the light-trident as a tileable PILLAR pair at TRUE obstacle scale.
    panelB = pygame.Rect(394, 56, 360, 560)
    bg = _sky(panelB.w, panelB.h, (10, 8, 32), (30, 20, 70), (60, 36, 110))
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (90, 60, 130), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE obstacle scale", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG                  # 82px — the real obstacle width
    slice_h = 470
    slice_x = panelB.x + 26
    slice_y = panelB.y + 46
    gap_top = 168
    gap_h = 120
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _trident_pillar_obstacle(top_h, 3, flip=True)
    bot_pillar = _trident_pillar_obstacle(bot_h, 3, flip=False)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (255, 255, 255), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px wide,", slice_x - 2, slice_y + slice_h + 6, (220, 210, 255))
    _label(sheet, small, "as it scrolls): 3-4 pulse", slice_x - 2, slice_y + slice_h + 22, (220, 210, 255))
    _label(sheet, small, "bands/post", slice_x - 2, slice_y + slice_h + 38, (220, 210, 255))

    # 2x zoom of the GAP region so the energy prongs + grid bands read.
    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    zoom_src.blit(top_pillar, (-2, -(gap_top - 70) - 2))
    zoom_src.blit(bot_pillar, (-2, gap_h + 70 - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 184
    zy = panelB.y + 70
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the gap:", zx - 4, zy - 16, (255, 255, 255))
    _label(sheet, small, "3-prong energy fork", zx - 4, zy + zh * 2 + 6, (220, 210, 255))
    _label(sheet, small, "cradles the core orb;", zx - 4, zy + zh * 2 + 22, (220, 210, 255))
    _label(sheet, small, "top<->bottom mirror", zx - 4, zy + zh * 2 + 38, (220, 210, 255))

    # — Cell C: 1x in-game-scale INSET on BOTH day and night skies.
    panelC = pygame.Rect(770, 56, 392, 560)
    pygame.draw.rect(sheet, (16, 12, 26), panelC, border_radius=8)
    pygame.draw.rect(sheet, (90, 60, 130), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) 1x in-game scale  —  day / night legibility", panelC.x + 8, panelC.y + 8)

    boss1x, _ = build_glitchfiend(scale=0.66, ss=3)
    boss1x_n, _ = build_glitchfiend(scale=0.66, ss=3, night=True)
    # The danger case per the guardrail: cyan/magenta on a BRIGHT day sky.
    day = _sky(180, 250, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 250, (5, 8, 30), (15, 25, 70), (35, 55, 115))
    for sx, sy in ((24, 40), (150, 26), (96, 70), (40, 120), (160, 150), (70, 200)):
        pygame.draw.circle(night, (220, 230, 255), (sx, sy), 1)

    dy = panelC.y + 40
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2,
                        dy + 250 - boss1x.get_height() - 6))
    sheet.blit(boss1x_n, (panelC.x + 200 + 90 - boss1x_n.get_width() // 2,
                          dy + 250 - boss1x_n.get_height() - 6))
    _label(sheet, small, "DAY (the danger case)", panelC.x + 14 + 6, dy + 6, (20, 20, 30))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (210, 220, 255))

    # — Grayscale silhouette check: the FLAT-first void body must carry the read
    #   with the glow stripped (the B6 guardrail that glow is an accent, not the
    #   construction).
    gy = dy + 270
    gray = pygame.Surface((boss1x.get_width(), boss1x.get_height()), pygame.SRCALPHA)
    gray.blit(boss1x, (0, 0))
    arr = pygame.surfarray.pixels3d(gray)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    gpanel = pygame.Rect(panelC.x + 14, gy, 360, 230)
    pygame.draw.rect(sheet, (120, 120, 128), gpanel, border_radius=6)
    sheet.blit(gray, (gpanel.centerx - gray.get_width() // 2,
                      gpanel.bottom - gray.get_height() - 8))
    _label(sheet, small, "grayscale (glow STRIPPED): near-black VOID body dominant -> a clear dark devil silhouette, neon = thin bright filaments only",
            gpanel.x + 6, gpanel.y + 6, (30, 30, 30))

    # — Footer caption.
    _label(sheet, small,
           "scary-cute: cocky finger-gun + narrowed laser-eye squint + a jagged zig-zag grin (one horn glitch-doubled = buggy hologram).",
           18, SH - 124, (200, 186, 226))
    _label(sheet, small,
           "value flip: near-black VOID is the DOMINANT body value; magenta is a ~30% lit-side accent; neon = CRISP filaments + TIGHT additive glow.",
           18, SH - 104, (200, 186, 226))
    _label(sheet, small,
           "guardrails: SHARP swept laser horns (no curved ram); electric magenta/cyan (no warm torch-gold, no green soul-fire).",
           18, SH - 84, (200, 186, 226))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "devil", "glitchfiend")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()

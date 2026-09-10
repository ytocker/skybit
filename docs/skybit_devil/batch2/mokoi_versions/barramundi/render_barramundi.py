"""Look-dev sheet for the Skybit BOSS mokoi-spin-off — "BARRAMUNDI-SPIRIT".

A FLAT-graphic painted x-ray fish-beast, spun off the shipped Mokoi flat-graphic
lineage. Where Mokoi is a front-on plank-MASK, Barramundi is the brood's ONLY
side-on animal AND the only see-through anatomy — the most original KIND of the
five. A chubby wide-eyed fish, adorable, until you read straight through its
hematite-rust body to the glowing pipeclay bones and one bright organ-lozenge.

House style this obeys (the leyak-epic / mokoi flat-graphic dialect):
  - CHIBI proportions — a fat round-bellied fish, oversized wide ring-eye, a tiny
    pursed mouth. Side-on profile so the x-ray cavity is the whole body.
  - FLAT saturated fills. NO within-shape gradients, NO bevels, NO soft edges.
    Detail is carried by PATTERN DENSITY + line-art (spine, ribs, rarrk fin
    hatch, dot-rows), NOT 3D triad shading.
  - Hard ink keyline (40,36,42) inside + a 1px grown outline on the silhouette so
    the fish POPS on any sky (the parrot `_add_outline` recipe).
  - Hematite-RUST is the DOMINANT body mass (the brood's red-earth lane). The
    pipeclay-white rib/organ LATTICE is the protected hue-blind tell — it
    survives a grayscale check on its own. Yellow-ochre is reserved for fin-tips.
    Ember glow is CONFINED to the gap-edge cap.
  - SUPERSAMPLE at SS=5-6 then smoothscale down — crisp geometry at downscale.

X-ray RE-SPEC (the hard one): the rib-lattice is the hero detail but the highest
noise-risk small. So the SPINE is ONE bold thick charcoal line, with 3-4 ribs
MAX per side and exactly ONE clear pipeclay organ-lozenge — NO dense rib-comb
(it greys to mush at 1x). The see-through read must survive at true 32px or the
whole concept's point is lost. The compact icon bakes a low-res x-ray tell
(belly window + spine + one big rib pair + the organ dot) sized to survive.

Prop -> pillar mirror: the fish-trap / WEIR-POLE is the pillar. One rib-ladder
band (echoing the body ribs) + one pipeclay dot-row band per repeat = the tiling
shaft; a small whole x-ray fish-MEDALLION (~strip+30%) = the gap-edge cap, with
the ember glow confined to that cap. Naturally vertical + symmetric — clean
mirror, no top-heavy cap.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/mokoi_versions/barramundi/render_barramundi.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (barramundi-spirit) — hex-exact from the locked brief ─────
# Hematite-RUST is the DOMINANT body mass — the brood's red-earth lane, kept
# clearly distinct from Mokoi's burnt-sienna and the yellow-ochre kinds. The
# charcoal bone-keyline is darker/cooler than the body so the line-art reads as
# ink, not shading. Pipeclay-white is the protected tell — it carries the read
# in grayscale (the rib/organ lattice). Yellow-ochre is reserved for fin-tips
# only. Ember is the lone warm glow, confined to the cap. No triad sheen — FLAT.
RUST        = (158, 72, 52)     # hematite-rust body (dominant, red-earth lane)
RUST_DK     = (118, 50, 38)     # deeper rust for inset wells / belly seam
RUST_HI     = (188, 96, 70)     # a flat lighter rust for graphic separation

CHAR        = (40, 36, 42)      # charcoal bone-keyline (spine + ribs + ink)
CHAR_DK     = (26, 23, 30)      # deeper charcoal for the body keyline mass

PIPECLAY    = (232, 226, 212)   # pipeclay-white rib/organ lattice — the tell
PIPECLAY_DK = (192, 186, 172)   # a quiet shade for dot keylines (still light)

OCHRE       = (206, 150, 72)    # yellow-ochre fin-tips (reserved accent)
OCHRE_DK    = (162, 112, 50)    # deep ochre fin keyline

EMBER       = (236, 138, 58)    # cap-only ember glow core
EMBER_HOT   = (255, 206, 132)   # ember twinkle centre

INK         = (40, 36, 42)      # the house keyline (== charcoal bone-keyline)


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


# ── flat-graphic primitives (NO triad — fills + ink keylines only) ───────────

def _dot_row(surf, cx, y, span_hw, n, r, col, *, key_col=None, ss=3):
    """A single evenly-spaced row of pipeclay dots — part of the protected tell.
    Flat filled circles with an optional 1px lighter keyline so a row reads as
    crisp clean geometry at high res and survives the downscale."""
    if n <= 1:
        xs = [cx]
    else:
        xs = [cx - span_hw + 2 * span_hw * (i / (n - 1)) for i in range(n)]
    for x in xs:
        pygame.draw.circle(surf, col, (int(x), int(y)), int(r))
        if key_col is not None:
            pygame.draw.circle(surf, key_col, (int(x), int(y)), int(r),
                               max(1, int(ss * 0.6)))


def _rarrk_fin(surf, pts, ss, *, base_col, hatch_col, n=4):
    """A flat fin polygon with sparse pipeclay rarrk cross-hatch. The fin is a
    flat ochre-tipped fill; the hatch is a FEW evenly spaced lines clipped to the
    polygon's bounding band — graphic linework, not a dense field that mushes."""
    ipts = [(int(x), int(y)) for x, y in pts]
    pygame.draw.polygon(surf, base_col, ipts)
    # Sparse parallel hatch across the fin's vertical extent (clipped by a temp
    # surface so the lines stay inside the fin shape).
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    clip = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    lw = max(1, int(1.2 * ss))
    for i in range(1, n + 1):
        fx = x0 + (x1 - x0) * (i / (n + 1))
        pygame.draw.line(clip, hatch_col, (int(fx), int(y0)),
                         (int(fx - (x1 - x0) * 0.18), int(y1)), lw)
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), ipts)
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(clip, (0, 0))
    pygame.draw.polygon(surf, INK, ipts, max(1, int(1.4 * ss)))


# ── the x-ray skeleton (the hero detail — kept deliberately sparse) ──────────

def _xray_skeleton(surf, cx, cy, body_hw, body_hh, ss):
    """The hero see-through detail, drawn DELIBERATELY SPARSE per the re-spec.

    ONE bold BRIGHT pipeclay spine arcing along the body axis (the brightest
    internal mass, beating the eye); 3 bold pipeclay ribs curving down off it,
    each as bright as the spine and clearly separated so the downscale never
    combs them to mush; exactly ONE clear warm-cored pipeclay organ-lozenge in
    the belly. This is what makes the fish see-through and must dominate."""
    # The SPINE must be the BRIGHTEST internal mass — a single thick, unbroken
    # pipeclay bar so it out-values the eye and bakes to a clean ~2px bone at
    # 32px. A thin charcoal centre-stroke reads it as ink-defined bone WITHOUT
    # darkening the bar's overall value (kept much thinner than the pipeclay).
    spine_x0 = cx - body_hw * 0.66
    spine_x1 = cx + body_hw * 0.46
    spine_y = cy - body_hh * 0.30
    spine_pts = []
    n = 18
    for i in range(n + 1):
        t = i / n
        x = spine_x0 + (spine_x1 - spine_x0) * t
        # a gentle downward dip toward the tail so it tracks the body silhouette
        y = spine_y + body_hh * 0.20 * (t * t)
        spine_pts.append((x, y))
    spine_ipts = [(int(x), int(y)) for x, y in spine_pts]
    pygame.draw.lines(surf, PIPECLAY, False, spine_ipts, max(4, int(7.0 * ss)))
    pygame.draw.lines(surf, CHAR_DK, False, spine_ipts, max(1, int(1.6 * ss)))

    # RIBS: drop the BAKE to 3 BOLD ribs per side so the downscale never combs to
    # mush — each rib is a fat pipeclay stroke, as bright as the spine, clearly
    # separated. A thin charcoal keyline keeps it reading as a bone outline.
    ribs = 3
    rib_lw = max(3, int(4.4 * ss))
    rib_key = max(1, int(1.3 * ss))
    for i in range(ribs):
        t = 0.14 + 0.62 * (i / max(1, ribs - 1))
        # anchor on the spine
        ax = spine_x0 + (spine_x1 - spine_x0) * t
        ay = spine_y + body_hh * 0.20 * (t * t)
        # the rib curves down and slightly back toward the belly floor
        rib = []
        m = 10
        reach = body_hh * (1.24 - 0.10 * i)
        for j in range(m + 1):
            u = j / m
            rx = ax - body_hw * 0.10 * u
            ry = ay + reach * u
            rib.append((rx, ry))
        ribpts = [(int(x), int(y)) for x, y in rib]
        pygame.draw.lines(surf, PIPECLAY, False, ribpts, rib_lw)
        pygame.draw.lines(surf, CHAR, False, ribpts, rib_key)

    # The ONE organ-lozenge: a single clear pipeclay belly-organ with a charcoal
    # keyline and a small rust core — the unmistakable internal-organ read that a
    # rib-comb alone never gives. Sits low-front in the belly cavity.
    org_cx = cx - body_hw * 0.18
    org_cy = cy + body_hh * 0.30
    org_rx = body_hw * 0.20
    org_ry = body_hh * 0.30
    org_rect = pygame.Rect(int(org_cx - org_rx), int(org_cy - org_ry),
                           int(2 * org_rx), int(2 * org_ry))
    pygame.draw.ellipse(surf, PIPECLAY, org_rect)
    pygame.draw.ellipse(surf, INK, org_rect, max(1, int(1.6 * ss)))
    # A small warm core inside the lozenge — the single organ reads as the warm
    # focal of the x-ray. A faint ember-tinted pipeclay (NOT a glow ring; the
    # cap keeps the only true ember light) so it stays the warmest internal mass.
    org_warm = lerp_color(PIPECLAY, EMBER, 0.34)
    pygame.draw.ellipse(surf, org_warm,
                        pygame.Rect(int(org_cx - org_rx * 0.52),
                                    int(org_cy - org_ry * 0.52),
                                    int(org_rx * 1.04), int(org_ry * 1.04)))
    pygame.draw.ellipse(surf, RUST_DK,
                        pygame.Rect(int(org_cx - org_rx * 0.30),
                                    int(org_cy - org_ry * 0.30),
                                    int(org_rx * 0.60), int(org_ry * 0.60)))


# ── the chubby x-ray fish ────────────────────────────────────────────────────

def _fish_body_poly(cx, cy, hw, hh):
    """The chubby side-on fish silhouette as a point list: a fat rounded oval
    body that pinches into a caudal peduncle and flares into a forked tail at the
    LEFT, with a small rounded snout at the RIGHT. Returns the closed polygon."""
    pts = []
    n = 40
    for i in range(n + 1):
        a = math.pi * (i / n)          # top arc, snout(right) -> tail(left)
        x = cx + math.cos(a) * hw
        y = cy - math.sin(a) * hh * (0.92 if math.cos(a) > 0 else 1.0)
        pts.append((x, y))
    for i in range(n + 1):
        a = math.pi + math.pi * (i / n)  # bottom arc, tail(left) -> snout(right)
        x = cx + math.cos(a) * hw
        y = cy - math.sin(a) * hh * (0.92 if math.cos(a) > 0 else 1.0)
        pts.append((x, y))
    return pts


def _fish(surf, cx, cy, hw, hh, ss, *, medallion=False):
    """The chubby wide-eyed x-ray barramundi, side-on, facing RIGHT.

    Flat hematite-rust body (dominant mass) with the x-ray skeleton showing
    THROUGH it: a pipeclay belly-cavity 'window' so the bones read as inside a
    translucent fish, the bold spine + sparse ribs + one organ-lozenge over it,
    yellow-ochre rarrk fins, a big chibi ring-eye, a tiny mouth. Everything flat;
    detail via pattern + line-art, never 3D shading. `medallion` is the compact
    cap variant (a whole small fish framed for the totem cap)."""
    tail_hw = hw * 0.30

    # ── TAIL (forked caudal fin) at the LEFT, ochre rarrk ──
    tx = cx - hw * 0.94
    tail = [
        (tx + tail_hw * 0.9, cy),
        (tx - tail_hw, cy - hh * 0.92),
        (tx - tail_hw * 0.2, cy - hh * 0.10),
        (tx - tail_hw, cy + hh * 0.92),
    ]
    _rarrk_fin(surf, tail, ss, base_col=OCHRE, hatch_col=PIPECLAY, n=3)

    # ── DORSAL + ANAL + PECTORAL fins (ochre rarrk), drawn before the body so the
    #    body keyline crisply overlaps their roots ──
    dorsal = [
        (cx - hw * 0.10, cy - hh * 0.86),
        (cx + hw * 0.34, cy - hh * 1.34),
        (cx + hw * 0.40, cy - hh * 0.82),
    ]
    _rarrk_fin(surf, dorsal, ss, base_col=OCHRE, hatch_col=PIPECLAY, n=3)
    anal = [
        (cx - hw * 0.04, cy + hh * 0.82),
        (cx + hw * 0.22, cy + hh * 1.18),
        (cx + hw * 0.34, cy + hh * 0.78),
    ]
    _rarrk_fin(surf, anal, ss, base_col=OCHRE, hatch_col=PIPECLAY, n=2)

    # ── BODY (dominant hematite-rust mass) ──
    body_pts = _fish_body_poly(cx, cy, hw, hh)
    ibody = [(int(x), int(y)) for x, y in body_pts]
    pygame.draw.polygon(surf, RUST, ibody)
    # A flat lighter-rust top-third panel for graphic separation (NOT a bevel —
    # a second flat fill marked by a clean seam, the dorsal "back" of the fish).
    back_pts = [(x, y) for x, y in body_pts if y < cy - hh * 0.04]
    if len(back_pts) >= 3:
        pygame.draw.polygon(surf, RUST_HI, [(int(x), int(y)) for x, y in back_pts])

    # ── the BELLY-CAVITY WINDOW: a flat DARK panel inset in the lower body so the
    #    pipeclay lattice has the value-contrast to pop (the bones-on-rust read
    #    went faint at 32px when they were close in value). A deep charcoal-rust
    #    under-plate — still flat, just a much darker flat region than the body. ──
    cav_col = lerp_color(RUST_DK, CHAR_DK, 0.55)
    cav_cx = cx - hw * 0.08
    cav_cy = cy + hh * 0.08
    cav_rx = hw * 0.62
    cav_ry = hh * 0.74
    cav_rect = pygame.Rect(int(cav_cx - cav_rx), int(cav_cy - cav_ry),
                           int(2 * cav_rx), int(2 * cav_ry))
    pygame.draw.ellipse(surf, cav_col, cav_rect)
    pygame.draw.ellipse(surf, CHAR_DK, cav_rect, max(1, int(1.4 * ss)))

    # ── the x-ray SKELETON over the cavity (the hero detail) ──
    _xray_skeleton(surf, cav_cx, cav_cy, cav_rx * 0.96, cav_ry * 0.92, ss)

    # ── body keyline LAST so the silhouette is crisp ink ──
    pygame.draw.polygon(surf, INK, ibody, max(2, int(2.2 * ss)))

    # ── a pipeclay dot-row along the lateral line (more of the protected tell,
    #    up on the rust where it contrasts) ──
    _dot_row(surf, cx + hw * 0.04, cy - hh * 0.50, hw * 0.52, 5, hw * 0.05,
             PIPECLAY, key_col=PIPECLAY_DK, ss=ss)

    # ── GILL arc: a single charcoal curved line behind the head ──
    gill_x = cx + hw * 0.40
    gill = [(gill_x + hw * 0.06 * math.sin(t), cy - hh * 0.6 + hh * 1.2 * (i / 12))
            for i, t in ((i, math.pi * (i / 12)) for i in range(13))]
    pygame.draw.lines(surf, CHAR, False, [(int(x), int(y)) for x, y in gill],
                      max(2, int(2.2 * ss)))

    # ── the chibi RING-EYE (wide-eyed, the cute read) up in the snout. DEMOTED:
    #    shrunk so the BONES, not the eye, win the brightest-internal-mass fight
    #    at 32px. Ringed in charcoal and its inner-white sheen DROPPED so it stops
    #    competing with the pipeclay lattice for the focal slot. ──
    eye_cx = cx + hw * 0.62
    eye_cy = cy - hh * 0.22
    eye_r = hh * 0.32
    pygame.draw.circle(surf, OCHRE, (int(eye_cx), int(eye_cy)), int(eye_r))
    pygame.draw.circle(surf, INK, (int(eye_cx), int(eye_cy)), int(eye_r * 0.52))
    pygame.draw.circle(surf, INK, (int(eye_cx), int(eye_cy)), int(eye_r),
                       max(2, int(2.2 * ss)))

    # ── tiny pursed MOUTH at the snout tip (the adorable beat — small, not a maw) ──
    mx = cx + hw * 0.94
    my = cy + hh * 0.04
    pygame.draw.line(surf, CHAR_DK, (int(mx - hw * 0.10), int(my)),
                     (int(mx + hw * 0.02), int(my + hh * 0.10)),
                     max(2, int(2.4 * ss)))


def build_barramundi(scale=1.0, ss=5, *, compact=False):
    """The full fish on its own transparent surface, facing right. Returns an
    outlined surface. Renders LARGE at SS=5-6 then smoothscales down so the
    sparse skeleton geometry stays crisp.

    `compact` is the GAMEPLAY / 32px-icon variant: the fish is centred with tight
    padding and the skeleton is baked at the low-res tell density so the icon
    reads 'see-through chubby fish' — spine + one big rib pair + organ dot +
    belly window — not a rust blob. The see-through read MUST survive here."""
    body_hw = int(56 * scale) * ss
    body_hh = int(34 * scale) * ss
    pad_x = int(20 * scale) * ss      # room for tail + snout + fins
    pad_y = int(30 * scale) * ss      # room for dorsal + anal fins

    W = body_hw * 2 + pad_x * 2
    H = body_hh * 2 + pad_y * 2
    cx = W // 2 + int(body_hw * 0.06)  # nudge right; tail+forked-fin eats left
    cy = H // 2

    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    _fish(surf, cx, cy, body_hw, body_hh, ss, medallion=compact)
    if compact:
        _xray_tell(surf, cx - body_hw * 0.08, cy + body_hh * 0.08,
                   body_hw * 0.60, body_hh * 0.72, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


def _xray_tell(surf, cx, cy, hw, hh, ss):
    """A baked LOW-RES x-ray tell for the compact icon: a single thick charcoal
    spine, ONE fat pipeclay rib pair, and one big pipeclay organ-dot over a dark
    belly window — sized so smoothscale to true 32px PRESERVES the see-through
    read instead of mushing the fine ribs to noise. At showcase scale it hides
    under the real sparse skeleton; at icon scale it is what survives, carrying
    the 'I can see its bones' read that is this concept's entire point."""
    # a DARK belly window so the light bones pop on it small — pushed deep
    # charcoal-rust so the pipeclay lattice has the value contrast to dominate.
    cav_col = lerp_color(RUST_DK, CHAR_DK, 0.60)
    pygame.draw.ellipse(surf, cav_col,
                        pygame.Rect(int(cx - hw), int(cy - hh),
                                    int(2 * hw), int(2 * hh)))
    # ONE bold pipeclay SPINE — the brightest internal mass, baking to ~2px.
    sp0 = (int(cx - hw * 0.80), int(cy - hh * 0.50))
    sp1 = (int(cx + hw * 0.72), int(cy - hh * 0.34))
    pygame.draw.line(surf, PIPECLAY, sp0, sp1, max(4, int(7.0 * ss)))
    pygame.draw.line(surf, CHAR_DK, sp0, sp1, max(1, int(1.6 * ss)))
    # 3 BOLD ribs (no comb): each a fat pipeclay stroke, clearly spaced, as
    # bright as the spine, dropping from along the spine into the belly.
    for i, fx in enumerate((-0.46, 0.02, 0.50)):
        ax = cx + hw * fx
        ay = cy - hh * (0.46 - 0.08 * i)
        pygame.draw.line(surf, PIPECLAY, (int(ax), int(ay)),
                         (int(ax - hw * 0.12), int(cy + hh * 0.66)),
                         max(3, int(5.0 * ss)))
    # one big organ-dot — warm-cored pipeclay, the x-ray focal.
    org = (int(cx - hw * 0.18), int(cy + hh * 0.34))
    pygame.draw.circle(surf, PIPECLAY, org, int(hh * 0.32))
    pygame.draw.circle(surf, lerp_color(PIPECLAY, EMBER, 0.34), org, int(hh * 0.22))
    pygame.draw.circle(surf, RUST_DK, org, int(hh * 0.11))


# ── pillar pair (prop -> pillar mirror proof) — the WEIR-POLE ─────────────────

OVERHANG = 12


def _weir_band_repeat(surf, cx, y0, band_h, half_w, ss):
    """ONE repeat of the fish-trap WEIR-POLE: a rib-LADDER band (echoing the
    fish's ribs) stacked over a pipeclay DOT-ROW band on the rust ground. This is
    the unit that TILES top<->bottom — exactly one rib-ladder + one dot-row per
    repeat. Pure flat motifs; the alternation + the rib echo is the read."""
    # Rust ground for this repeat (the dominant mass of the pole).
    pygame.draw.rect(surf, RUST, (int(cx - half_w), int(y0), int(2 * half_w), int(band_h)))

    # Top half: the RIB-LADDER — a bold charcoal centre spine with a few pipeclay
    # cross-rungs (the weir lashings = the fish ribs echoed). Sparse, countable.
    # Kept a touch LIGHTER/THINNER than the hero's own spine + ribs so the
    # CREATURE out-bolds its derived prop (the body must read at least as bold as
    # its pillar, not lose to it).
    spine_y0 = y0 + band_h * 0.06
    spine_y1 = y0 + band_h * 0.48
    pygame.draw.line(surf, PIPECLAY, (int(cx), int(spine_y0)),
                     (int(cx), int(spine_y1)), max(2, int(3.2 * ss)))
    pygame.draw.line(surf, CHAR_DK, (int(cx), int(spine_y0)),
                     (int(cx), int(spine_y1)), max(1, int(1.6 * ss)))
    rungs = 3
    for i in range(rungs):
        ry = spine_y0 + (spine_y1 - spine_y0) * (0.16 + 0.72 * (i / max(1, rungs - 1)))
        pygame.draw.line(surf, PIPECLAY, (int(cx - half_w * 0.60), int(ry)),
                         (int(cx + half_w * 0.60), int(ry)), max(2, int(2.2 * ss)))
        pygame.draw.line(surf, CHAR, (int(cx - half_w * 0.60), int(ry)),
                         (int(cx + half_w * 0.60), int(ry)), max(1, int(1.0 * ss)))

    # A thin charcoal-dark seam between the two bands (graphic divider).
    seam_y = y0 + band_h * 0.54
    pygame.draw.line(surf, CHAR_DK, (int(cx - half_w), int(seam_y)),
                     (int(cx + half_w), int(seam_y)), max(2, int(2.4 * ss)))

    # Bottom half: a pipeclay DOT-ROW band — ONE clean row of well-spaced dots
    # (the protected tell; kept countable, not a dense field).
    dot_y = y0 + band_h * 0.74
    _dot_row(surf, cx, dot_y, half_w * 0.62, 4, half_w * 0.20, PIPECLAY,
             key_col=PIPECLAY_DK, ss=ss)

    # Ochre rail-lines down both edges so the pole reads as one bound staff.
    for s in (-1, 1):
        pygame.draw.line(surf, OCHRE_DK, (int(cx + s * half_w * 0.92), int(y0)),
                         (int(cx + s * half_w * 0.92), int(y0 + band_h)),
                         max(1, int(1.8 * ss)))


def _weir_column(surf, cx, top_y, bot_y, half_w, ss):
    """The repeatable PILLAR BODY: the weir-pole as a straight tiling shaft —
    exactly one rib-ladder band + one pipeclay dot-row band per repeat on the
    rust ground (the band that mirrors top<->bottom). NO ember here — cap-only."""
    length = bot_y - top_y
    band = half_w * 3.0
    n = max(1, int(round(length / band)))
    band = length / n
    for i in range(n):
        _weir_band_repeat(surf, cx, top_y + i * band, band, half_w, ss)
    for s in (-1, 1):
        pygame.draw.line(surf, INK, (int(cx + s * half_w), int(top_y)),
                         (int(cx + s * half_w), int(bot_y)), max(1, int(1.6 * ss)))


def _medallion_cap(surf, cx, cap_base_y, half_w, ss, *, point_up, night=False):
    """The creature-derived GAP-EDGE CAP: a small whole x-ray fish-MEDALLION
    (~strip+30%) framed in a pipeclay dot-ring, sitting at the pole end facing
    the gap, with the EMBER glow CONFINED to this cap (the only warm light). A
    modest medallion, never a top-heavy slab. `point_up` faces it toward the gap."""
    d = -1 if point_up else 1
    med_r = half_w * 1.30           # cap ~ strip + 30%, no top-heavy slab
    cy = cap_base_y + d * (med_r + half_w * 0.4)

    # Ember glow CONFINED to the cap — radiates INTO the gap. Night alpha/radius
    # pulled DOWN so the halo stays a contained cap glow, not a crown-heavy bloom.
    gr = int(med_r * (1.35 if night else 1.2))
    gy = cap_base_y + d * half_w * 0.4
    gl = make_glow_surface(gr, EMBER, alpha_center=160 if night else 125, falloff=2.4)
    surf.blit(gl, (int(cx - gr), int(gy - gr)), special_flags=pygame.BLEND_ADD)

    # The medallion disk (rust ground, flat) framed by a pipeclay dot-ring tell.
    pygame.draw.circle(surf, RUST, (int(cx), int(cy)), int(med_r))
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(med_r), max(2, int(2.0 * ss)))
    ring_n = 10
    for i in range(ring_n):
        a = 2 * math.pi * (i / ring_n)
        rx = cx + math.cos(a) * med_r * 0.86
        ry = cy + math.sin(a) * med_r * 0.86
        pygame.draw.circle(surf, PIPECLAY, (int(rx), int(ry)), max(1, int(med_r * 0.085)))

    # A whole small x-ray fish inside the medallion, facing the gap.
    fish = build_barramundi(scale=0.46, ss=ss, compact=True)
    fw, fh = fish.get_size()
    if point_up:
        fish = pygame.transform.flip(fish, False, True)
    target = int(med_r * 1.5)
    fish = pygame.transform.smoothscale(fish, (target, int(target * fh / fw)))
    fw, fh = fish.get_size()
    surf.blit(fish, (int(cx - fw / 2), int(cy - fh / 2)))

    # The ember twinkle core sits at the medallion fish's eye so the warm light
    # reads as the cap's lit eye, not a free-floating spark.
    ex = cx + med_r * 0.34
    ey = cy - med_r * 0.18 * (1 if point_up else 1)
    pygame.draw.circle(surf, EMBER, (int(ex), int(ey)), max(1, int(med_r * 0.12)))
    pygame.draw.circle(surf, EMBER_HOT, (int(ex), int(ey)), max(1, int(med_r * 0.06)))


def _weir_pillar_obstacle(height, ss, *, flip, night=False):
    """One weir-pole pillar obstacle: the rib-ladder/dot-row shaft fills the post
    and a fish-medallion CAP sits at the GAP-facing edge, its ember glow
    radiating INTO the gap. `flip=True` is the TOP pillar — cap at the bottom
    (gap) edge; `flip=False` is the BOTTOM pillar — cap at the top (gap) edge.
    Both mirror the same rib/dot body into a clean vertical pole-pillar."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    half_w = int((PIPE_W * 0.42)) * ss
    cap_band = int(58 * ss)
    if flip:
        _weir_column(surf, cx, 0, bh - cap_band, half_w, ss)
        _medallion_cap(surf, cx, bh - cap_band, half_w, ss, point_up=False, night=night)
    else:
        _weir_column(surf, cx, cap_band, bh, half_w, ss)
        _medallion_cap(surf, cx, cap_band, half_w, ss, point_up=True, night=night)
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
        rng = _r.Random(99)
        for _ in range(26):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, int(h * 0.7))
            pygame.draw.circle(s, (220, 230, 255), (sx, sy), rng.choice((1, 1, 2)))
    return s


def _to_gray(src):
    g = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    g.blit(src, (0, 0))
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    return g


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1120, 780
    sheet = pygame.Surface((SW, SH))
    sheet.fill((120, 120, 124))            # neutral grey bg
    _label(sheet, font,
           "BARRAMUNDI-SPIRIT  —  mokoi spin-off  —  side-on x-ray fish-beast  —  round 2",
           18, 12, (24, 24, 28))
    _label(sheet, small,
           "FLAT-GRAPHIC: hematite-RUST body, charcoal bone-keyline, pipeclay-white rib/organ LATTICE (the tell), yellow-ochre fin-tips; ember CONFINED to cap. Sparse skeleton per re-spec.",
           18, 32, (40, 40, 46))

    # — Cell A: the BIG hero fish on a neutral panel (elevated SS=6).
    panel = pygame.Rect(18, 56, 360, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panel, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panel, 2, border_radius=8)
    _label(sheet, font, "(a) HERO  big scale  SS=6", panel.x + 8, panel.y + 8, (245, 240, 230))
    _label(sheet, small, "chubby fish; see THROUGH to BOLD spine + 3 ribs + 1 organ",
           panel.x + 8, panel.y + 28, (235, 230, 220))
    hero = build_barramundi(scale=1.7, ss=6)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2,
                      panel.centery - hero.get_height() // 2 + 20))

    # — Cell B: weir-pole as a tileable PILLAR pair at TRUE obstacle scale on
    #   NIGHT, plus a 2x zoom of the CAP band proving the contained ember + mirror.
    panelB = pygame.Rect(388, 56, 320, 600)
    bg = _sky(panelB.w, panelB.h, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (60, 60, 64), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE  (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 500
    slice_x = panelB.x + 22
    slice_y = panelB.y + 44
    gap_top = 158
    gap_h = 124
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _weir_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _weir_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (210, 200, 180), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native: rib-ladder +", slice_x - 2, slice_y + slice_h + 6,
           (235, 225, 210))
    _label(sheet, small, "dot-row per repeat tiles; ember on CAP only",
           slice_x - 2, slice_y + slice_h + 22, (255, 210, 150))

    cap_band = 58
    zw, zh = pw, 158
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 14
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 168
    zy = panelB.y + 120
    zbg = _sky(zw * 2, zh * 2, (8, 8, 30), (16, 14, 44), (28, 20, 58))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (210, 200, 180), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "fish-medallion cap;", zx - 2, zy + zh * 2 + 6, (255, 210, 150))
    _label(sheet, small, "mirror visible, ember -> gap", zx - 2, zy + zh * 2 + 22, (255, 210, 150))

    # — Cell C: TRUE 32px gameplay chip on a DAY sky AND a NIGHT sky, plus a
    #   blow-up audit + grayscale tell-check.
    panelC = pygame.Rect(718, 56, 384, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panelC, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8, (245, 240, 230))
    _label(sheet, small, "see-through read must survive; day + night", panelC.x + 8, panelC.y + 28,
           (235, 230, 220))

    # The compact gameplay creature blown up for a clear day/night read.
    boss = build_barramundi(scale=0.62, ss=5, compact=True)
    day = _sky(160, 240, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(160, 240, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    dy = panelC.y + 48
    sheet.blit(day, (panelC.x + 12, dy))
    sheet.blit(night, (panelC.x + 188, dy))
    sheet.blit(boss, (panelC.x + 12 + 80 - boss.get_width() // 2,
                      dy + 120 - boss.get_height() // 2))
    sheet.blit(boss, (panelC.x + 188 + 80 - boss.get_width() // 2,
                      dy + 120 - boss.get_height() // 2))
    _label(sheet, small, "DAY", panelC.x + 12 + 6, dy + 6, (18, 28, 24))
    _label(sheet, small, "NIGHT", panelC.x + 188 + 6, dy + 6, (255, 220, 200))

    # The TRUE-32 icon at 1x on day/night/neutral chips, then 3x audit + gray.
    icon_src = build_barramundi(scale=1.0, ss=5, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))
    sc64 = 64 / icon_src.get_height()
    icon64 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc64)), 64))

    gy = dy + 256
    _label(sheet, small, "TRUE 32px-tall at 1x (no blow-up):", panelC.x + 12, gy - 2,
           (235, 225, 215))
    swatches = [
        ((40, 110, 200), "day"),
        ((40, 30, 70), "night"),
        ((96, 96, 100), "neutral"),
    ]
    sx = panelC.x + 12
    sw = 118
    for col, lab in swatches:
        chip = pygame.Rect(sx, gy + 16, sw, 60)
        pygame.draw.rect(sheet, col, chip, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 240))
        sx += sw + 6

    # 3x nearest-neighbour blow-up of the true-32 icon so the tell is auditable,
    # plus the grayscale value check (the protected rib/organ tell must survive).
    chip = pygame.Rect(panelC.x + 12, gy + 92, 168, 110)
    pygame.draw.rect(sheet, (78, 78, 82), chip, border_radius=4)
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 3, icon32.get_height() * 3))
    sheet.blit(blow, (chip.x + 8, chip.centery - blow.get_height() // 2))
    sheet.blit(icon64, (chip.right - icon64.get_width() - 8,
                        chip.centery - icon64.get_height() // 2))
    _label(sheet, small, "3x / 64px audit", chip.x + 4, chip.y + 2, (240, 240, 240))

    gray = _to_gray(icon64)
    gchip = pygame.Rect(panelC.x + 196, gy + 92, 176, 110)
    pygame.draw.rect(sheet, (124, 128, 124), gchip, border_radius=4)
    sheet.blit(gray, (gchip.centerx - gray.get_width() // 2,
                      gchip.centery - gray.get_height() // 2))
    _label(sheet, small, "grayscale tell (bones survive?)", gchip.x + 4, gchip.y + 2, (24, 24, 24))

    # — Footer: style notes.
    _label(sheet, small,
           "FLAT only: detail via pattern + line-art (sparse spine/ribs, rarrk fins, dot-rows), never 3D shading; hematite-rust dominant; ochre fin-tips only; pipeclay rib/organ lattice = the protected hue-blind tell.",
           18, SH - 64, (40, 40, 46))
    _label(sheet, small,
           "prop->pillar: weir-pole = 1 rib-ladder band + 1 pipeclay dot-row band per repeat (tiles, echoes body); gap-edge cap = a whole x-ray fish-medallion (~+30%) w/ ember CONFINED to the cap. Clean mirror.",
           18, SH - 44, (40, 40, 46))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()

"""Look-dev sheet for the Skybit BOSS — "CHOCHIN-ANKO" (Umibozu-versions set #1).

The abyssal anglerfish lure-fiend: the brood ANCHOR, the most epic of the
deep-sea spin-offs. An oil-black bulbous deep-sea grump whose only light is the
hot-white-peach lure it wags on a stalk — a perpetually-annoyed face with a cute
underbite that opens into an endless needle-maw.

KIND = lure-on-a-stalk (distinct from the source umibozu's jelly-dome). The
illicium STALK is the body-as-pillar; the glowing esca lure-bulb is the gap-cap.

House style this obeys (the elevated "epic" lineage grammar):
  - CHIBI proportions — one oversized rounded near-silhouette body, big grump
    face; the illicium stalk + esca lure is the single focal hook.
  - FLAT saturated fills + a hard 1-2px ink keyline. No within-shape gradients,
    no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen lobe.
  - Scary-CUTE not grim: an annoyed deep grump wagging a nightlight; the
    underbite + needle-maw is endearing-menacing, never a pure horror snarl.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC pass: render BIG at SS=6, then smoothscale down for a crisp downscale.

Palette read (pinned): oil-black body (the body stays near-silhouette DARK so
the lure pip is the ONLY focal); blood-CORAL flush confined to the BELLY + gum
line ONLY (never a full-body wash, so it can't twin Akkorokamui's red lane);
cold-steel sheen as the top-left rim; hot-white-peach esca lure-glow as the SOLE
brightest pip. The dark-body-vs-single-hot-pip value split carries the read.

Prop -> pillar mirror: the illicium STALK is the pillar. A tileable segmented
filament (knuckle-node per repeat + barbel-feelers) = the repeatable PILLAR
BODY; the glowing esca lure-bulb (~stalk +30%) = the detachable GAP-EDGE CAP
radiating hot-white-peach INTO the gap. Naturally vertical + symmetric — clean
mirror, no top-heavy cap.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/umibozu_versions/chochin_anko/render_chochin_anko.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (chochin-anko) ────────────────────────────────────────────
# Oil-black body — the lowest value mass. The body is kept near-silhouette DARK
# so the single hot lure pip is the only thing the eye lands on. Coral is the
# ONLY warm body hue and is confined to the belly + gum line, never a full wash.
BODY        = (38, 52, 58)      # oil-black body fill (cold dark blue-grey)
BODY_DK     = (22, 32, 38)      # charcoal shade (dark-core ring / hollows)
BODY_SHEEN  = (150, 170, 176)   # cold-steel rim sheen (top-left lit lobe)
BODY_DEEP   = (16, 22, 26)      # near-black abyss base (lowest value)

CORAL       = (196, 86, 72)     # blood-coral belly + gum flush — BELLY ONLY
CORAL_DK    = (138, 54, 50)     # coral dark-core / under-belly shade
CORAL_LT    = (224, 132, 112)   # coral inner sheen (a touch of lit belly)

LURE        = (255, 224, 168)   # hot-white-peach esca glow — the SOLE focal pip
LURE_CORE   = (255, 244, 228)   # blown-out hot-white core of the lure (the pip)
LURE_DK     = (208, 158, 96)    # lure dark-seat ring (so the bulb has volume)

# Needle teeth + coral gum are pulled DOWN in value so NOTHING out-values the
# esca pip — the lure must win the value contest outright. Teeth = a dull cool
# bone (~25% under pure white); the maw coral stays a muted gum, not a bright
# grin.
TOOTH       = (176, 184, 184)   # dull cool-bone teeth (not bright white)
GUM         = (150, 66, 58)     # muted coral gum (lower value than belly coral)

STALK       = (46, 60, 66)      # illicium stalk filament (a hair lifted off body
                                # so the stalk reads as its own appendage)

INK         = (20, 26, 30)      # the house keyline
FACE_INK    = (14, 20, 24)      # eyes/maw drawn in deepest ink

# Night lifts a cold-steel keyline so the oil-black silhouette survives on the
# midnight-blue sky (dark ink would vanish there); grown 2px for shape read.
INK_NIGHT   = (172, 196, 200)


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_col=None,
                  sheen_scale=0.30):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Sculpted volume while staying flat-shaded. `sheen_col` overrides the
    sheen so the cold-steel highlight can replace a tinted fill."""
    pygame.draw.circle(surf, _shade_c(col, -24), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.06))))
    if sheen:
        sc = sheen_col if sheen_col is not None else _shade_c(col, 30)
        pygame.draw.circle(surf, sc,
                           (int(cx - r * 0.34), int(cy - r * 0.36)),
                           max(2, int(r * sheen_scale)))


def _add_outline(src, outline_color=(*INK, 235), width=1):
    """Grow a keyline from the alpha mask so the silhouette POPS on any sky. On
    night the keyline is a lifted cold-steel tone, not dark ink, AND grown
    thicker so the oil-black body edge survives on the dark sky by shape."""
    w, h = src.get_size()
    pad = width + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    offs = [(dx, dy) for dx in range(-width, width + 1)
            for dy in range(-width, width + 1) if (dx, dy) != (0, 0)]
    for dx, dy in offs:
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── the esca lure (the SOLE hot focal pip) ───────────────────────────────────

def _esca(surf, cx, cy, r, ss, *, night=False, glow_mult=1.0, epic=False):
    """The glowing esca lure-bulb — the ONE place the hot-white-peach is allowed
    and the single brightest pip in the whole design. A contained glow halo + a
    flat lure disc with a dark-seat ring + a blown-out hot core. Everything else
    stays oil-black so this is the only thing the eye lands on. The glow is kept
    TIGHT (a steep falloff) so it never bleeds a soft halo over the oil-black
    body and steals contrast from the pip — the body edge must stay crisp."""
    # Tight halo: a smaller radius + steeper falloff than r1 so the bloom hugs
    # the bulb instead of washing over the silhouette's top edge.
    gr = int(r * (3.0 if night else 2.2) * glow_mult)
    gl = make_glow_surface(max(1, gr), LURE, alpha_center=200 if night else 140,
                           falloff=2.8)
    surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)
    if epic:
        # Hero gets a tight inner WHITE bloom (small radius so it never bleeds over
        # the body) to make the pip feel genuinely incandescent at big scale.
        gr2 = int(r * 1.3 * glow_mult)
        gl2 = make_glow_surface(max(1, gr2), LURE_CORE, alpha_center=200,
                                falloff=3.0)
        surf.blit(gl2, (int(cx - gr2), int(cy - gr2)),
                  special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, LURE_DK, (int(cx), int(cy)), max(1, int(r)))
    pygame.draw.circle(surf, LURE, (int(cx), int(cy)), max(1, int(r * 0.86)))
    # A true hot-WHITE core blooming up out of the peach body so the lure reads
    # as a single incandescent PIP, not a flat lantern coin. The core is the
    # absolute brightest value in the whole design.
    pygame.draw.circle(surf, LURE, (int(cx), int(cy)), max(1, int(r * 0.58)))
    pygame.draw.circle(surf, LURE_CORE, (int(cx), int(cy)), max(1, int(r * 0.42)))
    # A tiny additive white spark dead-center pushes the core hotter than any
    # peach around it so it survives both the bright day sky and the dark night.
    spark = max(1, int(r * 0.22))
    sg = make_glow_surface(spark * 3, (255, 252, 244), alpha_center=235,
                           falloff=2.4)
    surf.blit(sg, (int(cx - spark * 3), int(cy - spark * 3)),
              special_flags=pygame.BLEND_ADD)


# ── one segment of the illicium stalk (segmented filament + knuckle-node) ─────

def _stalk_segment(surf, cx, top_y, seg_len, hw, ss, *, night=False,
                   barbels=True, node=True):
    """One repeat of the illicium STALK: a short tapering filament length capped
    by a KNUCKLE-NODE swelling, with a pair of thin BARBEL-FEELERS flicking off
    the node. This is the unit that TILES for the pillar body."""
    stalk = _shade_c(STALK, 10) if night else STALK
    # The filament shaft — a slightly waisted column (necks in the middle so the
    # node-to-node read is clearly segmented, not a smooth pole).
    steps = 18
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        y = top_y + seg_len * t
        # Waist in the middle, swell at both ends toward the nodes.
        w = hw * (0.66 + 0.34 * abs(math.cos(t * math.pi)))
        left.append((cx - w, y))
        right.append((cx + w, y))
    shape = left + right[::-1]
    pygame.draw.polygon(surf, _shade_c(stalk, -22),
                        [(int(x), int(y)) for x, y in shape])
    inner_l = [(x + ss, y) for x, y in left]
    inner_r = [(x - ss, y) for x, y in right]
    pygame.draw.polygon(surf, stalk,
                        [(int(x), int(y)) for x, y in (inner_l + inner_r[::-1])])
    # Cold-steel sheen stripe down the lit (left) edge of the filament. On night
    # it is muted to a low-contrast tone so the dark filament stays ONE unbroken
    # value at obstacle scale and never breaks into a dotted/dashed line.
    sheen = _shade_c(stalk, 22) if night else BODY_SHEEN
    sheen_pts = [(int(x + ss * 1.4), int(y)) for x, y in left[::2]]
    if len(sheen_pts) >= 2:
        pygame.draw.lines(surf, sheen, False, sheen_pts, max(1, int(1.0 * ss)))

    # KNUCKLE-NODE at the bottom of the segment — a fatter triad bead, the
    # per-repeat tell that marks each stalk joint.
    if node:
        nr = hw * 1.34
        ny = top_y + seg_len
        # BARBEL-FEELERS first (under the node) — a pair of thin flicking whiskers
        # off the joint, the appendage tell that keeps the stalk reading organic.
        if barbels:
            for s in (-1, 1):
                bx0 = cx + s * nr * 0.7
                by0 = ny
                bpts = []
                bsteps = 10
                for i in range(bsteps + 1):
                    t = i / bsteps
                    bx = bx0 + s * nr * (0.9 * t)
                    by = by0 + nr * (0.5 * t + 0.7 * t * t)
                    bpts.append((int(bx), int(by)))
                pygame.draw.lines(surf, _shade_c(stalk, -10), False, bpts,
                                  max(1, int(1.6 * ss)))
                pygame.draw.circle(surf, sheen, bpts[-1], max(1, int(hw * 0.16)))
        _triad_circle(surf, cx, ny, nr, stalk, sheen=True,
                      sheen_col=sheen, sheen_scale=0.26)
        # A thin cold-steel knuckle crease across the node so it reads jointed.
        pygame.draw.arc(surf, _shade_c(stalk, -18),
                        (int(cx - nr * 0.8), int(ny - nr * 0.5),
                         int(nr * 1.6), int(nr)),
                        math.radians(200), math.radians(340), max(1, int(1.4 * ss)))


# ── the perpetually-annoyed grump head (near-silhouette dark) ─────────────────

def _head(surf, cx, cy, r, ss, *, night=False, tell=False):
    """The oil-black anglerfish grump: a bulbous near-silhouette body, an
    annoyed heavy scowl-brow, two small cold pin-eyes, and a cute UNDERBITE that
    opens into an endless NEEDLE-MAW. A blood-coral flush sits ONLY on the belly
    + gum line. The body stays the DARKEST mass so the esca lure is the only
    focal. `tell` bakes a bolder low-res face mark for the 32px read."""
    body = _shade_c(BODY, 12) if night else BODY
    sheen = _shade_c(BODY_SHEEN, 40) if night else BODY_SHEEN
    coral = _shade_c(CORAL, 10) if night else CORAL

    # — Body mass: a fat ovoid, wider at the belly. Drawn as a big triad ellipse
    #   so the form is sculpted but flat.
    body_w = r * 1.78
    body_h = r * 1.66
    rect = pygame.Rect(0, 0, int(body_w), int(body_h))
    rect.center = (int(cx), int(cy))
    pygame.draw.ellipse(surf, _shade_c(body, -26), rect)
    pygame.draw.ellipse(surf, body, rect.inflate(-int(r * 0.12), -int(r * 0.12)))

    # — Blood-coral BELLY flush — a flat coral crescent low + front on the body,
    #   confined to the lower-front belly so it never washes the full body. Built
    #   as a coral ellipse low on the body, masked up by re-filling the upper part
    #   with body so only a clean belly band remains.
    belly = pygame.Rect(0, 0, int(body_w * 0.84), int(body_h * 0.72))
    belly.center = (int(cx + r * 0.04), int(cy + r * 0.42))
    pygame.draw.ellipse(surf, _shade_c(coral, -28), belly)
    pygame.draw.ellipse(surf, coral, belly.inflate(-int(r * 0.10), -int(r * 0.10)))
    # A restrained touch of lit coral inner sheen low-front (the belly catching
    # the lure). Held DOWN in value so the belly never out-values the esca pip.
    lit = pygame.Rect(0, 0, int(body_w * 0.40), int(body_h * 0.26))
    lit.center = (int(cx), int(cy + r * 0.60))
    pygame.draw.ellipse(surf, _shade_c(CORAL_LT, -28 if night else -22), lit)
    # Carve the coral back down to a belly band: re-fill the upper half with body
    # so the coral never climbs over the back (keeps it BELLY-only).
    cover = pygame.Rect(0, 0, int(body_w * 1.1), int(body_h * 0.62))
    cover.center = (int(cx), int(cy - r * 0.22))
    pygame.draw.ellipse(surf, body, cover)
    # Restore the body dark-core ring lost to the cover (so the back rim holds).
    pygame.draw.ellipse(surf, _shade_c(body, -26), rect, max(2, int(2.0 * ss)))

    # — Cold-steel rim sheen lobe on the top-left of the back (the lit pate). One
    #   crisp crescent: a lit disc minus a body-colored bite.
    s_cx, s_cy, s_r = cx - r * 0.40, cy - r * 0.46, r * 0.30
    pygame.draw.circle(surf, sheen, (int(s_cx), int(s_cy)), max(2, int(s_r)))
    pygame.draw.circle(surf, body,
                       (int(s_cx + s_r * 0.52), int(s_cy + s_r * 0.50)),
                       max(2, int(s_r * 0.86)))

    # — The endless NEEDLE-MAW + cute UNDERBITE. A wide dark maw cavity low-front,
    #   a coral gum line along the rims, and rows of fine needle teeth. The lower
    #   jaw juts (underbite) so the bottom row overshoots — endearing-menacing.
    maw_cx = cx + r * 0.26
    maw_cy = cy + r * 0.34
    maw_w = r * 1.06
    maw_h = r * 0.62
    maw = pygame.Rect(0, 0, int(maw_w), int(maw_h))
    maw.center = (int(maw_cx), int(maw_cy))
    # Dark maw cavity (deepest value).
    pygame.draw.ellipse(surf, BODY_DEEP, maw)
    # Muted coral GUM line — a thin arc hugging the TOP rim of the maw. Kept at a
    # LOW gum value (not the bright belly coral) so the grin never out-values the
    # esca pip; it's a dark flushed rim, not a bright smile.
    gum = _shade_c(GUM, 8) if night else GUM
    pygame.draw.arc(surf, gum,
                    (maw.x, maw.y - int(r * 0.04), maw.w, int(maw_h * 1.0)),
                    math.radians(8), math.radians(172), max(2, int(2.4 * ss)))
    # Lower coral gum (the underbite jaw rim) — darker still.
    pygame.draw.arc(surf, _shade_c(gum, -18),
                    (maw.x, maw.y + int(maw_h * 0.30), maw.w, int(maw_h * 0.9)),
                    math.radians(192), math.radians(348), max(2, int(2.2 * ss)))

    # Needle teeth — fine triangles top + bottom in a DULL cool bone (not bright
    # white) so the row never competes with the esca for the eye. Bottom row juts
    # up past the top seam (the cute underbite).
    n_teeth = 9
    top_lip_y = maw_cy - maw_h * 0.28
    bot_lip_y = maw_cy + maw_h * 0.30
    tooth_col = _shade_c(TOOTH, -10) if night else TOOTH
    for i in range(n_teeth):
        t = (i + 0.5) / n_teeth
        tx = maw_cx - maw_w * 0.42 + maw_w * 0.84 * t
        th = maw_h * (0.30 + 0.10 * math.sin(t * math.pi))
        pygame.draw.polygon(surf, tooth_col, [
            (int(tx - maw_w * 0.030), int(top_lip_y)),
            (int(tx + maw_w * 0.030), int(top_lip_y)),
            (int(tx), int(top_lip_y + th))])
    n_bot = 8
    for i in range(n_bot):
        t = (i + 0.5) / n_bot
        tx = maw_cx - maw_w * 0.40 + maw_w * 0.80 * t
        th = maw_h * (0.36 + 0.10 * math.sin(t * math.pi))
        # Bottom fangs point UP and overshoot the seam — the underbite.
        pygame.draw.polygon(surf, tooth_col, [
            (int(tx - maw_w * 0.032), int(bot_lip_y)),
            (int(tx + maw_w * 0.032), int(bot_lip_y)),
            (int(tx), int(bot_lip_y - th))])

    # — Eyes: two small cold pin-eyes set high + close, with heavy ANNOYED
    #   scowl-lids pressing down toward the centre (a frown V). The grump beat:
    #   tiny irritated eyes under a heavy frown, not big cute saucers.
    eye_dx = r * 0.34
    eye_y = cy - r * 0.18
    eye_r = r * 0.15
    for s in (-1, 1):
        ex = cx + s * eye_dx
        pygame.draw.circle(surf, BODY_DEEP, (int(ex), int(eye_y)), max(2, int(eye_r)))
        # Eye sclera kept a cool MID-grey, not bright white, so the tiny pin-eyes
        # don't read as bright pips competing with the esca.
        pygame.draw.circle(surf, (158, 174, 178), (int(ex), int(eye_y)),
                           max(1, int(eye_r * 0.62)))
        pygame.draw.circle(surf, FACE_INK, (int(ex), int(eye_y)),
                           max(1, int(eye_r * 0.40)))
        pygame.draw.circle(surf, (198, 212, 214),
                           (int(ex - eye_r * 0.24), int(eye_y - eye_r * 0.26)),
                           max(1, int(eye_r * 0.18)))
        # Heavy ANNOYED scowl-lid: a thick angled body-shade wedge cutting the top
        # of the eye, sloping DOWN toward the centre on both sides (a frown).
        inner = ex + s * eye_r * 1.6
        outer = ex - s * eye_r * 1.6
        lid = [
            (int(outer), int(eye_y - eye_r * 1.9)),
            (int(inner), int(eye_y - eye_r * 0.1)),
            (int(inner), int(eye_y - eye_r * 0.9)),
            (int(outer), int(eye_y - eye_r * 2.6)),
        ]
        pygame.draw.polygon(surf, _shade_c(body, -22), lid)

    # — A single deep annoyed frown crease between the brows (the grump tell).
    pygame.draw.line(surf, _shade_c(body, -26),
                     (int(cx), int(eye_y - eye_r * 0.8)),
                     (int(cx), int(eye_y + eye_r * 1.0)), max(1, int(1.6 * ss)))

    if tell:
        # Baked low-res face tell so the 32px icon keeps a creature read: two bold
        # dark angled scowl-brows (a frown V) + the wide dark needle-maw already
        # reads as the bottom dark band.
        for s in (-1, 1):
            ex = cx + s * eye_dx
            pygame.draw.line(surf, FACE_INK,
                             (int(ex - s * eye_r * 1.5), int(eye_y - eye_r * 1.8)),
                             (int(ex + s * eye_r * 1.5), int(eye_y - eye_r * 0.2)),
                             max(2, int(2.8 * ss)))


# ── the whole creature: head + illicium stalk + esca lure ─────────────────────

def build_chochin_anko(scale=1.0, ss=5, *, night=False, compact=False):
    """The full creature on a transparent surface: the oil-black grump body, an
    illicium STALK arching up + forward off the brow, ending in the glowing esca
    lure dangled over the face. EPIC pass renders BIG at SS, then smoothscales
    down. `compact` is the gameplay/32px variant — body grown to dominate, stalk
    shortened, a baked low-res face tell + a fat lure pip."""
    head_r = int(46 * scale) * ss

    # The stalk arcs UP off the brow then FORWARD so the lure dangles over the
    # face — the "wagging a nightlight" read. Compact pulls it tighter + bigger.
    stalk_rise = head_r * (1.5 if compact else 2.3)
    stalk_reach = head_r * (0.55 if compact else 0.7)
    lure_r = head_r * (0.42 if compact else 0.34)

    side_pad = int(20 * scale) * ss
    top_pad = int(20 * scale) * ss + lure_r
    bot_pad = int(18 * scale) * ss

    W = int(head_r * 1.78 + side_pad * 2 + stalk_reach * 2)
    H = int(head_r * 1.66 + stalk_rise + top_pad + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    cx = side_pad + int(head_r * 0.89)
    cy = H - bot_pad - int(head_r * 0.83)

    # — The illicium stalk: a smooth arc rising off the top of the brow, leaning
    #   FORWARD over the face. Drawn as a string of tapering quads with a node at
    #   each joint (the same unit as the pillar) so the segmented read carries.
    # Root the stalk DEEP into the brow (well inside the body top at ~-0.83r) so
    # the arc grows out of the forehead with no sky-gap between head and stalk.
    root_x = cx - head_r * 0.06
    root_y = cy - head_r * 0.62
    n_seg = 3 if compact else 4
    stalk = _shade_c(STALK, 10) if night else STALK
    sheen = _shade_c(BODY_SHEEN, 30) if night else BODY_SHEEN
    pts = []
    for i in range(n_seg + 1):
        t = i / n_seg
        ax = root_x + stalk_reach * math.sin(t * math.pi * 0.62)
        ay = root_y - stalk_rise * t
        pts.append((ax, ay))
    hw0 = head_r * 0.16
    if compact:
        # COMPACT bake: the stalk is ONE solid dark stroke (no per-segment sheen,
        # no node triads, no barbels) so at true 32px it reads as a definite
        # "lure on a stick," never a near-1px wisp broken into dashes. The stroke
        # is sized so it survives the downscale as a clean ~2px dark stalk.
        dark = _shade_c(stalk, -26)
        wide = max(3, int(hw0 * 1.7))
        line_pts = [(int(x), int(y)) for x, y in pts]
        pygame.draw.lines(surf, dark, False, line_pts, wide)
        # round the joints so the bend doesn't notch when downscaled
        for px, py in line_pts:
            pygame.draw.circle(surf, dark, (px, py), max(1, wide // 2))
    else:
        for i in range(n_seg):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            t0, t1 = i / n_seg, (i + 1) / n_seg
            w0 = hw0 * (1.0 - 0.42 * t0)
            w1 = hw0 * (1.0 - 0.42 * t1)
            dx, dy = x1 - x0, y1 - y0
            ln = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / ln, dx / ln
            quad = [
                (x0 - nx * w0, y0 - ny * w0), (x0 + nx * w0, y0 + ny * w0),
                (x1 + nx * w1, y1 + ny * w1), (x1 - nx * w1, y1 - ny * w1)]
            pygame.draw.polygon(surf, _shade_c(stalk, -22),
                                [(int(x), int(y)) for x, y in quad])
            inner = [
                (x0 - nx * (w0 - ss), y0 - ny * (w0 - ss)),
                (x0 + nx * (w0 - ss), y0 + ny * (w0 - ss)),
                (x1 + nx * (w1 - ss), y1 + ny * (w1 - ss)),
                (x1 - nx * (w1 - ss), y1 - ny * (w1 - ss))]
            pygame.draw.polygon(surf, stalk, [(int(x), int(y)) for x, y in inner])
            if i < n_seg - 1:
                nr = w1 * 1.5
                _triad_circle(surf, x1, y1, nr, stalk, sheen=True,
                              sheen_col=sheen, sheen_scale=0.24)
            pygame.draw.line(surf, sheen,
                             (int(x0 - nx * w0 * 0.5), int(y0 - ny * w0 * 0.5)),
                             (int(x1 - nx * w1 * 0.5), int(y1 - ny * w1 * 0.5)),
                             max(1, int(1.0 * ss)))

        # A pair of barbel-feelers flicking off the stalk tip (below the lure).
        tip_x, tip_y = pts[-1]
        for s in (-1, 1):
            bpts = []
            for i in range(9):
                t = i / 8
                bx = tip_x + s * hw0 * 1.5 * t
                by = tip_y + hw0 * (1.0 * t + 1.1 * t * t)
                bpts.append((int(bx), int(by)))
            pygame.draw.lines(surf, _shade_c(stalk, -8), False, bpts,
                              max(1, int(1.4 * ss)))
            pygame.draw.circle(surf, sheen, bpts[-1], max(1, int(hw0 * 0.18)))

    # Head over the stalk root so the brow occludes the stalk base (one body).
    _head(surf, cx, cy, head_r, ss, night=night, tell=compact)

    # Anchor NUB: a small oil-black mound where the stalk leaves the brow, drawn
    # AFTER the head so it visibly fuses the stalk base into the forehead — the
    # eye traces head -> stalk -> lure as one continuous form (no floating lure).
    body = _shade_c(BODY, 12) if night else BODY
    nub_x, nub_y = pts[0]
    nub_r = hw0 * 1.7
    pygame.draw.circle(surf, _shade_c(body, -26), (int(nub_x), int(nub_y)),
                       max(2, int(nub_r)))
    pygame.draw.circle(surf, body, (int(nub_x), int(nub_y)),
                       max(1, int(nub_r * 0.82)))
    # Re-lay the first stalk stub ON TOP of the nub so the filament visibly grows
    # OUT of the forehead mound (the head occluded the original base) — keynote of
    # the "lure on a stick rooted in THIS creature" read.
    stalk_c = _shade_c(STALK, 10) if night else STALK
    (jx0, jy0), (jx1, jy1) = pts[0], pts[1]
    if compact:
        # Compact keeps the same single solid dark stroke through the join so the
        # stub never thins to a wisp at 32px.
        pygame.draw.line(surf, _shade_c(stalk_c, -26),
                         (int(jx0), int(jy0)), (int(jx1), int(jy1)),
                         max(3, int(hw0 * 1.7)))
    else:
        pygame.draw.line(surf, _shade_c(stalk_c, -22),
                         (int(jx0), int(jy0)), (int(jx1), int(jy1)),
                         max(3, int(hw0 * 2.0)))
        pygame.draw.line(surf, stalk_c,
                         (int(jx0), int(jy0)), (int(jx1), int(jy1)),
                         max(2, int(hw0 * 1.3)))

    # The esca lure last + on TOP so its glow blooms over everything — the sole
    # brightest pip, dangled at the stalk tip over the grump's face.
    tip_x, tip_y = pts[-1]
    _esca(surf, tip_x, tip_y, lure_r, ss, night=night, epic=not compact)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(smallv, outline_color=oc, width=2 if night else 1)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _stalk_column(surf, cx, top_y, bot_y, span, ss, *, night=False):
    """The repeatable PILLAR BODY: the illicium STALK as a straight tiling shaft
    — a segmented filament with a knuckle-node + barbel-feeler pair per repeat,
    on a steady cadence. Drawn vertical so the band tiles cleanly top<->bottom."""
    length = bot_y - top_y
    hw = span * 0.20
    seg_len = span * 0.92
    n_seg = max(1, int(round(length / seg_len)))
    seg_len = length / n_seg
    for i in range(n_seg):
        sy = top_y + i * seg_len
        _stalk_segment(surf, cx, sy, seg_len, hw, ss, night=night,
                       barbels=True, node=True)


def _esca_cap(surf, cx, cap_base_y, span, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: the glowing esca lure-bulb (~stalk span +30%)
    sitting at the stalk's gap end, radiating hot-white-peach INTO the gap.
    `point_up` orients the bulb so it hangs toward the gap. Kept compact so the
    cap is never top-heavy vs the shaft."""
    d = -1 if point_up else 1
    # Shaft full width is span*0.40 (hw=span*0.20); a bulb diameter of ~span*0.54
    # is ~shaft +35% — modest, on-axis, never top-heavy vs the filament.
    bulb_r = span * 0.27
    neck_len = span * 0.34
    body = _shade_c(BODY, 12) if night else BODY
    sheen = _shade_c(BODY_SHEEN, 36) if night else BODY_SHEEN

    # Oil-black neck node from the shaft toward the gap (keeps the body dark up to
    # the very tip so the lure is the only bright thing).
    neck_y = cap_base_y + d * neck_len * 0.5
    _triad_circle(surf, cx, neck_y, span * 0.24, body, sheen=True,
                  sheen_col=sheen, sheen_scale=0.26)

    # The esca bulb glowing INTO the gap — the single hot focal of the obstacle.
    bulb_y = cap_base_y + d * (neck_len + bulb_r * 0.7)
    _esca(surf, cx, bulb_y, bulb_r, ss, night=night, glow_mult=1.0)


def _stalk_pillar_obstacle(height, ss, *, flip, night=False):
    """One illicium-stalk PILLAR obstacle: the segmented stalk fills the post and
    a glowing esca lure-bulb CAP sits at the GAP-facing edge, radiating into the
    gap. `flip=True` is the TOP pillar (cap at the bottom/gap edge, bulb hanging
    DOWN); `flip=False` is the BOTTOM pillar (cap at the top/gap edge, bulb up).
    Both mirror the same stalk body — clean vertical, no top-heavy cap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    span = (PIPE_W - 10) * ss
    cap_band = int(54 * ss)
    if flip:
        _stalk_column(surf, cx, 0, bh - cap_band, span, ss, night=night)
        _esca_cap(surf, cx, bh - cap_band, span, ss, point_up=False, night=night)
    else:
        _stalk_column(surf, cx, cap_band, bh, span, ss, night=night)
        _esca_cap(surf, cx, cap_band, span, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(out, outline_color=oc, width=2 if night else 1)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(238, 244, 244)):
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

    SW, SH = 1040, 770
    sheet = pygame.Surface((SW, SH))
    sheet.fill((46, 48, 52))          # neutral grey bg
    _label(sheet, font,
            "CHOCHIN-ANKO  —  Umibozu-versions #1  —  abyssal anglerfish lure-fiend (KIND: lure-on-a-stalk; brood ANCHOR)  —  round 2", 18, 12)
    _label(sheet, small,
            "Oil-black near-silhouette grump wagging a nightlight; cute underbite -> needle-maw; coral BELLY+gum flush only; the hot-white-peach esca is the SOLE brightest pip.",
            18, 32, (210, 196, 188))

    # — Cell A: BIG hero, on an abyssal teal-black sky.
    panel = pygame.Rect(18, 56, 320, 660)
    bgA = _sky(panel.w, panel.h, (8, 16, 22), (14, 30, 38), (24, 48, 54))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (110, 130, 134), panel, 2, border_radius=8)
    hero = build_chochin_anko(scale=1.7, ss=6)
    max_h = panel.h - 110
    if hero.get_height() > max_h:
        sc = max_h / hero.get_height()
        hero = pygame.transform.smoothscale(
            hero, (int(hero.get_width() * sc), int(hero.get_height() * sc)))
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 64))
    _label(sheet, font, "(a) HERO  big scale (SS=6)", panel.x + 8, panel.y + 8)
    _label(sheet, small, "grump body + illicium stalk + esca lure (sole hot pip)",
           panel.x + 8, panel.y + 28, (220, 206, 196))

    # — Cell B: stalk as a tileable PILLAR pair at TRUE obstacle scale (night),
    #   plus a 2x zoom on the cap band proving the esca bulb lanterns the gap.
    panelB = pygame.Rect(352, 56, 330, 660)
    bg = _sky(panelB.w, panelB.h, (6, 10, 18), (8, 18, 30), (14, 34, 44), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (110, 130, 134), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "segmented stalk tiles + esca lure-bulb cap (~shaft+30%)",
           panelB.x + 8, panelB.y + 28, (220, 206, 196))

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 540
    slice_x = panelB.x + 22
    slice_y = panelB.y + 50
    gap_top = 178
    gap_h = 132
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _stalk_pillar_obstacle(top_h, 5, flip=True, night=True)
    bot_pillar = _stalk_pillar_obstacle(bot_h, 5, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (170, 196, 198), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): stalk", slice_x - 2, slice_y + slice_h + 6, (210, 230, 230))
    _label(sheet, small, "tiles; esca lanterns gap", slice_x - 2, slice_y + slice_h + 22, (255, 224, 168))

    # 2x zoom of the cap band (top<->bottom mirror visible).
    cap_band = 54
    zw, zh = pw, 170
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 16
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 168
    zy = panelB.y + 116
    zbg = _sky(zw * 2, zh * 2, (6, 10, 18), (8, 16, 28), (12, 30, 40))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (170, 196, 198), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom: esca bulb", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "top<->bot mirror", zx - 2, zy + zh * 2 + 6, (255, 224, 168))

    # — Cell C: TRUE 32px gameplay chip on day + night, plus a 4x audit + grayscale.
    panelC = pygame.Rect(696, 56, 326, 660)
    pygame.draw.rect(sheet, (38, 40, 44), panelC, border_radius=8)
    pygame.draw.rect(sheet, (110, 130, 134), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "body-dominant compact / day + night sky", panelC.x + 8, panelC.y + 28,
           (220, 206, 196))

    boss_day = build_chochin_anko(scale=0.6, ss=6, compact=True)
    boss_night = build_chochin_anko(scale=0.6, ss=6, night=True, compact=True)
    day = _sky(150, 300, (60, 140, 215), (110, 185, 235), (180, 222, 246))
    night = _sky(150, 300, (6, 12, 26), (10, 24, 44), (18, 50, 64), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 12, dy))
    sheet.blit(night, (panelC.x + 170, dy))
    sheet.blit(boss_day, (panelC.x + 12 + 75 - boss_day.get_width() // 2, dy + 8))
    sheet.blit(boss_night, (panelC.x + 170 + 75 - boss_night.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 18, dy + 6, (16, 28, 40))
    _label(sheet, small, "NIGHT", panelC.x + 176, dy + 6, (255, 224, 168))

    gy = dy + 318
    _label(sheet, small, "TRUE 32px chip on day + night sky:", panelC.x + 12, gy - 2,
           (210, 226, 224))
    icon_src = build_chochin_anko(scale=1.0, ss=6, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))

    chips = [
        (_sky(86, 86, (60, 140, 215), (110, 185, 235), (180, 222, 246)), "day"),
        (_sky(86, 86, (6, 12, 26), (10, 24, 44), (18, 50, 64), stars=True), "night"),
    ]
    sx = panelC.x + 12
    for bg_chip, lab in chips:
        chip = pygame.Rect(sx, gy + 16, 86, 86)
        sheet.blit(bg_chip, chip.topleft)
        pygame.draw.rect(sheet, (140, 162, 162), chip, 1, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 244, 244))
        sx += 96

    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    bx = panelC.x + 12
    byy = gy + 118
    pygame.draw.rect(sheet, (58, 60, 64), (bx - 2, byy - 2, blow.get_width() + 4, blow.get_height() + 4),
                     border_radius=4)
    sheet.blit(blow, (bx, byy))
    _label(sheet, small, "4x blow-up of the 32px chip", bx, byy + blow.get_height() + 4,
           (210, 226, 224))

    gray = _to_gray(blow)
    gx = bx + blow.get_width() + 24
    pygame.draw.rect(sheet, (110, 114, 116), (gx - 2, byy - 2, gray.get_width() + 4, gray.get_height() + 4),
                     border_radius=4)
    sheet.blit(gray, (gx, byy))
    _label(sheet, small, "grayscale value check", gx, byy + gray.get_height() + 4, (24, 24, 24))

    _label(sheet, small,
           "STYLE: flat saturated fills, hard 1-2px ink keyline (20,26,30), dark-core -> flat-fill -> cold-steel rim-sheen triad, 1px grown outline, chibi, scary-CUTE.",
           18, SH - 40, (210, 196, 188))
    _label(sheet, small,
           "PILLAR: the segmented illicium STALK IS the shaft (tiles top<->bottom w/ knuckle-node + barbel-feeler cadence); the glowing esca lure-bulb (~shaft+30%) caps + lanterns the gap. On-axis mirror, no top-heavy cap.",
           18, SH - 22, (210, 196, 188))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()

"""Look-dev sheet for the Skybit BOSS — "BAIAME-ALLFATHER".

A spin-off off the shipped Mokoi flat-graphic plank-mask lineage: the
horned sky all-father reframed as the set's ONE monumental authority
CHARACTER. Where the Wiradjuri source paints Baiame as a larger-than-life
figure with hugely elongated outstretched arms and big white ring-eyes
(white-outline / red-fill body), this take INVERTS the value: a DARK
charcoal authority block carrying yellow-ochre only as banded accent. The
wide reaching double-arc arms could scoop you up or smite you — that is
the imposing read; the big concentric ring-eyes + severe bar-mouth keep
it scary-CUTE rather than merely grim.

Lineage rules this obeys (Mokoi flat-graphic dialect):
  - CHIBI + scary-CUTE; pushed EPIC via richer graphic pattern + scale.
  - FLAT saturated fills. NO within-shape gradients, NO bevels, NO soft
    edges. Detail is PATTERN DENSITY (ochre band-stripes, pipeclay
    dot-rows), never 3D triad shading.
  - Hard 1-2px ink keyline (28,22,30) inside + a 1px grown outline on the
    silhouette so the figure POPS on any sky (parrot `_add_outline`).
  - Charcoal is the DOMINANT mass / value; yellow-ochre lives ONLY in
    arc-dots / band-stripes / the crown — never a body fill. Pipeclay
    dot-rows are the protected hue-blind tell. Ember is cap-confined.
  - SUPERSAMPLE at SS=5-6 then smoothscale down.

PIN (vs sibling Mimi): Mimi is yellow-DOMINANT / LIGHT body; Baiame is
CHARCOAL-DOMINANT / yellow ACCENT — the OPPOSITE value structure. If it
ever drifts warm/light at 32px the body charcoal is pushed darker and the
ochre banding thinned, so the figure always reads as a dark block.

Prop -> pillar mirror: the banded ceremonial STAFF / message-stick is the
pillar — exactly 1 ochre band-stripe + 1 pipeclay dot-row per repeat. The
wide double-arc crown stays on the CHARACTER ONLY; the PILLAR cap is a
SINGLE compact on-axis arc-finial with dot-tipped finials dropped DOWN
toward the gap, so the cap mass falls INTO the gap, never top-heavy.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/mokoi_versions/baiame/render_baiame.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (baiame-allfather) — hex-exact from the locked brief ──────
# Charcoal is the DOMINANT mass AND the dominant VALUE (RE-SPEC B). Yellow
# -ochre is an ACCENT only — it lives in band-stripes, arc-dots, the crown,
# never a body fill. Pipeclay-white dot-rows are the protected hue-blind
# tell. The brick-red-ochre is a thin rim only. Ember is cap-confined.
CHAR        = (46, 42, 48)      # charcoal body (dominant)
CHAR_DK     = (28, 26, 32)      # deeper charcoal for wells / seams (kept dark)
CHAR_HI     = (62, 56, 64)      # a flat lighter charcoal for graphic separation

OCHRE       = (214, 162, 82)    # bright yellow-ochre — ACCENT only
OCHRE_D     = (168, 124, 56)    # deep yellow-ochre for band shadows / keylines

PIPECLAY    = (232, 226, 212)   # pipeclay-white — the protected dot tell
PIPECLAY_DK = (190, 184, 172)   # a quiet shade for dot keylines (still light)

REDRIM      = (172, 92, 60)     # thin brick-red-ochre rim — accent only

EMBER       = (236, 138, 58)    # cap-only ember glow core
EMBER_HOT   = (255, 206, 132)   # ember twinkle centre

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


# ── flat-graphic primitives (NO triad — fills + ink keylines only) ───────────

def _dot_row(surf, cx, y, span_hw, n, r, col, *, key_col=None, ss=3):
    """A single evenly-spaced row of pipeclay dots — the protected tell motif.
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


def _ring_eye(surf, cx, cy, r, ss):
    """A big CONCENTRIC ring-eye — the signature target motif kept from the
    lineage. Yellow-ochre is reserved for the OUTER ring only; the inner bands
    alternate strictly pipeclay<->ink so the target keeps crisp value-contrast
    down to 32px. Flat fills, hard edges — never shading. The stern wide stare
    is what makes the monument scary-CUTE."""
    bands = [
        (1.00, CHAR_DK),
        (0.86, OCHRE),
        (0.68, PIPECLAY),
        (0.50, INK),
        (0.34, PIPECLAY),
        (0.18, INK),
    ]
    for frac, col in bands:
        pygame.draw.circle(surf, col, (int(cx), int(cy)), max(1, int(r * frac)))
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r), max(1, int(1.4 * ss)))
    # A tiny pipeclay catch-dot — the only "glint", kept flat (a stamped dot).
    pygame.draw.circle(surf, PIPECLAY, (int(cx + r * 0.10), int(cy - r * 0.10)),
                       max(1, int(r * 0.07)))


def _arc_band(surf, cx, cy, r_out, r_in, a0, a1, col, ss, *, n=64):
    """A flat filled ARC ribbon (an annulus sector) — the band that builds the
    crown's wide double-arc and the slim pillar finial. Pure flat fill; the
    banding density, not shading, carries the read."""
    pts_out = []
    pts_in = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * (i / n)
        pts_out.append((cx + math.cos(a) * r_out, cy + math.sin(a) * r_out))
        pts_in.append((cx + math.cos(a) * r_in, cy + math.sin(a) * r_in))
    poly = pts_out + pts_in[::-1]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in poly])


def _arc_dot_row(surf, cx, cy, r, a0, a1, n, dr, col, ss, *, key_col=None):
    """A row of pipeclay dots stamped ALONG an arc — the tell, riding the crown
    arcs and the staff dot-rows that follow a curve."""
    for i in range(n):
        a = a0 + (a1 - a0) * (i / max(1, n - 1))
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        pygame.draw.circle(surf, col, (int(x), int(y)), int(dr))
        if key_col is not None:
            pygame.draw.circle(surf, key_col, (int(x), int(y)), int(dr),
                               max(1, int(ss * 0.6)))


# ── the all-father CHARACTER (hero) ──────────────────────────────────────────

def _wide_crown(surf, cx, cy, hw, ss):
    """The wide double-arc CROWN — the monumental authority read. Two concentric
    charcoal arc-ribbons spanning wide across the head, the outer rimmed thin in
    brick-red-ochre, an ochre band-stripe between, and a pipeclay dot-row riding
    the crest. This wide span is the HERO-ONLY flourish; the pillar gets a slim
    on-axis finial instead (RE-SPEC A)."""
    # The arcs open upward, spanning a wide authority crown above the head.
    a0, a1 = math.radians(202), math.radians(338)
    r1o, r1i = hw * 1.62, hw * 1.30        # outer wide arc
    r2o, r2i = hw * 1.22, hw * 0.96        # inner arc
    # Outer charcoal arc with a thin brick-red-ochre rim line on its crest.
    _arc_band(surf, cx, cy, r1o, r1i, a0, a1, CHAR, ss)
    _arc_band(surf, cx, cy, r1o, r1o - hw * 0.10, a0, a1, REDRIM, ss)
    # The ochre band-stripe ribbon between the two arcs (the ACCENT band).
    _arc_band(surf, cx, cy, r1i, r2o, a0, a1, OCHRE, ss)
    _arc_band(surf, cx, cy, r1i, r1i - hw * 0.06, a0, a1, OCHRE_D, ss)
    # Inner charcoal arc.
    _arc_band(surf, cx, cy, r2o, r2i, a0, a1, CHAR, ss)
    # Pipeclay dot-row riding the crest of the ochre stripe — the tell, up high.
    _arc_dot_row(surf, cx, cy, (r1i + r2o) * 0.5, a0 + 0.10, a1 - 0.10, 11,
                 hw * 0.07, PIPECLAY, ss, key_col=PIPECLAY_DK)
    # Three dot-tipped finial horns rising off the crown crest (the "horned"
    # all-father). Centre tallest — kept ON the hero only. FIX 5: deliberate call
    # — thicken the horn shafts ~1px so a hint of the "horned" tell survives down
    # to icon scale, while accepting they cleanly DROP at the true-32px chip
    # (where the brow band + crown silhouette already carry "crowned").
    for s, hfac in ((-1, 0.62), (0, 0.92), (1, 0.62)):
        a = math.radians(270 + s * 34)
        bx = cx + math.cos(a) * r1o
        by = cy + math.sin(a) * r1o
        tx = cx + math.cos(a) * (r1o + hw * hfac)
        ty = cy + math.sin(a) * (r1o + hw * hfac)
        pygame.draw.line(surf, CHAR, (int(bx), int(by)), (int(tx), int(ty)),
                         max(2, int(5.4 * ss)))
        pygame.draw.line(surf, OCHRE, (int(bx), int(by)), (int(tx), int(ty)),
                         max(1, int(2.0 * ss)))
        pygame.draw.circle(surf, PIPECLAY, (int(tx), int(ty)), max(1, int(hw * 0.12)))
        pygame.draw.circle(surf, INK, (int(tx), int(ty)), max(1, int(hw * 0.12)),
                           max(1, int(ss)))


def _reaching_arm(surf, cx, cy, hw, ss, side):
    """One hugely elongated reaching ARM sweeping out and down — the gesture that
    could scoop you up or smite you. A charcoal arc-limb banded with a single
    ochre stripe + a pipeclay dot-row, ending in a splayed pipeclay-dotted hand.
    The wide arm-span is the imposing, monumental authority read."""
    s = side
    # The arm arcs from the shoulder out wide then drops toward the gap.
    cax = cx + s * hw * 0.30        # arc centre
    cay = cy - hw * 0.10
    r_out = hw * 1.95
    r_in = hw * 1.55
    a0 = math.radians(-12 if s > 0 else 180 + 12)
    a1 = math.radians(78 if s > 0 else 180 - 78)
    lo, hi = (a0, a1) if a0 < a1 else (a1, a0)
    _arc_band(surf, cax, cay, r_out, r_in, lo, hi, CHAR, ss)
    # Ochre band-stripe down the centre of the arm + pipeclay dot-row tell.
    _arc_band(surf, cax, cay, (r_out + r_in) * 0.56, (r_out + r_in) * 0.50,
              lo, hi, OCHRE, ss)
    _arc_dot_row(surf, cax, cay, (r_out + r_in) * 0.5, lo + 0.08, hi - 0.08, 6,
                 hw * 0.085, PIPECLAY, ss, key_col=PIPECLAY_DK)
    # The reaching hand: a charcoal palm-knob with three splayed pipeclay finger
    # -dots, at the lower end of the arm arc (reaching DOWN toward the player).
    ha = a1 if s > 0 else a1
    hx = cax + math.cos(ha) * (r_out + r_in) * 0.5
    hy = cay + math.sin(ha) * (r_out + r_in) * 0.5
    # FIX 4: tie the palm to the arm-arc with a thick charcoal wrist beat so the
    # hand reads as the CONTINUATION of the reaching limb, not a detached mitt.
    wx = cax + math.cos(ha - 0.16 * s) * (r_out + r_in) * 0.5
    wy = cay + math.sin(ha - 0.16 * s) * (r_out + r_in) * 0.5
    pygame.draw.line(surf, CHAR, (int(wx), int(wy)), (int(hx), int(hy)),
                     max(2, int((r_out - r_in) * 0.95)))
    pygame.draw.circle(surf, CHAR, (int(hx), int(hy)), int(hw * 0.30))
    pygame.draw.circle(surf, INK, (int(hx), int(hy)), int(hw * 0.30), max(1, int(1.4 * ss)))
    for fk in (-1, 0, 1):
        fa = ha + math.radians(34 * fk) + math.radians(60 * s)
        fx = hx + math.cos(fa) * hw * 0.40
        fy = hy + math.sin(fa) * hw * 0.40
        pygame.draw.line(surf, CHAR, (int(hx), int(hy)), (int(fx), int(fy)),
                         max(2, int(3.2 * ss)))
        pygame.draw.circle(surf, PIPECLAY, (int(fx), int(fy)), max(1, int(hw * 0.09)))


def _allfather_body(surf, cx, cy, hw, hh, ss):
    """The stern big-eyed elder: a dark charcoal authority block of a body+head
    carrying the big concentric ring-eyes, a severe bar-mouth, ochre band-stripe
    chest, and pipeclay dot-row tells. Charcoal dominates the VALUE; yellow is
    banded accent only (RE-SPEC B)."""
    # The charcoal body block (dominant mass) — a tall rounded plinth/torso.
    body = pygame.Rect(int(cx - hw * 0.78), int(cy - hh * 0.10),
                       int(hw * 1.56), int(hh * 1.45))
    pygame.draw.rect(surf, CHAR, body, border_radius=int(hw * 0.30))
    pygame.draw.rect(surf, INK, body, max(1, int(1.6 * ss)), border_radius=int(hw * 0.30))
    # A single ochre band-stripe across the chest (the ACCENT band) with a
    # pipeclay dot-row riding it — the tell on the body.
    band_y = cy + hh * 0.62
    bh = hh * 0.16
    pygame.draw.rect(surf, OCHRE,
                     pygame.Rect(int(cx - hw * 0.70), int(band_y - bh),
                                 int(hw * 1.40), int(2 * bh)))
    pygame.draw.line(surf, OCHRE_D, (int(cx - hw * 0.70), int(band_y - bh)),
                     (int(cx + hw * 0.70), int(band_y - bh)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, OCHRE_D, (int(cx - hw * 0.70), int(band_y + bh)),
                     (int(cx + hw * 0.70), int(band_y + bh)), max(1, int(1.6 * ss)))
    _dot_row(surf, cx, band_y, hw * 0.56, 7, hw * 0.06, PIPECLAY,
             key_col=PIPECLAY_DK, ss=ss)
    # Lower body dot-row tell tying body to the staff below.
    _dot_row(surf, cx, cy + hh * 1.18, hw * 0.50, 6, hw * 0.055, PIPECLAY,
             key_col=PIPECLAY_DK, ss=ss)

    # The HEAD — a charcoal dome sitting on the body, the face-bearing mass.
    head_cy = cy - hh * 0.30
    head_r = hw * 0.86
    pygame.draw.circle(surf, CHAR, (int(cx), int(head_cy)), int(head_r))
    pygame.draw.circle(surf, INK, (int(cx), int(head_cy)), int(head_r), max(1, int(1.6 * ss)))
    # Thin brick-red-ochre brow rim arc above the eyes (accent only).
    pygame.draw.arc(surf, REDRIM,
                    pygame.Rect(int(cx - head_r * 0.82), int(head_cy - head_r * 0.74),
                                int(head_r * 1.64), int(head_r * 1.2)),
                    math.radians(200), math.radians(340), max(2, int(2.6 * ss)))

    # The two big concentric ring-eyes — the dominant face read.
    eye_dx = head_r * 0.46
    eye_y = head_cy - head_r * 0.02
    eye_r = head_r * 0.42
    for s in (-1, 1):
        _ring_eye(surf, cx + s * eye_dx, eye_y, eye_r, ss)

    # A slim ochre nose-bar down the centreline between the eyes (accent).
    nose_top = eye_y + eye_r * 0.5
    nose_bot = head_cy + head_r * 0.60
    pygame.draw.line(surf, OCHRE_D, (int(cx), int(nose_top)), (int(cx), int(nose_bot)),
                     max(2, int(3.0 * ss)))
    pygame.draw.line(surf, OCHRE, (int(cx), int(nose_top)), (int(cx), int(nose_bot)),
                     max(1, int(1.4 * ss)))

    # The SEVERE bar-mouth: a single flat charcoal-dark horizontal bar with a
    # thin pipeclay edge — stern, not a grin. The authority beat.
    mouth_y = head_cy + head_r * 0.74
    mw = head_r * 0.62
    mh = head_r * 0.13
    mouth = pygame.Rect(int(cx - mw), int(mouth_y - mh), int(2 * mw), int(2 * mh))
    pygame.draw.rect(surf, CHAR_DK, mouth, border_radius=int(mh * 0.5))
    pygame.draw.rect(surf, INK, mouth, max(1, int(1.4 * ss)), border_radius=int(mh * 0.5))
    pygame.draw.line(surf, PIPECLAY, (int(cx - mw * 0.82), int(mouth_y)),
                     (int(cx + mw * 0.82), int(mouth_y)), max(1, int(1.4 * ss)))


def build_baiame_hero(scale=1.0, ss=5):
    """The full all-father CHARACTER on its own transparent surface: the wide
    double-arc crown up top, the stern big-eyed charcoal body, and the two hugely
    elongated reaching arms sweeping out and down. Returns an outlined surface.
    Rendered LARGE at SS then smoothscaled so the dense geometry stays crisp.

    This is the HERO render — the wide double-arc crown + full arm-span live ONLY
    here (RE-SPEC A); the pillar gets a slim on-axis finial instead."""
    hw = int(44 * scale) * ss
    hh = int(40 * scale) * ss
    side_pad = int(64 * scale) * ss        # room for the wide reaching arms
    top_pad = int(40 * scale) * ss         # room for the crown horns
    bot_pad = int(20 * scale) * ss

    body_cy = top_pad + hh * 1.4
    W = int(hw * 1.95 * 2 + side_pad * 2)
    H = int(body_cy + hh * 1.45 + bot_pad)
    cx = W // 2

    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # Arms first (behind the body block), then crown behind the head, then the
    # body+face on top so the figure reads as one authority block reaching out.
    head_cy = body_cy - hh * 0.30
    for s in (-1, 1):
        _reaching_arm(surf, cx, body_cy - hh * 0.05, hw, ss, s)
    _wide_crown(surf, cx, head_cy, hw * 0.86, ss)
    _allfather_body(surf, cx, body_cy, hw, hh, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── compact gameplay / icon variant ──────────────────────────────────────────

def _face_tell(surf, cx, cy, hw, ss):
    """A baked LOW-RES face tell sized so smoothscale to true 32px PRESERVES a
    recognizable big-eyed authority head (two fat pipeclay ring-dots ringing two
    ink pupils + a stern pipeclay bar-mouth) instead of mushing to noise."""
    eye_dx = hw * 0.42
    eye_y = cy - hw * 0.06
    eye_r = hw * 0.36
    for s in (-1, 1):
        ex = cx + s * eye_dx
        # RE-SPEC B / FIX 3: the ochre ring is trimmed to a THIN rim only (a hair
        # over the pipeclay disc) so warm-ochre AREA on the chip drops; charcoal
        # stays the dominant value. FIX 2: the ink PUPIL is held FAT (0.56) so the
        # eye stays a clear concentric target and never merges to a solid ochre
        # disc at true 32px — the pupil hole reads as the protected target tell.
        pygame.draw.circle(surf, OCHRE, (int(ex), int(eye_y)), int(eye_r * 1.02))
        pygame.draw.circle(surf, PIPECLAY, (int(ex), int(eye_y)), int(eye_r * 0.92))
        pygame.draw.circle(surf, INK, (int(ex), int(eye_y)), int(eye_r * 0.56))
        # A pinprick pipeclay centre keeps a glint inside the dark pupil so the
        # concentric structure survives the downscale.
        pygame.draw.circle(surf, PIPECLAY, (int(ex), int(eye_y)), max(1, int(eye_r * 0.16)))
    # FIX 2: a stern pipeclay bar-mouth held TALLER (>=2px at true 32px) so it
    # never thins out; FIX 3: kept narrow so it adds little warm area.
    mw = hw * 0.42
    my = cy + hw * 0.50
    mh = hw * 0.14
    pygame.draw.rect(surf, PIPECLAY,
                     pygame.Rect(int(cx - mw), int(my - mh), int(2 * mw), int(2 * mh)),
                     border_radius=int(mh * 0.5))


def build_baiame_compact(scale=1.0, ss=5):
    """GAMEPLAY / 32px-icon variant: a head-dominant compact all-father. The body
    is shrunk and the wide arms are pulled in to short reaching stubs so the
    DARK head + big ring-eyes own the vertical budget at true 32px — the read is
    'big-eyed dark authority head', head unmistakably the hero. Bakes a low-res
    face tell. Charcoal stays the dominant value so it never drifts toward Mimi's
    light body."""
    hw = int(40 * scale) * ss
    hh = int(34 * scale) * ss
    side_pad = int(20 * scale) * ss
    top_pad = int(26 * scale) * ss
    bot_pad = int(12 * scale) * ss

    body_cy = top_pad + hh * 1.0
    W = int(hw * 2.2 + side_pad * 2)
    H = int(body_cy + hh * 1.1 + bot_pad)
    cx = W // 2
    head_cy = body_cy - hh * 0.30

    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # Short reaching arm stubs (the gesture survives, not the full span).
    for s in (-1, 1):
        ax = cx + s * hw * 0.86
        ay = body_cy + hh * 0.10
        pygame.draw.line(surf, CHAR, (int(cx + s * hw * 0.5), int(body_cy - hh * 0.05)),
                         (int(ax), int(ay)), max(2, int(6.0 * ss)))
        pygame.draw.circle(surf, CHAR, (int(ax), int(ay)), int(hw * 0.22))
        pygame.draw.circle(surf, PIPECLAY, (int(ax), int(ay)), max(1, int(hw * 0.08)))
    # A compact single-arc crown (NOT the wide hero double-arc) above the head.
    # FIX 3: the crown's charcoal ribbon is kept as the visible mass and the
    # ochre stripe inside it is THINNED so the crown silhouette still says
    # "crowned" without adding warm area at chip scale.
    crown_r = hw * 0.74
    _arc_band(surf, cx, head_cy, crown_r * 1.30, crown_r * 1.02,
              math.radians(208), math.radians(332), CHAR, ss)
    _arc_band(surf, cx, head_cy, crown_r * 1.14, crown_r * 1.08,
              math.radians(208), math.radians(332), OCHRE, ss)
    _arc_dot_row(surf, cx, head_cy, crown_r * 1.16, math.radians(220),
                 math.radians(320), 4, hw * 0.10, PIPECLAY, ss)

    # The dark head block + body.
    body = pygame.Rect(int(cx - hw * 0.66), int(body_cy - hh * 0.05),
                       int(hw * 1.32), int(hh * 1.10))
    pygame.draw.rect(surf, CHAR, body, border_radius=int(hw * 0.28))
    pygame.draw.rect(surf, INK, body, max(1, int(1.6 * ss)), border_radius=int(hw * 0.28))
    # FIX 3: chest band trimmed ~18% thinner so the total warm-ochre AREA on the
    # chip drops and the icon stays an unambiguous dark charcoal block vs Mimi.
    band_y = body_cy + hh * 0.55
    pygame.draw.rect(surf, OCHRE,
                     pygame.Rect(int(cx - hw * 0.54), int(band_y - hh * 0.09),
                                 int(hw * 1.08), int(hh * 0.18)))
    _dot_row(surf, cx, band_y, hw * 0.44, 5, hw * 0.065, PIPECLAY, ss=ss)

    head_r = hw * 0.80
    pygame.draw.circle(surf, CHAR, (int(cx), int(head_cy)), int(head_r))
    pygame.draw.circle(surf, INK, (int(cx), int(head_cy)), int(head_r), max(1, int(1.6 * ss)))
    _face_tell(surf, cx, head_cy, head_r, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── the banded ceremonial STAFF (pillar body) ────────────────────────────────

OVERHANG = 12


def _staff_repeat(surf, cx, y0, band_h, half_w, ss):
    """ONE repeat of the ceremonial STAFF / message-stick: exactly 1 ochre
    band-stripe stacked over 1 pipeclay dot-row, on the charcoal ground. This is
    the unit that TILES top<->bottom. Pure flat motifs; charcoal stays dominant,
    ochre is a single thin accent stripe per repeat (RE-SPEC B)."""
    # Charcoal ground for this repeat (the dominant mass of the staff).
    pygame.draw.rect(surf, CHAR, (int(cx - half_w), int(y0), int(2 * half_w), int(band_h)))

    # ONE ochre band-stripe across the top of the repeat, thin-edged in deep
    # ochre — the single accent band. Kept narrow so charcoal stays dominant.
    band_y = y0 + band_h * 0.22
    bh = band_h * 0.13
    pygame.draw.rect(surf, OCHRE,
                     pygame.Rect(int(cx - half_w * 0.92), int(band_y - bh),
                                 int(2 * half_w * 0.92), int(2 * bh)))
    pygame.draw.line(surf, OCHRE_D, (int(cx - half_w * 0.92), int(band_y - bh)),
                     (int(cx + half_w * 0.92), int(band_y - bh)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, OCHRE_D, (int(cx - half_w * 0.92), int(band_y + bh)),
                     (int(cx + half_w * 0.92), int(band_y + bh)), max(1, int(1.6 * ss)))

    # ONE pipeclay dot-row below it — the protected tell, a COUNTABLE motif.
    dot_y = y0 + band_h * 0.66
    _dot_row(surf, cx, dot_y, half_w * 0.60, 3, half_w * 0.20, PIPECLAY,
             key_col=PIPECLAY_DK, ss=ss)

    # Twin thin brick-red-ochre rail-lines down both edges (the thin rim accent)
    # so the staff reads as one banded post.
    for s in (-1, 1):
        pygame.draw.line(surf, REDRIM, (int(cx + s * half_w * 0.92), int(y0)),
                         (int(cx + s * half_w * 0.92), int(y0 + band_h)),
                         max(1, int(1.8 * ss)))


def _staff_column(surf, cx, top_y, bot_y, half_w, ss):
    """The repeatable PILLAR BODY: the ceremonial staff as a straight tiling shaft
    — exactly 1 ochre band-stripe + 1 pipeclay dot-row per repeat on the charcoal
    ground (the band that mirrors top<->bottom). NO ember here — ember is
    cap-only."""
    length = bot_y - top_y
    band = half_w * 2.6
    n = max(1, int(round(length / band)))
    band = length / n
    for i in range(n):
        _staff_repeat(surf, cx, top_y + i * band, band, half_w, ss)
    for s in (-1, 1):
        pygame.draw.line(surf, INK, (int(cx + s * half_w), int(top_y)),
                         (int(cx + s * half_w), int(bot_y)), max(1, int(1.6 * ss)))


def _arc_finial_cap(surf, cx, cap_base_y, half_w, ss, *, point_up, night=False):
    """The GAP-EDGE CAP (RE-SPEC A): a SINGLE compact arc-finial tucked tight to
    the shaft axis — NOT the wide hero double-arc. Its dot-tipped finials drop
    DOWN toward the gap so the cap MASS falls INTO the gap, never top-heavy. The
    EMBER glow is CONFINED to this cap (the only warm light anywhere)."""
    d = -1 if point_up else 1     # d points toward the gap
    # RE-SPEC A: the finial must NOT carry mass above the shaft axis. The arc is
    # pulled to a SLIM on-axis cap (span ~= shaft width +30%, no wider) and bows
    # AWAY from the gap, tucked tight against the shaft end so almost nothing
    # rides above it. The dot-tipped finials hang DOWN well into the gap so the
    # heaviest pipeclay mass falls below the shaft axis, never above it.
    cap_r = half_w * 1.30         # slim — shaft width +30%, capped here
    # Keep the arc apex barely proud of the shaft end so the band is on-axis and
    # the visible ribbon sits LOW, not perched as a wide bar overhead.
    cy = cap_base_y + d * half_w * 0.18

    # Ember glow CONFINED to the cap — radiates INTO the gap. Night alpha pulled
    # so the halo stays a contained cap glow.
    gr = int(cap_r * (1.18 if night else 1.0))
    gy = cap_base_y + d * half_w * 0.55
    gl = make_glow_surface(gr, EMBER, alpha_center=150 if night else 118, falloff=2.4)
    surf.blit(gl, (int(cx - gr), int(gy - gr)), special_flags=pygame.BLEND_ADD)

    # A single SLIM charcoal arc-ribbon, narrow in angular span so it reads as a
    # compact on-axis dome, NOT a wide horizontal smile-bar. The arc bows AWAY
    # from the gap; its open ends point toward the gap.
    if point_up:
        a0, a1 = math.radians(44), math.radians(136)    # narrow dome, bows down
    else:
        a0, a1 = math.radians(224), math.radians(316)   # narrow dome, bows up
    _arc_band(surf, cx, cy, cap_r, cap_r * 0.70, a0, a1, CHAR, ss)
    _arc_band(surf, cx, cy, cap_r * 0.90, cap_r * 0.80, a0, a1, OCHRE, ss)
    _arc_band(surf, cx, cy, cap_r, cap_r * 0.92, a0, a1, REDRIM, ss)

    # The pipeclay dot-row no longer rides ALONG the top of the arc (that read as
    # a smile-bar). Instead a SHORT 3-dot row sits at the on-axis crest, the
    # heaviest stamped mass deferred to the hanging finials below.
    _arc_dot_row(surf, cx, cy, cap_r * 0.82, a0 + 0.42, a1 - 0.42, 3,
                 half_w * 0.13, PIPECLAY, ss, key_col=PIPECLAY_DK)

    # Three dot-tipped finials dropping DOWN well into the gap from the arc — the
    # heaviest pipeclay mass falls BELOW the shaft axis (decisively bottom-weighted
    # like Big Reapy's bident). Centre finial longest, on-axis. Drop lengths are
    # held within the cap reserve so the tips read fully inside the gap, not clipped.
    finials = ((-1, 0.78, 0.78), (0, 0.0, 1.12), (1, 0.78, 0.78))
    for s, xfac, lfac in finials:
        bx = cx + s * cap_r * xfac
        by = cy
        tx = cx + s * cap_r * (xfac * 0.55)
        ty = cy + d * cap_r * lfac
        pygame.draw.line(surf, CHAR, (int(bx), int(by)), (int(tx), int(ty)),
                         max(2, int(3.4 * ss)))
        pygame.draw.line(surf, OCHRE, (int(bx), int(by)), (int(tx), int(ty)),
                         max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, PIPECLAY, (int(tx), int(ty)), max(1, int(half_w * 0.18)))
        pygame.draw.circle(surf, INK, (int(tx), int(ty)), max(1, int(half_w * 0.18)),
                           max(1, int(ss)))

    # The ember twinkle core sits at the on-axis arc crest, gap-facing, contained.
    ex = cx
    ey = cy + d * cap_r * 0.55
    pygame.draw.circle(surf, EMBER, (int(ex), int(ey)), max(1, int(half_w * 0.18)))
    pygame.draw.circle(surf, EMBER_HOT, (int(ex), int(ey)), max(1, int(half_w * 0.09)))


def _staff_pillar_obstacle(height, ss, *, flip, night=False):
    """One ceremonial-STAFF pillar obstacle: the band-stripe/dot-row staff fills
    the post and a SLIM on-axis arc-finial CAP sits at the GAP-facing edge, its
    ember glow radiating INTO the gap, its dotted finials dropping DOWN into the
    gap. `flip=True` is the TOP pillar (cap at the bottom/gap edge); `flip=False`
    is the BOTTOM pillar (cap at the top/gap edge). Clean on-axis mirror; the cap
    is never top-heavy (RE-SPEC A)."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    half_w = int((PIPE_W * 0.42)) * ss
    cap_band = int(48 * ss)
    if flip:
        _staff_column(surf, cx, 0, bh - cap_band, half_w, ss)
        _arc_finial_cap(surf, cx, bh - cap_band, half_w, ss, point_up=False, night=night)
    else:
        _staff_column(surf, cx, cap_band, bh, half_w, ss)
        _arc_finial_cap(surf, cx, cap_band, half_w, ss, point_up=True, night=night)
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
           "BAIAME-ALLFATHER  —  mokoi-lineage  —  wide double-arc crowned authority  —  round 2",
           18, 12, (24, 24, 28))
    _label(sheet, small,
           "FLAT-GRAPHIC: CHARCOAL-DOMINANT body/value, yellow-ochre ACCENT only (bands/arcs/crown), pipeclay-white dot-rows = protected tell; ember CAP-confined. Opposite value structure from Mimi.",
           18, 32, (40, 40, 46))

    # — Cell A: the BIG hero CHARACTER (wide double-arc crown + reaching arms).
    panel = pygame.Rect(18, 56, 380, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panel, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panel, 2, border_radius=8)
    _label(sheet, font, "(a) HERO CHARACTER  SS=6  (r2)", panel.x + 8, panel.y + 8, (245, 240, 230))
    _label(sheet, small, "wide double-arc crown + hugely reaching arms (HERO ONLY)",
           panel.x + 8, panel.y + 28, (235, 230, 220))
    hero = build_baiame_hero(scale=1.5, ss=6)
    # Fit the wide hero into the panel.
    maxw = panel.w - 24
    if hero.get_width() > maxw:
        sc = maxw / hero.get_width()
        hero = pygame.transform.smoothscale(
            hero, (int(hero.get_width() * sc), int(hero.get_height() * sc)))
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 56))

    # — Cell B: STAFF as a tileable PILLAR pair at TRUE obstacle scale on NIGHT,
    #   plus a 2x zoom of the CAP band proving the SLIM on-axis finial + mirror.
    panelB = pygame.Rect(406, 56, 320, 600)
    bg = _sky(panelB.w, panelB.h, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (60, 60, 64), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) STAFF -> PILLAR  @ TRUE  (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 500
    slice_x = panelB.x + 22
    slice_y = panelB.y + 44
    gap_top = 158
    gap_h = 124
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _staff_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _staff_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (210, 200, 180), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): 1 ochre band-stripe +", slice_x - 2,
           slice_y + slice_h + 6, (235, 225, 210))
    _label(sheet, small, "1 pipeclay dot-row per repeat; ember on CAP only",
           slice_x - 2, slice_y + slice_h + 22, (255, 210, 150))

    cap_band = 48
    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 14
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 168
    zy = panelB.y + 110
    zbg = _sky(zw * 2, zh * 2, (8, 8, 30), (16, 14, 44), (28, 20, 58))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (210, 200, 180), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "SLIM on-axis dome (shaft+30%);", zx - 2, zy + zh * 2 + 6, (255, 210, 150))
    _label(sheet, small, "3 finials DROP deep into gap = bottom-weighted",
           zx - 2, zy + zh * 2 + 22, (255, 210, 150))

    # — Cell C: TRUE 32px gameplay chip on a DAY sky AND a NIGHT sky, plus a 4x
    #   audit + grayscale tell-check (the value-dominance / Mimi separation read).
    panelC = pygame.Rect(734, 56, 368, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panelC, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8, (245, 240, 230))
    _label(sheet, small, "head-dominant compact; DARK block on day + night",
           panelC.x + 8, panelC.y + 28, (235, 230, 220))

    boss = build_baiame_compact(scale=0.62, ss=5)
    day = _sky(140, 280, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(140, 280, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    dy = panelC.y + 48
    sheet.blit(day, (panelC.x + 16, dy))
    sheet.blit(night, (panelC.x + 168, dy))
    sheet.blit(boss, (panelC.x + 16 + 70 - boss.get_width() // 2, dy + 8))
    sheet.blit(boss, (panelC.x + 168 + 70 - boss.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 16 + 6, dy + 6, (18, 28, 24))
    _label(sheet, small, "NIGHT", panelC.x + 168 + 6, dy + 6, (255, 220, 200))

    icon_src = build_baiame_compact(scale=1.0, ss=5)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))
    sc64 = 64 / icon_src.get_height()
    icon64 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc64)), 64))

    gy = dy + 296
    _label(sheet, small, "TRUE 32px at 1x (no blow-up):", panelC.x + 16, gy - 2,
           (235, 225, 215))
    swatches = [
        ((40, 110, 200), "day"),
        ((40, 30, 70), "night"),
        ((96, 96, 100), "neutral"),
    ]
    sx = panelC.x + 16
    sw = 92
    for col, lab in swatches:
        chip = pygame.Rect(sx, gy + 16, sw, 76)
        pygame.draw.rect(sheet, col, chip, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 240))
        sx += sw + 8

    chip = pygame.Rect(panelC.x + 16, gy + 104, 86, 100)
    pygame.draw.rect(sheet, (78, 78, 82), chip, border_radius=4)
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 3, icon32.get_height() * 3))
    sheet.blit(blow, (chip.x + 6, chip.centery - blow.get_height() // 2))
    sheet.blit(icon64, (chip.right + 10, chip.centery - icon64.get_height() // 2))
    _label(sheet, small, "3x / 64px audit", chip.x + 4, chip.y + 2, (240, 240, 240))

    gray = _to_gray(icon64)
    gchip = pygame.Rect(panelC.x + 244, gy + 104, 100, 100)
    pygame.draw.rect(sheet, (124, 128, 124), gchip, border_radius=4)
    sheet.blit(gray, (gchip.centerx - gray.get_width() // 2,
                      gchip.centery - gray.get_height() // 2))
    _label(sheet, small, "grayscale: dark block", gchip.x + 4, gchip.y + 2, (24, 24, 24))

    # — Footer: style notes.
    _label(sheet, small,
           "FLAT only: detail via PATTERN DENSITY (ochre band-stripes + pipeclay dot-rows), never 3D shading; CHARCOAL dominant in VALUE; yellow-ochre ACCENT only; ember CAP-confined.",
           18, SH - 64, (40, 40, 46))
    _label(sheet, small,
           "staff->pillar: 1 ochre band-stripe + 1 pipeclay dot-row per repeat (tiles); cap = SLIM on-axis arc-finial, dotted finials drop DOWN into gap. Wide double-arc crown = HERO only.",
           18, SH - 44, (40, 40, 46))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()

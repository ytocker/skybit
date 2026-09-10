"""Look-dev sheet for the Skybit DEVIL boss take A5 — "PYRECROWN".

A devilish-death hybrid: a SERENE pale SKULL crowned with FIVE black candle-horns
burning GREEN soul-flames — the Baphomet head-torch ("the soul exalted above
matter") multiplied into an altar-demon crown. Group A's only GREEN palette and
its only calm/closed-eye face: an eerie-cute priest of the dead, hands pressed in
a blessing under a tiny cassock.

House style this obeys (the warren-clown / Big-Reapy grammar):
  - CHIBI proportions — a tall-ish bone skull, tiny cassock body, the candle CROWN
    is the identity.
  - FLAT fills + hard 1-2px ink keylines (22,18,26). No within-shape gradients,
    no soft/feathered edges, no bevels.
  - Form via the triad: dark-core ring -> flat fill -> top-left rim sheen.
  - Flames are FLAT teardrop SHAPES with an OUTSIDE BLEND_ADD glow halo — never a
    soft gradient blob; the candle/soul-fire stays contained (not Glitchfiend neon,
    not Baalgoat's torch).
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - SUPERSAMPLE then smoothscale.

Set-wide guardrails honoured: the five candle-horns are STRAIGHT verticals (no
curved/ram-horn pair); the green soul-flame is a contained candle teardrop, not a
neon wash or a torch brazier.

Prop -> pillar mirror: a tall paschal CANDLE-PILLAR. The fat dripping WAX column =
the repeatable PILLAR BODY (wax-drip banding); a single big green flame + a small
skull-knob = the detachable GAP-EDGE CAP that flourishes INTO the gap. Distinct
from The Hollow's snuffer — this LIGHTS, never snuffs.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/render_skybit_devil_pyrecrown.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── "bone & green soul-flame" palette (take A5) ──────────────────────────────
# Pale bone DOMINANT for the serene skull; WAX-BLACK candle-horns + cassock as the
# value anchor that pins the silhouette on both skies; EMERALD/LIME soul-flame as
# the lone glow accent — Group A's only green. The serene closed-eye + green crown
# is the whole identity, so green must POP hardest on the night sky.
BONE        = (236, 228, 206)   # skull / bone fill
BONE_DK     = (170, 150, 112)   # dark-core ring + jaw shadow seat
BONE_SHEEN  = (252, 246, 226)   # top-left rim sheen
TOOTH       = (246, 240, 222)
TOOTH_DK    = (150, 130, 96)

WAX         = (44, 40, 52)      # wax-black candle-horn / cassock body fill
WAX_DK      = (26, 22, 32)      # candle dark-core / fold grooves
WAX_SHEEN   = (82, 76, 96)      # cool top-left rim on the black wax
ROBE        = (36, 60, 50)      # deep emerald-shadow cassock (green-dominant set)
ROBE_DK     = (22, 40, 34)
ROBE_SHEEN  = (66, 104, 84)

FLAME       = (110, 236, 168)   # soul-flame green (outer teardrop)
FLAME_CORE  = (206, 255, 224)   # flame-pale hot core
FLAME_DEEP  = (44, 150, 96)     # flame deep-green base seat
WICK        = (24, 20, 26)
GOLD        = (210, 178, 92)    # tiny cassock clasp / cord
GOLD_HI     = (250, 230, 160)

INK         = (22, 18, 26)      # the house keyline


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_d=28):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Sculpted volume while staying flat-shaded."""
    pygame.draw.circle(surf, _shade_c(col, -46), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.06))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, sheen_d),
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


# ── the green soul-flame (flat teardrop + outside glow) ──────────────────────

def _soul_flame(surf, cx, base_y, h, ss, *, night=False):
    """A contained soul-flame: an OUTSIDE additive glow halo, then a FLAT green
    teardrop (deep-green seat -> emerald body -> pale hot core) — NOT a soft
    gradient blob and NOT a neon wash. The teardrop tapers to a point above the
    wick. `night` lifts the halo so the green reads LIT on a dark sky (where this
    crown must pop hardest)."""
    w = h * 0.52
    # Outside glow first so the flat teardrop sits crisp on top of it.
    halo_a = 200 if night else 130
    halo_r = int(w * (1.35 if night else 1.05))
    glow = make_glow_surface(halo_r, FLAME, alpha_center=halo_a, falloff=2.2)
    surf.blit(glow, (int(cx - halo_r - 1), int(base_y - h * 0.55 - halo_r - 1)),
              special_flags=pygame.BLEND_ADD)

    def _teardrop(cy_top, ht, half_w, col):
        # A flame teardrop: rounded base bulge tapering to a tip, drawn as a flat
        # polygon (hard edges = candle-fire, not soft glow).
        pts = []
        n = 18
        for i in range(n + 1):
            t = i / n                              # 0 base .. 1 tip
            # Width swells just above the base then necks to the point.
            ww = half_w * math.sin(t * math.pi) * (1.0 - 0.35 * t) + half_w * 0.18 * (1 - t)
            # Gentle S-flicker lean so the flame isn't a stiff symmetric leaf.
            lean = half_w * 0.28 * math.sin(t * math.pi) * (t - 0.4)
            x = cx + lean
            y = cy_top + ht * t
            pts.append((x - ww, y))
        for i in range(n, -1, -1):
            t = i / n
            ww = half_w * math.sin(t * math.pi) * (1.0 - 0.35 * t) + half_w * 0.18 * (1 - t)
            lean = half_w * 0.28 * math.sin(t * math.pi) * (t - 0.4)
            x = cx + lean
            y = cy_top + ht * t
            pts.append((x + ww, y))
        pygame.draw.polygon(surf, col, [(int(px), int(py)) for px, py in pts])

    tip_y = base_y - h
    # Deep-green outer seat, emerald body, pale hot core — three flat nested drops.
    _teardrop(tip_y, h, w, FLAME_DEEP)
    _teardrop(tip_y + h * 0.10, h * 0.86, w * 0.74, FLAME)
    _teardrop(tip_y + h * 0.26, h * 0.62, w * 0.40, FLAME_CORE)
    # White-hot pinprick low in the core where the flame meets the wick.
    pygame.draw.circle(surf, (240, 255, 244),
                       (int(cx), int(base_y - h * 0.18)), max(1, int(w * 0.18)))


# ── one black candle-horn (straight vertical taper) ──────────────────────────

def _candle_horn(surf, cx, base_y, ch, hw, ss, *, night=False, lean=0.0):
    """A STRAIGHT vertical wax taper (NOT a curved horn) rising from the cranium
    rim, with frozen wax drips down one side, a melted lip, and a green soul-flame
    on top. `lean` tilts the taper slightly off-vertical so the five-candle fan
    splays OUTWARD — but each stays a straight taper, never a curved ram-horn arc.
    A fat melted-LIP overhang at the tip is the read that separates this from a
    horn/spike: an altar candle that has burned down and slumped."""
    top_y = base_y - ch
    tip_dx = lean * ch                            # straight lean, not a curve
    # The wax column: a tapering quad, dark-core then fill then sheen. A near-
    # cylindrical taper (only mild neck) so it reads as a fat CANDLE, not a spike.
    base_hw = hw
    top_hw = hw * 0.82
    col_pts = [
        (cx - base_hw, base_y),
        (cx + base_hw, base_y),
        (cx + tip_dx + top_hw, top_y),
        (cx + tip_dx - top_hw, top_y),
    ]
    pygame.draw.polygon(surf, WAX_DK, [(int(x), int(y)) for x, y in col_pts])
    inner = [
        (cx - base_hw + ss, base_y),
        (cx + base_hw - ss, base_y),
        (cx + tip_dx + top_hw - ss, top_y + ss),
        (cx + tip_dx - top_hw + ss, top_y + ss),
    ]
    pygame.draw.polygon(surf, WAX, [(int(x), int(y)) for x, y in inner])
    # Top-left cool sheen stripe down the lit side of the black wax.
    pygame.draw.line(surf, WAX_SHEEN,
                     (int(cx - base_hw + 1.4 * ss), int(base_y - ss)),
                     (int(cx + tip_dx - top_hw + 1.4 * ss), int(top_y + 2 * ss)),
                     max(1, int(1.6 * ss)))
    # Frozen wax drips: bulging teardrop runs frozen down BOTH sides so the candle
    # reads MELTED (an altar candle) even at 1x — the drip tell is the candle read.
    for dt, dl, side in ((0.34, 0.40, 1), (0.60, 0.30, -1), (0.78, 0.46, 1)):
        dy = base_y - ch * dt
        dx = cx + tip_dx * (1 - dt) + side * base_hw * 0.82
        rr = hw * dl
        pygame.draw.circle(surf, WAX_DK, (int(dx), int(dy)), int(rr))
        pygame.draw.circle(surf, WAX, (int(dx - ss), int(dy - ss)),
                           max(1, int(rr - ss)))
        # the drip tail running down
        pygame.draw.line(surf, WAX, (int(dx), int(dy)),
                         (int(dx - tip_dx * 0.04), int(dy + rr * 1.7)),
                         max(1, int(rr * 0.85)))
    # Fat MELTED LIP: a wide wax collar that overhangs the column top with a couple
    # of lip-drips spilling over the rim — the unmistakable burned-down-candle tell.
    lip_cx = cx + tip_dx
    lip_w = top_hw * 1.5
    pygame.draw.ellipse(surf, WAX_DK,
                        (int(lip_cx - lip_w), int(top_y - ss * 1.0),
                         int(lip_w * 2), int(lip_w * 1.05)))
    pygame.draw.ellipse(surf, WAX,
                        (int(lip_cx - lip_w + ss), int(top_y - ss * 0.5),
                         int(lip_w * 2 - 2 * ss), int(lip_w * 0.9)))
    # Cool sheen catching the front edge of the lip collar.
    pygame.draw.arc(surf, WAX_SHEEN,
                    (int(lip_cx - lip_w + ss), int(top_y - ss * 0.5),
                     int(lip_w * 2 - 2 * ss), int(lip_w * 0.9)),
                    math.radians(195), math.radians(345), max(1, int(1.4 * ss)))
    # Two lip-drips spilling over the rim — the molten overflow.
    for ld in (-0.62, 0.5):
        ldx = lip_cx + ld * lip_w
        pygame.draw.circle(surf, WAX, (int(ldx), int(top_y + lip_w * 0.5)),
                           max(1, int(hw * 0.24)))
        pygame.draw.line(surf, WAX, (int(ldx), int(top_y + lip_w * 0.4)),
                         (int(ldx), int(top_y + lip_w * 0.95)),
                         max(1, int(hw * 0.3)))
    # The molten wax pool at the wick, glowing faintly green from the flame above.
    pygame.draw.ellipse(surf, _shade_c(FLAME_DEEP, -6),
                        (int(lip_cx - top_hw * 0.5), int(top_y - ss * 0.5),
                         int(top_hw), int(top_hw * 0.7)))
    # Wick + soul-flame.
    pygame.draw.line(surf, WICK, (int(lip_cx), int(top_y)),
                     (int(lip_cx), int(top_y - ch * 0.05)), max(1, int(1.4 * ss)))
    fh = ch * 0.58
    _soul_flame(surf, lip_cx, top_y - ch * 0.02, fh, ss, night=night)


# ── the serene crowned skull face ────────────────────────────────────────────

def _skull_face(surf, cx, cy, r, ss, *, night=False):
    """A SERENE bone skull (closed/blessing eyes, calm small mouth) — the eerie
    priest-of-the-dead face. Calm closed-eye crescents (not glowing sockets), a
    small heart nose, a quiet pressed-lip tooth band. The candle CROWN above does
    the menace; the face stays peaceful — that contrast is the scary-cute beat."""
    # Cranium dome.
    _triad_circle(surf, cx, cy, r, BONE)

    # Jaw: a rounded trapezoid for the lower face so it reads skull, not ball.
    jaw_top = cy + r * 0.32
    jaw_bot = cy + r * 1.00
    jaw = [(cx - r * 0.70, jaw_top), (cx - r * 0.50, jaw_bot),
           (cx + r * 0.50, jaw_bot), (cx + r * 0.70, jaw_top)]
    pygame.draw.polygon(surf, _shade_c(BONE, -46),
                        [(int(x), int(y)) for x, y in jaw])
    inset = [(cx - r * 0.64, jaw_top + ss), (cx - r * 0.45, jaw_bot - ss),
             (cx + r * 0.45, jaw_bot - ss), (cx + r * 0.64, jaw_top + ss)]
    pygame.draw.polygon(surf, BONE, [(int(x), int(y)) for x, y in inset])
    _triad_circle(surf, cx, cy, r, BONE, sheen=True)

    # Cheekbone hollows — two shallow scoops so the wide jaw reads as bone.
    for s in (-1, 1):
        hr = pygame.Rect(0, 0, int(r * 0.28), int(r * 0.34))
        hr.center = (int(cx + s * r * 0.60), int(cy + r * 0.40))
        pygame.draw.ellipse(surf, _shade_c(BONE, -32), hr)

    # — Eyes: SERENE closed crescents inside softened socket hollows. A faint green
    #   under-rim from the crown's soul-light, NOT a glowing socket (this is the
    #   calm priest, not Big Reapy's lit eyes). The lashes-down crescent is the
    #   whole "blessing / at peace" read.
    eye_dx = r * 0.40
    eye_dy = -r * 0.02
    sock_r = r * 0.30
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        # Soft bone socket hollow (shape only — reads in grayscale).
        pygame.draw.circle(surf, _shade_c(BONE, -30), (int(ex), int(ey)),
                           int(sock_r))
        pygame.draw.circle(surf, _shade_c(BONE, -10),
                           (int(ex - s * sock_r * 0.18), int(ey - sock_r * 0.2)),
                           int(sock_r * 0.7))
        # A faint green soul-glow pooled along the lower socket rim (the crown's
        # light catching the bone) — subtle, so the face stays serene not lit.
        ga = 150 if night else 90
        gl = make_glow_surface(int(sock_r * 0.9), FLAME, alpha_center=ga, falloff=2.4)
        surf.blit(gl, (int(ex - sock_r * 0.9 - 1),
                       int(ey + sock_r * 0.25 - sock_r * 0.9 - 1)),
                  special_flags=pygame.BLEND_ADD)
        # Closed-eye crescent: a downward-bowed lash line (peaceful, eyes shut).
        lash_w = sock_r * 1.05
        pygame.draw.arc(surf, INK,
                        (int(ex - lash_w), int(ey - sock_r * 0.2),
                         int(lash_w * 2), int(sock_r * 1.1)),
                        math.radians(200), math.radians(340), max(2, int(2.4 * ss)))
        # A tiny green emphasis on the lash so the closed eye reads soul-touched.
        pygame.draw.arc(surf, FLAME_DEEP,
                        (int(ex - lash_w * 0.8), int(ey - sock_r * 0.1),
                         int(lash_w * 1.6), int(sock_r * 0.9)),
                        math.radians(210), math.radians(330), max(1, int(1.2 * ss)))
        # High calm bone brow — a gentle bow, never the angry inner-down V.
        pygame.draw.arc(surf, _shade_c(BONE, -32),
                        (int(ex - sock_r * 1.1), int(ey - sock_r * 1.5),
                         int(sock_r * 2.2), int(sock_r * 1.4)),
                        math.radians(28), math.radians(152), max(2, int(2.0 * ss)))

    # — Nose: small upturned heart hole between + below the sockets.
    nose_y = cy + r * 0.36
    nose = [(cx, nose_y - r * 0.09), (cx - r * 0.10, nose_y + r * 0.12),
            (cx + r * 0.10, nose_y + r * 0.12)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose])

    # — Mouth: a QUIET pressed lip — a small, gently-bowed tooth band, NOT a wide
    #   grin. The calm closed mouth keeps the priest serene. A faint smile lift.
    grin_y = cy + r * 0.66
    grin_hw = r * 0.42
    grin_h = r * 0.20
    bow_amp = grin_h * 0.5

    def _bow(xr):
        return bow_amp * (xr * xr)

    seat_top, seat_bot = [], []
    n = 12
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * grin_hw
        yt = grin_y - _bow(xr)
        seat_top.append((x, yt))
        seat_bot.append((x, yt + grin_h))
    seat = seat_top + seat_bot[::-1]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in seat])
    # A few small even teeth (quiet, not a jack-grin).
    teeth = 6
    gap = grin_hw * 0.12
    tw = (grin_hw * 2.0 - gap * (teeth - 1)) / teeth
    th = grin_h * 0.66
    for i in range(teeth):
        tx = -grin_hw + i * (tw + gap)
        xr = (tx + tw * 0.5) / grin_hw
        ty = grin_y - _bow(xr) + ss
        rect = pygame.Rect(int(cx + tx + ss * 0.5), int(ty),
                           int(tw - ss * 0.5), int(th))
        pygame.draw.rect(surf, TOOTH, rect, border_radius=max(1, int(1.2 * ss)))
        pygame.draw.rect(surf, TOOTH_DK, rect, max(1, int(ss)),
                         border_radius=max(1, int(1.2 * ss)))


def _crown(surf, cx, cy, r, ss, *, night=False):
    """The FIVE black candle-horns fanning up from the cranium rim — STRAIGHT
    tapers (never a curved horn pair), each tipped with a green soul-flame. The
    centre candle is tallest; the pair-leans splay symmetrically so the crown
    reads as a flaming altar-fan. This crown IS the identity."""
    # Five candles seated WIDE along the cranium rim so sky shows between tapers and
    # the crown reads as a splayed candelabra-fan, not a packed mohawk. The outer
    # pair splay clearly OUTWARD past the temples; leans are positive-outward (the
    # flames fan apart, never converging into one clump). Heights step BOLDLY
    # (short outers, tall centre) and widths vary so no two candles twin. Each
    # column stays a STRAIGHT taper (set-wide guardrail) — only the lean differs.
    specs = [
        # (x along rim, height factor, OUTWARD lean, width factor)
        (-1.02, 0.62, -0.30, 0.86),
        (-0.56, 0.96, -0.15, 1.12),
        (0.00, 1.20, 0.00, 1.00),    # tallest, slightly slimmer centre candle
        (0.56, 0.88, 0.15, 1.18),
        (1.02, 0.68, 0.30, 0.82),
    ]
    base_ch = r * 1.10
    base_hw = r * 0.165
    # Seat the candle feet on the dome so they look planted in the bone, following
    # the cranium curve so the outer feet sit lower (the dome curves away).
    for sx, hf, lean, wf in specs:
        bx = cx + sx * r * 0.72
        curve = max(0.0, 1.0 - min(1.0, (sx * 0.72) ** 2))
        by = cy - math.sqrt(curve) * r * 0.84 + r * 0.05
        ch = base_ch * hf
        _candle_horn(surf, bx, by, ch, base_hw * wf, ss, night=night, lean=lean)


def _cassock_body(surf, cx, neck_y, w, h, ss):
    """The tiny cassock body: a narrow deep-emerald robe (green-dominant set) with
    two little bone hands pressed together in prayer/blessing at the chest, a thin
    gold cord. Deliberately small so the skull + crown dominate."""
    hem_y = neck_y + h
    body = [
        (cx - w * 0.26, neck_y),
        (cx - w * 0.54, neck_y + h * 0.55),
        (cx - w * 0.60, hem_y),
        (cx + w * 0.60, hem_y),
        (cx + w * 0.54, neck_y + h * 0.55),
        (cx + w * 0.26, neck_y),
    ]
    pygame.draw.polygon(surf, ROBE_DK, [(int(x), int(y)) for x, y in body])
    inner = [(cx - w * 0.22, neck_y + ss), (cx - w * 0.48, neck_y + h * 0.55),
             (cx - w * 0.54, hem_y - ss), (cx + w * 0.54, hem_y - ss),
             (cx + w * 0.48, neck_y + h * 0.55), (cx + w * 0.22, neck_y + ss)]
    pygame.draw.polygon(surf, ROBE, [(int(x), int(y)) for x, y in inner])
    # Top-left rim sheen down the lit robe edge.
    pygame.draw.line(surf, ROBE_SHEEN,
                     (int(cx - w * 0.30), int(neck_y + h * 0.18)),
                     (int(cx - w * 0.52), int(hem_y - ss)), max(1, int(1.6 * ss)))
    # A centre fold groove so the robe reads draped.
    pygame.draw.line(surf, ROBE_DK, (int(cx), int(neck_y + h * 0.2)),
                     (int(cx), int(hem_y - ss)), max(1, int(1.4 * ss)))
    # Thin gold cord at the waist.
    cordy = neck_y + h * 0.46
    pygame.draw.line(surf, GOLD, (int(cx - w * 0.5), int(cordy)),
                     (int(cx + w * 0.5), int(cordy)), max(1, int(1.6 * ss)))
    pygame.draw.circle(surf, GOLD_HI, (int(cx - w * 0.5), int(cordy)),
                       max(1, int(1.4 * ss)))
    # Praying hands: a clean STEEPLE silhouette — a pale bone teardrop coming to a
    # point at the top with a visible centre seam splitting the two pressed palms,
    # so it reads as a praying gesture and not a random pale lump.
    hy = neck_y + h * 0.34
    steeple_w = w * 0.30
    steeple_h = h * 0.42
    tip = (cx, hy - steeple_h * 0.5)
    steeple = [
        tip,
        (cx + steeple_w * 0.5, hy - steeple_h * 0.12),
        (cx + steeple_w * 0.42, hy + steeple_h * 0.5),
        (cx - steeple_w * 0.42, hy + steeple_h * 0.5),
        (cx - steeple_w * 0.5, hy - steeple_h * 0.12),
    ]
    pygame.draw.polygon(surf, _shade_c(BONE, -34),
                        [(int(x), int(y)) for x, y in steeple])
    inner = [(tip[0], tip[1] + ss),
             (cx + steeple_w * 0.42, hy - steeple_h * 0.1),
             (cx + steeple_w * 0.34, hy + steeple_h * 0.44),
             (cx - steeple_w * 0.34, hy + steeple_h * 0.44),
             (cx - steeple_w * 0.42, hy - steeple_h * 0.1)]
    pygame.draw.polygon(surf, BONE, [(int(x), int(y)) for x, y in inner])
    # Centre seam between the two pressed palms — the steeple split.
    pygame.draw.line(surf, BONE_DK, (int(cx), int(tip[1] + ss)),
                     (int(cx), int(hy + steeple_h * 0.46)), max(1, int(ss)))
    # Top-left sheen on the lit palm.
    pygame.draw.line(surf, BONE_SHEEN,
                     (int(cx - steeple_w * 0.18), int(hy - steeple_h * 0.3)),
                     (int(cx - steeple_w * 0.3), int(hy + steeple_h * 0.3)),
                     max(1, int(ss)))


def build_pyrecrown(scale=1.0, ss=3, *, night=False):
    """The full boss figure on its own transparent surface: candle crown on top,
    serene skull mid, tiny praying cassock below. Returns an outlined surface and
    its baseline (feet) y. The surface is sized to the WHOLE figure — the crown's
    flame tips and the splayed outer flames each get explicit margin so nothing
    clips off the panel at showcase scale. `night` lifts the soul-flame glow so the
    green crown reads LIT on a dark sky (where it must pop hardest)."""
    skull_r = int(60 * scale) * ss
    body_h = int(90 * scale) * ss
    side_pad = int(34 * scale) * ss     # room for the splayed outer flames + glow
    top_pad = int(40 * scale) * ss      # room above the tallest flame tip + halo
    bot_pad = int(18 * scale) * ss

    # Geometry of the figure measured downward from the tallest flame tip.
    # Crown: centre candle base_ch = skull_r/ss*1.10*scale... computed in _crown,
    # so mirror its tallest reach here. Centre candle foot sits ~r*0.79 above the
    # skull centre; its column is base_ch*1.20 tall; the flame adds ch*0.58 more.
    base_ch = skull_r * 1.10
    centre_foot_above = skull_r * 0.79          # math.sqrt(1)*0.84 - 0.05
    centre_col = base_ch * 1.20
    centre_flame = (base_ch * 1.20) * 0.58
    crown_top_above_skull = centre_foot_above + centre_col + centre_flame

    skull_cy = top_pad + crown_top_above_skull
    neck_y = skull_cy + skull_r * 0.96
    feet_y = neck_y + body_h

    W = int(skull_r * 2 + side_pad * 2)
    H = int(feet_y + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    skull_cx = W // 2

    body_w = skull_r * 2.2

    # Draw order: crown candles behind the skull dome so the dome occludes their
    # feet (planted look), then skull, then body over the jaw.
    _crown(surf, skull_cx, skull_cy, skull_r, ss, night=night)
    _skull_face(surf, skull_cx, skull_cy, skull_r, ss, night=night)
    _cassock_body(surf, skull_cx, neck_y, body_w, body_h, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(small), feet_y / ss


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _wax_column(surf, cx, top_y, bot_y, hw, ss):
    """The repeatable PILLAR BODY: a fat dripping WAX column with melted drip
    BANDING down the shaft (the wax-band tile that mirrors). Triad-shaded black
    wax with cool sheen, drips bulging off both sides at a steady cadence."""
    length = bot_y - top_y
    # The column core.
    pygame.draw.rect(surf, WAX_DK, (int(cx - hw), int(top_y), int(2 * hw), int(length)))
    pygame.draw.rect(surf, WAX, (int(cx - hw + ss), int(top_y),
                                 int(2 * hw - 2 * ss), int(length)))
    # Top-left sheen stripe.
    pygame.draw.line(surf, WAX_SHEEN, (int(cx - hw + 1.6 * ss), int(top_y)),
                     (int(cx - hw + 1.6 * ss), int(bot_y)), max(1, int(1.8 * ss)))
    # Wax-drip banding: rounded melted bulges off both edges at a regular cadence
    # so the body tiles — the drip band is what repeats top<->bottom.
    band = hw * 1.4
    n = max(2, int(length / band))
    band = length / n
    for i in range(n):
        by = top_y + (i + 0.5) * band
        for s in (-1, 1):
            ex = cx + s * hw
            rr = hw * 0.52
            pygame.draw.circle(surf, WAX_DK, (int(ex), int(by)), int(rr))
            pygame.draw.circle(surf, WAX, (int(ex - s * ss), int(by - ss)),
                               max(1, int(rr - ss)))
            # short drip-run tail downward
            pygame.draw.line(surf, WAX, (int(ex), int(by)),
                             (int(ex), int(by + rr * 1.4)), max(1, int(rr * 0.8)))
        # A thin cool sheen tick on each band's left bulge.
        pygame.draw.circle(surf, WAX_SHEEN,
                           (int(cx - hw - ss), int(by - ss)), max(1, int(hw * 0.16)))


def _candle_cap(surf, cx, cap_base_y, hw, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: a small bone SKULL-KNOB melted onto the column
    top, crowned with one big GREEN soul-flame flourishing INTO the gap. This is
    the candle-pillar 'business end' — it LIGHTS the gap (distinct from Hollow's
    snuffer). `point_up` sends the flame toward the gap (up for a bottom pillar)."""
    d = -1 if point_up else 1
    # Melted wax lip the knob sits in.
    pygame.draw.ellipse(surf, WAX_SHEEN,
                        (int(cx - hw * 1.1), int(cap_base_y - hw * 0.4),
                         int(hw * 2.2), int(hw * 1.0)))
    # Small bone skull-knob.
    knob_r = hw * 0.92
    knob_cy = cap_base_y + d * knob_r * 1.05
    _triad_circle(surf, cx, knob_cy, knob_r, BONE)
    # Two tiny dark sockets + a stub jaw so the knob reads as a skull.
    for s in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (int(cx + s * knob_r * 0.4),
                            int(knob_cy - d * knob_r * 0.1)),
                           max(1, int(knob_r * 0.22)))
    pygame.draw.line(surf, INK,
                     (int(cx - knob_r * 0.35), int(knob_cy + d * knob_r * 0.45)),
                     (int(cx + knob_r * 0.35), int(knob_cy + d * knob_r * 0.45)),
                     max(1, int(1.4 * ss)))
    # Wick + the big soul-flame flourishing INTO the gap.
    wick_y = knob_cy + d * knob_r
    pygame.draw.line(surf, WICK, (int(cx), int(wick_y)),
                     (int(cx), int(wick_y + d * knob_r * 0.3)), max(1, int(1.6 * ss)))
    fh = hw * 3.1
    if point_up:
        _soul_flame(surf, cx, wick_y + d * knob_r * 0.3, fh, ss, night=night)
    else:
        # Flame points DOWN into the gap for the top pillar — draw a flipped
        # teardrop by rendering on a temp surface and blitting upside down.
        tmp = pygame.Surface((int(fh * 1.6), int(fh * 1.4)), pygame.SRCALPHA)
        _soul_flame(tmp, tmp.get_width() // 2, tmp.get_height() - 2, fh, ss,
                    night=night)
        tmp = pygame.transform.flip(tmp, False, True)
        surf.blit(tmp, (int(cx - tmp.get_width() // 2),
                        int(wick_y - 2)), special_flags=pygame.BLEND_RGBA_MAX)


def _candle_pillar_obstacle(height, ss, *, flip, night=False):
    """One candle-pillar PILLAR obstacle: the dripping wax column fills the post and
    the skull-knob + big flame CAP sits at the GAP-facing edge, flame flourishing
    INTO the gap. `flip=True` is the TOP pillar — its cap is at the BOTTOM edge with
    the flame pointing DOWN into the gap; `flip=False` is the BOTTOM pillar — cap at
    the TOP edge, flame pointing UP into the gap. Both mirror the same wax-drip body
    into a clean vertical candle-pillar lit at the gap (it LIGHTS, never snuffs)."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 16 * ss
    cap_band = int(72 * ss)
    if flip:
        # TOP pillar: column from the title edge down; cap at the bottom (gap) edge,
        # flame pointing DOWN into the gap below.
        _wax_column(surf, cx, 0, bh - cap_band, hw, ss)
        _candle_cap(surf, cx, bh - cap_band, hw, ss, point_up=False, night=night)
    else:
        # BOTTOM pillar: cap at the TOP (gap) edge, flame pointing UP into the gap
        # above; column runs from the cap band down to the ground.
        _wax_column(surf, cx, cap_band, bh, hw, ss)
        _candle_cap(surf, cx, cap_band, hw, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    out = _add_outline(out)
    return out


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


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((30, 36, 34))          # faint green-charcoal so the set reads green
    _label(sheet, font, "PYRECROWN  —  take A5  —  bone + wax-black + GREEN soul-flame  —  round 2", 18, 12)
    _label(sheet, small,
            "the candelabra-skull: a SERENE bone skull crowned with FIVE straight black candle-horns burning green soul-flames; tiny praying cassock",
            18, 32, (190, 210, 198))

    # — Cell A: boss at showcase scale.
    panel = pygame.Rect(18, 56, 360, 580)
    pygame.draw.rect(sheet, (44, 52, 48), panel, border_radius=8)
    pygame.draw.rect(sheet, (84, 104, 92), panel, 2, border_radius=8)
    boss, _ = build_pyrecrown(scale=1.7, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.bottom - boss.get_height() - 16))
    _label(sheet, font, "(a) BOSS  showcase scale", panel.x + 8, panel.y + 8)

    # — Cell B: the candle as a tileable PILLAR pair at TRUE obstacle scale, on the
    #   NIGHT sky (where the green gap-edge flame must earn its keep), + a 2x zoom
    #   re-aimed at the CAP BAND so the skull-knob + flame lighting the gap is proven.
    panelB = pygame.Rect(394, 56, 360, 580)
    bg = _sky(panelB.w, panelB.h, (5, 8, 30), (15, 25, 70), (35, 55, 115), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (84, 104, 92), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 470
    slice_x = panelB.x + 24
    slice_y = panelB.y + 44
    gap_top = 150
    gap_h = 128
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _candle_pillar_obstacle(top_h, 3, flip=True, night=True)
    bot_pillar = _candle_pillar_obstacle(bot_h, 3, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (200, 220, 255), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): wax-drip banding", slice_x - 2, slice_y + slice_h + 6, (200, 225, 255))
    _label(sheet, small, "tiles; green flames RIM-LIGHT the gap", slice_x - 2, slice_y + slice_h + 22, (200, 255, 220))

    # 2x zoom RE-AIMED at the gap CAP band: both skull-knobs + both green flames
    # lighting INTO the gap from each edge, on the night sky behind. This is the
    # payoff the prop must prove.
    cap_band = 72
    zw, zh = pw, 170
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    # Frame the GAP CAP band: the top pillar's bottom cap (flame DOWN) in the upper
    # area, the bottom pillar's top cap (flame UP) in the lower area, with a tight
    # representative gap between — proving BOTH green flames reach INTO the gap. The
    # represented gap is compressed (not the full obstacle gap) so both caps fit.
    top_anchor = 12            # px from zoom top to the top pillar's cap top
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 178
    zy = panelB.y + 96
    # A soft night backing behind the zoom so the green reads LIT (not on panel grey).
    zbg = _sky(zw * 2, zh * 2, (5, 8, 30), (12, 20, 56), (22, 34, 78))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (200, 220, 255), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "skull-knob + green flame", zx - 2, zy + zh * 2 + 6, (200, 255, 220))
    _label(sheet, small, "LIGHT the gap edges", zx - 2, zy + zh * 2 + 22, (200, 255, 220))

    # — Cell C: 1x in-game-scale INSET on BOTH day and night skies + grayscale.
    panelC = pygame.Rect(770, 56, 392, 580)
    pygame.draw.rect(sheet, (44, 52, 48), panelC, border_radius=8)
    pygame.draw.rect(sheet, (84, 104, 92), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) 1x in-game scale  —  day / night legibility", panelC.x + 8, panelC.y + 8)

    boss1x, _ = build_pyrecrown(scale=0.62, ss=3)
    boss1x_n, _ = build_pyrecrown(scale=0.62, ss=3, night=True)
    day = _sky(180, 260, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 260, (5, 8, 30), (15, 25, 70), (35, 55, 115), stars=True)

    dy = panelC.y + 40
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2,
                        dy + 260 - boss1x.get_height() - 6))
    sheet.blit(boss1x_n, (panelC.x + 200 + 90 - boss1x_n.get_width() // 2,
                          dy + 260 - boss1x_n.get_height() - 6))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 30, 26))
    _label(sheet, small, "NIGHT (green pops)", panelC.x + 200 + 6, dy + 6, (200, 255, 220))

    # — Grayscale silhouette check (face + crown must read without the green glow).
    gy = dy + 282
    gray = pygame.Surface((boss1x.get_width(), boss1x.get_height()), pygame.SRCALPHA)
    gray.blit(boss1x, (0, 0))
    arr = pygame.surfarray.pixels3d(gray)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    gpanel = pygame.Rect(panelC.x + 14, gy, 364, 232)
    pygame.draw.rect(sheet, (120, 124, 120), gpanel, border_radius=6)
    sheet.blit(gray, (gpanel.centerx - gray.get_width() // 2,
                      gpanel.bottom - gray.get_height() - 8))
    _label(sheet, small, "grayscale: closed-eye crescents + 5 black tapers carry the read (no green reliance)",
            gpanel.x + 6, gpanel.y + 6, (28, 28, 28))

    # — Footer captions: thesis.
    _label(sheet, small,
           "scary-cute: a SERENE blessing-face skull wearing far too many candles — an over-iced birthday skull; the calm face under the crown is the menace.",
           18, SH - 104, (190, 210, 198))
    _label(sheet, small,
           "house style: FLAT fills, ink keyline grown from alpha, dark-core->fill->sheen triad; flames = FLAT teardrops + OUTSIDE add-glow (contained, not neon/torch).",
           18, SH - 84, (190, 210, 198))
    _label(sheet, small,
           "prop->pillar: the dripping WAX column tiles; the skull-knob + big green flame cap LIGHTS into the gap (not Hollow's snuffer). 5 STRAIGHT candle-horns, no curved horns.",
           18, SH - 64, (190, 210, 198))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "reapy_devil", "pyrecrown")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()

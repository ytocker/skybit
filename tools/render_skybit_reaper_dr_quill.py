"""Look-dev mockup: the Skybit endgame-boss DEATH, take #5 — "DR. QUILL".

WHY: Death as a plague-doctor BIRD — a long-beaked physician reaper, the
sinister cousin of Skybit's player-macaw, here to take your "appointment."
This is the ONE beaked profile in the reaper roster and the only take that
leans on the game's own parrot DNA, so the maturing loop must keep it reading
as the macaw's uncanny cousin, NOT a recolored hero. The separation levers
(per the art-director cull guardrail) are baked in here: a LONG STRAIGHT
downward plague-mask beak (the hero's beak is short + hooked), a wide flat-brim
doctor's hat, two round goggle lenses, and a sickly apothecary palette that
never touches the hero's bright primary red/blue.

House-style spec it obeys (the chibi clown anchor, NOT the prior off-style grim
reaper finish): chibi proportions (big head+beak, short wide weight-shifted
body), FLAT fills + 1-2px hard ink keylines (28,22,30), form via the
dark-core -> light-fill -> top-left rim-sheen TRIAD, bold saturated palette,
silhouette POP via a grown 1px dark outline, playful scary-cute MENACE not grim
realism. Reuses the real game helpers (_shade_c, lerp_color, blit_glow) and
SUPERSAMPLES then smoothscales for crisp edges.

The signature prop is a tall APOTHECARY VIAL-STAFF that must mirror into a
vertical PILLAR pair (the snath->pillar decision ported from the epic reaper):
the banded cane shaft is the pillar BODY (mirrors top<->bottom into a clean
post), and the bulbous vial/ampoule cluster rides the GAP-EDGE as a glowing
flourish — so a tiled pair reads as a vertical post capped by a sickly tincture
vial flourishing INTO the gap.

Nothing under game/ is touched; only the real colour kit + helpers are imported.
Headless + deterministic. Output: docs/skybit_reaper/dr_quill/round_2.png.

    SDL_VIDEODRIVER=dummy python tools/render_skybit_reaper_dr_quill.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, blit_glow, make_gradient_surface
from game.config import PIPE_W

pygame.init()
pygame.font.init()


# ── "bile & wax" palette ──────────────────────────────────────────────────────
# Apothecary-green + waxen-gold + magenta. Deliberately OFF the hero macaw's
# bright primary red/blue so Dr. Quill reads as the sinister cousin, not a
# reskin. All bold + saturated (not the prior grim-reaper's desaturated void).
INK        = (28, 22, 30)            # hard keyline / under-shade

ROBE       = (62, 125, 46)           # apothecary-green robe — the dominant mass
ROBE_DK    = (37, 80, 23)            # dark-core fold
ROBE_HI    = (111, 190, 84)          # top-left rim sheen

# The HEAD + hat carry a DEEPER green than the robe so the figure doesn't read
# as one flat green blob at 1x — a clear head-vs-body value break (directive 3).
HEAD       = (44, 92, 32)            # darker apothecary-green head/hat mass
HEAD_DK    = (24, 56, 16)
HEAD_HI    = (92, 162, 66)

CAPE       = (138, 58, 222)          # violet cape lining (the dramatic flash)
CAPE_DK    = (78, 26, 132)
CAPE_HI    = (196, 138, 255)         # bright rim so the cape survives BOTH skies

WAX        = (232, 194, 74)          # waxen-gold beak + hat brim
WAX_DK     = (176, 137, 42)
WAX_HI     = (255, 228, 154)

GLASS      = (232, 77, 138)          # magenta goggle tincture (the eyes glow)
GLASS_DK   = (150, 38, 88)
GLASS_HI   = (255, 158, 196)
EYE_GLOW   = (255, 120, 175)         # pink pinprick eye behind the lens

TINCTURE   = (182, 255, 74)          # toxic-chartreuse vial glow (prop accent)
TINCTURE_DK = (118, 176, 36)

GLOVE      = (244, 238, 220)         # waxy bone-cream glove + talons
GLOVE_DK   = (188, 178, 150)


# ── sky backdrops (the real biome day + night keyframes) ──────────────────────
DAY_STOPS = [(0.0, (40, 110, 200)), (0.5, (90, 170, 230)), (1.0, (170, 220, 245))]
NIGHT_STOPS = [(0.0, (5, 8, 30)), (0.5, (15, 25, 70)), (1.0, (35, 55, 115))]


def _S(v, ss):
    return int(round(v * ss))


def _poly(surf, col, pts, ss):
    pygame.draw.polygon(surf, col, [(int(p[0]), int(p[1])) for p in pts])


def _triad_circle(surf, col, cx, cy, r, ss):
    """The house dark-core -> fill -> top-left sheen triad on a round mass, so a
    FLAT circle still reads sculpted without any within-shape gradient."""
    pygame.draw.circle(surf, _shade_c(col, -55), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), int(r - ss))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - r * 0.34), int(cy - r * 0.34)),
                       max(1, int(r * 0.34)))


def _add_outline(src, ss, outline_color=(*INK, 235)):
    """Grow a 1px (post-downscale) dark outline around the silhouette so Dr.
    Quill pops on any sky — same idiom as parrot._add_outline, thickness scaled
    so it survives the smoothscale-down."""
    w, h = src.get_size()
    r = max(1, int(round(ss)))
    pad = r + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx == 0 and dy == 0 or max(abs(dx), abs(dy)) > r:
                continue
            out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── the boss ───────────────────────────────────────────────────────────────────

def _draw_vial_cluster(surf, cx, cy, r, ss, *, glow=True):
    """The signature prop's head: a bulbous apothecary VIAL of sickly tincture
    with a waxen-gold stopper + a small ampoule bubble. Shared by the held-staff
    boss and the pillar-pair so the prop->pillar mirror is provably the SAME art.
    Rides the gap-edge as the glowing flourish when tiled into a pillar."""
    # Glow is an OUTSIDE halo ONLY — it must never wash over the bulb interior,
    # or the chartreuse pool stops dominating (the round-1 mis-mask). So the
    # sickly-green bleed reads as light escaping the vial, not as the fluid hue.
    if glow:
        halo = pygame.Surface((int(r * 4), int(r * 4)), pygame.SRCALPHA)
        hc = halo.get_rect().center
        blit_glow(halo, hc[0], hc[1], int(r * 1.9), TINCTURE, alpha=170)
        # Punch the bulb footprint out of the halo so only the OUTSIDE ring shows.
        pygame.draw.circle(halo, (0, 0, 0, 0), hc, int(r * 1.02))
        surf.blit(halo, (int(cx - r * 2), int(cy - r * 2)))
    # Bulb: magenta GLASS body (dark-core + fill), so the glass reads round + flat.
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r + ss))
    pygame.draw.circle(surf, _shade_c(GLASS, -45), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, GLASS, (int(cx), int(cy)), int(r - ss))
    # CHARTREUSE tincture pool: an OPAQUE flat shape clipped to the lower ⅔ of the
    # bulb (no additive glow muddying it), so the two-colour contrast reads
    # "chartreuse fluid inside magenta glass" — the sickly-tincture signature.
    fill = pygame.Surface((int(r * 2.2), int(r * 2.2)), pygame.SRCALPHA)
    fr = fill.get_rect()
    pygame.draw.circle(fill, TINCTURE, (fr.centerx, fr.centerx), int(r - ss))
    cut = pygame.Surface(fill.get_size(), pygame.SRCALPHA)
    cut.fill((255, 255, 255, 255))
    # Erase the TOP third so the pool sits in the lower bulb (a flat meniscus line).
    pygame.draw.rect(cut, (0, 0, 0, 0), (0, 0, fr.w, int(r * 0.78)))
    fill.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(fill, (int(cx - r * 1.1), int(cy - r * 1.1)))
    # Flat meniscus highlight where fluid meets air (sells the liquid surface).
    pygame.draw.line(surf, _shade_c(TINCTURE, 70),
                     (int(cx - r * 0.62), int(cy - r * 0.30)),
                     (int(cx + r * 0.62), int(cy - r * 0.30)), max(1, int(1.4 * ss)))
    # Magenta glass rim sheen (top-left) on the empty upper third — glassy + flat.
    pygame.draw.circle(surf, GLASS_HI,
                       (int(cx - r * 0.36), int(cy - r * 0.46)),
                       max(1, int(r * 0.24)))
    # Two rising bubbles inside the chartreuse pool — the "still cooking" charm.
    pygame.draw.circle(surf, _shade_c(TINCTURE, 80),
                       (int(cx + r * 0.18), int(cy + r * 0.28)), max(1, int(r * 0.15)))
    pygame.draw.circle(surf, _shade_c(TINCTURE, 80),
                       (int(cx - r * 0.22), int(cy + r * 0.50)), max(1, int(r * 0.10)))
    # Waxen-gold stopper neck + cork on top.
    sw = int(r * 0.8)
    neck = pygame.Rect(int(cx - sw / 2), int(cy - r - sw * 0.7), sw, int(sw * 0.9))
    pygame.draw.rect(surf, INK, neck.inflate(int(2 * ss), int(2 * ss)), border_radius=int(2 * ss))
    pygame.draw.rect(surf, WAX, neck, border_radius=int(2 * ss))
    pygame.draw.line(surf, WAX_HI, (neck.left + ss, neck.top + ss),
                     (neck.right - ss, neck.top + ss), max(1, int(ss)))


def _draw_staff(surf, cx, top_y, bot_y, hw, ss, *, with_cluster=True):
    """The tall apothecary CANE/VIAL-STAFF — the prop the boss holds and the body
    the pillar mirrors. A banded waxen-gold cane (the banding = pillar banding)
    with the vial cluster atop. Returns nothing; draws in place."""
    span = bot_y - top_y
    # Cane shaft: dark-core + waxen fill + a top-left highlight stripe (the triad,
    # done on a vertical bar) so the FLAT pole reads cylindrical.
    pygame.draw.rect(surf, INK, (int(cx - hw - ss), int(top_y), int(2 * hw + 2 * ss), int(span)))
    pygame.draw.rect(surf, _shade_c(WAX, -40), (int(cx - hw), int(top_y), int(2 * hw), int(span)))
    pygame.draw.rect(surf, WAX, (int(cx - hw + ss), int(top_y), int(hw), int(span)))
    pygame.draw.line(surf, WAX_HI, (int(cx - hw + ss * 1.5), int(top_y)),
                     (int(cx - hw + ss * 1.5), int(bot_y)), max(1, int(ss)))
    # Grip bands every ~⅛ of the shaft — a tidy banding that becomes the pillar's
    # banding when mirrored.
    n = 7
    for i in range(1, n):
        by = top_y + span * i / n
        pygame.draw.line(surf, INK, (int(cx - hw - ss), int(by)),
                         (int(cx + hw + ss), int(by)), max(2, int(2 * ss)))
        pygame.draw.line(surf, WAX_HI, (int(cx - hw), int(by - ss)),
                         (int(cx + hw), int(by - ss)), max(1, int(ss)))
    if with_cluster:
        _draw_vial_cluster(surf, cx, top_y - hw * 1.4, hw * 2.4, ss)


def build_dr_quill(scale=1.0, ss=3):
    """Dr. Quill, the plague-doctor bird reaper, head-to-talons on his own
    geometry. Everything keys off `H` (hat-brim to talon height) so the chibi
    figure scales as one mass.

    Construction:
      - a wide flat-brim DOCTOR'S HAT disc crowning the figure (instant
        not-a-hood, not-a-macaw read);
      - a big round HEAD with a long STRAIGHT downward plague-mask BEAK jutting
        forward (the silhouette spike no other reaper take owns, and the key
        separator from the hero's short hooked beak);
      - two round goggle LENSES with glowing magenta pinprick eyes — the curious,
        head-tilted "say aaah" charm beat;
      - a short caped apothecary-green ROBE body with a high collar, weight cocked
        to one hip (chibi contrapposto);
      - two bone-cream GLOVE hands (one gripping the vial-staff, one cradling a
        tiny vial), bird-foot TALONS peeking at the hem to seal the bird read;
      - the tall held APOTHECARY VIAL-STAFF (the prop that mirrors to a pillar).
    """
    H = int(300 * scale * ss)
    W = int(150 * scale * ss)
    pad = int(40 * ss)
    surf = pygame.Surface((W + pad * 2, H + pad * 2), pygame.SRCALPHA)
    ox = pad + W // 2          # body centre x
    top = pad                  # hat-brim top y

    # Body proportions (chibi: head+hat ≈ 45% of height, short wide torso).
    head_r = int(H * 0.20)
    head_cx = ox - int(W * 0.06)            # head sits slightly left (head-tilt)
    head_cy = top + int(H * 0.26)
    hip_cx = ox + int(W * 0.05)             # torso cocked to opposite hip
    body_top = head_cy + int(head_r * 0.55)
    feet_y = top + H

    # ── held VIAL-STAFF (drawn FIRST so the body hand overlaps the shaft) ──
    # Pushed further right so the cane + its top vial clear the hat brim's right
    # edge — the round-1 staff crowded the brim and made the disc read lopsided
    # (directive 5). Its top cluster sits below the brim line, not behind it.
    staff_cx = ox + int(W * 0.52)
    _draw_staff(surf, staff_cx, top + int(H * 0.20), feet_y - int(H * 0.02),
                int(W * 0.038), ss)

    # ── CAPE behind the body (the violet flash) — a wide flat fan ──
    cape_pts = [
        (hip_cx - W * 0.30, body_top + head_r * 0.2),
        (hip_cx + W * 0.34, body_top + head_r * 0.2),
        (hip_cx + W * 0.42, feet_y - head_r * 0.2),
        (hip_cx - W * 0.40, feet_y - head_r * 0.2),
    ]
    _poly(surf, CAPE_DK, [(p[0] + ss, p[1]) for p in cape_pts], ss)
    _poly(surf, CAPE, cape_pts, ss)
    # A bright violet RIM stroke along the cape's outer silhouette so the cape
    # carries its own light edge and survives the dark night sky (directive 3) —
    # not just the ink outline, which alone vanishes the cape into night.
    for a, b in (
        (cape_pts[0], cape_pts[3]),     # left outer edge
        (cape_pts[3], cape_pts[2]),     # bottom hem
        (cape_pts[1], cape_pts[2]),     # right outer edge
    ):
        pygame.draw.line(surf, CAPE_HI, (int(a[0]), int(a[1])),
                         (int(b[0]), int(b[1])), max(2, int(2.4 * ss)))
    # Cape top-left sheen panel + a couple of ink fold lines.
    _poly(surf, CAPE_HI, [
        (hip_cx - W * 0.27, body_top + head_r * 0.25),
        (hip_cx - W * 0.10, body_top + head_r * 0.25),
        (hip_cx - W * 0.20, feet_y - head_r * 0.4),
        (hip_cx - W * 0.34, feet_y - head_r * 0.4),
    ], ss)
    for fx in (-0.12, 0.10, 0.26):
        pygame.draw.line(surf, CAPE_DK,
                         (int(hip_cx + W * fx), int(body_top + head_r * 0.3)),
                         (int(hip_cx + W * fx * 1.3), int(feet_y - head_r * 0.3)),
                         max(1, int(1.5 * ss)))

    # ── bird-foot TALONS at the hem (seals the bird read) — thickened + dropped
    # clear of the hem so they hold their own claw shape at 1x instead of melting
    # into the keyline (directive 3). ──
    for s, tx in ((-1, hip_cx - W * 0.13), (1, hip_cx + W * 0.13)):
        base = (int(tx), int(feet_y - head_r * 0.18))
        for spread in (-0.075, 0.0, 0.075):
            tip = (int(tx + spread * W + s * 0.02 * W), int(feet_y + head_r * 0.16))
            pygame.draw.line(surf, INK, base, tip, max(4, int(5.0 * ss)))
            pygame.draw.line(surf, GLOVE, base, tip, max(2, int(2.8 * ss)))
        pygame.draw.circle(surf, INK, base, max(3, int(3.6 * ss)))
        pygame.draw.circle(surf, GLOVE, base, max(2, int(3.0 * ss)))
        pygame.draw.circle(surf, GLOVE_DK, base, max(2, int(3.0 * ss)), max(1, int(ss)))

    # ── ROBE body (short wide bell, weight-shifted) — flat fill + triad ──
    robe_pts = [
        (hip_cx - W * 0.12, body_top),                      # left shoulder
        (hip_cx + W * 0.14, body_top - head_r * 0.10),      # right shoulder (raised)
        (hip_cx + W * 0.26, feet_y - head_r * 0.20),        # right hem flare
        (hip_cx - W * 0.24, feet_y - head_r * 0.20),        # left hem flare
    ]
    _poly(surf, ROBE_DK, [(p[0] + ss, p[1] + ss) for p in robe_pts], ss)
    _poly(surf, ROBE, robe_pts, ss)
    # Top-left rim sheen panel on the robe (the triad's third tone).
    _poly(surf, ROBE_HI, [
        (hip_cx - W * 0.10, body_top + head_r * 0.05),
        (hip_cx + W * 0.0, body_top + head_r * 0.0),
        (hip_cx - W * 0.06, feet_y - head_r * 0.45),
        (hip_cx - W * 0.20, feet_y - head_r * 0.40),
    ], ss)
    # A central robe button-placket + two waxen toggle buttons (clinical tidy).
    pygame.draw.line(surf, ROBE_DK, (int(hip_cx + W * 0.02), int(body_top)),
                     (int(hip_cx + W * 0.0), int(feet_y - head_r * 0.3)),
                     max(2, int(2 * ss)))
    for bt in (0.30, 0.55):
        pygame.draw.circle(surf, WAX, (int(hip_cx + W * 0.02),
                                       int(body_top + (feet_y - body_top) * bt)),
                           max(2, int(2.6 * ss)))
        pygame.draw.circle(surf, INK, (int(hip_cx + W * 0.02),
                                       int(body_top + (feet_y - body_top) * bt)),
                           max(2, int(2.6 * ss)), max(1, int(ss)))

    # ── high collar (a flat waxen wing-collar tucked under the head) ──
    collar = [
        (head_cx - head_r * 0.8, body_top + head_r * 0.05),
        (head_cx + head_r * 0.85, body_top - head_r * 0.05),
        (head_cx + head_r * 0.45, body_top + head_r * 0.55),
        (head_cx - head_r * 0.45, body_top + head_r * 0.60),
    ]
    _poly(surf, WAX_DK, [(p[0], p[1] + ss) for p in collar], ss)
    _poly(surf, WAX, collar, ss)
    pygame.draw.line(surf, WAX_HI,
                     (int(head_cx - head_r * 0.7), int(body_top + head_r * 0.1)),
                     (int(head_cx + head_r * 0.75), int(body_top - head_r * 0.02)),
                     max(1, int(ss)))

    # ── HEAD (round, the DEEPER apothecary-green so it breaks from the robe) ──
    _triad_circle(surf, HEAD, head_cx, head_cy, head_r, ss)

    # ── long STRAIGHT plague-mask BEAK (THE read; juts forward, near-horizontal) ──
    # A LONG straight tapered cone (~2.0x head_r), base at the CENTER of the face,
    # only a subtle downward tip — the macaw's beak is short + hooked, so this
    # straight spike is the whole identity + the key hero separator. Drawn here
    # AFTER the head fill but BEFORE the goggles, so the lenses sit on top and the
    # beak base reads as exiting from between/below them at face center.
    beak_len = head_r * 2.05
    beak_base_top = (head_cx + head_r * 0.06, head_cy - head_r * 0.16)
    beak_base_bot = (head_cx + head_r * 0.10, head_cy + head_r * 0.30)
    beak_tip = (head_cx + beak_len, head_cy + head_r * 0.22)   # near-horizontal
    beak = [beak_base_top, beak_tip, beak_base_bot]
    _poly(surf, WAX_DK, [(p[0], p[1] + ss) for p in beak], ss)
    _poly(surf, WAX, beak, ss)
    # Top ridge sheen runs the full length so the straight spike reads as one
    # crisp dorsal line (the silhouette gesture).
    pygame.draw.line(surf, WAX_HI, (int(beak_base_top[0]), int(beak_base_top[1] + ss * 1.5)),
                     (int(beak_tip[0] - head_r * 0.1), int(beak_tip[1] - head_r * 0.04)),
                     max(2, int(2 * ss)))
    # Breathing-slit notches near the tip (the plague-mask filter detail).
    for sn in (0.55, 0.68):
        sx = beak_base_top[0] + (beak_tip[0] - beak_base_top[0]) * sn
        sy = beak_base_top[1] + (beak_tip[1] - beak_base_top[1]) * sn + head_r * 0.06
        pygame.draw.line(surf, INK, (int(sx), int(sy)),
                         (int(sx + head_r * 0.05), int(sy + head_r * 0.12)),
                         max(1, int(1.4 * ss)))
    # Bottom + top keylines so the long straight spike holds a hard silhouette.
    pygame.draw.line(surf, INK, (int(beak_base_bot[0]), int(beak_base_bot[1])),
                     (int(beak_tip[0]), int(beak_tip[1])), max(2, int(2.2 * ss)))
    pygame.draw.line(surf, INK, (int(beak_base_top[0]), int(beak_base_top[1])),
                     (int(beak_tip[0]), int(beak_tip[1])), max(1, int(1.6 * ss)))

    # ── two round goggle LENSES with glowing magenta pinprick eyes ──
    for s, lx in ((-1, head_cx - head_r * 0.42), (1, head_cx + head_r * 0.30)):
        ly = head_cy - head_r * 0.18
        lr = head_r * 0.40
        # Glow bleed behind the lens so the pink eye reads as lit-from-within.
        blit_glow(surf, int(lx), int(ly), int(lr * 1.5), GLASS, alpha=120)
        # Waxen-gold rim + dark glass + magenta tincture + a top-left glass sheen.
        pygame.draw.circle(surf, WAX, (int(lx), int(ly)), int(lr + 2 * ss))
        pygame.draw.circle(surf, INK, (int(lx), int(ly)), int(lr + ss))
        pygame.draw.circle(surf, GLASS_DK, (int(lx), int(ly)), int(lr))
        pygame.draw.circle(surf, GLASS, (int(lx), int(ly)), int(lr * 0.78))
        # Glowing pink pinprick pupil — the curious bird "eye" (looks toward beak).
        pygame.draw.circle(surf, EYE_GLOW,
                           (int(lx + lr * 0.25), int(ly + lr * 0.10)),
                           max(2, int(lr * 0.30)))
        pygame.draw.circle(surf, (255, 255, 255),
                           (int(lx + lr * 0.05), int(ly - lr * 0.20)),
                           max(1, int(lr * 0.16)))
        # Lens glint (top-left), the glassy flat sheen.
        pygame.draw.circle(surf, GLASS_HI,
                           (int(lx - lr * 0.34), int(ly - lr * 0.38)),
                           max(1, int(lr * 0.22)))

    # ── wide flat-brim DOCTOR'S HAT (crown disc + brim ellipse) ──
    brim_cy = head_cy - head_r * 0.78
    brim_w = head_r * 1.85
    brim_h = head_r * 0.46
    brim_rect = pygame.Rect(int(head_cx - brim_w), int(brim_cy - brim_h / 2),
                            int(brim_w * 2), int(brim_h))
    pygame.draw.ellipse(surf, INK, brim_rect.inflate(int(2 * ss), int(2 * ss)))
    pygame.draw.ellipse(surf, HEAD_DK, brim_rect)
    pygame.draw.ellipse(surf, HEAD, brim_rect.inflate(int(-2 * ss), int(-2 * ss)))
    # A waxen-gold under-brim rim line breaks the brim off the head value-wise.
    pygame.draw.ellipse(surf, WAX_DK, brim_rect.inflate(int(-2 * ss), int(-2 * ss)),
                        max(1, int(ss)))
    # Brim top-left sheen crescent.
    sheen = pygame.Rect(int(head_cx - brim_w * 0.8), int(brim_cy - brim_h / 2),
                        int(brim_w * 0.9), int(brim_h * 0.5))
    pygame.draw.ellipse(surf, HEAD_HI, sheen)
    # Low rounded crown + a waxen hatband (clinical apothecary touch).
    crown_w = head_r * 1.05
    crown_h = head_r * 0.78
    crown_rect = pygame.Rect(int(head_cx - crown_w / 2),
                             int(brim_cy - crown_h), int(crown_w), int(crown_h * 1.05))
    pygame.draw.ellipse(surf, HEAD_DK, crown_rect)
    pygame.draw.ellipse(surf, HEAD, crown_rect.inflate(int(-2 * ss), int(-2 * ss)))
    pygame.draw.ellipse(surf, HEAD_HI,
                        pygame.Rect(int(head_cx - crown_w * 0.34),
                                    int(brim_cy - crown_h * 0.92),
                                    int(crown_w * 0.4), int(crown_h * 0.4)))
    band = pygame.Rect(int(head_cx - crown_w / 2), int(brim_cy - crown_h * 0.34),
                       int(crown_w), int(crown_h * 0.26))
    pygame.draw.ellipse(surf, WAX_DK, band)
    pygame.draw.ellipse(surf, WAX, band.inflate(0, int(-2 * ss)))
    pygame.draw.ellipse(surf, WAX_HI,
                        pygame.Rect(band.left + int(crown_w * 0.12), band.top + ss,
                                    int(crown_w * 0.3), max(1, int(2 * ss))))

    # ── GLOVE hands: one gripping the staff, one cradling a tiny vial ──
    # Grip hand on the staff (right).
    grip = (int(staff_cx - W * 0.02), int(top + H * 0.42))
    pygame.draw.circle(surf, INK, grip, max(3, int(W * 0.05 + ss)))
    pygame.draw.circle(surf, GLOVE, grip, int(W * 0.05))
    pygame.draw.circle(surf, GLOVE_DK, grip, int(W * 0.05), max(1, int(ss)))
    # Cradle hand (left) holding a tiny chartreuse vial — the "your prescription"
    # charm beat.
    cradle = (int(hip_cx - W * 0.22), int(body_top + head_r * 0.55))
    pygame.draw.circle(surf, INK, cradle, max(3, int(W * 0.052 + ss)))
    pygame.draw.circle(surf, GLOVE, cradle, int(W * 0.052))
    pygame.draw.circle(surf, GLOVE_DK, cradle, int(W * 0.052), max(1, int(ss)))
    # tiny vial in the cradle hand — same colour stack as the big bulb: an
    # OUTSIDE-only chartreuse halo, magenta-glass body, then an opaque chartreuse
    # pool in the lower half (no inside glow), so even at this size it reads as
    # green fluid in pink glass.
    tv = pygame.Rect(int(cradle[0] - W * 0.020), int(cradle[1] - W * 0.10),
                     int(W * 0.040), int(W * 0.12))
    halo = pygame.Surface((int(W * 0.22), int(W * 0.22)), pygame.SRCALPHA)
    hc = halo.get_rect().center
    blit_glow(halo, hc[0], hc[1], int(W * 0.07), TINCTURE, alpha=140)
    pygame.draw.rect(halo, (0, 0, 0, 0),
                     (hc[0] - tv.w // 2 - int(ss), hc[1] - tv.h // 2 - int(ss),
                      tv.w + int(2 * ss), tv.h + int(2 * ss)))
    surf.blit(halo, (tv.centerx - int(W * 0.11), tv.centery - int(W * 0.11)))
    pygame.draw.rect(surf, INK, tv.inflate(int(2 * ss), int(2 * ss)), border_radius=int(2 * ss))
    pygame.draw.rect(surf, GLASS, tv, border_radius=int(2 * ss))
    pygame.draw.rect(surf, TINCTURE, (tv.x, tv.y + tv.h // 2, tv.w, tv.h // 2),
                     border_radius=int(ss))
    pygame.draw.rect(surf, WAX, (tv.x, tv.y - int(2 * ss), tv.w, int(3 * ss)),
                     border_radius=int(ss))

    return _add_outline(surf, ss)


# ── pillar pair (prop -> pillar mirror) ─────────────────────────────────────────

def build_pillar_pair(gap_h, col_h, ss=3):
    """Prove the prop->pillar mirror: the vial-STAFF tiled as a top + bottom
    sandstone-column pair with the apothecary gap mouth between them. The cane
    shaft IS the pillar body (mirrors top<->bottom into a clean banded post); the
    vial cluster rides the GAP-EDGE as the glowing flourish. Returns (top, bottom)
    surfaces sized like the in-game PIPE_W column."""
    overhang = int(14 * ss)
    bw = PIPE_W * ss + overhang * 2
    cx = bw // 2
    hw = int(PIPE_W * 0.30 * ss)

    def _column(height, flip):
        s = pygame.Surface((bw, int(height)), pygame.SRCALPHA)
        # Mirror so the vial flourish always sits at the GAP edge: for the top
        # column the flourish is at the bottom; for the bottom column, the top.
        gap_y = height - int(8 * ss) if not flip else int(8 * ss)
        far_y = int(8 * ss) if not flip else height - int(8 * ss)
        # The shaft is APOTHECARY-GREEN (the robe's green), NOT the waxen gold —
        # gold reads too close to the sandstone pillars it sits beside, so the
        # green post + gold banding clearly separates "Dr. Quill's cane" from an
        # ordinary pillar (directive 4). Banding stays gold for the cane read.
        top_y, bot_y = sorted((gap_y, far_y))
        pygame.draw.rect(s, INK, (cx - hw - ss, top_y, 2 * hw + 2 * ss, bot_y - top_y))
        pygame.draw.rect(s, ROBE_DK, (cx - hw, top_y, 2 * hw, bot_y - top_y))
        pygame.draw.rect(s, ROBE, (cx - hw + ss, top_y, hw, bot_y - top_y))
        pygame.draw.line(s, ROBE_HI, (cx - hw + int(ss * 1.5), top_y),
                         (cx - hw + int(ss * 1.5), bot_y), max(1, int(ss)))
        # Waxen-gold grip banding along the green post.
        span = bot_y - top_y
        n = max(4, int(span / (22 * ss)))
        for i in range(1, n):
            by = top_y + span * i / n
            pygame.draw.line(s, INK, (cx - hw - ss, int(by)),
                             (cx + hw + ss, int(by)), max(3, int(3 * ss)))
            pygame.draw.line(s, WAX, (cx - hw, int(by - ss * 0.5)),
                             (cx + hw, int(by - ss * 0.5)), max(2, int(2 * ss)))
            pygame.draw.line(s, WAX_HI, (cx - hw, int(by - ss * 1.2)),
                             (cx + hw, int(by - ss * 1.2)), max(1, int(ss)))
        # A gold COLLAR ferrule + value break between the green shaft and the gap
        # flourish, so the vial pops off the post as a distinct prop, not debris.
        coll_y = gap_y - int((1 if not flip else -1) * PIPE_W * 0.42 * ss)
        ferr = pygame.Rect(int(cx - hw * 1.5), int(min(coll_y, gap_y)),
                           int(hw * 3), int(abs(gap_y - coll_y)))
        if ferr.height > ss:
            pygame.draw.rect(s, INK, ferr.inflate(int(2 * ss), 0))
            pygame.draw.rect(s, WAX, ferr.inflate(int(-2 * ss), int(-2 * ss)))
        # Push a sickly-green glow burst at the GAP MOUTH — the signature read
        # (the prop glowing INTO the gap). Drawn before the vial so the vial sits
        # crisp on top of its own halo.
        burst = pygame.Surface((int(hw * 8), int(hw * 8)), pygame.SRCALPHA)
        bc = burst.get_rect().center
        blit_glow(burst, bc[0], bc[1], int(hw * 2.6), TINCTURE, alpha=130)
        s.blit(burst, (int(cx - hw * 4), int(gap_y - hw * 4)))
        # The vial cluster flourish AT the gap edge (its own glow is outside-only).
        _draw_vial_cluster(s, cx, gap_y, int(PIPE_W * 0.42 * ss), ss)
        return s

    top = _column(col_h, flip=False)
    bot = _column(col_h, flip=True)
    return top, bot


# ── sheet assembly ──────────────────────────────────────────────────────────────

def _label(surf, text, x, y, size=20, col=(245, 240, 230)):
    font = pygame.font.SysFont("dejavusans", size, bold=True)
    sh = font.render(text, True, (12, 10, 16))
    tx = font.render(text, True, col)
    surf.blit(sh, (x + 1, y + 1))
    surf.blit(tx, (x, y))


def _downscale(src, factor):
    w, h = src.get_size()
    return pygame.transform.smoothscale(src, (w // factor, h // factor))


def main():
    ss = 3
    SHEET_W, SHEET_H = 1180, 900
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((40, 36, 48))

    # ── cell A: boss at showcase scale ──
    boss_ss = build_dr_quill(scale=1.0, ss=ss)
    boss = _downscale(boss_ss, ss)
    # neutral apothecary-dark panel behind the showcase boss
    pygame.draw.rect(sheet, (26, 30, 24), (20, 50, 420, 820))
    pygame.draw.rect(sheet, (70, 110, 60), (20, 50, 420, 820), 2)
    br = boss.get_rect(center=(230, 470))
    sheet.blit(boss, br.topleft)
    _label(sheet, "A — DR. QUILL boss (showcase scale)", 30, 22)
    _label(sheet, "plague-doctor BIRD: long straight beak,", 30, 815, size=15,
           col=(190, 230, 170))
    _label(sheet, "brim hat, goggle eyes — macaw's cousin", 30, 835, size=15,
           col=(190, 230, 170))

    # ── cell B: prop -> pillar pair ──
    gap_h = 150
    col_h = 320 * ss
    top_col, bot_col = build_pillar_pair(gap_h, col_h, ss=ss)
    top_col = _downscale(top_col, ss)
    bot_col = _downscale(bot_col, ss)
    pygame.draw.rect(sheet, (24, 22, 30), (470, 50, 320, 820))
    pygame.draw.rect(sheet, (70, 110, 60), (470, 50, 320, 820), 2)
    _label(sheet, "B — vial-staff -> PILLAR pair", 480, 22)
    pcx = 630
    sheet.blit(top_col, top_col.get_rect(midtop=(pcx, 80)).topleft)
    sheet.blit(bot_col, bot_col.get_rect(midbottom=(pcx, 860)).topleft)
    _label(sheet, "shaft = post (mirrors),", 480, 815, size=15, col=(255, 220, 150))
    _label(sheet, "vial cluster rides the gap edge", 480, 835, size=15,
           col=(190, 255, 120))

    # ── cells C/D: 1x in-game-scale insets on day + night skies ──
    # 1x in-game boss: build small + downscale to a true gameplay footprint.
    boss_1x_ss = build_dr_quill(scale=0.34, ss=ss)
    boss_1x = _downscale(boss_1x_ss, ss)

    inset_w, inset_h = 350, 400
    day_sky = make_gradient_surface(inset_w, inset_h, DAY_STOPS)
    night_sky = make_gradient_surface(inset_w, inset_h, NIGHT_STOPS)
    # a few night stars so the night panel reads as the real biome night
    for sx, sy in ((40, 60), (120, 30), (210, 90), (300, 50),
                   (80, 140), (260, 160), (180, 50), (330, 120)):
        pygame.draw.circle(night_sky, (220, 230, 255), (sx, sy), 1)

    for sky, label, oy in ((day_sky, "C — 1x in-game inset (DAY sky)", 50),
                           (night_sky, "D — 1x in-game inset (NIGHT sky)", 460)):
        panel = pygame.Surface((inset_w, inset_h))
        panel.blit(sky, (0, 0))
        # one vial-pillar pair flanking the gap, boss flying through
        ptop, pbot = build_pillar_pair(gap_h, 150 * ss, ss=ss)
        ptop = _downscale(ptop, ss)
        pbot = _downscale(pbot, ss)
        pgx = 250
        panel.blit(ptop, ptop.get_rect(midtop=(pgx, -8)).topleft)
        panel.blit(pbot, pbot.get_rect(midbottom=(pgx, inset_h + 8)).topleft)
        panel.blit(boss_1x, boss_1x.get_rect(center=(120, inset_h // 2)).topleft)
        sheet.blit(panel, (810, oy + 30))
        pygame.draw.rect(sheet, (70, 110, 60), (810, oy + 30, inset_w, inset_h), 2)
        _label(sheet, label, 810, oy + 6)

    out_dir = os.path.join(os.path.dirname(__file__), os.pardir,
                           "docs", "skybit_reaper", "dr_quill")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()

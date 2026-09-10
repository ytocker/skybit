"""Look-dev sheet for the Skybit BOSS batch-2 LEYAK-EPIC set — concept #1 "KRASUE".

SE-Asian Krasue / penanggalan re-cuted as a sleepy floating SKULL-LANTERN that
dangles its own viscera as a vertical STRING of glowing marsh gut-orbs — the
orb-string IS the pillar. Distinct from the shipped Leyak (ash face + hot-pink
viscera-RIBBON): here the body runs COOL dusk-mauve and the only warm hue is
firefly-gold contained STRICTLY inside 5-6 discrete gut-orbs (body cool / glow
warm). The repeatable pillar body is the evenly-beaded orb-string on a thin
sinew; the gap-edge cap is the creature's OWN form — a single cracked bottom
lantern-orb radiating into the gap.

House style this obeys (warren-clown / Big-Reapy / Leyak grammar), ELEVATED:
  - CHIBI proportions — one oversized floating head, no torso/limbs; the
    orb-string is the body.
  - FLAT saturated fills + hard 1-2px ink keyline (28,22,30). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC: render LARGE at SS=6, then smoothscale down — crisp at downscale.
    More geometry (membrane veining, inner orb glow-lobes, thin sinew), richer
    triad, stronger make_glow_surface glow than the source.

Accessibility tell: the warm gut-orb STRING shape + cool head vs warm-orb
contrast carry the read independent of hue.

Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/leyak_epic/krasue/render_krasue.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (leyak-epic krasue) — hex-exact from the locked brief ─────
# Body runs COOL dusk-mauve; the ONLY warm hue is firefly-gold contained inside
# the gut-orbs. Body cool / glow warm opens a clean lane vs shipped Ifra's coral
# body and Leyak's hot-pink trail.
BODY        = (150, 128, 150)   # cool dusk-mauve face / skull fill
BODY_DK     = (96, 78, 104)     # deep mauve shade (dark-core ring / hollows)
BODY_SHEEN  = (214, 200, 220)   # lilac top-left rim sheen

SINEW       = (118, 96, 120)    # the thin mauve thread the orbs string onto
SINEW_DK    = (78, 62, 86)

# Firefly-gold — ONLY ever inside the discrete gut-orbs. Never on flesh.
# Value/saturation pushed ~15-20% over round 1 so the beads survive the chip
# and don't wash into a dark-blue night sky (critique priority 2).
ORB         = (255, 214, 96)    # firefly-gold orb fill (richer / less pastel)
ORB_DK      = (182, 128, 48)    # amber orb shade (dark-core / cracks)
ORB_SHEEN   = (255, 244, 198)   # pale-gold rim sheen
ORB_CORE    = (255, 252, 236)   # the will-o'-the-wisp inner core twinkle
ORB_INK     = (74, 50, 14)      # near-ink amber keyline around each bead

INK         = (28, 22, 30)      # the house keyline (epic-set ink)

# Tooth/jaw reuse a bone-pale cool family so the grin reads skull, not gold.
BONE        = (224, 214, 222)
BONE_DK     = (150, 138, 150)


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_d=34):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Sculpted volume while staying flat-shaded."""
    pygame.draw.circle(surf, _shade_c(col, -46), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.055))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, sheen_d),
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.34)))


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot _add_outline recipe). Returns a padded surface."""
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


# ── one glowing gut-orb (warm-gold triad sphere; glow strictly inside) ───────

def _gut_orb(surf, cx, cy, r, ss, *, night=False, cracked=False, glow=True):
    """A single luminous marsh gut-LANTERN, built so it survives the 32px chip
    (critique priority 2 + directive 4). Three-zone lantern, not a flat disc:
      - a contained warm bloom halo (the ONLY warm glow, bounded to the orb);
      - a 1px amber-ink keyline so beads stay discrete and don't smear into one
        blob or wash into the night sky;
      - a warm-gold core glow-LOBE offset down-RIGHT (like a flame settling in a
        lantern), a mid gold fill, and a small COOL lilac rim-sheen pip top-left.
    `cracked` scores the bottom lantern-orb's own-form fracture as a crisp ink
    line with a lilac-sheen lip so it reads as cracked ceramic, not a smudge."""
    if glow:
        # Stronger, localized warm bloom — but bounded to the bead so the body
        # stays cool (critique: warm reads as a contained firefly, never a wash).
        gr = int(r * (2.2 if night else 1.7))
        gl = make_glow_surface(gr, ORB, alpha_center=235 if night else 150,
                               falloff=2.0)
        surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)

    # Amber-ink keyline ring first — keeps each bead a discrete, gapped shape.
    pygame.draw.circle(surf, ORB_INK, (int(cx), int(cy)), max(2, int(r + ss)))
    # Warm-gold body (dark amber ring -> flat fill).
    pygame.draw.circle(surf, ORB_DK, (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, ORB, (int(cx), int(cy)), max(1, int(r * 0.86)))
    # Inner glow-LOBE — a brighter disc offset DOWN-RIGHT, the flame settling in
    # the lantern (directive 4). Larger than r1's so it carries at the chip.
    pygame.draw.circle(surf, ORB_SHEEN,
                       (int(cx + r * 0.16), int(cy + r * 0.20)),
                       max(1, int(r * 0.52)))
    # Will-o'-the-wisp core twinkle, biased into the lobe.
    pygame.draw.circle(surf, ORB_CORE,
                       (int(cx + r * 0.14), int(cy + r * 0.18)),
                       max(1, int(r * 0.24)))
    if cracked:
        # A crisp 1px ink fracture branching across the membrane — the OWN-form
        # tell that this end-orb is the cracked bottom lantern, with a thin
        # lilac-sheen lip on the upper edge so it reads as cracked ceramic.
        cw = max(1, int(0.8 * ss))
        a = (cx - r * 0.58, cy - r * 0.34)
        b = (cx - r * 0.04, cy + r * 0.02)
        c = (cx + r * 0.42, cy - r * 0.44)
        d = (cx + r * 0.22, cy + r * 0.52)
        lip = (int(cw * 0.6), -int(cw * 0.6))
        pygame.draw.lines(surf, BODY_SHEEN, False,
                          [(int(x + lip[0]), int(y + lip[1]))
                           for x, y in (a, b, c)], max(1, int(cw * 0.5)))
        pygame.draw.lines(surf, INK, False,
                          [(int(x), int(y)) for x, y in (a, b, c)], cw)
        pygame.draw.lines(surf, INK, False,
                          [(int(x), int(y)) for x, y in (b, d)], cw)
    # Cool lilac rim-sheen pip top-left — the only cool pip on the warm bead;
    # reinforces warm-in-orb / cool-body and keeps the triad honest.
    pygame.draw.circle(surf, BODY_SHEEN,
                       (int(cx - r * 0.40), int(cy - r * 0.42)),
                       max(1, int(r * 0.18)))


# ── the orb-string (creature viscera + the pillar body) ──────────────────────

def _orb_string(surf, top_x, top_y, length, base_r, ss, *, n_orbs, wave=0.0,
                phase=0.0, end_cracked=False, night=False):
    """The viscera orb-STRING streaming straight DOWN: a thin mauve SINEW thread
    strung with evenly-spaced glowing gut-orbs at a steady cadence (the band that
    TILES top<->bottom for the pillar). `end_cracked` makes the bottom orb the
    cracked lantern-orb gap cap. Orbs shrink gently down the string for depth."""
    def _x_at(t):
        return top_x + wave * base_r * math.sin(t * math.pi * 2.2 + phase) \
            * (0.30 + 0.70 * t)

    # The sinew thread first, so the orbs sit ON it. A visible INK cord with a
    # mauve underside, drawn thick enough to survive the chip as the connective
    # tissue that strings the beads into ONE gut-line (directive 3).
    pts = []
    steps = 36
    for i in range(steps + 1):
        t = i / steps
        pts.append((_x_at(t), top_y + length * t))
    ipts = [(int(x), int(y)) for x, y in pts]
    upts = [(int(x + 1.0 * ss), int(y)) for x, y in pts]   # mauve underside
    pygame.draw.lines(surf, INK, False, ipts, max(2, int(3.4 * ss)))
    pygame.draw.lines(surf, SINEW_DK, False, upts, max(1, int(1.6 * ss)))
    pygame.draw.lines(surf, SINEW, False, ipts, max(1, int(1.4 * ss)))

    # Evenly-spaced gut-orbs threaded on the sinew (the repeatable organ band).
    # Bigger, fewer beads at a clean cadence so each survives downscale.
    for i in range(n_orbs):
        t = (i + 0.5) / n_orbs
        x = _x_at(t)
        y = top_y + length * t
        r = base_r * (1.0 - 0.18 * t)
        cracked = end_cracked and (i == n_orbs - 1)
        _gut_orb(surf, x, y, r, ss, night=night, cracked=cracked)


# ── the floating skull-lantern head ──────────────────────────────────────────

def _head(surf, cx, cy, r, ss, *, night=False):
    """The oversized floating skull-LANTERN head: a round cool dusk-mauve skull
    with soft membrane veining, big sleepy half-lidded eyes glowing a contained
    gold (the lantern within), a small skull nose-hole, and a gentle bone tusk-
    grin. Scary-CUTE — drowsy, not menacing. `night` lifts the cool body value so
    the head stays a clean LIGHT-mauve blob against dark-blue night biomes."""
    # Night lifts the cool body so it stays a light blob on dark sky; DAY instead
    # cools+darkens the base ~1 value step (a touch more blue, a touch less value)
    # so the ink lids + grille hold contrast against the bright-blue day sky and
    # the head reads lantern-skull, not a pale blob (critique priority 2). The
    # night/dusk balance is untouched.
    if night:
        body = _shade_c(BODY, 14)
        body_sheen = _shade_c(BODY_SHEEN, 8)
    else:
        body = _shade_c((BODY[0] - 10, BODY[1] - 12, BODY[2] + 2), -14)
        body_sheen = BODY_SHEEN

    # Cranium dome (cool mauve) — slightly squashed wide for a lantern/gourd read.
    _triad_circle(surf, cx, cy, r, body)
    # Lower-cheek bulge so it reads as a head, not a perfect ball.
    cheek = pygame.Rect(0, 0, int(r * 1.84), int(r * 1.48))
    cheek.center = (int(cx), int(cy + r * 0.30))
    pygame.draw.ellipse(surf, _shade_c(body, -46), cheek)
    inner = cheek.inflate(-int(r * 0.14), -int(r * 0.14))
    pygame.draw.ellipse(surf, body, inner)
    _triad_circle(surf, cx, cy, r, body)       # re-seat the dome over the cheek
    # Bright cranium-top sheen cap so the crown catches light on night skies.
    pygame.draw.circle(surf, body_sheen,
                       (int(cx - r * 0.30), int(cy - r * 0.42)),
                       max(2, int(r * 0.30)))

    # Faint membrane veining on the head (elevated detail) — a few thin
    # dark-mauve hairlines fanning from the crown, NOT gore-realistic.
    vein = _shade_c(body, -34)
    for k in (-0.6, -0.2, 0.25, 0.62):
        a0 = math.pi * (0.5 + 0.42 * k)
        x0 = cx + math.cos(a0) * r * 0.30
        y0 = cy - r * 0.10 + math.sin(a0) * r * 0.20
        x1 = cx + math.cos(a0) * r * 0.86
        y1 = cy - r * 0.04 + math.sin(a0) * r * 0.62
        xm = (x0 + x1) * 0.5 + k * r * 0.10
        ym = (y0 + y1) * 0.5
        pygame.draw.lines(surf, vein, False,
                          [(int(x0), int(y0)), (int(xm), int(ym)),
                           (int(x1), int(y1))], max(1, int(0.8 * ss)))

    # — A single cracked-BROW ridge above the eyes — the secondary focal tell
    #   (directive 6) that breaks the bilateral symmetry and screams lantern-
    #   skull, not generic lich. A dark mauve brow bar with a hairline ink crack.
    brow_y = cy - r * 0.30
    brow = pygame.Rect(int(cx - r * 0.82), int(brow_y - r * 0.10),
                       int(r * 1.64), int(r * 0.22))
    pygame.draw.ellipse(surf, _shade_c(body, -40), brow)
    pygame.draw.lines(surf, INK, False,
                      [(int(cx - r * 0.18), int(brow_y - r * 0.12)),
                       (int(cx - r * 0.02), int(brow_y + r * 0.02)),
                       (int(cx + r * 0.14), int(brow_y - r * 0.08)),
                       (int(cx + r * 0.10), int(brow_y + r * 0.12))],
                      max(1, int(1.0 * ss)))

    # — Eyes: big SLEEPY heavy-lidded sockets glowing a contained gold (the
    #   lantern inside the skull). The sleepy read is now carried by the SHAPE
    #   of the socket itself: a WIDE SHORT slot (wider than tall) under a HEAVY
    #   ink lid that covers the top ~58% — so the eye reads as a low crescent
    #   smile-curve of glow, not a tall startled oval (critique priority 1).
    eye_dx = r * 0.46
    eye_dy = r * 0.06
    eye_hw = r * 0.50          # socket is WIDE…
    eye_hh = r * 0.30          # …and SHORT — wider than tall = drowsy slot
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        # Deep-mauve socket recess as a WIDE SHORT ellipse + a 1px ink rim, so
        # the resting socket shape already reads heavy-lidded, not round.
        sock = pygame.Rect(0, 0, int(eye_hw * 2.20), int(eye_hh * 2.20))
        sock.center = (int(ex), int(ey))
        pygame.draw.ellipse(surf, INK, sock)
        sock_i = pygame.Rect(0, 0, int(eye_hw * 2.0), int(eye_hh * 2.0))
        sock_i.center = (int(ex), int(ey))
        pygame.draw.ellipse(surf, BODY_DK, sock_i)
        # Contained gold glow within the socket (warm only inside the eye),
        # biased LOW so the bloom sits in the crescent under the lid.
        gl = make_glow_surface(int(eye_hw * 1.3), ORB,
                               alpha_center=170 if night else 120, falloff=2.1)
        surf.blit(gl, (int(ex - eye_hw * 1.3),
                       int(ey + eye_hh * 0.30 - eye_hw * 1.3)),
                  special_flags=pygame.BLEND_ADD)
        # The gold itself is a WIDE LOW crescent-ellipse pooled at the bottom of
        # the socket — a thin smile-curve of light, wider than it is tall.
        gold = pygame.Rect(0, 0, int(eye_hw * 1.80), int(eye_hh * 1.30))
        gold.center = (int(ex), int(ey + eye_hh * 0.40))
        pygame.draw.ellipse(surf, ORB_DK, gold)
        gold_i = gold.inflate(-int(eye_hw * 0.30), -int(eye_hh * 0.30))
        pygame.draw.ellipse(surf, ORB, gold_i)
        pygame.draw.circle(surf, ORB_CORE,
                           (int(ex + eye_hw * 0.10), int(ey + eye_hh * 0.55)),
                           max(1, int(eye_hh * 0.30)))
        # HEAVY INK upper-lid covering the top ~58% of the socket — the dominant
        # SHAPE. A wide ellipse-segment in INK (never flesh) drooping low so the
        # only gold left is a thin low crescent (the half-closed sleepy beat).
        lw, lh = int(eye_hw * 2.6), int(eye_hh * 2.8)
        lid = pygame.Surface((lw, lh), pygame.SRCALPHA)
        pygame.draw.ellipse(lid, INK,
                            pygame.Rect(0, 0, lw, int(eye_hh * 2.5)))
        # Cut the lower portion so the heavy lid covers ~58% of the slot.
        lid.fill((0, 0, 0, 0),
                 pygame.Rect(0, int(eye_hh * 1.28), lw, lh))
        surf.blit(lid, (int(ex - lw / 2),
                        int(ey - eye_hh * 1.10)))
        # A thin lilac sheen lip riding the lid's lower edge — a sleepy lash
        # highlight that keeps the heavy-lid crescent crisp + cute.
        pygame.draw.line(surf, body_sheen,
                         (int(ex - eye_hw * 0.72), int(ey - eye_hh * 0.06)),
                         (int(ex + eye_hw * 0.72), int(ey - eye_hh * 0.12)),
                         max(1, int(1.2 * ss)))

    # — Nose: a small dark upside-down heart skull-hole between + below the eyes.
    nose_y = cy + r * 0.30
    nose = [(cx, nose_y + r * 0.12), (cx - r * 0.10, nose_y - r * 0.05),
            (cx + r * 0.10, nose_y - r * 0.05)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose])

    # — Mouth: a BOLD lantern-skull tusk-grille — the jack-o tell strengthened
    #   to survive the chip (directive 6) so the read is sleepy-cute lantern-
    #   skull, never a generic lich. Wider, deeper ink seat; chunkier teeth.
    grin_y = cy + r * 0.66
    grin_hw = r * 0.78
    grin_h = r * 0.42
    seat_top, seat_bot = [], []
    n = 16
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * grin_hw
        lift = grin_h * 0.50 * (xr * xr)
        seat_top.append((x, grin_y - grin_h * 0.5 + lift))
        seat_bot.append((x, grin_y + grin_h * 0.5 + lift * 0.4))
    seat = seat_top + seat_bot[::-1]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in seat])

    # Even teeth (4) leave a fat ink GRILLE POST dead-center — the jack-o tell,
    # fattened ~1px via a wider inter-tooth gap so the central post survives
    # day-1x as a tell, not a smudge (critique priority 2).
    teeth = 4
    gap = grin_hw * 0.18
    tw = (grin_hw * 1.55 - gap * (teeth - 1)) / teeth
    th = grin_h * 0.58
    for i in range(teeth):
        tx = -grin_hw * 0.78 + i * (tw + gap)
        xr = (tx + tw * 0.5) / grin_hw
        ty = grin_y - grin_h * 0.5 + grin_h * 0.50 * (xr * xr) + ss
        rect = pygame.Rect(int(cx + tx + ss * 0.5), int(ty),
                           int(tw - ss * 0.5), int(th))
        pygame.draw.rect(surf, BONE, rect, border_radius=max(1, int(1.2 * ss)))
        pygame.draw.rect(surf, BONE_DK, rect, max(1, int(ss)),
                         border_radius=max(1, int(1.2 * ss)))

    for s in (-1, 1):
        bx = cx + s * grin_hw * 0.84
        by = grin_y + grin_h * 0.08
        tusk = [
            (bx, by),
            (bx + s * grin_hw * 0.14, by - grin_h * 0.85),
            (bx + s * grin_hw * 0.30, by - grin_h * 0.58),
            (bx + s * grin_hw * 0.18, by + grin_h * 0.30),
        ]
        pygame.draw.polygon(surf, BONE_DK, [(int(x), int(y)) for x, y in tusk])
        inner_k = [(bx + s * ss, by - ss),
                   (bx + s * grin_hw * 0.12, by - grin_h * 0.74),
                   (bx + s * grin_hw * 0.24, by - grin_h * 0.50),
                   (bx + s * grin_hw * 0.16, by + grin_h * 0.18)]
        pygame.draw.polygon(surf, BONE, [(int(x), int(y)) for x, y in inner_k])


# ── the whole creature: head + trailing orb-string, on one surface ───────────

def _face_tell(surf, cx, cy, r, ss):
    """A baked LOW-RES face tell (icon gate) that PRESERVES the sleepy-skull
    read at true 32px instead of collapsing to two gold blobs (critique
    priority 1). Each eye is a gold crescent capped by a HARD INK upper-lid
    bar — the half-closed SHAPE survives downscale — over a BOLD ink grin-bar
    with notched teeth so the lantern-skull tell holds. Gold doubles as the
    contained-warm tell at icon scale; the INK does the expression."""
    eye_dx = r * 0.46
    eye_dy = r * 0.06
    eye_hw = r * 0.40          # WIDE…
    eye_hh = r * 0.24          # …SHORT — the heavy-lidded slot at icon scale
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        # Ink socket rim (wide short) + a WIDE LOW gold crescent pooled at the
        # bottom — wider than tall so it reads sleepy, not a round open eye.
        rim = pygame.Rect(0, 0, int(eye_hw * 2.30), int(eye_hh * 2.30))
        rim.center = (int(ex), int(ey))
        pygame.draw.ellipse(surf, INK, rim)
        gold = pygame.Rect(0, 0, int(eye_hw * 1.85), int(eye_hh * 1.50))
        gold.center = (int(ex), int(ey + eye_hh * 0.42))
        pygame.draw.ellipse(surf, ORB, gold)
        pygame.draw.circle(surf, ORB_CORE,
                           (int(ex), int(ey + eye_hh * 0.55)),
                           max(1, int(eye_hh * 0.40)))
        # HEAVY INK upper-lid covering the top ~58% — the dominant sleepy SHAPE
        # tell that holds at true 32px (a thin gold crescent left beneath).
        lw, lh = int(eye_hw * 2.6), int(eye_hh * 2.8)
        lid = pygame.Surface((lw, lh), pygame.SRCALPHA)
        pygame.draw.ellipse(lid, INK,
                            pygame.Rect(0, 0, lw, int(eye_hh * 2.4)))
        lid.fill((0, 0, 0, 0),
                 pygame.Rect(0, int(eye_hh * 1.18), lw, lh))
        surf.blit(lid, (int(ex - lw / 2), int(ey - eye_hh * 1.05)))

    # A cracked-brow ink hint above the eyes (focal asymmetry at icon scale).
    pygame.draw.line(surf, INK,
                     (int(cx - r * 0.20), int(cy - r * 0.36)),
                     (int(cx + r * 0.20), int(cy - r * 0.30)),
                     max(2, int(1.6 * ss)))

    # BOLD ink grin-bar with notched teeth — the lantern-skull grille tell.
    gw = r * 0.82
    gy = cy + r * 0.58
    gh = r * 0.26
    top, bot = [], []
    n = 12
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * gw
        lift = gh * 1.25 * (xr * xr)
        top.append((x, gy - gh * 0.5 + lift))
        bot.append((x, gy + gh * 0.5 + lift))
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in (top + bot[::-1])])
    # Two bone tooth-notches spread a touch WIDER so the central ink GRILLE POST
    # between them fattens ~1px — the jack-o tell that must survive day-1x
    # against bright sky, not collapse to a smudge (critique priority 2).
    for tx in (-r * 0.28, r * 0.28):
        xr = tx / gw
        ty = gy - gh * 0.5 + gh * 1.25 * (xr * xr)
        rect = pygame.Rect(int(cx + tx - r * 0.06), int(ty + gh * 0.10),
                           int(r * 0.12), int(gh * 0.62))
        pygame.draw.rect(surf, BONE, rect)


def build_krasue(scale=1.0, ss=6, *, night=False, compact=False):
    """The full creature on its own transparent surface: the floating skull-
    lantern head up top, a viscera ORB-STRING streaming straight down beneath it
    tipped with the cracked bottom lantern-orb. Returns an outlined surface.
    EPIC pipeline: built LARGE at SS=6, smoothscaled down for crisp downscale.

    `compact` is the GAMEPLAY / 32px-icon variant: the HEAD is grown to dominate
    ~55-60% of the vertical budget and the string cut to 3 orbs, so the icon reads
    'sleepy skull on a short orb-string' — never a faint thread + speck. Compact
    also bakes a low-res face tell.

    EPIC (critique priority 4 + directive 5): the hero head is grown to dominate
    ~60-65% of the frame, the string drops to 4 FAT beads (legibility > count),
    and a restrained cool-mauve outer AURA rings the whole head so it reads as a
    screen-filling boss, not a coin pickup."""
    head_r = int(46 * scale) * ss
    string_mult = 1.20 if compact else 2.35
    string_len = int(head_r * string_mult)
    n_orbs = 3 if compact else 4
    # Tighter side pad so the big head FILLS its frame (boss read, not pickup).
    side_pad = int(12 * scale) * ss
    top_pad = int(20 * scale) * ss         # room for the cool aura halo
    bot_pad = int(26 * scale) * ss         # room for the bottom orb glow halo

    head_cx_off = side_pad + head_r + int(8 * scale) * ss
    head_cy = top_pad + head_r * 1.04

    # The orb-string springs from just under the jaw.
    string_top_y = head_cy + head_r * 1.20
    feet_y = string_top_y + string_len

    W = int(head_cx_off * 2)
    H = int(feet_y + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # — Restrained cool-mauve outer aura around the whole head (NOT a gradient
    #   wash) — a low-alpha additive halo that pushes the EPIC boss-scale read
    #   while keeping the body cool (warm stays inside the orbs).
    aura_r = int(head_r * 1.55)
    aura = make_glow_surface(aura_r, BODY_SHEEN,
                             alpha_center=70 if night else 48, falloff=2.6)
    surf.blit(aura, (int(cx - aura_r), int(head_cy - aura_r)),
              special_flags=pygame.BLEND_ADD)

    base_r = head_r * (0.30 if compact else 0.36)
    _orb_string(surf, cx, string_top_y, string_len, base_r, ss,
                n_orbs=n_orbs, wave=0.6 if compact else 0.9, phase=0.5,
                end_cracked=True, night=night)

    _head(surf, cx, head_cy, head_r, ss, night=night)
    if compact:
        _face_tell(surf, cx, head_cy, head_r, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _orb_column(surf, cx, top_y, bot_y, base_r, ss):
    """The repeatable PILLAR BODY: the viscera orb-string as a straight tiling
    shaft — a thin mauve sinew threaded with evenly-spaced gold gut-orbs at a
    steady on-axis cadence (the band that mirrors top<->bottom). Drawn vertical
    (no wave) so it tiles cleanly along the post."""
    length = bot_y - top_y
    # The sinew cord down the axis — a visible INK thread with a mauve underside
    # so the beads read strung onto one gut-line at 1x (directive 3).
    pygame.draw.line(surf, INK, (int(cx), int(top_y)), (int(cx), int(bot_y)),
                     max(2, int(3.4 * ss)))
    pygame.draw.line(surf, SINEW_DK, (int(cx + 1.0 * ss), int(top_y)),
                     (int(cx + 1.0 * ss), int(bot_y)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, SINEW, (int(cx), int(top_y)),
                     (int(cx), int(bot_y)), max(1, int(1.4 * ss)))
    # Evenly-spaced orbs — the organ band that repeats top<->bottom. Slightly
    # gappier cadence so each bead stays discrete at the true obstacle scale.
    band = base_r * 2.9
    n = max(2, int(length / band))
    band = length / n
    for i in range(n):
        by = top_y + (i + 0.5) * band
        _gut_orb(surf, cx, by, base_r, ss)


def _cracked_cap(surf, cx, cap_base_y, base_r, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP, derived from the creature's OWN form: a short
    sinew neck of one small orb, then a big CRACKED bottom lantern-orb hanging at
    the gap edge and radiating gold INTO the gap. `point_up` reaches toward the
    gap (up for a bottom pillar). Sits on-axis so the top<->bottom mirror is
    clean and there is no top-heavy cap (the cap == one larger orb, not a crown)."""
    d = -1 if point_up else 1
    # A short connective neck: one small orb between shaft and the lantern.
    neck_y = cap_base_y + d * base_r * 1.6
    _gut_orb(surf, cx, neck_y, base_r * 0.7, ss, night=night)
    # The big cracked bottom lantern-orb at the gap edge.
    hy = cap_base_y + d * base_r * 4.0
    _gut_orb(surf, cx, hy, base_r * 1.45, ss, night=night, cracked=True)


def _orb_pillar_obstacle(height, ss, *, flip, night=False):
    """One viscera orb-string PILLAR obstacle: the beaded orb-string fills the
    post and the cracked bottom lantern-orb CAP sits at the GAP-facing edge,
    radiating INTO the gap. `flip=True` is the TOP pillar — cap at the bottom
    (gap) edge, reaching DOWN into the gap; `flip=False` is the BOTTOM pillar —
    cap at the TOP (gap) edge, reaching UP. Both mirror the same orb-string body
    into a clean vertical orb-pillar lanterned at the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    base_r = 13 * ss
    cap_band = int(56 * ss)
    if flip:
        _orb_column(surf, cx, 0, bh - cap_band, base_r, ss)
        _cracked_cap(surf, cx, bh - cap_band, base_r, ss, point_up=False, night=night)
    else:
        _orb_column(surf, cx, cap_band, bh, base_r, ss)
        _cracked_cap(surf, cx, cap_band, base_r, ss, point_up=True, night=night)
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


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((58, 56, 62))          # neutral grey bg
    _label(sheet, font,
            "KRASUE  —  leyak-EPIC #1  —  cool dusk-mauve skull-lantern + warm-gold gut-orb STRING  —  round 3", 18, 12)
    _label(sheet, small,
            "EPIC pipeline: rendered LARGE @ SS=6 then smoothscaled. Body COOL (mauve); firefly-gold confined STRICTLY to discrete gut-orbs. Orb-string IS the pillar.",
            18, 32, (210, 200, 218))

    # — Cell A: BIG hero sprite on a dusk-mauve sky.
    panel = pygame.Rect(18, 56, 360, 580)
    bgA = _sky(panel.w, panel.h, (52, 36, 66), (104, 70, 108), (176, 132, 150))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (130, 110, 140), panel, 2, border_radius=8)
    boss = build_krasue(scale=2.2, ss=6)
    # Pin the big head high in the panel so it FILLS the frame (EPIC boss read).
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2, panel.y + 38))
    _label(sheet, font, "(a) HERO  big @ SS=6", panel.x + 8, panel.y + 8)
    _label(sheet, small, "BOSS-scale head + cool aura + 4 fat lantern-orbs on an ink sinew",
           panel.x + 8, panel.y + 28, (232, 222, 238))

    # — Cell B: orb-string as a tileable PILLAR pair @ TRUE obstacle scale (NIGHT),
    #   plus a 2x zoom on the CAP band proving the cracked lantern-orb lights the gap.
    panelB = pygame.Rect(394, 56, 360, 580)
    bg = _sky(panelB.w, panelB.h, (8, 8, 32), (20, 18, 58), (44, 32, 78), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (130, 110, 140), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE scale (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 470
    slice_x = panelB.x + 24
    slice_y = panelB.y + 44
    gap_top = 150
    gap_h = 128
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _orb_pillar_obstacle(top_h, 6, flip=True, night=True)
    bot_pillar = _orb_pillar_obstacle(bot_h, 6, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (210, 196, 222), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): even gut-orb", slice_x - 2, slice_y + slice_h + 6, (225, 215, 232))
    _label(sheet, small, "cadence tiles; cracked end-orb", slice_x - 2, slice_y + slice_h + 22, (255, 236, 196))
    _label(sheet, small, "LANTERNS the gap (mirrored)", slice_x - 2, slice_y + slice_h + 38, (255, 236, 196))

    cap_band = 56
    zw, zh = pw, 170
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 12
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 178
    zy = panelB.y + 96
    zbg = _sky(zw * 2, zh * 2, (8, 8, 32), (16, 14, 48), (30, 22, 64))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (210, 196, 222), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "cracked bottom lantern-orb", zx - 2, zy + zh * 2 + 6, (255, 236, 196))
    _label(sheet, small, "(creature's own form, on-axis)", zx - 2, zy + zh * 2 + 22, (255, 236, 196))

    # — Cell C: the GAMEPLAY icon (compact, head-dominant) — the TRUE 32px chip on
    #   a day sky AND a night sky to prove legibility, then a 4x audit + grayscale.
    panelC = pygame.Rect(770, 56, 392, 580)
    pygame.draw.rect(sheet, (44, 42, 48), panelC, border_radius=8)
    pygame.draw.rect(sheet, (130, 110, 140), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) GAMEPLAY ICON  —  TRUE 32px legibility", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "head ~55-60% of the icon / short 3-orb string", panelC.x + 8, panelC.y + 28,
           (232, 222, 238))

    boss1x = build_krasue(scale=0.62, ss=6, compact=True)
    boss1x_n = build_krasue(scale=0.62, ss=6, night=True, compact=True)
    day = _sky(180, 300, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 300, (8, 8, 32), (20, 18, 58), (44, 32, 78), stars=True)

    dy = panelC.y + 46
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2, dy + 8))
    sheet.blit(boss1x_n, (panelC.x + 200 + 90 - boss1x_n.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 30, 26))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (255, 236, 196))

    gy = dy + 312
    _label(sheet, small, "TRUE 32px chip on day + night sky (1x, no blow-up):",
           panelC.x + 14, gy - 2, (228, 218, 228))
    icon_src = build_krasue(scale=1.0, ss=6, compact=True)
    target_h = 64
    sc = target_h / icon_src.get_height()
    icon = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc)), target_h))
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * (32 / icon_src.get_height()))), 32))
    swatches = [
        ((40, 110, 200), "day 1x"),
        ((44, 32, 78), "night 1x"),
        ((104, 70, 108), "dusk 1x"),
    ]
    sx = panelC.x + 14
    sw = 86
    for col, lab in swatches:
        chip = pygame.Rect(sx, gy + 16, sw, 84)
        pygame.draw.rect(sheet, col, chip, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 240))
        sx += sw + 10

    chip = pygame.Rect(panelC.x + 14, gy + 112, 86, 84)
    pygame.draw.rect(sheet, (90, 90, 96), chip, border_radius=4)
    sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                        chip.centery - icon32.get_height() // 2))
    sheet.blit(icon, (chip.centerx + 22, chip.centery - icon.get_height() // 2))
    _label(sheet, small, "32 / 64px", chip.x + 4, chip.y + 2, (240, 240, 240))
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    sheet.blit(blow, (panelC.x + 116, gy + 8))
    _label(sheet, small, "4x blow-up of the 32px icon (face tell baked)",
           panelC.x + 116, gy + 8 + blow.get_height() + 2, (228, 218, 228))

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

    gray = _to_gray(icon)
    chip = pygame.Rect(panelC.x + 290, gy + 112, 86, 84)
    pygame.draw.rect(sheet, (120, 124, 120), chip, border_radius=4)
    sheet.blit(gray, (chip.centerx - gray.get_width() // 2,
                      chip.centery - gray.get_height() // 2))
    _label(sheet, small, "grayscale", chip.x + 4, chip.y + 2, (24, 24, 24))

    # — Footer captions.
    _label(sheet, small,
           "STYLE: flat saturated fills; hard 1-2px ink keyline (28,22,30); dark-core -> flat-fill -> top-left lilac rim-sheen triad; 1px grown outline; chibi; scary-CUTE (sleepy half-lids).",
           18, SH - 84, (205, 196, 214))
    _label(sheet, small,
           "BODY COOL: dusk-mauve face/skull; firefly-gold ONLY inside the gut-orbs (contained warm glow, never on flesh). Membrane veining + inner orb glow-lobes = elevated detail.",
           18, SH - 64, (205, 196, 214))
    _label(sheet, small,
           "PROP->PILLAR: the evenly-beaded gut-orb string tiles as the shaft (thin sinew); the cracked bottom lantern-orb (own form) caps + LIGHTS the gap on-axis. Clean mirror, no top-heavy cap.",
           18, SH - 44, (205, 196, 214))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()

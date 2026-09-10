"""
Round-2 concept renderer for STUPIKA — the walking skull-stupa reliquary lord
(Batch 2 / Citipati-versions set, concept #2). Headless Pygame; ELEVATED
pipeline (supersample SS=6 → smoothscale) so the stacked geometry stays crisp
at downscale. Keeps the shipped house grammar: flat saturated fills, hard 1-2px
ink keyline, dark-core → flat-fill → top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE; procedural-only (no gradients/PNGs).

WHY this concept is the STACKED-TOWER of the brood (the one architectural /
stacked-mass silhouette): every sibling is a creature wearing bone — Stupika IS
masonry that grew a face. A holy bone-skyscraper that sprouted big eyes on its
GROUND FLOOR and toddled off: sacred, stomping, weirdly endearing. The skull
tiers are literal stupa modules — a multi-tier lion-throne base, a bell-dome
belly, a harmika cube neck, capped by a kapala-dome + 13-disc spire finial.

WHY the read survives the cross-set police: the ONE live face is the LOWEST
tier (big eyes) so the figure reads as a creature, never a wall — and mass sits
at the BASE, never top-heavy. 3 tiers MAX so each skull-band reads at 1x. Gilt-
saffron is reserved STRICTLY to the cornice bands + spire (a thin focal line,
never a second mass). Vermilion is STRICTLY LINEAR — a thin prayer-cord swag,
never a fill. The cleanest creature=prop=pillar mirror in the set: the tower IS
the shaft, the kapala-dome + spire IS the gap-cap.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Chalk-grey bone — a hair DARKER / warmer-neutral than the brood's other pales
# so the gilt-saffron cornices read as the focal value, not the bone.
BONE      = (206, 202, 196)   # chalk-grey bone (dominant fill)
BONE_D    = (146, 144, 142)   # slate-chalk dark-core / shade
BONE_DD   = (104, 102, 100)   # deepest hollow (sockets, module grooves)
BONE_SH   = (244, 242, 238)   # bone top-left rim-sheen
GILT      = (228, 176,  72)   # gilt-saffron — CORNICE BANDS + spire ONLY
GILT_BR   = (248, 212, 132)   # gilt highlight
GILT_D    = (170, 124,  44)   # gilt dark-core
VERMILION = (196,  72,  58)   # vermilion prayer-cord swag — THIN LINEAR only
VERMIL_BR = (228, 116,  96)
LAMP      = (255, 214, 128)   # butter-lamp glow at spire / dome
LAMP_HOT  = (255, 240, 196)   # hottest lamp core
INK       = ( 28,  26,  26)   # hard ink keyline
SHEEN     = (244, 242, 238)   # sheen highlight

BG        = ( 96,  96, 100)   # neutral grey review backdrop
PANEL     = ( 74,  76,  80)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, SHEEN, 0.6), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob — dark core bottom-right, sheen top-left."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, SHEEN, 0.65),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


# ── a gilt cornice band (the ONLY home for gilt-saffron on the body) ──────────
def gilt_cornice(surf, cx, y, half_w, s, flare=0.14, ow=None):
    """A thin trapezoidal gilt ledge capping a module — the stupa cornice. WHY a
    flared lip: it reads as architectural masonry stepping outward, and keeps
    gilt a CRISP LINEAR ledge (never a mass). Top-left sheen + dark underside."""
    if ow is None:
        ow = max(1, int(1.2 * s))
    lip = int(half_w * flare)
    band = [(cx - half_w - lip, y),
            (cx + half_w + lip, y),
            (cx + half_w, y + int(6 * s)),
            (cx - half_w, y + int(6 * s))]
    triad_blob(surf, GILT, band,
               sheen_pts=[(cx - half_w - lip, y), (cx + int(2 * s), y),
                          (cx + int(2 * s), y + int(2 * s)),
                          (cx - half_w - lip, y + int(2 * s))],
               ow=ow)
    # bright top edge — the metallic catch
    pygame.draw.line(surf, GILT_BR, (cx - half_w - lip + int(s), y + int(s)),
                     (cx + half_w + lip - int(s), y + int(s)), max(1, int(1 * s)))


# ── a thin vermilion prayer-cord swag (the ONLY home for vermilion) ───────────
def prayer_swag(surf, cx, y, half_w, s, droop=10):
    """A thin slack catenary cord with a tiny knot at each peg — strictly LINEAR.
    WHY drawn as a polyline, never a fill: the cross-set rule forbids a second
    saturated mass; the cord is a hair-thin festoon hung between two tiers."""
    pts = []
    seg = 10
    d = int(droop * s)
    for i in range(seg + 1):
        t = i / seg
        x = cx - half_w + (2 * half_w) * t
        # catenary-ish sag
        sag = math.sin(t * math.pi) * d
        pts.append((x, y + sag))
    pygame.draw.lines(surf, INK, False, pts, max(2, int(2.6 * s)))
    pygame.draw.lines(surf, VERMILION, False, pts, max(1, int(1.8 * s)))
    pygame.draw.lines(surf, VERMIL_BR, False, pts[:len(pts)//2], max(1, int(1 * s)))
    # peg knots at each end
    for px in (cx - half_w, cx + half_w):
        pygame.draw.circle(surf, INK, (int(px), y), max(1, int(2.2 * s)))
        pygame.draw.circle(surf, VERMILION, (int(px), y), max(1, int(1.4 * s)))


# ── the kapala-dome + 13-disc spire finial (the gap-cap, also the body crown) ─
def stupa_crown(surf, cx, base_y, w, s, lit=True, full=True):
    """A bell/kapala dome topped by a tapering 13-disc gilt spire and a butter-
    lamp jewel. WHY this is the cap AND the creature's crown: the boss's own head
    finial tiles directly as the pillar gap-cap — the cleanest mirror in the
    brood. `lit` lights the lamp-jewel toward the gap. `full` draws the spire;
    when False only the dome shows (used when stacking under another tier)."""
    dome_r = int(w * 0.5)
    dome_cx, dome_cy = cx, base_y - int(dome_r * 0.62)
    # === kapala bell-dome — a half-egg bone mass ===
    dome_rect = (dome_cx - dome_r, dome_cy - int(dome_r * 0.86),
                 dome_r * 2, int(dome_r * 1.7))
    # build the dome as a polygon so the bell curve reads (flat top-ish, round)
    dome = []
    for i in range(13):
        a = math.pi + (i / 12) * math.pi   # left → right across the top
        dome.append((dome_cx + math.cos(a) * dome_r,
                     dome_cy + math.sin(a) * int(dome_r * 0.92)))
    dome += [(dome_cx + int(dome_r * 0.92), base_y),
             (dome_cx - int(dome_r * 0.92), base_y)]
    triad_blob(surf, BONE, dome,
               core_pts=[(dome_cx, dome_cy),
                         (dome_cx + int(dome_r * 0.9), dome_cy + int(dome_r * 0.2)),
                         (dome_cx + int(dome_r * 0.85), base_y),
                         (dome_cx, base_y)],
               sheen_pts=[(dome_cx - int(dome_r * 0.9), dome_cy + int(dome_r * 0.1)),
                          (dome_cx - int(dome_r * 0.2), dome_cy - int(dome_r * 0.7)),
                          (dome_cx - int(dome_r * 0.05), dome_cy - int(dome_r * 0.5)),
                          (dome_cx - int(dome_r * 0.55), dome_cy + int(dome_r * 0.15))],
               ow=max(1, int(1.6 * s)))
    # a relic "eye" socket on the dome — the reliquary aperture, lamp-lit
    sock_y = dome_cy + int(dome_r * 0.1)
    pygame.draw.circle(surf, INK, (dome_cx, sock_y), max(2, int(dome_r * 0.30)))
    if lit:
        pygame.draw.circle(surf, LAMP, (dome_cx, sock_y), max(1, int(dome_r * 0.21)))
        pygame.draw.circle(surf, LAMP_HOT, (dome_cx, sock_y - int(s)), max(1, int(dome_r * 0.10)))
    else:
        pygame.draw.circle(surf, BONE_DD, (dome_cx, sock_y), max(1, int(dome_r * 0.20)))

    if not full:
        return dome_cy

    # === harmika cube — a small square plinth above the dome ===
    harm_w = int(dome_r * 0.66)
    harm_h = int(dome_r * 0.42)
    harm_y = dome_cy - int(dome_r * 0.78)
    harm = [(dome_cx - harm_w // 2, harm_y),
            (dome_cx + harm_w // 2, harm_y),
            (dome_cx + harm_w // 2, harm_y + harm_h),
            (dome_cx - harm_w // 2, harm_y + harm_h)]
    triad_blob(surf, BONE, harm,
               core_pts=[(dome_cx, harm_y), (dome_cx + harm_w // 2, harm_y),
                         (dome_cx + harm_w // 2, harm_y + harm_h),
                         (dome_cx, harm_y + harm_h)],
               ow=max(1, int(1.2 * s)))
    # gilt cornice capping the harmika
    gilt_cornice(surf, dome_cx, harm_y, harm_w // 2, s, flare=0.2)

    # === 13-disc gilt spire — tapering stacked discs ===
    spire_base = harm_y - int(2 * s)
    n_disc = 7   # reads as "many discs" at scale without mush; 13 implied
    disc_pitch = int(dome_r * 0.16)
    for i in range(n_disc):
        dy = spire_base - i * disc_pitch
        dw = int(dome_r * (0.46 - i * 0.045))
        pygame.draw.line(surf, INK, (dome_cx - dw, dy), (dome_cx + dw, dy),
                         max(2, int(3.0 * s)))
        pygame.draw.line(surf, GILT, (dome_cx - dw, dy), (dome_cx + dw, dy),
                         max(1, int(2.0 * s)))
        pygame.draw.line(surf, GILT_BR, (dome_cx - int(dw * 0.7), dy - int(0.4 * s)),
                         (dome_cx + int(dw * 0.2), dy - int(0.4 * s)), max(1, int(1 * s)))
    # spire core rod
    spire_top = spire_base - (n_disc - 1) * disc_pitch
    pygame.draw.line(surf, GILT_D, (dome_cx, spire_base), (dome_cx, spire_top),
                     max(1, int(1.6 * s)))

    # === parasol / crescent + the crowning butter-lamp jewel ===
    jewel_y = spire_top - int(dome_r * 0.30)
    # small crescent cradle
    pygame.draw.arc(surf, GILT,
                    (dome_cx - int(dome_r * 0.22), jewel_y - int(dome_r * 0.02),
                     int(dome_r * 0.44), int(dome_r * 0.34)),
                    math.radians(200), math.radians(340), max(1, int(1.8 * s)))
    # the glowing lamp jewel — the single warm focal at the very top
    triad_circle(surf, LAMP, (dome_cx, jewel_y), max(2, int(dome_r * 0.20)),
                 ow=max(1, int(1.2 * s)), core=False)
    pygame.draw.circle(surf, LAMP_HOT, (dome_cx - int(s), jewel_y - int(s)),
                       max(1, int(dome_r * 0.09)))
    return dome_cy


# ── a single skull-tier MODULE (the repeatable shaft band) ───────────────────
def skull_tier(surf, cx, top_y, half_w, h, s, face=False, lit_eyes=False):
    """One stacked stupa module shaped as a blunt skull-block: a slab cranium
    with a gilt cornice ledge under it and a vermilion swag slung beneath. WHY
    blocky not round: this is masonry — the tower must read as architecture, the
    skull is implied by socket-notches + a cornice 'brow'. Only the LOWEST tier
    passes `face=True` to wake the big live eyes (the creature tell)."""
    bot_y = top_y + h
    # slab body — slightly battered (wider at base) like a stupa course
    taper = int(half_w * 0.10)
    body = [(cx - half_w + taper, top_y),
            (cx + half_w - taper, top_y),
            (cx + half_w, bot_y),
            (cx - half_w, bot_y)]
    triad_blob(surf, BONE, body,
               core_pts=[(cx + int(2 * s), top_y),
                         (cx + half_w - taper, top_y),
                         (cx + half_w, bot_y), (cx + int(2 * s), bot_y)],
               sheen_pts=[(cx - half_w + taper, top_y),
                          (cx - int(half_w * 0.4), top_y),
                          (cx - int(half_w * 0.5), bot_y),
                          (cx - half_w, bot_y)],
               ow=max(1, int(1.6 * s)))

    if face:
        # === the LOWEST tier wears the ONE live face (big scary-cute eyes) ===
        # WHY the eyes sit LOW in the tier and the cornice/swag stay clear of
        # them: at 32px the only thing that flips "gold dots on a band" into
        # "two glowing eyes" is a DARK SOCKET GAP that isolates each lamp-core
        # from any horizontal trim. So the eye row owns the middle of the tier,
        # the gilt cornice lives at the very bottom, and NO vermilion crosses it.
        eye_y = top_y + int(h * 0.46)
        eye_dx = int(half_w * 0.50)   # widen the inter-eye dark gap
        eye_r = int(half_w * 0.30)
        for sgn in (-1, 1):
            ex = cx + sgn * eye_dx
            # recessed dark socket BOWL — a deep ink hollow the lamp sits inside,
            # ringed by chalk shade so the hole reads even when desaturated.
            pygame.draw.circle(surf, BONE_DD, (ex, eye_y), int(eye_r * 1.42))
            pygame.draw.circle(surf, INK, (ex, eye_y), int(eye_r * 1.12))
            # warm butter-lamp pupil — alive, peering out of the reliquary, sunk
            # inside the ink so a clear dark gap rings it on every side.
            pygame.draw.circle(surf, LAMP, (ex + sgn * int(s), eye_y + int(s)),
                               int(eye_r * 0.60))
            pygame.draw.circle(surf, LAMP_HOT, (ex - int(0.5 * s), eye_y - int(s)),
                               max(1, int(eye_r * 0.28)))
        # nose triangle hollow — small, kept between & below the eye line
        ny = eye_y + int(eye_r * 1.6)
        pygame.draw.polygon(surf, BONE_DD,
                            [(cx - int(half_w * 0.12), ny),
                             (cx + int(half_w * 0.12), ny),
                             (cx, ny + int(half_w * 0.22))])
        # a small, calm grin — scary-cute, a row of square teeth (the doorway),
        # sitting directly UNDER the eyes: eyes-over-teeth is the whole face read.
        my = bot_y - int(h * 0.20)
        tw = int(half_w * 0.60)
        pygame.draw.rect(surf, INK, (cx - tw, my - int(3 * s), tw * 2, int(7 * s)))
        for k in range(-2, 3):
            tx = cx + int(k * tw * 0.42)
            pygame.draw.line(surf, BONE, (tx, my - int(2 * s)),
                             (tx, my + int(3 * s)), max(1, int(1.4 * s)))
        # gilt cornice ledge — at the very BOTTOM of the live tier, well clear of
        # the eye row so gold never bands across the eyes.
        gilt_cornice(surf, cx, bot_y - int(3 * s), half_w, s, flare=0.16)
    else:
        # === upper tiers: BLIND architecture — no round + no warm core, so only
        # the lowest tier ever reads as a live face. These are masonry niches:
        # tall slot recesses + a relief lattice, deliberately NOT eye-shaped.
        gilt_cornice(surf, cx, bot_y - int(3 * s), half_w, s, flare=0.16)
        niche_y = top_y + int(h * 0.30)
        niche_h = int(h * 0.46)
        niche_w = int(half_w * 0.26)
        for sgn in (-1, 0, 1):
            nx = cx + sgn * int(half_w * 0.48)
            # an arched blind NICHE (tall slot, not a round socket)
            slot = [(nx - niche_w, niche_y + int(niche_h * 0.18)),
                    (nx - niche_w, niche_y + niche_h),
                    (nx + niche_w, niche_y + niche_h),
                    (nx + niche_w, niche_y + int(niche_h * 0.18))]
            pygame.draw.polygon(surf, BONE_DD, slot)
            # arched top of the niche
            pygame.draw.circle(surf, BONE_DD, (nx, niche_y + int(niche_h * 0.18)),
                               niche_w)
            # a thin shade lattice bar across the course (relief, reads as trim)
            pygame.draw.line(surf, BONE_D, (cx - int(half_w * 0.7), bot_y - int(h * 0.18)),
                             (cx + int(half_w * 0.7), bot_y - int(h * 0.18)),
                             max(1, int(1.4 * s)))

    return bot_y


# ── the walking skull-stupa ───────────────────────────────────────────────────
def draw_stupika(surf, cx, cy, s):
    """A 3-tier bone-stupa that toddled off: a WIDE lion-throne base tier with
    the live face, a narrower bell-belly tier, a slim harmika neck tier, capped
    by the kapala-dome + 13-disc spire finial. Two stubby bone feet poke out the
    base so it's caught mid-stomp (the 'walking' read). Mass sits at the BASE.
    `s` = unit scale around a ~150-unit-tall tower."""

    # vertical layout — base is the tallest/widest so the tower never goes
    # top-heavy. Heights chosen so 3 tiers + cap each read at 1x.
    base_bot = cy + int(58 * s)            # ground line of the throne plinth

    # === lion-throne plinth (the multi-step pedestal — pure mass at the floor) =
    plinth_w = int(56 * s)
    for i, (pw, ph) in enumerate(((plinth_w, 8), (int(plinth_w * 0.86), 7))):
        py = base_bot - i * int(8 * s)
        step = [(cx - pw, py - int(ph * s)), (cx + pw, py - int(ph * s)),
                (cx + pw - int(2 * s), py), (cx - pw + int(2 * s), py)]
        triad_blob(surf, BONE, step,
                   core_pts=[(cx, py - int(ph * s)), (cx + pw, py - int(ph * s)),
                             (cx + pw - int(2 * s), py), (cx, py)],
                   ow=max(1, int(1.4 * s)))
    # gilt cornice on the top plinth step
    gilt_cornice(surf, cx, base_bot - int(16 * s), int(plinth_w * 0.86), s, flare=0.12)

    # === stubby walking feet — ANCHORED into the plinth silhouette so they read
    # as part of the base block, not detached flecks at 1x. Each foot's TOP
    # overlaps up into the plinth (no gap to shimmer), and a short bone ankle
    # ties it to the plinth underside so the toddled-off read survives downscale.
    foot_y = base_bot - int(4 * s)
    for sgn, fx in ((-1, cx - int(28 * s)), (+1, cx + int(26 * s))):
        # one foot lifted mid-stomp (the right one, slightly up & forward)
        lift = int(5 * s) if sgn > 0 else 0
        # ankle stub bridging plinth → foot (kills the detached look)
        pygame.draw.rect(surf, BONE,
                         (fx - int(6 * s), base_bot - int(16 * s),
                          int(12 * s), int(16 * s)))
        foot = [(fx - int(13 * s), foot_y - lift),
                (fx + int(15 * s), foot_y - lift - int(2 * s)),
                (fx + int(14 * s), foot_y - lift + int(10 * s)),
                (fx - int(14 * s), foot_y - lift + int(9 * s))]
        triad_blob(surf, BONE, foot,
                   sheen_pts=[(fx - int(13 * s), foot_y - lift),
                              (fx + int(2 * s), foot_y - lift),
                              (fx + int(1 * s), foot_y - lift + int(3 * s)),
                              (fx - int(13 * s), foot_y - lift + int(3 * s))],
                   ow=max(1, int(1.4 * s)))
        # two stubby toe-bone ticks
        for k in (-5, 2):
            pygame.draw.line(surf, BONE_DD,
                             (fx + int(k * s), foot_y - lift + int(5 * s)),
                             (fx + int(k * s), foot_y - lift + int(9 * s)),
                             max(1, int(1.4 * s)))

    # === TIER 1 — wide base, the LIVE FACE (ground floor) ====================
    t1_h = int(46 * s)
    t1_top = base_bot - int(16 * s) - t1_h
    t1_hw = int(46 * s)
    skull_tier(surf, cx, t1_top, t1_hw, t1_h, s, face=True)

    # === TIER 2 — bell-belly, narrower ========================================
    t2_h = int(34 * s)
    t2_hw = int(35 * s)
    t2_top = t1_top - t2_h
    skull_tier(surf, cx, t2_top, t2_hw, t2_h, s, face=False)

    # vermilion prayer-cord swag hung at the TIER 2/1 division — the cornice seam
    # ABOVE the eye row, never crossing or kissing it. The cord must read as
    # masonry trim while the eyes alone read as the creature; they cannot share
    # a horizontal line (the round-1 merge that collapsed the face at 32px).
    prayer_swag(surf, cx, t1_top - int(2 * s), int(t1_hw * 0.78), s, droop=8)

    # === TIER 3 — slim harmika neck ===========================================
    t3_h = int(24 * s)
    t3_hw = int(25 * s)
    t3_top = t2_top - t3_h
    skull_tier(surf, cx, t3_top, t3_hw, t3_h, s, face=False)

    # === CAP — kapala-dome + 13-disc spire finial (the creature's crown) ======
    stupa_crown(surf, cx, t3_top + int(2 * s), int(t3_hw * 1.5), s, lit=True, full=True)


# ── the stupa tower → pillar mirror ───────────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The boss IS the pillar — the cleanest mirror in the brood. The stacked
    skull-tier MODULES tile as the shaft; the kapala-dome + spire finial caps the
    gap edge exactly as it crowns the creature. Mass is bottom-rooted: the gap
    cap is just the dome+spire, the heavy tiers run along the shaft toward the
    ground. `cap` names the END that faces the GAP."""
    shaft_hw = int(20 * s)
    cap_room = int(40 * s)

    # central battered shaft column the modules sit on (a faint ink core)
    pygame.draw.rect(surf, lerp(BONE, INK, 0.2),
                     (cx - shaft_hw, top, shaft_hw * 2, bot - top))

    # stack repeating skull-tier modules along the shaft toward the FAR end
    mod_h = int(26 * s)
    if cap == "bottom":
        # cap faces down → modules fill from the TOP down to the cap room
        y = top + int(2 * s)
        end = bot - cap_room
        while y + mod_h <= end:
            skull_tier(surf, cx, y, shaft_hw, mod_h, s, face=False)
            # thin vermilion swag every other module
            prayer_swag(surf, cx, y + int(5 * s), int(shaft_hw * 0.8), s, droop=5)
            y += mod_h
        cap_base = bot - int(6 * s)
        stupa_crown(surf, cx, cap_base, int(shaft_hw * 1.7), s, lit=True, full=True)
    else:
        # cap faces up → cap sits near the top, modules run down to the ground
        cap_base = top + cap_room
        y = cap_base + int(2 * s)
        end = bot - int(2 * s)
        while y + mod_h <= end:
            skull_tier(surf, cx, y, shaft_hw, mod_h, s, face=False)
            prayer_swag(surf, cx, y + int(5 * s), int(shaft_hw * 0.8), s, droop=5)
            y += mod_h
        stupa_crown(surf, cx, cap_base, int(shaft_hw * 1.7), s, lit=True, full=True)


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 820
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("STUPIKA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "walking skull-stupa reliquary lord  ·  STACKED-TOWER · ONE live face = lowest tier · gilt cornices + spire · round 2",
        True, LABEL_DIM), (210, 26))

    # === (a) BIG HERO =========================================================
    hero_big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
    draw_stupika(hero_big, 180 * SS, 235 * SS, 1.9 * SS)
    hero = grow_outline(pygame.transform.smoothscale(hero_big, (360, 470)), INK + (255,), 1)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("ONLY the lowest tier is live: lamp-eyes SUNK in dark ink sockets, over a", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("teeth grin. Upper tiers are BLIND niches (no round/no glow). Swag moved", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("OFF the eye line to the tier seam above. Feet anchored to the plinth.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable shaft ================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 62, 68), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — stupa-tower", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("skull-tier modules = tileable shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("kapala-dome + spire finial caps each gap edge", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted mass)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        # render a genuine ~32px-TALL tower
        big = pygame.Surface((72 * SS, 96 * SS), pygame.SRCALPHA)
        draw_stupika(big, 36 * SS, 50 * SS, (32 / 168.0) * SS)
        small = pygame.transform.smoothscale(big, (72, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 39, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 39, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # a 32px pillar gap-cap chip beside, on both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (BONE, "chalk-grey bone"), (BONE_D, "slate-chalk sh"),
        (GILT, "gilt-saffron"), (VERMILION, "vermilion swag"),
        (LAMP, "butter-lamp"), (LAMP_HOT, "lamp core"),
        (INK, "ink keyline"), (SHEEN, "sheen"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,26,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()

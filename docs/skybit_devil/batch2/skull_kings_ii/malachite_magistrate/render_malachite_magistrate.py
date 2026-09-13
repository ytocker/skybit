"""
Round-1 concept renderer for the MALACHITE MAGISTRATE — a royal SKULL-KING of
the second skull-king brood (DISCRETION sibling: no cradle, two arms). Headless
Pygame; ELEVATED pipeline (SS=6 -> smoothscale) so the banded-stone collar and
the bone face survive the downscale. Procedural-only (no gradients/PNGs).

WHY this king reads at a glance: the dominant mass is a WIDE FLAT ANVIL-T
SHOULDER-YOKE — a massive horizontal squared stone collar far wider than the
head, sitting on a narrow hidden body. The single hardest LOCK is that the
silhouette is widest at the SHOULDERS (a flat top bar) and tapers to a NARROW
planted base; if it ever widened at the base it would collapse into Carnelian's
top-down wedge. The magistrate is the read: an immovable stone judge, arms
folded sternly into the yoke, never a cradle and never a serpent coil.

WHY concentric malachite banding, kept BOLD: malachite's identity is its
banding, but fine stripes vanish at 32px. So the collar carries only 2-3 broad
light/dark green bands (dark-green ground, one mid-green band, one pale-green
sheen band) — bold enough to survive the downscale, never hairline.

WHY a green DOME + SKULL BOSS crown: the above-head tell is a low banded
malachite dome of two crossed bands meeting at a single bone skull boss at the
apex — a compact royal cap that breaks the silhouette over the head and stays
legible day and night without scattering into a comb.

WHY the focal is a single malachite eye-band: the brief's gate wants ONE named
brightest pixel. The face is cool bone; the brass edge is thin and dull; the
ONE saturated malachite eye-band glow (a bright green pin set across the
sockets) is the single brightest + most-saturated point — the magistrate's
gaze. Everything else is desaturated so that gaze owns the peak.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Cool bone face — the second-largest read; kept desaturated so the malachite
# eye-band stays the single brightest/most-saturated focal.
BONE      = (208, 212, 200)   # cool bone face (dominant non-green light)
BONE_D    = (160, 166, 156)   # bone shade / socket rim
BONE_DD   = (104, 110, 104)   # deepest bone hollow
BONE_SH   = (224, 228, 218)   # bone top-left rim-sheen (kept below the gaze peak)
# Malachite banding — the dominant mass colour; 2-3 BOLD bands only.
MAL_D     = ( 64, 128,  86)   # dark malachite ground (the dominant green band)
MAL       = ( 92, 156, 106)   # mid malachite (transition band)
MAL_BR    = (120, 184, 128)   # pale malachite sheen band
MAL_DD    = ( 40,  92,  62)   # deepest malachite recess (band seams)
# the SINGLE focal — a saturated malachite EYE-BAND glow (the magistrate's gaze)
EYE       = (104, 220, 120)   # saturated malachite gaze (focal base)
EYE_HOT   = (228, 255, 234)   # hottest gaze core (must be the brightest pixel)
EYE_D     = ( 60, 150,  82)   # gaze rim
# thin brass edge — a dull worked-metal trim ONLY, never a second mass.
BRASS     = (196, 168,  92)   # brass edge base (low-key)
BRASS_HI  = (228, 206, 140)   # thin brass specular pip (deliberately < eye core)
BRASS_D   = (132, 110,  56)   # recessed brass shadow
INK       = ( 28,  22,  30)   # 1-2px ink keyline

BG        = ( 96, 100, 108)
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


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
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, BONE, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, BONE, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                     core=False)


def brass_edge(surf, p0, p1, s):
    """A thin 1-2px brass trim line + a darker shadow line under it. WHY a line,
    not a fill: at 32px any filled brass becomes a second warm mass that fights
    the malachite gaze. A top brass edge + a recessed shadow edge reads as worked
    trim on stone at hero scale yet dissolves to near-nothing at 32px."""
    lw = max(1, int(1.4 * s))
    pygame.draw.line(surf, BRASS, p0, p1, lw)
    pygame.draw.line(surf, BRASS_D, (p0[0], p0[1] + lw), (p1[0], p1[1] + lw),
                     max(1, int(1.0 * s)))


def banded_panel(surf, pts, s, n=3, horizontal=True):
    """Fill a quad with 2 BOLD malachite bands split across the SHORT axis. WHY a
    straight light/dark SPLIT, not concentric insets: concentric green-on-green
    rings collapsed to one muddy tone at 32px (round-1 blocker). A single clean
    horizontal step — pale-malachite top half over dark-malachite bottom half —
    survives the downscale as an unmistakable light/dark banding read, and the
    seam is a THIN lightened line (not a heavy ink groove) so the slab never
    collapses to a single value."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pygame.draw.polygon(surf, INK, pts)
    if horizontal:
        # pale band on top, dark band on the bottom (light/dark step)
        mid = (y0 + y1) / 2.0
        pygame.draw.polygon(surf, MAL_D, pts)
        pygame.draw.rect(surf, MAL_BR, (x0, y0, x1 - x0, max(1, mid - y0)))
        # HARD light/dark step: a hairline ink seam (round 2's thick MAL seam
        # blurred the two bands into one tone at 32px — keep it 1px so the
        # MAL_BR / MAL_D value break stays crisp on the chip).
        pygame.draw.line(surf, MAL_DD, (x0, int(mid)), (x1, int(mid)), 1)
    else:
        # vertical robe-front: pale left, dark right
        mid = (x0 + x1) / 2.0
        pygame.draw.polygon(surf, MAL_D, pts)
        pygame.draw.rect(surf, MAL_BR, (x0, y0, max(1, mid - x0), y1 - y0))
        pygame.draw.line(surf, MAL, (int(mid), y0), (int(mid), y1),
                         max(1, int(1.4 * s)))
    pygame.draw.polygon(surf, INK, pts, max(1, int(1.4 * s)))


# -- malachite-LIGHT cap, a bone-white skull NOTCH for an apex, value-break ----
# Two crown values, brightened a step over MAL_BR so the cap out-values the bone
# face — round 2 still merged because three tiers (dome+boss+crescent) lived in
# ~6 vertical px at 32px. These read GREEN even at gameplay scale.
CAP_GREEN = (148, 214, 150)   # malachite-LIGHT cap — brightest green after EYE
CAP_RIM   = (108, 232, 128)   # saturated cap rim that carries green on night sky
# the skull NOTCH must read as a WHITE pop at 32px (round-3 BONE_SH was too cool
# /low to survive the chip); near-white out-values the green cap and the bone
# face both, so the apex pip stays a bright crown after the downscale.
NOTCH_WH  = (238, 240, 232)   # bone-white skull notch — a bright white pop on
                              # the green cap, but kept a step BELOW the EYE_HOT
                              # gaze core so the malachite eye-band stays the
                              # single brightest/most-saturated focal (LOCKED).
# a WARM brass detach-row between the green cap and the cool-bone face. WHY warm
# (not BONE_SH): a warm hue against cool-green above and cool-bone below is a
# real hue+value step that survives the downscale, where a near-bone ledge fused.
DETACH_BR = (224, 196, 120)   # warm brass detach-row (the float gap, day + night)


def dome_crown(surf, cx, cy, r, s):
    """ONE solid malachite-LIGHT cap, a bone-white skull NOTCH as its apex, and a
    single bone/brass value-break row detaching the cap from the bone face.

    WHY only TWO above-face values now (not three): at 32px there is room for a
    green cap and one bone pop above the face — no more. Round 2 stacked a dome,
    a separate boss BELOW the apex, and an underside crescent; in ~6px they
    merged to a dark blob. Here the cap is ONE solid CAP_GREEN ellipse (a full
    step brighter than the bone face so it out-values it), the skull boss IS the
    top of that cap as a single bone-white notch (not a tier beneath it), and a
    saturated CAP_RIM keeps the cap green on the night chip.

    WHY a forced bone/brass value-break ROW under the cap: a thin LIGHTEST-value
    ledge between the green cap and the bone face is the only thing that detaches
    the cap on the day chip — without it the bone cap-skirt and bone face share a
    value and fuse. Confirmed on the 32px chip, not the hero."""
    # base of the cap (the flat bottom that sits ON the value-break ledge)
    base_y = cy + int(r * 0.46)

    # the malachite-LIGHT CAP — one solid bright-green dome polygon (a flat-
    # bottomed half-ellipse) so it reads as a CAP, not a ball; no inner
    # crescent/sheen tiers to muddy it at scale. A 1px saturated rim ring under
    # it carries the green on the night chip. WHY a tall cap that sits HIGH and
    # well above the ledge: at 32px the green must own the whole top band so it
    # reads GREEN before the small bone notch — round-3a buried the green by
    # seating the cap into the ledge.
    cap_pts = []
    for k in range(0, 13):
        ang = math.pi * k / 12.0           # 0..pi sweep -> upper arc only
        cap_pts.append((cx - int(r * math.cos(ang)),
                        base_y - int(r * 1.18 * math.sin(ang))))
    cap_pts.append((cx + r, base_y))
    cap_pts.append((cx - r, base_y))
    pygame.draw.polygon(surf, INK, cap_pts)
    pygame.draw.polygon(surf, CAP_RIM, cap_pts)
    inner = [(cx + int((p[0] - cx) * 0.84), base_y - int((base_y - p[1]) * 0.88))
             for p in cap_pts]
    pygame.draw.polygon(surf, CAP_GREEN, inner)

    # FORCED VALUE-BREAK: a solid WARM-BRASS row (the float gap) seated where the
    # green cap meets the bone face — STOLEN FROM THE TOP OF THE FACE (it overlaps
    # the forehead, the cap mass above is untouched). WHY a full brass band, not a
    # bone ledge + hairline: a warm hue+value strip reads against BOTH the cool
    # green above and the cool bone below, so it survives the 32px downscale as a
    # crisp detach where round-3's near-bone ledge fused into the forehead. Made
    # tall enough (>= ~1px at the chip) that the cap visibly floats at 32px.
    row_h = max(2, int(r * 0.26))
    detach = [(cx - int(r * 1.04), base_y - int(r * 0.02)),
              (cx + int(r * 1.04), base_y - int(r * 0.02)),
              (cx + int(r * 0.96), base_y + row_h),
              (cx - int(r * 0.96), base_y + row_h)]
    pygame.draw.polygon(surf, INK, detach)
    pygame.draw.polygon(surf, DETACH_BR, detach)
    # a thin top specular keeps the brass reading as worked metal at the hero
    pygame.draw.line(surf, BRASS_HI,
                     (cx - int(r * 0.96), base_y - int(r * 0.02)),
                     (cx + int(r * 0.96), base_y - int(r * 0.02)),
                     max(1, int(1.2 * s)))

    # the skull NOTCH = the APEX of the cap, a bone-WHITE wedge set at the very top
    # of the green so green flanks + skirts it. WHY a wide near-white triangle (not
    # a small bone circle): round-3's BONE_SH circle was too cool + too small to
    # survive the chip; a near-white wedge raised to NOTCH_WH and widened owns a
    # bright crowning pop above the green that holds the squint at 32px.
    bx, by = cx, base_y - int(r * 0.86)
    bw = max(3, int(r * 0.52))         # half-width — wide enough to read at 32px
    bh = max(4, int(r * 0.64))         # tall wedge so the pop survives downscale
    notch = [(bx, by - bh),                     # apex
             (bx + bw, by + int(bh * 0.45)),    # right shoulder
             (bx + int(bw * 0.5), by + int(bh * 0.45)),
             (bx, by + int(bh * 0.18)),         # base notch (the skull cleft)
             (bx - int(bw * 0.5), by + int(bh * 0.45)),
             (bx - bw, by + int(bh * 0.45))]
    pygame.draw.polygon(surf, INK, notch)
    pygame.draw.polygon(surf, NOTCH_WH, notch)
    # tiny ink eye-pits so the white pop reads as a SKULL at hero scale (they
    # disappear at 32px, leaving a clean white crown — exactly the wanted read)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (bx + sgn * int(bw * 0.40), by),
                           max(1, int(bw * 0.20)))


# -- the bone skull face -------------------------------------------------------
def skull_face(surf, head_c, hr, s):
    """Cool bone skull. WHY the eye-band is drawn as a single saturated malachite
    BAR across BOTH sockets (not two separate glows): the focal must be ONE
    brightest point at 32px; a connected gaze-band collapses to a single bright
    green pixel-run, the magistrate's stare."""
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    # cheek hollows
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.28))
    # a stern flat brow ridge — the magistrate's immovable frown
    brow = [(head_c[0] - int(hr * 0.82), head_c[1] - int(hr * 0.30)),
            (head_c[0] + int(hr * 0.82), head_c[1] - int(hr * 0.30)),
            (head_c[0] + int(hr * 0.74), head_c[1] - int(hr * 0.10)),
            (head_c[0] - int(hr * 0.74), head_c[1] - int(hr * 0.10))]
    pygame.draw.polygon(surf, BONE_D, brow)
    pygame.draw.line(surf, INK, brow[0], brow[1], max(1, int(1.6 * s)))

    # the SOCKETS — dark recesses that frame the malachite gaze
    sock_y = head_c[1] + int(hr * 0.08)
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        pygame.draw.circle(surf, BONE_DD, (ex, sock_y), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, sock_y), int(hr * 0.28))

    # === FOCAL: the malachite EYE-BAND — one saturated bar across the sockets ==
    band_w = int(hr * 1.10)
    band_h = max(3, int(hr * 0.30))
    bx0 = head_c[0] - band_w // 2
    # soft saturated halo so the gaze owns the brightest region
    halo = pygame.Surface((band_w * 2, band_h * 4), pygame.SRCALPHA)
    pygame.draw.ellipse(halo, EYE + (70,),
                        (band_w * 0.5, band_h * 1.2, band_w, band_h * 1.6))
    surf.blit(halo, (head_c[0] - band_w, sock_y - band_h * 2))
    band = [(bx0, sock_y - band_h // 2), (bx0 + band_w, sock_y - band_h // 2),
            (bx0 + band_w, sock_y + band_h // 2), (bx0, sock_y + band_h // 2)]
    pygame.draw.polygon(surf, EYE_D, band)
    inner = [(bx0 + 2, sock_y - band_h // 2 + 1),
             (bx0 + band_w - 2, sock_y - band_h // 2 + 1),
             (bx0 + band_w - 2, sock_y + band_h // 2 - 1),
             (bx0 + 2, sock_y + band_h // 2 - 1)]
    pygame.draw.polygon(surf, EYE, inner)
    # the hottest core — the single brightest pixel of the whole king
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        pygame.draw.circle(surf, EYE_HOT, (ex, sock_y), max(2, int(hr * 0.13)))

    # nasal + grim tooth-row
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.12), head_c[1] + int(hr * 0.34)),
                         (head_c[0] + int(hr * 0.12), head_c[1] + int(hr * 0.34)),
                         (head_c[0], head_c[1] + int(hr * 0.58))])
    my = head_c[1] + int(hr * 0.76)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.44), my),
                     (head_c[0] + int(hr * 0.44), my), max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK,
                         (head_c[0] + int(k * hr * 0.18), my - int(hr * 0.06)),
                         (head_c[0] + int(k * hr * 0.18), my + int(hr * 0.10)),
                         max(1, int(1 * s)))


# -- the seated magistrate: ANVIL-T yoke over a narrow hidden body ------------
def draw_magistrate(surf, cx, cy, s):
    """LOCK: the silhouette is widest at the SHOULDERS (a flat top bar) and
    tapers to a NARROW planted base. Body is hidden under the yoke; two arms are
    folded sternly INTO the collar (the immovable judge), never cradling."""
    head_c = (cx, cy - int(34 * s))
    hr = int(20 * s)
    yoke_y = cy + int(2 * s)           # the flat horizontal shoulder bar
    yoke_half = int(58 * s)            # WIDEST measure — far wider than the head
    base_half = int(20 * s)            # narrow planted base (must stay < yoke_half)
    base_y = cy + int(52 * s)

    # === NARROW HIDDEN BODY (drawn first, mostly hidden by the yoke) ==========
    # WHY narrow + tapering DOWN: keeps all width at the shoulders so the read is
    # an anvil-T, not a bottom-heavy wedge. Base is a slim planted plinth.
    body = [(cx - int(22 * s), yoke_y + int(4 * s)),
            (cx + int(22 * s), yoke_y + int(4 * s)),
            (cx + base_half, base_y),
            (cx - base_half, base_y)]
    triad_blob(surf, BONE, body,
               core_pts=[(cx - int(6 * s), yoke_y + int(8 * s)),
                         (cx + int(18 * s), yoke_y + int(6 * s)),
                         (cx + int(base_half - 2), base_y - int(2 * s)),
                         (cx - int(2 * s), base_y - int(2 * s))],
               ow=max(1, int(1.6 * s)))
    # a slim banded malachite robe-front down the centre of the hidden body
    robe = [(cx - int(11 * s), yoke_y + int(6 * s)),
            (cx + int(11 * s), yoke_y + int(6 * s)),
            (cx + int(8 * s), base_y - int(2 * s)),
            (cx - int(8 * s), base_y - int(2 * s))]
    banded_panel(surf, robe, s, n=2, horizontal=False)
    # narrow planted plinth foot — slim so the base stays the narrowest point
    plinth = [(cx - base_half, base_y - int(2 * s)),
              (cx + base_half, base_y - int(2 * s)),
              (cx + base_half - int(3 * s), base_y + int(10 * s)),
              (cx - base_half + int(3 * s), base_y + int(10 * s))]
    triad_blob(surf, BONE_D, plinth, ow=max(1, int(1.6 * s)))
    brass_edge(surf, (cx - base_half + int(4 * s), base_y + int(2 * s)),
               (cx + base_half - int(4 * s), base_y + int(2 * s)), s)

    # === THE ANVIL-T SHOULDER-YOKE — the dominant mass =======================
    # A massive flat SQUARED stone collar, far wider than the head, banded green.
    # Drawn as a wide low bar with squared-off ends (the anvil top), thin at the
    # vertical extent so the silhouette stays a horizontal bar, not a block.
    yoke_th = int(20 * s)
    yoke = [(cx - yoke_half, yoke_y - yoke_th // 2),
            (cx + yoke_half, yoke_y - yoke_th // 2),
            (cx + yoke_half, yoke_y + yoke_th // 2),
            (cx + int(28 * s), yoke_y + yoke_th // 2 + int(6 * s)),
            (cx - int(28 * s), yoke_y + yoke_th // 2 + int(6 * s)),
            (cx - yoke_half, yoke_y + yoke_th // 2)]
    banded_panel(surf, yoke, s, n=3, horizontal=True)
    # squared anvil END-CAPS — bold band stacks at each shoulder tip so the bar
    # reads as a worked stone yoke with heavy ends (the anvil-T silhouette).
    for sgn in (-1, 1):
        ex = cx + sgn * yoke_half
        cap = [(ex - sgn * int(12 * s), yoke_y - yoke_th // 2 - int(3 * s)),
               (ex, yoke_y - yoke_th // 2 - int(3 * s)),
               (ex, yoke_y + yoke_th // 2 + int(3 * s)),
               (ex - sgn * int(12 * s), yoke_y + yoke_th // 2 + int(3 * s))]
        banded_panel(surf, cap, s, n=3, horizontal=True)
    # thin brass top-edge running the full span of the yoke (worked-stone trim)
    brass_edge(surf, (cx - yoke_half + int(3 * s), yoke_y - yoke_th // 2),
               (cx + yoke_half - int(3 * s), yoke_y - yoke_th // 2), s)

    # === TWO ARMS folded sternly INTO the yoke ===============================
    # WHY drawn after the yoke and tucked across the collar front: the magistrate
    # holds nothing — the folded forearms read as crossed authority, locking the
    # 'judge' silhouette and explicitly NOT a cradle.
    arm_th = int(9 * s)
    # left forearm crosses to the right, right forearm crosses to the left
    bone_limb(surf, (cx - int(34 * s), yoke_y + int(8 * s)),
              (cx - int(10 * s), yoke_y + int(13 * s)),
              (cx + int(20 * s), yoke_y + int(10 * s)), arm_th, s, joint=False)
    bone_limb(surf, (cx + int(34 * s), yoke_y + int(12 * s)),
              (cx + int(10 * s), yoke_y + int(17 * s)),
              (cx - int(18 * s), yoke_y + int(15 * s)), arm_th, s, joint=False)
    # bony knuckle clusters at the fold (hands tucked, not open)
    for (hx, hy) in ((cx + int(20 * s), yoke_y + int(10 * s)),
                     (cx - int(18 * s), yoke_y + int(15 * s))):
        triad_circle(surf, BONE, (hx, hy), int(5 * s), ow=max(1, int(1.2 * s)),
                     core=False)

    # === HEAD + DOME CROWN ===================================================
    skull_face(surf, head_c, hr, s)
    # WHY a bigger dome radius + a higher seat: the round-1 dome was too small to
    # survive 32px; a wider hump seated clear of the brow holds green + boss.
    dome_crown(surf, head_c[0], head_c[1] - int(hr * 1.04), int(hr * 1.02), s)


# -- the pillar mirror: a stacked banded-malachite yoke-column ----------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The magistrate's forms read into a pillar: a slim banded-stone shaft with
    stacked horizontal YOKE-BARS (echoing the anvil shoulders) and a domed cap
    crowned by a skull boss. Mirrors cleanly top<->bottom on-axis."""
    shaft_w = int(14 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    pitch = int(30 * s)
    cap_room = int(46 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        # slim banded malachite shaft segment
        seg = [(cx - shaft_w, y - int(11 * s)), (cx + shaft_w, y - int(11 * s)),
               (cx + shaft_w, y + int(11 * s)), (cx - shaft_w, y + int(11 * s))]
        banded_panel(surf, seg, s, n=2, horizontal=False)
        # a wide flat YOKE-BAR cinching the shaft (the anvil-T echo)
        bar = [(cx - shaft_w * 1.9, y - int(5 * s)),
               (cx + shaft_w * 1.9, y - int(5 * s)),
               (cx + shaft_w * 1.9, y + int(5 * s)),
               (cx - shaft_w * 1.9, y + int(5 * s))]
        banded_panel(surf, bar, s, n=3, horizontal=True)
        brass_edge(surf, (cx - shaft_w * 1.8, y - int(5 * s)),
                   (cx + shaft_w * 1.8, y - int(5 * s)), s)
        y += pitch

    # === domed cap with skull boss at the gap edge ===========================
    cap_y = (bot - int(30 * s)) if cap == "bottom" else (top + int(30 * s))
    fan_dir = -1 if cap == "bottom" else 1
    # a wide flat capstone yoke
    cap_bar = [(cx - int(26 * s), cap_y), (cx + int(26 * s), cap_y),
               (cx + int(20 * s), cap_y + fan_dir * int(12 * s)),
               (cx - int(20 * s), cap_y + fan_dir * int(12 * s))]
    banded_panel(surf, cap_bar, s, n=3, horizontal=True)
    brass_edge(surf, (cx - int(24 * s), cap_y),
               (cx + int(24 * s), cap_y), s)
    # the dome + skull boss pointing into the gap
    dome_y = cap_y - fan_dir * int(14 * s)
    if fan_dir < 0:
        dome_crown(surf, cx, dome_y, int(13 * s), s)
    else:
        # mirror the dome for the top-rooted cap by flipping vertically
        tmp = pygame.Surface((int(60 * s), int(60 * s)), pygame.SRCALPHA)
        dome_crown(tmp, int(30 * s), int(40 * s), int(13 * s), s)
        tmp = pygame.transform.flip(tmp, False, True)
        surf.blit(tmp, (cx - int(30 * s), dome_y - int(20 * s)))


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_magistrate(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_fonts():
    base = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(base, "..", "..", "..", "..", "..",
                      "game", "assets", "LiberationSans-Bold.ttf")
    try:
        return (pygame.font.Font(fp, 30), pygame.font.Font(fp, 17),
                pygame.font.Font(fp, 12))
    except Exception:
        return (pygame.font.SysFont("DejaVu Sans", 30, bold=True),
                pygame.font.SysFont("DejaVu Sans", 17, bold=True),
                pygame.font.SysFont("DejaVu Sans", 12))


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("MALACHITE MAGISTRATE", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "skull-KING (discretion: no cradle, 2 arms)  ·  WIDE FLAT ANVIL-T banded-green shoulder-yoke · "
        "green LIGHT cap + bone skull-notch crown · stern bone face · malachite eye-band focal · round 4",
        True, LABEL_DIM), (360, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 226, 1.85)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("ONE dominant mass = the wide flat ANVIL-T shoulder-yoke (widest at the", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("shoulders, taper to a NARROW base — not a wedge). 2-3 BOLD malachite bands;", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("dome + skull boss above; arms FOLDED in; malachite eye-band = brightest focal.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored ======================================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — banded yoke-column", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("slim banded malachite shaft, stacked flat YOKE-bars;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("domed capstone + skull boss into the gap", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_magistrate(big, 48 * SS, 50 * SS, (32 / 128.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        # WHY a BRIGHT malachite rim on the night chip: the bone+green mass would
        # muddy against a dark sky; a saturated pale-green halo (round-1 used a
        # too-dark EYE_D rim that vanished) carries the yoke + dome as GREEN while
        # the eye-band stays the unambiguous brightest point.
        if night:
            base = grow_outline(small, EYE + (255,), 2)
            return grow_outline(base, INK + (200,), 1)
        return grow_outline(small, INK + (255,), 1)

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(day_chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(night_chip, (panel_x + 20 + 27 - 1, night_y + 27 - 1))
    sheet.blit(font_sm.render("32px on night sky (malachite rim)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof — blacked-out hero so the anvil-T read is checked
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_magistrate(big, 75 * SS, 94 * SS, 1.30 * SS)
        small = pygame.transform.smoothscale(big, (150, 200))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((150, 200), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 150, 200))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 150, 200), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (sil_x, day_y + 204))
    sheet.blit(font_sm.render("(anvil-T: wide top, narrow base)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 168
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (MAL_D, "malachite dark band"), (MAL_BR, "malachite light band"),
        (BONE, "cool bone face"), (BONE_DD, "bone hollow"),
        (EYE, "eye-band (focal)"), (EYE_HOT, "eye-band hot core"),
        (BRASS, "brass edge"), (BRASS_HI, "brass highlight"),
        (MAL_DD, "band-seam recess"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 188
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ANVIL-T LOCK: widest at the SHOULDERS, taper to a NARROW base (never base-wide = Carnelian's wedge).  No serpent coil.  "
        "2-3 BOLD malachite bands only.  Malachite eye-band stays the single brightest focal; brass kept thin.  SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_4.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    self_check()


def self_check():
    """Verify (1) the brightest pixel sits inside the malachite eye-band, and
    (2) the anvil-T lock holds: the shoulder span is clearly wider than the base
    span on a hero render."""
    surf = pygame.Surface((400, 520), pygame.SRCALPHA)
    draw_magistrate(surf, 200, 250, 2.0)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    is_eye = (g > 230 and g >= r and g > b)

    # anvil-T width check: opaque span at the shoulder row vs the base row
    def span(row):
        xs = [x for x in range(w) if a[x, row] > 60]
        return (max(xs) - min(xs)) if xs else 0
    shoulder_row = by  # eye band sits just above the yoke; sample near yoke
    # the yoke sits ~2px below centre at scale 2 -> centre is y=250
    shoulder_span = span(252)
    base_span = span(250 + int(52 * 2.0) - 4)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> eye-band?", is_eye)
    print("self-check anvil-T: shoulder span=%d  base span=%d  -> wide-top? %s"
          % (shoulder_span, base_span, shoulder_span > base_span * 1.4))


if __name__ == "__main__":
    main()

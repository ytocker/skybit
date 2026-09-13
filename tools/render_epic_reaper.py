"""Look-dev mockup: the `reaper-shade` EPIC EVENT-BOSS, round 2.

WHY: a clean-sheet late-game boss that must out-class the chibi clown and stay
distinct from its sibling concepts. Reaper-shade's thesis is "Death itself" — a
FACELESS HOODED specter whose lower body DISSOLVES into smoke (no feet, the only
legless read in the set), gliding rather than standing, with a huge curved
GREAT-SCYTHE arcing overhead.

FACELESS is the gate: the hood interior is pure black emptiness — no eyes, no
orbs. Emptiness reads as more Death than any glow (Hollow Knight void / Cuphead
Devil). At most a single narrow vertical void-glow sliver sits DEEP in the hood
shadow at very low alpha; when in doubt, nothing.

Palette discipline is the separation lever: a sibling lich owns teal/cyan, so
this stays VOID-VIOLET dominant. The spectral pale-green is a THIN cold ACCENT
only — a 1px rim on the scythe's inner cutting edge and a faint underglow at the
smoke-dissolve hem. Total green is a few percent of the figure, never a focal
mass, never lime, never cyan.

The signature prop is a GREAT-SCYTHE that must later mirror into a vertical
PILLAR pair. The decision: the SNATH (the long straight shaft) is the pillar
body, and the curved blade rides the GAP-EDGE as a flourish — so a top/bottom
mirror reads as a clean vertical post with a hooked blade flourishing INTO the
gap, not a confusing horizontal claw.

Nothing under `game/` is touched; we import the real colour kit only. Headless + deterministic. Output: docs/epic_boss/reaper-shade/round_3.png.

    PYTHONPATH=. python tools/render_epic_reaper.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color


pygame.init()

# ── reaper-shade palette ──────────────────────────────────────────────────────
# Void black-violet DOMINATES; spectral pale-green is a THIN cold accent only;
# bone-white is reserved for the blade edge + skeletal grip. All desaturated and
# low-luminance so the green can never read as the clown's lime or the lich's
# cyan.
VOID        = (34, 28, 46)        # robe core — the dominant mass
VOID_DK     = (20, 16, 30)        # deepest folds / hood cavity rim
VOID_HEM    = (44, 36, 60)        # raised fold / shoulder catchlight (still dark)
SOUL        = (176, 236, 180)     # spectral soul-light — used SPARINGLY
SOUL_DIM    = (96, 140, 104)      # desaturated soul, for the wider inner glow
BONE        = (228, 224, 212)     # blade + skeletal fingers
BONE_DK     = (150, 146, 136)     # bone underside / blade spine shadow
SMOKE       = (52, 44, 70)        # dissolving-hem wisp (violet-grey, never grey)


# ── builder ───────────────────────────────────────────────────────────────────

def _blit_glow(surf, cx, cy, r, col, alpha):
    """A soft additive halo — used only for the faint soul-light bleed so the
    hood reads as lit-from-within without a bright disc. Kept tiny on purpose so
    violet stays dominant."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(4):
        rr = int(r * (1 - i / 4.0))
        a = int(alpha * (i + 1) / 4.0)
        pygame.draw.circle(g, (*col, a), (r, r), rr)
    surf.blit(g, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)


def _ramp_to_transparent(surf, x0, y0, w, h, ramp_top, ramp_bot):
    """Erase the bottom band of an already-drawn figure into a smooth alpha
    gradient, so the robe's base FADES OUT into the sky with no hard hem. Works by
    multiplying a top→bottom alpha ramp over the region (BLEND_RGBA_MULT keeps the
    colour, lowers the alpha), which sells the glide instead of a standing hem."""
    ramp = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        gy = y0 + y
        if gy <= ramp_top:
            a = 255
        elif gy >= ramp_bot:
            a = 0
        else:
            a = int(255 * (1 - (gy - ramp_top) / max(1, (ramp_bot - ramp_top))) ** 1.3)
        ramp.fill((255, 255, 255, a), (0, y, w, 1))
    surf.blit(ramp, (x0, y0), special_flags=pygame.BLEND_RGBA_MULT)


def _smoke_dissolve(surf, cx, base_y, width, ss, rng_seed=0):
    """The lower body breaking into wispy smoke instead of feet — the distinct
    LEGLESS read. A few (3–5) WISPY VERTICAL tendrils of decreasing opacity drift
    slightly outward below the faded robe base, so the silhouette trails off into
    nothing rather than ending in a fringed skirt. Drawn on a scratch so the alpha
    falloff composites cleanly under whatever sky sits behind."""
    import random
    rng = random.Random(rng_seed)
    h = int(90 * ss)
    scratch = pygame.Surface((width * 3, h), pygame.SRCALPHA)
    ox = width * 3 // 2
    # Five wispy tendrils that read as the body coming apart into rising smoke, not
    # tassels: each starts thin, sways, and DRIFTS OUTWARD as it descends so the
    # column frays wider and thinner toward the bottom, then vanishes to zero alpha.
    offsets = (-0.34, -0.16, 0.0, 0.18, 0.36)
    for i, spread in enumerate(offsets):
        x0 = ox + int(spread * width * 0.42)
        length = int(h * (0.62 + 0.38 * rng.random()))
        sway = rng.uniform(2.2, 4.0) * ss
        w0 = max(2, int((4.5 - 3.0 * abs(spread)) * ss))
        # Centre tendrils start a touch more opaque so the fray spreads from the
        # middle; all stay low so smoke never competes with the solid robe above.
        a0 = int(105 * (1 - abs(spread) * 0.7))
        prev = (x0, 0)
        steps = 18
        for s in range(1, steps + 1):
            ft = s / steps
            # Outward drift grows with depth (ft**1.4) → wisps splay apart at the
            # base; sway adds the organic curl of smoke.
            px = x0 + int(math.sin(ft * 2.6 + i) * sway * ft) \
                + int(spread * width * 0.34 * ft ** 1.4)
            py = int(length * ft)
            a = int(a0 * (1 - ft) ** 2.0)        # steeper falloff → fully gone at tip
            w = max(1, int(w0 * (1 - ft * 0.75)))
            col = lerp_color(VOID, SMOKE, ft)
            pygame.draw.line(scratch, (*col, a), prev, (px, py), w)
            prev = (px, py)
    surf.blit(scratch, (cx - ox, base_y))


def draw_reaper(surf, cx, feet_y, scale=1.0, ss=1):
    """The reaper-shade specter, head-to-smoke, built on its own geometry.

    Construction (all keyed off `H`, the hood-to-hem figure height, so the figure
    scales as one mass):
      - a tall draped ROBE column, narrow at the cowl, flaring slightly at the
        chest, then NOT resolving into a hem — its base is RAMPED to transparency
        and frays into vertical smoke tendrils (no feet, no hard hem);
      - a PEAKED, forward-drooping HOOD whose cavity is pure black EMPTINESS —
        FACELESS, no eyes; at most one faint vertical void-glow sliver set deep in
        the shadow at very low alpha;
      - one BONE skeletal hand emerging from a sleeve to grip the snath;
      - the GREAT-SCYTHE held: a long straight SNATH planted past the figure, a
      huge bone BLADE sweeping in an arc overhead, outlined in violet-black so it
      holds its silhouette on blue sky, with a 1px cold SOUL rim on the cutting
      edge as the sole green accent on the figure.
    `feet_y` is where the smoke dissolves to nothing (the glide line)."""
    H = int(300 * scale * ss)
    W = int(120 * scale * ss)
    top_y = feet_y - H

    # — Robe column: a tapered draped mass, widest at the chest, pinching toward
    #   the cowl and again toward the dissolving base. Built as a silhouette polygon
    #   so the violet body is one solid dark shape (the legibility carrier). The
    #   robe + its folds + the shoulder drape are drawn onto a dedicated scratch so
    #   the bottom band can be RAMPED to transparency as one mass — selling the
    #   legless glide rather than a flat skirt with a hard hem.
    chest_y = top_y + int(H * 0.30)
    waist_y = top_y + int(H * 0.68)
    # Carry the robe LOWER (no early hem cut) so its base is what fades out; the
    # alpha ramp, not a polygon edge, decides where the figure stops.
    base_y  = feet_y - int(H * 0.02)
    cowl_w  = int(W * 0.30)
    chest_w = int(W * 0.52)
    waist_w = int(W * 0.40)
    base_w  = int(W * 0.34)

    robe = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    body = [
        (cx - cowl_w, top_y + int(H * 0.10)),
        (cx - chest_w, chest_y),
        (cx - waist_w, waist_y),
        (cx - base_w, base_y),
        (cx + base_w, base_y),
        (cx + waist_w, waist_y),
        (cx + chest_w, chest_y),
        (cx + cowl_w, top_y + int(H * 0.10)),
    ]
    pygame.draw.polygon(robe, VOID, body)
    pygame.draw.polygon(robe, VOID_DK, body, max(1, int(2 * ss)))

    # Vertical drape folds — a few long dark grooves so the robe reads as cloth,
    # not a flat blob, without lifting the value (folds stay at/under VOID).
    for fx in (-0.55, -0.18, 0.18, 0.55):
        x = cx + int(fx * chest_w * 1.2)
        pygame.draw.line(robe, VOID_DK, (x, chest_y + int(8 * ss)),
                         (x + int(fx * 6 * ss), base_y), max(1, int(1.6 * ss)))
    # One raised lit fold catch on the chest so the cloth has a hint of form.
    pygame.draw.line(robe, VOID_HEM, (cx - int(chest_w * 0.2), chest_y),
                     (cx - int(waist_w * 0.1), waist_y), max(1, int(2 * ss)))

    # — Shoulders / cowl drape: two dark cloth lobes pulled up to the hood so the
    #   silhouette shoulders read broad and ominous, sloping down off the cowl.
    for s in (-1, 1):
        sh = [
            (cx + s * cowl_w, top_y + int(H * 0.11)),
            (cx + s * int(W * 0.50), top_y + int(H * 0.20)),
            (cx + s * chest_w, chest_y),
            (cx + s * int(chest_w * 0.55), top_y + int(H * 0.22)),
        ]
        pygame.draw.polygon(robe, VOID, sh)
        pygame.draw.polygon(robe, VOID_DK, sh, max(1, int(1.6 * ss)))

    # Ramp the bottom ~28% of the robe to FULL transparency so the base FADES into
    # the sky with NO hard hem line and NO fringed-skirt read. The ramp begins well
    # above the waist and reaches zero alpha before the polygon base, so the body
    # is already gone where a hem would otherwise sit — the figure has no edge to
    # stand on. A steep exponent keeps the upper robe solid then drops fast.
    ramp_top = top_y + int(H * 0.72)
    ramp_bot = top_y + int(H * 0.94)
    _ramp_to_transparent(robe, 0, ramp_top, robe.get_width(),
                          robe.get_height() - ramp_top, ramp_top, ramp_bot)
    surf.blit(robe, (0, 0))

    # — The dissolving smoke tendrils, rising/trailing from the faded base: a few
    #   wispy vertical wisps of decreasing opacity that drift slightly outward, so
    #   the silhouette trails off into nothing instead of ending in tassels.
    _smoke_dissolve(surf, cx, ramp_top + int(H * 0.02), W, ss, rng_seed=7)
    # — Faint cold SOUL underglow pooled where the robe dissolves — the figure's
    #   ONLY green besides the blade rim. Deliberately tiny + low so it never blooms
    #   into a focal mass: a thin cold breath at the hem, not a lamp.
    _blit_glow(surf, cx, ramp_bot - int(H * 0.01), int(W * 0.34), SOUL_DIM, 12)

    # — PEAKED HOOD: a forward-drooping cowl, the strongest silhouette hook. Built
    #   as a pointed cloth shape leaning slightly toward the held scythe, with a
    #   deep VOID cavity for the faceless interior.
    peak_y  = top_y - int(H * 0.02)
    hood_top = top_y + int(H * 0.02)
    hood = [
        (cx - int(W * 0.22), top_y + int(H * 0.18)),    # left jaw of the cowl
        (cx - int(W * 0.26), top_y + int(H * 0.09)),
        (cx - int(W * 0.04), peak_y),                   # the peak, leaning right
        (cx + int(W * 0.10), peak_y - int(H * 0.02)),   # forward droop tip
        (cx + int(W * 0.30), top_y + int(H * 0.10)),
        (cx + int(W * 0.24), top_y + int(H * 0.20)),    # right jaw
        (cx, top_y + int(H * 0.26)),                    # chin of the cowl
    ]
    pygame.draw.polygon(surf, VOID, hood)
    pygame.draw.polygon(surf, VOID_DK, hood, max(1, int(2 * ss)))

    # Hood cavity: pure black EMPTINESS — the FACELESS read. NO eyes, NO orbs.
    # A tall near-black void recessed under the cowl brow so the hood reads as a
    # bottomless hollow, not a mask. Emptiness here is the whole point — Death is
    # the absence of a face (Hollow Knight void / Cuphead Devil). The cavity is a
    # vertical slot, NOT a round socket, so nothing can read as an eye.
    cav_cx, cav_cy = cx + int(W * 0.01), top_y + int(H * 0.175)
    cav = pygame.Rect(0, 0, int(W * 0.26), int(H * 0.15))
    cav.center = (cav_cx, cav_cy)
    pygame.draw.ellipse(surf, VOID_DK, cav)
    pygame.draw.ellipse(surf, (5, 3, 9), cav.inflate(-int(5 * ss), -int(5 * ss)))
    # The only light in the hood is a faint VIOLET cloth rim along the upper brow
    # arc — it shapes the mouth of the cowl without lighting the void inside. Kept
    # violet (never green) so the green budget stays wholly on the blade.
    pygame.draw.arc(surf, VOID_HEM, cav.inflate(int(2 * ss), int(2 * ss)),
                    math.radians(35), math.radians(145), max(1, int(1.4 * ss)))
    # No interior glow at all: the hood is a pure black VOID. Any green sliver here
    # — however dim — out-contrasts the rest of the figure inside the dark slot and
    # reads as a single glowing eye (a cyclops face, MORE of a face than two orbs).
    # Emptiness is the faceless read; green earns full intensity only on the blade.

    # — GREAT-SCYTHE, held across the body. The SNATH is the future pillar body:
    #   a long straight bone-grey shaft running top-to-bottom on the figure's left,
    #   gripped by a skeletal hand. The huge curved BLADE sweeps overhead as the
    #   gap-edge FLOURISH.
    snath_x = cx - int(W * 0.62)
    snath_top = top_y - int(H * 0.26)
    snath_bot = feet_y + int(H * 0.02)
    sw = max(2, int(5 * ss))
    # Shaft: dark-cored with a bone rail so it reads round and holds value.
    pygame.draw.line(surf, VOID_DK, (snath_x, snath_top), (snath_x, snath_bot), sw + max(1, int(2 * ss)))
    pygame.draw.line(surf, BONE_DK, (snath_x, snath_top), (snath_x, snath_bot), sw)
    pygame.draw.line(surf, BONE, (snath_x - int(1 * ss), snath_top),
                     (snath_x - int(1 * ss), snath_bot), max(1, int(2 * ss)))
    # A binding collar where the blade socket meets the snath.
    pygame.draw.circle(surf, VOID_DK, (snath_x, snath_top + int(6 * ss)), max(3, int(5 * ss)))
    pygame.draw.circle(surf, BONE_DK, (snath_x, snath_top + int(6 * ss)), max(2, int(3.5 * ss)))

    # The BLADE: a great curved bone hook arcing up + across from the snath top,
    # sweeping rightward overhead — the second unmistakable silhouette hook. Built
    # as a filled crescent (outer arc + inner arc) so it reads as a solid scythe
    # blade, with a hairline SOUL gleam tracing the cutting edge.
    bx, by = snath_x, snath_top + int(4 * ss)
    outer, inner = [], []
    span = int(W * 1.15)
    rise = int(H * 0.30)
    for i in range(25):
        t = i / 24.0
        # A swept arc bowing up then curling forward to a tapered point.
        ax = bx + int(span * t)
        ay = by - int(rise * math.sin(t * math.pi * 0.92))
        thick = (1 - t) * int(W * 0.16) + int(3 * ss)
        outer.append((ax, ay - thick))   # blunt back (spine) of the blade
        inner.append((ax, ay))           # concave cutting edge facing the figure
    blade = outer + list(reversed(inner))
    pygame.draw.polygon(surf, BONE, blade)
    # FULL-blade violet-black outline so the bone arc keeps its silhouette on the
    # bright blue day sky — without it the pale blade washes out against the sky.
    pygame.draw.polygon(surf, VOID_DK, blade, max(2, int(2.4 * ss)))
    # Spine shadow along the back of the blade for form.
    pygame.draw.lines(surf, BONE_DK, False, [(p[0], p[1] + int(3 * ss)) for p in outer],
                      max(1, int(2 * ss)))
    # The figure's ONLY scythe green: a 1px cold SOUL rim on the INNER (concave)
    # cutting edge — a thin spectral gleam, never a focal mass.
    pygame.draw.lines(surf, SOUL, False, inner, max(1, int(1.2 * ss)))

    # — Skeletal BONE HAND gripping the snath at chest height (one strong shape +
    #   a couple of dark grooves; anatomy fizzes small, so keep it sparse).
    hx, hy = snath_x, chest_y + int(H * 0.02)
    # Wrist/sleeve cuff (void cloth) the hand emerges from.
    pygame.draw.polygon(surf, VOID, [
        (cx - chest_w + int(4 * ss), chest_y + int(6 * ss)),
        (hx + int(10 * ss), hy - int(8 * ss)),
        (hx + int(12 * ss), hy + int(12 * ss)),
        (cx - waist_w + int(2 * ss), waist_y - int(6 * ss)),
    ])
    # Palm + four bony fingers curling around the front of the shaft.
    pygame.draw.circle(surf, BONE_DK, (hx + int(2 * ss), hy), max(3, int(5 * ss)))
    pygame.draw.circle(surf, BONE, (hx + int(1 * ss), hy - int(1 * ss)), max(2, int(3.5 * ss)))
    for k in range(4):
        fy = hy - int(6 * ss) + k * int(4 * ss)
        pygame.draw.line(surf, BONE, (hx - int(3 * ss), fy), (hx + int(4 * ss), fy + int(1 * ss)),
                         max(1, int(2 * ss)))
        pygame.draw.line(surf, BONE_DK, (hx - int(3 * ss), fy + int(1 * ss)),
                         (hx + int(4 * ss), fy + int(2 * ss)), max(1, int(1 * ss)))

    # Deliberately NO drifting soul embers and NO robe dots: green is spent ONLY on
    # the blade's inner-edge rim and the faint dissolve-hem underglow, so the total
    # green stays a few percent of the figure and violet stays dominant.


# ── pillar-fit thumbnail ──────────────────────────────────────────────────────

def draw_snath_pillar(surf, cx, top, bot, w, ss, *, flip):
    """Prove the SNATH-as-pillar decision: the straight shaft is the vertical post
    that runs the full obstacle height; the curved blade is a GAP-EDGE FLOURISH at
    the inner (gap) end only — a readable hooked crescent flourishing INTO the gap,
    NOT a horizontal claw. `flip` mirrors it for the opposing (top vs bottom) pier
    so a top/bottom pair reads as one matched vertical obstacle."""
    # Shaft: full-height bone-grey post, dark-cored.
    pygame.draw.line(surf, VOID_DK, (cx, top), (cx, bot), w + max(1, int(2 * ss)))
    pygame.draw.line(surf, BONE_DK, (cx, top), (cx, bot), w)
    pygame.draw.line(surf, BONE, (cx - int(1 * ss), top), (cx - int(1 * ss), bot), max(1, int(2 * ss)))
    # Binding collars banding the post so it reads as a worked snath, not a stick.
    for cy in (top + int((bot - top) * 0.30), top + int((bot - top) * 0.62)):
        pygame.draw.circle(surf, VOID_DK, (cx, cy), max(3, int(4 * ss)))
        pygame.draw.circle(surf, BONE_DK, (cx, cy), max(2, int(2.6 * ss)))

    # The blade flourish at the GAP end (here the TOP end before any flip). It
    # curls FORWARD over the gap as a crescent hook — the same blade as the held
    # figure, now reading as a finial that frames the gap edge.
    gap_y = top
    bx = cx
    outer, inner = [], []
    span = int(34 * ss)
    rise = int(26 * ss)
    for i in range(20):
        t = i / 19.0
        ax = bx + int(span * t)
        ay = gap_y - int(rise * math.sin(t * math.pi * 0.9))
        thick = (1 - t) * int(9 * ss) + int(2 * ss)
        outer.append((ax, ay - thick))
        inner.append((ax, ay))
    blade = outer + list(reversed(inner))

    work = surf
    pygame.draw.polygon(work, BONE, blade)
    pygame.draw.polygon(work, BONE_DK, blade, max(1, int(1.6 * ss)))
    pygame.draw.lines(work, SOUL, False, outer, max(1, int(1.2 * ss)))
    # Socket collar where the blade meets the shaft top.
    pygame.draw.circle(work, VOID_DK, (cx, gap_y + int(4 * ss)), max(3, int(4 * ss)))
    pygame.draw.circle(work, BONE_DK, (cx, gap_y + int(4 * ss)), max(2, int(2.6 * ss)))


# ── sheet composition ─────────────────────────────────────────────────────────

def _sky_panel(w, h, night):
    """The day/night sky gradient using the GAME's real biome keyframes (DAY and
    NIGHT from game/biome.py), so the reaper is judged on the actual backdrop it
    must read on — a bright blue day and a deep blue night — not a forgiving card."""
    surf = pygame.Surface((w, h))
    if night:
        top, bot = (5, 8, 30), (35, 55, 115)          # biome NIGHT keyframe
    else:
        top, bot = (40, 110, 200), (170, 220, 245)    # biome DAY keyframe
    for y in range(h):
        pygame.draw.line(surf, lerp_color(top, bot, y / h), (0, y), (w, y))
    return surf


def main():
    ss = 3
    PANEL_W, PANEL_H = 460, 720
    ground_y = PANEL_H - 90
    GAP = 30
    THUMB_W = 300
    SHEET_W = PANEL_W * 2 + GAP * 3 + THUMB_W
    SHEET_H = PANEL_H + 120

    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((26, 24, 32))

    title_f = pygame.font.SysFont("dejavusans", 30, bold=True)
    label_f = pygame.font.SysFont("dejavusans", 19, bold=True)
    note_f = pygame.font.SysFont("dejavusans", 14)

    sheet.blit(title_f.render("EPIC EVENT-BOSS  —  reaper-shade  —  round 3", True, (236, 236, 240)), (28, 22))
    sheet.blit(note_f.render(
        "Death itself: FACELESS peaked HOOD (no eyes), robe DISSOLVING into smoke (no feet), great-scythe overhead. "
        "Void-violet dominant; spectral green a thin accent only.",
        True, (170, 170, 184)), (28, 60))

    # Two big panels: day + night, full boss scale over a ground line.
    for i, (night, name) in enumerate([(False, "DAY SKY"), (True, "NIGHT SKY")]):
        px = GAP + i * (PANEL_W + GAP)
        py = 92
        # Render the specter at ss into an oversized scratch, then downscale for AA.
        big = pygame.Surface((PANEL_W * ss, PANEL_H * ss), pygame.SRCALPHA)
        draw_reaper(big, int(PANEL_W * 0.50 * ss), int(ground_y * ss), scale=0.78, ss=ss)
        small = pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))

        panel = _sky_panel(PANEL_W, PANEL_H, night)
        # Ground band + a FAINT diffuse smoke pool (not a hard cast shadow): the
        # specter glides, so there is no crisp standing-shadow to imply feet — just
        # a soft low-alpha smudge where the dissolving robe meets the ground.
        pygame.draw.rect(panel, (40, 34, 30) if not night else (22, 20, 30),
                         (0, ground_y, PANEL_W, PANEL_H - ground_y))
        pygame.draw.line(panel, (60, 52, 44) if not night else (50, 44, 58),
                         (0, ground_y), (PANEL_W, ground_y), 2)
        pool = pygame.Surface((PANEL_W, 60), pygame.SRCALPHA)
        for rr, aa in ((150, 14), (110, 18), (70, 22)):
            pygame.draw.ellipse(pool, (8, 6, 14, aa),
                                (PANEL_W // 2 - rr, 30 - 8, rr * 2, 24))
        panel.blit(pool, (0, ground_y - 26))
        panel.blit(small, (0, 0))

        sheet.blit(panel, (px, py))
        pygame.draw.rect(sheet, (70, 64, 80), (px, py, PANEL_W, PANEL_H), 1)
        lab = label_f.render(name, True, (236, 236, 240))
        sheet.blit(lab, (px + (PANEL_W - lab.get_width()) // 2, py + PANEL_H + 8))

    # MANDATORY 1x AT-SCALE insets — the figure at true gameplay pixel size on the
    # REAL day AND night skies (not a white card), so the faceless hood, the
    # two-hook (peaked hood + scythe-arc) silhouette, and the smoke-dissolve base
    # are all judged at the size the player actually sees. Two stacked insets sit
    # over the top-left of the day panel; a solid-black silhouette beside them
    # isolates the two-hook read.
    ins_w, ins_h = 120, 200
    ins_scale = 0.36           # ~ true 1x boss footprint within a 360x640 canvas
    ix = GAP + 6
    iy = 92 + 6
    for j, night in enumerate((False, True)):
        big_i = pygame.Surface((ins_w * ss, ins_h * ss), pygame.SRCALPHA)
        draw_reaper(big_i, int(ins_w * 0.52 * ss), int((ins_h - 8) * ss),
                    scale=ins_scale, ss=ss)
        small_i = pygame.transform.smoothscale(big_i, (ins_w, ins_h))
        sky_i = _sky_panel(ins_w, ins_h, night)
        sky_i.blit(small_i, (0, 0))
        frame = pygame.Surface((ins_w + 12, ins_h + 26), pygame.SRCALPHA)
        frame.fill((20, 18, 26, 235))
        frame.blit(sky_i, (6, 22))
        frame.blit(note_f.render("1x  " + ("NIGHT" if night else "DAY"), True,
                                 (220, 222, 230)), (8, 3))
        pygame.draw.rect(frame, (90, 84, 104), (6, 22, ins_w, ins_h), 1)
        sheet.blit(frame, (ix, iy + j * (ins_h + 30)))

    # Solid-black silhouette beside the insets — strips colour so only the two-hook
    # shape (peaked hood + overhead scythe arc) is left to judge.
    sil_w, sil_h = 110, 230
    tmp = pygame.Surface((sil_w * ss, sil_h * ss), pygame.SRCALPHA)
    draw_reaper(tmp, int(sil_w * 0.52 * ss), int((sil_h - 12) * ss), scale=0.40, ss=ss)
    mask = pygame.mask.from_surface(tmp)
    sil = mask.to_surface(setcolor=(14, 12, 18, 255), unsetcolor=(0, 0, 0, 0))
    sil_small = pygame.transform.smoothscale(sil, (sil_w, sil_h))
    sframe = pygame.Surface((sil_w + 12, sil_h + 26), pygame.SRCALPHA)
    sframe.fill((228, 230, 236, 235))
    sframe.blit(sil_small, (6, 22))
    sframe.blit(note_f.render("silhouette", True, (40, 40, 48)), (8, 3))
    sheet.blit(sframe, (ix + ins_w + 22, iy))

    # — Pillar-fit thumbnail column on the right: a TOP + BOTTOM snath pillar pair
    #   over a sky strip, proving the mirror reads as a vertical obstacle.
    tx = GAP * 2 + PANEL_W * 2 + GAP
    ty = 92
    th = PANEL_H
    tw = THUMB_W
    thumb = _sky_panel(tw, th, False)
    # A gameplay gap: top pier hangs from the ceiling, bottom pier rises from floor.
    gap_top = int(th * 0.42)
    gap_bot = int(th * 0.62)
    col_x = tw // 2
    post_w = max(3, int(6 * ss))

    big_t = pygame.Surface((tw * ss, th * ss), pygame.SRCALPHA)
    # Bottom pier: post rises from the ground, blade flourishes UP into the gap.
    draw_snath_pillar(big_t, col_x * ss, gap_bot * ss, (th - 10) * ss, post_w, ss, flip=False)
    # Top pier: a mirror — post hangs from the ceiling, blade flourishes DOWN into
    # the gap. Built by drawing the same pillar then flipping the whole scratch.
    top_scratch = pygame.Surface((tw * ss, th * ss), pygame.SRCALPHA)
    draw_snath_pillar(top_scratch, col_x * ss, (th - gap_top) * ss, (th - 10) * ss, post_w, ss, flip=False)
    top_scratch = pygame.transform.flip(top_scratch, False, True)
    big_t.blit(top_scratch, (0, 0))

    small_t = pygame.transform.smoothscale(big_t, (tw, th))
    thumb.blit(small_t, (0, 0))
    # Mark the gap lane.
    pygame.draw.line(thumb, (90, 160, 110), (8, gap_top), (tw - 8, gap_top), 1)
    pygame.draw.line(thumb, (90, 160, 110), (8, gap_bot), (tw - 8, gap_bot), 1)
    thumb.blit(note_f.render("flap gap", True, (40, 80, 50)), (10, gap_top + 4))

    sheet.blit(thumb, (tx, ty))
    pygame.draw.rect(sheet, (70, 64, 80), (tx, ty, tw, th), 1)
    lab = label_f.render("PILLAR-FIT (snath=post)", True, (236, 236, 240))
    sheet.blit(lab, (tx + (tw - lab.get_width()) // 2, ty + th + 8))
    sheet.blit(note_f.render("blade = gap-edge flourish, not a claw", True, (170, 170, 184)),
               (tx + 4, ty + th + 32))

    out = "/home/user/skybit/docs/epic_boss/reaper-shade/round_3.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()

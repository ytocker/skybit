"""Round-2 render for the FUSED BONE-PLATE SLAB clown-event column.

The 5th column logic: an honestly SOLID fortress wall built from tessellated
cranial plates / jammed-together skulls — a charnel WALL, not a stack. No tier
rhythm, no taper: an unbroken mortared mass whose ONLY structure is the plate
mosaic, capped at Pip's gap by one oversized boss-skull KEYSTONE.

Round-2 rework (art-director punch list):
  1. Killed the horizontal banding — the per-plate dark-core band created
     regular light/dark courses (a tier rhythm). The backing is now flat
     warm-ivory with only a very-low-frequency VERTICAL value drift; no
     horizontal courses exist anywhere.
  2. Each plate is filled with ONE flat value from a tight 3-step warm-ivory
     ramp (light / mid / shadow). The mosaic reads as solid tessellated MASS by
     VALUE — the value blocks survive the downscale; lines alone don't.
  3. Plates enlarged to ~22px (≈2.5-3 across the 58px width) — fewer, chunkier
     facets instead of a fine triangulated net.
  4. Gold seams halved and broken into short glints (≤2 plate-edges). Most
     grout is recessed dark bone-shadow; gold is an occasional accent only —
     no continuous gilt trellis.
  5. Void test protected: recessed grout stays clearly darker than sky, never
     drops to sky value, never touches the keyline edge.
  6. Keystone suture cleaned to a carved symmetric brow (dark core under gold).

Built in the locked bone-roster idiom (warm-ivory bone, ink keyline, dark-core/
flat/rim-sheen triad, gold thin-accent seams, sparing faceted cyan/purple gems)
and supersampled → smoothscaled with an alpha-grown 1px silhouette outline.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import math
import random
import pygame

pygame.init()

# Bone-roster palette (the locked batch2 house style this set inherits).
INK     = (28, 22, 30)
BONE    = (228, 222, 206)
BONE_DK = (150, 144, 128)
BONE_HI = (250, 247, 236)
GOLD    = (250, 205, 72)
GOLD_HI = (255, 236, 150)
GOLD_DK = (176, 130, 30)
CYAN    = (120, 214, 222)
CYAN_HI = (224, 252, 252)
PURPLE  = (158, 120, 214)
PURPLE_HI = (224, 200, 252)

# Tight 3-step warm-ivory value ramp for the plate fills. The mosaic reads as
# solid tessellated mass by VALUE, not line — these survive the downscale.
PLATE_LIGHT  = (236, 230, 214)
PLATE_MID    = (214, 207, 190)
PLATE_SHADOW = (190, 182, 164)
# Recessed grout: a darker warm-grey, clearly darker than sky but never sky-dark
# and never black — depth between fused plates without opening a hole.
GROUT  = (118, 110, 100)

PW = 58


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _grow_outline(surf):
    """Alpha-grown 1px ink silhouette (house finishing pass): dilate the alpha
    mask one ring and paint the new edge ink so the slab carves cleanly out of a
    busy sky regardless of where its plates meet the column edge."""
    mask = pygame.mask.from_surface(surf, 8)
    outline = mask.outline()
    if len(outline) > 1:
        pygame.draw.lines(surf, INK, True, outline, 1)
    return surf


# ── The tessellated cranial-plate pavement ────────────────────────────────────
# A coarse jittered point lattice whose cells become chunky fused plates. Coarse
# on purpose — fine plates collapse to a wireframe net at 1x, so the plate count
# is kept low (~2.5-3 across) and each cell is carried by a FLAT VALUE, not lines.

def _plate_lattice(x0, x1, y0, y1, step, jitter, rng):
    """A jittered grid of points; alternate rows offset so the cells read as
    irregular jammed plates, not a tidy brick course. Outer ring is clamped to
    the body edge so plates fill the full 58px width edge-to-edge (no gutter)."""
    cols = max(2, round((x1 - x0) / step))
    rows = max(2, round((y1 - y0) / step))
    pts = {}
    for r in range(rows + 1):
        for c in range(cols + 1):
            gx = x0 + c * (x1 - x0) / cols
            gy = y0 + r * (y1 - y0) / rows
            jx = 0 if (c == 0 or c == cols) else rng.uniform(-jitter, jitter)
            jy = 0 if (r == 0 or r == rows) else rng.uniform(-jitter, jitter)
            # Stagger interior rows so quads break into a charnel weave. The
            # offset is small + jittered so no clean horizontal course survives.
            sx = (step * 0.34) if (r % 2 and 0 < c < cols) else 0.0
            pts[(r, c)] = (gx + jx + sx, gy + jy)
    return pts, rows, cols


def _plate_value(gx, gy, bw, H, rng):
    """Pick ONE flat fill from the 3-step ramp for a whole plate. Selection is
    spatially incoherent (hashed jitter) so NO horizontal course of equal value
    forms — but biased by a very-low-frequency VERTICAL drift (darker toward the
    bottom of the column) so the mass reads carved, never striped."""
    # Low-frequency vertical drift only: a single smooth gradient over the whole
    # column, NOT a per-row band. This is the one permitted value trend.
    vdrift = gy / max(1.0, H)                      # 0 at top → 1 at bottom
    roll = rng.random() * 0.62 + vdrift * 0.38     # bias darker low, but noisy
    if roll < 0.40:
        base = PLATE_LIGHT
    elif roll < 0.74:
        base = PLATE_MID
    else:
        base = PLATE_SHADOW
    # A tiny per-plate tint so adjacent equal-step plates still separate slightly.
    return _shade(base, rng.randint(-5, 5))


def _draw_plate(surf, poly, fill, ss):
    """One fused cranial plate: a FLAT value block (the mass) with a single
    short top-left rim-sheen stroke (the roster's top-left light). No interior
    dark-core band — the value ramp across plates carries the carved depth, so
    no per-plate gradient can re-introduce horizontal courses."""
    ipoly = [(int(p[0]), int(p[1])) for p in poly]
    pygame.draw.polygon(surf, fill, ipoly)

    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    left, right = min(xs), max(xs)
    top, bot = min(ys), max(ys)
    cx = (left + right) * 0.5
    cy = (top + bot) * 0.5

    # Top-left rim sheen: brighten only the upper-left edges of the plate so the
    # light reads from the top-left across the whole wall (house triad).
    n = len(poly)
    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]
        mx, my = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
        if my < cy and mx < cx + (right - left) * 0.12:
            pygame.draw.line(surf, _shade(fill, 26),
                             (int(a[0]), int(a[1])), (int(b[0]), int(b[1])),
                             max(1, int(1.1 * ss)))


def _draw_seams(surf, edges, ss, rng):
    """Trace the tessellation. MOST seams are recessed bone-shadow grout (depth
    between fused plates, ivory stays the dominant value). Gold appears ONLY as
    occasional SHORT glints — never a continuous run — so it reads as a sparse
    accent catching the light, not a gilt trellis."""
    for (a, b) in edges:
        # Recessed grout core for every seam: darker warm-grey, kept off the
        # sky value so jitter never opens a hole. A 1px ink hairline inside it
        # sells the deep crack.
        pygame.draw.line(surf, GROUT,
                         (int(a[0]), int(a[1])), (int(b[0]), int(b[1])),
                         max(2, int(1.8 * ss)))
        pygame.draw.line(surf, _shade(GROUT, -34),
                         (int(a[0]), int(a[1])), (int(b[0]), int(b[1])),
                         max(1, int(ss)))

    # Gold only as short glints: pick a sparse subset of edges and gild just a
    # fragment of each (a midpoint stub), so no two gilt edges chain into a run.
    for (a, b) in edges:
        if rng.random() > 0.16:        # ~1 in 6 edges carries any gold at all
            continue
        # Gild a short central fragment of this single edge — ≤ one edge long,
        # so it cannot read as a continuous diagonal seam.
        t0 = rng.uniform(0.18, 0.34)
        t1 = t0 + rng.uniform(0.28, 0.40)
        ga = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
        gb = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
        pygame.draw.line(surf, GOLD_DK,
                         (int(ga[0]), int(ga[1])), (int(gb[0]), int(gb[1])),
                         max(1, int(1.3 * ss)))
        pygame.draw.line(surf, GOLD,
                         (int(ga[0]), int(ga[1])), (int(gb[0]), int(gb[1])),
                         max(1, int(ss)))


def _gem(surf, cx, cy, r, ss, col, col_hi):
    """A faceted wisdom gem: ink-rimmed kite with a bright top-left facet spark."""
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in pts])
    inner = [(cx, cy - r + ss), (cx + r - ss, cy), (cx, cy + r - ss), (cx - r + ss, cy)]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in inner])
    pygame.draw.line(surf, _shade(col, -50), (int(cx), int(cy)), (int(cx), int(cy + r - ss)), max(1, int(ss)))
    pygame.draw.circle(surf, col_hi, (int(cx - r * 0.3), int(cy - r * 0.3)), max(1, int(r * 0.32)))


def _boss_keystone(surf, cx, cy, R, ss, *, flip):
    """The oversized boss-skull KEYSTONE that caps the slab at Pip's gap: a
    cranium wider than the column plates, gem-eyed, mortared INTO the wall with a
    gold keystone-wedge frame so it reads as set INTO the mass, not perched on it.
    `flip` orients the jaw toward the gap (jaw faces the gap, crown into the wall).

    KEPT INTACT per the brief (best focal in the set): skull silhouette, jaw
    orientation, cyan+purple gem sockets. Only the suture is reworked."""
    sgn = 1 if not flip else -1     # +1: jaw downward (top half); -1: jaw upward (bottom half)

    # A bone keystone wedge socket framing the boss into the wall, jaw-side wider:
    # an ivory block (so the boss stays seated in the SAME bone mass) with a thin
    # gold outline tracing the wedge — gold stays a hairline accent, not a frame.
    wedge = [
        (cx - R * 1.18, cy - sgn * R * 0.55),
        (cx + R * 1.18, cy - sgn * R * 0.55),
        (cx + R * 0.92, cy + sgn * R * 1.15),
        (cx - R * 0.92, cy + sgn * R * 1.15),
    ]
    pygame.draw.polygon(surf, _shade(BONE, -22), [(int(x), int(y)) for x, y in wedge])
    pygame.draw.polygon(surf, GOLD_DK, [(int(x), int(y)) for x, y in wedge], max(1, int(1.6 * ss)))
    pygame.draw.polygon(surf, GOLD, [(int(x), int(y)) for x, y in wedge], max(1, int(ss)))
    # Bright keystone rim along the wall-side (away from gap) so it seats INTO the slab.
    pygame.draw.line(surf, GOLD_HI,
                     (int(cx - R * 1.16), int(cy - sgn * R * 0.53)),
                     (int(cx + R * 1.16), int(cy - sgn * R * 0.53)), max(1, int(1.4 * ss)))

    # Cranium dome.
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(R) + max(1, int(ss)))
    pygame.draw.circle(surf, BONE, (int(cx), int(cy)), int(R))
    # Dark-core lower cranium + top-left dome sheen.
    prev = surf.get_clip()
    surf.set_clip(pygame.Rect(int(cx - R), int(cy), int(2 * R), int(R) + 2))
    pygame.draw.circle(surf, _shade(BONE, -30), (int(cx), int(cy)), int(R))
    surf.set_clip(prev)
    pygame.draw.circle(surf, BONE_HI, (int(cx - R * 0.34), int(cy - R * 0.34)), int(R * 0.34))

    # The cranial suture: a SYMMETRIC carved brow arch over the eye sockets. A
    # dark-core shadow under a gold hairline so it reads as a carved suture, not
    # a stray scribble (round-1 had a single thin wandering gold line).
    brow_y = cy - R * 0.30
    brow = [(cx - R * 0.66, brow_y + R * 0.10),
            (cx - R * 0.30, brow_y - R * 0.14),
            (cx,            brow_y - R * 0.20),
            (cx + R * 0.30, brow_y - R * 0.14),
            (cx + R * 0.66, brow_y + R * 0.10)]
    ibrow = [(int(x), int(y)) for x, y in brow]
    # Dark shadow core sits just below the gold so the suture reads recessed.
    pygame.draw.lines(surf, _shade(BONE, -50), False,
                      [(x, y + max(1, int(1.4 * ss))) for x, y in ibrow], max(1, int(1.8 * ss)))
    pygame.draw.lines(surf, GOLD_DK, False, ibrow, max(1, int(1.7 * ss)))
    pygame.draw.lines(surf, GOLD, False, ibrow, max(1, int(ss)))

    # Gem eye sockets — the sparing cyan/purple wisdom gems live HERE (keystone only).
    ex = R * 0.46
    ey = cy - sgn * R * 0.02
    for s, col, hi in ((-1, CYAN, CYAN_HI), (1, PURPLE, PURPLE_HI)):
        socket = (int(cx + s * ex), int(ey))
        pygame.draw.circle(surf, INK, socket, int(R * 0.30))
        pygame.draw.circle(surf, _shade(INK, 6), socket, int(R * 0.30), max(1, int(ss)))
        _gem(surf, socket[0], socket[1], int(R * 0.24), ss, col, hi)

    # A small triangular nasal void below the eyes (toward the crown side).
    nz = cy - sgn * R * 0.40
    pygame.draw.polygon(surf, INK, [
        (int(cx), int(nz)),
        (int(cx - R * 0.12), int(nz + sgn * R * 0.22)),
        (int(cx + R * 0.12), int(nz + sgn * R * 0.22)),
    ])

    # The boss JAW — a toothed grin facing the gap, the silhouette tell at scale.
    jy = cy + sgn * R * 0.62
    jaw = pygame.Rect(int(cx - R * 0.78), int(min(jy, jy + sgn * R * 0.6)),
                      int(R * 1.56), int(R * 0.6))
    pygame.draw.rect(surf, INK, jaw.inflate(int(ss), int(ss)), border_radius=int(R * 0.22))
    pygame.draw.rect(surf, BONE, jaw, border_radius=int(R * 0.22))
    pygame.draw.rect(surf, _shade(BONE, -28),
                     (jaw.x, jaw.y + jaw.h // 2, jaw.w, jaw.h // 2),
                     border_radius=int(R * 0.18))
    for i in range(-3, 4):
        tx = int(cx + i * R * 0.22)
        pygame.draw.line(surf, INK, (tx, jaw.y + 1), (tx, jaw.bottom - 1), max(1, int(ss)))


def _build_slab(height_px, ss, *, flip, seed):
    """Render one slab half (top OR bottom) at supersample `ss`, with its boss
    keystone seated at the gap-facing end. Returns the smoothscaled, outlined
    PW-wide surface."""
    rng = random.Random(seed)
    bw = PW * ss
    H = max(1, int(height_px)) * ss
    surf = pygame.Surface((bw, H), pygame.SRCALPHA)

    x0, x1 = 0, bw
    boss_R = PW * 0.52 * ss
    boss_band = int(boss_R * 2.1)

    if not flip:
        # TOP half: plates fill from the ceiling down; keystone caps the bottom.
        py0, py1 = 0, H - boss_band
        boss_cy = H - boss_R * 1.05
        boss_flip = False
    else:
        # BOTTOM half: keystone caps the top; plates fill below it to the ground.
        py0, py1 = boss_band, H
        boss_cy = boss_R * 1.05
        boss_flip = True

    # Solid backing fill across the WHOLE body first so any seam jitter never
    # opens a hole to the sky — this is the "honest solid mass" guarantee. A flat
    # warm-ivory with ONLY a very-low-frequency vertical drift (no horizontal
    # courses): one smooth top→bottom darkening, the single permitted trend.
    for y in range(H):
        t = y / max(1, H)
        c = (int(PLATE_MID[0] - 18 * t),
             int(PLATE_MID[1] - 18 * t),
             int(PLATE_MID[2] - 16 * t))
        pygame.draw.line(surf, c, (0, y), (bw, y))

    # Chunky plates: ~22px true (≈2.5-3 across the 58px width). Fewer, bigger
    # facets that survive the downscale as value blocks instead of mushing.
    step = 22 * ss
    jitter = 4.2 * ss
    pts, rows, cols = _plate_lattice(x0, x1, py0, py1, step, jitter, rng)

    edges = []
    seen = set()

    def add_edge(a, b):
        key = (min(a, b), max(a, b))
        if key not in seen:
            seen.add(key)
            edges.append((pts[a], pts[b]))

    # Each lattice cell becomes ONE chunky quad plate filled with a single flat
    # value (no per-cell triangulation — that fine net was the round-1 wireframe).
    for r in range(rows):
        for c in range(cols):
            tl, tr = pts[(r, c)], pts[(r, c + 1)]
            br, bl = pts[(r + 1, c + 1)], pts[(r + 1, c)]
            quad = [tl, tr, br, bl]
            gx = (tl[0] + br[0]) * 0.5
            gy = (tl[1] + br[1]) * 0.5
            fill = _plate_value(gx, gy, bw, H, rng)
            _draw_plate(surf, quad, fill, ss)
            add_edge((r, c), (r, c + 1))
            add_edge((r, c + 1), (r + 1, c + 1))
            add_edge((r + 1, c + 1), (r + 1, c))
            add_edge((r + 1, c), (r, c))

    _draw_seams(surf, edges, ss, rng)

    # A faint occasional plate-set gem dotting the wall, very sparingly, so the
    # mass reads as a charnel reliquary without rivalling the keystone focal.
    for _ in range(max(1, (rows * cols) // 10)):
        gr = rng.randint(1, rows - 1)
        gc = rng.randint(1, cols - 1)
        gx, gy = pts[(gr, gc)]
        if abs(gy - boss_cy) < boss_band:
            continue
        _gem(surf, gx, gy, int(2.6 * ss), ss,
             CYAN if rng.random() < 0.5 else PURPLE,
             CYAN_HI if rng.random() < 0.5 else PURPLE_HI)

    _boss_keystone(surf, bw // 2, boss_cy, boss_R, ss, flip=boss_flip)

    small = pygame.transform.smoothscale(surf, (PW, max(1, int(height_px))))
    return _grow_outline(small)


# ── Sky backdrops for the read test ───────────────────────────────────────────

def _day_sky(w, h):
    sky = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        c = (int(116 + 60 * t), int(186 + 30 * t), int(232 - 20 * t))
        pygame.draw.line(sky, c, (0, y), (w, y))
    rng = random.Random(7)
    for _ in range(14):
        cx = rng.randint(0, w)
        cy = rng.randint(int(h * 0.08), int(h * 0.7))
        for k in range(rng.randint(3, 6)):
            r = rng.randint(10, 26)
            pygame.draw.circle(sky, (244, 248, 252),
                               (cx + rng.randint(-22, 22), cy + rng.randint(-6, 6)), r)
    for _ in range(40):
        pygame.draw.circle(sky, (255, 255, 255),
                           (rng.randint(0, w), rng.randint(0, h)), 1)
    return sky


def _night_sky(w, h):
    """A night-biome strip so the void test is checked against a DARK sky too:
    the recessed grout must stay clearly readable as bone, never collapse toward
    the dark sky value or open a hole."""
    sky = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        c = (int(22 + 26 * t), int(26 + 28 * t), int(54 + 30 * t))
        pygame.draw.line(sky, c, (0, y), (w, y))
    rng = random.Random(11)
    for _ in range(70):
        pygame.draw.circle(sky, (220, 226, 244),
                           (rng.randint(0, w), rng.randint(0, h)), rng.choice([1, 1, 1, 2]))
    # A pale moon glow so there is a bright patch for grout to be tested against.
    pygame.draw.circle(sky, (210, 214, 236), (int(w * 0.7), int(h * 0.16)), 16)
    return sky


def main():
    SS = 5
    GAP = 150
    TOP_H = 250
    BOT_H = 250

    margin = 24

    title_f = pygame.font.SysFont("dejavusans", 19, bold=True)
    sub_f = pygame.font.SysFont("dejavusans", 12)

    top = _build_slab(TOP_H, SS, flip=False, seed=51)
    bot = _build_slab(BOT_H, SS, flip=True, seed=52)

    # Layout: a 2.4x hero on day sky, a 1x display-zoomed strip, a true-1x strip
    # on day sky, and a true-1x strip on NIGHT sky (the new void/banding check).
    view = 2.4
    col_w = int(PW * view)
    crop_h = TOP_H + GAP + BOT_H
    hero_h = int(crop_h * 0.74)

    sheet_w = 760
    sheet_h = hero_h + 130
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((40, 44, 56))
    sheet.blit(title_f.render("FUSED BONE-PLATE SLAB - round 2", True, (255, 255, 255)), (20, 12))
    sheet.blit(sub_f.render("flat-value plate mosaic (no horizontal courses) - chunky facets - sparse gold glints - boss keystone kept",
                            True, (206, 208, 220)), (20, 36))

    hero_x = margin
    hero_y = 60

    # ── 2.4x hero over busy day sky ──────────────────────────────────────────
    hero_sky = _day_sky(col_w + 36, hero_h)
    sheet.blit(hero_sky, (hero_x, hero_y))
    top_v = pygame.transform.smoothscale(top, (col_w, int(TOP_H * view * 0.74)))
    bot_v = pygame.transform.smoothscale(bot, (col_w, int(BOT_H * view * 0.74)))
    cx_hero = hero_x + 18 + col_w // 2
    sheet.blit(top_v, (cx_hero - col_w // 2, hero_y))
    gap_v = int(GAP * view * 0.74)
    bot_y = hero_y + top_v.get_height() + gap_v
    sheet.blit(bot_v, (cx_hero - col_w // 2, bot_y))
    pip_y = hero_y + top_v.get_height() + gap_v // 2
    pygame.draw.circle(sheet, (250, 196, 60), (cx_hero, pip_y), 9)
    pygame.draw.circle(sheet, INK, (cx_hero, pip_y), 9, 2)
    sheet.blit(sub_f.render("2.4x hero (day)", True, (230, 232, 240)), (hero_x + 4, hero_y + hero_h + 6))

    crop_scale = hero_h / crop_h

    def zoomed_strip(skyfun, label, x):
        strip = pygame.Surface((PW + 26, crop_h))
        strip.blit(skyfun(PW + 26, crop_h), (0, 0))
        sx = 13
        strip.blit(top, (sx, 0))
        strip.blit(bot, (sx, TOP_H + GAP))
        pygame.draw.circle(strip, (250, 196, 60), (sx + PW // 2, TOP_H + GAP // 2), 4)
        pygame.draw.circle(strip, INK, (sx + PW // 2, TOP_H + GAP // 2), 4, 1)
        disp = pygame.transform.scale(strip, (int((PW + 26) * crop_scale), int(crop_h * crop_scale)))
        sheet.blit(disp, (x, hero_y))
        sheet.blit(sub_f.render(label, True, (230, 232, 240)), (x, hero_y + disp.get_height() + 6))
        return x + disp.get_width()

    # ── 1x display-zoomed over day sky (the honest downscaled pixels) ─────────
    x = hero_x + col_w + 54
    x = zoomed_strip(_day_sky, "1x @ 58px (day, real px)", x)

    # ── 1x display-zoomed over NIGHT sky (void + banding re-check) ────────────
    x = zoomed_strip(_night_sky, "1x @ 58px (night)", x + 40)

    # ── True-pixel pair, no zoom, on day sky (the absolute honest read) ───────
    truth_x = x + 44
    truth_sky = _day_sky(PW + 18, crop_h)
    sheet.blit(truth_sky, (truth_x, hero_y))
    sheet.blit(top, (truth_x + 9, hero_y))
    sheet.blit(bot, (truth_x + 9, hero_y + TOP_H + GAP))
    pygame.draw.circle(sheet, (250, 196, 60),
                       (truth_x + 9 + PW // 2, hero_y + TOP_H + GAP // 2), 4)
    sheet.blit(sub_f.render("1x true", True, (230, 232, 240)), (truth_x, hero_y + crop_h + 6))

    out = "/home/user/skybit/docs/clown_bone_columns/bone-plate-slab/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()

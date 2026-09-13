"""Round-2 render for the STACKED SKULL-STUPA bone column (clown-event obstacle).

A walking skull-stupa: discrete tapering bone TIERS stacked vertically.
Alternating bands -- a domed skull-tier, then a blind reliquary niche-tier with
a faceted cyan/purple wisdom-gem -- repeat down the shaft so it tiles by the
band. The lowest tier of each half (the one bordering Pip's gap) is a single
WIDE "awake" skull with gold lamp-eyes turned to face the gap; every other skull
is blind/sleeping. The chunky discrete-tier silhouette is this column's whole
identity -- it must not converge on the threaded/trellis/candle columns.

Procedural-only review art; renders both halves framing a gap plus a 1x
gameplay-scale crop so the read at 58px is verifiable.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.config import PIPE_W

pygame.init()

# ── House-style bone roster palette (warm ivory, ink keyline, gold accent) ───
INK = (28, 22, 30)
BONE_CORE = (150, 134, 120)     # dark-core: deepest recess / under-shade
BONE_FILL = (214, 201, 178)     # flat-fill: the body's median ivory
BONE_RIM = (248, 240, 222)      # top-left rim-sheen
# Socket / niche cavity. WARM mid-dark (~35% value) -- NOT near-black: a dark
# hollow that still reads as carved bone, never as sky punched through the body.
# (The epic_boss roster keeps recess detail inside a lit silhouette this way.)
BONE_DEEP = (118, 86, 70)
BONE_DEEP_HI = (150, 112, 90)   # the warm cavity's own lit lip (closes the read)
GOLD = (250, 205, 72)
GOLD_HI = (255, 236, 150)
GOLD_DK = (176, 130, 30)
# Faceted wisdom gem -- cyan core flushing to violet at the facets.
GEM_CY = (120, 232, 236)
GEM_CY_HI = (215, 252, 252)
GEM_VIO = (150, 110, 224)
GEM_VIO_DK = (78, 52, 138)
LAMP = (255, 198, 70)           # awake skull's gold lamp-eye
LAMP_HI = (255, 240, 180)
LAMP_CORE = (180, 92, 18)

OVERHANG = 9                    # tiers bulge this far past the 58px column


def _box(H, ss):
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(H)) * ss
    return pygame.Surface((bw, bh), pygame.SRCALPHA), bw, bh


def _facet_gem(surf, cx, cy, r, ss, *, violet_bias):
    """A faceted cyan/violet wisdom-gem cut as a kite (diamond): a bright cyan
    upper crown and a darker violet pavilion, with a hard ink keyline and a
    single hot specular chip. `violet_bias` (0..1) shifts the body toward the
    violet half of the set so alternating niches read warm/cool, not identical."""
    top = (cx, cy - r)
    bot = (cx, cy + r)
    le = (cx - int(r * 0.78), cy + int(r * 0.10))
    ri = (cx + int(r * 0.78), cy + int(r * 0.10))
    crown_c = GEM_VIO if violet_bias > 0.5 else GEM_CY
    # Pavilion stays a SATURATED cool tone, not near-black, so the gem core never
    # reads as a hole in the body -- the dark is colour, not void.
    pav_c = GEM_VIO_DK if violet_bias > 0.5 else _shade(GEM_CY, -55)
    # Ink seat so the gem reads as set INTO the bone, not stuck on.
    pygame.draw.polygon(surf, INK, [top, ri, bot, le])
    inset = max(1, int(ss))
    tt = (cx, cy - r + inset)
    bb = (cx, cy + r - inset)
    ll = (le[0] + inset, le[1])
    rr = (ri[0] - inset, ri[1])
    # Upper crown (lit) vs lower pavilion (shaded) split across the girdle.
    pygame.draw.polygon(surf, crown_c, [tt, rr, (cx, cy), ll])
    pygame.draw.polygon(surf, pav_c, [ll, (cx, cy), rr, bb])
    # Centre facet seam + the cool/violet cross-bleed so it reads multi-faceted.
    cross = GEM_VIO if violet_bias <= 0.5 else GEM_CY
    pygame.draw.line(surf, _shade(cross, -10), (cx, int(cy - r + inset)),
                     (cx, int(cy + r - inset)), max(1, int(ss)))
    pygame.draw.line(surf, _shade(crown_c, 30), ll, rr, max(1, int(ss)))
    # One hot specular chip on the upper-left crown facet.
    pygame.draw.circle(surf, GEM_CY_HI,
                       (int(cx - r * 0.30), int(cy - r * 0.34)), max(1, int(ss * 1.3)))


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _tier_block(surf, cx, top_y, w, h, ss, *, kind, gem_idx=0):
    """One stacked stupa TIER -- a chunky rounded slab the full column width.
    `kind`:
      "niche"   -> a blind reliquary band with a recessed cavity + wisdom-gem.
      "skull"   -> a domed sleeping skull-tier (closed/blind sockets).
    The slab carries the dark-core -> flat-fill -> top-left rim triad so each tier
    reads as a discrete carved drum, stacked drum-on-drum (the stupa rhythm)."""
    cx = int(cx)
    hw = int(w * 0.5)
    rad = max(2, int(h * 0.34))
    rect = pygame.Rect(cx - hw, int(top_y), 2 * hw, int(h))
    # Dark-core base slab (slightly oversized) so a hard ground reads beneath fill.
    pygame.draw.rect(surf, BONE_CORE, rect.inflate(int(2 * ss), int(2 * ss)),
                     border_radius=rad)
    pygame.draw.rect(surf, BONE_FILL, rect, border_radius=rad)
    # Per-tier rim-sheen across the TOP of the drum: a bright lit band on the
    # upper face so each drum catches light separately -- this is what lets a
    # player COUNT the stacked tiers at 1x (the discrete-stacking thesis).
    top_band = pygame.Rect(rect.x + int(3 * ss), rect.y + int(2 * ss),
                           rect.w - int(6 * ss), int(h * 0.30))
    pygame.draw.rect(surf, BONE_RIM, top_band,
                     border_radius=max(1, int(h * 0.18)))
    sheen = rect.inflate(-int(3 * ss), -int(3 * ss))
    pygame.draw.arc(surf, BONE_RIM, sheen, math.pi * 0.45, math.pi * 1.05,
                    max(1, int(2 * ss)))
    # Hard ink keyline carrying the silhouette value (the load-bearing read @1x).
    pygame.draw.rect(surf, INK, rect, max(1, int(2 * ss)), border_radius=rad)
    # The tier seam is the whole "discrete stacking" read, so it's beefed ~2x:
    # a hard ink shadow line at the joint, then a WIDE two-tone gold collar that
    # ticks every drum-on-drum joint metallically -- countable at true 1x.
    cy = int(top_y + h)
    inset = int(2 * ss)
    pygame.draw.line(surf, INK, (cx - hw + inset, cy - int(2 * ss)),
                     (cx + hw - inset, cy - int(2 * ss)), max(1, int(ss)))
    pygame.draw.line(surf, GOLD_DK, (cx - hw + inset, cy),
                     (cx + hw - inset, cy), max(2, int(3 * ss)))
    pygame.draw.line(surf, GOLD, (cx - hw + int(3 * ss), cy - int(ss)),
                     (cx + hw - int(3 * ss), cy - int(ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, GOLD_HI, (cx - hw + int(4 * ss), cy - int(1.6 * ss)),
                     (cx + hw - int(4 * ss), cy - int(1.6 * ss)), max(1, int(ss)))

    mid_y = int(top_y + h * 0.5)
    if kind == "niche":
        # A blind reliquary niche: a WARM dark arched cavity sunk into the drum
        # face with the faceted wisdom-gem set blind in its centre. Kept narrow
        # enough that a continuous ivory rim wraps it on every side -- the dark
        # cavity never reaches the drum's silhouette edge, so it can't read as a
        # fly-through window.
        nw = int(hw * 0.84)
        nh = int(h * 0.56)
        nrect = pygame.Rect(cx - nw // 2, mid_y - nh // 2, nw, nh)
        nrad = max(2, int(nh * 0.45))
        # Warm cavity, then a lit lower-right lip so the recess reads as a curved
        # carved pocket (closed) rather than a flat black aperture.
        pygame.draw.rect(surf, BONE_DEEP, nrect, border_radius=nrad)
        pygame.draw.arc(surf, BONE_DEEP_HI, nrect.inflate(-int(ss), -int(ss)),
                        math.pi * 1.15, math.pi * 1.85, max(1, int(1.4 * ss)))
        pygame.draw.rect(surf, INK, nrect, max(1, int(1.4 * ss)), border_radius=nrad)
        # Gold arch-lintel over the niche so the recess reads gilded, not a hole.
        pygame.draw.arc(surf, GOLD, nrect.inflate(int(2 * ss), int(2 * ss)),
                        math.pi * 0.08, math.pi * 0.92, max(1, int(1.4 * ss)))
        _facet_gem(surf, cx, mid_y, int(nh * 0.38), ss,
                   violet_bias=1.0 if gem_idx % 2 else 0.0)
    else:
        _sleeping_skull(surf, cx, mid_y, int(hw * 0.92), int(h * 0.42), ss)


def _sleeping_skull(surf, cx, cy, hw, hh, ss):
    """A blind/sleeping skull carved into a drum face: a domed cranium with two
    sunken CLOSED sockets (lidded slits, no glow) and a stitched nasal + jaw
    hint. Reads as 'one of the dormant tiers' against the awake gap skull."""
    cranium = pygame.Rect(cx - hw, cy - hh, 2 * hw, int(hh * 1.7))
    pygame.draw.ellipse(surf, BONE_CORE, cranium.inflate(int(2 * ss), int(2 * ss)))
    pygame.draw.ellipse(surf, BONE_FILL, cranium)
    pygame.draw.arc(surf, BONE_RIM, cranium.inflate(-int(3 * ss), -int(3 * ss)),
                    math.pi * 0.45, math.pi * 1.0, max(1, int(1.6 * ss)))
    pygame.draw.ellipse(surf, INK, cranium, max(1, int(1.8 * ss)))
    # Two sunken CLOSED sockets. Pulled IN and shrunk so a continuous ivory rim
    # wraps each one -- the warm dark never approaches the cranium silhouette, so
    # the pair can't read as two windows. Each is a closed lidded hollow, not a
    # punched hole: a bright ivory upper lid arcs over a warm-dark slit.
    ex = int(hw * 0.40)
    er = max(2, int(hw * 0.24))
    sy = cy - int(hh * 0.04)
    for s in (-1, 1):
        ox = cx + s * ex
        # Lit ivory socket bed first so dark sits on bone, not on the body edge.
        pygame.draw.circle(surf, BONE_RIM, (ox, sy), er + max(1, int(ss)))
        pygame.draw.circle(surf, BONE_DEEP, (ox, sy), er)
        # Warm lit lip on the lower rim so the hollow reads curved/closed.
        pygame.draw.arc(surf, BONE_DEEP_HI, (ox - er, sy - er, 2 * er, 2 * er),
                        math.pi * 1.1, math.pi * 1.9, max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, INK, (ox, sy), er, max(1, int(1.4 * ss)))
        # Lidded slit (the 'asleep' tell) -- a dark down-curve across the socket.
        pygame.draw.arc(surf, INK, (ox - er, sy - er, 2 * er, 2 * er),
                        math.pi * 1.05, math.pi * 1.95, max(1, int(1.8 * ss)))
    # Triangular nasal cavity (warm, small, well inside the face).
    nx = cx
    ny = cy + int(hh * 0.30)
    pygame.draw.polygon(surf, BONE_DEEP,
                        [(nx, ny - int(hh * 0.16)),
                         (nx - int(er * 0.42), ny + int(hh * 0.14)),
                         (nx + int(er * 0.42), ny + int(hh * 0.14))])
    # Jaw hint: a stitched tooth row low on the drum.
    jy = cy + int(hh * 0.58)
    for k in range(-2, 3):
        tx = cx + k * int(hw * 0.30)
        pygame.draw.line(surf, INK, (tx, jy), (tx, jy + int(hh * 0.16)),
                         max(1, int(ss)))


def _awake_skull(surf, cx, cy, hw, hh, ss, *, look_down):
    """The single WIDE awake skull at the gap edge -- the focal of each half
    (modelled on the frost-lich soul-standard). A broad cranium with two GOLD
    lamp-eyes turned to face the gap, a glowing nasal and a bared tooth row. The
    only lit skull; its gold sockets carry the 'this end is watching you' read."""
    cranium = pygame.Rect(cx - hw, cy - hh, 2 * hw, int(hh * 1.9))
    pygame.draw.ellipse(surf, BONE_CORE, cranium.inflate(int(3 * ss), int(3 * ss)))
    pygame.draw.ellipse(surf, BONE_FILL, cranium)
    # Cheek/zygomatic flare so the awake skull is visibly WIDER than the drums.
    for s in (-1, 1):
        cheek = [(cx + s * hw, cy + int(hh * 0.10)),
                 (cx + s * int(hw * 1.18), cy + int(hh * 0.55)),
                 (cx + s * int(hw * 0.74), cy + int(hh * 0.95))]
        pygame.draw.polygon(surf, BONE_FILL, cheek)
        pygame.draw.polygon(surf, INK, cheek, max(1, int(1.4 * ss)))
    pygame.draw.arc(surf, BONE_RIM, cranium.inflate(-int(4 * ss), -int(4 * ss)),
                    math.pi * 0.42, math.pi * 1.02, max(1, int(2 * ss)))
    pygame.draw.ellipse(surf, INK, cranium, max(1, int(2 * ss)))

    # Gold lamp-eyes -- the glow + iris turned toward the gap (down for the top
    # half, up for the bottom half). Pushed apart with a wide INK BRIDGE between
    # so the two lamps never blur into one smudge at 1x; the halo is kept TIGHT
    # (a single near-radius ring) so it sharpens the cap silhouette rather than
    # blooming into the bone.
    ex = int(hw * 0.54)
    er = max(3, int(hw * 0.32))
    iris_dy = int(er * (0.45 if look_down else -0.45))
    oy = cy - int(hh * 0.04)
    # Ink bridge: a hard dark septum the lit lamps read against, keeping them two.
    pygame.draw.line(surf, INK, (cx, oy - er), (cx, oy + er), max(2, int(2.4 * ss)))
    for s in (-1, 1):
        ox = cx + s * ex
        # A tight halo (one ring, ~1.4x the socket) so the cap stays crisp.
        glow = pygame.Surface((er * 4, er * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*LAMP, 110), (er * 2, er * 2), int(er * 1.45))
        surf.blit(glow, (ox - int(er * 2), oy - int(er * 2)),
                  special_flags=pygame.BLEND_RGBA_ADD)
        # Lit ivory rim seats the lamp on bone (dark/gold never touches the edge).
        pygame.draw.circle(surf, BONE_RIM, (ox, oy), er + max(1, int(2 * ss)))
        pygame.draw.circle(surf, LAMP_CORE, (ox, oy), er + max(1, int(ss)))
        pygame.draw.circle(surf, LAMP, (ox, oy), er)
        pygame.draw.circle(surf, INK, (ox, oy), er, max(1, int(1.4 * ss)))
        # Bright pupil aimed at the gap -- high-value chip so the lamp reads LIT.
        pygame.draw.circle(surf, LAMP_HI, (ox, oy + iris_dy), max(2, int(er * 0.48)))
        pygame.draw.circle(surf, (255, 255, 255),
                           (ox - int(er * 0.2), oy + iris_dy - int(er * 0.2)),
                           max(1, int(er * 0.22)))
    # Heavy ink brow ridge over the lamps (the 'awake/scowling' tell).
    pygame.draw.arc(surf, INK,
                    (cx - int(hw * 0.85), cy - int(hh * 0.62),
                     int(hw * 1.7), int(hh * 0.9)),
                    math.pi * 0.12, math.pi * 0.88, max(2, int(2.2 * ss)))
    # Glowing triangular nasal.
    ny = cy + int(hh * 0.42)
    nz = int(hw * 0.20)
    pygame.draw.polygon(surf, LAMP_CORE,
                        [(cx, ny - int(hh * 0.22)),
                         (cx - nz, ny + int(hh * 0.14)),
                         (cx + nz, ny + int(hh * 0.14))])
    # Bared tooth row across a wide grin band -- the awake skull is grinning.
    jw = int(hw * 0.92)
    jy = cy + int(hh * 0.70)
    jrect = pygame.Rect(cx - jw, jy, 2 * jw, int(hh * 0.42))
    pygame.draw.rect(surf, BONE_RIM, jrect, border_radius=max(1, int(2 * ss)))
    pygame.draw.rect(surf, INK, jrect, max(1, int(1.4 * ss)),
                     border_radius=max(1, int(2 * ss)))
    n_teeth = 6
    for k in range(1, n_teeth):
        tx = cx - jw + int(2 * jw * k / n_teeth)
        pygame.draw.line(surf, INK, (tx, jy), (tx, jy + int(hh * 0.42)),
                         max(1, int(ss)))


def _stupa_half(H, ss):
    """Render ONE half of the stupa: the awake wide skull seats at the GAP edge
    (the bottom of the box, before flip), then alternating niche / sleeping-skull
    tiers stack away toward the closed end, tapering slightly wider at the base.
    The repeating niche/skull band gives the tileable shaft."""
    surf, bw, bh = _box(H, ss)
    cx = bw / 2.0

    # Tier band geometry. The awake skull occupies a tall wide tier at the gap
    # edge; the rest of the shaft tiles a 2-tier band (niche + sleeping skull).
    awake_h = int(46 * ss)
    band_tier_h = int(34 * ss)
    gap_y = bh                                   # box bottom == gap edge pre-flip

    # Full-width column the awake skull flares past; drums taper from full at the
    # gap toward a hair narrower up the closed end so it reads as a built stupa.
    full_w = (PIPE_W + 2 * OVERHANG) * ss * 0.82
    drum_w = PIPE_W * ss * 0.92

    # 1) The repeating shaft: niche / skull / niche / skull ... from top of box
    #    DOWN to just above the awake skull. Drawn top-first so seams overlap
    #    cleanly downward (toward the gap).
    shaft_bottom = gap_y - awake_h
    y = int(2 * ss)
    idx = 0
    while y < shaft_bottom - band_tier_h:
        # Near-constant width with only a HAIR of taper: a beefier seam means the
        # bump-in/out at each joint must stay shallow, or the pinch reads as a
        # passable notch in a solid body. Keep drums effectively full-width.
        t = y / max(1, shaft_bottom)
        w = drum_w * (0.97 + 0.03 * t)
        kind = "niche" if idx % 2 == 0 else "skull"
        _tier_block(surf, cx, y, w, band_tier_h, ss, kind=kind, gem_idx=idx // 2)
        y += band_tier_h
        idx += 1
    # Fill the last partial tier flush to the awake skull so no sky-gap shows.
    if y < shaft_bottom:
        kind = "niche" if idx % 2 == 0 else "skull"
        _tier_block(surf, cx, y, drum_w, shaft_bottom - y, ss,
                    kind=kind, gem_idx=idx // 2)

    # 2) A gold collar plinth seating the awake skull on the shaft.
    plinth_y = shaft_bottom - int(3 * ss)
    pygame.draw.rect(surf, GOLD_DK,
                     (int(cx - full_w * 0.5), plinth_y,
                      int(full_w), int(6 * ss)),
                     border_radius=int(2 * ss))
    pygame.draw.rect(surf, GOLD,
                     (int(cx - full_w * 0.5 + ss), plinth_y + ss,
                      int(full_w - 2 * ss), int(4 * ss)),
                     border_radius=int(2 * ss))

    # 3) The single WIDE awake skull at the gap edge.
    _awake_skull(surf, cx, gap_y - int(awake_h * 0.5),
                 int(full_w * 0.52), int(awake_h * 0.42), ss, look_down=True)

    return surf, bw, bh


def _grow_outline(surf, ss):
    """Alpha-grown 1px silhouette outline (after smoothscale): a hard 1px ink rim
    around the whole column so it crisps against a busy day sky -- the roster's
    silhouette-outline finish."""
    mask = pygame.mask.from_surface(surf)
    outline = mask.outline()
    if len(outline) > 2:
        pygame.draw.lines(surf, INK, True, outline, 1)
    return surf


def render_half(H, *, flip):
    """Supersample -> smoothscale -> alpha-grown outline: the roster finish. The
    awake skull always faces the gap (flip the top half so its skull points
    DOWN)."""
    ss = 4
    surf, bw, bh = _stupa_half(H, ss)
    out_w = PIPE_W + 2 * OVERHANG
    small = pygame.transform.smoothscale(surf, (out_w, max(1, int(H))))
    if flip:
        small = pygame.transform.flip(small, False, True)
    _grow_outline(small, ss)
    return small


# ── Review sheet ─────────────────────────────────────────────────────────────

def _sky_column(w, h):
    """A busy day-sky strip (the hardest read background) under each render."""
    surf = pygame.Surface((w, h))
    top = (90, 170, 230)
    bot = (170, 220, 245)
    for yy in range(h):
        t = yy / max(1, h - 1)
        surf.fill((int(top[0] + (bot[0] - top[0]) * t),
                   int(top[1] + (bot[1] - top[1]) * t),
                   int(top[2] + (bot[2] - top[2]) * t)),
                  (0, yy, w, 1))
    # Busy clutter: clouds + a few distant ground bumps so the silhouette has to
    # fight a non-flat field.
    rng = __import__("random").Random(7)
    for _ in range(9):
        cxp = rng.randint(0, w)
        cyp = rng.randint(int(h * 0.1), int(h * 0.7))
        cr = rng.randint(10, 26)
        cloud = pygame.Surface((cr * 4, cr * 2), pygame.SRCALPHA)
        for k in range(3):
            pygame.draw.circle(cloud, (255, 255, 255, 130),
                               (cr + k * cr, cr), cr - k * 2)
        surf.blit(cloud, (cxp - cr * 2, cyp - cr))
    return surf


def main():
    pygame.font.init()
    f_title = pygame.font.SysFont("Arial", 24, bold=True)
    f_lbl = pygame.font.SysFont("Arial", 14, bold=True)
    f_sub = pygame.font.SysFont("Arial", 12)

    BG = (38, 40, 52)
    sheet = pygame.Surface((900, 740))
    sheet.fill(BG)

    sheet.blit(f_title.render(
        "STACKED SKULL-STUPA  --  clown bone column  --  round 2",
        True, (240, 240, 245)), (20, 14))
    sheet.blit(f_sub.render(
        "1x panel is the PRIMARY JUDGE -- solid read, countable tiers, "
        "lit awake cap. Holes closed; seams ~2x.",
        True, (180, 200, 210)), (20, 38))

    panel_y = 60
    PANEL_H = 600

    # ── PRIMARY JUDGE: the true 58px gameplay crop, drawn FIRST and largest in
    #    reading order. Every fix is validated here, not on the flattering hero. ──
    crop_x = 30
    CROP_W = 200
    csky = _sky_column(CROP_W, PANEL_H)
    sheet.blit(csky, (crop_x, panel_y))
    c_gap_top = 252
    c_gap_h = 138
    c_top = render_half(c_gap_top, flip=True)
    c_bot = render_half(PANEL_H - c_gap_top - c_gap_h, flip=False)
    ccx = crop_x + CROP_W // 2 - (PIPE_W + 2 * OVERHANG) // 2
    sheet.blit(c_top, (ccx, panel_y))
    sheet.blit(c_bot, (ccx, panel_y + c_gap_top + c_gap_h))
    pygame.draw.rect(sheet, (255, 210, 90), (crop_x, panel_y, CROP_W, PANEL_H), 2)
    # The ONLY red on the sheet: the 58px width ruler, floated in the clear gap
    # against open sky (never under a cap) so it can't be mistaken for art.
    ruler_y = panel_y + c_gap_top + c_gap_h // 2
    pygame.draw.line(sheet, (255, 90, 90),
                     (ccx + OVERHANG, ruler_y),
                     (ccx + OVERHANG + PIPE_W, ruler_y), 2)
    sheet.blit(f_sub.render("58px body", True, (255, 120, 120)),
               (ccx + OVERHANG, ruler_y + 4))
    sheet.blit(f_lbl.render("1x  IN-GAME SIZE  (PRIMARY)", True, (255, 220, 120)),
               (crop_x, panel_y + PANEL_H + 6))
    sheet.blit(f_sub.render("squint: any dark = sky-through? must be NO",
                            True, (255, 200, 130)), (crop_x, panel_y + PANEL_H + 24))

    # ── Squint test: the 1x crop hard-downscaled then back up, nearest-neighbour,
    #    so blob-level reads are exposed (does the body hold as solid?). ──
    sq_src = sheet.subsurface(
        (crop_x, panel_y, CROP_W, PANEL_H)).copy()
    sq_small = pygame.transform.smoothscale(sq_src, (CROP_W // 4, PANEL_H // 4))
    sq_big = pygame.transform.scale(sq_small, (110, PANEL_H))
    sq_x = crop_x + CROP_W + 22
    sheet.blit(sq_big, (sq_x, panel_y))
    pygame.draw.rect(sheet, (200, 205, 215), (sq_x, panel_y, 110, PANEL_H), 1)
    sheet.blit(f_lbl.render("SQUINT", True, (235, 235, 240)),
               (sq_x, panel_y + PANEL_H + 6))

    # ── Hero: top half hangs down + bottom half rises up, framing a gap ──
    panel_x = sq_x + 110 + 26
    PANEL_W = 210
    sky = _sky_column(PANEL_W, PANEL_H)
    sheet.blit(sky, (panel_x, panel_y))
    gap_top = 248
    gap_h = 150
    top_half = render_half(gap_top, flip=True)
    bot_half = render_half(PANEL_H - gap_top - gap_h, flip=False)
    col_x = panel_x + PANEL_W // 2 - (PIPE_W + 2 * OVERHANG) // 2
    sheet.blit(top_half, (col_x, panel_y))
    sheet.blit(bot_half, (col_x, panel_y + gap_top + gap_h))
    pygame.draw.rect(sheet, (200, 205, 215), (panel_x, panel_y, PANEL_W, PANEL_H), 1)
    sheet.blit(f_lbl.render("HERO  --  gap framed", True, (235, 235, 240)),
               (panel_x, panel_y + PANEL_H + 6))
    sheet.blit(f_sub.render("caps mirror exactly", True, (200, 205, 215)),
               (panel_x, panel_y + PANEL_H + 24))

    # ── Tall single half to prove the band repeats / tiles + countable tiers ──
    tall_x = panel_x + PANEL_W + 26
    tw = PIPE_W + 2 * OVERHANG + 8
    tsky = _sky_column(tw, PANEL_H)
    sheet.blit(tsky, (tall_x, panel_y))
    tall = render_half(PANEL_H, flip=False)
    sheet.blit(tall, (tall_x + 4, panel_y))
    pygame.draw.rect(sheet, (200, 205, 215), (tall_x, panel_y, tw, PANEL_H), 1)
    sheet.blit(f_lbl.render("TILING SHAFT", True, (235, 235, 240)),
               (tall_x, panel_y + PANEL_H + 6))
    sheet.blit(f_sub.render("count the drums", True, (200, 205, 215)),
               (tall_x, panel_y + PANEL_H + 24))

    out_dir = "/home/user/skybit/docs/clown_bone_columns/skull-stupa"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print(out_path)


if __name__ == "__main__":
    main()

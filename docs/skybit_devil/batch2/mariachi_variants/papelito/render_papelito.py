"""
Papelito — a calaca built from PAPEL PICADO, perforated tissue-paper bunting
given a body (MARIACHI-lineage warm-skeleton family, concept D).

LEAD FACET: CALACA DECORATION. The creature is nothing but festival decoration
that woke up — a flat scalloped cut-paper sheet strung from a bunting line, with
a skull face PUNCHED as negative space out of the sheet-top (sky shows THROUGH
the sockets). The punched-out face IS the anatomy; the fluttering banner IS the
body. Deliberately the LEAST bony body in the family — flat and papery where
every other take is volumetric bone.

House style: chibi proportions, FLAT saturated fills + hard 1-2px ink keylines,
form via a TRIAD — but here, to PROTECT THE FLATNESS, the triad reads strictly
as front-sheet / back-sheet shadow / top-edge sheen (NO volumetric bone, NO
rounded rim-light dome anywhere). Silhouette POP via a 1px outline grown from
the alpha mask; supersample SS=4 -> smoothscale.

The whole gag is negative space. So every punch — the two eye sockets, the nose
triangle, the mouth, and the papel-picado perforation field — is cut as a TRUE
hole through the FINISHED, FULLY-LAYERED sheet (front fill AND back-sheet shadow
together) in one final alpha pass, so the backdrop shows clean through them. We
cut everything LAST and we cut it through every layer at once — that is the only
way the sky reaches the socket interior instead of a stray sliver of back-sheet.
The two sockets are pinned big enough to survive a clear sky-colored void at
32px with a cream bridge between them.

Run headless:  SDL_VIDEODRIVER=dummy python render_papelito.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (locked brief D, exact hexes) ─────────────────────────────
CREAM       = (246, 238, 222)   # paper-cream sheet base — HERO body mass
MARIGOLD    = (244, 150,  44)   # marigold-orange flag
PINK        = (232,  96, 150)   # papel-pink flag
MASA        = (226, 182,  80)   # masa-gold flag
TURQ        = ( 56, 168, 168)   # turquoise flag — the SINGLE cool note
CORD        = (190,  60,  50)   # rust-red bunting cord
INK         = ( 28,  22,  26)   # keyline ink
SHEEN       = (252, 246, 232)   # top-left rim sheen

# Derived working tones, all kept inside the pinned families. For Papelito the
# "dark-core" of the triad is a BACK-SHEET SHADOW (a flat darker copy of the same
# hue offset down-right), never a rounded bone core — this keeps every mass
# reading as a flat sheet of paper with a sheet behind it, not a 3D volume.
CREAM_BACK  = (206, 196, 176)   # cream back-sheet shadow (flat, offset)
CREAM_SHEEN = (252, 247, 236)   # cream top-edge catch
MARI_BACK   = (196, 110,  28)
PINK_BACK   = (188,  66, 112)
MASA_BACK   = (184, 142,  52)
TURQ_BACK   = ( 34, 122, 124)

SS = 4   # supersample factor


# ── helpers ──────────────────────────────────────────────────────────────────

def _poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def paper_sheet(surf, pts, fill, back, sheen, outline=INK,
                shadow_dx=None, shadow_dy=None, sheen_band=None):
    """A flat cut-paper sheet via the protected-flat triad:
      back-sheet shadow (flat darker copy offset down-right)
        -> flat front fill
          -> a thin top-edge sheen band (a CATCH on the paper lip, never a dome).
    Read is "front sheet over its own shadow", deliberately NON-volumetric."""
    if shadow_dx is None:
        shadow_dx = SS * 2.4
    if shadow_dy is None:
        shadow_dy = SS * 2.4
    # Back-sheet shadow: same silhouette, offset, flat darker hue.
    _poly(surf, back, [(x + shadow_dx, y + shadow_dy) for x, y in pts])
    # Hard ink keyline (fat stroke at SS scale so 1-2px survives smoothscale).
    if outline is not None:
        _poly(surf, outline, pts)
        pygame.draw.polygon(surf, outline, [(int(x), int(y)) for x, y in pts],
                            int(SS * 1.4))
    # Flat front fill, inset just inside the keyline.
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    inset = [(p[0] + (cx - p[0]) * 0.05, p[1] + (cy - p[1]) * 0.05) for p in pts]
    _poly(surf, fill, inset)
    # Top-edge sheen band: a flat sliver hugging the upper edge only.
    if sheen_band:
        _poly(surf, sheen, sheen_band)


def cut_holes(surf, draw_fn):
    """Punch TRUE cut-through holes through the WHOLE finished sheet at once.

    The round-1 miss was punching mid-build: the back-sheet-shadow layer drawn
    UNDER the front fill survived inside the socket, so the interior sampled
    paper, not sky. Here we cut LAST, against the fully-composited surface, so the
    cut removes front fill AND back-sheet shadow together and the backdrop shows
    clean through. draw_fn(mask_surf) draws the punch shapes opaque-white onto a
    scratch surface; wherever that scratch is opaque we drive the sheet alpha to 0
    via a BLEND_RGBA_MULT mask."""
    W, H = surf.get_size()
    hole = pygame.Surface((W, H), pygame.SRCALPHA)
    draw_fn(hole)                       # punch shapes drawn opaque white
    m = pygame.mask.from_surface(hole)
    # keep == white(opaque); punched == alpha 0  -> multiply zeroes sheet alpha.
    mult = m.to_surface(setcolor=(255, 255, 255, 0),
                        unsetcolor=(255, 255, 255, 255))
    surf.blit(mult, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def ink_ring_ellipse(surf, rect, thick):
    pygame.draw.ellipse(surf, INK, rect, thick)


def grow_outline(surf, color=INK, thickness=1):
    """1px (post-scale) outline grown from the alpha mask — the silhouette POP.
    Run at supersample scale so it survives smoothscale. Because Papelito has
    punched interior holes, the mask outline traces the OUTER edge; interior
    cuts keep their own keylines drawn at punch time."""
    mask = pygame.mask.from_surface(surf)
    for pts in mask.outline(every=2), :
        if len(pts) > 2:
            pygame.draw.lines(surf, color, True, pts, max(1, thickness * SS))


# ── the creature ─────────────────────────────────────────────────────────────

def draw_papelito(target_size):
    """A papel-picado banner-spirit: a scalloped rectangular cream paper SHEET
    (pinked zig-zag hem) strung from an arc of triangular bunting flags, a skull
    face PUNCHED into the sheet-top (sky-through sockets), stamped perforations
    across the body, and tiny paper-strip arms.

    Build order is deliberate: paint EVERY positive layer first (bunting, arms,
    sheet, fold, painted rim notches, ink ring lips), THEN cut every hole in one
    final alpha pass so the sky reaches each socket interior."""
    S = target_size * SS
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S * 0.5

    # Layout. The dominant read is a tall flat sheet; the bunting arc crowns it.
    bunt_y  = S * 0.115         # bunting cord arc height
    sheet_t = S * 0.215         # sheet top edge
    sheet_b = S * 0.80          # sheet bottom (before pinked hem)
    sheet_w = S * 0.30          # half-width of the main sheet

    # Face geometry — shared by the painted rim lips AND the final cut pass so the
    # ink lip and the hole register exactly. Sockets pinned BIG: ~3-4px clear void
    # at 32px with >=2px cream bridge between them so they never fuse.
    face_y   = sheet_t + S * 0.175
    eye_dx   = S * 0.105        # socket centre offset from axis (wide bridge)
    eye_rx   = S * 0.072        # socket half-width
    eye_ry   = S * 0.084        # socket half-height (tall teardrop skull socket)
    nose_y   = face_y + S * 0.118
    mouth_y  = face_y + S * 0.205

    # Per-hole records so the painted ink lips and the cut pass stay in lockstep.
    sockets = [(cx - eye_dx, face_y), (cx + eye_dx, face_y)]

    # ── BUNTING STRING: a rust cord arc with stacked triangular papel flags ────
    cord_pts = []
    for i in range(31):
        t = i / 30.0
        x = S * 0.10 + t * S * 0.80
        y = bunt_y + math.sin(t * math.pi) * S * 0.018 * -1 + (1 - math.sin(t * math.pi)) * S * 0.04
        cord_pts.append((x, y))
    pygame.draw.lines(surf, INK, False, [(int(x), int(y)) for x, y in cord_pts],
                      max(2, int(SS * 1.8)))
    pygame.draw.lines(surf, CORD, False, [(int(x), int(y)) for x, y in cord_pts],
                      max(1, int(SS * 1.0)))

    flag_cols = [MARIGOLD, PINK, MASA, TURQ, PINK, MARIGOLD, MASA]
    flag_back = [MARI_BACK, PINK_BACK, MASA_BACK, TURQ_BACK, PINK_BACK,
                 MARI_BACK, MASA_BACK]
    nfl = len(flag_cols)
    flag_holes = []     # collect flag perforations to cut in the final pass
    for i in range(nfl):
        ct = (i + 0.5) / nfl
        cidx = int(ct * (len(cord_pts) - 1))
        ax, ay = cord_pts[cidx]
        fw = S * 0.05
        fh = S * 0.085
        tri = [(ax - fw, ay), (ax + fw, ay), (ax, ay + fh)]
        paper_sheet(surf, tri, flag_cols[i], flag_back[i], SHEEN,
                    shadow_dx=SS * 1.6, shadow_dy=SS * 1.6,
                    sheen_band=[(ax - fw, ay), (ax - fw * 0.2, ay),
                                (ax - fw * 0.45, ay + fh * 0.4)])
        flag_holes.append((ax, ay + fh * 0.42, S * 0.013))

    # ── PAPER-STRIP ARMS: thin folded cut-paper streamers off the sheet sides ──
    # Thicken the join to the body so they don't detach into floating confetti at
    # gameplay scale (AD note 6): start the strip a touch INSIDE the sheet edge
    # and run a slightly fatter ribbon.
    for side in (-1, 1):
        ax0 = cx + side * sheet_w * 0.88
        ay0 = S * 0.50
        strip = [(ax0, ay0)]
        for k in range(1, 5):
            strip.append((ax0 + side * S * (0.045 * k),
                          ay0 + (S * 0.03 if k % 2 else -S * 0.005) + k * S * 0.012))
        for k in range(len(strip) - 1):
            seg_col = MARIGOLD if k % 2 == 0 else PINK
            seg_bk = MARI_BACK if k % 2 == 0 else PINK_BACK
            a = strip[k]
            b = strip[k + 1]
            half = S * 0.026          # fatter ribbon than r1's 0.022 (firmer join)
            quad = [(a[0], a[1] - half), (b[0], b[1] - half * 0.82),
                    (b[0], b[1] + half * 0.82), (a[0], a[1] + half)]
            paper_sheet(surf, quad, seg_col, seg_bk, SHEEN,
                        shadow_dx=SS * 1.2, shadow_dy=SS * 1.4, sheen_band=None)

    # ── MAIN PAPEL SHEET (the body) — a tall scalloped rectangle ──────────────
    n_scal = 7
    body = [(cx - sheet_w, sheet_t), (cx + sheet_w, sheet_t),
            (cx + sheet_w, sheet_b)]
    for i in range(n_scal + 1):
        t = i / n_scal
        x = cx + sheet_w - t * (2 * sheet_w)
        dip = S * 0.055 if i % 2 == 0 else S * 0.018
        body.append((x, sheet_b + dip))
    body.append((cx - sheet_w, sheet_b))
    paper_sheet(surf, body, CREAM, CREAM_BACK, CREAM_SHEEN,
                shadow_dx=SS * 2.6, shadow_dy=SS * 2.6,
                sheen_band=[(cx - sheet_w, sheet_t),
                            (cx - sheet_w * 0.3, sheet_t),
                            (cx - sheet_w * 0.5, sheet_t + S * 0.05),
                            (cx - sheet_w, sheet_t + S * 0.06)])

    # A folded crease line down the sheet (flat ink tick, no volume).
    pygame.draw.line(surf, CREAM_BACK,
                     (int(cx), int(sheet_t + S * 0.02)),
                     (int(cx), int(sheet_b)),
                     max(1, int(SS * 0.8)))

    # ── INK LIPS around the punched cuts (drawn BEFORE the cut) ────────────────
    # The cut is alpha; the keyline is the dark paper lip hugging the cut edge.
    # Painted now so it sits under nothing and registers exactly with the hole.
    for ex, ey in sockets:
        ink_ring_ellipse(surf, (int(ex - eye_rx - SS), int(ey - eye_ry - SS),
                                int(eye_rx * 2 + SS * 2), int(eye_ry * 2 + SS * 2)),
                         max(1, int(SS * 1.3)))
        # 2 hard pinked NOTCHES at the outer socket rim — a CUT detail (replaces
        # r1's fuzzy painted lash-ticks; stays on-medium at 32px, AD note 4).
        sgn = 1 if ex > cx else -1
        for k in (-1, 1):
            nx = ex + sgn * eye_rx * 0.92
            ny = ey + k * eye_ry * 0.42
            pygame.draw.line(surf, INK, (int(nx), int(ny)),
                             (int(nx + sgn * eye_rx * 0.42), int(ny + k * eye_ry * 0.10)),
                             max(1, int(SS * 1.1)))
    # nose ink lip
    nose = [(cx, nose_y + S * 0.052),
            (cx - S * 0.030, nose_y),
            (cx + S * 0.030, nose_y)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose],
                        max(1, int(SS * 1.2)))
    # mouth ink lip — a single stamped slot broken by cream bridges into a short
    # 3-tooth grin (the THIRD punch, reinforcing negative-space language; AD
    # note 3 — no positive ink teeth-dots, the grin is read by the cut alone).
    m_w = S * 0.105
    m_h = S * 0.044
    pygame.draw.ellipse(surf, INK,
                        (int(cx - m_w - SS), int(mouth_y - m_h - SS),
                         int(m_w * 2 + SS * 2), int(m_h * 2 + SS * 2)),
                        max(1, int(SS * 1.2)))

    # ── FINAL CUT PASS — every hole punched through the finished sheet at once ─
    def _allcuts(h):
        white = (255, 255, 255, 255)
        # Eye sockets — the dominant 32px tell, big clean voids.
        for ex, ey in sockets:
            pygame.draw.ellipse(h, white,
                                (int(ex - eye_rx), int(ey - eye_ry),
                                 int(eye_rx * 2), int(eye_ry * 2)))
        # Nose — punched triangle.
        pygame.draw.polygon(h, white, [(int(x), int(y)) for x, y in nose])
        # Mouth — one stamped slot, broken by 2 cream bridges into a 3-tooth grin
        # (the slot is the cut; the bridges are uncut cream = the teeth).
        slot = pygame.Surface((h.get_width(), h.get_height()), pygame.SRCALPHA)
        pygame.draw.ellipse(slot, white,
                            (int(cx - m_w), int(mouth_y - m_h),
                             int(m_w * 2), int(m_h * 2)))
        for bx in (cx - m_w * 0.34, cx + m_w * 0.34):
            pygame.draw.rect(slot, (0, 0, 0, 0),
                             (int(bx - SS * 1.4), int(mouth_y - m_h),
                              int(SS * 2.8), int(m_h * 2)))
        h.blit(slot, (0, 0))
        # Flag perforations (papel-picado holes that punch through the flags too).
        for fx, fy, fr in flag_holes:
            pygame.draw.circle(h, white, (int(fx), int(fy)), int(fr))
        # Body perforation field — a low-count run of TRUE punch-holes BELOW the
        # face so the gag shows the instant the silhouette moves against sky (AD
        # note 5) without crowding the grin. Kept small + few so it stays clean at
        # 32px: two flanking marigold-flower-ish punches + one centred dot row.
        for sx in (cx - S * 0.175, cx + S * 0.175):
            pygame.draw.circle(h, white, (int(sx), int(sheet_t + S * 0.475)),
                               int(S * 0.028))
        for k in range(-2, 3):
            dx = cx + k * S * 0.085
            pygame.draw.circle(h, white,
                               (int(dx), int(sheet_t + S * 0.585)), int(S * 0.017))

    cut_holes(surf, _allcuts)

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (target_size, target_size))


# ── the prop -> pillar mirror (bunting string + marigold-rosette cap) ─────────

def draw_pillar(width, height, top_cap=True):
    """Bunting string / flagpole pillar. A banner cord strung with stacked
    papel-picado flags = repeatable shaft body (each flag a band); a larger
    cut-paper marigold-rosette medallion = detachable gap-edge cap. On-axis flags
    + a round radial rosette read naturally vertical and symmetric (mirror clean).
    Flag + rosette perforations punch through as TRUE holes (same final-pass cut
    as the creature), so the bunting reads as real papel picado on the pillar too.
    Cap sized ~shaft +35% so it stays balanced at the gap line."""
    W = width * SS
    H = height * SS
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W * 0.5

    pygame.draw.line(surf, INK, (cx, 0), (cx, H), max(2, int(SS * 2.2)))
    pygame.draw.line(surf, CORD, (cx, 0), (cx, H), max(1, int(SS * 1.2)))

    band_h = W * 0.62
    flag_cols = [MARIGOLD, PINK, MASA, TURQ]
    flag_back = [MARI_BACK, PINK_BACK, MASA_BACK, TURQ_BACK]
    n = max(2, int(H / band_h))
    fw = W * 0.30
    holes = []
    for i in range(n):
        fy = i * band_h + band_h * 0.1
        ci = i % len(flag_cols)
        tri = [(cx - fw, fy), (cx + fw, fy), (cx, fy + band_h * 0.78)]
        paper_sheet(surf, tri, flag_cols[ci], flag_back[ci], SHEEN,
                    shadow_dx=SS * 1.4, shadow_dy=SS * 1.4,
                    sheen_band=[(cx - fw, fy), (cx - fw * 0.2, fy),
                                (cx - fw * 0.4, fy + band_h * 0.35)])
        holes.append((cx, fy + band_h * 0.38, W * 0.07))

    rose_cuts = []
    if top_cap:
        rr = W * 0.42
        ry = H - rr - W * 0.10
        for ring, (col, bk, rad) in enumerate((
                (MARIGOLD, MARI_BACK, rr),
                (MASA, MASA_BACK, rr * 0.66),
                (PINK, PINK_BACK, rr * 0.36))):
            npet = 12 if ring == 0 else 10
            pts = []
            for k in range(npet * 2):
                a = k * math.tau / (npet * 2)
                r = rad if k % 2 == 0 else rad * 0.72
                pts.append((cx + math.cos(a) * r, ry + math.sin(a) * r))
            paper_sheet(surf, pts, col, bk, SHEEN,
                        shadow_dx=SS * 1.6, shadow_dy=SS * 1.6, sheen_band=None)
        for k in range(8):
            a = k * math.tau / 8
            rose_cuts.append((cx + math.cos(a) * rr * 0.5,
                              ry + math.sin(a) * rr * 0.5, rr * 0.085))
        rose_cuts.append((cx, ry, rr * 0.13))
        pygame.draw.circle(surf, INK, (int(cx), int(ry)),
                           int(rr * 0.13 + SS), max(1, int(SS * 0.9)))

    def _cuts(h):
        for fx, fy, fr in holes:
            pygame.draw.circle(h, (255, 255, 255, 255), (int(fx), int(fy)), int(fr))
        for rx, ryy, rr2 in rose_cuts:
            pygame.draw.circle(h, (255, 255, 255, 255), (int(rx), int(ryy)), int(rr2))
    cut_holes(surf, _cuts)

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (width, height))


# ── pure-black silhouette read (accessibility / outline test) ─────────────────

def draw_silhouette(target_size):
    """Flatten the creature to a pure-black mask — proves the signature reads in
    the outline alone: scalloped paper rectangle + bunting arc + punched skull
    sockets cut clean through (the holes stay holes in the mask)."""
    rgba = draw_papelito(target_size)
    mask = pygame.mask.from_surface(rgba)
    surf = mask.to_surface(setcolor=(18, 16, 20, 255), unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    out.blit(surf, (0, 0))
    return out


# ── sky helpers + socket-sample verification ──────────────────────────────────

SKY_TOP = (120, 188, 232)
SKY_BOT = (78, 132, 198)


def sky_panel(w, h):
    s = pygame.Surface((w, h))
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, yy), (w, yy))
    return s


def sample_socket_through(size):
    """Compose the creature over sky at the given size and sample the pixel at the
    LEFT socket centre. Returns (sampled_rgb, expected_sky_rgb). If the punch is a
    real hole the sample matches sky; if it's faked cream it matches CREAM."""
    panel = sky_panel(size, size)
    panel.blit(draw_papelito(size), (0, 0))
    # left socket centre in target-size coords (mirror of draw_papelito layout)
    sx = size * 0.5 - size * 0.105
    sy = size * 0.215 + size * 0.175
    sampled = panel.get_at((int(sx), int(sy)))[:3]
    t = sy / max(1, size - 1)
    expect = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * t) for i in range(3))
    return sampled, expect


# ── sheet composition ─────────────────────────────────────────────────────────

def build_sheet():
    W, H = 1000, 760
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 40, 52))   # warm-dark neutral review backdrop

    font = pygame.font.SysFont("arial", 18, bold=True)
    small = pygame.font.SysFont("arial", 13)

    def label(txt, x, y, col=(245, 238, 226)):
        sheet.blit(font.render(txt, True, col), (x, y))

    def caption(txt, x, y, col=(208, 200, 210)):
        sheet.blit(small.render(txt, True, col), (x, y))

    label("PAPELITO — papel-picado banner-spirit  ·  round 2", 18, 12,
          (252, 224, 150))
    caption("LEAD FACET: CALACA DECORATION — sockets/nose/mouth + perforations "
            "are now TRUE cut-through holes (sky shows through)", 18, 36)

    # Large creature.
    big = draw_papelito(300)
    sheet.blit(big, (24, 60))
    caption("creature · large (300px)", 24, 364)

    # Mid-scale legibility ramp.
    mid = draw_papelito(150)
    sheet.blit(mid, (352, 60))
    caption("creature · 150px", 352, 214)

    # 32px creature + 4x zoom.
    tiny = draw_papelito(32)
    sheet.blit(tiny, (352, 240))
    caption("32px", 352, 274)
    zoom = pygame.transform.scale(tiny, (128, 128))
    sheet.blit(zoom, (392, 240))
    caption("32px @4x", 392, 372)

    # Pure-black silhouette read.
    sil_big = draw_silhouette(150)
    sheet.blit(sil_big, (24, 408))
    caption("silhouette · 150px", 24, 562)
    caption("read: scalloped paper sheet,", 24, 578)
    caption("bunting arc, punched skull cuts", 24, 594)
    sil_tiny = draw_silhouette(32)
    sil_zoom = pygame.transform.scale(sil_tiny, (128, 128))
    sheet.blit(sil_zoom, (200, 408))
    caption("silhouette 32px @4x", 200, 540)

    # SKY-THROUGH-SOCKETS verification — large.
    panel_x = 352
    sheet.blit(sky_panel(160, 160), (panel_x, 408))
    pygame.draw.rect(sheet, (24, 20, 26), (panel_x, 408, 160, 160), 2)
    sheet.blit(draw_papelito(150), (panel_x + 5, 410))
    caption("sky shows THROUGH the cuts", panel_x, 570)
    caption("(punched skull = negative space)", panel_x, 586)

    # 32px on sky.
    sky2_x = panel_x + 168
    sheet.blit(sky_panel(64, 64), (sky2_x, 408))
    pygame.draw.rect(sheet, (24, 20, 26), (sky2_x, 408, 64, 64), 2)
    sheet.blit(pygame.transform.scale(draw_papelito(32), (64, 64)), (sky2_x, 408))
    caption("32px on sky", sky2_x, 474)
    caption("cuts hold", sky2_x, 490)

    # Socket-sample PROOF strip — sample the left socket centre through sky at two
    # scales and print the RGB so the gag is verified numerically, not by eye.
    proof_y = 510
    for i, sz in enumerate((150, 32)):
        sampled, expect = sample_socket_through(sz)
        dist = sum(abs(sampled[k] - expect[k]) for k in range(3))
        cd = sum(abs(sampled[k] - CREAM[k]) for k in range(3))
        ok = dist < cd     # closer to sky than to cream == punched through
        sw_x = sky2_x + i * 0
        py = proof_y + i * 22
        pygame.draw.rect(sheet, sampled, (sw_x, py, 16, 16))
        pygame.draw.rect(sheet, (20, 18, 22), (sw_x, py, 16, 16), 1)
        caption(f"{sz}px socket -> {sampled}  {'sky OK' if ok else 'CREAM!'}",
                sw_x + 22, py + 1, (150, 220, 150) if ok else (240, 150, 150))

    # Prop -> pillar mirror.
    px = 600
    py = 60
    cap_h = 84
    shaft_h = 150
    big_w = 70
    bot_cap = draw_pillar(big_w, cap_h, top_cap=True)
    bot_shaft = draw_pillar(big_w, shaft_h, top_cap=False)
    top_cap = pygame.transform.flip(bot_cap, False, True)
    top_shaft = pygame.transform.flip(bot_shaft, False, True)

    gap = 60
    sheet.blit(top_shaft, (px, py))
    sheet.blit(top_cap, (px, py + shaft_h))
    gap_y = py + shaft_h + cap_h
    sheet.blit(bot_cap, (px, gap_y + gap))
    sheet.blit(bot_shaft, (px, gap_y + gap + cap_h))
    caption("prop->pillar mirror", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 8)
    caption("bunting string + marigold rosette cap", px - 4,
            py + shaft_h * 2 + cap_h * 2 + gap + 24)

    # 32px pillar cap.
    tcap = draw_pillar(30, 42, top_cap=True)
    sheet.blit(tcap, (px + 140, py + 20))
    czoom = pygame.transform.scale(tcap, (120, 168))
    sheet.blit(czoom, (px + 185, py + 20))
    caption("cap 30px / @4x", px + 140, py + 196)
    caption("rosette cap ~shaft +35%", px + 140, py + 212)

    # Palette swatch strip.
    sw_y = H - 54
    swatches = [
        ("cream", CREAM), ("marigold", MARIGOLD), ("pink", PINK),
        ("masa", MASA), ("turq", TURQ), ("cord", CORD),
        ("ink", INK), ("sheen", SHEEN),
    ]
    for i, (nm, col) in enumerate(swatches):
        sx = 420 + i * 72
        pygame.draw.rect(sheet, col, (sx, sw_y, 60, 30))
        pygame.draw.rect(sheet, (20, 18, 22), (sx, sw_y, 60, 30), 2)
        caption(nm, sx + 2, sw_y + 32)

    return sheet


if __name__ == "__main__":
    out = build_sheet()
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(out, dst)
    print("wrote", dst)
    # Console proof of the punch-through at both scales.
    for sz in (300, 150, 32):
        s, e = sample_socket_through(sz)
        cd = sum(abs(s[k] - CREAM[k]) for k in range(3))
        sd = sum(abs(s[k] - e[k]) for k in range(3))
        print(f"socket@{sz}: sampled={s} sky={e} d_sky={sd} d_cream={cd} "
              f"{'THROUGH' if sd < cd else 'FAKED'}")

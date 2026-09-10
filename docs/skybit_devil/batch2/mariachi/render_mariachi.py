"""
Mariachi — the strumming charro skeleton musician (BATCH 2 / Skeletons).

Procedural Pygame, house style: chibi proportions, flat saturated fills + hard
ink keylines, form via the dark-core -> flat-fill -> top-left rim-sheen TRIAD,
silhouette POP via a 1px outline grown from the alpha mask, supersample ->
smoothscale.

Sheet shows the creature AND its prop->pillar mirror (guitarron neck) at both
large and 32px scales, a pure-black silhouette read panel, plus the PINNED
PALETTE swatches.

Round 2 resolves the AD critique: the three load-bearing 32px reads must land
together — (1) flat sombrero DISC, (2) one splayed mid-zapateado KICK leg, and
(3) the round guitarron tilted OFF-AXIS so its body breaks the torso silhouette
edge instead of fusing into a centred lump.

Run headless:  SDL_VIDEODRIVER=dummy python render_mariachi.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (locked brief, exact hexes) ───────────────────────────────
BONE        = (236, 226, 202)   # warm-bone base
BONE_SHADE  = (180, 162, 124)   # tan-bone shade
RUST        = (186,  62,  48)   # rust-red jacket accent
SILVER      = (208, 210, 216)   # silver botonadura button
OCHRE       = (214, 168,  84)   # ochre sombrero
TURQ        = ( 64, 176, 168)   # turquoise rosette
INK         = ( 28,  22,  22)   # keyline ink
SHEEN       = (252, 244, 222)   # top-left rim sheen

# Derived working tones (kept inside the pinned families).
BONE_CORE   = (158, 142, 108)   # dark-core under bone (deeper than tan shade)
OCHRE_CORE  = (158, 120,  52)   # dark-core under sombrero
OCHRE_SHEEN = (244, 210, 140)   # ochre top-left sheen
RUST_CORE   = (122,  38,  30)   # dark-core under jacket rust
RUST_SHEEN  = (224, 110,  86)   # rust top-left sheen
GUITAR_WOOD = (160,  96,  54)   # guitarron rosewood body
GUITAR_CORE = (104,  60,  34)
GUITAR_SHEEN= (206, 150,  96)
SILVER_SHEEN= (242, 244, 248)
SILVER_CORE = (150, 152, 162)

SS = 4   # supersample factor


# ── geometry / triad helpers ─────────────────────────────────────────────────

def _ell(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color,
                        (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def triad_ellipse(surf, cx, cy, rx, ry, core, fill, sheen, outline=INK):
    """dark-core -> flat-fill -> top-left rim-sheen on an ellipse mass, with a
    hard ink keyline. The triad reads as form without any soft gradient."""
    if outline is not None:
        _ell(surf, outline, cx, cy, rx + SS, ry + SS)
    _ell(surf, core, cx, cy, rx, ry)
    _ell(surf, fill, cx, cy, rx - SS * 0.7, ry - SS * 0.7)
    _ell(surf, sheen, cx - rx * 0.34, cy - ry * 0.36, rx * 0.5, ry * 0.42)


def triad_poly(surf, pts, core, fill, sheen, outline=INK, sheen_pts=None):
    """Triad on an arbitrary polygon: ink keyline (fat stroke), core fill, inset
    fill, then an optional top-left sheen sliver polygon."""
    if outline is not None:
        pygame.draw.polygon(surf, outline, pts)
        pygame.draw.polygon(surf, outline, pts, SS * 2)
    pygame.draw.polygon(surf, core, pts)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    inset = [(p[0] + (cx - p[0]) * 0.16, p[1] + (cy - p[1]) * 0.16) for p in pts]
    pygame.draw.polygon(surf, fill, inset)
    if sheen_pts:
        pygame.draw.polygon(surf, sheen, sheen_pts)


def grow_outline(surf, color=INK, thickness=1):
    """1px (post-scale) outline grown from the alpha mask — the silhouette POP.
    Run at supersample scale so it survives smoothscale."""
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) > 2:
        pygame.draw.lines(surf, color, True, outline_pts, max(1, thickness * SS))


def _rot_pts(pts, cx, cy, ang):
    """Rotate a point list about (cx,cy) — used to TILT the guitarron off-axis so
    its body breaks the torso silhouette edge instead of fusing into the centre."""
    ca, sa = math.cos(ang), math.sin(ang)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return out


# ── the creature ─────────────────────────────────────────────────────────────

def draw_mariachi(target_size):
    """Strumming charro calaca: vast circular sombrero DISC with a LOW crown,
    grinning moustachioed skull, broad rust charro jacket with silver botonadura,
    one bone leg planted + one thrown out in a mid-zapateado KICK, and a fat round
    guitarron TILTED across the body so its resonator bumps the right silhouette
    edge as a clearly held instrument."""
    S = target_size * SS
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S * 0.5

    # Layout anchors (fractions of S). Crown dropped low so the dominant read is
    # a wide flat plate, kept clear of Catrina's tall plumed couture brim.
    hat_y   = S * 0.265
    head_y  = S * 0.345
    body_y  = S * 0.56

    # ── BONE LEGS mid-dance-kick (drawn first so jacket overlaps the hips) ─────
    hip_y = S * 0.645

    def bone_limb(p0, p1, p2, w):
        for a, b in ((p0, p1), (p1, p2)):
            pygame.draw.line(surf, INK, a, b, int(w + SS * 1.6))
        for a, b in ((p0, p1), (p1, p2)):
            pygame.draw.line(surf, BONE_SHADE, a, b, int(w))
            pygame.draw.line(surf, BONE, a, b, int(w * 0.5))
        for p in (p0, p1, p2):
            triad_ellipse(surf, p[0], p[1], w * 0.6, w * 0.6,
                          BONE_CORE, BONE, SHEEN)

    legw = S * 0.058
    # Planted leg (player-left): bent at the knee, foot tucked UNDER the body —
    # the weight-bearing stomp anchor of the zapateado.
    bone_limb((cx - S * 0.075, hip_y),
              (cx - S * 0.155, S * 0.79),
              (cx - S * 0.055, S * 0.90), legw)
    # Kicked leg (player-right): thrust OUT on a hard diagonal so the boot-toe is
    # the silhouette's lowest + outermost point — a kick legible in outline alone.
    bone_limb((cx + S * 0.06, hip_y),
              (cx + S * 0.165, S * 0.76),
              (cx + S * 0.345, S * 0.93), legw)
    # Charro boots (rust toe-caps). The kicked boot is exaggerated + pointed so
    # the outline tip reads as a thrown foot, not a round knob.
    triad_ellipse(surf, cx - S * 0.05, S * 0.915, S * 0.058, S * 0.04,
                  RUST_CORE, RUST, RUST_SHEEN)
    boot_tip = _rot_pts([
        (cx + S * 0.30,  S * 0.965),
        (cx + S * 0.30,  S * 0.885),
        (cx + S * 0.405, S * 0.905),
        (cx + S * 0.40,  S * 0.955),
    ], cx + S * 0.345, S * 0.92, 0.0)
    triad_poly(surf, boot_tip, RUST_CORE, RUST, RUST_SHEEN)

    # ── CHARRO JACKET torso (broad short bolero, rust-red) ────────────────────
    # Shoulders widened into a weight-shifted triangle so the body fills under
    # the disc instead of leaving an empty waist.
    jacket = [
        (cx - S * 0.185, body_y - S * 0.055),
        (cx + S * 0.185, body_y - S * 0.055),
        (cx + S * 0.165, hip_y),
        (cx + S * 0.08,  hip_y + S * 0.014),
        (cx,             hip_y - S * 0.012),
        (cx - S * 0.08,  hip_y + S * 0.014),
        (cx - S * 0.165, hip_y),
    ]
    triad_poly(surf, jacket, RUST_CORE, RUST, RUST_SHEEN,
               sheen_pts=[(cx - S * 0.155, body_y - S * 0.035),
                          (cx - S * 0.04,  body_y - S * 0.045),
                          (cx - S * 0.07,  body_y + S * 0.06),
                          (cx - S * 0.155, body_y + S * 0.05)])
    # Bone neck/sternum peeking above the jacket lapels.
    triad_ellipse(surf, cx, body_y - S * 0.082, S * 0.052, S * 0.058,
                  BONE_CORE, BONE, SHEEN)

    # Botonadura: silver button rows down both jacket sides (charro signature),
    # on the outer lapel edges so the tilted guitarron can't occlude them.
    for side in (-1, 1):
        for i in range(3):
            byp = body_y - S * 0.02 + i * S * 0.048
            bxp = cx + side * (S * 0.155 - i * S * 0.006)
            triad_ellipse(surf, bxp, byp, S * 0.02, S * 0.02,
                          SILVER_CORE, SILVER, SILVER_SHEEN)

    # ── ROUND GUITARRON tilted across the body (player-right, off-axis) ────────
    # Pushed off-centre and rotated so the resonator BREAKS the torso's right
    # silhouette edge as a secondary round bump = "held instrument", never a
    # body-centred shield/idol. An ink gap + sheen keep the disc edge legible
    # through the 1x alpha-outline.
    tilt = -0.42                       # neck up-left, body down-right
    gx, gy = cx + S * 0.16, body_y + S * 0.085
    grx, gry = S * 0.16, S * 0.155

    # Ink separation halo so the wood disc never merges with the rust jacket.
    _ell(surf, INK, gx, gy, grx + SS * 2.2, gry + SS * 2.2)
    triad_ellipse(surf, gx, gy, grx, gry, GUITAR_CORE, GUITAR_WOOD, GUITAR_SHEEN)
    # Sound hole + turquoise rosette ring (the single cool spark).
    triad_ellipse(surf, gx - S * 0.006, gy - S * 0.008, S * 0.058, S * 0.058,
                  (40, 30, 24), (54, 38, 30), (90, 64, 48), outline=None)
    pygame.draw.circle(surf, TURQ, (int(gx - S * 0.006), int(gy - S * 0.008)),
                       int(S * 0.07), int(SS * 1.6))
    pygame.draw.circle(surf, SHEEN, (int(gx - S * 0.006), int(gy - S * 0.008)),
                       int(S * 0.07), int(SS * 0.5))

    # Short angled NECK rising up-left off the resonator toward the strumming
    # shoulder — reinforces the diagonal "carried across the body" read.
    neck_base = (gx - grx * 0.3, gy - gry * 0.85)
    neck_pts = _rot_pts([
        (gx - S * 0.03, gy - gry * 0.4),
        (gx + S * 0.03, gy - gry * 0.4),
        (gx + S * 0.018, gy - gry * 2.4),
        (gx - S * 0.018, gy - gry * 2.4),
    ], gx, gy, tilt)
    triad_poly(surf, neck_pts, GUITAR_CORE, GUITAR_WOOD, GUITAR_SHEEN)
    # Headstock tuning block at the neck tip.
    head_tip = neck_pts[2]
    head_top = neck_pts[3]
    htx = (head_tip[0] + head_top[0]) / 2
    hty = (head_tip[1] + head_top[1]) / 2
    triad_ellipse(surf, htx, hty, S * 0.032, S * 0.026,
                  GUITAR_CORE, GUITAR_WOOD, GUITAR_SHEEN)

    # Strings fanning from the bridge up the neck.
    for k in range(-1, 2):
        pygame.draw.line(surf, BONE,
                         (gx + k * S * 0.014, gy + gry * 0.45),
                         (htx + k * S * 0.006, hty),
                         max(1, int(SS * 0.6)))

    # Bone strumming hand on the lower body, fingers spread over the strings.
    triad_ellipse(surf, gx - S * 0.012, gy + S * 0.07, S * 0.05, S * 0.04,
                  BONE_CORE, BONE, SHEEN)
    for f in range(3):
        fx = gx - S * 0.05 + f * S * 0.024
        pygame.draw.line(surf, INK, (fx, gy + S * 0.06),
                         (fx + S * 0.004, gy + S * 0.115), max(1, int(SS)))
        pygame.draw.line(surf, BONE, (fx, gy + S * 0.06),
                         (fx + S * 0.004, gy + S * 0.115), max(1, int(SS * 0.5)))

    # ── SKULL head (small, grinning) ──────────────────────────────────────────
    triad_ellipse(surf, cx, head_y, S * 0.135, S * 0.145,
                  BONE_CORE, BONE, SHEEN)
    triad_ellipse(surf, cx, head_y + S * 0.09, S * 0.10, S * 0.062,
                  BONE_CORE, BONE, SHEEN)
    # Eye sockets — DotD style, with a tiny ochre marigold petal ring.
    for ex in (cx - S * 0.052, cx + S * 0.052):
        triad_ellipse(surf, ex, head_y - S * 0.01, S * 0.034, S * 0.038,
                      (40, 28, 26), (58, 40, 36), (96, 70, 60), outline=None)
        for k in range(8):
            a = k * math.tau / 8
            px = ex + math.cos(a) * S * 0.044
            py = (head_y - S * 0.01) + math.sin(a) * S * 0.05
            pygame.draw.circle(surf, OCHRE, (int(px), int(py)), max(1, int(SS * 1.1)))
        pygame.draw.circle(surf, INK, (int(ex), int(head_y - S * 0.01)),
                           int(S * 0.016))
    # Nose triangle.
    pygame.draw.polygon(surf, (40, 28, 26), [
        (cx, head_y + S * 0.022),
        (cx - S * 0.016, head_y + S * 0.055),
        (cx + S * 0.016, head_y + S * 0.055),
    ])
    # Grinning stitched smile.
    sm_y = head_y + S * 0.082
    pygame.draw.arc(surf, INK,
                    (cx - S * 0.072, sm_y - S * 0.04, S * 0.144, S * 0.08),
                    math.pi * 1.05, math.pi * 1.95, max(1, int(SS * 1.6)))
    for k in range(-3, 4):
        tx = cx + k * S * 0.02
        pygame.draw.line(surf, INK, (tx, sm_y - S * 0.012),
                         (tx, sm_y + S * 0.014), max(1, int(SS)))
    # Curly painted moustache (rust to read warm against bone).
    for side in (-1, 1):
        msx = cx + side * S * 0.02
        pts = [(int(cx), int(head_y + S * 0.06))]
        for t in range(0, 11):
            tt = t / 10.0
            ang = tt * math.pi * 1.5
            mx = msx + side * (S * 0.02 + tt * S * 0.052)
            my = head_y + S * 0.066 + math.sin(ang) * S * 0.018 + tt * S * 0.006
            pts.append((int(mx), int(my)))
        pygame.draw.lines(surf, INK, False, pts, max(2, int(SS * 2.2)))
        pygame.draw.lines(surf, RUST, False, pts, max(1, int(SS * 1.2)))

    # ── VAST CIRCULAR SOMBRERO — flat disc brim (the dominant read) ───────────
    # Thin ink underside band first so the disc edge + the face beneath survive
    # against warm desert/ochre AND dark night skies.
    _ell(surf, INK, cx, hat_y + S * 0.018, S * 0.405, S * 0.118)
    triad_ellipse(surf, cx, hat_y, S * 0.40, S * 0.112,
                  OCHRE_CORE, OCHRE, OCHRE_SHEEN)
    # Embroidered brim band: rust + turquoise stitch ring near the rim edge.
    pygame.draw.ellipse(surf, RUST,
                        (cx - S * 0.36, hat_y - S * 0.090,
                         S * 0.72, S * 0.18), max(2, int(SS * 1.8)))
    pygame.draw.ellipse(surf, TURQ,
                        (cx - S * 0.31, hat_y - S * 0.076,
                         S * 0.62, S * 0.152), max(1, int(SS)))
    # LOW rounded crown (dropped ~38% vs round 1) so the wide plate dominates and
    # never edges toward a couture block.
    crown = [
        (cx - S * 0.105, hat_y - S * 0.010),
        (cx - S * 0.085, hat_y - S * 0.072),
        (cx - S * 0.045, hat_y - S * 0.095),
        (cx + S * 0.045, hat_y - S * 0.095),
        (cx + S * 0.085, hat_y - S * 0.072),
        (cx + S * 0.105, hat_y - S * 0.010),
    ]
    triad_poly(surf, crown, OCHRE_CORE, OCHRE, OCHRE_SHEEN,
               sheen_pts=[(cx - S * 0.09, hat_y - S * 0.015),
                          (cx - S * 0.05, hat_y - S * 0.085),
                          (cx - S * 0.01, hat_y - S * 0.09),
                          (cx - S * 0.04, hat_y - S * 0.015)])
    # Crown band (rust) + silver concha.
    pygame.draw.line(surf, RUST,
                     (cx - S * 0.092, hat_y - S * 0.018),
                     (cx + S * 0.092, hat_y - S * 0.018), max(2, int(SS * 2)))
    triad_ellipse(surf, cx, hat_y - S * 0.022, S * 0.02, S * 0.02,
                  SILVER_CORE, SILVER, SILVER_SHEEN)

    grow_outline(surf, INK, 1)
    out = pygame.transform.smoothscale(surf, (target_size, target_size))
    return out


# ── the prop -> pillar mirror (guitarron neck) ───────────────────────────────

def draw_pillar(width, height, top_cap=True):
    """Upright guitarron / guitar neck pillar. Fretted neck = repeatable shaft
    body (fret banding); round sound-hole body with a turquoise rosette =
    detachable gap-edge cap. Cap nudged to ~shaft +35% so it doesn't go
    top-heavy at the gap line."""
    W = width * SS
    H = height * SS
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W * 0.5

    neck_w = W * 0.34
    neck = pygame.Rect(int(cx - neck_w / 2), 0, int(neck_w), int(H))
    pygame.draw.rect(surf, GUITAR_CORE, neck)
    inner = neck.inflate(-int(SS * 3), 0)
    pygame.draw.rect(surf, GUITAR_WOOD, inner)
    pygame.draw.rect(surf, GUITAR_SHEEN,
                     (int(cx - neck_w / 2 + SS * 2), 0,
                      int(neck_w * 0.26), int(H)))
    fret_n = max(4, int(height / 14))
    for i in range(1, fret_n):
        fy = int(H * i / fret_n)
        pygame.draw.line(surf, SILVER,
                         (cx - neck_w / 2, fy), (cx + neck_w / 2, fy),
                         max(1, int(SS)))
        pygame.draw.circle(surf, SILVER_SHEEN,
                           (int(cx), fy), max(1, int(SS * 0.8)))
    for k in (-1, 1):
        pygame.draw.line(surf, BONE,
                         (cx + k * neck_w * 0.14, 0),
                         (cx + k * neck_w * 0.14, H), max(1, int(SS * 0.7)))

    # Gap-edge cap: round resonator body sized to ~shaft +35% so the mirror stays
    # balanced at the gap line (Cernun/Raijin discipline).
    if top_cap:
        body_r = neck_w * 0.675   # ~shaft width +35% per radius
        by = H - body_r - W * 0.04
        triad_ellipse(surf, cx, by, body_r, body_r * 0.92,
                      GUITAR_CORE, GUITAR_WOOD, GUITAR_SHEEN)
        triad_ellipse(surf, cx, by, body_r * 0.34, body_r * 0.34,
                      (40, 30, 24), (54, 38, 30), (90, 64, 48), outline=None)
        pygame.draw.circle(surf, TURQ, (int(cx), int(by)),
                           int(body_r * 0.42), max(2, int(SS * 1.6)))
        pygame.draw.circle(surf, SHEEN, (int(cx), int(by)),
                           int(body_r * 0.42), max(1, int(SS * 0.6)))
        for k in range(-1, 2):
            pygame.draw.line(surf, BONE,
                             (cx + k * body_r * 0.12, by + body_r * 0.6),
                             (cx + k * neck_w * 0.14, by - body_r),
                             max(1, int(SS * 0.7)))

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (width, height))


# ── pure-black silhouette read (accessibility / outline test) ─────────────────

def draw_silhouette(target_size):
    """Flatten the creature to a pure-black mask — proves the three pinned reads
    survive in the outline alone: flat disc + splayed kick leg + off-axis bump."""
    rgba = draw_mariachi(target_size)
    sil = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(rgba)
    for x, y in mask.outline():
        pass
    # Fill every opaque pixel solid black.
    surf = mask.to_surface(setcolor=(18, 16, 20, 255), unsetcolor=(0, 0, 0, 0))
    sil.blit(surf, (0, 0))
    return sil


# ── sheet composition ─────────────────────────────────────────────────────────

def build_sheet():
    W, H = 980, 700
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 40, 52))   # warm-dark neutral review backdrop

    font = pygame.font.SysFont("arial", 18, bold=True)
    small = pygame.font.SysFont("arial", 13)

    def label(txt, x, y, col=(245, 238, 226)):
        sheet.blit(font.render(txt, True, col), (x, y))

    def caption(txt, x, y, col=(208, 200, 210)):
        sheet.blit(small.render(txt, True, col), (x, y))

    label("MARIACHI — strumming charro skeleton musician  ·  round 2", 18, 12,
          (252, 224, 150))
    caption("warm-bone + rust-red + ochre · warm festive (vs Catrina's cool couture)",
            18, 36)

    # Large creature.
    big = draw_mariachi(300)
    sheet.blit(big, (24, 60))
    caption("creature · large", 24, 362)

    # Mid-scale legibility ramp.
    mid = draw_mariachi(150)
    sheet.blit(mid, (350, 60))
    caption("creature · 150px", 350, 218)

    # 32px creature + 4x zoom.
    tiny = draw_mariachi(32)
    sheet.blit(tiny, (350, 248))
    caption("32px", 350, 282)
    zoom = pygame.transform.scale(tiny, (128, 128))
    sheet.blit(zoom, (392, 248))
    caption("32px @4x", 392, 378)

    # Pure-black silhouette read (creature scale + 32px@4x) — the AD ship test.
    sil_big = draw_silhouette(150)
    sheet.blit(sil_big, (24, 408))
    caption("silhouette · 150px", 24, 560)
    sil_tiny = draw_silhouette(32)
    sil_zoom = pygame.transform.scale(sil_tiny, (128, 128))
    sheet.blit(sil_zoom, (188, 408))
    caption("silhouette 32px @4x", 188, 538)
    caption("read: hatted musician kicking", 188, 554)

    # Prop -> pillar mirror (guitarron neck).
    px = 560
    py = 60
    cap_h = 88
    shaft_h = 150
    big_w = 64
    bot_cap = draw_pillar(big_w, cap_h, top_cap=True)
    bot_shaft = draw_pillar(big_w, shaft_h, top_cap=False)
    top_cap = pygame.transform.flip(bot_cap, False, True)
    top_shaft = pygame.transform.flip(bot_shaft, False, True)

    gap = 64
    sheet.blit(top_shaft, (px, py))
    sheet.blit(top_cap, (px, py + shaft_h))
    gap_y = py + shaft_h + cap_h
    sheet.blit(bot_cap, (px, gap_y + gap))
    sheet.blit(bot_shaft, (px, gap_y + gap + cap_h))
    caption("prop->pillar mirror", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 6)
    caption("guitarron neck", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 22)

    # 32px pillar cap (judge the gap-edge read small).
    tcap = draw_pillar(28, 40, top_cap=True)
    sheet.blit(tcap, (px + 120, py + 20))
    czoom = pygame.transform.scale(tcap, (112, 160))
    sheet.blit(czoom, (px + 160, py + 20))
    caption("cap 28px / @4x", px + 120, py + 188)
    caption("cap ~shaft +35%", px + 120, py + 204)

    # Palette swatch strip.
    sw_y = H - 56
    swatches = [
        ("bone", BONE), ("tan", BONE_SHADE), ("rust", RUST),
        ("silver", SILVER), ("ochre", OCHRE), ("turq", TURQ),
        ("ink", INK), ("sheen", SHEEN),
    ]
    for i, (nm, col) in enumerate(swatches):
        sx = 420 + i * 70
        pygame.draw.rect(sheet, col, (sx, sw_y, 58, 30))
        pygame.draw.rect(sheet, (20, 18, 22), (sx, sw_y, 58, 30), 2)
        caption(nm, sx + 2, sw_y + 32)

    return sheet


if __name__ == "__main__":
    out = build_sheet()
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(out, dst)
    print("wrote", dst)

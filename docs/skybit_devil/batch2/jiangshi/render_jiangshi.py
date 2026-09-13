"""
Round-1 concept renderer for JIANGSHI — the talisman-sealed hopping Qing corpse
(Batch 2 / Section 2 Skeletons). Headless Pygame; supersample → smoothscale to
match the house grammar (chibi, flat fills, hard ink keyline, dark-core →
flat-fill → top-left rim-sheen triad, 1px alpha-grown outline).

WHY a standalone script: review art must never enter the shipped bundle, so it
lives under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief — exact hexes) ──────────────────────────────
SKIN      = (120, 158, 118)   # jade-corpse skin base
SKIN_D    = ( 76, 112,  80)   # deep-jade shade (dark core)
ROBE      = (124,  52,  72)   # rust-plum robe (NOT indigo)
ROBE_D    = ( 84,  34,  50)   # deep rust-plum shade
ROBE_T    = (158,  78, 100)   # rust-plum rim-sheen helper
TAL_CREAM = (238, 224, 176)   # talisman cream paper
CINNABAR  = (206,  52,  42)   # cinnabar brush strokes / lantern / rank-badge
CINNA_D   = (150,  34,  30)   # deep cinnabar shade
GOLD      = (222, 184,  86)   # gold hat-trim
GOLD_D    = (168, 132,  54)
INK       = ( 24,  30,  26)   # hard ink keyline
SHEEN     = (176, 206, 166)   # jade rim-sheen (top-left)
QUEUE     = ( 34,  30,  34)   # black queue braid
QUEUE_H   = ( 70,  66,  74)

BG        = ( 70,  92, 120)   # neutral slate review backdrop
PANEL     = ( 52,  70,  94)
LABEL     = (236, 238, 240)
LABEL_DIM = (176, 190, 206)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (1px at native, so SS*1 at supersample) ─
def grow_outline(surf, color, px):
    """Halo the opaque silhouette with `px` of `color` — the house keyline."""
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    # Stamp filled discs along the silhouette edge, then re-lay the art on top.
    for (ox, oy) in outline_pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.45), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.35), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


# ── the creature ─────────────────────────────────────────────────────────────
def draw_jiangshi(surf, cx, cy, s):
    """Chibi hopping corpse, arms locked straight FORWARD (T-of-arms),
    tall winged mandarin court hat, brow talisman, queue braid behind.
    `s` is a unit scale; geometry is authored around a ~120-unit-tall figure."""

    # --- long queue braid trailing behind (drawn first, sits behind body) ---
    braid_x = cx + int(34*s)
    bx = [braid_x, braid_x + int(10*s), braid_x + int(4*s),
          braid_x + int(14*s), braid_x + int(8*s)]
    by = [cy - int(36*s), cy - int(10*s), cy + int(14*s),
          cy + int(38*s), cy + int(60*s)]
    pts = list(zip(bx, by))
    for i in range(len(pts)-1):
        pygame.draw.line(surf, INK, pts[i], pts[i+1], int(9*s)+2)
    for i in range(len(pts)-1):
        pygame.draw.line(surf, QUEUE, pts[i], pts[i+1], int(8*s))
    for i in range(len(pts)-1):
        pygame.draw.line(surf, QUEUE_H, pts[i], pts[i+1], max(1, int(2*s)))
    # red braid-tie at the tail
    tie = pts[-1]
    pygame.draw.circle(surf, INK, tie, int(5*s))
    pygame.draw.circle(surf, CINNABAR, tie, int(4*s))
    pygame.draw.circle(surf, lerp(CINNABAR, (255,255,255), 0.4),
                       (tie[0]-int(1*s), tie[1]-int(1*s)), max(1, int(1.5*s)))

    # --- boxy robe body (rigid Qing official changpao) ---
    bw, bh = int(56*s), int(78*s)
    bx0, by0 = cx - bw//2, cy - int(8*s)
    body = [(bx0, by0), (bx0+bw, by0), (bx0+bw, by0+bh),
            (bx0+bw-int(8*s), by0+bh), (cx, by0+bh-int(4*s)),
            (bx0+int(8*s), by0+bh), (bx0, by0+bh)]
    triad_blob(
        surf, ROBE, body,
        core_pts=[(cx, by0+int(10*s)), (bx0+bw, by0+int(20*s)),
                  (bx0+bw, by0+bh), (cx, by0+bh-int(4*s))],
        sheen_pts=[(bx0+int(3*s), by0+int(2*s)), (cx-int(2*s), by0+int(2*s)),
                   (cx-int(2*s), by0+bh-int(6*s)), (bx0+int(3*s), by0+bh-int(10*s))],
        ow=int(2*s)+1,
    )
    # robe centre seam + lower hem band (gold trim)
    pygame.draw.line(surf, ROBE_D, (cx, by0+int(4*s)), (cx, by0+bh-int(6*s)), int(2*s))
    pygame.draw.rect(surf, GOLD, (bx0+int(2*s), by0+bh-int(12*s), bw-int(4*s), int(7*s)))
    pygame.draw.rect(surf, GOLD_D, (bx0+int(2*s), by0+bh-int(6*s), bw-int(4*s), int(2*s)))
    pygame.draw.rect(surf, INK, (bx0+int(2*s), by0+bh-int(12*s), bw-int(4*s), int(7*s)), max(1,int(1*s)))

    # --- round rank-badge (buzi) on the chest, cinnabar with gold ring ---
    badge = (cx, by0 + int(30*s))
    pygame.draw.circle(surf, INK, badge, int(15*s)+1)
    pygame.draw.circle(surf, GOLD, badge, int(15*s))
    pygame.draw.circle(surf, CINNABAR, badge, int(12*s))
    pygame.draw.circle(surf, CINNA_D, badge, int(12*s), max(1, int(1.5*s)))
    # stylised crane glyph: simple gold bird mark
    pygame.draw.circle(surf, GOLD, (badge[0], badge[1]-int(2*s)), int(4*s))
    pygame.draw.polygon(surf, GOLD, [(badge[0], badge[1]+int(1*s)),
                                     (badge[0]-int(5*s), badge[1]+int(7*s)),
                                     (badge[0]+int(5*s), badge[1]+int(7*s))])
    pygame.draw.circle(surf, lerp(CINNABAR,(255,255,255),0.3),
                       (badge[0]-int(4*s), badge[1]-int(4*s)), max(1,int(2*s)))

    # --- tiny feet together mid-hop (just below hem) ---
    fy = by0 + bh
    for fx in (cx-int(8*s), cx+int(8*s)):
        triad_blob(surf, ROBE_D,
                   [(fx-int(7*s), fy), (fx+int(7*s), fy),
                    (fx+int(8*s), fy+int(9*s)), (fx-int(8*s), fy+int(9*s))],
                   ow=max(1,int(1.5*s)))
        pygame.draw.rect(surf, INK, (fx-int(8*s), fy+int(7*s), int(16*s), int(3*s)))
        pygame.draw.rect(surf, (236,236,236), (fx-int(8*s), fy+int(7*s), int(16*s), int(2*s)))

    # --- both arms locked straight FORWARD (T-of-arms) — toward viewer-left ---
    arm_y = by0 + int(16*s)
    aw, ah = int(46*s), int(15*s)
    ax1 = bx0 - aw
    arm = [(ax1, arm_y), (bx0+int(4*s), arm_y),
           (bx0+int(4*s), arm_y+ah), (ax1, arm_y+ah)]
    triad_blob(
        surf, ROBE, arm,
        core_pts=[(ax1, arm_y+ah-int(5*s)), (bx0+int(4*s), arm_y+ah-int(3*s)),
                  (bx0+int(4*s), arm_y+ah), (ax1, arm_y+ah)],
        sheen_pts=[(ax1+int(2*s), arm_y+int(1*s)), (bx0, arm_y+int(1*s)),
                   (bx0, arm_y+int(4*s)), (ax1+int(2*s), arm_y+int(4*s))],
        ow=int(2*s)+1,
    )
    # gold cuff + outstretched jade hands w/ long black claw-nails
    pygame.draw.rect(surf, GOLD, (ax1, arm_y, int(7*s), ah))
    pygame.draw.rect(surf, INK, (ax1, arm_y, int(7*s), ah), max(1,int(1*s)))
    hand_c = (ax1-int(8*s), arm_y+ah//2)
    triad_blob(surf, SKIN,
               [(hand_c[0]-int(9*s), arm_y+int(1*s)),
                (hand_c[0]+int(8*s), arm_y+int(1*s)),
                (hand_c[0]+int(8*s), arm_y+ah-int(1*s)),
                (hand_c[0]-int(9*s), arm_y+ah-int(1*s))],
               sheen_pts=[(hand_c[0]-int(8*s), arm_y+int(2*s)),
                          (hand_c[0]+int(2*s), arm_y+int(2*s)),
                          (hand_c[0]+int(2*s), arm_y+int(5*s)),
                          (hand_c[0]-int(8*s), arm_y+int(5*s))],
               ow=max(1,int(1.5*s)))
    for i in range(3):
        ny = arm_y + int(3*s) + i*int(4*s)
        pygame.draw.line(surf, INK, (hand_c[0]-int(9*s), ny),
                         (hand_c[0]-int(14*s), ny), max(1,int(2*s)))

    # --- greenish skull-face (head) ---
    hr = int(26*s)
    hc = (cx, by0 - int(20*s))
    triad_blob(
        surf, SKIN,
        [(hc[0]-hr, hc[1]-hr), (hc[0]+hr, hc[1]-hr),
         (hc[0]+hr, hc[1]+hr), (hc[0]-hr, hc[1]+hr)],
        core_pts=[(hc[0]+int(6*s), hc[1]-int(2*s)), (hc[0]+hr, hc[1]),
                  (hc[0]+hr, hc[1]+hr), (hc[0]-int(6*s), hc[1]+hr)],
        sheen_pts=[(hc[0]-hr+int(2*s), hc[1]-hr+int(2*s)),
                   (hc[0]-int(2*s), hc[1]-hr+int(2*s)),
                   (hc[0]-int(2*s), hc[1]+int(2*s)),
                   (hc[0]-hr+int(2*s), hc[1]+int(2*s))],
        ow=int(2*s)+1,
    )
    # round the face slightly with a jade overlay-circle for chibi softness
    pygame.draw.circle(surf, SKIN, hc, hr-int(1*s))
    pygame.draw.circle(surf, INK, hc, hr, int(2*s)+1)
    pygame.draw.circle(surf, lerp(SKIN, SHEEN, 0.7),
                       (hc[0]-int(10*s), hc[1]-int(10*s)), int(6*s))
    # sunken dark eye-sockets with glowing pin-points (cute menace)
    for ex in (hc[0]-int(11*s), hc[0]+int(11*s)):
        ey = hc[1] + int(2*s)
        pygame.draw.circle(surf, SKIN_D, (ex, ey), int(7*s))
        pygame.draw.circle(surf, INK, (ex, ey), int(5*s))
        pygame.draw.circle(surf, CINNABAR, (ex, ey), int(3*s))
        pygame.draw.circle(surf, (255, 230, 200), (ex-int(1*s), ey-int(1*s)), max(1,int(1.5*s)))
    # nose hollow + stitched grim-cute mouth
    pygame.draw.polygon(surf, SKIN_D, [(hc[0]-int(2*s), hc[1]+int(8*s)),
                                       (hc[0]+int(2*s), hc[1]+int(8*s)),
                                       (hc[0], hc[1]+int(12*s))])
    my = hc[1] + int(16*s)
    pygame.draw.line(surf, INK, (hc[0]-int(10*s), my), (hc[0]+int(10*s), my), max(1,int(2*s)))
    for sx in range(-8, 9, 4):
        pygame.draw.line(surf, INK, (hc[0]+int(sx*s), my-int(2*s)),
                         (hc[0]+int(sx*s), my+int(2*s)), max(1,int(1*s)))

    # --- yellow paper talisman on the brow (red brush-strokes, cinnabar seal) ---
    tw, th = int(16*s), int(30*s)
    tx, ty = hc[0]-tw//2, hc[1]-hr-int(6*s)
    pygame.draw.rect(surf, INK, (tx-1, ty-1, tw+2, th+2))
    pygame.draw.rect(surf, TAL_CREAM, (tx, ty, tw, th))
    pygame.draw.rect(surf, lerp(TAL_CREAM,(255,255,255),0.4), (tx+int(1*s), ty+int(1*s), tw-int(3*s), int(4*s)))
    # vertical column of cinnabar brush glyphs
    for i in range(3):
        gy = ty + int(6*s) + i*int(8*s)
        pygame.draw.line(surf, CINNABAR, (hc[0]-int(3*s), gy), (hc[0]+int(3*s), gy), max(1,int(2*s)))
        pygame.draw.line(surf, CINNABAR, (hc[0], gy-int(2*s)), (hc[0], gy+int(2*s)), max(1,int(2*s)))
    # red square seal at the foot
    pygame.draw.rect(surf, CINNA_D, (hc[0]-int(3*s), ty+th-int(7*s), int(6*s), int(6*s)))

    # --- tall winged mandarin court hat (sits over the talisman top) ---
    hat_base_y = hc[1] - hr + int(3*s)
    # crown — tapering tall block
    crown = [(hc[0]-int(16*s), hat_base_y), (hc[0]+int(16*s), hat_base_y),
             (hc[0]+int(11*s), hat_base_y-int(34*s)),
             (hc[0]-int(11*s), hat_base_y-int(34*s))]
    triad_blob(
        surf, INK,
        [(hc[0]-int(18*s), hat_base_y+int(2*s)), (hc[0]+int(18*s), hat_base_y+int(2*s)),
         (hc[0]+int(13*s), hat_base_y-int(36*s)), (hc[0]-int(13*s), hat_base_y-int(36*s))],
        outline=False,
    )
    pygame.draw.polygon(surf, (44, 40, 50), crown)
    pygame.draw.polygon(surf, lerp((44,40,50),(255,255,255),0.25),
                        [(hc[0]-int(16*s), hat_base_y), (hc[0]-int(6*s), hat_base_y),
                         (hc[0]-int(5*s), hat_base_y-int(34*s)),
                         (hc[0]-int(11*s), hat_base_y-int(34*s))])
    pygame.draw.polygon(surf, INK, crown, int(2*s)+1)
    # gold brim band + top knob
    pygame.draw.rect(surf, GOLD, (hc[0]-int(18*s), hat_base_y-int(2*s), int(36*s), int(6*s)))
    pygame.draw.rect(surf, INK, (hc[0]-int(18*s), hat_base_y-int(2*s), int(36*s), int(6*s)), max(1,int(1*s)))
    pygame.draw.circle(surf, GOLD, (hc[0], hat_base_y-int(36*s)), int(4*s))
    pygame.draw.circle(surf, INK, (hc[0], hat_base_y-int(36*s)), int(4*s), max(1,int(1*s)))
    # the two side WINGS (futou flaps) — the mandarin court-hat tell
    for sgn in (-1, 1):
        wy = hat_base_y - int(14*s)
        wing = [(hc[0]+sgn*int(15*s), wy),
                (hc[0]+sgn*int(34*s), wy-int(4*s)),
                (hc[0]+sgn*int(34*s), wy+int(7*s)),
                (hc[0]+sgn*int(15*s), wy+int(9*s))]
        pygame.draw.polygon(surf, INK, wing)
        pygame.draw.polygon(surf, (44, 40, 50), wing)
        pygame.draw.polygon(surf, GOLD, [(hc[0]+sgn*int(30*s), wy-int(2*s)),
                                         (hc[0]+sgn*int(33*s), wy),
                                         (hc[0]+sgn*int(31*s), wy+int(4*s))])
        pygame.draw.polygon(surf, INK, wing, max(1,int(1.5*s)))


# ── the prop → pillar mirror (talisman-scroll / lantern-pole) ────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """Pole strung with hanging paper talismans = repeatable shaft band;
    red paper LANTERN = gap-edge cap. `cap` end faces the gap."""
    shaft_w = int(16*s)
    # repeatable shaft: dark-edged plum pole
    pygame.draw.rect(surf, INK, (cx-shaft_w//2-1, top, shaft_w+2, bot-top))
    pygame.draw.rect(surf, ROBE, (cx-shaft_w//2, top, shaft_w, bot-top))
    pygame.draw.rect(surf, ROBE_D, (cx+shaft_w//2-int(5*s), top, int(5*s), bot-top))
    pygame.draw.rect(surf, ROBE_T, (cx-shaft_w//2, top, int(4*s), bot-top))
    # talisman bands strung down the pole (each a body band)
    band = top + int(18*s)
    while band < bot - int(22*s):
        tw, th = int(20*s), int(26*s)
        tx = cx - tw//2
        # peg the talisman to one side, alternating, so it reads as "hung"
        pygame.draw.rect(surf, INK, (tx-1, band-1, tw+2, th+2))
        pygame.draw.rect(surf, TAL_CREAM, (tx, band, tw, th))
        pygame.draw.rect(surf, lerp(TAL_CREAM,(255,255,255),0.4),
                         (tx+int(1*s), band+int(1*s), tw-int(3*s), int(4*s)))
        for i in range(3):
            gy = band + int(5*s) + i*int(7*s)
            pygame.draw.line(surf, CINNABAR, (cx-int(3*s), gy), (cx+int(3*s), gy), max(1,int(2*s)))
            pygame.draw.line(surf, CINNABAR, (cx, gy-int(2*s)), (cx, gy+int(2*s)), max(1,int(2*s)))
        pygame.draw.rect(surf, CINNA_D, (cx-int(3*s), band+th-int(6*s), int(6*s), int(5*s)))
        band += int(36*s)

    # red paper LANTERN gap-edge cap (round on-axis, glows at the gap)
    ly = bot - int(8*s) if cap == "bottom" else top + int(8*s)
    lr = int(20*s)
    # warm glow halo behind the lantern
    glow = pygame.Surface((lr*4, lr*4), pygame.SRCALPHA)
    for r in range(lr*2, 0, -1):
        a = int(70 * (1 - r/(lr*2)))
        pygame.draw.circle(glow, (*CINNABAR, a), (lr*2, lr*2), r)
    surf.blit(glow, (cx-lr*2, ly-lr*2), special_flags=pygame.BLEND_ADD)
    # gold cap fittings top & bottom of lantern
    for off in (-lr-int(3*s), lr-int(1*s)):
        pygame.draw.rect(surf, GOLD, (cx-int(6*s), ly+off, int(12*s), int(5*s)))
        pygame.draw.rect(surf, INK, (cx-int(6*s), ly+off, int(12*s), int(5*s)), max(1,int(1*s)))
    # lantern body — triad-lit cinnabar ellipse
    rect = pygame.Rect(cx-lr, ly-int(lr*1.15), lr*2, int(lr*2.3))
    pygame.draw.ellipse(surf, INK, rect.inflate(int(3*s), int(3*s)))
    pygame.draw.ellipse(surf, CINNABAR, rect)
    dark = rect.copy(); dark.left = cx
    pygame.draw.ellipse(surf, CINNA_D, dark)
    pygame.draw.ellipse(surf, lerp(CINNABAR,(255,255,255),0.45),
                        pygame.Rect(cx-lr+int(3*s), ly-int(lr*0.9), int(lr*0.7), int(lr*0.9)))
    pygame.draw.ellipse(surf, INK, rect, int(2*s)+1)
    # vertical lantern ribs + a tiny cinnabar tassel
    for rx in (-int(7*s), 0, int(7*s)):
        pygame.draw.line(surf, CINNA_D, (cx+rx, ly-int(lr*1.0)), (cx+rx, ly+int(lr*1.0)), max(1,int(1*s)))
    ty = ly + lr + int(4*s)
    pygame.draw.line(surf, CINNABAR, (cx, ty), (cx, ty+int(10*s)), max(1,int(2*s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 4   # supersample factor


def render_big(draw_fn, w, h):
    """Render at SSx then smoothscale down — the project's anti-alias path."""
    big = pygame.Surface((w*SS, h*SS), pygame.SRCALPHA)
    draw_fn(big)
    small = pygame.transform.smoothscale(big, (w, h))
    return grow_outline(small, INK + (255,), 1)


def main():
    W, H = 980, 760
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 13)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    # title bar
    pygame.draw.rect(sheet, PANEL, (0, 0, W, 54))
    sheet.blit(font_big.render("JIANGSHI", True, LABEL), (24, 12))
    sheet.blit(font_sm.render("talisman-sealed hopping Qing corpse  ·  jade-corpse + rust-plum + cinnabar  ·  round 1",
                              True, LABEL_DIM), (210, 24))

    # --- HERO creature (large) ---
    hero = render_big(lambda b: draw_jiangshi(b, 150*SS, 200*SS, 1.6*SS), 300, 400)
    sheet.blit(hero, (30, 100))
    sheet.blit(font.render("Creature — hero", True, LABEL), (90, 504))
    sheet.blit(font_sm.render("arms locked FORWARD (T-of-arms), winged court hat, brow talisman, queue", True, LABEL_DIM), (30, 528))

    # --- prop → pillar mirror (large) ---
    pil = pygame.Surface((220, 460), pygame.SRCALPHA)
    big = pygame.Surface((220*SS, 460*SS), pygame.SRCALPHA)
    draw_pillar(big, 110*SS, 6*SS, 454*SS, 1.0*SS, cap="bottom")
    pil = pygame.transform.smoothscale(big, (220, 460))
    pil = grow_outline(pil, INK + (255,), 1)
    sheet.blit(pil, (360, 90))
    sheet.blit(font.render("Prop → pillar", True, LABEL), (392, 556))
    sheet.blit(font_sm.render("talisman-scroll shaft + red lantern gap-cap", True, LABEL_DIM), (360, 580))

    # mirror twin (cap flipped to the top edge — the top↔bottom mirror)
    big2 = pygame.Surface((220*SS, 200*SS), pygame.SRCALPHA)
    draw_pillar(big2, 110*SS, 6*SS, 196*SS, 1.0*SS, cap="top")
    pil2 = pygame.transform.smoothscale(big2, (220, 200))
    pil2 = grow_outline(pil2, INK + (255,), 1)
    sheet.blit(pil2, (360, 600))

    # --- scale strip: 32 px + 24 px + 48 px ---
    pygame.draw.rect(sheet, PANEL, (600, 90, 350, 300))
    sheet.blit(font.render("Scale read", True, LABEL), (620, 100))
    targets = [(48, "48px"), (32, "32px (gameplay)"), (24, "24px")]
    yx = 150
    for px, lbl in targets:
        chip = render_big(lambda b: draw_jiangshi(b, (px*0.30)*SS*(px/48), (px*0.42)*SS*(px/48), 0.0+ (px/120)*1.0*SS), px, px)
        # render the creature scaled to fit a px box
        boxbig = pygame.Surface((px*SS*2, px*SS*2), pygame.SRCALPHA)
        draw_jiangshi(boxbig, px*SS, px*SS, (px/118.0)*SS)
        chip = pygame.transform.smoothscale(boxbig, (px*2, px*2))
        chip = grow_outline(chip, INK + (255,), 1)
        # checker behind the chip so we see the silhouette pop
        for ci in range(0, px*2, 8):
            for cj in range(0, px*2, 8):
                col = (96,116,140) if (ci//8 + cj//8) % 2 else (84,104,128)
                pygame.draw.rect(sheet, col, (620+ci, yx+cj, 8, 8))
        sheet.blit(chip, (620, yx))
        sheet.blit(font_sm.render(lbl, True, LABEL), (620 + px*2 + 14, yx + px - 6))
        yx += px*2 + 18

    # 32px pillar chip beside it
    pchipbig = pygame.Surface((40*SS, 120*SS), pygame.SRCALPHA)
    draw_pillar(pchipbig, 20*SS, 2*SS, 118*SS, 0.27*SS, cap="bottom")
    pchip = pygame.transform.smoothscale(pchipbig, (40, 120))
    pchip = grow_outline(pchip, INK + (255,), 1)
    sheet.blit(font_sm.render("pillar @ gap-cap", True, LABEL), (800, 150))
    sheet.blit(pchip, (820, 175))

    # --- palette swatch row ---
    pygame.draw.rect(sheet, PANEL, (600, 410, 350, 320))
    sheet.blit(font.render("Pinned palette", True, LABEL), (620, 420))
    swatches = [
        (SKIN, "jade-corpse"), (SKIN_D, "deep-jade"),
        (ROBE, "rust-plum"), (ROBE_D, "rust-plum D"),
        (TAL_CREAM, "talisman cream"), (CINNABAR, "cinnabar"),
        (GOLD, "hat gold"), (QUEUE, "queue black"),
        (INK, "ink"), (SHEEN, "jade sheen"),
    ]
    sx, sy = 620, 458
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        rx = sx + col*165
        ry = sy + row*52
        pygame.draw.rect(sheet, INK, (rx-1, ry-1, 42, 42))
        pygame.draw.rect(sheet, c, (rx, ry, 40, 40))
        sheet.blit(font_sm.render(name, True, LABEL), (rx+48, ry+6))
        sheet.blit(font_sm.render("%d,%d,%d" % c, True, LABEL_DIM), (rx+48, ry+22))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()

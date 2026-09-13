"""
Round-2 concept renderer for JIANGSHI — the talisman-sealed hopping Qing corpse
(Batch 2 / Section 2 Skeletons). Headless Pygame; supersample → smoothscale to
match the house grammar (chibi, flat fills, hard ink keyline, dark-core →
flat-fill → top-left rim-sheen triad, 1px alpha-grown outline).

WHY round 2 is a near-total redraw of the figure: the AD gated this concept on
the canonical jiangshi silhouette — BOTH arms thrust straight FORWARD at the
SAME height (the T-of-arms). Round 1 rendered a 3/4 figure with a single
side-extended arm while the queue braid occupied the right-arm slot, so it read
as a one-armed pointing robot. The fix is a FRONTAL pose: two parallel
forward-foreshortened rust-plum sleeve tubes with matched jade hands, the queue
pulled to center-behind so the two arms own the horizontal axis; feet brought
together mid-hop; hat wings narrowed so the arms are the dominant horizontal.

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
GOLD_BR   = (244, 206, 110)   # brighter gold — night-biome anchor lift
INK       = ( 24,  30,  26)   # hard ink keyline
SHEEN     = (176, 206, 166)   # jade rim-sheen (top-left)
QUEUE     = ( 34,  30,  34)   # black queue braid
QUEUE_H   = ( 70,  66,  74)

BG        = ( 70,  92, 120)   # neutral slate review backdrop
PANEL     = ( 52,  70,  94)
NIGHT_BG  = ( 26,  32,  58)   # dark-blue night biome for the contrast check
LABEL     = (236, 238, 240)
LABEL_DIM = (176, 190, 206)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
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


def forward_arm(surf, x0, y0, w, h, gold):
    """One rust-plum sleeve tube thrust straight FORWARD (toward viewer):
    a foreshortened rounded rect ending in a gold cuff + jade hand w/ claws.
    Both arms call this at the SAME y0 so they read as the parallel T-of-arms."""
    # sleeve tube — flat rust-plum slab, dark core along the bottom, sheen on top
    sleeve = [(x0, y0), (x0+w, y0+int(h*0.10)),
              (x0+w, y0+h-int(h*0.10)), (x0, y0+h)]
    triad_blob(
        surf, ROBE, sleeve,
        core_pts=[(x0+int(w*0.2), y0+h-int(h*0.32)), (x0+w, y0+h-int(h*0.36)),
                  (x0+w, y0+h-int(h*0.10)), (x0+int(w*0.2), y0+h)],
        sheen_pts=[(x0+int(w*0.05), y0+int(h*0.06)), (x0+w-int(w*0.1), y0+int(h*0.14)),
                   (x0+w-int(w*0.1), y0+int(h*0.24)), (x0+int(w*0.05), y0+int(h*0.22))],
        ow=max(2, int(h*0.14)),
    )
    # gold cuff ring at the wrist (forward end)
    cuff_w = int(w*0.16)
    pygame.draw.rect(surf, gold, (x0+w-cuff_w, y0+int(h*0.08), cuff_w, h-int(h*0.16)))
    pygame.draw.rect(surf, INK, (x0+w-cuff_w, y0+int(h*0.08), cuff_w, h-int(h*0.16)), max(2, int(h*0.05)))
    # jade hand poking out the cuff
    hcx = x0 + w + int(w*0.10)
    hh = int(h*0.78)
    hand = [(x0+w-int(cuff_w*0.2), y0+int(h*0.12)), (hcx, y0+int((h-hh)/2)),
            (hcx, y0+int((h-hh)/2)+hh), (x0+w-int(cuff_w*0.2), y0+h-int(h*0.12))]
    triad_blob(surf, SKIN, hand,
               sheen_pts=[(x0+w, y0+int(h*0.18)), (hcx-int(w*0.02), y0+int(h*0.22)),
                          (hcx-int(w*0.02), y0+int(h*0.36)), (x0+w, y0+int(h*0.34))],
               ow=max(2, int(h*0.08)))
    # long black claw-nails projecting forward
    nails = 3
    for i in range(nails):
        ny = y0 + int((h-hh)/2) + int(hh*0.18) + i*int(hh*0.28)
        pygame.draw.line(surf, INK, (hcx, ny), (hcx+int(w*0.16), ny-int(h*0.04)), max(2, int(h*0.08)))


# ── the creature ─────────────────────────────────────────────────────────────
def draw_jiangshi(surf, cx, cy, s):
    """FRONTAL chibi hopping corpse: both stiff arms thrust straight FORWARD at
    the same height (T-of-arms), tall winged mandarin court hat, brow talisman,
    queue braid trailing CENTER-BEHIND. `s` is a unit scale around a ~120-unit
    figure."""

    # body box geometry (defined up front so arms + queue can key off it)
    bw, bh = int(54*s), int(74*s)
    bx0, by0 = cx - bw//2, cy - int(4*s)

    # --- queue braid trailing CENTER-BEHIND (drawn first → sits behind body) ---
    # WHY center-behind + thinned: round 1's side braid sat in the right-arm slot
    # and masqueraded as the missing arm; pulling it to dead-center and tapering
    # it lets the two FORWARD arms own the horizontal axis unambiguously.
    bqx = cx + int(2*s)
    seg = [(bqx,            by0 - int(2*s)),
           (bqx - int(3*s), by0 + int(22*s)),
           (bqx + int(3*s), by0 + int(46*s)),
           (bqx - int(2*s), by0 + int(70*s)),
           (bqx + int(2*s), by0 + int(92*s))]
    for w, col in ((int(8*s)+2, INK), (int(7*s), QUEUE)):
        for i in range(len(seg)-1):
            pygame.draw.line(surf, col, seg[i], seg[i+1], w)
    # taper highlight + binding rings so it reads as a plaited queue, not an arm
    for i in range(len(seg)-1):
        pygame.draw.line(surf, QUEUE_H, seg[i], seg[i+1], max(1, int(2*s)))
    for i in range(1, len(seg)-1):
        pygame.draw.circle(surf, INK, seg[i], int(4*s))
        pygame.draw.circle(surf, QUEUE_H, seg[i], max(1, int(2*s)))
    tie = seg[-1]
    pygame.draw.circle(surf, INK, tie, int(5*s))
    pygame.draw.circle(surf, CINNABAR, tie, int(4*s))
    pygame.draw.circle(surf, lerp(CINNABAR, (255,255,255), 0.4),
                       (tie[0]-int(1*s), tie[1]-int(1*s)), max(1, int(1.5*s)))

    # --- boxy robe body (rigid Qing official changpao) ---
    body = [(bx0, by0), (bx0+bw, by0), (bx0+bw, by0+bh),
            (bx0+bw-int(7*s), by0+bh), (cx, by0+bh-int(3*s)),
            (bx0+int(7*s), by0+bh), (bx0, by0+bh)]
    triad_blob(
        surf, ROBE, body,
        core_pts=[(cx, by0+int(10*s)), (bx0+bw, by0+int(20*s)),
                  (bx0+bw, by0+bh), (cx, by0+bh-int(4*s))],
        sheen_pts=[(bx0+int(3*s), by0+int(2*s)), (cx-int(2*s), by0+int(2*s)),
                   (cx-int(2*s), by0+bh-int(6*s)), (bx0+int(3*s), by0+bh-int(10*s))],
        ow=int(2*s)+1,
    )
    # centre seam + gold hem band (hem uses brighter gold to anchor at night)
    pygame.draw.line(surf, ROBE_D, (cx, by0+int(4*s)), (cx, by0+bh-int(6*s)), int(2*s))
    pygame.draw.rect(surf, GOLD_BR, (bx0+int(2*s), by0+bh-int(12*s), bw-int(4*s), int(7*s)))
    pygame.draw.rect(surf, GOLD_D, (bx0+int(2*s), by0+bh-int(6*s), bw-int(4*s), int(2*s)))
    pygame.draw.rect(surf, INK, (bx0+int(2*s), by0+bh-int(12*s), bw-int(4*s), int(7*s)), max(1,int(1*s)))

    # --- both arms locked straight FORWARD (the T-of-arms) ---
    # WHY both arms before the body's badge but after the body box: they emerge
    # from the shoulders and overlap the torso edges; rendered as a matched pair
    # at one y so the silhouette is symmetric and unmistakable at 32px.
    arm_y = by0 + int(14*s)
    arm_w, arm_h = int(24*s), int(21*s)
    gap = int(3*s)
    forward_arm(surf, cx - arm_w - gap, arm_y, arm_w, arm_h, GOLD_BR)   # left arm
    forward_arm(surf, cx + gap,         arm_y, arm_w, arm_h, GOLD_BR)   # right arm

    # --- round rank-badge (buzi) on the chest, cinnabar with gold ring ---
    # sits low/center so the forward arms don't cover it; warm focal at night.
    badge = (cx, by0 + int(46*s))
    pygame.draw.circle(surf, INK, badge, int(13*s)+1)
    pygame.draw.circle(surf, GOLD_BR, badge, int(13*s))
    pygame.draw.circle(surf, CINNABAR, badge, int(10*s))
    pygame.draw.circle(surf, CINNA_D, badge, int(10*s), max(1, int(1.5*s)))
    pygame.draw.circle(surf, GOLD, (badge[0], badge[1]-int(2*s)), int(3*s))
    pygame.draw.polygon(surf, GOLD, [(badge[0], badge[1]+int(1*s)),
                                     (badge[0]-int(4*s), badge[1]+int(6*s)),
                                     (badge[0]+int(4*s), badge[1]+int(6*s))])
    pygame.draw.circle(surf, lerp(CINNABAR,(255,255,255),0.3),
                       (badge[0]-int(3*s), badge[1]-int(3*s)), max(1,int(1.5*s)))

    # --- tiny feet TOGETHER mid-hop (single block lifted off the baseline) ---
    fy = by0 + bh + int(6*s)   # lifted gap = the hop
    fblock = [(cx-int(11*s), fy), (cx+int(11*s), fy),
              (cx+int(12*s), fy+int(9*s)), (cx-int(12*s), fy+int(9*s))]
    triad_blob(surf, ROBE_D, fblock, ow=max(1,int(1.5*s)))
    pygame.draw.line(surf, INK, (cx, fy), (cx, fy+int(9*s)), max(1, int(1.5*s)))  # toe split
    pygame.draw.rect(surf, INK, (cx-int(12*s), fy+int(7*s), int(24*s), int(3*s)))
    pygame.draw.rect(surf, (236,236,236), (cx-int(12*s), fy+int(7*s), int(24*s), int(2*s)))

    # --- greenish skull-face (head) ---
    hr = int(25*s)
    hc = (cx, by0 - int(20*s))
    pygame.draw.circle(surf, INK, hc, hr+int(2*s))
    pygame.draw.circle(surf, SKIN, hc, hr)
    # dark core (lower-right) + top-left jade sheen
    pygame.draw.circle(surf, SKIN_D, (hc[0]+int(7*s), hc[1]+int(7*s)), int(hr*0.7))
    pygame.draw.circle(surf, SKIN, hc, int(hr*0.86))
    pygame.draw.circle(surf, lerp(SKIN, SHEEN, 0.7),
                       (hc[0]-int(10*s), hc[1]-int(10*s)), int(6*s))
    pygame.draw.circle(surf, INK, hc, hr, int(2*s)+1)
    # sunken sockets w/ glowing cinnabar pin-points (scary-cute)
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

    # --- yellow paper talisman on the brow (cinnabar strokes + seal) ---
    tw, th = int(15*s), int(28*s)
    tx, ty = hc[0]-tw//2, hc[1]-hr-int(5*s)
    pygame.draw.rect(surf, INK, (tx-1, ty-1, tw+2, th+2))
    pygame.draw.rect(surf, TAL_CREAM, (tx, ty, tw, th))
    pygame.draw.rect(surf, lerp(TAL_CREAM,(255,255,255),0.4), (tx+int(1*s), ty+int(1*s), tw-int(3*s), int(4*s)))
    for i in range(3):
        gy = ty + int(6*s) + i*int(7*s)
        pygame.draw.line(surf, CINNABAR, (hc[0]-int(3*s), gy), (hc[0]+int(3*s), gy), max(1,int(2*s)))
        pygame.draw.line(surf, CINNABAR, (hc[0], gy-int(2*s)), (hc[0], gy+int(2*s)), max(1,int(2*s)))
    pygame.draw.rect(surf, CINNA_D, (hc[0]-int(3*s), ty+th-int(7*s), int(6*s), int(6*s)))

    # --- tall winged mandarin court hat (wings narrowed ~15% per AD) ---
    hat_base_y = hc[1] - hr + int(3*s)
    crown = [(hc[0]-int(15*s), hat_base_y), (hc[0]+int(15*s), hat_base_y),
             (hc[0]+int(10*s), hat_base_y-int(33*s)),
             (hc[0]-int(10*s), hat_base_y-int(33*s))]
    triad_blob(
        surf, INK,
        [(hc[0]-int(17*s), hat_base_y+int(2*s)), (hc[0]+int(17*s), hat_base_y+int(2*s)),
         (hc[0]+int(12*s), hat_base_y-int(35*s)), (hc[0]-int(12*s), hat_base_y-int(35*s))],
        outline=False,
    )
    pygame.draw.polygon(surf, (44, 40, 50), crown)
    pygame.draw.polygon(surf, lerp((44,40,50),(255,255,255),0.25),
                        [(hc[0]-int(15*s), hat_base_y), (hc[0]-int(6*s), hat_base_y),
                         (hc[0]-int(5*s), hat_base_y-int(33*s)),
                         (hc[0]-int(10*s), hat_base_y-int(33*s))])
    pygame.draw.polygon(surf, INK, crown, int(2*s)+1)
    pygame.draw.rect(surf, GOLD, (hc[0]-int(17*s), hat_base_y-int(2*s), int(34*s), int(6*s)))
    pygame.draw.rect(surf, INK, (hc[0]-int(17*s), hat_base_y-int(2*s), int(34*s), int(6*s)), max(1,int(1*s)))
    pygame.draw.circle(surf, GOLD, (hc[0], hat_base_y-int(35*s)), int(4*s))
    pygame.draw.circle(surf, INK, (hc[0], hat_base_y-int(35*s)), int(4*s), max(1,int(1*s)))
    # the two side WINGS (futou flaps) — narrowed & angled UP so they don't
    # compete with the arms' horizontal; hat stays the taller vertical accent.
    for sgn in (-1, 1):
        wy = hat_base_y - int(15*s)
        wing = [(hc[0]+sgn*int(14*s), wy),
                (hc[0]+sgn*int(28*s), wy-int(8*s)),
                (hc[0]+sgn*int(29*s), wy-int(1*s)),
                (hc[0]+sgn*int(14*s), wy+int(8*s))]
        pygame.draw.polygon(surf, INK, wing)
        pygame.draw.polygon(surf, (44, 40, 50), wing)
        pygame.draw.polygon(surf, GOLD, [(hc[0]+sgn*int(25*s), wy-int(6*s)),
                                         (hc[0]+sgn*int(28*s), wy-int(4*s)),
                                         (hc[0]+sgn*int(26*s), wy-int(1*s))])
        pygame.draw.polygon(surf, INK, wing, max(1,int(1.5*s)))


# ── the prop → pillar mirror (talisman-scroll / lantern-pole) ────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """Pole strung with hanging paper talismans = repeatable shaft band;
    red paper LANTERN = gap-edge cap. `cap` end faces the gap."""
    shaft_w = int(16*s)
    pygame.draw.rect(surf, INK, (cx-shaft_w//2-1, top, shaft_w+2, bot-top))
    pygame.draw.rect(surf, ROBE, (cx-shaft_w//2, top, shaft_w, bot-top))
    pygame.draw.rect(surf, ROBE_D, (cx+shaft_w//2-int(5*s), top, int(5*s), bot-top))
    pygame.draw.rect(surf, ROBE_T, (cx-shaft_w//2, top, int(4*s), bot-top))
    band = top + int(18*s)
    while band < bot - int(22*s):
        tw, th = int(20*s), int(26*s)
        tx = cx - tw//2
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

    ly = bot - int(8*s) if cap == "bottom" else top + int(8*s)
    lr = int(20*s)
    glow = pygame.Surface((lr*4, lr*4), pygame.SRCALPHA)
    for r in range(lr*2, 0, -1):
        a = int(70 * (1 - r/(lr*2)))
        pygame.draw.circle(glow, (*CINNABAR, a), (lr*2, lr*2), r)
    surf.blit(glow, (cx-lr*2, ly-lr*2), special_flags=pygame.BLEND_ADD)
    for off in (-lr-int(3*s), lr-int(1*s)):
        pygame.draw.rect(surf, GOLD, (cx-int(6*s), ly+off, int(12*s), int(5*s)))
        pygame.draw.rect(surf, INK, (cx-int(6*s), ly+off, int(12*s), int(5*s)), max(1,int(1*s)))
    rect = pygame.Rect(cx-lr, ly-int(lr*1.15), lr*2, int(lr*2.3))
    pygame.draw.ellipse(surf, INK, rect.inflate(int(3*s), int(3*s)))
    pygame.draw.ellipse(surf, CINNABAR, rect)
    dark = rect.copy(); dark.left = cx
    pygame.draw.ellipse(surf, CINNA_D, dark)
    pygame.draw.ellipse(surf, lerp(CINNABAR,(255,255,255),0.45),
                        pygame.Rect(cx-lr+int(3*s), ly-int(lr*0.9), int(lr*0.7), int(lr*0.9)))
    pygame.draw.ellipse(surf, INK, rect, int(2*s)+1)
    for rx in (-int(7*s), 0, int(7*s)):
        pygame.draw.line(surf, CINNA_D, (cx+rx, ly-int(lr*1.0)), (cx+rx, ly+int(lr*1.0)), max(1,int(1*s)))
    tyy = ly + lr + int(4*s)
    pygame.draw.line(surf, CINNABAR, (cx, tyy), (cx, tyy+int(10*s)), max(1,int(2*s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 4


def render_creature_box(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw*SS, boxh*SS), pygame.SRCALPHA)
    draw_jiangshi(big, draw_cx*SS, draw_cy*SS, scale*SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def checker(sheet, x, y, w, h, dark, light):
    for ci in range(0, w, 8):
        for cj in range(0, h, 8):
            col = light if (ci//8 + cj//8) % 2 else dark
            pygame.draw.rect(sheet, col, (x+ci, y+cj, 8, 8))


def main():
    W, H = 1020, 800
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 13)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 54))
    sheet.blit(font_big.render("JIANGSHI", True, LABEL), (24, 12))
    sheet.blit(font_sm.render("talisman-sealed hopping Qing corpse  ·  jade-corpse + rust-plum + cinnabar  ·  round 2 — T-of-arms",
                              True, LABEL_DIM), (210, 24))

    # --- HERO creature (large) — full frontal T-of-arms ---
    hero = render_creature_box(310, 410, 155, 215, 1.55)
    sheet.blit(hero, (24, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (80, 510))
    sheet.blit(font_sm.render("BOTH arms thrust straight FORWARD, same height (T-of-arms);", True, LABEL_DIM), (24, 534))
    sheet.blit(font_sm.render("feet together mid-hop; queue trails center-behind", True, LABEL_DIM), (24, 552))

    # --- prop → pillar mirror (large) ---
    pil_big = pygame.Surface((210*SS, 470*SS), pygame.SRCALPHA)
    draw_pillar(pil_big, 105*SS, 6*SS, 464*SS, 1.0*SS, cap="bottom")
    pil = pygame.transform.smoothscale(pil_big, (210, 470))
    pil = grow_outline(pil, INK + (255,), 1)
    sheet.blit(pil, (350, 84))
    sheet.blit(font.render("Prop → pillar", True, LABEL), (378, 560))
    sheet.blit(font_sm.render("talisman-scroll shaft + red lantern gap-cap", True, LABEL_DIM), (350, 584))

    # mirror twin (cap flipped to the TOP edge — the top↔bottom mirror)
    mir_big = pygame.Surface((210*SS, 200*SS), pygame.SRCALPHA)
    draw_pillar(mir_big, 105*SS, 6*SS, 196*SS, 1.0*SS, cap="top")
    mir = pygame.transform.smoothscale(mir_big, (210, 200))
    mir = grow_outline(mir, INK + (255,), 1)
    sheet.blit(mir, (350, 604))

    # --- scale strip: 48 / 32 / 24 px, day checker ---
    pygame.draw.rect(sheet, PANEL, (580, 84, 420, 322))
    sheet.blit(font.render("Scale read (day)", True, LABEL), (600, 94))
    targets = [(48, "48px"), (32, "32px (gameplay)"), (24, "24px")]
    yx = 134
    for px, lbl in targets:
        boxbig = pygame.Surface((px*SS*2, px*SS*2), pygame.SRCALPHA)
        draw_jiangshi(boxbig, px*SS, px*SS, (px/116.0)*SS)
        chip = pygame.transform.smoothscale(boxbig, (px*2, px*2))
        chip = grow_outline(chip, INK + (255,), 1)
        checker(sheet, 600, yx, px*2, px*2, (84,104,128), (96,116,140))
        sheet.blit(chip, (600, yx))
        sheet.blit(font_sm.render(lbl, True, LABEL), (600 + px*2 + 14, yx + px - 6))
        yx += px*2 + 16

    # 32px pillar gap-cap chip beside the creature chips
    pchipbig = pygame.Surface((40*SS, 120*SS), pygame.SRCALPHA)
    draw_pillar(pchipbig, 20*SS, 2*SS, 118*SS, 0.27*SS, cap="bottom")
    pchip = pygame.transform.smoothscale(pchipbig, (40, 120))
    pchip = grow_outline(pchip, INK + (255,), 1)
    sheet.blit(font_sm.render("pillar @ gap-cap", True, LABEL), (810, 134))
    sheet.blit(pchip, (838, 158))

    # --- NIGHT contrast check (AD note 6): warm focal must anchor on dark-blue ---
    pygame.draw.rect(sheet, PANEL, (580, 420, 420, 168))
    sheet.blit(font.render("Night-biome contrast check", True, LABEL), (600, 430))
    sheet.blit(font_sm.render("rust-plum robe is mid-value — gold hem/trim + cinnabar badge", True, LABEL_DIM), (600, 458))
    sheet.blit(font_sm.render("lifted brighter to keep the warm focal anchored on dark-blue night", True, LABEL_DIM), (600, 474))
    nx = 600
    for px in (48, 32):
        boxbig = pygame.Surface((px*SS*2, px*SS*2), pygame.SRCALPHA)
        draw_jiangshi(boxbig, px*SS, px*SS, (px/116.0)*SS)
        chip = pygame.transform.smoothscale(boxbig, (px*2, px*2))
        chip = grow_outline(chip, INK + (255,), 1)
        pygame.draw.rect(sheet, NIGHT_BG, (nx, 496, px*2, px*2))
        sheet.blit(chip, (nx, 496))
        sheet.blit(font_sm.render("%dpx night" % px, True, LABEL_DIM), (nx, 496 + px*2 + 2))
        nx += px*2 + 30

    # --- palette swatch row ---
    pygame.draw.rect(sheet, PANEL, (580, 600, 420, 192))
    sheet.blit(font.render("Pinned palette", True, LABEL), (600, 610))
    swatches = [
        (SKIN, "jade-corpse"), (SKIN_D, "deep-jade"),
        (ROBE, "rust-plum"), (CINNABAR, "cinnabar"),
        (TAL_CREAM, "talisman cream"), (GOLD, "hat gold"),
        (GOLD_BR, "gold (night-lift)"), (QUEUE, "queue black"),
        (INK, "ink"), (SHEEN, "jade sheen"),
    ]
    sx, sy = 600, 644
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        rx = sx + col*205
        ry = sy + row*28
        pygame.draw.rect(sheet, INK, (rx-1, ry-1, 24, 24))
        pygame.draw.rect(sheet, c, (rx, ry, 22, 22))
        sheet.blit(font_sm.render("%s  %d,%d,%d" % (name, *c), True, LABEL), (rx+30, ry+4))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()

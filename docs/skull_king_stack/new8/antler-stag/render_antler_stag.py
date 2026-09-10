import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

# WHY antler-stag wears bone like a TREE, not a tiara: the identity is a tall
# branched candelabra of separate spikes rising UP off a small-ish cranium. The
# whole chip-read hinges on the BACKGROUND GAPS between tines — gaps are what say
# "antler rack" instead of "fuzzy spiky dome". So the build is deliberately sparse:
# AD-locked CAP of 2 beams x 2 tines = 4 tips, each kept >=2px thick after the
# downscale, with wide angular spread so daylight shows between every fork.


def _taper_ribbon(surf, p0, p1, w0, w1, col, ow):
    """A straight tapering bone segment (root width w0 -> tip width w1) drawn as an
    ink-keyed triad quad with a top-left edge sheen. WHY a quad not a line: a taper
    keeps each tine reading as carved antler bone (fat root, fine tip) rather than a
    uniform spike, and the triad fill matches the house grammar."""
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]
    L = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy/L, dx/L
    quad = [(p0[0]+nx*w0, p0[1]+ny*w0), (p1[0]+nx*w1, p1[1]+ny*w1),
            (p1[0]-nx*w1, p1[1]-ny*w1), (p0[0]-nx*w0, p0[1]-ny*w0)]
    # the lit (upper-left) flank carries the sheen wedge of the triad
    sheen = [(p0[0]+nx*w0, p0[1]+ny*w0), (p1[0]+nx*w1, p1[1]+ny*w1),
             (p1[0]+nx*w1*0.3, p1[1]+ny*w1*0.3), (p0[0]+nx*w0*0.3, p0[1]+ny*w0*0.3)]
    sk.triad_blob(surf, col, [(int(x), int(y)) for x, y in quad],
                  sheen_pts=[(int(x), int(y)) for x, y in sheen], ow=ow)


def draw(surf, cx, cy, r, s, lit=False):
    thick = max(2, int(1.6 * s))
    thin = max(1, int(1.0 * s))
    BONE, BONE_D, BONE_DD, BONE_SH = sk.BONE, sk.BONE_D, sk.BONE_DD, sk.BONE_SH
    GOLD, GOLD_D, INK = sk.GOLD, sk.GOLD_D, sk.INK

    # === ANTLER RACK (drawn FIRST so the cranium overlaps the beam roots) =======
    # Two beams plant on the temples and lean OUT+UP; each forks into exactly two
    # tines. WHY a low fork: forking early (close to the crown) opens a big triangle
    # of background between the inner and outer tine of each beam, the gap that reads
    # as antler. Tip ferrules are GOLD only if they survive >=2px at chip scale.
    beam_w0 = max(2, int(0.34 * r))     # fat antler base where it meets the skull
    fork_w = max(2, int(0.20 * r))      # beam width at the fork node
    tine_tip = max(2, thin)             # AD lock: every tine >=2px after downscale
    ferr_r = int(0.13 * r)
    show_ferrule = ferr_r >= 2 * (s / max(1.0, s))  # ferrule only if it reads >=2px

    for sgn in (-1, 1):
        # beam root sits just outside the temple, on top of the cranium
        root = (cx + sgn * int(r * 0.46), cy - int(r * 0.30))
        fork = (cx + sgn * int(r * 0.78), cy - int(r * 1.06))   # the split node, up+out
        _taper_ribbon(surf, root, fork, beam_w0, fork_w, BONE, thick)

        # OUTER tine — long, sweeps further up-and-out (the tall identity spike)
        outer = (cx + sgn * int(r * 1.18), cy - int(r * 2.00))
        _taper_ribbon(surf, fork, outer, fork_w, tine_tip, BONE, thick)
        # INNER tine — shorter, rakes UP toward the midline; the gap between the two
        # tines of a beam is the deliberate daylight that says "branched antler".
        inner = (cx + sgn * int(r * 0.56), cy - int(r * 1.70))
        _taper_ribbon(surf, fork, inner, fork_w, tine_tip, BONE, thin)

        # a dark fork-node knuckle (carved-bone joint), keeps the split legible
        pygame.draw.circle(surf, BONE_D, (int(fork[0]), int(fork[1])), max(1, int(0.10 * r)))

        # GOLD tip ferrules — warm accent, NEVER out-glows cyan; omitted if too small
        if show_ferrule:
            for tip in (outer, inner):
                sk.triad_circle(surf, GOLD, (int(tip[0]), int(tip[1])), ferr_r,
                                ow=thin, core=False)
                pygame.draw.circle(surf, sk.GOLD_BR,
                                   (int(tip[0] - ferr_r*0.3), int(tip[1] - ferr_r*0.3)),
                                   max(1, int(ferr_r*0.4)))

    # === CRANIUM — a normal-ish small chibi skull (the base the rack crowns) =====
    cr = int(r * 0.92)                  # cranium kept modest so the rack dominates
    dome = []
    for ang_deg in range(-180, 1, 18):  # top half-ring brow -> temples -> crown
        a = math.radians(ang_deg)
        dome.append((cx + math.cos(a) * cr * 0.98, cy + math.sin(a) * cr * 0.96))
    dome.append((cx + cr * 0.70, cy + cr * 0.34))   # cheeks taper to jaw line
    dome.append((cx - cr * 0.70, cy + cr * 0.34))
    sk.triad_blob(surf, BONE, [(int(x), int(y)) for x, y in dome], ow=thick)
    # top-left bone sheen wedge (the triad highlight)
    sheen = [(cx - cr*0.58, cy - cr*0.08), (cx - cr*0.10, cy - cr*0.62),
             (cx - cr*0.02, cy - cr*0.30), (cx - cr*0.46, cy + cr*0.04)]
    pygame.draw.polygon(surf, BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # median suture climbing the crown (carved-bone read at hero scale)
    pygame.draw.line(surf, BONE_DD, (int(cx), int(cy - cr*0.84)),
                     (int(cx), int(cy - cr*0.08)), thin)

    # jaw — a tucked trapezoid stub
    jaw = [(cx - cr*0.46, cy + cr*0.50), (cx + cr*0.46, cy + cr*0.50),
           (cx + cr*0.30, cy + cr*0.98), (cx - cr*0.30, cy + cr*0.98)]
    sk.triad_blob(surf, BONE, [(int(x), int(y)) for x, y in jaw], ow=thin)

    # two deep ink sockets with a carved bone rim; the brow may glint dim cyan
    socket_r = int(cr * 0.30)
    for sgn in (-1, 1):
        ex = cx + sgn * int(cr * 0.42)
        ey = cy + int(cr * 0.06)
        pygame.draw.circle(surf, BONE_D, (ex, ey), socket_r + max(1, thin))
        pygame.draw.circle(surf, INK, (ex, ey), socket_r)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), max(1, int(socket_r * 0.55)))

    # nasal pit
    pygame.draw.circle(surf, INK, (cx, cy + int(cr * 0.42)), max(1, int(cr * 0.13)))

    # tooth bar — a short row with a few slits
    ty = cy + int(cr * 0.70)
    pygame.draw.line(surf, INK, (cx - int(cr*0.32), ty), (cx + int(cr*0.32), ty), thin)
    for j in range(3):
        tx = cx - int(cr*0.22) + j * int(cr*0.22)
        pygame.draw.line(surf, INK, (tx, ty - int(cr*0.08)), (tx, ty + int(cr*0.10)), thin)

    # DIM cyan brow glint — value-ladder safe (focal=False reserved for the KING).
    # A faint third-eye spark between the brows; never the brightest pixel here.
    if lit:
        sk.cyan_gem(surf, (cx, cy - int(cr * 0.30)), max(2, int(cr * 0.20)), s, focal=False)


# ── round_1 review sheet: TRUE chip (REAL bar recipe) + ~300px hero ───────────
def _chip():
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw*ssr, ch*ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.33) * ssr
    sline = (int(min(cw, ch) * 0.33) / 12.0) * ssr
    cx = cw*ssr // 2
    # WHY cy pushed DOWN to ~0.66: the antler rack roughly doubles the bounding
    # height upward, so the dome must sit low in the cell or the tines clip the top.
    cy = int(ch*ssr * 0.66)
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)
    return chip, cw, ch


def _hero(box=300):
    ss = 6
    big = pygame.Surface((box*ss, box*ss), pygame.SRCALPHA)
    r = int(box * 0.26) * ss
    sline = (box * 0.26 / 12.0) * ss
    cx = box*ss // 2
    cy = int(box*ss * 0.66)
    draw(big, cx, cy, r, sline, lit=True)
    return sk.grow_outline(pygame.transform.smoothscale(big, (box, box)), sk.INK + (255,), 1)


def main():
    W, H = 760, 480
    f_big = sk.font(26)
    f = sk.font(15)
    f_sm = sk.font(12)
    sheet = pygame.Surface((W, H))
    sheet.fill(sk.BG)

    pygame.draw.rect(sheet, sk.PANEL, (0, 0, W, 50))
    sheet.blit(f_big.render("ANTLER-STAG  —  round 1", True, sk.LABEL), (20, 12))
    sheet.blit(f_sm.render("WILD: a stag-king skull crowned by a branched antler rack (2 beams x 2 tines = 4 tips)",
                           True, sk.LABEL_DIM), (250, 20))

    # (a) TRUE chip render (REAL bar recipe) on day + night sky + blackout proof
    chip, cw, ch = _chip()
    sk_panel_x = 20
    pygame.draw.rect(sheet, sk.PANEL, (sk_panel_x, 70, 360, 380))
    sheet.blit(f.render("TRUE ~24px chip (REAL bar)", True, sk.LABEL), (sk_panel_x + 12, 80))

    def cell(x, y, top, bot, lbl):
        sk.vgrad(sheet, (x, y, cw, ch), top, bot)
        pygame.draw.rect(sheet, sk.INK, (x, y, cw, ch), 1)
        sheet.blit(chip, (x, y))
        sheet.blit(f_sm.render(lbl, True, sk.LABEL_DIM), (x, y + ch + 4))

    cell(sk_panel_x + 14, 108, sk.DAY_SKY_T, sk.DAY_SKY_B, "DAY sky")
    cell(sk_panel_x + 14 + cw + 18, 108, sk.NIGHT_T, sk.NIGHT_B, "NIGHT sky")

    # blackout silhouette proof — the antler-tines-with-gaps self-audit
    bo = sk.blackout(chip)
    bx = sk_panel_x + 14
    by = 108 + ch + 28
    pygame.draw.rect(sheet, (208, 214, 224), (bx, by, cw, ch))
    pygame.draw.rect(sheet, sk.INK, (bx, by, cw, ch), 1)
    sheet.blit(bo, (bx, by))
    sheet.blit(f_sm.render("blackout: do tines read?", True, sk.LABEL_DIM), (bx, by + ch + 4))

    # (b) ~300px hero
    hero = _hero(300)
    hx = 410
    sk.vgrad(sheet, (hx, 70, 330, 380), (74, 84, 104), (40, 46, 64))
    pygame.draw.rect(sheet, sk.INK, (hx, 70, 330, 380), 1)
    sheet.blit(hero, (hx + 15, 78))
    sheet.blit(f.render("~300px hero", True, sk.LABEL), (hx + 12, 78))
    sheet.blit(f_sm.render("dim cyan brow glint (focal=False) — king keeps focal=True", True, sk.LABEL_DIM),
               (hx + 12, 432))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()

import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def _curl_polygon(cx, cy, r, side, s):
    """One fat inward C-curl/comma horn for ONE temple. side=-1 left, +1 right.

    WHY a swept tapering crescent (NOT a spiral): at a 24px chip a spiral muds to
    a disc, so the horn is a single bold comma — a fat root at the temple sweeping
    OUTWARD then curling back INWARD to a rounded tip. It is built as a filled band
    between an OUTER sweep arc and an INNER sweep arc, the band width tapering from
    thick at the root to a point at the tip, so the negative space INSIDE the curl
    stays open and the lobe reads as its own mass beside the cranium, not fused to it.
    """
    # the curl's own centre sits out beside the temple so the comma bulges laterally
    ox = cx + side * r * 1.04
    oy = cy - r * 0.26
    cr = r * 0.66                      # curl radius (the comma's body)
    # sweep angle: start low-outer, swing up-and-over, hook back inward to the tip.
    # right horn sweeps clockwise from below to inner-top; left mirrors.
    if side > 0:
        a0, a1 = math.radians(118), math.radians(-128)   # ccw long sweep
    else:
        a0, a1 = math.radians(62), math.radians(-52 + 360)  # mirror
    steps = 26
    root_w = r * 0.40                  # fat band at the root
    outer, inner = [], []
    for i in range(steps + 1):
        t = i / steps
        a = a0 + (a1 - a0) * t
        w = root_w * (1.0 - 0.86 * t) + 1.0   # taper to a near-point tip
        ca, sa = math.cos(a), math.sin(a)
        # outer edge bulges out, inner edge hugs the curl centre
        outer.append((ox + ca * (cr + w * 0.5), oy + sa * (cr + w * 0.5)))
        inner.append((ox + ca * (cr - w * 0.5), oy + sa * (cr - w * 0.5)))
    band = outer + inner[::-1]
    return [(int(x), int(y)) for x, y in band], outer


def draw(surf, cx, cy, r, s, lit=False):
    """RAM-SKULL reliquary whose identity IS two great temple horns: a small low
    cranium beneath two fat inward C-curls, far wider than tall. Warm BONE tier,
    hard INK keyline, flat fill + dark-core/top-left sheen via triad_*."""
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # === TWO HORN CURLS (drawn FIRST → cranium overlaps the roots, but each curl's
    # BODY swings clear so an open background gap separates lobe from dome) ========
    for side in (-1, 1):
        band, outer = _curl_polygon(cx, cy, r, side, s)
        sk.triad_blob(surf, sk.BONE, band, ow=ow_thick)
        # a single BONE_SH sheen stripe down the curl's OUTER edge (carved relief)
        sheen = [(int(x), int(y)) for x, y in outer[: len(outer) * 2 // 3]]
        if len(sheen) >= 2:
            pygame.draw.lines(surf, sk.BONE_SH, False, sheen, ow_thin)
        # a faint inner shade line so the curl reads as a rounded ridge, not a slab
        ish = [(int(x), int(y)) for x, y in outer[len(outer) // 3:]]
        if len(ish) >= 2:
            pygame.draw.lines(surf, sk.BONE_D, False, ish, ow_thin)

    # === CRANIUM — small, LOW, set between the curl roots so the horns own the
    # silhouette. An ink-keyed bone polygon: a short rounded dome over a narrow face.
    cw, ch = r * 0.44, r * 0.54        # deliberately small vs the wide horn span
    dome = []
    for ang in range(-180, 1, 18):
        a = math.radians(ang)
        dome.append((cx + math.cos(a) * cw, cy + math.sin(a) * ch))
    # narrow cheeks taper into the short muzzle
    dome.append((cx + cw * 0.66, cy + ch * 0.62))
    dome.append((cx + cw * 0.40, cy + ch * 1.10))
    dome.append((cx - cw * 0.40, cy + ch * 1.10))
    dome.append((cx - cw * 0.66, cy + ch * 0.62))
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in dome], ow=ow_thick)
    # top-left sheen wedge on the cranium (the triad highlight)
    sheen = [(cx - cw * 0.56, cy - ch * 0.16), (cx - cw * 0.10, cy - ch * 0.70),
             (cx - cw * 0.02, cy - ch * 0.34), (cx - cw * 0.46, cy + ch * 0.04)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # === SHORT MUZZLE — a stubby snout below the face, narrow set jaw ============
    muz = [(cx - cw * 0.40, cy + ch * 1.02), (cx + cw * 0.40, cy + ch * 1.02),
           (cx + cw * 0.30, cy + ch * 1.62), (cx - cw * 0.30, cy + ch * 1.62)]
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in muz], ow=ow_thin)
    # nasal pit at the muzzle tip + a set-jaw mouth line
    pygame.draw.circle(surf, sk.BONE_DD, (int(cx), int(cy + ch * 1.38)), max(1, int(r * 0.09)))
    pygame.draw.line(surf, sk.INK, (int(cx - cw * 0.26), int(cy + ch * 1.50)),
                     (int(cx + cw * 0.26), int(cy + ch * 1.50)), ow_thin)

    # === TWO SOCKET PITS — deep BONE_DD ovals, ram-set wide on the small face ====
    for side in (-1, 1):
        ex = int(cx + side * cw * 0.42)
        ey = int(cy + ch * 0.18)
        rr = max(2, int(cw * 0.30))
        pygame.draw.circle(surf, sk.INK, (ex, ey), rr + max(1, int(0.8 * s)))
        pygame.draw.circle(surf, sk.BONE_DD, (ex, ey), rr)
        pygame.draw.circle(surf, sk.INK, (ex, ey), max(1, int(rr * 0.5)))

    # === BROW BOSS GEM — one cabochon set high between the curl roots ===========
    # value ladder: focal=False (a step below the king's hero gem).
    gx, gy = int(cx), int(cy - ch * 0.36)
    sk.cyan_gem(surf, (gx, gy), max(3, int(r * 0.20)), s, focal=False)


def _panel():
    bg = sk.PANEL
    W, H = 520, 380
    panel = pygame.Surface((W, H))
    panel.fill(bg)
    f = sk.font(20)
    fs = sk.font(13)
    panel.blit(f.render("HORNED-RAM  -  skull-king reference", True, sk.LABEL), (16, 12))

    # (a) TRUE chip render (the real 24px bar, blown up nearest-neighbour to see it)
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.26) * ssr
    sline = (int(min(cw, ch) * 0.26) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.50)
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)

    # true 24px chip + a few nearest-neighbour zooms so the chip read is honest
    chip24 = pygame.transform.smoothscale(chip, (24, int(24 * ch / cw)))
    panel.blit(fs.render("chip 24px", True, sk.LABEL_DIM), (28, 54))
    panel.blit(chip24, (28, 72))
    for i, z in enumerate((2, 4)):
        zs = pygame.transform.scale(chip24, (24 * z, int(24 * ch / cw) * z))
        panel.blit(fs.render(f"x{z}", True, sk.LABEL_DIM), (28 + 70 + i * 120, 54))
        panel.blit(zs, (28 + 70 + i * 120, 72))

    # blacked-out silhouette of the chip (the self-audit read)
    mask = pygame.mask.from_surface(chip24)
    sil = mask.to_surface(setcolor=sk.INK, unsetcolor=(0, 0, 0, 0))
    sil_z = pygame.transform.scale(sil, (24 * 4, int(24 * ch / cw) * 4))
    panel.blit(fs.render("blackout", True, sk.LABEL_DIM), (360, 54))
    panel.blit(sil_z, (360, 72))

    # (b) ~300px hero
    hero = pygame.Surface((300, 300), pygame.SRCALPHA)
    draw(hero, 150, 150, 74, 74 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(fs.render("hero ~300px", True, sk.LABEL_DIM), (210, 196))
    panel.blit(hero, (200, 64))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    p = _panel()
    print("WROTE", p)

import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def draw(surf, cx, cy, r, s, lit=False):
    """CALVARIA — the jawless skull-and-crossbones cranium: a domed vault that
    truncates HARD into a flat-bottomed arch of upper teeth, with NO lower jaw.

    WHY this construction reads at a 24px blackout: the whole identity is the
    silhouette's violent bottom truncation. A round dome that simply STOPS at a
    flat tooth row is the most universal "skull" glyph there is — it needs no
    interior detail to be unmistakable. So the mass is built as a single bone
    blob (wide temples, narrow cheeks pinching in, then a flat tooth lip), and
    the interior (sockets, nasal triangle) only sharpens a read the outline
    already guarantees. Warm BONE tier, hard INK keyline, flat fill + dark-core
    sockets via the house triad_* helpers. `lit` only faintly deepens sockets.
    """
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # half-extents — wide cranium, slightly taller than the tooth-row drop so the
    # jawless flat bottom sits below the socket line, not at it.
    hw = r * 1.02            # temple half-width (widest point, high on the vault)
    top = cy - r * 1.06      # crown
    cheek_y = cy + r * 0.30  # where cheeks have pinched to their narrowest
    tooth_y = cy + r * 0.70  # the flat bottom lip (upper teeth) — the truncation

    # === SKULL MASS — one closed bone polygon, traced as a single loop =========
    # WHY explicit cheek pinch: a plain dome+rectangle muds into an egg at 24px;
    # the inward pinch at the cheekbones is what separates "skull" from "blob".
    # The loop runs: left temple -> over the domed vault -> right temple -> right
    # cheek pinch -> down to the flat tooth lip -> across the bottom -> left
    # cheek -> back up to the left temple (close). The widest point (the temple)
    # sits at mid-height; the crown is the tall apex; the bottom is dead flat.
    vault = []
    for ang in range(-90, 91, 12):       # left edge, over the crown, to right edge
        a = math.radians(ang)
        x = cx + math.sin(a) * hw                       # widest at the temples
        y = cy + r * 0.16 - math.cos(a) * (r * 1.22)    # crown apex at ang=0
        vault.append((x, y))
    pts = vault + [
        (cx + hw * 0.88, cheek_y),       # right cheek barely pinches — stay broad
        (cx + hw * 0.84, tooth_y),       # drop to the WIDE flat tooth lip
        (cx - hw * 0.84, tooth_y),       # dead-flat wide bottom — the jawless truncation
        (cx - hw * 0.88, cheek_y),       # left cheek, mirrored, back up to temple
    ]
    skull = [(int(x), int(y)) for x, y in pts]
    sk.triad_blob(surf, sk.BONE, skull, ow=ow_thick)

    # top-left rim sheen on the dome (the triad highlight wedge)
    sheen = [(cx - hw * 0.66, cy - r * 0.10), (cx - hw * 0.28, cy - r * 0.82),
             (cx - hw * 0.02, cy - r * 0.52), (cx - hw * 0.40, cy + r * 0.06)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # faint cheek-shade so the pinch reads as rounded zygomatic bone, not a notch
    for side in (-1, 1):
        sh = [(cx + side * hw * 0.88, cheek_y),
              (cx + side * hw * 0.84, tooth_y),
              (cx + side * hw * 0.64, tooth_y),
              (cx + side * hw * 0.66, cheek_y + r * 0.04)]
        pygame.draw.polygon(surf, sk.BONE_D, [(int(x), int(y)) for x, y in sh])

    # === TWO ROUND SOCKETS — big, deep, set high on the vault ===================
    # WHY large & round: at chip scale the eye sockets are the second-strongest
    # cue after the truncation; oversized round pits punch through any downscale.
    sock_r = max(2, int(r * 0.29))     # smaller, so the wide tooth-shelf is the focal cue
    sock_off = hw * 0.44
    sock_y = cy - r * 0.16
    core = sk.BONE_DD if not lit else sk.lerp(sk.BONE_DD, sk.INK, 0.4)
    for side in (-1, 1):
        ex = int(cx + side * sock_off)
        ey = int(sock_y)
        pygame.draw.circle(surf, sk.INK, (ex, ey), sock_r + max(1, int(0.8 * s)))
        pygame.draw.circle(surf, core, (ex, ey), sock_r)
        # tiny ink pip at lower-inner — the depth catch-light reversal
        pygame.draw.circle(surf, sk.INK, (ex + side * int(sock_r * 0.18),
                                          ey + int(sock_r * 0.22)),
                           max(1, int(sock_r * 0.42)))

    # === NASAL TRIANGLE — inverted, between the sockets, above the tooth arch ===
    nx = cx
    ny = cy + r * 0.18
    nh = r * 0.30
    nw = r * 0.20
    nasal = [(nx - nw * 0.5, ny), (nx + nw * 0.5, ny), (nx, ny + nh)]
    pygame.draw.polygon(surf, sk.INK, [(int(x), int(y)) for x, y in nasal])
    pygame.draw.polygon(surf, core, [(int(nx - nw * 0.30), int(ny + nh * 0.06)),
                                      (int(nx + nw * 0.30), int(ny + nh * 0.06)),
                                      (int(nx), int(ny + nh * 0.82))])

    # === UPPER TOOTH ARCH — vertical clefts along the flat bottom lip ===========
    # WHY ink clefts only (no carved gaps in the silhouette): the flat bottom must
    # stay a clean unbroken edge in blackout — the teeth are read as INTERIOR
    # division lines, so they sharpen the near read without softening the chip.
    n_teeth = 8
    span = hw * 1.56            # tooth row spans nearly the full wide flat lip
    x0 = cx - span * 0.5
    top_lip = cy + r * 0.44     # top of the tooth band
    for i in range(1, n_teeth):
        tx = int(x0 + span * i / n_teeth)
        pygame.draw.line(surf, sk.INK, (tx, int(top_lip)), (tx, int(tooth_y)), ow_thin)
    # a horizontal lip line where the tooth band meets the cheeks
    pygame.draw.line(surf, sk.INK, (int(x0), int(top_lip)),
                     (int(x0 + span), int(top_lip)), ow_thin)


def _panel():
    bg = sk.PANEL
    W, H = 520, 380
    panel = pygame.Surface((W, H))
    panel.fill(bg)
    f = sk.font(20)
    fs = sk.font(13)
    panel.blit(f.render("CALVARIA  -  classic skull reference", True, sk.LABEL), (16, 12))

    # (a) TRUE chip render (the real 24px bar, blown up nearest-neighbour to see it)
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.30) * ssr
    sline = (int(min(cw, ch) * 0.30) / 12.0) * ssr
    cx = cw * ssr // 2
    # jawless mass sits high — bias cy up so the dome+teeth centre in the chip
    cy = int(ch * ssr * 0.46)
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
    draw(hero, 150, 158, 74, 74 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(fs.render("hero ~300px", True, sk.LABEL_DIM), (210, 196))
    panel.blit(hero, (200, 64))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    p = _panel()
    print("WROTE", p)

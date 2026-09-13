import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def draw(surf, cx, cy, r, s, lit=False):
    """EGG-DOME — a classic plain skull whose identity is a markedly TALL, high-
    domed cranium: a long noble forehead rising well ABOVE normally-placed sockets,
    temples visibly pinched so the blackout silhouette reads unmistakably as a
    vertical egg, never just slightly oval. Same four-band stack as any classic
    skull (vault → orbits → nasal hole → tooth row + jaw); only the vault
    proportion is pushed hard vertical. Plain BONE tier — flat fill, INK keyline,
    one top-left sheen wedge; sockets/nose/teeth are dark holes. No gems, no beads.

    WHY the egg is exaggerated, not merely oval: at a 24px chip a gently-oval dome
    reads identical to the round baseline, so the cranium is built tall (ch=1.25)
    AND narrow across the temples (cw=0.88) with the crown lifted high, and the
    sockets are pushed LOW on the long face. That leaves the tall smooth forehead
    as the dominant mass in the silhouette — the trait that distinguishes this from
    the round `round-cap` and from `child-skull` (whose vault bulges LOW over very
    low sockets; here the vault rises ABOVE the sockets)."""
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # cranium width/height units — the egg push lives here. The face hangs BELOW
    # the dome's lower flank, so the whole figure is offset up a touch to keep the
    # tall crown clear of the top edge while the jaw still has room beneath.
    cw, ch = r * 0.88, r * 1.25
    oy = cy - r * 0.18                  # raise the head so the lifted crown breathes

    # === TALL DOMED CRANIUM — an ink-keyed vertical ovoid, pinched at the temples
    # so the egg read is in the SILHOUETTE. The top of the ring is lifted extra
    # high and the temple flanks are drawn in (a smaller horizontal radius up top)
    # so the crown noticeably overhangs the narrower brow → unmistakably tall/egg.
    dome = []
    for ang in range(-180, 1, 12):
        a = math.radians(ang)
        # pinch: the upper dome is narrower than the brow level, exaggerating the
        # vertical-egg waist across the temples instead of a plain ellipse.
        pinch = 1.0 - 0.22 * max(0.0, -math.sin(a))   # squeeze x where y is high
        dx = math.cos(a) * cw * pinch
        dy = math.sin(a) * ch
        # lift the very crown so the forehead is long and the egg tip is tall
        if math.sin(a) < -0.5:
            dy *= 1.10
        dome.append((cx + dx, oy + dy))
    # the brow flanks taper gently inward into the narrow face below the dome
    dome.append((cx + cw * 0.78, oy + ch * 0.30))
    dome.append((cx + cw * 0.50, oy + ch * 0.78))
    dome.append((cx - cw * 0.50, oy + ch * 0.78))
    dome.append((cx - cw * 0.78, oy + ch * 0.30))
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in dome], ow=ow_thick)

    # one top-left sheen wedge running the FULL HEIGHT of the tall dome (the triad
    # highlight) — a long vertical sliver to emphasise the lifted forehead.
    sheen = [(cx - cw * 0.50, oy + ch * 0.18),
             (cx - cw * 0.14, oy - ch * 0.92),
             (cx + cw * 0.02, oy - ch * 0.40),
             (cx - cw * 0.30, oy + ch * 0.22)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # === NARROW FACE — a short tucked muzzle below the dome's lower flank ========
    muz = [(cx - cw * 0.50, oy + ch * 0.70), (cx + cw * 0.50, oy + ch * 0.70),
           (cx + cw * 0.40, oy + ch * 1.18), (cx - cw * 0.40, oy + ch * 1.18)]
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in muz], ow=ow_thin)

    # === SMALL TUCKED JAW — a narrow rounded U slung under the narrow face =======
    jaw = [(cx - cw * 0.40, oy + ch * 1.12), (cx + cw * 0.40, oy + ch * 1.12),
           (cx + cw * 0.28, oy + ch * 1.46), (cx - cw * 0.28, oy + ch * 1.46)]
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)

    # === TWO ROUND SOCKETS — standard size, pushed LOW so the forehead stays tall.
    # WHY low: the whole egg identity is the brow ABOVE the eyes; high sockets would
    # eat the forehead and collapse the read back toward an ordinary oval.
    socket_r = max(2, int(cw * 0.32))
    ey = int(oy + ch * 0.50)
    for side in (-1, 1):
        ex = int(cx + side * cw * 0.42)
        pygame.draw.circle(surf, sk.INK, (ex, ey), socket_r + max(1, int(0.8 * s)))
        pygame.draw.circle(surf, sk.BONE_DD, (ex, ey), socket_r)
        # faint top-left rim glow when lit — the only `lit` tell, never a colour
        rim = sk.lerp(sk.BONE_DD, sk.BONE_SH, 0.5) if lit else sk.INK
        pygame.draw.circle(surf, rim, (ex, ey), max(1, int(socket_r * 0.5)))

    # === NASAL APERTURE — an inverted triangle hole just below/between the sockets
    n_top = (cx, oy + ch * 0.72)
    n_l = (cx - cw * 0.14, oy + ch * 0.96)
    n_r = (cx + cw * 0.14, oy + ch * 0.96)
    pygame.draw.polygon(surf, sk.INK, [(int(n_top[0]), int(n_top[1])),
                                       (int(n_l[0]), int(n_l[1])),
                                       (int(n_r[0]), int(n_r[1]))])

    # === PLAIN TOOTH ROW — even INK slits in the pale lower face / jaw bar =======
    ty0 = int(oy + ch * 1.14)
    ty1 = int(oy + ch * 1.34)
    pygame.draw.line(surf, sk.INK, (int(cx - cw * 0.30), ty0),
                     (int(cx + cw * 0.30), ty0), ow_thin)
    nteeth = 6
    for j in range(nteeth):
        tx = int(cx - cw * 0.26 + j * (cw * 0.52 / (nteeth - 1)))
        pygame.draw.line(surf, sk.INK, (tx, ty0), (tx, ty1), max(1, int(1.0 * s)))


def _panel():
    bg = sk.PANEL
    W, H = 520, 380
    panel = pygame.Surface((W, H))
    panel.fill(bg)
    f = sk.font(20)
    fs = sk.font(13)
    panel.blit(f.render("EGG-DOME  -  classic skull reference", True, sk.LABEL), (16, 12))

    # (a) TRUE chip render — a tall skull needs the chip aspect taller and r a touch
    # smaller / cy a touch higher so the lifted crown isn't clipped at the top.
    ssr = 6
    cw, ch = 104, 144                  # taller chip box for the vertical egg
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.30) * ssr
    sline = (int(min(cw, ch) * 0.30) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.52)
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)

    # true 24px chip + nearest-neighbour zooms so the chip read is honest
    chip24 = pygame.transform.smoothscale(chip, (24, int(24 * ch / cw)))
    panel.blit(fs.render("chip 24px", True, sk.LABEL_DIM), (28, 54))
    panel.blit(chip24, (28, 72))
    for i, z in enumerate((2, 4)):
        zs = pygame.transform.scale(chip24, (24 * z, int(24 * ch / cw) * z))
        panel.blit(fs.render(f"x{z}", True, sk.LABEL_DIM), (28 + 70 + i * 120, 54))
        panel.blit(zs, (28 + 70 + i * 120, 72))

    # blacked-out silhouette of the chip (the self-audit read — must read TALL)
    mask = pygame.mask.from_surface(chip24)
    sil = mask.to_surface(setcolor=sk.INK, unsetcolor=(0, 0, 0, 0))
    sil_z = pygame.transform.scale(sil, (24 * 4, int(24 * ch / cw) * 4))
    panel.blit(fs.render("blackout", True, sk.LABEL_DIM), (368, 54))
    panel.blit(sil_z, (368, 72))

    # (b) ~300px hero
    hero = pygame.Surface((300, 320), pygame.SRCALPHA)
    draw(hero, 150, 150, 70, 70 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(fs.render("hero ~300px", True, sk.LABEL_DIM), (210, 246))
    panel.blit(hero, (200, 56))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    p = _panel()
    print("WROTE", p)

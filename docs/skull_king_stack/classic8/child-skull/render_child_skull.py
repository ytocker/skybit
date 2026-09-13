import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def draw(surf, cx, cy, r, s, lit=False):
    """CHILD-SKULL — a classic plain skull built to INFANT proportions: a HUGE,
    broad, rounded cranium bulging large up top over a TINY face crammed into the
    bottom. The whole identity is the vault-to-face RATIO — a baby's big-forehead
    skull, not a tall egg. Same four-band stack as any classic skull (vault →
    orbits → nasal hole → tooth row + jaw); only the proportion is pushed.
    Plain BONE tier — flat fill, INK keyline, one top-left sheen wedge;
    sockets/nose/teeth are dark holes. No gems, no beads.

    WHY this reads infant and NOT `egg-dome`: the contrast is WHERE the vault sits
    relative to the eyes. Egg-dome lifts a tall narrow forehead ABOVE normally-
    placed sockets. Child here does the opposite — a BROAD low dome (cw=1.18 wider
    than tall, ch=1.0) whose mass bulges out sideways, with the sockets shoved VERY
    LOW (ey at ch*0.86, near the dome's bottom flank) and a tiny muzzle+jaw crammed
    beneath them. So the silhouette is a big round ball balanced on a little chin:
    the cranium owns ~3/4 of the height, the face the last quarter. The sockets are
    drawn proportionally LARGE on that small face (a baby's big-eyed look), which
    also separates it from the round baseline whose eyes sit at mid-height."""
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # cranium width/height — BROAD and bulging, wider than tall (the infant vault).
    # The whole figure rides up so the big dome breathes and the low face has room.
    cw, ch = r * 1.18, r * 1.02
    oy = cy - r * 0.30                  # lift the head: dome is the dominant mass

    # === HUGE BULGING CRANIUM — an ink-keyed broad dome that swells OUTWARD at the
    # temples (a bossed forehead) rather than rising into a point. WHY a sideways
    # bulge: a baby skull's vault is widest high up and overhangs a pinched little
    # face, so the upper ring is pushed FATTER (a temple boss) and the lower flanks
    # tuck sharply inward to the tiny muzzle — the read is a ball, not an oval.
    dome = []
    for ang in range(-180, 1, 10):
        a = math.radians(ang)
        # boss: widen x in the upper-mid band so the forehead bulges past the brow
        boss = 1.0 + 0.10 * max(0.0, -math.sin(a)) * (1.0 - abs(math.cos(a)))
        dx = math.cos(a) * cw * boss
        dy = math.sin(a) * ch
        dome.append((cx + dx, oy + dy))
    # the brow flanks tuck HARD inward into the tiny face below the big vault
    dome.append((cx + cw * 0.74, oy + ch * 0.52))
    dome.append((cx + cw * 0.34, oy + ch * 0.96))
    dome.append((cx - cw * 0.34, oy + ch * 0.96))
    dome.append((cx - cw * 0.74, oy + ch * 0.52))
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in dome], ow=ow_thick)

    # one broad top-left sheen wedge across the swollen forehead (the triad
    # highlight) — wide and high to read the big rounded vault as a lit dome.
    sheen = [(cx - cw * 0.62, oy + ch * 0.04),
             (cx - cw * 0.20, oy - ch * 0.78),
             (cx + cw * 0.10, oy - ch * 0.44),
             (cx - cw * 0.30, oy + ch * 0.06)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # === TINY FACE — a short pinched muzzle crammed at the bottom of the big vault.
    # Deliberately small so the dome dwarfs it (the infant ratio).
    muz = [(cx - cw * 0.34, oy + ch * 0.90), (cx + cw * 0.34, oy + ch * 0.90),
           (cx + cw * 0.26, oy + ch * 1.20), (cx - cw * 0.26, oy + ch * 1.20)]
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in muz], ow=ow_thin)

    # === LITTLE JAW — a small rounded U slung under the tiny face ================
    jaw = [(cx - cw * 0.26, oy + ch * 1.14), (cx + cw * 0.26, oy + ch * 1.14),
           (cx + cw * 0.18, oy + ch * 1.40), (cx - cw * 0.18, oy + ch * 1.40)]
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)

    # === TWO BIG ROUND SOCKETS — pushed VERY LOW on the small face, and drawn
    # proportionally LARGE (baby's big-eyed look). WHY low + big: this is the trait
    # that separates child from egg-dome and from the round baseline — the eyes ride
    # near the dome's bottom flank so the whole forehead bulges empty above them.
    socket_r = max(2, int(cw * 0.26))   # a touch smaller + dropped lower → tinier face
    ey = int(oy + ch * 0.86)
    for side in (-1, 1):
        ex = int(cx + side * cw * 0.36)
        pygame.draw.circle(surf, sk.INK, (ex, ey), socket_r + max(1, int(0.8 * s)))
        pygame.draw.circle(surf, sk.BONE_DD, (ex, ey), socket_r)
        # faint top-left rim glow when lit — the only `lit` tell, never a colour
        rim = sk.lerp(sk.BONE_DD, sk.BONE_SH, 0.5) if lit else sk.INK
        pygame.draw.circle(surf, rim, (ex, ey), max(1, int(socket_r * 0.5)))

    # === TINY NASAL APERTURE — a small inverted triangle hole just under the eyes,
    # crammed into the narrow face (proportionally small to keep the face delicate).
    n_top = (cx, oy + ch * 1.00)
    n_l = (cx - cw * 0.10, oy + ch * 1.16)
    n_r = (cx + cw * 0.10, oy + ch * 1.16)
    pygame.draw.polygon(surf, sk.INK, [(int(n_top[0]), int(n_top[1])),
                                       (int(n_l[0]), int(n_l[1])),
                                       (int(n_r[0]), int(n_r[1]))])

    # === SMALL MOUTH — a single dark INK slot split into a FEW chunky teeth by two
    # bone dividers. WHY a filled slot, not fine slits: at the chip the tiny face is
    # only a few px, so hairline teeth turn to mush — a solid dark slot survives and
    # the dividers read as 3 blocky baby teeth.
    ty0 = int(oy + ch * 1.22)
    ty1 = int(oy + ch * 1.40)
    mw = int(cw * 0.21)
    pygame.draw.rect(surf, sk.INK, (cx - mw, ty0, 2 * mw, ty1 - ty0))
    for dx in (-mw // 3, mw // 3):
        pygame.draw.line(surf, sk.BONE, (cx + dx, ty0), (cx + dx, ty1), max(1, int(1.4 * s)))


def _panel():
    bg = sk.PANEL
    W, H = 520, 380
    panel = pygame.Surface((W, H))
    panel.fill(bg)
    f = sk.font(20)
    fs = sk.font(13)
    panel.blit(f.render("CHILD-SKULL  -  classic skull reference", True, sk.LABEL), (16, 12))

    # (a) TRUE chip render — the big dome sits high, so the chip box is a touch
    # taller and cy is lifted so the bulging vault isn't clipped at the top edge.
    ssr = 6
    cw, ch = 112, 138
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.28) * ssr
    sline = (int(min(cw, ch) * 0.28) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.50)
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

    # blacked-out silhouette of the chip (the self-audit read — big-dome/low-face)
    mask = pygame.mask.from_surface(chip24)
    sil = mask.to_surface(setcolor=sk.INK, unsetcolor=(0, 0, 0, 0))
    sil_z = pygame.transform.scale(sil, (24 * 4, int(24 * ch / cw) * 4))
    panel.blit(fs.render("blackout", True, sk.LABEL_DIM), (368, 54))
    panel.blit(sil_z, (368, 72))

    # (b) ~300px hero
    hero = pygame.Surface((300, 320), pygame.SRCALPHA)
    draw(hero, 150, 156, 72, 72 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(fs.render("hero ~300px", True, sk.LABEL_DIM), (210, 252))
    panel.blit(hero, (200, 56))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    p = _panel()
    print("WROTE", p)

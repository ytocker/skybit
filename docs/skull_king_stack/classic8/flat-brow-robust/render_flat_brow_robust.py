import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def draw(surf, cx, cy, r, s, lit=False):
    """FLAT-BROW-ROBUST — a heavy, archaic, robust classic skull whose identity is a
    LOW, FLAT-TOPPED crown over a broad robust vault, with a heavy shelf BROW that
    steps the outline OUT over deep-set sockets. It owns the set's only flat-topped
    silhouette region (every sibling is domed / bulging / tall). Same four-band
    classic stack (vault -> orbits -> nasal hole -> tooth row + jaw); only the vault
    is squat, flat-crowned and shelf-browed. Plain BONE tier — flat fill, INK
    keyline, one top-left sheen wedge; sockets / nose / teeth are dark holes. No
    gems, no beads.

    WHY the brow is a FLATTENING OF THE OUTLINE, not a protruding ridge bar: a brow
    drawn as an applied horizontal bar reads as a cyclops band (the rejected look).
    Instead the cranial silhouette itself is built archaic — the crown is capped LOW
    and FLAT, the temple flanks fall almost straight, and at brow level the outline
    STEPS OUTWARD to a shelf that is WIDER than the flat crown above it, then tucks
    back IN for the cheeks. So the heavy brow is a proportion of the vault carried in
    the blackout (a flat lid sitting on a wider shelf), and the round sockets are
    tucked UNDER that overhang in shadow. The face below is a broad, heavy, robust
    jaw — mass everywhere — to sell the archaic, low-and-wide read against the tall
    `egg-dome` and the rounded `round-cap`."""
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # vault width/height units — squat and broad. The whole figure rides a touch
    # high so the flat lid breathes at the top and the heavy jaw clears the bottom.
    cw, ch = r * 1.06, r * 0.96
    oy = cy - r * 0.10

    crown_y = oy - ch * 0.74            # the LOW flat crown line (capped, not domed)
    crown_hw = cw * 0.60                # crown half-width — NARROWER than the shelf
    brow_y = oy + ch * 0.06             # where the shelf juts out over the sockets
    shelf_hw = cw * 1.00                # shelf half-width — the widest point: the brow
    cheek_y = oy + ch * 0.50            # cheeks tuck back in below the shelf
    cheek_hw = cw * 0.80

    # === ROBUST VAULT — an ink-keyed silhouette built corner by corner so the FLAT
    # lid + the OUTWARD-STEPPING shelf live in the outline. Read top-down on the
    # right flank: short flat crown edge, near-vertical temple, a small outward kick
    # to the shelf peak at brow level, then a tuck back in to the broad cheek.
    # The crown's two corners are softly rounded so it reads as a heavy capped lid,
    # not a knife-edged box.
    vault = []
    # --- flat crown lid (left corner -> right corner), gently rounded ends ---
    vault.append((cx - crown_hw, crown_y + ch * 0.02))
    vault.append((cx - crown_hw * 0.94, crown_y))      # hard, near-square crown corners
    vault.append((cx + crown_hw * 0.94, crown_y))      # so the flat top is unmistakable
    vault.append((cx + crown_hw, crown_y + ch * 0.02))
    # --- right temple falls almost straight, flaring slightly to the shelf ---
    vault.append((cx + cw * 0.74, oy - ch * 0.34))
    # --- the BROW SHELF: the outline steps OUT to its widest point over the socket ---
    vault.append((cx + shelf_hw, brow_y - ch * 0.04))
    vault.append((cx + shelf_hw, brow_y + ch * 0.10))
    # --- tuck back IN to the broad heavy cheek below the overhang ---
    vault.append((cx + cheek_hw, cheek_y))
    vault.append((cx + cheek_hw * 0.84, oy + ch * 0.90))
    # --- mirror back up the left side ---
    vault.append((cx - cheek_hw * 0.84, oy + ch * 0.90))
    vault.append((cx - cheek_hw, cheek_y))
    vault.append((cx - shelf_hw, brow_y + ch * 0.10))
    vault.append((cx - shelf_hw, brow_y - ch * 0.04))
    vault.append((cx - cw * 0.74, oy - ch * 0.34))
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in vault], ow=ow_thick)

    # the shelf's UNDERSIDE shadow — a dark band tucked just beneath the brow
    # overhang so the shelf reads as a heavy protruding mass at hero scale (the
    # sockets sit IN this shadow). Kept inside the silhouette, never an added bar.
    underbrow = [(cx - shelf_hw * 0.94, brow_y + ch * 0.04),
                 (cx + shelf_hw * 0.94, brow_y + ch * 0.04),
                 (cx + cheek_hw * 0.86, brow_y + ch * 0.40),
                 (cx - cheek_hw * 0.86, brow_y + ch * 0.40)]
    pygame.draw.polygon(surf, sk.BONE_DD, [(int(x), int(y)) for x, y in underbrow])

    # one top-left sheen wedge across the flat crown lid + down the left temple (the
    # triad highlight) — a broad slab of light to sell the flat heavy cap.
    sheen = [(cx - crown_hw * 0.86, crown_y + ch * 0.04),
             (cx + crown_hw * 0.10, crown_y - ch * 0.02),
             (cx - cw * 0.20, oy - ch * 0.10),
             (cx - cw * 0.62, oy - ch * 0.18)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # === HEAVY BROAD JAW — a wide robust U slung under the face, nearly as wide as
    # the cheeks so the whole lower mass stays heavy (archaic, not gracile). ========
    jaw = [(cx - cheek_hw * 0.84, oy + ch * 0.84),
           (cx + cheek_hw * 0.84, oy + ch * 0.84),
           (cx + cheek_hw * 0.62, oy + ch * 1.34),
           (cx, oy + ch * 1.44),
           (cx - cheek_hw * 0.62, oy + ch * 1.34)]
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)

    # === TWO DEEP-SET ROUND SOCKETS — tucked UNDER the shelf overhang, in shadow.
    # WHY round and deep: the archaic read is heavy bone over recessed eyes, so the
    # sockets sit high (right under the brow) and are ringed dark to feel sunken.
    socket_r = max(2, int(cw * 0.30))
    ey = int(brow_y + ch * 0.24)
    for side in (-1, 1):
        ex = int(cx + side * cw * 0.46)
        pygame.draw.circle(surf, sk.INK, (ex, ey), socket_r + max(1, int(0.8 * s)))
        pygame.draw.circle(surf, sk.BONE_DD, (ex, ey), socket_r)
        # faint top-left rim glow when lit — the only `lit` tell, never a colour
        rim = sk.lerp(sk.BONE_DD, sk.BONE_SH, 0.5) if lit else sk.INK
        pygame.draw.circle(surf, rim, (ex, ey), max(1, int(socket_r * 0.5)))

    # === NASAL APERTURE — a broad inverted triangle hole below / between the sockets
    n_top = (cx, brow_y + ch * 0.36)
    n_l = (cx - cw * 0.17, oy + ch * 0.74)
    n_r = (cx + cw * 0.17, oy + ch * 0.74)
    pygame.draw.polygon(surf, sk.INK, [(int(n_top[0]), int(n_top[1])),
                                       (int(n_l[0]), int(n_l[1])),
                                       (int(n_r[0]), int(n_r[1]))])

    # === PLAIN TOOTH ROW — even INK slits across the broad lower face / jaw bar ====
    ty0 = int(oy + ch * 0.88)
    ty1 = int(oy + ch * 1.10)
    pygame.draw.line(surf, sk.INK, (int(cx - cheek_hw * 0.62), ty0),
                     (int(cx + cheek_hw * 0.62), ty0), ow_thin)
    nteeth = 7                          # a wide robust jaw carries one more tooth
    span = cheek_hw * 1.10
    for j in range(nteeth):
        tx = int(cx - span * 0.5 + j * (span / (nteeth - 1)))
        pygame.draw.line(surf, sk.INK, (tx, ty0), (tx, ty1), max(1, int(1.0 * s)))


def _panel():
    bg = sk.PANEL
    W, H = 520, 380
    panel = pygame.Surface((W, H))
    panel.fill(bg)
    f = sk.font(20)
    fs = sk.font(13)
    panel.blit(f.render("FLAT-BROW-ROBUST  -  classic skull reference", True, sk.LABEL), (16, 12))

    # (a) TRUE chip render — a squat broad skull wants a wider-than-tall chip box so
    # the flat-topped, shelf-browed silhouette isn't pinched.
    ssr = 6
    cw, ch = 124, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.30) * ssr
    sline = (int(min(cw, ch) * 0.30) / 12.0) * ssr
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

    # blacked-out silhouette of the chip (the self-audit read — must read LOW + FLAT
    # with a shelf, never a domed blob or a protruding brow bar)
    mask = pygame.mask.from_surface(chip24)
    sil = mask.to_surface(setcolor=sk.INK, unsetcolor=(0, 0, 0, 0))
    sil_z = pygame.transform.scale(sil, (24 * 4, int(24 * ch / cw) * 4))
    panel.blit(fs.render("blackout", True, sk.LABEL_DIM), (368, 54))
    panel.blit(sil_z, (368, 72))

    # (b) ~300px hero
    hero = pygame.Surface((300, 300), pygame.SRCALPHA)
    draw(hero, 150, 142, 76, 76 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(fs.render("hero ~300px", True, sk.LABEL_DIM), (210, 250))
    panel.blit(hero, (200, 60))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    p = _panel()
    print("WROTE", p)

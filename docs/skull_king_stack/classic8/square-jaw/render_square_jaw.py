import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def draw(surf, cx, cy, r, s, lit=False):
    """SQUARE-JAW — the clean two-mass classic skull: a rounded cranium vault
    sitting over a big, separately-hanging SQUARE mandible with a flat WIDE chin.
    Its whole identity is the heavy square jaw mass slung at the BOTTOM, read as a
    DISTINCT bone in the silhouette.

    WHY the jaw is its own ink-keyed polygon drawn UNDER a narrower hinge neck
    (not just an interior shadow band): a shadow line alone closes up at a 24px
    chip and fuses vault + jaw into one blob. So the silhouette itself STEPS — the
    cranium tapers IN at the cheeks to a narrow hinge, then the mandible juts back
    OUT to its full wide chin below. That re-widening creates a visible notch on
    each side of the silhouette, so the blackout reads as a circle-over-box with a
    pinch between them, not one lump.

    WHY the weight is at JAW level (low), not cheek level: this is what separates
    it from broad-zygo, whose width lives UP at the cheekbones. Here the cheeks are
    modest and the broadest, heaviest mass is the chin block at the very bottom."""
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── proportion units. The vault is a near-round dome; the mandible drops a tall
    # wide box beneath a deliberately PINCHED hinge so the two masses separate. ──
    cw, ch = r * 0.92, r * 0.96          # cranium half-width / half-height (round-ish)
    hinge_y = cy + ch * 0.62             # where the upper face narrows to the hinge
    hinge_w = cw * 0.52                  # narrow neck between vault and jaw (the pinch)
    jaw_w = cw * 0.94                    # mandible re-widens to nearly the vault width
    jaw_bot = cy + ch * 1.86             # flat chin line, slung well below the vault
    chin_w = jaw_w * 0.80                # flat WIDE chin (squared, not pointed)

    # === MANDIBLE (drawn FIRST so the upper face overlaps its top edge cleanly) ===
    # A broad squared U: it juts OUT past the hinge neck on both sides — that lateral
    # re-widening is the silhouette step that makes the jaw its own mass.
    jaw = [
        (cx - jaw_w, hinge_y + ch * 0.04),          # left hinge corner (out past neck)
        (cx - jaw_w * 1.02, cy + ch * 1.30),        # square left flank, barely tapering
        (cx - chin_w, jaw_bot - ch * 0.06),         # chin shoulder left
        (cx - chin_w * 0.70, jaw_bot),              # flat chin, left
        (cx + chin_w * 0.70, jaw_bot),              # flat chin, right
        (cx + chin_w, jaw_bot - ch * 0.06),         # chin shoulder right
        (cx + jaw_w * 1.02, cy + ch * 1.30),        # square right flank
        (cx + jaw_w, hinge_y + ch * 0.04),          # right hinge corner
    ]
    jaw = [(int(x), int(y)) for x, y in jaw]
    sk.triad_blob(surf, sk.BONE, jaw, ow=ow_thick)
    # top-left sheen down the jaw's left flank so the block reads as rounded bone
    jaw_sheen = [(cx - jaw_w * 0.86, hinge_y + ch * 0.10),
                 (cx - jaw_w * 0.88, cy + ch * 1.28),
                 (cx - jaw_w * 0.64, cy + ch * 1.30),
                 (cx - jaw_w * 0.62, hinge_y + ch * 0.14)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in jaw_sheen])
    # a dark hollow tucked under the chin shelf (carved relief, keeps the box solid)
    pygame.draw.polygon(surf, sk.BONE_D, [
        (int(cx - chin_w * 0.58), int(jaw_bot - ch * 0.04)),
        (int(cx + chin_w * 0.58), int(jaw_bot - ch * 0.04)),
        (int(cx + chin_w * 0.42), int(jaw_bot - ch * 0.30)),
        (int(cx - chin_w * 0.42), int(jaw_bot - ch * 0.30))])

    # === CRANIAL VAULT — rounded dome over a short upper face that TAPERS IN to the
    # hinge neck. The taper is the upper half of the silhouette pinch. ============
    dome = []
    for ang in range(-180, 1, 15):       # top half-ring: brow → temples → crown
        a = math.radians(ang)
        dome.append((cx + math.cos(a) * cw, cy + math.sin(a) * ch))
    # cheeks come down, then pull IN hard to the narrow hinge (creating the notch)
    dome += [
        (cx + cw * 0.94, cy + ch * 0.30),
        (cx + cw * 0.78, cy + ch * 0.50),
        (cx + hinge_w, hinge_y),                 # narrow hinge, right
        (cx - hinge_w, hinge_y),                 # narrow hinge, left
        (cx - cw * 0.78, cy + ch * 0.50),
        (cx - cw * 0.94, cy + ch * 0.30),
    ]
    dome = [(int(x), int(y)) for x, y in dome]
    sk.triad_blob(surf, sk.BONE, dome, ow=ow_thick)
    # top-left sheen wedge on the dome (the triad highlight)
    sheen = [(cx - cw * 0.58, cy - ch * 0.18), (cx - cw * 0.12, cy - ch * 0.74),
             (cx - cw * 0.02, cy - ch * 0.36), (cx - cw * 0.50, cy + ch * 0.02)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # a faint median brow shade so the forehead reads as a smooth rounded pad
    pygame.draw.line(surf, sk.BONE_D, (int(cx), int(cy - ch * 0.66)),
                     (int(cx), int(cy - ch * 0.18)), ow_thin)

    # === THE HINGE GAP — a hard INK shadow band UNDER the upper teeth, on TOP of
    # the silhouette step. Pairs with the notch so the jaw is unmistakably separate
    # both in outline AND in ink. ================================================
    gap_y = cy + ch * 0.70
    pygame.draw.line(surf, sk.INK, (int(cx - hinge_w * 1.30), int(gap_y)),
                     (int(cx + hinge_w * 1.30), int(gap_y)), max(1, int(2.2 * s)))

    # === TWO ROUND SOCKETS — standard size, set wide and a touch below midline,
    # deep ink pits with a dark core (the triad-circle read). =====================
    socket_r = max(2, int(cw * 0.30))
    for sgn in (-1, 1):
        ex = int(cx + sgn * cw * 0.42)
        ey = int(cy + ch * 0.10)
        pygame.draw.circle(surf, sk.INK, (ex, ey), socket_r + max(1, int(0.9 * s)))
        pygame.draw.circle(surf, sk.BONE_DD, (ex, ey), socket_r)
        pygame.draw.circle(surf, sk.INK, (ex, ey), max(1, int(socket_r * 0.56)))
        # `lit` only faintly warms the socket RIM — never a colour accent (plain bone)
        if lit:
            pygame.draw.circle(surf, sk.BONE_SH, (ex - int(socket_r * 0.4),
                               ey - int(socket_r * 0.4)), max(1, int(socket_r * 0.22)))

    # === NASAL APERTURE — a small inverted-heart / triangle hole below the sockets =
    n_top = (cx, cy + ch * 0.40)
    n_l = (cx - cw * 0.13, cy + ch * 0.66)
    n_r = (cx + cw * 0.13, cy + ch * 0.66)
    pygame.draw.polygon(surf, sk.INK, [(int(n_top[0]), int(n_top[1])),
                                       (int(n_l[0]), int(n_l[1])),
                                       (int(n_r[0]), int(n_r[1]))])

    # === UPPER TEETH — a plain even row of short ink slits across the maxilla,
    # sitting just ABOVE the hinge gap so they belong to the upper jaw. ===========
    ty0, ty1 = cy + ch * 0.56, gap_y - ch * 0.02
    n_up = 6
    span = hinge_w * 1.10
    pygame.draw.line(surf, sk.INK, (int(cx - span), int(ty0)),
                     (int(cx + span), int(ty0)), ow_thin)
    for j in range(1, n_up):
        tx = cx - span + j * (2 * span / n_up)
        pygame.draw.line(surf, sk.INK, (int(tx), int(ty0)), (int(tx), int(ty1)), ow_thin)

    # === LOWER TEETH — hinted as short ink slits on the mandible's TOP edge, so the
    # box reads as a tooth-bearing jaw bone, not a blank slab. ====================
    ly0 = gap_y + ch * 0.06
    ly1 = ly0 + ch * 0.18
    lspan = hinge_w * 1.16
    n_lo = 5
    for j in range(n_lo + 1):
        tx = cx - lspan + j * (2 * lspan / n_lo)
        pygame.draw.line(surf, sk.INK, (int(tx), int(ly0)), (int(tx), int(ly1)), ow_thin)


def _panel():
    bg = sk.PANEL
    W, H = 520, 380
    panel = pygame.Surface((W, H))
    panel.fill(bg)
    f = sk.font(20)
    fs = sk.font(13)
    panel.blit(f.render("SQUARE-JAW  -  classic skull reference", True, sk.LABEL), (16, 12))

    # (a) TRUE chip render (the real 24px bar, blown up nearest-neighbour to see it).
    # WHY a TALLER chip box than horned-ram: the vault+hanging-jaw stack is tall, so
    # the chip canvas is given extra height (and r tuned down) so nothing clips.
    ssr = 6
    cw, ch = 104, 150
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.24) * ssr
    sline = (int(min(cw, ch) * 0.24) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.40)
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)

    chip24 = pygame.transform.smoothscale(chip, (24, int(24 * ch / cw)))
    panel.blit(fs.render("chip 24px", True, sk.LABEL_DIM), (28, 54))
    panel.blit(chip24, (28, 72))
    for i, z in enumerate((2, 4)):
        zs = pygame.transform.scale(chip24, (24 * z, int(24 * ch / cw) * z))
        panel.blit(fs.render(f"x{z}", True, sk.LABEL_DIM), (28 + 70 + i * 120, 54))
        panel.blit(zs, (28 + 70 + i * 120, 72))

    # blacked-out silhouette of the chip (the self-audit read — must show TWO masses)
    mask = pygame.mask.from_surface(chip24)
    sil = mask.to_surface(setcolor=sk.INK, unsetcolor=(0, 0, 0, 0))
    sil_z = pygame.transform.scale(sil, (24 * 4, int(24 * ch / cw) * 4))
    panel.blit(fs.render("blackout", True, sk.LABEL_DIM), (360, 54))
    panel.blit(sil_z, (360, 72))

    # (b) ~300px hero
    hero = pygame.Surface((300, 340), pygame.SRCALPHA)
    draw(hero, 150, 132, 66, 66 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(fs.render("hero ~300px", True, sk.LABEL_DIM), (210, 350))
    panel.blit(hero, (200, 40))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    p = _panel()
    print("WROTE", p)

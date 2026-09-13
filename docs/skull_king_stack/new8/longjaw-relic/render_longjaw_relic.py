import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

# LONGJAW-RELIC (CROWN-RELIC): an equine-style relic — the only long-faced skull
# in the set. A compact dome up top, then a long deep muzzle/mandible projecting
# DOWN so the blackout reads as a front-heavy snouted wedge, not a round face.
#
# WHY cyan-free / gold-free: this is the dimmest CROWN_BONE relic tier — its
# distinctness must live entirely in the elongated geometry, so no gem, no bead,
# no warm hue. The muzzle length IS the identity.


def draw(surf, cx, cy, r, s, lit=False):
    """Equine long-faced relic. `r` ≈ cranium scale, `s` = stroke unit
    (thick ≈ 1.6*s, thin ≈ 1.0*s). The muzzle block hangs ~1.4× the cranium
    height below the dome so the cell must reserve room downward — callers seat
    `cy` high in the cell."""
    thick = max(1, int(1.6 * s))
    thin  = max(1, int(1.0 * s))

    # --- COMPACT DOME up top (deliberately modest so the muzzle owns the read) ---
    # The dome is a low broad arc; its bottom edge is the brow line where the long
    # muzzle takes over. Narrow temples keep mass off the sides — the silhouette
    # is meant to be vertical, not round.
    dome_w = r * 0.82          # compact: narrower than a normal crown dome
    dome_h = r * 0.74          # low cranium — most of the figure is the muzzle
    brow_y = cy + dome_h * 0.34
    dome = []
    for ang_deg in range(-180, 1, 16):     # top half-ring brow→temple→crown→temple
        a = math.radians(ang_deg)
        dome.append((cx + math.cos(a) * dome_w, brow_y + math.sin(a) * dome_h))
    # temples taper straight into the muzzle root (no wide cheek flare)
    muzzle_top = brow_y
    mw_top = dome_w * 0.62     # muzzle root width (narrower than the dome)
    dome.append((cx + mw_top, muzzle_top))
    dome.append((cx - mw_top, muzzle_top))
    triad_dome = [(int(x), int(y)) for x, y in dome]

    # --- LONG MUZZLE / MANDIBLE BLOCK projecting DOWN ~1.4× the cranium height ---
    # A keystone/boot taper: full at the root under the dome, narrowing gently to a
    # blunt chin, with a slight forward (right) lean at the tip for the equine read.
    muz_len = dome_h * 2.0 + r * 0.55      # long — this is the silhouette's mass
    chin_y = muzzle_top + muz_len
    mw_chin = mw_top * 0.70                # narrows toward the chin
    lean = r * 0.10                        # subtle forward set of the snout tip
    muzzle = [(int(cx - mw_top), int(muzzle_top + r * 0.04)),
              (int(cx + mw_top), int(muzzle_top + r * 0.04)),
              (int(cx + mw_chin + lean), int(chin_y - r * 0.18)),
              (int(cx + mw_chin * 0.55 + lean), int(chin_y)),
              (int(cx - mw_chin * 0.55 + lean), int(chin_y)),
              (int(cx - mw_chin + lean * 0.4), int(chin_y - r * 0.18))]

    # Draw muzzle first (behind), then the dome over its root so they fuse cleanly.
    sk.triad_blob(surf, sk.CROWN_BONE, muzzle, ow=thick)
    sk.triad_blob(surf, sk.CROWN_BONE, triad_dome, ow=thick)

    # --- top-left sheen wedges (CROWN_SH, the dim relic highlight) ---
    # dome crown sheen
    dsh = [(cx - dome_w * 0.52, brow_y - dome_h * 0.10),
           (cx - dome_w * 0.10, brow_y - dome_h * 0.62),
           (cx - dome_w * 0.02, brow_y - dome_h * 0.34),
           (cx - dome_w * 0.42, brow_y + dome_h * 0.02)]
    pygame.draw.polygon(surf, sk.CROWN_SH, [(int(x), int(y)) for x, y in dsh])
    # muzzle-RIDGE sheen — a faint vertical highlight ribbon down the lit (left)
    # edge of the snout, the carved-bone read that sells the muzzle's curvature.
    ridge = [(cx - mw_top * 0.78, muzzle_top + r * 0.10),
             (cx - mw_top * 0.40, muzzle_top + r * 0.10),
             (cx - mw_chin * 0.30 + lean, chin_y - r * 0.30),
             (cx - mw_chin * 0.66 + lean, chin_y - r * 0.30)]
    pygame.draw.polygon(surf, sk.CROWN_SH, [(int(x), int(y)) for x, y in ridge])

    # --- median suture (CROWN_BONE_D line) climbing dome crown into the muzzle ---
    pygame.draw.line(surf, sk.CROWN_BONE_D,
                     (int(cx), int(brow_y - dome_h * 0.86)),
                     (int(cx), int(muzzle_top + muz_len * 0.30)), thin)

    # --- two sockets set HIGH and CLOSE TOGETHER (equine narrow-set eyes) ---
    eye_y = brow_y + dome_h * 0.06
    eye_dx = r * 0.30          # close-set
    socket_r = max(2, int(r * 0.22))
    for sgn in (-1, 1):
        ex = int(cx + sgn * eye_dx)
        pygame.draw.circle(surf, sk.INK, (ex, int(eye_y)), socket_r)
        if lit and sgn == -1:
            pygame.draw.circle(surf, sk.CROWN_BONE_D, (ex, int(eye_y)),
                               max(1, int(socket_r * 0.5)))

    # --- nasal slit — a thin inked aperture partway down the long muzzle ---
    nasal_y = muzzle_top + muz_len * 0.34
    pygame.draw.line(surf, sk.INK, (int(cx), int(nasal_y - r * 0.12)),
                     (int(cx + lean * 0.4), int(nasal_y + r * 0.12)),
                     max(1, int(1.3 * s)))

    # --- 4–5 CHUNKY tooth slits along the lower muzzle (NOT fine; they must hold
    # at chip scale). A long bar runs the snout's lower length, crossed by a few
    # bold vertical breaks reading as a long equine tooth row. ---
    row_y0 = muzzle_top + muz_len * 0.54
    row_y1 = chin_y - r * 0.10
    bar_x = mw_top * 0.68
    # the long inked gum-line bar
    pygame.draw.line(surf, sk.INK,
                     (int(cx - bar_x + lean * 0.3), int(row_y0)),
                     (int(cx - bar_x * 0.6 + lean), int(row_y1)), max(1, int(1.6 * s)))
    pygame.draw.line(surf, sk.INK,
                     (int(cx + bar_x + lean * 0.3), int(row_y0)),
                     (int(cx + bar_x * 0.6 + lean), int(row_y1)), max(1, int(1.6 * s)))
    n_teeth = 5
    for j in range(n_teeth):
        t = j / (n_teeth - 1)
        ty = row_y0 + (row_y1 - row_y0) * t
        half = (bar_x * (1 - t) + bar_x * 0.6 * t)
        pygame.draw.line(surf, sk.INK,
                         (int(cx - half + lean * (0.3 + t * 0.7)), int(ty)),
                         (int(cx + half + lean * (0.3 + t * 0.7)), int(ty)),
                         max(1, int(1.4 * s)))


# ── review sheet ──────────────────────────────────────────────────────────────
def font(sz):
    return sk.font(sz)


if __name__ == "__main__":
    PANEL_W, PANEL_H = 520, 420
    panel = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    panel.fill(sk.PANEL)

    title = font(22).render("longjaw-relic  (CROWN-RELIC)", True, sk.LABEL)
    panel.blit(title, (18, 14))
    sub = font(13).render("equine long muzzle · cyan-free · gold-free · dimmest tier",
                          True, sk.LABEL_DIM)
    panel.blit(sub, (18, 42))

    # (a) TRUE chip render — the recipe from the brief, the read that matters most.
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.40) * ssr
    sline = (int(min(cw, ch) * 0.40) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.30)          # seat HIGH so the long muzzle fits the cell
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(
        pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)

    chip_x, chip_y = 30, 90
    # tile the chip background so the alpha sprite reads at true scale
    pygame.draw.rect(panel, (60, 64, 76), (chip_x - 6, chip_y - 6, cw + 12, ch + 12))
    panel.blit(chip, (chip_x, chip_y))
    lab = font(13).render("(a) TRUE chip  116x132", True, sk.LABEL_DIM)
    panel.blit(lab, (chip_x - 6, chip_y + ch + 10))

    # blackout silhouette beside the chip — the distinctness audit view
    mask = pygame.mask.from_surface(chip)
    sil = mask.to_surface(setcolor=sk.INK + (255,), unsetcolor=(0, 0, 0, 0))
    blk_x = chip_x + cw + 28
    pygame.draw.rect(panel, (60, 64, 76), (blk_x - 6, chip_y - 6, cw + 12, ch + 12))
    panel.blit(sil, (blk_x, chip_y))
    lab2 = font(13).render("blackout", True, sk.LABEL_DIM)
    panel.blit(lab2, (blk_x + 24, chip_y + ch + 10))

    # (b) ~300px hero — full detail
    hero_r = 110
    hsline = hero_r / 12.0
    hero = pygame.Surface((300, 360), pygame.SRCALPHA)
    draw(hero, 150, int(360 * 0.28), hero_r, hsline)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    hx = blk_x + cw + 30
    panel.blit(pygame.transform.smoothscale(hero, (150, 180)), (hx, 80))
    lab3 = font(13).render("(b) hero", True, sk.LABEL_DIM)
    panel.blit(lab3, (hx + 50, 266))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    print("wrote", out, panel.get_size())

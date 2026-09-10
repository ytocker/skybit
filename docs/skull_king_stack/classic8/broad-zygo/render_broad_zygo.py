"""Round-1 concept renderer for BROAD-ZYGO — the wide-cheeked robust classic
skull, concept #3 of the plain-bone "classic8" set. Headless Pygame; reuses the
house grammar (flat saturated fills, hard 1-2px ink keyline, dark-core/top-left
sheen triad, alpha-grown outline) from the shipped asthi-dakini helper module.

WHY this skull's identity is its SILHOUETTE, not an accessory: the set's rule is
that a skull reads as a distinct KIND only through proportion + bone condition.
Broad-zygo owns the "broad heavy-boned man" axis — its widest point sits at the
CHEEKBONES (the zygomatic arches), kicked OUT as real corner KINKS so the face is
a hexagon/diamond, then tapering DOWN to a narrow chin. A robust hourglass with
all the weight at cheek level.

WHY hard corner kinks (not a soft wide oval): at a 24px chip a softly-rounded
wide face muds to a plain oval and the cheek read is lost. So the cheek vertices
are pushed to sharp lateral corners — they survive the downscale as two bumped
points beside the sockets, visible even in blackout. This is the trait that the
blackout silhouette must show.

WHY a NARROW tapered jaw: the width must stay at CHEEK level. If the jaw were
also wide, this would collapse into `square-jaw` (whose weight is a big square
mandible). Broad-zygo keeps the lower face pinched so the cheek is unmistakably
the widest band. And it is the POSITIVE of `gaunt-hollow`: the face FLARES out at
the cheeks, it does not dent in.

Plain BONE tier only — no gems, no beadwork. `lit` is a faint socket darkening
no-op, since these are timeless plain skulls, not the exotic earlier batch.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers from the
vendored module, not runtime sprite code.
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def _skull_outline(cx, cy, r):
    """The defining HEXAGONAL hourglass silhouette: a low wide cranial dome whose
    temples bow out to hard CHEEK CORNERS at socket level (the widest band), then
    two straight diagonals taper IN to a narrow squared chin. Returned as one
    closed polygon so the cheek kinks live in the silhouette itself (visible in
    blackout), not merely as interior shading.

    WHY built corner-by-corner rather than from a smooth ellipse: the kink at the
    cheek must be an actual vertex with a sharp change of direction, so it cannot
    soften into an oval when the chip is downscaled."""
    # ── width ladder: cheeks are the WIDEST, jaw is the NARROWEST ──
    cheek_w = r * 1.36          # zygomatic flare — DECISIVELY the widest point
    dome_w  = r * 0.84          # cranial vault — clearly narrower than the cheeks
    temple_w = r * 0.92         # the cheek must out-reach the vault, so pull this in
    jaw_w   = r * 0.48          # narrow tapered chin — well inside the cheek line
    # ── height ladder (y grows downward) ──
    crown_y = cy - r * 1.02     # top of the low broad vault
    temple_y = cy - r * 0.36    # where the dome meets the temple/cheek rise
    cheek_y = cy + r * 0.16     # the hard cheek corner — sits AT socket level
    jaw_y   = cy + r * 0.78     # chin / bottom of the mandible

    pts = []
    # right side, top-down: crown → dome shoulder → temple → CHEEK CORNER → chin
    pts.append((cx, crown_y))                              # crown apex
    pts.append((cx + dome_w * 0.62, crown_y + r * 0.10))   # dome shoulder
    pts.append((cx + temple_w, temple_y))                  # temple (above cheek)
    pts.append((cx + cheek_w, cheek_y))                    # >>> CHEEK KINK (widest)
    pts.append((cx + jaw_w * 1.04, jaw_y - r * 0.18))      # under-cheek, taper begins
    pts.append((cx + jaw_w, jaw_y))                        # chin corner (right)
    # bottom of the chin
    pts.append((cx, jaw_y + r * 0.06))                     # chin midpoint dip
    # left side, bottom-up: mirror back to the crown
    pts.append((cx - jaw_w, jaw_y))
    pts.append((cx - jaw_w * 1.04, jaw_y - r * 0.18))
    pts.append((cx - cheek_w, cheek_y))                    # >>> CHEEK KINK (left)
    pts.append((cx - temple_w, temple_y))
    pts.append((cx - dome_w * 0.62, crown_y + r * 0.10))
    return pts, dict(cheek_w=cheek_w, cheek_y=cheek_y, jaw_w=jaw_w, jaw_y=jaw_y,
                     temple_y=temple_y, crown_y=crown_y, dome_w=dome_w)


def draw(surf, cx, cy, r, s, lit=False):
    """BROAD-ZYGO classic skull: a low wide hexagonal vault flaring to hard cheek
    corners at socket level, tapering to a narrow chin. Standard round sockets,
    triangular nasal aperture, plain even teeth. Plain BONE tier — no jewels."""
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    pts, g = _skull_outline(cx, cy, r)
    ipts = [(int(x), int(y)) for x, y in pts]

    # === MAIN BONE MASS — the hexagonal hourglass, ink-keyed flat fill ===========
    sk.triad_blob(surf, sk.BONE, ipts, ow=ow_thick)

    # top-left sheen wedge on the vault/cheek (the triad highlight; reads as a
    # rounded bone, not a flat slab — kept to the upper-left per the house light)
    sheen = [(cx - g["dome_w"] * 0.50, g["crown_y"] + r * 0.30),
             (cx - g["dome_w"] * 0.10, g["crown_y"] + r * 0.06),
             (cx - g["dome_w"] * 0.04, g["temple_y"] + r * 0.10),
             (cx - g["cheek_w"] * 0.58, g["cheek_y"] - r * 0.04),
             (cx - g["cheek_w"] * 0.42, g["temple_y"] + r * 0.30)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # a faint shade pocket UNDER each cheek corner so the zygomatic reads as a
    # raised arch with the face tapering away beneath it (positive flare, not a
    # hollow dent — the shade sits BELOW the corner, the corner itself stays full)
    for sgn in (-1, 1):
        pocket = [(cx + sgn * g["cheek_w"] * 0.94, g["cheek_y"] + r * 0.02),
                  (cx + sgn * g["jaw_w"] * 1.00, g["jaw_y"] - r * 0.20),
                  (cx + sgn * g["jaw_w"] * 0.66, g["jaw_y"] - r * 0.16),
                  (cx + sgn * g["cheek_w"] * 0.56, g["cheek_y"] + r * 0.10)]
        pygame.draw.polygon(surf, sk.BONE_D, [(int(x), int(y)) for x, y in pocket])

    # === BROW LINE — a low flat browridge bar above the sockets (robust read) ====
    brow_y = g["temple_y"] + r * 0.42
    pygame.draw.line(surf, sk.BONE_D,
                     (int(cx - g["cheek_w"] * 0.62), int(brow_y)),
                     (int(cx + g["cheek_w"] * 0.62), int(brow_y)),
                     max(1, int(1.6 * s)))

    # === TWO ROUND SOCKETS — set wide, AT the cheek-corner band ==================
    # WHY at cheek level: the sockets sitting on the same line as the widest point
    # reinforces "the cheekbones are the eyes' shelf" — the robust zygomatic read.
    eye_y = int(g["cheek_y"] - r * 0.04)
    eye_dx = int(g["cheek_w"] * 0.46)
    rr = max(2, int(r * 0.27))
    socket_col = sk.lerp(sk.BONE_DD, sk.INK, 0.25) if lit else sk.BONE_DD
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        pygame.draw.circle(surf, sk.INK, (ex, eye_y), rr + max(1, int(0.8 * s)))
        pygame.draw.circle(surf, socket_col, (ex, eye_y), rr)
        # a small ink core bottom-inner so the pit reads as deep, not a flat disc
        pygame.draw.circle(surf, sk.INK,
                           (ex - sgn * int(rr * 0.18), eye_y + int(rr * 0.16)),
                           max(1, int(rr * 0.46)))

    # === NASAL APERTURE — a small inverted triangle below/between the sockets ====
    n_top_y = eye_y + int(r * 0.30)
    n_bot_y = eye_y + int(r * 0.66)
    nose = [(cx, n_top_y),
            (cx - int(r * 0.15), n_bot_y),
            (cx + int(r * 0.15), n_bot_y)]
    pygame.draw.polygon(surf, sk.INK, nose)

    # === TEETH — a plain even row of small blocks on the narrow lower face =======
    # WHY narrow: the tooth row spans only the tapered jaw width, which visually
    # confirms the chin is far narrower than the cheeks above it.
    ty = int(g["jaw_y"] - r * 0.16)
    half = int(g["jaw_w"] * 0.78)
    pygame.draw.line(surf, sk.INK, (cx - half, ty), (cx + half, ty),
                     max(1, int(1.2 * s)))
    n_teeth = 5
    for j in range(n_teeth):
        tx = cx - half + int(2 * half * j / (n_teeth - 1))
        pygame.draw.line(surf, sk.INK, (tx, ty - int(r * 0.07)),
                         (tx, ty + int(r * 0.12)), max(1, int(1.0 * s)))


def _panel():
    bg = sk.PANEL
    W, H = 520, 380
    panel = pygame.Surface((W, H))
    panel.fill(bg)
    f = sk.font(20)
    fs = sk.font(13)
    panel.blit(f.render("BROAD-ZYGO  -  classic skull reference", True, sk.LABEL), (16, 12))

    # (a) TRUE chip render — a WIDE cell + a slightly smaller r so the cheek flare
    # is never clipped (a broad skull needs more horizontal room than a tall one).
    ssr = 6
    cw, ch = 132, 124          # wider cell than tall — the skull is broad
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.27) * ssr
    sline = (int(min(cw, ch) * 0.27) / 12.0) * ssr
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

    # blacked-out silhouette of the chip (the self-audit read — must show the
    # cheek corners + narrow chin)
    mask = pygame.mask.from_surface(chip24)
    sil = mask.to_surface(setcolor=sk.INK, unsetcolor=(0, 0, 0, 0))
    sil_z = pygame.transform.scale(sil, (24 * 4, int(24 * ch / cw) * 4))
    panel.blit(fs.render("blackout", True, sk.LABEL_DIM), (360, 54))
    panel.blit(sil_z, (360, 72))

    # (b) ~300px hero
    hero = pygame.Surface((300, 300), pygame.SRCALPHA)
    draw(hero, 150, 150, 78, 78 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(fs.render("hero ~300px", True, sk.LABEL_DIM), (210, 196))
    panel.blit(hero, (200, 60))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    p = _panel()
    print("WROTE", p)

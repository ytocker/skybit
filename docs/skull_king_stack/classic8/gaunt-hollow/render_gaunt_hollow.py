import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def draw(surf, cx, cy, r, s, lit=False):
    """GAUNT-HOLLOW — a lean, weathered memento-mori skull whose identity IS the
    concave TEMPLE hollow: the negative of a broad-cheeked flare. The skull is the
    OPPOSITE of round-cap's full vault — it pinches.

    WHY the temple pinch is committed to the SILHOUETTE as a bold dent (not an
    interior shade): a faint inside shadow dies at the 24px chip and would only read
    as a narrow round-cap. So the cranium outline itself WAISTS inward at the temples
    — a tall round crown, then both sides bite IN above the sockets, then flare back
    OUT a little at the wide cheekbones (the zygomatic span), then taper hard into a
    narrow gaunt jaw. That hourglass crown→temple→cheek→jaw run is the whole brief: a
    peanut-waisted blackout that no other classic sibling owns.

    WHY the cheek-hollow pockets stay FLAT BONE_DD: any darker doubled oval below the
    sockets would read as a second socket / set stone, so the gaunt hollows are a
    single flat shade plane hugging the cheek under each orbit — value depth only,
    never a contained shape.

    WHY `lit` is a near-no-op: this batch is plain BONE tier (the opposite of the
    rejected jewel skulls), so lighting only faintly warms the socket rims.
    """
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # === CRANIAL VAULT — built as a polygon that WAISTS at the temples. Walking the
    # outline top→down on each side: high round crown, a deliberate INWARD pinch at
    # temple height (above the sockets), a modest OUTWARD cheekbone flare at socket
    # level, then a hard taper into a narrow jaw. The temple indent is the deepest
    # horizontal move in the whole silhouette so the dent survives the chip.
    cw = r * 0.98                      # broader round crown above the waist
    ch = r * 1.06                      # slightly tall vault — a lean, long head
    temple_w = r * 0.46                # the WAIST — a deep dent far inside crown + cheek
    cheek_w  = r * 0.92                # cheekbone flares back OUT well past the waist
    jaw_w    = r * 0.40                # narrow gaunt jaw

    # upper dome: top half-ring from brow round over the crown, but the lower brow
    # points are pulled IN to temple_w so the sides cave before the cheek flare.
    dome = []
    for ang in range(-180, 1, 12):
        a = math.radians(ang)
        ex = math.cos(a) * cw
        ey = math.sin(a) * ch
        # near the horizontal (temple height) squeeze the width toward temple_w so
        # the crown's roundness ends in an inward bite, not a smooth circle.
        if math.sin(a) > -0.35:        # lower portion of the half-ring = the temples
            pinch = (math.sin(a) + 0.35) / 1.35   # 0 at temple top → 1 at brow line
            ex *= 1.0 - (1.0 - temple_w / cw) * pinch
        dome.append((cx + ex, cy + ey))

    # right side descending: temple waist → cheekbone flare → jaw taper → chin
    side = [
        (cx + temple_w,        cy - ch * 0.04),   # the temple WAIST (deepest dent)
        (cx + cheek_w,         cy + ch * 0.24),   # cheekbone flares back OUT
        (cx + cheek_w * 0.86,  cy + ch * 0.50),
        (cx + jaw_w,           cy + ch * 0.86),   # hard pull-in to the gaunt jaw
        (cx + jaw_w * 0.74,    cy + ch * 1.16),
        (cx,                   cy + ch * 1.24),   # pointed lean chin
        (cx - jaw_w * 0.74,    cy + ch * 1.16),
        (cx - jaw_w,           cy + ch * 0.86),
        (cx - cheek_w * 0.86,  cy + ch * 0.50),
        (cx - cheek_w,         cy + ch * 0.24),   # left cheekbone flare
        (cx - temple_w,        cy - ch * 0.04),   # left temple WAIST
    ]
    poly = [(int(x), int(y)) for x, y in dome + side]
    sk.triad_blob(surf, sk.BONE, poly, ow=ow_thick)

    # single top-left sheen wedge over the tall forehead (the triad highlight) —
    # kept above the temple line so it reinforces the high round crown.
    sheen = [(cx - cw * 0.54, cy - ch * 0.22),
             (cx - cw * 0.10, cy - ch * 0.80),
             (cx + cw * 0.04, cy - ch * 0.42),
             (cx - cw * 0.38, cy - ch * 0.08)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # === TEMPLE HOLLOW shade — a FLAT BONE_DD wedge tucked just inside each temple
    # dent so the carved concavity reads at hero scale too. It hugs the outline edge
    # (never a contained oval) so it can't be mistaken for a socket or an inlay.
    for sgn in (-1, 1):
        tw = [(cx + sgn * temple_w,         cy - ch * 0.02),
              (cx + sgn * temple_w * 0.52,  cy + ch * 0.06),
              (cx + sgn * temple_w * 0.62,  cy + ch * 0.30),
              (cx + sgn * cheek_w * 0.80,   cy + ch * 0.22)]
        pygame.draw.polygon(surf, sk.BONE_DD, [(int(x), int(y)) for x, y in tw])

    # === SOCKETS — standard round orbits, set a touch DEEPER/LARGER than the anchor
    # and tucked under the strong brow the temple pinch creates. Ink pit + darker
    # core ring + deep ink centre (the carved hollow), no colour.
    sock_r = int(r * 0.30)
    eye_y = int(cy + ch * 0.22)
    for sgn in (-1, 1):
        ex = int(cx + sgn * r * 0.40)
        pygame.draw.circle(surf, sk.INK, (ex, eye_y), sock_r + max(1, int(0.9 * s)))
        pygame.draw.circle(surf, sk.BONE_DD, (ex, eye_y), sock_r)
        pygame.draw.circle(surf, sk.INK, (ex, eye_y), int(sock_r * 0.64))
        if lit:
            pygame.draw.circle(surf, sk.BONE_SH,
                               (ex - int(sock_r * 0.34), eye_y - int(sock_r * 0.36)),
                               max(1, int(sock_r * 0.18)), max(1, ow_thin))

    # === CHEEK HOLLOW shade — a FLAT BONE_DD plane sweeping down-and-in below each
    # socket, the sunken-cheek read. Deliberately an open swept wedge (not an oval)
    # that tapers to nothing toward the jaw so it never doubles as a second socket.
    for sgn in (-1, 1):
        ch_pkt = [(cx + sgn * cheek_w * 0.78, cy + ch * 0.30),
                  (cx + sgn * r * 0.30,       cy + ch * 0.44),
                  (cx + sgn * jaw_w * 0.70,   cy + ch * 0.82),
                  (cx + sgn * cheek_w * 0.66, cy + ch * 0.56)]
        pygame.draw.polygon(surf, sk.BONE_DD, [(int(x), int(y)) for x, y in ch_pkt])

    # === NASAL APERTURE — a narrow, tall inverted teardrop (a lean nose for a lean
    # skull), all INK with a small BONE_DD inner notch for a hair of depth.
    nx = int(cx)
    n_top = int(cy + ch * 0.46)
    n_bot = int(cy + ch * 0.80)
    nw = int(r * 0.13)
    nose = [(nx, n_top + int(r * 0.05)),
            (nx - nw, n_top + int(r * 0.02)),
            (nx - int(nw * 0.58), n_top + int(r * 0.18)),
            (nx - int(nw * 0.30), n_bot - int(r * 0.05)),
            (nx, n_bot),
            (nx + int(nw * 0.30), n_bot - int(r * 0.05)),
            (nx + int(nw * 0.58), n_top + int(r * 0.18)),
            (nx + nw, n_top + int(r * 0.02))]
    pygame.draw.polygon(surf, sk.INK, nose)
    pygame.draw.circle(surf, sk.BONE_DD, (nx, n_top + int(r * 0.07)), max(1, int(r * 0.04)))

    # === TOOTH ROW — a SHORT narrow plain tooth bar to match the gaunt jaw: 5 even
    # slits in a gently arched pale bar biting off the lower face.
    n_teeth = 5
    bar_w = r * 0.52
    bar_y = cy + ch * 0.98
    x0 = cx - bar_w / 2.0
    for j in range(n_teeth):
        t = j / (n_teeth - 1)
        tx = int(x0 + t * bar_w)
        arc = math.sin(t * math.pi) * r * 0.05
        ty = int(bar_y + arc)
        pygame.draw.line(surf, sk.INK, (tx, ty - int(r * 0.06)),
                         (tx, ty + int(r * 0.10)), max(1, ow_thin))
    # faint gum shade so the tooth bar reads set into the narrow jaw
    gum = [(int(x0 - r * 0.02), int(bar_y - r * 0.08)),
           (int(cx), int(bar_y - r * 0.13)),
           (int(x0 + bar_w + r * 0.02), int(bar_y - r * 0.08))]
    pygame.draw.lines(surf, sk.BONE_D, False, gum, max(1, ow_thin))


def _panel():
    bg = sk.PANEL
    W, H = 520, 380
    panel = pygame.Surface((W, H))
    panel.fill(bg)
    f = sk.font(20)
    fs = sk.font(13)
    panel.blit(f.render("GAUNT-HOLLOW  -  classic skull reference", True, sk.LABEL), (16, 12))

    # (a) TRUE chip render (the real 24px bar, blown up nearest-neighbour to see it)
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.28) * ssr
    sline = (int(min(cw, ch) * 0.28) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.42)
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

    # blacked-out silhouette of the chip (the self-audit read — the temple WAIST)
    mask = pygame.mask.from_surface(chip24)
    sil = mask.to_surface(setcolor=sk.INK, unsetcolor=(0, 0, 0, 0))
    sil_z = pygame.transform.scale(sil, (24 * 4, int(24 * ch / cw) * 4))
    panel.blit(fs.render("blackout", True, sk.LABEL_DIM), (360, 54))
    panel.blit(sil_z, (360, 72))

    # (b) ~300px hero
    hero = pygame.Surface((300, 300), pygame.SRCALPHA)
    draw(hero, 150, 140, 72, 72 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(fs.render("hero ~300px", True, sk.LABEL_DIM), (210, 196))
    panel.blit(hero, (200, 64))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    p = _panel()
    print("WROTE", p)

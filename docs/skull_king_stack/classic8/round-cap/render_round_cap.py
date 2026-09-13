import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def draw(surf, cx, cy, r, s, lit=False):
    """ROUND-CAP — the platonic default skull, the neutral anchor of the classic-8
    set. A near-perfect ROUND vault (cw==ch) sitting on a short boxy upper-face,
    the LARGEST + ROUNDEST sockets of the set set wide and a touch low, a symmetric
    inverted-heart nasal hole, and a clean even tooth row biting straight off the
    lower edge. Plain BONE tier only: flat fill + INK keyline + one top-left sheen
    wedge; sockets/nose are dark ink holes with a darker core. No hanging jaw, no
    jewels, no sutures — this is THE skull everyone pictures, calm and balanced.

    WHY the vault is built as an ink-keyed POLYGON rather than a plain circle: the
    distinctness of every sibling in the set has to live in the SILHOUETTE so it
    survives the blackout test, so even the baseline anchor commits its identity
    (broad round low-brow) to the outline, not just to interior holes.

    WHY `lit` is a near-no-op: the set is the deliberate plain-bone opposite of the
    rejected jewel batch, so lighting only faintly warms the socket rims — never a
    colour accent.
    """
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # === CRANIAL VAULT — a wide ROUND dome (cw==ch) flowing into a short upper-face.
    # The face stops at the maxilla: teeth bite off the lower edge, no separate
    # mandible, so the whole silhouette is essentially one friendly round mass.
    cw, ch = r * 1.00, r * 1.00        # the neutral 1:1 the other seven deviate from
    dome = []
    for ang in range(-180, 1, 12):     # top half-ring: brow → temples → high crown
        a = math.radians(ang)
        dome.append((cx + math.cos(a) * cw, cy + math.sin(a) * ch))
    # cheeks flare gently at socket level then sweep in to a soft rounded chin so
    # the lower face keeps the classic cheek-to-jaw taper without a boxy jaw.
    dome.append((cx + cw * 0.92, cy + ch * 0.30))
    dome.append((cx + cw * 0.74, cy + ch * 0.78))
    dome.append((cx + cw * 0.40, cy + ch * 1.06))
    dome.append((cx,             cy + ch * 1.14))
    dome.append((cx - cw * 0.40, cy + ch * 1.06))
    dome.append((cx - cw * 0.74, cy + ch * 0.78))
    dome.append((cx - cw * 0.92, cy + ch * 0.30))
    dome = [(int(x), int(y)) for x, y in dome]
    sk.triad_blob(surf, sk.BONE, dome, ow=ow_thick)

    # single soft top-left sheen wedge over the tall smooth forehead (the triad
    # highlight) — the only depth cue the dome needs at the plain-bone tier.
    sheen = [(cx - cw * 0.60, cy - ch * 0.18),
             (cx - cw * 0.12, cy - ch * 0.78),
             (cx + cw * 0.04, cy - ch * 0.40),
             (cx - cw * 0.42, cy + ch * 0.02)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # === SOCKETS — the LARGEST + ROUNDEST of the set, set wide and a touch BELOW
    # the vault midline so a tall calm forehead reads above them. Each is an ink
    # pit with a darker BONE_DD core ring + a deep ink centre (the triad-style
    # carved hollow), giving roundness without any colour.
    sock_r = int(r * 0.34)
    eye_y = int(cy + ch * 0.08)        # lifted off the jaw so a proper dome reads above
    for sgn in (-1, 1):
        ex = int(cx + sgn * cw * 0.44)
        pygame.draw.circle(surf, sk.INK, (ex, eye_y), sock_r + max(1, int(0.9 * s)))
        pygame.draw.circle(surf, sk.BONE_DD, (ex, eye_y), sock_r)
        pygame.draw.circle(surf, sk.INK, (ex, eye_y), int(sock_r * 0.62))
        # a faint warm rim glint only when lit — never a colour, never a glow.
        if lit:
            pygame.draw.circle(surf, sk.BONE_SH,
                               (ex - int(sock_r * 0.34), eye_y - int(sock_r * 0.36)),
                               max(1, int(sock_r * 0.18)), max(1, ow_thin))

    # === NASAL APERTURE — a symmetric inverted heart / spade just below and between
    # the sockets: the single most "skull-not-anything-else" hole after the orbits.
    # Built as two rounded upper lobes meeting at a narrow throat that flares to a
    # point, all in INK with a BONE_DD inner notch for a hair of depth.
    nx = int(cx)
    n_top = int(cy + ch * 0.40)
    n_bot = int(cy + ch * 0.78)
    nw = int(r * 0.18)
    nose = [(nx, n_top + int(r * 0.04)),               # dimpled top of the heart
            (nx - nw, n_top),                          # left lobe shoulder
            (nx - int(nw * 0.70), n_top + int(r * 0.16)),
            (nx - int(nw * 0.34), n_bot - int(r * 0.06)),
            (nx, n_bot),                               # flared point
            (nx + int(nw * 0.34), n_bot - int(r * 0.06)),
            (nx + int(nw * 0.70), n_top + int(r * 0.16)),
            (nx + nw, n_top)]                          # right lobe shoulder
    pygame.draw.polygon(surf, sk.INK, nose)
    pygame.draw.circle(surf, sk.BONE_DD, (nx, n_top + int(r * 0.05)), max(1, int(r * 0.05)))

    # === TOOTH ROW — 6 EVEN slits in a gently arched pale bar biting off the lower
    # face. The clean, evenly-spaced set is the calm baseline the aged gap-tooth
    # sibling deviates from; the slight arch follows the maxilla so it reads as a
    # bite, not a fence.
    n_teeth = 6
    bar_w = r * 0.74
    bar_y = cy + ch * 0.96
    x0 = cx - bar_w / 2.0
    for j in range(n_teeth):
        t = j / (n_teeth - 1)
        tx = int(x0 + t * bar_w)
        # arch: teeth toward the centre sit a touch lower (the bite curves down)
        arc = math.sin(t * math.pi) * r * 0.07
        ty = int(bar_y + arc)
        pygame.draw.line(surf, sk.INK, (tx, ty - int(r * 0.07)),
                         (tx, ty + int(r * 0.11)), max(1, ow_thin))
    # a faint shade line along the gum so the tooth bar reads as set into the face
    gum = [(int(x0 - r * 0.02), int(bar_y - r * 0.09)),
           (int(cx), int(bar_y - r * 0.16)),
           (int(x0 + bar_w + r * 0.02), int(bar_y - r * 0.09))]
    pygame.draw.lines(surf, sk.BONE_D, False, gum, max(1, ow_thin))


def _panel():
    bg = sk.PANEL
    W, H = 520, 380
    panel = pygame.Surface((W, H))
    panel.fill(bg)
    f = sk.font(20)
    fs = sk.font(13)
    panel.blit(f.render("ROUND-CAP  -  classic skull reference", True, sk.LABEL), (16, 12))

    # (a) TRUE chip render (the real 24px bar, blown up nearest-neighbour to see it)
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.30) * ssr
    sline = (int(min(cw, ch) * 0.30) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.44)
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
    draw(hero, 150, 142, 74, 74 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(fs.render("hero ~300px", True, sk.LABEL_DIM), (210, 196))
    panel.blit(hero, (200, 64))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    p = _panel()
    print("WROTE", p)

import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def draw(surf, cx, cy, r, s, lit=False):
    """SIMPLE-SKULL — the plainest, calmest skull in the set: a smooth rounded
    cranium over a short face, two even round sockets, a small triangular nose and
    one clean tooth row. No horns, jewels, cracks or ornament — deliberately the
    quiet, instantly-readable skull that replaces the busy ram at slot #15. Plain
    BONE tier: flat fill + INK keyline + a single soft top-left sheen wedge; the
    sockets/nose are dark ink holes. `lit` is a near-no-op (this tier carries no
    colour accent), only faintly warming the socket rims."""
    ow_thick = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # === CRANIUM — one smooth rounded mass: a gently tall dome flowing through soft
    # cheeks to a rounded chin (no separate jaw), so the whole silhouette is calm.
    cw, ch = r * 1.00, r * 1.04
    dome = []
    for ang in range(-180, 1, 12):
        a = math.radians(ang)
        dome.append((cx + math.cos(a) * cw, cy + math.sin(a) * ch))
    dome.append((cx + cw * 0.86, cy + ch * 0.40))
    dome.append((cx + cw * 0.50, cy + ch * 0.98))
    dome.append((cx,             cy + ch * 1.08))
    dome.append((cx - cw * 0.50, cy + ch * 0.98))
    dome.append((cx - cw * 0.86, cy + ch * 0.40))
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in dome], ow=ow_thick)

    # single soft top-left sheen wedge over the forehead (the only depth cue needed)
    sheen = [(cx - cw * 0.58, cy - ch * 0.16), (cx - cw * 0.10, cy - ch * 0.74),
             (cx + cw * 0.02, cy - ch * 0.38), (cx - cw * 0.42, cy + ch * 0.00)]
    pygame.draw.polygon(surf, sk.BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # === TWO ROUND SOCKETS — even, friendly, set just below the dome midline so a
    # calm forehead reads above. Ink pit + darker core ring + deep ink centre.
    sock_r = int(r * 0.30)
    eye_y = int(cy + ch * 0.08)
    for sgn in (-1, 1):
        ex = int(cx + sgn * cw * 0.42)
        pygame.draw.circle(surf, sk.INK, (ex, eye_y), sock_r + max(1, int(0.9 * s)))
        pygame.draw.circle(surf, sk.BONE_DD, (ex, eye_y), sock_r)
        pygame.draw.circle(surf, sk.INK, (ex, eye_y), int(sock_r * 0.58))
        if lit:
            pygame.draw.circle(surf, sk.BONE_SH,
                               (ex - int(sock_r * 0.32), eye_y - int(sock_r * 0.34)),
                               max(1, int(sock_r * 0.18)), max(1, ow_thin))

    # === NASAL APERTURE — one small inverted triangle between + below the sockets ==
    n_top = cy + ch * 0.36
    nh, nw = r * 0.24, r * 0.16
    pygame.draw.polygon(surf, sk.INK, [(int(cx - nw * 0.5), int(n_top)),
                                       (int(cx + nw * 0.5), int(n_top)),
                                       (int(cx), int(n_top + nh))])

    # === TOOTH ROW — a few even INK slits in a softly arched pale bar; the simplest
    # possible bite, no chips or gaps.
    n_teeth = 5
    bar_w = r * 0.64
    bar_y = cy + ch * 0.74
    x0 = cx - bar_w / 2.0
    pygame.draw.line(surf, sk.BONE_D, (int(x0 - r * 0.02), int(bar_y - r * 0.07)),
                     (int(x0 + bar_w + r * 0.02), int(bar_y - r * 0.07)), max(1, ow_thin))
    for j in range(n_teeth):
        tx = int(x0 + bar_w * j / (n_teeth - 1))
        pygame.draw.line(surf, sk.INK, (tx, int(bar_y - r * 0.06)),
                         (tx, int(bar_y + r * 0.11)), max(1, ow_thin))


def _panel():
    """A quick review panel: true 24px chip + x4 zoom + blackout + ~300px hero."""
    panel = pygame.Surface((520, 360)); panel.fill(sk.PANEL)
    panel.blit(sk.font(20).render("SIMPLE-SKULL  -  replacement for #15", True, sk.LABEL), (16, 12))
    cw, ch, ssr = 116, 132, 6
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.30) * ssr
    sline = (int(min(cw, ch) * 0.30) / 12.0) * ssr
    draw(big, cw * ssr // 2, int(ch * ssr * 0.46), r, sline)
    chip = sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)
    chip24 = pygame.transform.smoothscale(chip, (24, int(24 * ch / cw)))
    panel.blit(sk.font(13).render("chip 24px", True, sk.LABEL_DIM), (24, 50))
    panel.blit(chip24, (24, 68))
    panel.blit(pygame.transform.scale(chip24, (24 * 4, int(24 * ch / cw) * 4)), (90, 68))
    mask = pygame.mask.from_surface(chip24)
    sil = mask.to_surface(setcolor=sk.INK, unsetcolor=(0, 0, 0, 0))
    panel.blit(sk.font(13).render("blackout", True, sk.LABEL_DIM), (210, 50))
    panel.blit(pygame.transform.scale(sil, (24 * 4, int(24 * ch / cw) * 4)), (210, 68))
    hero = pygame.Surface((300, 300), pygame.SRCALPHA)
    draw(hero, 150, 140, 76, 76 / 12.0)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    panel.blit(hero, (290, 60))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    return out


if __name__ == "__main__":
    print("WROTE", _panel())

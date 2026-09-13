import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

# CYCLOPS-BROW (WILD) — a one-eyed monk-relic whose whole face is reorganized
# around ONE great central socket. The gate-critical identity is the SILHOUETTE:
# a heavy FORWARD BROW-BOSS overhangs the single socket up top, then the skull
# narrows to a TAPERING CHIN below — a "lightbulb / inverted-pear" blackout, NOT
# a symmetric teardrop and NOT a pointy spire. The brow overhang is the read.
#
# Value ladder: the central ring_eye is the most-lit of the wild four but uses
# focal=False — it is capped a value step UNDER the king's hero gem (focal=True).

P = sk  # palette + primitive namespace


def draw(surf, cx, cy, r, s, lit=False):
    """Cyclops-brow relic. cranium scale ~r, stroke unit s.

    Built around the vertical midline: a broad heavy brow-boss bulges forward
    over a single central socket, then the lower face tapers to a narrow chin
    (inverted-pear). One ring_eye in the socket, a nasal slit below, a tight
    small tooth cluster on the chin, and a saint-relic bead halo over the boss.
    """
    ink = sk.INK
    ow_main = max(2, int(1.7 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── BLACKOUT SILHOUETTE: heavy forward brow-boss → tapering chin ──────────
    # WHY a hand-laid polygon, not an ellipse: the identity lives in the
    # asymmetry of mass top-to-bottom — a WIDE overhanging brow shelf up top that
    # bulges PAST the cheeks, then a hard inward taper to a small chin. An ellipse
    # would read as a teardrop; the explicit overhang corners are what make the
    # blackout say "heavy single brow narrowing to a chin".
    bw = r * 1.18          # brow-boss half-width (the widest point, up high)
    crown_y = cy - r * 1.08
    boss_y = cy - r * 0.30   # the brow shelf sits here — the bulge line
    chin_y = cy + r * 1.34
    chin_w = r * 0.40        # narrow chin

    # right half walked top→bottom, then mirrored — the boss is the max width and
    # sits HIGH, with a soft overhang lip jutting out just above the socket.
    skull = [
        (cx,             crown_y),                      # crown apex
        (cx + r * 0.62,  crown_y + r * 0.10),           # upper dome shoulder
        (cx + r * 0.98,  boss_y - r * 0.46),            # boss rising
        (cx + bw,        boss_y - r * 0.06),            # BROW-BOSS widest point
        (cx + bw * 0.96, boss_y + r * 0.20),            # overhang lip (juts out)
        (cx + r * 0.78,  boss_y + r * 0.58),            # undercut: face pulls IN
        (cx + r * 0.56,  cy + r * 0.50),                # cheek taper
        (cx + chin_w + r * 0.10, chin_y - r * 0.40),    # jaw line
        (cx + chin_w,    chin_y),                       # chin corner
        (cx - chin_w,    chin_y),                        # chin corner (mirror)
        (cx - chin_w - r * 0.10, chin_y - r * 0.40),
        (cx - r * 0.56,  cy + r * 0.50),
        (cx - r * 0.78,  boss_y + r * 0.58),
        (cx - bw * 0.96, boss_y + r * 0.20),
        (cx - bw,        boss_y - r * 0.06),
        (cx - r * 0.98,  boss_y - r * 0.46),
        (cx - r * 0.62,  crown_y + r * 0.10),
    ]
    skull_i = [(int(x), int(y)) for x, y in skull]

    # dark-core wedge (lower-right) + top-left sheen wedge for the house triad
    core = [(cx + r * 0.10, boss_y + r * 0.10),
            (cx + r * 0.70, boss_y + r * 0.40),
            (cx + chin_w * 0.6, chin_y - r * 0.20),
            (cx + r * 0.06, cy + r * 0.40)]
    sheen = [(cx - r * 0.20, crown_y + r * 0.20),
             (cx - r * 0.86, boss_y - r * 0.30),
             (cx - bw * 0.80, boss_y - r * 0.02),
             (cx - r * 0.40, boss_y + r * 0.18),
             (cx - r * 0.16, cy + r * 0.10)]
    sk.triad_blob(surf, sk.BONE, skull_i,
                  sheen_pts=[(int(x), int(y)) for x, y in sheen],
                  core_pts=[(int(x), int(y)) for x, y in core],
                  ow=ow_main)

    # the BROW-OVERHANG shadow — a dark band tucked UNDER the boss lip, selling
    # the forward overhang as a cast shadow above the socket (depth read).
    overhang = [(cx - bw * 0.86, boss_y + r * 0.16),
                (cx + bw * 0.86, boss_y + r * 0.16),
                (cx + r * 0.66,  boss_y + r * 0.40),
                (cx - r * 0.66,  boss_y + r * 0.40)]
    pygame.draw.polygon(surf, sk.lerp(sk.BONE, ink, 0.5),
                        [(int(x), int(y)) for x, y in overhang])

    # carved median SUTURE down the boss (GOLD_D) — a saint-relic seam on the
    # vertical midline, reinforcing the single-axis build.
    pygame.draw.line(surf, sk.GOLD_D, (int(cx), int(crown_y + r * 0.22)),
                     (int(cx), int(boss_y - r * 0.30)), max(2, int(1.6 * s)))
    for j in range(3):
        sy = crown_y + r * 0.30 + j * r * 0.24
        pygame.draw.circle(surf, sk.GOLD, (int(cx), int(sy)), max(1, int(1.0 * s)))

    # ── THE ONE GREAT CENTRAL SOCKET ─────────────────────────────────────────
    # A large almond/round pit on the brow line, deep INK, with a carved bone rim
    # so the ring_eye reads as set INTO the boss.
    soc_cx, soc_cy = cx, int(boss_y + r * 0.40)
    soc_r = int(r * 0.46)
    pygame.draw.circle(surf, sk.BONE_D, (soc_cx, soc_cy), soc_r + max(2, int(1.6 * s)))
    pygame.draw.circle(surf, ink, (soc_cx, soc_cy), soc_r)
    # ring_eye fills the socket — rings sized so each survives the downscale.
    sk.ring_eye(surf, (soc_cx, soc_cy), int(soc_r * 0.86), s)

    # ── NASAL SLIT below the socket — a small inverted ink teardrop ───────────
    n_y = cy + r * 0.62
    nasal = [(cx, n_y), (cx - r * 0.12, n_y + r * 0.30),
             (cx + r * 0.12, n_y + r * 0.30)]
    pygame.draw.polygon(surf, ink, [(int(x), int(y)) for x, y in nasal])

    # ── NARROW CHIN with a TIGHT small tooth cluster ─────────────────────────
    # A short jaw bar low on the taper, with a few close-packed slits — small,
    # clustered, so the chin reads pinched (vs a wide grin that would broaden it).
    ty = int(chin_y - r * 0.34)
    tw = chin_w * 0.92
    jaw = [(cx - chin_w, chin_y - r * 0.46), (cx + chin_w, chin_y - r * 0.46),
           (cx + chin_w * 0.82, chin_y - r * 0.02), (cx - chin_w * 0.82, chin_y - r * 0.02)]
    sk.triad_blob(surf, sk.BONE, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
    pygame.draw.line(surf, ink, (int(cx - tw), ty), (int(cx + tw), ty), max(1, int(1.2 * s)))
    for j in range(4):
        tx = cx - tw * 0.7 + j * (tw * 1.4 / 3)
        pygame.draw.line(surf, ink, (int(tx), int(ty - r * 0.06)),
                         (int(tx), int(ty + r * 0.16)), max(1, int(1.0 * s)))

    # ── SAINT-RELIC HALO — a bead_arc crowning the brow-boss ─────────────────
    # A pale bone bead crescent arcing OVER the boss (a relic's holy ring),
    # crisp gold spacer-pips for the warm hue note. Sits above the silhouette so
    # it crowns the heavy brow rather than widening the dome blackout.
    halo_r = int(r * 1.16)
    sk.bead_arc(surf, cx, int(boss_y + r * 0.06), halo_r,
                math.radians(-150), math.radians(-30),
                max(2, int(2.4 * s)), s, gold_every=3)


# ── REVIEW PANEL ──────────────────────────────────────────────────────────────
def _label(surf, txt, x, y, sz=22, col=None):
    f = sk.font(sz)
    surf.blit(f.render(txt, True, col or sk.LABEL), (x, y))


if __name__ == "__main__":
    # (a) TRUE chip render — exact downscale recipe from the brief.
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.40) * ssr
    sline = (int(min(cw, ch) * 0.40) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.52)
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)

    # (b) ~300px hero — same draw at native res for detail review.
    HS = 320
    hero = pygame.Surface((HS, HS), pygame.SRCALPHA)
    hr = int(HS * 0.30)
    hs = (HS * 0.30) / 12.0
    draw(hero, HS // 2, int(HS * 0.52), hr, hs)
    hero = sk.grow_outline(hero, sk.INK + (255,), max(1, int(hs * 0.9)))

    # blackout chip (silhouette self-audit) — fill the chip alpha solid black.
    black = pygame.Surface((cw, ch), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(chip)
    for px, py in mask.outline():
        pass
    for yy in range(ch):
        for xx in range(cw):
            if mask.get_at((xx, yy)):
                black.set_at((xx, yy), sk.INK + (255,))

    # compose the panel
    PW, PH = 760, 520
    panel = pygame.Surface((PW, PH))
    panel.fill(sk.BG)
    pygame.draw.rect(panel, sk.PANEL, (0, 0, PW, 60))
    _label(panel, "cyclops-brow (WILD) — one-eyed monk-relic · round_1", 18, 16, 24)

    # day + night strips behind the hero so the cyan reads against both biomes
    def sky_grad(w, h, top, bot):
        g = pygame.Surface((w, h))
        for yy in range(h):
            g.fill(sk.lerp(top, bot, yy / max(1, h - 1)), (0, yy, w, 1))
        return g
    hx, hy = 360, 110
    panel.blit(sky_grad(HS, HS, sk.DAY_SKY_T, sk.DAY_SKY_B), (hx, hy))
    panel.blit(hero, (hx, hy))
    _label(panel, "(b) ~300px hero", hx + 80, hy + HS + 8, 20, sk.LABEL_DIM)

    # chip column on the left at TRUE size + a 3x zoom so the panel reader sees it
    cxp, cyp = 40, 110
    pygame.draw.rect(panel, sk.PANEL, (cxp - 8, cyp - 8, cw + 16, ch + 16), border_radius=6)
    panel.blit(chip, (cxp, cyp))
    _label(panel, "(a) TRUE 24px-class chip", cxp - 6, cyp + ch + 8, 18, sk.LABEL_DIM)

    zoom = pygame.transform.scale(chip, (cw * 2, ch * 2))
    zx, zy = cxp, cyp + ch + 40
    panel.blit(zoom, (zx, zy))
    _label(panel, "chip @2x", zx + 60, zy + ch * 2 + 4, 18, sk.LABEL_DIM)

    # blackout self-audit (is it a heavy-brow lightbulb, not a teardrop?)
    bx, by = cxp + cw * 2 + 30, cyp + ch + 40
    pygame.draw.rect(panel, (210, 214, 224), (bx - 6, by - 6, cw + 12, ch + 12), border_radius=6)
    panel.blit(black, (bx, by))
    _label(panel, "blackout audit", bx + 18, by + ch + 4, 18, sk.LABEL_DIM)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    print("wrote", out, os.path.exists(out))

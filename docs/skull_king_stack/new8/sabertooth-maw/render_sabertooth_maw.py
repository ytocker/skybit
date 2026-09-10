import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

# SABERTOOTH-MAW — a predator reliquary skull whose whole read is the two long
# down-curving SABRE FANGS plunging BELOW the jawline. WHY the menace lives below
# the jaw: nothing else in the Skull-King set claims that silhouette region, so an
# inverted-tongs / downward-dagger mass instantly distinguishes this figure at
# chip scale. The cranium is deliberately COMPACT up top — the eye is pulled down
# to the dropped, agape jaw and the fang pair so the mass reads bottom-heavy.


def draw(surf, cx, cy, r, s, lit=False):
    """Compact chibi predator cranium with an agape dropped jaw and two long
    sabre fangs hooking inward below it. Reuses only sk primitives + palette.
    `r` ~ cranium radius unit; `s` stroke unit (thick~1.6s, thin~1.0s). The fang
    mass is the load-bearing silhouette, so it is drawn wide-at-root, tapering to
    inward-hooked tips that stop SHORT of touching — an open central gap keeps the
    two fangs from fusing into one dark blob when blacked out at 24px."""
    thick = max(1, int(1.6 * s))
    thin = max(1, int(1.0 * s))
    BONE, BONE_D, BONE_DD, BONE_SH = sk.BONE, sk.BONE_D, sk.BONE_DD, sk.BONE_SH
    INK, GOLD, GOLD_D = sk.INK, sk.GOLD, sk.GOLD_D
    rot = math.radians

    # ── FANGS first → drawn behind the jaw so the jaw seats over the fang roots ──
    # WHY draw fangs before the jaw plate: the roots tuck UNDER the dropped jaw,
    # reading as teeth emerging from the maw rather than pasted-on horns. Each fang
    # is a tapering quad spine (wide root → narrow body) capped by an inward HOOK.
    def fang(sgn):
        # root anchors wide apart under the jaw corners; tip hooks toward centre
        root_x = cx + sgn * int(r * 0.50)
        root_y = cy + int(r * 0.60)
        # control points sweep down-and-slightly-out, then the tip hooks inward.
        # the inward hook tips stop short of the axis → an open gap (no fusing).
        body_x = cx + sgn * int(r * 0.58)
        body_y = cy + int(r * 1.24)
        tip_x = cx + sgn * int(r * 0.24)      # hooked inward, but NOT to centre
        tip_y = cy + int(r * 1.82)
        # outer edge (wide root → body) and inner edge define the tapering blade;
        # min width clamps so the blade is never thinner than ~2-3px after scale.
        wr = max(int(2.8 * s), int(r * 0.22))   # half-width at root
        wt = max(int(1.6 * s), int(r * 0.10))   # half-width near the hooked tip
        outer = [(root_x + sgn * wr, root_y),
                 (body_x + sgn * wr, body_y),
                 (tip_x + sgn * wt, tip_y)]
        inner = [(tip_x - sgn * wt, tip_y),
                 (body_x - sgn * wr, body_y),
                 (root_x - sgn * wr, root_y)]
        blade = outer + inner
        sk.triad_blob(surf, BONE, [(int(x), int(y)) for x, y in blade], ow=thick)
        # a top-rooted sheen sliver down the outer face (the triad highlight)
        sheen = [(root_x + sgn * int(wr * 0.5), root_y + int(r * 0.05)),
                 (body_x + sgn * int(wr * 0.5), body_y - int(r * 0.10)),
                 (body_x, body_y - int(r * 0.10)),
                 (root_x, root_y + int(r * 0.05))]
        pygame.draw.polygon(surf, BONE_SH, [(int(x), int(y)) for x, y in sheen])
        # a carved blood-groove down the blade centre (deep hollow read)
        pygame.draw.line(surf, BONE_DD,
                         (int(root_x), int(root_y + r * 0.08)),
                         (int((body_x + tip_x) / 2), int((body_y + tip_y) / 2)), thin)

    fang(-1)
    fang(+1)

    # ── DROPPED AGAPE JAW plate — seats over the fang roots, hangs open below the
    # cranium. WHY a dark maw gap above it: the open mouth sells "agape" and lets
    # the upper fang roots read as emerging from inside the maw. No small upper
    # tooth slits — the two sabres carry the entire tooth read (AD-locked).
    maw = [(cx - int(r * 0.50), cy + int(r * 0.30)),
           (cx + int(r * 0.50), cy + int(r * 0.30)),
           (cx + int(r * 0.42), cy + int(r * 0.70)),
           (cx - int(r * 0.42), cy + int(r * 0.70))]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in maw])
    jaw = [(cx - int(r * 0.46), cy + int(r * 0.58)),
           (cx + int(r * 0.46), cy + int(r * 0.58)),
           (cx + int(r * 0.30), cy + int(r * 0.92)),
           (cx - int(r * 0.30), cy + int(r * 0.92))]
    sk.triad_blob(surf, BONE, [(int(x), int(y)) for x, y in jaw], ow=thick)
    # a chin shade pocket so the jaw plate reads as rounded bone, not a flat bar
    pygame.draw.line(surf, BONE_D, (int(cx - r * 0.22), int(cy + r * 0.80)),
                     (int(cx + r * 0.22), int(cy + r * 0.80)), thin)

    # ── COMPACT CRANIUM — a low, broad predator dome that tapers to cheekbones
    # framing the maw. Kept short on purpose so the centre of mass reads BELOW it.
    dome = []
    for ang in range(-180, 1, 18):
        a = rot(ang)
        dome.append((cx + math.cos(a) * r * 1.04, cy + math.sin(a) * r * 0.86))
    # cheekbones flare out then taper down to the jaw line, framing the maw
    dome.append((cx + int(r * 0.86), cy + int(r * 0.12)))
    dome.append((cx + int(r * 0.52), cy + int(r * 0.40)))
    dome.append((cx - int(r * 0.52), cy + int(r * 0.40)))
    dome.append((cx - int(r * 0.86), cy + int(r * 0.12)))
    sk.triad_blob(surf, BONE, [(int(x), int(y)) for x, y in dome], ow=thick)
    # top-left sheen wedge (triad highlight on the cranium)
    sheen = [(cx - int(r * 0.62), cy - int(r * 0.10)),
             (cx - int(r * 0.12), cy - int(r * 0.62)),
             (cx - int(r * 0.02), cy - int(r * 0.30)),
             (cx - int(r * 0.48), cy + int(r * 0.04))]
    pygame.draw.polygon(surf, BONE_SH, [(int(x), int(y)) for x, y in sheen])

    # cranial suture — a short median seam + a brow ridge (carved-bone read)
    pygame.draw.line(surf, BONE_DD, (int(cx), int(cy - r * 0.74)),
                     (int(cx), int(cy - r * 0.18)), thin)
    pygame.draw.line(surf, BONE_DD, (int(cx - r * 0.40), int(cy - r * 0.18)),
                     (int(cx + r * 0.40), int(cy - r * 0.18)), thick)

    # ── SOCKETS — a heavy dark predator socket on each side; the LEFT socket holds
    # the lone cyan eye (focal=False — brightest point of THIS skull, capped under
    # the king's hero gem). The opposite socket stays a hollow ink pit + gold rim
    # so the gem socket reads as the single accent.
    sock_r = int(r * 0.30)
    eyL = (cx - int(r * 0.42), cy - int(r * 0.04))
    eyR = (cx + int(r * 0.42), cy - int(r * 0.04))
    for (ex, ey) in (eyL, eyR):
        pygame.draw.circle(surf, BONE_D, (ex, ey), sock_r + thin)
        pygame.draw.circle(surf, INK, (ex, ey), sock_r)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(sock_r * 0.6))
    # warm gold bezel around the hollow socket so both sockets feel jewel-set bone
    pygame.draw.circle(surf, GOLD_D, eyR, sock_r, thin)
    # the predator eye — DIM cyan cut-stone, focal OFF (value-ladder cap)
    sk.cyan_gem(surf, eyL, max(2, int(sock_r * 0.58)), s, focal=False)

    # nasal aperture — an inverted ink teardrop above the maw
    n_top = (cx, cy + int(r * 0.06))
    n_l = (cx - int(r * 0.13), cy + int(r * 0.30))
    n_r = (cx + int(r * 0.13), cy + int(r * 0.30))
    pygame.draw.polygon(surf, INK, [(int(n_top[0]), int(n_top[1])),
                                    (int(n_l[0]), int(n_l[1])),
                                    (int(n_r[0]), int(n_r[1]))])


# ── review sheet ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    W, H = 520, 420
    panel = pygame.Surface((W, H))
    panel.fill(sk.PANEL)

    f_title = sk.font(26)
    f_lab = sk.font(16)
    panel.blit(f_title.render("SABERTOOTH-MAW", True, sk.LABEL), (18, 14))
    panel.blit(f_lab.render("predator reliquary — sabre fangs below the jaw",
                            True, sk.LABEL_DIM), (18, 46))

    # (a) TRUE chip render — the deliverable scale recipe
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.34) * ssr
    sline = (int(min(cw, ch) * 0.34) / 12.0) * ssr
    cx = cw * ssr // 2
    # mass hangs BELOW the jaw — shift cy UP so the long fangs fit the cell
    cy = int(ch * ssr * 0.34)
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)),
                           sk.INK + (255,), 1)

    chip_x, chip_y = 40, 100
    panel.blit(f_lab.render("(a) chip ~24px read", True, sk.LABEL_DIM), (chip_x - 6, chip_y - 26))
    panel.blit(chip, (chip_x, chip_y))
    # a TRUE 24px down-render beside it, nearest so we judge the real silhouette
    chip24 = pygame.transform.smoothscale(chip, (24, int(24 * ch / cw)))
    panel.blit(f_lab.render("24px", True, sk.LABEL_DIM), (chip_x + 70, chip_y + 40))
    panel.blit(chip24, (chip_x + 72, chip_y + 60))
    # blacked-out silhouette self-audit swatch
    sil = pygame.mask.from_surface(chip).to_surface(setcolor=(20, 20, 20),
                                                    unsetcolor=(120, 124, 136))
    sil = pygame.transform.smoothscale(sil, (24, int(24 * ch / cw)))
    panel.blit(f_lab.render("mask", True, sk.LABEL_DIM), (chip_x + 70, chip_y + 96))
    panel.blit(sil, (chip_x + 72, chip_y + 116))

    # (b) ~300px hero
    HR = 300
    hero = pygame.Surface((HR, HR), pygame.SRCALPHA)
    hr = int(HR * 0.27)
    hs = hr / 18.0
    hcx = HR // 2
    hcy = int(HR * 0.34)
    draw(hero, hcx, hcy, hr, hs)
    hero = sk.grow_outline(hero, sk.INK + (255,), 2)
    hero_x, hero_y = 200, 96
    panel.blit(f_lab.render("(b) ~300px hero", True, sk.LABEL_DIM), (hero_x + 60, hero_y - 4))
    panel.blit(hero, (hero_x, hero_y + 16))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    print("wrote", out)

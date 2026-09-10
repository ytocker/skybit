"""
Round-1 concept renderer for KEYHOLE-RELIC — a Skull-King figure whose entire
identity is a HOLE punched clean through the cranium. Headless Pygame; ELEVATED
pipeline (SS=6 supersample → smoothscale) so the interior negative space survives
the downscale to chip size.

WHY this concept is distinct from every other skull in the set: no other has an
interior cutout in its OUTLINE. Here the natural occipital foramen is enlarged
into a bold ovoid void punched right through the upper-central cranium, so the
silhouette literally has a hole in it — the background shows through the bone.
That void IS the figure's identity; a blacked-out chip still reads as "the skull
with the hole."

WHY it reads as bounded bone and not a smudge: the void is genuinely transparent
(alpha multiplied to zero inside the circle on the SRCALPHA surface), rimmed by a
darker CROWN_BONE_D ring drawn AFTER the punch so the rim survives, and the chip's
grow_outline keylines the inner edge too — so the hole carries the same hard ink
edge as the outer silhouette.

WHY the CROWN-RELIC tier: cyan-FREE and gold-FREE, geometry only, on the dim
cooler CROWN_BONE family so this relic sits as the quietest, oldest member of the
stack — its drama is structural (the void), not chromatic.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers from the
asthi_ringeye reference, not runtime sprite modules.
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk


def draw(surf, cx, cy, r, s, lit=False):
    """KEYHOLE-RELIC cranium: a solid rounded CROWN_BONE skull with normal sockets
    + jaw, then a bold ovoid foramen punched THROUGH the upper-central cranium so
    the silhouette carries a real interior void.

    cx,cy   centre of the cranium
    r       cranium scale (~cranium half-width reference)
    s       stroke unit; thick stroke ~1.6*s, thin ~1.0*s
    lit     unused for this tier (cyan/gold-free, geometry only) — kept for the
            shared draw() signature so the harness can call every concept alike.
    """
    thick = max(2, int(round(1.6 * s)))
    thin  = max(1, int(round(1.0 * s)))

    BONE   = sk.CROWN_BONE
    BONE_D = sk.CROWN_BONE_D
    SH     = sk.CROWN_SH
    HOLLOW = sk.BONE_DD
    INK    = sk.INK

    # ── cranium dome: a rounded wide bell, drawn as a filled polygon so the
    # silhouette is clean and the rim-sheen/dark-core triad can be layered on.
    cw = r                      # cranium half-width
    ch = int(r * 1.18)          # cranium half-height (slightly taller than wide)
    dome = []
    for i in range(33):
        a = math.pi * (i / 32.0)            # 0..pi sweep across the top dome
        dome.append((cx - int(cw * math.cos(a)),
                     cy - int(ch * 0.62 * math.sin(a)) - int(ch * 0.18)))
    # zygomatic cheeks taper down to the jaw — close the cranium polygon
    jaw_w = int(cw * 0.74)
    jaw_top = cy + int(ch * 0.30)
    jaw_bot = cy + int(ch * 0.86)
    crani = dome + [
        (cx + int(cw * 0.98), cy + int(ch * 0.04)),
        (cx + int(cw * 0.86), cy + int(ch * 0.26)),
        (cx + jaw_w,          jaw_top),
        (cx + int(jaw_w*0.84),jaw_bot),
        (cx,                  cy + int(ch * 0.98)),
        (cx - int(jaw_w*0.84),jaw_bot),
        (cx - jaw_w,          jaw_top),
        (cx - int(cw * 0.86), cy + int(ch * 0.26)),
        (cx - int(cw * 0.98), cy + int(ch * 0.04)),
    ]
    # dark-core (pushed down-right) + top-left sheen, via the house triad
    core = [(int(x + cw * 0.10), int(y + ch * 0.10)) for (x, y) in crani]
    sheen = [(int(cx + (x - cx) * 0.62 - cw * 0.18),
              int(cy + (y - cy) * 0.62 - ch * 0.20)) for (x, y) in dome]
    sk.triad_blob(surf, BONE, crani, sheen_pts=sheen, core_pts=core,
                  outline=True, ow=thick)

    # ── eye sockets: two sunken hollows low on the face (below the foramen).
    sock_r = int(r * 0.30)
    sock_y = cy + int(ch * 0.30)
    sock_dx = int(cw * 0.46)
    for sx in (cx - sock_dx, cx + sock_dx):
        pygame.draw.circle(surf, INK, (sx, sock_y), sock_r + thin)
        pygame.draw.circle(surf, HOLLOW, (sx, sock_y), sock_r)
        # a faint inner deepening so the socket reads as a bowl, not a flat disc
        pygame.draw.circle(surf, sk.lerp(HOLLOW, INK, 0.5),
                           (sx + int(sock_r * 0.18), sock_y + int(sock_r * 0.22)),
                           int(sock_r * 0.62))

    # ── nasal aperture: a small inverted-heart hollow between/below the sockets.
    nx, ny = cx, cy + int(ch * 0.58)
    nasal = [(nx, ny - int(r * 0.10)),
             (nx - int(r * 0.13), ny + int(r * 0.16)),
             (nx, ny + int(r * 0.08)),
             (nx + int(r * 0.13), ny + int(r * 0.16))]
    pygame.draw.polygon(surf, INK, nasal)
    pygame.draw.polygon(surf, HOLLOW, [(int(x), int(y)) for (x, y) in nasal])

    # ── teeth band on the jaw: short vertical ticks so the lower face reads as a
    # mouth without competing with the foramen for attention.
    tn = 6
    tw = int(jaw_w * 1.4)
    ty = cy + int(ch * 0.70)
    for k in range(tn + 1):
        tx = cx - tw // 2 + int(tw * k / tn)
        pygame.draw.line(surf, sk.lerp(BONE, INK, 0.55),
                         (tx, ty - int(r * 0.06)), (tx, ty + int(r * 0.07)), thin)

    # ── THE FORAMEN — the identity. A bold ovoid hole punched through the
    # upper-central cranium. Diameter ~0.56× cranium width, seated high so it
    # never collides with the sockets below.
    hr = int(cw * 0.44)               # horizontal radius — punctuates, not consumes
    hvr = int(hr * 1.10)              # very slightly taller → ovoid
    hx, hy = cx, cy - int(ch * 0.40)  # raised → solid brow band above, sockets below

    # TRANSPARENT PUNCH: multiply alpha to 0 inside the ovoid so the bone is truly
    # erased there and the background shows through on the SRCALPHA surface.
    hole = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    hole.fill((255, 255, 255, 255))
    pygame.draw.ellipse(hole, (255, 255, 255, 0),
                        (hx - hr, hy - hvr, hr * 2, hvr * 2))
    surf.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # RIM drawn AFTER the punch so it survives: a darker CROWN_BONE_D ring binds
    # the void as deliberate bone, plus a hard INK keyline on the inner edge and a
    # thin top-left sheen arc so the rim reads as rounded, not a cut.
    rim_w = max(thick, int(round(2.0 * s)))
    pygame.draw.ellipse(surf, INK,
                        (hx - hr - thin, hy - hvr - thin,
                         (hr + thin) * 2, (hvr + thin) * 2), thick)
    pygame.draw.ellipse(surf, BONE_D,
                        (hx - hr, hy - hvr, hr * 2, hvr * 2), rim_w)
    # top-left sheen on the rim — a short bright arc catching the light
    pygame.draw.arc(surf, SH,
                    (hx - hr, hy - hvr, hr * 2, hvr * 2),
                    math.radians(60), math.radians(150),
                    max(1, thin))
    # inner ink keyline hugging the void edge so the transparent hole has the same
    # hard edge as the outer silhouette (grow_outline will reinforce it too)
    pygame.draw.ellipse(surf, INK,
                        (hx - hr, hy - hvr, hr * 2, hvr * 2), thin)


# ── review panel ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))

    # (a) TRUE chip render at ~24px-class scale via the brief's recipe.
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.40) * ssr
    sline = (int(min(cw, ch) * 0.40) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.52)
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(
        pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)

    # (b) ~300px hero — same draw() at large SS so the rim/sheen read.
    hss = 4
    hw = 300
    hbig = pygame.Surface((hw * hss, hw * hss), pygame.SRCALPHA)
    hr = int(hw * 0.40) * hss
    hsl = (int(hw * 0.40) / 12.0) * hss
    draw(hbig, hw * hss // 2, int(hw * hss * 0.52), hr, hsl)
    hero = sk.grow_outline(
        pygame.transform.smoothscale(hbig, (hw, hw)), sk.INK + (255,), 2)

    # blacked-out silhouette of the chip — the self-audit proof that the void is a
    # real hole in the outline (background shows through).
    sil = pygame.Surface((cw, ch), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(chip)
    for x in range(cw):
        for y in range(ch):
            if mask.get_at((x, y)):
                sil.set_at((x, y), sk.INK + (255,))

    # ── compose panel ──────────────────────────────────────────────────────────
    PW, PH = 720, 520
    panel = pygame.Surface((PW, PH))
    panel.fill(sk.BG)

    def label(txt, x, y, big=False, dim=False):
        f = sk.font(22 if big else 15)
        col = sk.LABEL if not dim else sk.LABEL_DIM
        panel.blit(f.render(txt, True, col), (x, y))

    label("KEYHOLE-RELIC  ·  CROWN-RELIC tier  ·  foramen punched THROUGH the cranium", 20, 16, big=True)
    label("cyan-free · gold-free · geometry only · the void IS the identity", 20, 46, dim=True)

    # checkerboard tiles so the transparent void is unmistakable on each render
    def checker(w, h, sz=8):
        s = pygame.Surface((w, h))
        a = (54, 58, 68); b = (74, 78, 90)
        for yy in range(0, h, sz):
            for xx in range(0, w, sz):
                s.fill(a if ((xx // sz + yy // sz) % 2 == 0) else b,
                       (xx, yy, sz, sz))
        return s

    # hero on its own checker
    hx0, hy0 = 30, 90
    panel.blit(checker(hw, hw), (hx0, hy0))
    panel.blit(hero, (hx0, hy0))
    label("(b) ~300px hero — background visible through the foramen", hx0, hy0 + hw + 6, dim=True)

    # chip + scale strip + silhouette on the right
    rx = 380
    # true chip on checker
    panel.blit(checker(cw, ch), (rx, hy0))
    panel.blit(chip, (rx, hy0))
    label("(a) true chip", rx, hy0 + ch + 4, dim=True)

    # 24px chip on checker (downscaled to the actual play size)
    chip24 = pygame.transform.smoothscale(chip, (24, 27))
    c24x = rx + cw + 26
    panel.blit(checker(24, 27), (c24x, hy0))
    panel.blit(chip24, (c24x, hy0))
    label("24px", c24x, hy0 + 27 + 4, dim=True)
    # 3x zoom of the 24px so reviewers can see what survives
    z = pygame.transform.scale(chip24, (72, 81))
    panel.blit(checker(72, 81), (c24x, hy0 + 50))
    panel.blit(z, (c24x, hy0 + 50))
    label("24px ·3", c24x, hy0 + 50 + 81 + 4, dim=True)

    # blacked-out silhouette proof — the HOLE must be visible here
    sx0 = rx
    sy0 = hy0 + ch + 36
    panel.blit(checker(cw, ch), (sx0, sy0))
    panel.blit(sil, (sx0, sy0))
    label("silhouette proof — HOLE in outline", sx0, sy0 + ch + 4, dim=True)

    pygame.image.save(panel, os.path.join(HERE, "round_1.png"))
    print("wrote", os.path.join(HERE, "round_1.png"))

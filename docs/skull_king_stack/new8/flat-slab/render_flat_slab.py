import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

# FLAT-SLAB (CROWN-RELIC) — the only non-domed skull in the set: a low, flat-topped
# masonry slab. WHY hard rectangles everywhere: the whole concept lives in the
# blackout silhouette, so the cranium is a battered BOX (flat horizontal crown,
# near-vertical temple walls), the brow is a full-width straight SHELF casting a
# shade band, and the sockets are deep-set RECTANGLES — circles would read as the
# same organic dome every sibling already is. Dimmest cool CROWN_BONE tier,
# geometry only: no cyan, no gold (the relic reads as carved stone, not jewel-set).


def draw(surf, cx, cy, r, s, lit=False):
    ow_thick = max(1, int(1.6 * s))
    ow_thin  = max(1, int(1.0 * s))

    # cooler/dimmer slab tier — a value step down from the crown-bone so the masonry
    # relic stays the darkest figure and never competes with the lit/jewel skulls.
    SLAB    = sk.lerp(sk.CROWN_BONE,   sk.INK, 0.14)
    SLAB_D  = sk.lerp(sk.CROWN_BONE_D, sk.INK, 0.10)
    SLAB_SH = sk.lerp(sk.CROWN_SH,     sk.INK, 0.08)

    # ── BOX CRANIUM ──────────────────────────────────────────────────────────────
    # A wide plateau: flat top, near-vertical temple walls, only the corners battered
    # (clipped) so the rectangle survives downscale without going round. The whole
    # silhouette must blackout as a box, so width > height and the walls stay plumb.
    half_w  = int(r * 1.06)            # wide — a horizontal plateau, not a dome
    top_y   = cy - int(r * 1.02)       # flat crown line
    wall_y  = cy + int(r * 0.50)       # temple walls run nearly straight down to here
    chamf   = int(r * 0.20)            # battered (clipped) corners — crisp, axis-aligned

    box = [
        (cx - half_w + chamf, top_y),              # top-left chamfer start
        (cx + half_w - chamf, top_y),              # top-right chamfer start
        (cx + half_w,         top_y + chamf),      # top-right corner
        (cx + half_w,         wall_y - chamf),     # right wall down
        (cx + half_w - chamf, wall_y),             # bottom-right batter
        (cx - half_w + chamf, wall_y),             # bottom-left batter
        (cx - half_w,         wall_y - chamf),
        (cx - half_w,         top_y + chamf),
    ]
    sk.triad_blob(surf, SLAB, box, ow=ow_thick)

    # flat top-lip sheen — a thin horizontal band hugging the crown edge (carved
    # masonry catches light on its flat top plane, reinforcing the slab read).
    sheen = [
        (cx - half_w + chamf + int(r*0.06), top_y + max(1, int(0.6*s))),
        (cx + half_w - chamf - int(r*0.06), top_y + max(1, int(0.6*s))),
        (cx + half_w - chamf - int(r*0.06), top_y + int(r * 0.16)),
        (cx - half_w + chamf + int(r*0.06), top_y + int(r * 0.16)),
    ]
    pygame.draw.polygon(surf, SLAB_SH, [(int(x), int(y)) for x, y in sheen])

    # left temple wall sheen — a thin vertical strip so the wall reads as a plumb,
    # lit masonry face (the top-left light direction of the house triad).
    pygame.draw.line(surf, SLAB_SH,
                     (cx - half_w + max(1, int(0.8*s)), top_y + int(r * 0.20)),
                     (cx - half_w + max(1, int(0.8*s)), wall_y - int(r * 0.16)),
                     max(1, int(1.2 * s)))

    # ── HEAVY BROW SHELF ───────────────────────────────────────────────────────
    # A full-width straight bar (>=2px) of the darker slab tier sitting proud of the
    # face, with a bright top-lip and a SHADE BAND dropped beneath it — the shelf is
    # the relic's signature: it must read as an overhanging shadow ledge at chip scale.
    brow_y  = cy - int(r * 0.18)
    brow_h  = max(2, int(r * 0.30))
    brow_l  = cx - int(half_w * 0.92)
    brow_r  = cx + int(half_w * 0.92)
    brow = [(brow_l, brow_y), (brow_r, brow_y),
            (brow_r + int(r*0.04), brow_y + brow_h),
            (brow_l - int(r*0.04), brow_y + brow_h)]
    pygame.draw.polygon(surf, sk.INK, [(int(x), int(y)) for x, y in brow])
    pygame.draw.polygon(surf, SLAB_D, [(int(x+0), int(y+max(1,int(0.8*s)))) for x, y in brow])
    # bright top-lip of the shelf — the lit leading edge of the overhang
    pygame.draw.line(surf, SLAB_SH, (brow_l, brow_y + max(1, int(0.6*s))),
                     (brow_r, brow_y + max(1, int(0.6*s))), max(2, int(1.4 * s)))
    # SHADE BAND — a darkened face strip directly under the shelf, so the brow casts
    # a clear horizontal shadow over the eye region (the deep-set read).
    shade_y0 = brow_y + brow_h
    shade_y1 = shade_y0 + int(r * 0.30)
    shade = [(brow_l, shade_y0), (brow_r, shade_y0),
             (brow_r, shade_y1), (brow_l, shade_y1)]
    pygame.draw.polygon(surf, SLAB_D, [(int(x), int(y)) for x, y in shade])

    # ── DEEP-SET RECTANGULAR SOCKETS ─────────────────────────────────────────────
    # Hard ink rectangles (never circles) tucked under the shelf — the angular socket
    # is what stops the eye region from reading as a soft dome's round eyes.
    sock_w  = int(r * 0.40)
    sock_h  = int(r * 0.34)
    sock_y  = shade_y0 + max(1, int(0.5 * s))
    gap     = int(r * 0.16)
    for sgn in (-1, 1):
        # symmetric rectangular sockets around a central pier (the gap)
        x0 = (cx - gap // 2 - sock_w) if sgn < 0 else (cx + gap // 2)
        rect = pygame.Rect(x0, sock_y, sock_w, sock_h)
        pygame.draw.rect(surf, sk.INK, rect)
        # a thin inner deepening at the bottom — the pit recedes (darkest core)
        inner = pygame.Rect(x0 + max(1, int(0.8*s)), sock_y + int(sock_h * 0.42),
                            sock_w - max(2, int(1.6*s)), sock_h - int(sock_h * 0.42) - max(1, int(0.6*s)))
        pygame.draw.rect(surf, sk.BONE_DD, inner)
        pygame.draw.rect(surf, sk.INK, inner, max(1, int(0.9 * s)))

    # central nasal — a narrow vertical rectangular slot (keeps the angular grammar)
    nas_w = max(2, int(r * 0.14))
    nas = pygame.Rect(cx - nas_w // 2, sock_y + int(sock_h * 0.34), nas_w, int(sock_h * 0.78))
    pygame.draw.rect(surf, sk.INK, nas)

    # ── SHORT SQUARED JAW ────────────────────────────────────────────────────────
    # A stubby rectangular mandible — narrower than the cranium but still hard-edged,
    # keeping the whole figure boxy from crown to chin.
    jaw_y0 = wall_y - max(1, int(1.0 * s))      # tuck just under the cranium base
    jaw_y1 = cy + int(r * 0.94)
    jaw_hw = int(half_w * 0.66)
    jchamf = int(r * 0.12)
    jaw = [
        (cx - jaw_hw, jaw_y0), (cx + jaw_hw, jaw_y0),
        (cx + jaw_hw, jaw_y1 - jchamf), (cx + jaw_hw - jchamf, jaw_y1),
        (cx - jaw_hw + jchamf, jaw_y1), (cx - jaw_hw, jaw_y1 - jchamf),
    ]
    sk.triad_blob(surf, SLAB, [(int(x), int(y)) for x, y in jaw], ow=max(1, int(1.4 * s)))

    # tooth row — short vertical ink slits on a straight gum line (angular, no curve)
    gum_y = jaw_y0 + int((jaw_y1 - jaw_y0) * 0.30)
    pygame.draw.line(surf, sk.INK, (cx - int(jaw_hw * 0.82), gum_y),
                     (cx + int(jaw_hw * 0.82), gum_y), max(1, int(1.2 * s)))
    n_teeth = 5
    for j in range(n_teeth):
        tx = cx - int(jaw_hw * 0.66) + j * int(jaw_hw * 1.32 / (n_teeth - 1))
        pygame.draw.line(surf, sk.INK, (tx, gum_y - int(r * 0.04)),
                         (tx, gum_y + int(r * 0.16)), max(1, int(1.0 * s)))

    # a vertical median seam on the crown — a single carved masonry joint (NOT a
    # rounded suture), reinforcing the "stacked stone" read on the flat top plane.
    pygame.draw.line(surf, SLAB_D, (cx, top_y + int(r * 0.10)),
                     (cx, brow_y - int(r * 0.04)), ow_thin)


# ── review panel ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    def font(sz):
        return sk.font(sz)

    # (a) TRUE chip render — the exact downscale recipe the brief pins.
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.40) * ssr
    sline = (int(min(cw, ch) * 0.40) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.52)
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)

    # (b) ~300px hero — same draw at large scale for detail inspection.
    HS = 256
    hero = pygame.Surface((HS, HS), pygame.SRCALPHA)
    hr = int(HS * 0.30)
    hs = hr / 12.0
    draw(hero, HS // 2, int(HS * 0.50), hr, hs)
    hero = sk.grow_outline(hero, sk.INK + (255,), max(1, int(1.4)))

    # compose labeled panel on the house review backdrop
    W, H = 560, 460
    panel = pygame.Surface((W, H))
    panel.fill(sk.BG)

    title = font(26).render("FLAT-SLAB  ·  CROWN-RELIC  ·  round 1", True, sk.LABEL)
    panel.blit(title, (20, 16))
    sub = font(15).render("the only hard-edged box skull: flat-top slab, brow shelf, rectangular sockets",
                          True, sk.LABEL_DIM)
    panel.blit(sub, (20, 48))

    # (a) chip card — render the true 24px-class chip, then also a magnified copy so
    # the panel shows BOTH the literal chip and a zoom of it (the readability proof).
    card_a = pygame.Rect(28, 84, 210, 330)
    pygame.draw.rect(panel, sk.PANEL, card_a, border_radius=10)
    la = font(16).render("(a) TRUE chip", True, sk.LABEL)
    panel.blit(la, (card_a.x + 12, card_a.y + 10))

    # literal chip at native size, centered near the top of the card
    cx_a = card_a.centerx - cw // 2
    cy_a = card_a.y + 40
    panel.blit(chip, (cx_a, cy_a))
    cap = font(13).render(f"{cw}x{ch}px native", True, sk.LABEL_DIM)
    panel.blit(cap, (card_a.centerx - cap.get_width() // 2, cy_a + ch + 4))

    # a small TRUE ~24px chip + a 4x zoom of it (the actual ship-scale read)
    chip24 = pygame.transform.smoothscale(chip, (24, int(24 * ch / cw)))
    z = pygame.transform.scale(chip24, (24 * 4, int(24 * ch / cw) * 4))
    zy = cy_a + ch + 26
    panel.blit(chip24, (card_a.x + 24, zy + 30))
    cap2 = font(12).render("24px", True, sk.LABEL_DIM)
    panel.blit(cap2, (card_a.x + 24, zy + 30 + chip24.get_height() + 2))
    panel.blit(z, (card_a.right - z.get_width() - 18, zy + 6))
    cap3 = font(12).render("4x zoom", True, sk.LABEL_DIM)
    panel.blit(cap3, (card_a.right - z.get_width() - 18, zy + 6 + z.get_height() + 2))

    # (b) hero card
    card_b = pygame.Rect(258, 84, 274, 330)
    pygame.draw.rect(panel, sk.PANEL, card_b, border_radius=10)
    lb = font(16).render("(b) hero ~300px", True, sk.LABEL)
    panel.blit(lb, (card_b.x + 12, card_b.y + 10))
    panel.blit(hero, (card_b.centerx - HS // 2, card_b.y + 44))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(panel, out)
    print("wrote", out)

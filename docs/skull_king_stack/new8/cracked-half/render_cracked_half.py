import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye"))
import pygame; pygame.init()
import render_switchbig as sk

# CRACKED-HALF (CROWN-RELIC) — a battle-worn relic split by a vertical fracture.
# WHY the break must live in the SILHOUETTE, not an interior line: the shipped
# crowns already do "lean" (a whole intact dome tilted), so the only way this reads
# as genuinely BROKEN at 24px is for the OUTLINE itself to be broken — a bite gone
# from the sheared temple corner and the two cranium halves stepped at clearly
# different heights. An interior crack alone smudges to a grey smear at chip scale,
# so the interior fracture is reduced to a SINGLE short top-edge notch only.
# WHY the dimmest CROWN tier, geometry-only: this is a CROWN-RELIC — no cyan, no
# gold; the silhouette break is the whole story.


def draw(surf, cx, cy, r, s, lit=False):
    thick = max(1, int(1.6 * s))
    thin  = max(1, int(1.0 * s))

    # Two cranium halves at clearly different heights. The intact (left) crown sits
    # at full height; the sheared (right) crown is dropped so its top is a clean STEP
    # below the left — the step has to survive the downscale, so it is generous
    # (~0.30r at supersample, well over the gate's ≥3px-in-chip threshold).
    step = int(r * 0.44)              # vertical shear between the two halves
    seam_x = cx - int(r * 0.04)       # fracture plane, just left of centre
    crown_l = cy - int(r * 1.02)      # intact crown top
    crown_r = crown_l + step          # sheared crown top (lower)

    # The sheared side also loses its TEMPLE CORNER — a bite taken straight out of
    # the outline so the right shoulder of the dome is a flat sheared facet, not a
    # rounded temple. This is the silhouette tell that says "broken", not "leaning".
    bite_x = cx + int(r * 0.66)       # where the temple corner has been sheared off
    bite_top = crown_r + int(r * 0.10)
    bite_bot = cy + int(r * 0.16)     # the shear cut runs down the right temple

    # ── INTACT LEFT HALF — a full rounded dome from crown round to the seam ──
    left = []
    # top-left dome arc: brow round, up over the crown, to the seam at full height
    for ang_deg in range(-180, -89, 15):     # left brow → crown apex
        a = math.radians(ang_deg)
        dx = math.cos(a) * r * 1.00
        dy = math.sin(a) * r * 1.02
        left.append((cx + dx, crown_l + r * 1.02 + dy))
    left.append((seam_x, crown_l))           # crown apex meets the seam (full height)
    left.append((seam_x, cy + int(r * 0.30)))# seam runs straight down the fracture
    left.append((cx - int(r * 0.70), cy + int(r * 0.30)))  # left cheek/jaw line
    left.append((cx - int(r * 1.00), cy - int(r * 0.10)))  # left temple
    left = [(int(x), int(y)) for x, y in left]
    sk.triad_blob(surf, sk.CROWN_BONE, left, ow=thick)

    # ── SHEARED RIGHT HALF — lower crown + a bitten-off temple corner ──
    right = []
    right.append((seam_x, crown_r))                        # crown apex, dropped (the STEP)
    # short rounded crown over the right half, then the SHEARED facet (the bite)
    right.append((cx + int(r * 0.30), crown_r - int(r * 0.04)))
    right.append((bite_x, bite_top))                       # corner of the shear facet
    right.append((cx + int(r * 0.92), bite_bot))           # sheared facet plunges in (BITE)
    right.append((cx + int(r * 0.74), cy + int(r * 0.18))) # remaining cheek
    right.append((cx + int(r * 0.30), cy + int(r * 0.30))) # right jaw line
    right.append((seam_x, cy + int(r * 0.30)))             # back to the seam
    right = [(int(x), int(y)) for x, y in right]
    sk.triad_blob(surf, sk.CROWN_BONE, right, ow=thick)

    # dim top-left sheen wedge on the intact half only (never brighter than body)
    sheen = [(cx - int(r * 0.62), crown_l + int(r * 0.40)),
             (cx - int(r * 0.16), crown_l + int(r * 0.06)),
             (cx - int(r * 0.06), crown_l + int(r * 0.46)),
             (cx - int(r * 0.50), crown_l + int(r * 0.84))]
    pygame.draw.polygon(surf, sk.CROWN_SH, [(int(x), int(y)) for x, y in sheen])

    # ── SINGLE short interior crack notch at the TOP edge only ──
    # WHY just a short top notch (not a full jagged polyline down the face): a long
    # interior crack mushes to a grey smudge at chip scale; one stubby BONE_DD wedge
    # biting down from the crown edge reads as the fracture mouth without smearing.
    notch = [(seam_x - int(r * 0.06), crown_r - int(r * 0.02)),
             (seam_x + int(r * 0.10), crown_r + int(r * 0.04)),
             (seam_x, crown_r + int(r * 0.34))]
    pygame.draw.polygon(surf, sk.BONE_DD, [(int(x), int(y)) for x, y in notch])

    # ── SOCKETS — the sheared (right) socket sits LOWER than the intact one ──
    # the height offset of the two eyes reinforces the broken/stepped read.
    sock_r = int(r * 0.27)
    lx, ly = cx - int(r * 0.42), cy - int(r * 0.06)        # intact socket
    rx, ry = cx + int(r * 0.40), cy + int(r * 0.10)        # sheared socket, dropped
    pygame.draw.circle(surf, sk.INK, (lx, ly), sock_r)
    pygame.draw.circle(surf, sk.INK, (rx, ry), sock_r)
    # faint cooler rim on the intact socket only (a carved-bone tell, dim tier)
    pygame.draw.circle(surf, sk.CROWN_BONE_D, (lx, ly), sock_r, thin)

    # nasal pit, biased toward the intact side (the face is off-centre after shear)
    pygame.draw.polygon(surf, sk.INK,
                        [(cx - int(r * 0.04), cy + int(r * 0.22)),
                         (cx - int(r * 0.18), cy + int(r * 0.46)),
                         (cx + int(r * 0.08), cy + int(r * 0.46))])

    # ── JAW — plain, tilted to MATCH the shear (lower on the sheared side) ──
    jaw = [(cx - int(r * 0.62), cy + int(r * 0.34)),
           (cx + int(r * 0.50), cy + int(r * 0.44)),     # right corner dropped (tilt)
           (cx + int(r * 0.34), cy + int(r * 0.96)),
           (cx - int(r * 0.40), cy + int(r * 0.86))]
    sk.triad_blob(surf, sk.CROWN_BONE, [(int(x), int(y)) for x, y in jaw], ow=thick)

    # plain tooth bar, tilted with the jaw; a single dropped tooth where it cracked
    ty0 = cy + int(r * 0.52)
    pygame.draw.line(surf, sk.INK,
                     (cx - int(r * 0.32), ty0),
                     (cx + int(r * 0.30), ty0 + int(r * 0.10)), thick)
    for j in range(3):
        f = j / 2.0
        tx = cx - int(r * 0.24) + int(f * r * 0.48)
        tyj = ty0 + int(f * r * 0.10)
        if j == 2:
            continue   # the sheared-side tooth is gone (matches the broken half)
        pygame.draw.line(surf, sk.INK, (tx, tyj - int(r * 0.08)),
                         (tx, tyj + int(r * 0.10)), thin)


if __name__ == "__main__":
    OUT = os.path.dirname(os.path.abspath(__file__))

    def label(surf, txt, x, y, color=(238, 240, 246), sz=22):
        surf.blit(sk.font(sz).render(txt, True, color), (x, y))

    # ── TRUE chip render (the gate) ──
    ssr = 6
    cw, ch = 116, 132
    big = pygame.Surface((cw * ssr, ch * ssr), pygame.SRCALPHA)
    r = int(min(cw, ch) * 0.40) * ssr
    sline = (int(min(cw, ch) * 0.40) / 12.0) * ssr
    cx = cw * ssr // 2
    cy = int(ch * ssr * 0.52)
    draw(big, cx, cy, r, sline)
    chip = sk.grow_outline(pygame.transform.smoothscale(big, (cw, ch)), sk.INK + (255,), 1)

    # ── ~300px hero render ──
    hw, hh = 300, 340
    hbig = pygame.Surface((hw * 3, hh * 3), pygame.SRCALPHA)
    hr = int(min(hw, hh) * 0.40) * 3
    hs = (int(min(hw, hh) * 0.40) / 12.0) * 3
    draw(hbig, hw * 3 // 2, int(hh * 3 * 0.52), hr, hs)
    hero = sk.grow_outline(pygame.transform.smoothscale(hbig, (hw, hh)), sk.INK + (255,), 1)

    # ── panel ──
    PW, PH = 760, 460
    panel = pygame.Surface((PW, PH))
    panel.fill(sk.BG)
    label(panel, "cracked-half (CROWN-RELIC) — sheared, stepped, bitten outline", 18, 12, sk.LABEL, 22)

    # (a) TRUE chip — shown at native 24px-ish plus a 3x inspect tile + a blackout
    chip_card = pygame.Surface((cw, ch))
    chip_card.fill(sk.PANEL)
    chip_card.blit(chip, (0, 0))
    panel.blit(chip_card, (24, 60))
    label(panel, "(a) chip", 24, 60 + ch + 4, sk.LABEL_DIM, 16)

    chip3 = pygame.transform.scale(chip, (cw * 2, ch * 2))
    c3card = pygame.Surface((cw * 2, ch * 2)); c3card.fill(sk.PANEL); c3card.blit(chip3, (0, 0))
    panel.blit(c3card, (24, 60 + ch + 28))
    label(panel, "2x inspect", 24, 60 + ch + 28 + ch * 2 + 2, sk.LABEL_DIM, 16)

    # blackout: the self-audit — does the OUTLINE alone read as broken/stepped?
    mask = pygame.mask.from_surface(chip)
    blk = pygame.Surface((cw, ch)); blk.fill((230, 232, 238))
    sil = mask.to_surface(setcolor=(20, 22, 28, 255), unsetcolor=(0, 0, 0, 0))
    blk.blit(sil, (0, 0))
    bcard = pygame.transform.scale(blk, (cw * 2, ch * 2))
    panel.blit(bcard, (24 + cw * 2 + 18, 60 + ch + 28))
    label(panel, "blackout (silhouette test)", 24 + cw * 2 + 18, 60 + ch + 28 + ch * 2 + 2, sk.LABEL_DIM, 16)

    # (b) hero
    panel.blit(hero, (PW - hw - 24, 56))
    label(panel, "(b) hero ~300px", PW - hw - 24, 56 + hh + 2, sk.LABEL_DIM, 16)

    pygame.image.save(panel, os.path.join(OUT, "round_1.png"))
    print("wrote", os.path.join(OUT, "round_1.png"))

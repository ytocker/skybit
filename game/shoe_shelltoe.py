import pygame


# SHELL TOE — chunky white low-top with the signature ribbed rubber toe cap
# and three bold dark side stripes. Authored in unit-box space (toe RIGHT at
# facing=1) so the SAME call serves the ~104x62 product shot and the ~15x10
# bird-foot sprite. The two hero cues are kept loud on purpose: three FAT
# stripes that survive downscale, and a few FAT ribs that read as texture
# rather than gray mush. Baseline + cupsole thickness match AIR FLYER /
# COURT GREEN so the Store grid sits level. Stylized homage, no real logo.

_UPPER      = (245, 245, 240)   # off-white upper body
_UPPER_EDGE = (212, 210, 202)   # upper shadow / soft 1px seam
_SHELL      = (238, 236, 228)   # rubber shell toe cap
_SHELL_EDGE = (190, 188, 180)   # cap seam against the upper
_RIB_HI     = (250, 250, 246)   # fat rib highlight
_RIB_LO     = (176, 174, 166)   # fat rib shadow — high contrast so it reads
_SOLE       = (250, 250, 248)   # flat white cupsole face
_SOLE_EDGE  = (60, 60, 66)      # crisp dark sole/upper break + ground line
_STRIPE     = (26, 26, 32)      # the three bold side stripes
_LACE       = (250, 250, 248)
_LACE_EDGE  = (200, 200, 196)
_COLLAR     = (224, 224, 218)   # collar / heel quarter shading


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile SHELL TOE sneaker into box (x, y, w, h).

    Toe points RIGHT when facing=1 (mirrored for -1): the ribbed shell cap
    wraps the toe (+x side), the three stripes rake the midfoot just behind
    it. No outer outline — the caller adds the house outline.
    """
    # Unit-box mapping mirrored about u=0.5 for facing=-1, matching the rest of
    # the set so one body of geometry serves both store orientations / feet.
    def px(u):
        return x + (u * w if facing == 1 else (1.0 - u) * w)

    def py(v):
        return y + v * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(u), py(v)) for u, v in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, (px(a[0]), py(a[1])),
                         (px(b[0]), py(b[1])), max(1, int(round(width))))

    # Bottom ~22% of the box is the cupsole; baseline at v=1.0 and sole crown
    # near v=0.78 mirror AIR FLYER so the Store row of shoes sits flat.
    ground   = 1.00
    sole_top = 0.80   # where the white cupsole meets the upper
    up_top   = 0.28   # crown of the rounded low-top upper

    # ── white rubber cupsole: flat slab, faint toe spring, crisp dark edge ──
    poly(_SOLE_EDGE, [
        (0.04, sole_top), (0.20, sole_top - 0.02), (0.94, sole_top - 0.02),
        (0.985, sole_top + 0.02), (0.96, ground), (0.05, ground),
        (0.015, sole_top + 0.06),
    ])
    poly(_SOLE, [
        (0.05, sole_top + 0.005), (0.94, sole_top + 0.005),
        (0.955, sole_top + 0.05), (0.06, sole_top + 0.06),
    ])
    # The signature crisp dark break where the cupsole meets the upper.
    line(_SOLE_EDGE, (0.05, sole_top), (0.95, sole_top - 0.015),
         h * 0.035)
    # Thin dark ground line.
    line(_SOLE_EDGE, (0.06, ground - 0.01), (0.95, ground - 0.01),
         h * 0.025)

    # ── main off-white upper body (heel quarter through vamp) ──────────────
    poly(_UPPER, [
        (0.05, sole_top), (0.05, 0.50), (0.10, 0.38),
        (0.24, up_top + 0.02), (0.42, up_top), (0.58, up_top + 0.02),
        (0.72, 0.40), (0.86, 0.56), (0.90, sole_top),
    ])
    # Soft heel-back seam for definition.
    poly(_UPPER_EDGE, [
        (0.05, sole_top), (0.05, 0.50), (0.075, 0.50), (0.075, sole_top),
    ])

    # ── three FAT dark side stripes raking the MIDFOOT, just behind the cap ─
    # Authored first under the cap so the cap's back edge laps cleanly over
    # them. Thick bars + thick white gaps so the block reads as THREE at 48px
    # and at least a dark diagonal slash at 16px.
    rake  = 0.05          # forward lean of each bar
    s_w   = 0.075         # bar thickness (loud on purpose)
    s_gap = 0.055         # white gap between bars
    s_top = up_top + 0.14
    s_bot = sole_top - 0.005
    bx = 0.40             # leading edge of the first bar
    for _ in range(3):
        poly(_STRIPE, [
            (bx, s_bot), (bx + s_w, s_bot),
            (bx + s_w + rake, s_top), (bx + rake, s_top),
        ])
        bx += s_w + s_gap

    # ── ribbed rubber SHELL TOE cap wrapping the toe (right side) ──────────
    # A rounded cap owning the front ~28% of the width. Drawn after the
    # stripes so its flat back edge laps over the last stripe, anchoring the
    # cap "in front of" the three-stripe block.
    cap_back  = 0.68
    cap_front = 0.985
    cap_top   = up_top + 0.18
    cap_bot   = sole_top
    poly(_SHELL, [
        (cap_back, cap_bot), (cap_back, cap_top + 0.06),
        (cap_back + 0.08, cap_top), (0.85, cap_top - 0.02),
        (cap_front - 0.05, cap_top + 0.06), (cap_front, cap_top + 0.22),
        (cap_front, cap_bot),
    ])
    # Cap seam against the upper, so it separates even when edge lines vanish.
    line(_SHELL_EDGE, (cap_back, cap_top + 0.06), (cap_back, cap_bot),
         h * 0.022)

    # FAT vertical ribs — 4 wide bars with hard highlight/shadow pairs so the
    # toe reads as ribbed rubber, not gray mush. Each rib is a light face with
    # a darker right lip.
    n_ribs = 4
    rib_w = max(2, int(w * 0.026))
    span0, span1 = cap_back + 0.07, cap_front - 0.05
    for i in range(n_ribs):
        t = (i + 0.5) / n_ribs
        ru = span0 + (span1 - span0) * t
        # Ribs hug the toe curve: a touch shorter toward the rounded front.
        droop = (t - 0.5) * (t - 0.5) * 0.10
        r_top = cap_top + 0.12 + droop
        r_bot = cap_bot - 0.015
        # Dark groove first (wide), bright rib face on top — the high value
        # contrast is what makes the ribbing read as texture, not gray mush.
        gu = ru + (rib_w + 1) / float(w)
        line(_RIB_LO, (gu, r_top + 0.005), (gu, r_bot), max(2, rib_w // 2 + 1))
        line(_RIB_HI, (ru, r_top), (ru, r_bot), rib_w)

    # ── collar dip + heel quarter shading for the low-top read ─────────────
    poly(_COLLAR, [
        (0.07, 0.42), (0.16, up_top + 0.01), (0.28, up_top + 0.05),
        (0.22, 0.46), (0.09, 0.50),
    ])
    # Heel tab nub at the back — small shell-toe cue.
    poly(_SHELL, [
        (0.045, up_top + 0.06), (0.10, up_top + 0.02),
        (0.105, 0.40), (0.05, 0.42),
    ])

    # ── fat flat laces over the throat ─────────────────────────────────────
    lace_w = 0.20
    for i in range(3):
        lv = up_top + 0.06 + i * 0.10
        lu = 0.22 + i * 0.012
        rect = pygame.Rect(
            int(min(px(lu), px(lu + lace_w))), int(py(lv)),
            int(abs(px(lu + lace_w) - px(lu))), max(2, int(h * 0.07)))
        rad = max(1, rect.height // 2)
        pygame.draw.rect(surf, _LACE, rect, border_radius=rad)
        pygame.draw.rect(surf, _LACE_EDGE, rect, width=1, border_radius=rad)

    # Subtle vamp seam to break the large white field on the product shot.
    line(_UPPER_EDGE, (0.30, up_top + 0.03), (0.66, 0.34), 1)

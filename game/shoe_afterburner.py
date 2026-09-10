import math

import pygame


# AFTERBURNER — legendary rocket-thruster boot. The hero read is THRUST: a
# chrome/steel mecha boot shell with a rear exhaust nozzle at the heel and a
# layered flame plume (red outer → orange → white-hot core) streaming BEHIND
# the boot, blasting past the box on the low-t (heel) side. Chrome is sold by a
# bright top highlight + steel underside shadow on every plate so it reads
# metallic, not flat grey; riveted plating + glowing heat vents add the mecha
# detail. The flame is the signature — it is drawn on a soft SRCALPHA glow layer
# so even at 40px the eye sees a hot exhaust trail, not just a boot.
#
# Geometry is proportional in facing=1 (toe right, heel/exhaust left) space and
# mirrors for facing=-1 so one body of shapes serves both directions. The plume
# deliberately runs to t<0 (behind the heel) AND slightly above the box, so
# callers must leave rear + top headroom or it clips.

_CHROME   = (201, 210, 219)   # bright chrome plate
_CHROME_HI = (242, 247, 252)  # chrome specular highlight (the metal "shine")
_STEEL    = (110, 122, 136)   # steel mid
_STEEL_D  = ( 64,  72,  84)   # steel underside shadow
_PLATE_D  = ( 42,  46,  54)   # dark plating / seams / nozzle mouth
_RIVET    = (225, 232, 238)   # rivet dot

_FLAME_RED = (226,  40,  16)  # outer plume
_FLAME_ORG = (255, 122,  26)  # mid plume
_FLAME_YEL = (255, 226, 122)  # inner flame
_FLAME_WHT = (255, 252, 232)  # white-hot core
_VENT_GLOW = (255, 150,  40)  # heat-vent glow


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile AFTERBURNER rocket boot into box (x,y,w,h)."""
    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [(px(a), py(b)) for a, b in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, (px(a[0]), py(a[1])),
                         (px(b[0]), py(b[1])), max(1, int(round(width))))

    sole_top = 0.78

    # ── FLAME PLUME (drawn first, behind the boot) ───────────────────────────────
    # The hero read. A single TEARDROP plume: tall rounded root flush against the
    # nozzle bell, tapering to a narrow point at the tail, biased DOWN-and-back so
    # it reads as a thrust vector, not a dead-horizontal diamond. Built as three
    # nested chunky values — red rim / orange body / white core — so it survives
    # the 17px foot box with hard readable edges (no supersample-dependent
    # subtlety). A soft outer glow underlay is blitted UNDER the chunky flame so
    # the icon blooms and the red rim separates from a dark night sky, but the
    # readable shape never depends on that bloom.
    #
    # Plume box-t window: root overlaps PAST the nozzle lip (T_MAX>0) so fire and
    # machine touch; tail runs to T_MIN well behind the heel for a long exhaust.
    T_MIN, T_MAX = -0.92, 0.20

    # Teardrop tongue: a tall rounded root flush at the nozzle that tapers to a
    # single narrow point at the tail. Built from a centreline that DROOPS
    # down-and-back (thrust vector) with a half-width that shrinks from fat at the
    # root to zero at the tip. Sampling along the centreline and offsetting by the
    # half-width gives a smooth tongue whose top edge sinks toward the tail and
    # whose bottom edge sinks faster — never a flat-topped lozenge.
    def _tongue(root_t, half, tip_t, sink):
        # root_t: nozzle-side anchor; half: root half-height; tip_t: tail point;
        # sink: how far the centreline drops from root to tip (down-and-back bias).
        n = 7
        top, bot = [], []
        for i in range(n + 1):
            f = i / n                          # 0 at root → 1 at tail point
            t = root_t + (tip_t - root_t) * f
            cy = sink * (f ** 1.3)             # centreline droops toward tail
            # Half-width: fat near root, eased to a sharp zero at the tip.
            hw = half * (1.0 - f) ** 1.45
            top.append((t, cy - hw))
            bot.append((t, cy + hw))
        # Rounded root crown/base (pull the nozzle-side edge slightly outward) →
        # a bulged root, not a clipped flat end.
        crown = (root_t + 0.03, -half * 0.55)
        base = (root_t + 0.03, half * 0.55)
        return [crown] + top[1:] + list(reversed(bot[1:])) + [base]

    # Three nested tongues, each shorter + thinner so inner values sit inside the
    # outer rim. The white core is a slim short lance biased toward the nozzle
    # (short reach, low droop) — a hot blade at the throat, not a centred blob.
    red_t  = _tongue(0.18, 0.40, T_MIN, sink=0.52)
    org_t  = _tongue(0.17, 0.30, -0.60, sink=0.46)
    core_t = _tongue(0.15, 0.16, -0.22, sink=0.34)

    # Soft outer glow underlay — a fat blurred red-orange teardrop so the plume
    # has atmosphere and the rim pops on night sky. Built supersampled then
    # smooth-downscaled; purely additive mood under the chunky shape.
    ss = 2
    span = T_MAX - T_MIN
    gw = max(2, int(round(w * span * ss)))
    gh = max(2, int(round(h * 2.4 * ss)))
    glow = pygame.Surface((gw, gh), pygame.SRCALPHA)
    gy0 = h * ss * 1.2

    def gpt(t, b):
        return ((t - T_MIN) * w * ss, gy0 + b * h * ss)

    for col, alpha, scl in ((_FLAME_RED, 95, 1.25), (_FLAME_ORG, 120, 0.95)):
        glow_pts = [gpt(t, b * scl + 0.06) for t, b in red_t]
        pygame.draw.polygon(glow, (*col, alpha), glow_pts)
    soft = pygame.transform.smoothscale(
        glow, (max(1, int(w * span)), max(1, int(h * 2.4))))
    gx0 = px(T_MIN if facing == 1 else T_MAX) - (0 if facing == 1 else int(w * span))
    surf.blit(soft, (gx0, py(0.0) - h * 1.2))

    # Chunky 3-value flame, hard edges, drawn directly in box space so it stays
    # crisp at 17px. Red rim first (widest), then orange body, then white core.
    poly(_FLAME_RED, red_t)
    poly(_FLAME_ORG, org_t)
    poly(_FLAME_WHT, core_t)

    # Warm yellow-white embers flung off the tail along the drooping centreline —
    # on-palette, colorblind-safe (no teal/cyan).
    for et, eb, er in ((-0.70, 0.40, 0.07), (-0.55, 0.30, 0.05),
                       (-0.85, 0.52, 0.05), (-0.45, 0.18, 0.05)):
        pygame.draw.circle(surf, _FLAME_YEL, (int(px(et)), int(py(eb))),
                           max(1, int(round(er * h))))

    # ── dark exhaust nozzle bell at the heel ─────────────────────────────────────
    # A flared bell mouth the plume erupts from; the dark mouth + steel ring make
    # the thrust source read as machinery, not a fire decal.
    poly(_PLATE_D, [
        (0.04, 0.30), (0.10, 0.27), (0.13, 0.40),
        (0.13, 0.62), (0.10, 0.74), (0.04, 0.70),
    ])
    poly(_STEEL, [
        (0.10, 0.27), (0.16, 0.31), (0.16, 0.70),
        (0.10, 0.74), (0.13, 0.62), (0.13, 0.40),
    ])
    poly(_STEEL_D, [
        (0.10, 0.62), (0.16, 0.58), (0.16, 0.70), (0.10, 0.74),
    ])
    # Hot ignition flare at the throat — a white-blue blob right where the plume
    # erupts from the bell, so the eye traces fire → nozzle → boot as one machine
    # with no gap. Drawn AFTER the bell so it sits on the lip, over the plume root.
    flare_c = (px(0.10), py(0.50))
    fr = max(1, int(round(h * 0.13)))
    pygame.draw.circle(surf, (210, 232, 255), flare_c, fr)
    pygame.draw.circle(surf, _FLAME_WHT, flare_c, max(1, int(fr * 0.6)))

    # ── chrome sole / thruster underframe ────────────────────────────────────────
    poly(_PLATE_D, [
        (0.13, 1.00), (0.92, 1.00), (0.97, 0.92),
        (0.90, 0.88), (0.16, 0.88), (0.13, 0.94),
    ])
    poly(_CHROME, [
        (0.13, 0.93), (0.16, sole_top), (0.90, sole_top),
        (0.96, 0.875), (0.96, 0.93), (0.92, 0.95), (0.16, 0.95),
    ])
    # Chrome specular streak along the sole top — the single brightest band.
    poly(_CHROME_HI, [
        (0.18, sole_top + 0.01), (0.88, sole_top + 0.01),
        (0.88, sole_top + 0.045), (0.18, sole_top + 0.05),
    ])
    poly(_STEEL_D, [
        (0.16, 0.95), (0.92, 0.95), (0.90, 0.88), (0.16, 0.91),
    ])

    # ── armoured chrome boot shell (the body) ────────────────────────────────────
    # A riveted plate body, taller at the heel where the nozzle climbs into the
    # cuff. Chrome base with a steel underside so the curve reads round/metallic.
    shell = [
        (0.16, sole_top), (0.16, 0.40), (0.22, 0.22),
        (0.40, 0.16), (0.62, 0.20), (0.78, 0.40),
        (0.90, 0.56), (0.92, sole_top),
    ]
    poly(_CHROME, shell)
    # Steel shadow along the lower/forward belly so chrome reads as a curved
    # volume catching light from above.
    poly(_STEEL, [
        (0.16, sole_top), (0.62, sole_top), (0.78, 0.46),
        (0.90, 0.58), (0.92, sole_top),
    ])
    poly(_STEEL_D, [
        (0.62, sole_top), (0.78, 0.46), (0.90, 0.58),
        (0.90, 0.66), (0.78, 0.56), (0.62, 0.70),
    ])
    # Top-edge chrome highlight along the instep ridge — the metal catch-light.
    pygame.draw.lines(
        surf, _CHROME_HI, False,
        [(px(t), py(b)) for t, b in
         ((0.22, 0.235), (0.40, 0.175), (0.62, 0.215), (0.78, 0.41))],
        max(1, int(round(h * 0.05))),
    )

    # ── armoured ankle cuff rising above the box (mecha greave) ──────────────────
    # A bevelled chrome cuff that breaks the box top; a dark ankle slot reads as
    # the opening you lock the foot into.
    poly(_CHROME, [
        (0.30, 0.24), (0.30, -0.10), (0.40, -0.20),
        (0.58, -0.18), (0.64, -0.02), (0.62, 0.22),
        (0.46, 0.16), (0.36, 0.20),
    ])
    poly(_STEEL, [
        (0.58, -0.18), (0.64, -0.02), (0.62, 0.22),
        (0.52, 0.18), (0.54, -0.04), (0.50, -0.17),
    ])
    poly(_CHROME_HI, [
        (0.30, -0.10), (0.40, -0.20), (0.47, -0.18),
        (0.38, -0.10), (0.33, 0.02),
    ])
    # Dark ankle slot sunk into the cuff top.
    hole_c = (px(0.47), py(-0.02))
    rx = max(1, int(round(w * 0.075)))
    ry = max(1, int(round(h * 0.11)))
    pygame.draw.ellipse(surf, _PLATE_D,
                        (hole_c[0] - rx, hole_c[1] - ry, rx * 2, ry * 2))

    # ── glowing heat-exhaust vents on the side plate ─────────────────────────────
    # Three angled slots venting heat — dark slot with a hot glow lip so they read
    # as live thruster vents, the second energy cue after the plume.
    vent_w = max(2, int(round(h * 0.10)))
    for vt0, vb0, vt1, vb1 in (
        (0.42, 0.40, 0.56, 0.36),
        (0.46, 0.52, 0.60, 0.48),
        (0.50, 0.64, 0.64, 0.60),
    ):
        line(_PLATE_D, (vt0, vb0 + 0.02), (vt1, vb1 + 0.02), vent_w)
        line(_VENT_GLOW, (vt0, vb0), (vt1, vb1), max(1, int(vent_w * 0.5)))

    # ── riveted plating seams + rivet dots ───────────────────────────────────────
    # A seam splitting the shell into two armour plates + rivets along it; the
    # rivets clamp to >=1px so the "bolted metal" cue survives the foot shrink.
    line(_STEEL_D, (0.30, 0.30), (0.34, sole_top), max(1, int(round(w * 0.014))))
    line(_STEEL_D, (0.66, 0.30), (0.74, 0.46), max(1, int(round(w * 0.012))))
    for rt, rb in ((0.24, 0.30), (0.40, 0.225), (0.58, 0.25),
                   (0.34, 0.62), (0.74, 0.58)):
        r = max(1, int(round(h * 0.045)))
        pygame.draw.circle(surf, _RIVET, (int(px(rt)), int(py(rb))), r)
        pygame.draw.circle(surf, _STEEL_D, (int(px(rt)), int(py(rb))),
                           r, max(1, r // 2))

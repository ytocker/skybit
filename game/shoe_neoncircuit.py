import pygame


# NEON CIRCUIT — LED light-up cyber high-top (epic). The whole read is EMISSION:
# a near-black tech upper that recedes so the lit cues are the silhouette — an
# electric-blue→magenta sole light-strip with a soft halo, circuit-trace lines
# climbing the side panel, glowing eyelets, and a light-up heel chevron. The
# glow is faked the cheap procedural way: a few expanding low-alpha strokes laid
# under each bright core line on an SRCALPHA temp, so the neon reads as light
# spilling outward rather than a flat coloured line.
#
# The hard problem is FOOT SCALE: the worn shoe is drawn at ~17x11 then upscaled
# to ~40px. At that size two failures dominate — (1) additive halos bloom past
# the thin upper onto the sky and wash to WHITE because there's no dark ground
# behind them, and (2) fine detail (traces, eyelets, collar rim) blurs to mush.
# So the builder splits on scale: when the box is tiny (worn foot) it lays a
# SOLID near-black upper mass FIRST as dark ground for the bloom, keeps only the
# bold cues (sole strip + heel chevron + one ankle collar band), and clamps halo
# radii TIGHT so the neon stays two saturated hues — cyan + magenta — not a haze.
# The full circuit-trace / eyelet detail only paints in the roomy product shot.
# Like RETRO 1 the collar rises above the box top (t < 0); callers reserve it.

_BLACK    = ( 14,  16,  24)   # near-black tech upper
_BLACK_D  = (  8,   9,  15)   # darker seams / sole body
_BLACK_HI = ( 30,  34,  48)   # cool panel sheen so it reads tech, not matte
_CYAN     = ( 25, 224, 255)   # electric-blue glow (strip front)
_MAGENTA  = (255,  60, 199)   # magenta glow (strip rear)
_VIOLET   = (122,  72, 255)   # violet mid-blend
_HOT      = (221, 246, 255)   # hot light core


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile NEON CIRCUIT high-top into box (x,y,w,h)."""
    # Worn-foot pass: the box is tiny and gets upscaled, so additive bloom would
    # white out and fine detail would vanish. Switch to the bold, dark-backed read.
    foot = w < 25 or h < 20

    def px(t):
        return x + (t * w if facing == 1 else (1.0 - t) * w)

    def py(t):
        return y + t * h

    def P(t):
        return (px(t[0]), py(t[1]))

    def poly(color, pts):
        pygame.draw.polygon(surf, color, [P(p) for p in pts])

    def line(color, a, b, width):
        pygame.draw.line(surf, color, P(a), P(b), max(1, int(round(width))))

    # A dedicated SRCALPHA layer for every emissive cue: glow halos are additive
    # low-alpha strokes that must spill past the dark upper without darkening it.
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)

    # At foot scale, cap halos HARD: a wide halo is exactly what blooms onto the
    # sky and reads white. A tight, saturated halo reads as coloured light.
    halo_cap = (h * 0.16) if foot else 1e9

    def gline(a, b, color, core_w, halo_w, layers=4):
        """Emissive line — widening low-alpha halo passes under a hot core."""
        halo_w = min(halo_w, halo_cap)
        pa, pb = P(a), P(b)
        for i in range(layers, 0, -1):
            f = i / layers
            wpx = max(1, int(round(core_w + (halo_w - core_w) * f)))
            # Worn foot keeps more energy in the saturated colour, less in the
            # outer haze, so the hue survives instead of averaging toward white.
            base = 64 if foot else 46
            alpha = int(base * (1.0 - f) + 18)
            pygame.draw.line(glow, (*color, alpha), pa, pb, wpx)
        # Core: pure-ish hue on the foot (so cyan stays cyan, magenta stays
        # magenta); only the product shot bleaches the core toward white.
        core_col = color if foot else _lerp(color, _HOT, 0.5)
        pygame.draw.line(glow, (*core_col, 245), pa, pb,
                         max(1, int(round(core_w))))

    def gdot(t, color, core_r, halo_r):
        halo_r = min(halo_r, halo_cap)
        cx, cy = P(t)
        for i in range(4, 0, -1):
            f = i / 4
            r = max(1, int(round(core_r + (halo_r - core_r) * f)))
            alpha = int(50 * (1.0 - f) + 22)
            pygame.draw.circle(glow, (*color, alpha), (cx, cy), r)
        core_col = color if foot else _lerp(color, _HOT, 0.6)
        pygame.draw.circle(glow, (*core_col, 245),
                           (cx, cy), max(1, int(round(core_r))))

    sole_top = 0.82

    # ── solid near-black backing mass (the dark GROUND for the bloom) ───────────
    # CRUCIAL: this is laid FIRST and OPAQUE so every additive halo above blooms
    # against black, not sky. On the worn foot a single bold mass (toe → instep →
    # tall ankle counter) is enough and reads as the silhouette; the product shot
    # gets the same mass plus moulded facets below.
    poly(_BLACK_D, [
        (0.03, 1.00), (0.95, 1.00), (0.98, 0.93),
        (0.91, 0.905), (0.06, 0.905), (0.03, 0.95),
    ])
    poly(_BLACK, [
        (0.05, 0.94), (0.07, sole_top), (0.92, sole_top),
        (0.96, 0.905), (0.95, 0.95), (0.92, 0.965), (0.07, 0.965),
    ])

    # One continuous dark upper, INCLUDING the tall ankle rise, as a single
    # opaque mass — the high-top column the ankle band will glow against.
    upper = [
        (0.07, sole_top), (0.07, 0.40), (0.13, 0.30), (0.24, 0.30),
        (0.34, 0.26), (0.62, 0.30), (0.80, 0.40), (0.90, 0.56),
        (0.93, 0.70), (0.93, sole_top),
    ]
    poly(_BLACK, upper)
    # The tall cyber cuff, drawn as ONE opaque black column rising above the box
    # top — this gives the worn foot a clear vertical high-top mass and dark
    # ground for the ankle glow band.
    collar = [
        (0.115, 0.46), (0.115, 0.04), (0.16, -0.14), (0.28, -0.18),
        (0.42, -0.11), (0.47, 0.10), (0.44, 0.34), (0.30, 0.42),
        (0.18, 0.44),
    ]
    poly(_BLACK, collar)

    if not foot:
        # Product shot only: moulded facets, sheen, heel block — sub-threshold
        # detail that just muddies the upscaled foot, so it stays out of it.
        poly(_BLACK_HI, [
            (0.34, 0.30), (0.50, 0.31), (0.56, 0.46), (0.40, 0.44),
        ])
        poly(_BLACK_D, [
            (0.07, sole_top), (0.07, 0.40), (0.20, 0.34), (0.20, sole_top),
        ])
        poly(_BLACK_HI, [
            (0.115, 0.04), (0.16, -0.14), (0.28, -0.18), (0.25, -0.11),
            (0.18, -0.05), (0.14, 0.04),
        ])

    # ── lit ankle collar band — the high-top read (survives at 40px) ────────────
    # A fat, bright neon band wrapping the cuff opening: it gives the shoe a clear
    # vertical rise so it reads HIGH-TOP, and confirms epic tier over a low-top.
    # Cyan→violet→magenta along the rim so both hero hues live in the ankle.
    if foot:
        band_w = max(2, w * 0.16)
        band_halo = w * 0.20
    else:
        band_w = max(2, w * 0.05)
        band_halo = w * 0.085
    gline((0.155, -0.02), (0.30, -0.05), _CYAN, band_w, band_halo, layers=4)
    gline((0.30, -0.05), (0.43, 0.04), _MAGENTA, band_w, band_halo, layers=4)
    if not foot:
        # The thin open-top rim line — fine detail, product shot only.
        gline((0.13, 0.06), (0.155, -0.10), _CYAN, w * 0.012, w * 0.04, layers=3)

    # ── circuit-trace lines + eyelets — PRODUCT SHOT ONLY ───────────────────────
    # These blur to mush at 40px and their wide halos are what wash the foot, so
    # they are gated entirely out of the worn pass.
    if not foot:
        trace_w = max(1, w * 0.013)
        halo = w * 0.045
        gline((0.40, 0.66), (0.40, 0.50), _CYAN, trace_w, halo, layers=3)
        gline((0.40, 0.50), (0.54, 0.50), _CYAN, trace_w, halo, layers=3)
        gline((0.54, 0.50), (0.54, 0.40), _CYAN, trace_w, halo, layers=3)
        gline((0.60, 0.64), (0.72, 0.64), _VIOLET, trace_w, halo, layers=3)
        gline((0.72, 0.64), (0.72, 0.54), _VIOLET, trace_w, halo, layers=3)
        gdot((0.54, 0.40), _CYAN, max(1, w * 0.012), w * 0.030)
        gdot((0.40, 0.66), _CYAN, max(1, w * 0.011), w * 0.026)
        gdot((0.72, 0.54), _VIOLET, max(1, w * 0.012), w * 0.030)

        eyelets = [(0.32, 0.46), (0.38, 0.40), (0.45, 0.35), (0.52, 0.31)]
        for i, e in enumerate(eyelets):
            c = _lerp(_CYAN, _MAGENTA, i / (len(eyelets) - 1))
            gdot(e, c, max(1, w * 0.013), w * 0.034)
        lace_w = max(1, h * 0.030)
        for i in range(len(eyelets) - 1):
            a, b = eyelets[i], eyelets[i + 1]
            line((150, 170, 200), (a[0], a[1] + 0.04), (b[0], b[1] + 0.04), lace_w)

    # ── light-up heel chevron (a bold rear cue that holds at 40px) ──────────────
    # A fat "<" on the heel counter. On the foot it's chunkier with a tighter halo.
    if foot:
        cw = max(2, w * 0.10)
        chal = w * 0.16
    else:
        cw = max(1, w * 0.018)
        chal = w * 0.055
    gline((0.15, 0.44), (0.10, 0.57), _MAGENTA, cw, chal, layers=4)
    gline((0.10, 0.57), (0.15, 0.70), _MAGENTA, cw, chal, layers=4)

    # ── electric-blue→magenta LED sole strip with halo (the dominant glow) ──────
    # A continuous lit channel along the whole midsole, colour-shifting blue→
    # magenta front-to-back, blooming against the dark outsole below it.
    sy0, sy1 = 0.80, 0.815
    x0, x1 = 0.085, 0.915
    segs = 16
    if foot:
        sole_w = max(2, h * 0.16)
        sole_halo = h * 0.16   # clamped so it stays coloured, not a white haze
        layers = 4
    else:
        sole_w = max(1, h * 0.075)
        sole_halo = h * 0.34
        layers = 5
    for s in range(segs):
        t0 = s / segs
        t1 = (s + 1) / segs
        ax = x0 + (x1 - x0) * t0
        bx = x0 + (x1 - x0) * t1
        ay = sy0 + (sy1 - sy0) * t0
        by = sy0 + (sy1 - sy0) * t1
        # blue at the toe (right) shifting to magenta at the heel (left)
        col = _lerp(_MAGENTA, _CYAN, t0)
        gline((ax, ay), (bx, by), col, sole_w, sole_halo, layers=layers)

    # Composite all emission over the dark shoe — additive blend so halos
    # brighten against the black backing mass without muddying the upper.
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

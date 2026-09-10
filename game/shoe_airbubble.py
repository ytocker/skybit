import pygame


# Volt-on-grey reads instantly as the "tech air runner" without any logo;
# the see-through heel window is the one cue that must survive down to 16px,
# so it is drawn as a single lighter rounded shape rather than fine detail.
_GREY_UP = (176, 180, 188)      # mesh upper
_GREY_UP_D = (138, 143, 152)    # upper shadow / panel seams
_GREY_TOE = (158, 163, 172)     # toe cap, slightly distinct from mesh
_MID = (236, 238, 242)          # bright stacked midsole foam
_MID_D = (198, 202, 210)        # midsole shadow band
_OUTSOLE = (74, 78, 86)         # dark rubber outsole
_VOLT = (196, 255, 36)          # neon accent swoop + pull-tab
_VOLT_D = (150, 206, 22)        # volt shade
_BUBBLE = (70, 120, 140)        # dark glassy teal cavity (a see-through hole)
_BUBBLE_CORE = (120, 178, 198)  # lighter glass core toward the centre
_BUBBLE_HI = (214, 244, 255)    # bubble specular crescent
_BUBBLE_SHAD = (40, 70, 84)     # dark cavity shadow under the foam overhang


def _lerp_pts(pts, x, y, w, h):
    # Variant authoring is in 0..1 box space; map to pixels once here.
    return [(x + px * w, y + py * h) for px, py in pts]


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile AIR BUBBLE sneaker into box (x,y,w,h)."""
    x, y, w, h = float(x), float(y), float(w), float(h)

    # Render the whole shoe facing right on a scratch surface, then flip once
    # for facing=-1 so every shape below can assume a single orientation.
    work = pygame.Surface((max(1, int(round(w))), max(1, int(round(h)))), pygame.SRCALPHA)
    bw, bh = work.get_width(), work.get_height()

    def poly(color, pts, width=0):
        pygame.draw.polygon(work, color, _lerp_pts(pts, 0, 0, bw, bh), width)

    def ellipse(color, rx0, ry0, rx1, ry1):
        r = pygame.Rect(rx0 * bw, ry0 * bh, (rx1 - rx0) * bw, (ry1 - ry0) * bh)
        if r.width >= 1 and r.height >= 1:
            pygame.draw.ellipse(work, color, r)

    # --- Stacked chunky midsole (the bulk of the silhouette) -------------
    # Slight toe-spring kicks the front up; heel sits a touch taller.
    midsole = [
        (0.04, 0.78), (0.02, 0.90), (0.10, 0.965),
        (0.86, 0.965), (0.97, 0.90), (0.985, 0.80),
        (0.93, 0.72), (0.55, 0.70), (0.18, 0.71),
    ]
    poly(_MID, midsole)

    # Shadow band along the lower midsole to give the foam thickness.
    poly(_MID_D, [
        (0.03, 0.875), (0.10, 0.945), (0.86, 0.945),
        (0.965, 0.885), (0.94, 0.845), (0.10, 0.86),
    ])

    # --- Dark outsole on the ground line --------------------------------
    poly(_OUTSOLE, [
        (0.05, 0.915), (0.11, 0.985), (0.85, 0.985),
        (0.955, 0.92), (0.93, 0.905), (0.10, 0.905),
    ])

    # --- Encapsulated AIR WINDOW punched into the heel foam (hero cue) ---
    # A see-through cavity, not a sticker: a dark glassy teal fill (darker
    # than the foam) with a lighter core, a shadow under the foam overhang,
    # foam-coloured pillars seen through it, and a dark outsole rim wrapping
    # the bottom/outer edge so the foam clearly contains the window.
    br = pygame.Rect(0.085 * bw, 0.725 * bh, 0.34 * bw, 0.18 * bh)
    if br.width >= 2 and br.height >= 2:
        # Glassy cavity body: dark teal so it reads as a hole, lighter core.
        pygame.draw.ellipse(work, _BUBBLE, br)
        cr = br.inflate(-br.width * 0.30, -br.height * 0.34)
        pygame.draw.ellipse(work, _BUBBLE_CORE, cr)

        # Foam overhang shadow hugging the top inner edge sells "punched in".
        sr = pygame.Rect(br.x, br.y, br.width, max(2, int(br.height * 0.26)))
        clip = work.get_clip()
        work.set_clip(sr)
        pygame.draw.ellipse(work, _BUBBLE_SHAD, br.inflate(-1, 0))
        work.set_clip(clip)

        # Vertical foam pillars seen through the air unit (encapsulated air).
        for fx in (0.40, 0.62):
            sx = br.x + br.width * fx
            top = br.y + br.height * 0.16
            bot = br.y + br.height * 0.84
            pygame.draw.line(work, _MID_D, (sx, top), (sx, bot),
                             max(1, int(br.width * 0.045)))

        # Outsole-coloured rim wrapping the bottom/outer arc contains it.
        rim_w = max(1, int(br.height * 0.16))
        pygame.draw.arc(work, _OUTSOLE, br, 3.55, 6.0, rim_w)

        # Small specular crescent only in the upper core for the glass cue.
        hr = pygame.Rect(0, 0, int(br.width * 0.30), int(br.height * 0.22))
        hr.center = (int(br.centerx - br.width * 0.12),
                     int(br.y + br.height * 0.30))
        if hr.width >= 2 and hr.height >= 2:
            pygame.draw.ellipse(work, _BUBBLE_HI, hr)

    # --- Upper: grey mesh body ------------------------------------------
    upper = [
        (0.10, 0.72), (0.12, 0.40), (0.20, 0.24),
        (0.40, 0.16), (0.58, 0.16), (0.66, 0.22),
        (0.70, 0.40), (0.86, 0.52), (0.95, 0.66),
        (0.93, 0.72), (0.55, 0.70), (0.18, 0.71),
    ]
    poly(_GREY_UP, upper)

    # Heel counter shadow for depth at the back.
    poly(_GREY_UP_D, [
        (0.10, 0.72), (0.115, 0.46), (0.20, 0.30),
        (0.27, 0.34), (0.22, 0.52), (0.21, 0.70),
    ])

    # Toe cap, a hair darker than the mesh.
    poly(_GREY_TOE, [
        (0.70, 0.40), (0.86, 0.52), (0.95, 0.66),
        (0.93, 0.715), (0.74, 0.70), (0.70, 0.55),
    ])

    # --- Volt accent: forward-swept speed-slashes -----------------------
    # Two parallel volt darts raked toward the toe. Deliberately a twin
    # chevron-stripe motif (not a single hooked swoosh) so it reads as a
    # generic sporty speed graphic rather than any trademarked check.
    # Each slash is a thin parallelogram with a kicked-up trailing notch.
    poly(_VOLT, [
        (0.34, 0.62), (0.68, 0.42), (0.72, 0.485),
        (0.40, 0.685),
    ])
    poly(_VOLT_D, [
        (0.34, 0.62), (0.40, 0.685), (0.355, 0.675),
        (0.305, 0.635),
    ])
    poly(_VOLT, [
        (0.30, 0.685), (0.56, 0.535), (0.595, 0.595),
        (0.345, 0.735),
    ])
    poly(_VOLT_D, [
        (0.30, 0.685), (0.345, 0.735), (0.305, 0.725),
        (0.275, 0.695),
    ])

    # --- Volt heel pull-tab ---------------------------------------------
    poly(_VOLT, [
        (0.10, 0.32), (0.20, 0.22), (0.255, 0.27),
        (0.155, 0.38),
    ])
    poly(_VOLT_D, [
        (0.155, 0.38), (0.255, 0.27), (0.255, 0.315),
        (0.165, 0.41),
    ])

    # Collar / ankle opening shadow.
    poly(_GREY_UP_D, [
        (0.30, 0.20), (0.58, 0.19), (0.62, 0.25),
        (0.40, 0.255),
    ])

    if facing < 0:
        work = pygame.transform.flip(work, True, False)

    surf.blit(work, (int(round(x)), int(round(y))))

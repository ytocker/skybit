"""CRYSTAL DECANTER — cut-crystal spirits decanter parcel cosmetic.

The IDENTITY is the heavy faceted-crystal read: a SQUAT, WIDE-SHOULDERED
decanter body (much wider than it is tall, unlike the slim bottle parcels),
filled with AMBER whiskey behind a bright meniscus, and capped by a fat round
KNOB stopper on a short pinched neck. The amber liquid + the squat faceted glass
mass + the knob stopper are the three beats that make it read as fine whiskey,
not a water bottle.

22px read tradeoffs (WHY): "cut crystal" is sold with ONE committed hard
vertical glass sheen down the left edge plus the bright meniscus — a fussy facet
grid only aliases to mud at the downscale, the heavy silhouette + the bold amber
mass do the work and the single vertical glint says "polished heavy glass". The
body is filled almost entirely with rich amber (the whiskey is the loudest cue)
with only a thin clear-glass band above the bright meniscus, so the warm slug
survives rotation and grayscale. The premium read is a WARM/COOL split: a true
GOLD knob (warm metal value ramp + a hot specular dot, no cool glass tint) and a
1px gold collar at the shoulder against the COOL crystal body — that gold trim is
what separates a fine-spirits decanter from a generic glass potion. The knob is
kept FAT and round on a short pinched neck so it stays a distinct top beat — a
slim cap would fuse into the wide shoulder when banked. Drawn on a 44px work surface then smoothscaled to 22 so the facet sheen
and stopper curve antialias cleanly. A baked dark OUTLINE (inflated, drawn first)
carries the shape on bright DAY sky; a cool KEYLINE rim inside is the NIGHT
lifeline; the decanter is held well off the surface edges so the gameplay
rotozoom never clips the knob stopper or the wide base.
"""
import pygame

# Tight palette: a COOL cut-crystal glass body vs. a WARM-GOLD knob stopper +
# a rich AMBER whiskey slug — the warm/cool split is what separates a fine-
# spirits decanter from a generic glass potion. The gold knob and the amber slug
# must stay distinct mid/upper-mid values against the cool glass in grayscale.
GLASS = (207, 224, 230)       # cool cut-crystal glass (clear band)
GLASS_HI = (244, 250, 252)    # the single committed vertical glass sheen
AMBER = (200, 121, 30)        # amber whiskey body fill — deeper/richer
AMBER_LO = (154, 86, 14)      # deep amber at the base (volume)
AMBER_HI = (236, 168, 78)     # warm amber under the meniscus (still rich, not pale)
MENISCUS = (252, 230, 178)    # bright liquid-surface line — loudest interior beat
# Gold stopper value ramp: a true warm metal gradient, never a cool glass tint.
GOLD_HI = (248, 224, 138)     # bright gold top-left
GOLD = (216, 168, 62)         # gold mid
GOLD_LO = (150, 110, 30)      # deep gold-shadow lower-right (#966E1E-ish)
GOLD_SPEC = (255, 250, 224)   # hot 1px specular dot
COLLAR = (224, 178, 74)       # gold collar band at the shoulder — "fine spirits"
OUTLINE = (42, 36, 24)        # dark, warm: reads on bright day sky
KEYLINE = (214, 230, 236)     # cool rim — the NIGHT lifeline on the BODY


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static decanter sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a SQUAT wide-shouldered body, a short pinched neck, and a fat
    # round knob stopper. Held off the surface edges so the rotozoom never clips.
    BW = 28                       # wide body (the heavy-crystal mass)
    body_top = 20                 # shoulder line (sits low so the body is squat)
    body_bot = 38                 # wide flat base
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 4

    # Shoulder: the body widens out HARD from a narrow neck — a tall, steep
    # trapezoid cap so the wide-shouldered decanter silhouette is unmistakable
    # (the steep flare is the decanter tell vs. a straight-walled bottle).
    sh_top = 13                   # where the shoulder meets the neck step
    sh_lx = cx - 5                # narrow top of the shoulder (neck width-ish)
    sh_rx = cx + 5

    # Neck: a SHORT pinched step bridging the shoulder to the knob.
    NW = 8
    neck_rect = pygame.Rect(cx - NW // 2, 9, NW, 5)

    # Knob stopper: a FAT round faceted knob — the premium top beat.
    knob_r = 6
    knob_cy = 7

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.circle(surf, OUTLINE, (cx, knob_cy), knob_r + 2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3))
    # Shoulder trapezoid outline (inflated by drawing a slightly larger polygon).
    pygame.draw.polygon(surf, OUTLINE, [
        (sh_lx - 2, sh_top - 1),
        (sh_rx + 2, sh_top - 1),
        (body_rect.right + 2, body_top + 3),
        (body_rect.x - 2, body_top + 3),
    ])
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4), border_radius=body_rad + 2)

    # --- Shoulder fill: the angled crystal shoulder cut between neck and body.
    pygame.draw.polygon(surf, GLASS, [
        (sh_lx, sh_top),
        (sh_rx, sh_top),
        (body_rect.right, body_top + 2),
        (body_rect.x, body_top + 2),
    ])

    # --- BODY built on its own alpha surface: a thin clear-glass band on top,
    # then the amber whiskey fill below the meniscus, masked to the squat shape.
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Meniscus sits high so the body is almost all amber — the whiskey is the
    # loudest cue and a fat warm mass survives the downscale + rotation.
    fill_top = int(bh * 0.22)

    # Clear crystal band above the liquid surface.
    body.fill(GLASS + (245,), pygame.Rect(0, 0, bw, fill_top))
    # Amber whiskey: a vertical deepening from the bright top to a richer base.
    for y in range(fill_top, bh):
        t = (y - fill_top) / max(1, bh - 1 - fill_top)
        if t < 0.35:
            tt = t / 0.35
            c = (
                int(AMBER_HI[0] + (AMBER[0] - AMBER_HI[0]) * tt),
                int(AMBER_HI[1] + (AMBER[1] - AMBER_HI[1]) * tt),
                int(AMBER_HI[2] + (AMBER[2] - AMBER_HI[2]) * tt),
            )
        else:
            tt = (t - 0.35) / 0.65
            c = (
                int(AMBER[0] + (AMBER_LO[0] - AMBER[0]) * tt),
                int(AMBER[1] + (AMBER_LO[1] - AMBER[1]) * tt),
                int(AMBER[2] + (AMBER_LO[2] - AMBER[2]) * tt),
            )
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))

    # Bright meniscus line at the liquid surface — the loud "this is liquid" cue.
    pygame.draw.line(body, MENISCUS, (1, fill_top), (bw - 2, fill_top), 2)

    # Mask to a squat shape: base corners round, top stays square under shoulder.
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=1,
                     border_top_right_radius=1)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- CRYSTAL sheen: ONE committed hard VERTICAL glass highlight streak down
    # the left edge of the body. A single bright cool glint reads as polished
    # heavy glass; a fussy facet grid only aliases to mud at the downscale. The
    # vertical glint + the bright meniscus are the whole "cut crystal" read.
    pygame.draw.line(surf, GLASS_HI,
                     (body_rect.x + 3, body_rect.y + 2),
                     (body_rect.x + 3, body_rect.bottom - 4), 2)

    # --- NECK fill (between the shoulder and the knob).
    pygame.draw.rect(surf, GLASS, neck_rect)

    # --- GOLD collar: a 1px gold band on the FRONT edge where the pinched neck
    # meets the shoulder. The gold trim is the "fine spirits" tell that pushes the
    # decanter past a plain glass potion bottle.
    pygame.draw.line(surf, COLLAR,
                     (sh_lx, sh_top + 1), (sh_rx, sh_top + 1), 1)

    # --- KNOB stopper: a fat round GOLD knob. The premium tell is a warm metal
    # value ramp (bright gold top-left → gold mid → deep gold-shadow lower-right)
    # against the cool glass body — NO cool keyline/glass highlight here, or it
    # reads as another glass blob. Built by stacking offset gold discs from dark
    # base to bright top-left, capped by one hot specular dot.
    pygame.draw.circle(surf, GOLD_LO, (cx, knob_cy), knob_r)
    pygame.draw.circle(surf, GOLD, (cx - 1, knob_cy - 1), knob_r - 1)
    pygame.draw.circle(surf, GOLD_HI, (cx - 2, knob_cy - 2), knob_r - 3)
    # One hot specular dot — the metal glint.
    pygame.draw.circle(surf, GOLD_SPEC, (cx - 2, knob_cy - 2), 1)
    # Hard groove where the knob seats on the neck.
    pygame.draw.line(surf, OUTLINE,
                     (neck_rect.x, neck_rect.y),
                     (neck_rect.right - 1, neck_rect.y), 2)

    # --- Cool keyline rim INSIDE the outline on the BODY only — the NIGHT
    # lifeline. The knob is deliberately LEFT OUT: a cool rim there would fight
    # the warm-gold read; the gold value ramp + dark outline carry the knob on
    # dark sky. Traces the body wall + the shoulder so the glass mass glows.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=1, border_top_right_radius=1)
    pygame.draw.line(surf, KEYLINE, (sh_lx, sh_top), (body_rect.x + 1, body_top + 1), 1)
    pygame.draw.line(surf, KEYLINE, (sh_rx, sh_top), (body_rect.right - 1, body_top + 1), 1)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))

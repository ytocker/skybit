"""PLASTIC BOTTLE — single-use supermarket PET water bottle parcel cosmetic.

The IDENTITY is the throwaway PET bottle read. Three beats carry it: a small
BLUE screw CAP, a white/blue paper LABEL band wrapping the MIDDLE of the body
(the brand read), and a RIBBED lower body (the moulded PET base flutes). The
body is clear-blue tinted with blue water, so the vessel reads as drink even
before the label.

22px read tradeoffs (WHY): at true size the label band is the single loudest
disposable-bottle cue, so it is a FAT full-width white MASS spanning ~0.30–0.66
of the body — fenced top AND bottom with the dark OUTLINE colour so it stays one
hard, discrete white block after the smoothscale instead of bleeding into the
clear PET or water. The band is kept PURE white (no blue stripe — that stripe was
the same blue as the water and split the thin white into slivers); the white mass
IS the brand read, so it is protected. The cap is kept SMALL and narrow (a screw
cap, not a sport lid) to read "cheap single-use", but its blue is DEEPENED and it
is taller with a hard cap/neck groove so it survives as a distinct top beat on
the night/grayscale
rows. PET ribbing is a SINGLE dark OUTLINE-value flute low in the rounded base —
two faint lines read as mud, one committed flute reads as "ribbed". Drawn on a
44px work surface then smoothscaled to 22 so the label edges antialias cleanly. A
baked dark OUTLINE (inflated, drawn first) carries the shape on bright DAY sky; a
cool KEYLINE rim inside is the NIGHT lifeline; the bottle is held off the surface
edges so the gameplay rotozoom never clips the cap or base.
"""
import pygame

# Tight palette from the concept: clear-blue tinted PET, blue water, a small blue
# screw cap, a white label band (the brand read + grayscale anchor), a dark
# outline for day and a cool keyline for night.
BODY = (191, 227, 242)         # clear blue-tinted PET (upper body / shoulder)
WATER = ( 62, 154, 214)        # blue water in the body
WATER_HI = (150, 205, 240)     # meniscus / glint highlight
CAP = ( 33,  86, 168)          # small blue screw cap — deepened so it stays a beat
CAP_HI = (130, 172, 230)       # cap top edge highlight
LABEL = (245, 247, 250)        # white paper label band (the brand mass)
LABEL_ACCENT = (150, 178, 205) # faint 1px blue-grey print accent (kept subtle)
OUTLINE = ( 30,  53,  80)      # dark, high-value: reads on bright day sky
KEYLINE = (210, 232, 246)      # cool rim — the NIGHT lifeline
RIB = ( 70, 130, 175)          # dark PET base flutes (ribbing)


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static bottle sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a tall slim PET body with a tucked shoulder and a SMALL cap.
    # Held off the surface edges so the gameplay rotozoom never clips it.
    BW = 16
    body_top = 15
    body_bot = 39
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 4                  # PET base rounds in for the moulded-base read

    # Neck: a short narrow step bridging the shoulder to the small cap.
    NW = 6
    neck_rect = pygame.Rect(cx - NW // 2, 10, NW, 6)

    # Cap: a SMALL narrow blue screw cap — the cheap single-use read. Taller so
    # the screw cap stays a distinct top beat on the night/grayscale rows.
    CW, CH = 9, 8
    cap_rect = pygame.Rect(cx - CW // 2, 3, CW, CH)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3))
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4), border_radius=body_rad + 2)

    # --- Shoulder tuck: darker diagonals from the body wall corners up into the
    # neck so the cap/neck and body never fuse into one mass at the downscale.
    sh_y = neck_rect.bottom
    sh_dark = (46, 92, 140)
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.x, body_top + 3),
        (neck_rect.x, sh_y - 1),
        (neck_rect.x, sh_y + 1),
        (body_rect.x, body_top + 5),
    ])
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.right, body_top + 3),
        (neck_rect.right, sh_y - 1),
        (neck_rect.right, sh_y + 1),
        (body_rect.right, body_top + 5),
    ])
    # Fill the shoulder interior so the body wall meets the neck cleanly.
    pygame.draw.polygon(surf, BODY, [
        (body_rect.x + 1, body_top + 4),
        (neck_rect.x, sh_y),
        (neck_rect.right, sh_y),
        (body_rect.right - 1, body_top + 4),
    ])

    # --- BODY built on its own alpha surface: a clear-blue top, the white LABEL
    # band across the middle, then blue water + ribbing below, masked to the
    # straight-walled PET shape and composited in one piece.
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Label band geometry: a FAT full-width white mass across the MIDDLE of the
    # body. Spanning ~0.30–0.66 of body height so the white core survives the
    # downscale + rotation as a fat band, not a 1px line — the loudest cue.
    label_top = int(bh * 0.30)
    label_bot = int(bh * 0.66)

    # Clear-blue tinted PET above the label (the see-through upper body).
    body.fill(BODY + (245,), pygame.Rect(0, 0, bw, label_top))
    # Water below the label: a gentle vertical deepening so it reads as volume.
    for y in range(label_bot, bh):
        t = (y - label_bot) / max(1, bh - 1 - label_bot)
        c = (
            int(WATER_HI[0] + (WATER[0] - WATER_HI[0]) * t),
            int(WATER_HI[1] + (WATER[1] - WATER_HI[1]) * t),
            int(WATER_HI[2] + (WATER[2] - WATER_HI[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))

    # White LABEL band — the loudest disposable cue: a PURE white mass wrapping
    # the body. FENCED top + bottom with the dark OUTLINE colour (not the soft
    # blue rib) so it stays one hard, discrete white block after the smoothscale.
    # No blue stripe — it was the water's blue and split the white into slivers;
    # the white mass IS the brand read, so it is protected. At most a single 1px
    # blue-grey print accent low in the band.
    body.fill(LABEL + (255,), pygame.Rect(0, label_top, bw, label_bot - label_top))
    pygame.draw.line(body, OUTLINE, (0, label_top), (bw, label_top), 1)
    pygame.draw.line(body, OUTLINE, (0, label_bot - 1), (bw, label_bot - 1), 1)
    accent_y = label_bot - 4
    pygame.draw.line(body, LABEL_ACCENT, (2, accent_y), (bw - 3, accent_y), 1)

    # PET base ribbing: ONE committed dark flute (OUTLINE value) low in the
    # rounded base so it reads "ribbed" without two faint lines aliasing to mud.
    pygame.draw.line(body, OUTLINE, (3, bh - 5), (bw - 4, bh - 5), 1)

    # Mask to a STRAIGHT-WALLED shape: only the bottom corners round.
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=0,
                     border_top_right_radius=0)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- Meniscus glint just under the label so the upper body reads as water.
    my = body_rect.y + label_bot
    pygame.draw.line(surf, WATER_HI,
                     (body_rect.x + 2, my + 1), (body_rect.right - 3, my + 1), 1)
    # Vertical glint streak on the water (plastic translucency cue).
    pygame.draw.line(surf, WATER_HI,
                     (body_rect.x + 3, my + 3),
                     (body_rect.x + 3, body_rect.bottom - 6), 2)

    # --- NECK fill (between the shoulder tuck and the small cap).
    pygame.draw.rect(surf, BODY, neck_rect)

    # --- CAP: small blue screw cap with a flat top highlight + a hard groove at
    # the cap/neck join (OUTLINE colour) so it reads as a screw-on lid.
    pygame.draw.rect(surf, CAP, cap_rect, border_radius=2)
    pygame.draw.line(surf, CAP_HI,
                     (cap_rect.x + 1, cap_rect.y + 1),
                     (cap_rect.right - 2, cap_rect.y + 1), 1)
    pygame.draw.line(surf, OUTLINE,
                     (cap_rect.x, cap_rect.bottom - 1),
                     (cap_rect.right - 1, cap_rect.bottom - 1), 2)

    # --- Cool keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the straight body wall + cap.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=0, border_top_right_radius=0)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=2)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))

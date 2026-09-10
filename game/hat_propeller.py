import math

import pygame

# Cheerful primary colorway — the classic kid's beanie reads instantly via
# alternating panels, so we lean on saturated red/yellow/blue plus a green
# accent rather than any logo.
_RED = (228, 58, 58)
_YELLOW = (248, 206, 60)
_BLUE = (66, 132, 224)
_GREEN = (88, 188, 104)
_PANEL_SEAM = (40, 40, 60)
_CAP_RIM = (236, 236, 244)
_BUTTON = (238, 238, 246)
_STALK = (150, 150, 162)
_STALK_HI = (208, 208, 218)
_PROP = (236, 80, 70)
_PROP_HI = (255, 168, 150)
_HUB = (60, 60, 78)


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile PROPELLER CAP sized for a head of width head_w, centered at cx, base line at base_y."""
    r = head_w * 0.5
    # The cap hugs the upper hemisphere of a round head: its base sits a touch
    # below the crown-top so the underside curve appears to wrap the skull.
    cap_base_y = base_y + r * 0.34
    cap_h = r * 0.80
    cap_top_y = cap_base_y - cap_h
    cap_half = r * 1.04  # slightly wider than the head so the rim overhangs

    left = cx - cap_half
    right = cx + cap_half

    # Dome built as a polygon arc so the silhouette stays smooth at any size.
    dome = []
    steps = 18
    for i in range(steps + 1):
        t = i / steps
        ang = math.pi - t * math.pi  # pi (left) -> 0 (right)
        x = cx + math.cos(ang) * cap_half
        y = cap_base_y - math.sin(ang) * cap_h
        dome.append((x, y))

    # Filled base cap (single tone first, then panels overlay) keeps edges clean.
    base_poly = dome + [(right, cap_base_y), (left, cap_base_y)]
    pygame.draw.polygon(surf, _BLUE, base_poly)

    # Color-segment panels: gate the seams off when too small to resolve them,
    # but always keep the cap + propeller silhouette intact.
    show_panels = head_w >= 22
    if show_panels:
        # Five vertical wedges in primary colors, drawn as pie-ish slices from
        # the apex down to the rim so they read as stitched panels in profile.
        panel_cols = [_RED, _YELLOW, _BLUE, _RED, _YELLOW]
        # Re-color by sampling the dome arc into wedge bands.
        n = len(panel_cols)
        for p in range(n):
            a0 = p / n
            a1 = (p + 1) / n
            wedge = [(cx, cap_top_y - cap_h * 0.02)]
            sub = 6
            for j in range(sub + 1):
                t = a0 + (a1 - a0) * (j / sub)
                ang = math.pi - t * math.pi
                x = cx + math.cos(ang) * cap_half
                y = cap_base_y - math.sin(ang) * cap_h
                wedge.append((x, y))
            pygame.draw.polygon(surf, panel_cols[p], wedge)
            # Thin seam between panels for the stitched look.
            seam_w = max(1, int(head_w * 0.02))
            pygame.draw.line(surf, _PANEL_SEAM, (cx, cap_top_y),
                             (wedge[1][0], wedge[1][1]), seam_w)

    # Bright rim band along the cap base gives the beanie its finished edge;
    # rounded ends + a curved underside read as wrapping the round head.
    rim_h = max(2, r * 0.18)
    band = pygame.Rect(int(left), int(cap_base_y - rim_h),
                       int(cap_half * 2), int(rim_h * 2))
    pygame.draw.ellipse(surf, _CAP_RIM, band)
    # Flat-top the band so it meets the panels cleanly instead of bulging up.
    pygame.draw.rect(surf, _CAP_RIM,
                     pygame.Rect(int(left), int(cap_base_y - rim_h),
                                 int(cap_half * 2), int(rim_h)))

    # Apex button where the panels meet.
    btn_r = max(1, r * 0.10)
    btn_y = cap_top_y + btn_r * 0.4
    pygame.draw.circle(surf, _BUTTON, (int(cx), int(btn_y)), int(btn_r))
    pygame.draw.circle(surf, _PANEL_SEAM, (int(cx), int(btn_y)), int(btn_r), 1)

    # Short stalk lifting the propeller off the button.
    stalk_h = max(2, r * 0.22)
    stalk_w = max(1, r * 0.07)
    stalk_top = btn_y - stalk_h
    pygame.draw.line(surf, _STALK, (cx, btn_y), (cx, stalk_top),
                     int(stalk_w * 2) if stalk_w * 2 >= 1 else 1)
    if head_w >= 22:
        pygame.draw.line(surf, _STALK_HI, (cx - stalk_w * 0.4, btn_y),
                         (cx - stalk_w * 0.4, stalk_top), 1)

    # Two-blade propeller as a flat horizontal lens/ellipse so it reads as a
    # spinner from the side; facing mirrors the slight pitch of the blades.
    prop_half = r * 0.66
    prop_h = max(2, r * 0.16)
    prop_cx = cx
    prop_cy = stalk_top
    # Blades: two stretched ellipses kissing at the hub, tilted opposite ways.
    pitch = r * 0.10 * facing
    left_blade = [
        (prop_cx, prop_cy),
        (prop_cx - prop_half * 0.5, prop_cy - prop_h - pitch * 0.4),
        (prop_cx - prop_half, prop_cy - pitch),
        (prop_cx - prop_half * 0.5, prop_cy + prop_h - pitch * 0.4),
    ]
    right_blade = [
        (prop_cx, prop_cy),
        (prop_cx + prop_half * 0.5, prop_cy - prop_h + pitch * 0.4),
        (prop_cx + prop_half, prop_cy + pitch),
        (prop_cx + prop_half * 0.5, prop_cy + prop_h + pitch * 0.4),
    ]
    pygame.draw.polygon(surf, _PROP, left_blade)
    pygame.draw.polygon(surf, _GREEN, right_blade)
    if head_w >= 22:
        # Tiny highlight streak along each blade sells the glossy plastic.
        pygame.draw.line(surf, _PROP_HI,
                         (prop_cx - prop_half * 0.8, prop_cy - pitch * 0.8),
                         (prop_cx - prop_half * 0.2, prop_cy - prop_h * 0.4), 1)

    # Central hub pin holding the blades.
    hub_r = max(1, r * 0.09)
    pygame.draw.circle(surf, _HUB, (int(prop_cx), int(prop_cy)), int(hub_r))

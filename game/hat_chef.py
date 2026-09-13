import math
import pygame

# Cool-white chef whites read crisp against a navy card; greys are the
# pleat shadows that carve the billowy crown into vertical columns.
_WHITE = (244, 246, 250)
_RIM = (255, 255, 255)
_SHADE1 = (214, 218, 228)
_SHADE2 = (196, 201, 214)
_BAND_SHADE = (224, 228, 236)
_BAND_LINE = (205, 210, 220)


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile CHEF TOQUE sized for a head of width head_w, centered at cx, band line at base_y."""
    f = 1 if facing >= 0 else -1

    band_h = max(2, head_w * 0.20)
    band_top = base_y - band_h
    half = head_w * 0.5
    # The puffy top mushrooms wider than the head and rises above base_y. Kept a
    # compact ~0.85× so the toque reads as headwear on the bird instead of a
    # towering column that dwarfs the head.
    crown_h = head_w * 0.85
    crown_top = base_y - band_h - crown_h
    puff_half = head_w * 0.62

    detailed = head_w >= 22

    def X(dx):
        return int(round(cx + f * dx))

    # --- Stiff band hugging the head ---
    band_rect = pygame.Rect(X(-half), int(band_top), int(head_w), int(round(band_h)) + 1)
    if band_rect.width < 0:
        band_rect.normalize()
    pygame.draw.rect(surf, _WHITE, band_rect)
    # Soft lower shadow + a crease line where the band meets the crown.
    pygame.draw.rect(surf, _BAND_SHADE,
                     pygame.Rect(band_rect.x, int(band_top + band_h * 0.55),
                                 band_rect.width, max(1, int(band_h * 0.45)) + 1))
    pygame.draw.line(surf, _BAND_LINE,
                     (band_rect.left, int(band_top)), (band_rect.right, int(band_top)),
                     max(1, int(head_w * 0.03)))

    # --- Billowy mushroom crown ---
    # Built as a closed silhouette: narrow waist at the band, bulging out past
    # the head to puff_half, then a row of soft rounded billows across the top.
    waist = half * 0.92
    shoulder_y = crown_top + crown_h * 0.58  # where the crown bulges widest
    dome_y = crown_top + crown_h * 0.22

    left_pts = [
        (X(-waist), band_top + 1),
        (X(-puff_half * 0.96), shoulder_y),
        (X(-puff_half), dome_y),
    ]
    right_pts = [
        (X(puff_half), dome_y),
        (X(puff_half * 0.96), shoulder_y),
        (X(waist), band_top + 1),
    ]

    # Soft billowy top: overlapping rounded lobes read as a pillowy mushroom
    # rather than a spiky crown. Drawn as the fill plus circles that bulge up.
    silhouette = left_pts + [(X(-puff_half), dome_y), (X(puff_half), dome_y)] + right_pts
    pygame.draw.polygon(surf, _WHITE, silhouette)

    n_lobes = 3 if detailed else 2
    lobe_r = puff_half * (0.46 if n_lobes == 3 else 0.62)
    for i in range(n_lobes):
        t = (i + 0.5) / n_lobes
        lx = -puff_half + (puff_half * 2.0) * t
        # Center lobe rides highest; outer lobes tuck slightly lower and fuller.
        lift = 1.0 - abs(t - 0.5) * 0.7
        ly = dome_y - lobe_r * 0.35 * lift
        pygame.draw.circle(surf, _WHITE, (X(lx), int(round(ly))), int(round(lobe_r)))

    # --- Vertical pleat shadows carving the crown into soft columns ---
    if detailed:
        n_pleats = 4
        for i in range(1, n_pleats):
            t = i / n_pleats
            px = -puff_half * 0.78 + (puff_half * 1.56) * t
            # Pleats narrow toward the band (waist) and fan out near the top.
            top_x = px
            bot_x = px * (waist / puff_half)
            col_top = crown_top + crown_h * 0.12
            col_bot = band_top + 1
            shade = _SHADE2 if i % 2 == 0 else _SHADE1
            w = max(1, int(head_w * 0.07))
            pygame.draw.line(surf, shade,
                             (X(top_x), int(col_top)), (X(bot_x), int(col_bot)), w)
        # A broad soft shadow on the trailing side gives the puff its volume.
        shade_poly = [
            (X(f * puff_half * 0.40), int(dome_y + crown_h * 0.05)),
            (X(puff_half), int(dome_y)),
            (X(puff_half * 0.92), int(shoulder_y)),
            (X(waist), int(band_top + 1)),
            (X(f * waist * 0.45), int(band_top + 1)),
        ]
        pygame.draw.polygon(surf, _SHADE1, shade_poly)

    # --- Crisp light rim along the leading (facing) edge of the crown ---
    rim_w = max(1, int(head_w * 0.05))
    rim_path = [
        (X(-waist), int(band_top + 1)),
        (X(-puff_half * 0.96), int(shoulder_y)),
        (X(-puff_half), int(dome_y)),
        (X(-puff_half * 0.55), int(dome_y - lobe_r * 0.30)),
    ]
    pygame.draw.lines(surf, _RIM, False, rim_path, rim_w)

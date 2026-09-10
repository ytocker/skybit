import pygame

# Snapback identity = a perfectly flat, stiff bill, so we draw the brim as a
# crisp quad with zero curl; everything else is proportional to head_w so the
# silhouette survives from hero (80) down to icon (18) scale.

# Two-tone streetwear palette: matte black crown, vivid accent panel/underbrim.
_CROWN = (24, 24, 30)
_CROWN_HI = (54, 54, 66)
_ACCENT = (235, 64, 52)
_ACCENT_HI = (255, 110, 96)
_BILL = (18, 18, 24)
_BILL_UNDER = (210, 52, 42)
_PATCH = (240, 226, 196)
_PATCH_INK = (24, 24, 30)
_SNAP = (228, 228, 236)


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile SNAPBACK cap sized for a head of width head_w, centered at cx, base line at base_y."""
    r = head_w * 0.5
    f = facing  # +1 bill points right; mirror x-offsets when -1

    def px(dx):
        # horizontal offset relative to head center, flipped by facing
        return cx + f * dx

    # Crown rides above the base line and wraps the round head. A tall,
    # structured front gives the snapback its boxy streetwear stance.
    crown_h = r * 1.14
    top_y = base_y - crown_h
    back_x = -r * 1.00   # rear of crown (away from bill)
    front_x = r * 0.86   # front of crown (over the bill)

    # ---- BILL (drawn first) -------------------------------------------------
    # HERO CUE: a flat, stiff slab held dead-level, no curl. Drawn before the
    # crown so the front panel overlaps its root and it reads as projecting
    # from under the cap, the way a real flat brim does.
    bill_y = base_y + r * 0.24
    bill_th = max(3, r * 0.22)
    bill_root = r * 0.10          # tucks under the front panel
    bill_tip = front_x + r * 1.28  # long flat-brim reach
    # Colored underbrim — classic two-tone snapback seen from below the slab.
    bill_under = [
        (px(bill_root), bill_y + bill_th * 0.45),
        (px(bill_tip), bill_y + bill_th * 0.45),
        (px(bill_tip - r * 0.04), bill_y + bill_th * 1.15),
        (px(bill_root), bill_y + bill_th * 1.05),
    ]
    pygame.draw.polygon(surf, _BILL_UNDER, bill_under)
    # Top slab: the dead-flat top edge is the whole snapback read.
    bill_top = [
        (px(bill_root), bill_y - bill_th * 0.50),
        (px(bill_tip), bill_y - bill_th * 0.50),
        (px(bill_tip), bill_y + bill_th * 0.50),
        (px(bill_root), bill_y + bill_th * 0.50),
    ]
    pygame.draw.polygon(surf, _BILL, bill_top)
    pygame.draw.line(
        surf, _CROWN_HI,
        (px(bill_root), bill_y - bill_th * 0.42),
        (px(bill_tip), bill_y - bill_th * 0.42),
        max(1, int(r * 0.05)),
    )

    # ---- SNAP closure (behind the crown back edge) --------------------------
    snap_x = back_x * 0.86
    snap_y = base_y + r * 0.04
    dots = 4 if r >= 14 else 3
    dot_r = max(1, r * 0.065)
    step = r * 0.17
    for i in range(dots):
        cxp = px(snap_x - i * step)
        pygame.draw.circle(surf, _SNAP, (int(cxp), int(snap_y)), int(dot_r))

    # ---- CROWN (over the bill root) -----------------------------------------
    # Front edge near-vertical (structured panel), back rounded.
    crown = [
        (px(back_x), base_y - r * 0.05),
        (px(back_x * 0.96), top_y + crown_h * 0.34),
        (px(-r * 0.45), top_y),
        (px(r * 0.30), top_y - crown_h * 0.03),
        (px(front_x), base_y - r * 0.26),
        (px(front_x), base_y + r * 0.16),
    ]
    pygame.draw.polygon(surf, _CROWN, crown)

    # Curved underside so the crown seats on a round head, not a flat one.
    seat_rect = pygame.Rect(0, 0, head_w * 0.98, r * 0.66)
    seat_rect.center = (cx, base_y + r * 0.06)
    pygame.draw.ellipse(surf, _CROWN, seat_rect)

    # Bright accent front panel — the two-tone block facing the bill.
    panel = [
        (px(r * 0.16), top_y + crown_h * 0.10),
        (px(front_x), base_y - r * 0.26),
        (px(front_x), base_y + r * 0.16),
        (px(r * 0.16), base_y + r * 0.12),
    ]
    pygame.draw.polygon(surf, _ACCENT, panel)

    # Soft top highlight band on the black crown for a stitched-panel read.
    hi = [
        (px(-r * 0.42), top_y + crown_h * 0.04),
        (px(r * 0.20), top_y - crown_h * 0.01),
        (px(r * 0.10), top_y + crown_h * 0.20),
        (px(-r * 0.44), top_y + crown_h * 0.22),
    ]
    pygame.draw.polygon(surf, _CROWN_HI, hi)
    # Seam between black crown and accent panel.
    pygame.draw.line(
        surf, _ACCENT_HI,
        (px(r * 0.16), top_y + crown_h * 0.11),
        (px(front_x - r * 0.01), base_y - r * 0.24),
        max(1, int(r * 0.05)),
    )

    # ---- PATCH (front panel, no real logo) ----------------------------------
    pw = r * 0.32
    ph = r * 0.30
    patch = pygame.Rect(0, 0, pw, ph)
    patch.center = (px(r * 0.46), base_y - r * 0.28)
    pygame.draw.rect(surf, _PATCH, patch, border_radius=max(1, int(r * 0.05)))
    if r >= 16:
        # Two tiny ink bars suggest stitched lettering without a trademark.
        bar = pygame.Rect(0, 0, pw * 0.60, max(1, ph * 0.15))
        bar.center = (patch.centerx, patch.centery - ph * 0.17)
        pygame.draw.rect(surf, _PATCH_INK, bar)
        bar2 = pygame.Rect(0, 0, pw * 0.44, max(1, ph * 0.15))
        bar2.center = (patch.centerx, patch.centery + ph * 0.17)
        pygame.draw.rect(surf, _PATCH_INK, bar2)

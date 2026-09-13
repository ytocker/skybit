import pygame


# Two-tone trucker palette. The white foam front and the off-white mesh back
# carry the silhouette; deeper greys give the bill and underbrim a touch of
# form against bright skies without a hard outer outline (caller adds that).
FRONT       = (242, 244, 248)   # foam front panel — bold, near-white
FRONT_SHADE = (205, 210, 222)   # foam front lower curve / right edge
MESH        = (222, 226, 234)   # mesh back base (slightly cooler than foam)
MESH_SHADE  = (192, 198, 210)   # mesh lower curve
MESH_DOT    = (168, 176, 192)   # the perforation grid — the trucker tell
BILL        = (212, 60, 64)     # red curved bill + button
BILL_DK     = (150, 36, 42)     # bill underside / shadow
SEAM        = (180, 186, 200)   # panel seam between front and back
PATCH       = (236, 196, 86)    # oval front patch — warm gold so it pops
PATCH_DK    = (170, 130, 40)    # patch edge
PATCH_LINE  = (120, 92, 30)     # stylized stitch mark on the patch (no logo)


def _mx(cx, x, facing):
    # Mirror an absolute x about cx so the whole cap flips with `facing`.
    return cx + (x - cx) * facing


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile TRUCKER CAP sized for a head of width head_w,
    centered at cx, base line at base_y.

    Crown rises above base_y; the bill points RIGHT at facing=1 and the
    underside is curved so the cap seats on a round head of diameter head_w.
    """
    r = head_w / 2.0

    # The cap straddles base_y: the crown bulges up by ~0.62r, and the band
    # wraps a touch below base_y so it reads as hugging a round skull.
    crown_h = r * 0.62
    band_dy = r * 0.10                       # how far the band dips below base_y
    front_x = cx - r * 0.04                  # foam front seam sits near centre

    # ── back / mesh crown ────────────────────────────────────────────────
    # The mesh half is the boxier dome behind the seam. Built from a polygon
    # so the silhouette stays crisp at tiny sizes where ellipses get mushy.
    back_top = base_y - crown_h * 0.92
    back_pts = [
        (_mx(cx, front_x, facing),            base_y - crown_h * 0.98),
        (_mx(cx, front_x, facing),            base_y + band_dy * 0.4),
        (_mx(cx, cx - r * 1.02, facing),      base_y + band_dy),
        (_mx(cx, cx - r * 1.02, facing),      base_y - crown_h * 0.30),
        (_mx(cx, cx - r * 0.78, facing),      base_y - crown_h * 0.78),
        (_mx(cx, cx - r * 0.32, facing),      back_top),
    ]
    pygame.draw.polygon(surf, MESH, back_pts)
    # Lower-rear curve shade so the dome reads round, not flat.
    pygame.draw.polygon(surf, MESH_SHADE, [
        (_mx(cx, cx - r * 1.02, facing),      base_y - crown_h * 0.04),
        (_mx(cx, cx - r * 1.02, facing),      base_y + band_dy),
        (_mx(cx, front_x, facing),            base_y + band_dy * 0.4),
        (_mx(cx, front_x, facing),            base_y - crown_h * 0.20),
    ])

    # ── foam front panel ─────────────────────────────────────────────────
    # Taller, boxy, stiff-foam front — the structural signature of a trucker
    # cap. Extends forward to meet the bill root.
    fwd_x = cx + r * 0.92
    front_pts = [
        (_mx(cx, front_x, facing),            base_y - crown_h * 0.98),
        (_mx(cx, cx + r * 0.30, facing),      base_y - crown_h * 1.04),
        (_mx(cx, fwd_x, facing),              base_y - crown_h * 0.50),
        (_mx(cx, fwd_x, facing),              base_y + band_dy * 0.55),
        (_mx(cx, front_x, facing),            base_y + band_dy * 0.40),
    ]
    pygame.draw.polygon(surf, FRONT, front_pts)
    # Front lower-right curve shade — gives the stiff foam a rounded brow.
    pygame.draw.polygon(surf, FRONT_SHADE, [
        (_mx(cx, fwd_x, facing),              base_y - crown_h * 0.50),
        (_mx(cx, fwd_x, facing),              base_y + band_dy * 0.55),
        (_mx(cx, cx + r * 0.40, facing),      base_y + band_dy * 0.45),
        (_mx(cx, cx + r * 0.40, facing),      base_y - crown_h * 0.20),
    ])

    # ── panel seam ───────────────────────────────────────────────────────
    sw = max(1, int(round(r * 0.07)))
    pygame.draw.line(surf, SEAM,
                     (_mx(cx, front_x, facing), base_y - crown_h * 0.96),
                     (_mx(cx, front_x, facing), base_y + band_dy * 0.40), sw)

    # ── mesh-dot texture (the trucker tell) ──────────────────────────────
    # Gated off below ~22px head_w: at tiny sizes the dots become noise and
    # the two-tone silhouette alone has to carry the read.
    if head_w >= 22:
        step = max(2, r * 0.16)
        x0 = cx - r * 0.95
        x1 = front_x - r * 0.10
        y0 = base_y - crown_h * 0.70
        y1 = base_y + band_dy * 0.2
        row = 0
        y = y0
        while y < y1:
            # Brick-offset every other row so it reads as a woven grid.
            xoff = (step * 0.5) if (row % 2) else 0.0
            x = x0 + xoff
            while x < x1:
                # Skirt the rounded rear edge so dots stay on the dome.
                edge = x0 + (y - y0) * 0.12
                if x >= edge:
                    px = int(round(_mx(cx, x, facing)))
                    pygame.draw.rect(surf, MESH_DOT, (px, int(round(y)), 1, 1))
                x += step
            y += step
            row += 1

    # ── oval front patch (no logo — stylized stitch cue only) ────────────
    pcx = _mx(cx, cx + r * 0.36, facing)
    pcy = base_y - crown_h * 0.42
    pw = r * 0.52
    ph = r * 0.34
    prect = pygame.Rect(0, 0, max(3, int(round(pw))), max(2, int(round(ph))))
    prect.center = (int(round(pcx)), int(round(pcy)))
    pygame.draw.ellipse(surf, PATCH_DK, prect.inflate(2, 2))
    pygame.draw.ellipse(surf, PATCH, prect)
    # A single stitched bar across the patch — a brand cue with no real mark.
    if head_w >= 22:
        bar_y = prect.centery
        pygame.draw.line(surf, PATCH_LINE,
                         (prect.left + prect.w * 0.28, bar_y),
                         (prect.right - prect.w * 0.24, bar_y),
                         max(1, int(round(r * 0.05))))

    # ── curved bill pointing right ───────────────────────────────────────
    # Drawn as a thin downward-curving wedge: top surface lit, underside
    # darker, with a tip that droops below base_y like a pre-curved brim.
    bx0 = cx + r * 0.62
    bx_tip = cx + r * 1.72
    bill_top = [
        (_mx(cx, bx0, facing),                base_y - crown_h * 0.06),
        (_mx(cx, cx + r * 1.16, facing),      base_y - crown_h * 0.04),
        (_mx(cx, bx_tip, facing),             base_y + r * 0.18),
        (_mx(cx, cx + r * 1.28, facing),      base_y + r * 0.12),
        (_mx(cx, bx0, facing),                base_y + band_dy * 0.6),
    ]
    pygame.draw.polygon(surf, BILL, bill_top)
    # Underside shadow strip along the bill's lower curve.
    pygame.draw.polygon(surf, BILL_DK, [
        (_mx(cx, bx0, facing),                base_y + band_dy * 0.6),
        (_mx(cx, cx + r * 1.28, facing),      base_y + r * 0.12),
        (_mx(cx, bx_tip, facing),             base_y + r * 0.18),
        (_mx(cx, bx_tip - r * 0.10, facing),  base_y + r * 0.27),
        (_mx(cx, cx + r * 1.18, facing),      base_y + r * 0.20),
        (_mx(cx, bx0, facing),                base_y + band_dy * 1.0),
    ])

    # ── crown button ─────────────────────────────────────────────────────
    btn_r = max(1, int(round(r * 0.10)))
    btn_c = (int(round(_mx(cx, cx - r * 0.18, facing))),
             int(round(back_top - btn_r * 0.4)))
    pygame.draw.circle(surf, BILL, btn_c, btn_r)

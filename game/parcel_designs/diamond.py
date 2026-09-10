"""DIAMOND — a brilliant-cut gem parcel cosmetic carried below Pip.

The identity is the classic brilliant-cut silhouette read by VALUE, not hue: a
flat top TABLE, a short CROWN of facets stepping down to a girdle, then a long
pointed PAVILION tapering to a tip — the unmistakable gem shape. It reads icy
cyan-white, but the gem-ness rides on a hard value ladder (bright table + a lit
crown facet vs a clearly darker shade facet + a deep pavilion) so it survives
grayscale as a faceted stone rather than a flat shard.

22px read tradeoffs (WHY): at true size a fussy facet grid aliases to mud, so we
commit to a FEW bold facets — a single table, two crown facets (one lit, one
shade), and two pavilion facets (one lit, one shade) split down a centre seam.
That centre seam is the load-bearing line that says "cut gem": the eye reads the
left half as lit and the right half as shade across both crown and pavilion. One
hot sparkle glint sits on the upper-left table corner — the brilliant-cut's
signature fire — kept to a single bright pip so it never smears. A baked dark
OUTLINE drawn first (slightly inflated) carries the angular shape on bright DAY
sky; a cool icy keyline rim inside is the NIGHT lifeline. The whole gem is held
off the surface edges so the sharp pavilion tip never clips under the gameplay
rotozoom as Pip banks.
"""
import pygame

# Icy palette tuned so IDENTITY RIDES ON VALUE, not hue, so the gem survives
# grayscale. A committed light->dark ladder: near-white table, a bright lit
# crown/pavilion on the left, a clearly darker shade crown/pavilion on the right,
# and the deepest tone at the pavilion tip. In grayscale the eye then reads a lit
# half and a shade half meeting at a centre seam — a faceted stone, not a disc.
TABLE = (236, 250, 255)       # flat top facet — the brightest mass
CROWN_HI = (200, 234, 248)    # lit crown facet (upper-left)
CROWN_SH = (126, 176, 206)    # shade crown facet (upper-right) — hard step down
PAV_HI = (158, 210, 236)      # lit pavilion facet (lower-left)
PAV_SH = (86, 138, 178)       # shade pavilion facet (lower-right) — darker still
PAV_TIP = (52, 96, 134)       # deepest tone where the pavilion points to its tip
GLINT = (255, 255, 255)       # the single hot sparkle pip on the table corner
OUTLINE = (16, 34, 54)        # dark, cool: reads as an edge on bright day sky
KEYLINE = (188, 232, 250)     # icy rim — the NIGHT lifeline


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static diamond sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Brilliant-cut geometry, held inside the surface so the sharp tip never
    # clips under the rotozoom. The gem is wide-shouldered at the girdle and tall,
    # with a short crown above the girdle and a long pavilion below — the classic
    # proportions that make the silhouette unmistakable even tiny.
    half_w = 14                    # girdle half-width (widest point)
    table_half = 7                 # table half-width (flat top)
    top_y = 11                     # table line (top of crown)
    girdle_y = 19                  # widest line (crown/pavilion boundary)
    tip_y = 35                     # pavilion point (bottom tip)

    # Key vertices.
    table_l = (cx - table_half, top_y)
    table_r = (cx + table_half, top_y)
    gird_l = (cx - half_w, girdle_y)
    gird_r = (cx + half_w, girdle_y)
    tip = (cx, tip_y)
    top_mid = (cx, top_y)          # centre seam top (table centre)
    gird_mid = (cx, girdle_y)      # centre seam at girdle

    # --- Baked dark OUTLINE drawn first, slightly inflated, so the angular gem
    # silhouette carries on bright DAY sky. An outset polygon traced around the
    # full brilliant-cut hull.
    hull = [table_l, table_r, gird_r, tip, gird_l]
    outline_hull = [
        (table_l[0] - 2, table_l[1] - 2), (table_r[0] + 2, table_r[1] - 2),
        (gird_r[0] + 2, gird_r[1]),       (tip[0], tip[1] + 2),
        (gird_l[0] - 2, gird_l[1]),
    ]
    pygame.draw.polygon(surf, OUTLINE, outline_hull)

    # --- PAVILION (drawn first so the crown overlaps cleanly at the girdle).
    # Two big facets split down the centre seam: a lit left half and a clearly
    # darker shade right half, both converging on the tip — the long taper that
    # says "gem", read by value so it holds in grayscale.
    pygame.draw.polygon(surf, PAV_HI, [gird_l, gird_mid, tip])
    pygame.draw.polygon(surf, PAV_SH, [gird_mid, gird_r, tip])
    # A deep tip wedge so the pavilion darkens toward its point — adds a third
    # value step and pins the eye to the sharp bottom that reads as a cut stone.
    pygame.draw.polygon(surf, PAV_TIP, [
        (cx - 5, girdle_y + 7), (cx + 5, girdle_y + 7), tip])

    # --- CROWN: two bevel facets between the girdle and the table, split on the
    # same centre seam so the lit/shade halves continue up from the pavilion —
    # one continuous lit-left / shade-right read across the whole gem.
    pygame.draw.polygon(surf, CROWN_HI, [table_l, top_mid, gird_mid, gird_l])
    pygame.draw.polygon(surf, CROWN_SH, [top_mid, table_r, gird_r, gird_mid])

    # --- TABLE: the flat bright top facet, the brightest mass and the anchor of
    # the value ladder. A small trapezoid seated on the crown.
    pygame.draw.polygon(surf, TABLE, [
        table_l, table_r, (cx + table_half - 1, top_y + 3),
        (cx - table_half + 1, top_y + 3)])

    # --- Centre seam: a faint dark line down the gem's axis so the two halves
    # read as separate facets meeting at a ridge, not a smooth gradient. Kept
    # subtle so it never fights the value steps.
    pygame.draw.line(surf, OUTLINE, top_mid, tip, 1)
    pygame.draw.line(surf, OUTLINE, gird_l, gird_r, 1)   # girdle ridge

    # --- ICY keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the gem hull just inside the
    # dark outline so the silhouette never dies on a night sky.
    pygame.draw.polygon(surf, KEYLINE, hull, 1)

    # --- The single hot SPARKLE glint on the upper-left table corner — the
    # brilliant-cut's signature fire. One bright pip plus a tiny 4-point cross so
    # it reads as a sparkle, kept compact so it never smears at 22px.
    gx, gy = cx - table_half + 2, top_y + 1
    pygame.draw.circle(surf, GLINT, (gx, gy), 2)
    pygame.draw.line(surf, GLINT, (gx - 3, gy), (gx + 3, gy), 1)
    pygame.draw.line(surf, GLINT, (gx, gy - 3), (gx, gy + 3), 1)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))

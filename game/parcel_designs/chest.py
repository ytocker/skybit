"""TREASURE CHEST parcel cosmetic (HIGH tier).

A gold-banded pirate chest: a wood trunk with a low DOMED lid split from the
body by a dark SHADOW SEAM, two thick vertical metal corner BANDS and a centre
LOCK plate that is the single brightest element. The dark lid seam is the line
that converts "banded barrel" into "chest"; the near-white lock plate wins the
centre so the eye lands on loot, not staves. The chest is deliberately WIDER
than TALL — the genre-standard horizontal box read.

Built at 2× (44px) then smoothscaled to 22 so the dark outline, the gold band
edges, the lid seam and the lock survive the tiny read AND the bird's tilt
rotation. The identity (gold bands + dark lid seam + bright lock) is packed
into the LOWER/visible half because Pip and his red body occlude the parcel's
top in carry; the dome TOP stays plain wood so nothing up top relies on pure
red, which would melt into Pip."""
import pygame

SIZE = 22
SS = 44  # 2× supersample; smoothscaled down for a crisp outline at 22px

# DAY palette — warm wood trunk, bright gold bands, near-white lock plate.
WOOD = (0x7A, 0x4A, 0x22)
WOOD_SH = (0x52, 0x30, 0x14)   # trunk-bottom shade for a rounded body
WOOD_HI = (0xA0, 0x6C, 0x3A)   # lit upper face of the lid dome
GOLD = (0xE8, 0xB2, 0x3C)      # bands — the supporting value colour
GOLD_HI = (0xFB, 0xE0, 0x8A)   # band highlight; lifts gold off the wood by day
GOLD_SH = (0xA8, 0x7A, 0x1E)   # band/lid shadow seam — reads dark in grayscale
SEAM = (0x6B, 0x46, 0x12)      # the lid seam, darker than GOLD_SH so it reads
                               # as a true split line at 22px and in grayscale
LOCK = (0xF6, 0xC8, 0x52)      # lock plate body — a step brighter than the bands
LOCK_HI = (0xFF, 0xF4, 0xC8)   # lock top bevel near-white — the brightest pixel,
                               # so the lock unambiguously leads the read
LOCK_GLOW = (0xFF, 0xD6, 0x59) # warm rim so the lock pops by day and at night
OUTLINE = (0x24, 0x12, 0x08)   # dark high-value edge to hold the silhouette


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _vgrad_rounded(w, h, top, bot, radius):
    """A vertical-gradient fill clipped to a rounded rect — the rounded trunk
    body and the lock plate both lean on this so they read as volume, not flats."""
    fill = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        fill.fill(_lerp(top, bot, y / max(1, h - 1)) + (255,),
                  pygame.Rect(0, y, w, 1))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=radius)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return fill


def build(mode="normal", icon_size: int = 0):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    # WIDER + SHORTER than round 1 — a horizontal box reads as a chest where a
    # tall banded cylinder reads as a barrel.
    BODY_W = 38
    bx = cx - BODY_W // 2

    # ── Drop shadow grounds the chest under Pip ──────────────────────────────
    sh = pygame.Surface((BODY_W + 6, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 14, 120), sh.get_rect())
    s.blit(sh, (cx - (BODY_W + 6) // 2, 39))

    # ── Trunk body (lower, visible half) ─────────────────────────────────────
    # The carried parcel shows its bottom most, so the trunk + bands + lock all
    # sit here. Outline frame first, then the rounded wood gradient.
    body = pygame.Rect(bx, 24, BODY_W, 15)
    pygame.draw.rect(s, OUTLINE, body.inflate(4, 4), border_radius=5)
    s.blit(_vgrad_rounded(body.w, body.h, WOOD, WOOD_SH, 4), body.topleft)

    # ── Domed lid (upper, partly occluded in carry) ──────────────────────────
    # A wide, low arch sitting on the trunk — dome height cut ~15% from round 1
    # so the chest stays horizontal. Its top is what Pip overlaps, so the dome
    # stays plain wood; the gold lives on the bands/lock below it.
    lid = pygame.Rect(bx - 1, 13, BODY_W + 2, 15)
    pygame.draw.ellipse(s, OUTLINE, lid.inflate(4, 4))
    dome_mask = pygame.Surface((lid.w, lid.h), pygame.SRCALPHA)
    pygame.draw.ellipse(dome_mask, (255, 255, 255, 255), dome_mask.get_rect())
    dome = pygame.Surface((lid.w, lid.h), pygame.SRCALPHA)
    for y in range(lid.h):
        dome.fill(_lerp(WOOD_HI, WOOD, y / max(1, lid.h - 1)) + (255,),
                  pygame.Rect(0, y, lid.w, 1))
    dome.blit(dome_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(dome, lid.topleft)

    # ── LID SEAM — the line that makes it a chest, not a barrel ──────────────
    # A readable dark split between the domed lid and the trunk body. A thick
    # dark seam under a thin gold lip: the gold catches light on the lid's lower
    # edge, the dark line below it is the shadow where lid meets body.
    seam_y = body.top
    pygame.draw.rect(s, GOLD_HI, (bx, seam_y - 2, BODY_W, 1))   # lit lid lip
    pygame.draw.rect(s, SEAM, (bx - 2, seam_y - 1, BODY_W + 4, 2))  # dark seam
    pygame.draw.line(s, OUTLINE, (bx - 1, seam_y + 1),
                     (body.right, seam_y + 1), 1)

    # ── Two thick vertical corner bands ──────────────────────────────────────
    # Only two (plus the dark lid seam acting as the horizontal element) — the
    # bands SUPPORT, they no longer compete with the lock. Each is a gold strip
    # with a highlight edge and a shadow seam so it reads as raised metal.
    band_top = lid.top + 4
    for vx in (bx + 4, body.right - 8):
        band = pygame.Rect(vx, band_top, 4, body.bottom - band_top + 1)
        pygame.draw.rect(s, OUTLINE, band.inflate(2, 0))
        pygame.draw.rect(s, GOLD, band)
        pygame.draw.line(s, GOLD_HI, (band.x, band.y),
                         (band.x, band.bottom - 1), 1)
        pygame.draw.line(s, GOLD_SH, (band.right - 1, band.y),
                         (band.right - 1, band.bottom - 1), 1)

    # ── Centre LOCK plate — the unambiguous focal point ──────────────────────
    # Squarer and a touch larger than round 1, pushed one clear value step
    # BRIGHTER than the bands (near-white top bevel), with a warm rim glow and a
    # single rim-glint on the top bevel. This is the brightest, squarest element
    # so the eye lands on the lock first — "treasure chest", not "banded box".
    lock = pygame.Rect(0, 0, 12, 12)
    lock.center = (cx, 33)
    pygame.draw.rect(s, OUTLINE, lock.inflate(3, 3), border_radius=3)
    pygame.draw.rect(s, LOCK_GLOW, lock.inflate(1, 1), border_radius=3)
    s.blit(_vgrad_rounded(lock.w, lock.h, LOCK_HI, LOCK, 3), lock.topleft)
    # Top bevel: a near-white band so the lock out-values the gold bands, plus a
    # single warm rim-glint at the bevel's top corner (replaces the coin glints).
    pygame.draw.rect(s, LOCK_HI, (lock.x + 1, lock.y + 1, lock.w - 2, 2))
    pygame.draw.circle(s, (255, 255, 255), (lock.x + 3, lock.y + 1), 1)
    # Keyhole: dark circle + slot, reads as a lock even when banked.
    pygame.draw.circle(s, OUTLINE, (cx, lock.y + 6), 2)
    pygame.draw.rect(s, OUTLINE, (cx - 1, lock.y + 6, 2, 4))

    if icon_size:
        return pygame.transform.smoothscale(s, (icon_size, icon_size))
    return pygame.transform.smoothscale(s, (SIZE, SIZE))

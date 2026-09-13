"""MONOCLE — a single dapper round lens over Pip's near eye, in side profile.

Aristocratic read: ONE heavy gold-rimmed lens sits over the front (+facing)
eye, with a tiny gold "brow pinch" at the top of the rim and a short solid
chain hooking down/back toward the ear (-facing). Because Pip is shown in side
profile a single near-eye lens reads perfectly — no far lens, no bridge.

Tiny-scale read is the hard case: at eye_w=22 one pale disc + a dangling
dotted chain reads as a COIN or BUBBLE, not eyewear. Three defences keep it
unmistakably "frame": the rim is a FILLED ring with a DARK gold outer edge
(a stroked 1px circle would stipple and break, but a dark disc under a lighter
disc gives a solid frame-coloured band); the glass is AMBER-tinted so it never
reads as one of the white/clear lens styles; and the chain collapses to a few
SOLID dots / a short solid hook instead of a stipple that smears into noise.
"""
import pygame

# Gold standardized for the SET's "dapper" frame family. The OUTER edge is a
# deliberately dark gold so the rim reads as a metal frame, not a bright coin.
_RIM_EDGE = (110,  74,  22)         # dark outer edge — sells "frame", not coin
_RIM      = (232, 184,  78)         # warm gold metal body
_RIM_H    = (255, 240, 174)         # bright top-rim crescent
_RIM_D    = (150, 104,  38)         # underside / shadow side of the wire
# Amber glass — kept translucent so the dark eye reads THROUGH it; the warm
# tint still separates the lens from the white/clear-frame disc styles.
_GLASS_T  = (255, 206, 118)         # warm amber top of the tinted glass
_GLASS_B  = (210, 148,  64)         # deeper amber floor (vertical fade = curve)
_GLINT    = (255, 252, 238)


def _tinted_disc(r, top, bot, alpha):
    """Round glass disc of radius r with a vertical top→bot tint at `alpha`.
    The vertical fade gives the flat disc a sense of curved amber glass."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    span = max(1, r * 2 - 1)
    for yy in range(r * 2):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(g, c, (0, yy), (r * 2, yy))
    clip = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (r, r), r)
    g.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return g


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r   = max(3, int(eye_w * 0.30))
    # Heavier rim than before so the gold band survives + reads as a frame.
    rim = max(2, int(eye_w * 0.10))
    # Sit the lens over the near eye, ridden slightly FORWARD so the gold ring
    # laps the beak base the way a worn monocle grips the socket; a small lift
    # keeps the disc + lower chain anchor off the beak tip.
    lx = cx + f * int(eye_w * 0.10)
    ly = cy - max(1, int(eye_w * 0.07))

    tiny = eye_w < 30   # at tiny scale, collapse the chain to a solid hook

    # Chain anchors at the BACK-bottom of the rim (toward the ear, -facing).
    cr = max(1, int(eye_w * 0.05))
    ax = lx - f * int(r * 0.78)
    ay = ly + int(r * 0.62)
    if tiny:
        # A dotted run stipples into noise at 22px, so use ONE short solid hook
        # of three fat dots — unambiguously a hanging chain, never a stipple.
        drop = eye_w * 0.46
        for i in range(1, 4):
            t = i / 3.0
            px = ax - f * int(eye_w * 0.07 * (t - t * t) * 4.0)
            py = ay + int(drop * t)
            pygame.draw.circle(surf, _RIM_D, (px, py + 1), cr + 1)
            pygame.draw.circle(surf, _RIM, (px, py), cr + 1)
    else:
        drop = eye_w * 0.62
        for i in range(1, 7):
            t = i / 6.0
            px = ax - f * int(eye_w * 0.10 * (t - t * t) * 4.0)  # bows back
            py = ay + int(drop * t)
            pygame.draw.circle(surf, _RIM_D, (px, py + 1), cr)
            pygame.draw.circle(surf, _RIM, (px, py), cr)
    # A slightly fatter "fixing ring" where the chain meets the rim.
    pygame.draw.circle(surf, _RIM_D, (ax, ay + 1), cr + 1)
    pygame.draw.circle(surf, _RIM, (ax, ay), cr + 1)

    # Solid gold ring built as nested filled discs (no 1px stroked circles):
    # dark outer EDGE, then the gold body, then the amber glass inset by rim.
    # The dark edge is the key tiny-scale fix — a 1–2px dark band bounds the
    # gold so the lens reads as a framed circle, not a flat pale coin.
    edge = max(1, int(eye_w * 0.03))
    pygame.draw.circle(surf, _RIM_EDGE, (lx, ly), r)
    pygame.draw.circle(surf, _RIM_D, (lx, ly + 1), r - edge)  # underside wire
    pygame.draw.circle(surf, _RIM, (lx, ly), max(2, r - edge))
    # The gold ring and the orange beak are near-identical in hue/value, so at
    # the beak-side (+facing) arc they fuse into one blob. Lay a hard dark edge
    # only on that forward arc (>=1px even tiny) so the ring reads as a separate
    # framed lens against the beak behind it.
    bedge = max(1, int(eye_w * 0.045))
    pygame.draw.arc(surf, _RIM_EDGE, (lx - r, ly - r, r * 2, r * 2),
                    -1.15, 1.15, bedge)
    gr = max(2, r - rim)
    # Low alpha so the dark eye behind the lens still reads through the tint —
    # an opaque disc here would look like a solid gold coin, not eyewear.
    glass = _tinted_disc(gr, _GLASS_T, _GLASS_B, 110)
    surf.blit(glass, (lx - gr, ly - gr))
    # A small dark PUPIL inside the lens so the monocle reads as glass-over-eye
    # (not a blank gold coin) and stays legible at native scale through the amber.
    pup = max(1, int(eye_w * 0.06))
    pygame.draw.circle(surf, (40, 26, 12), (lx + f * (gr // 4), ly), pup)

    # Bright top crescent so the round metal pops off the scarlet head.
    pygame.draw.arc(surf, _RIM_H, (lx - r, ly - r, r * 2, r * 2),
                    0.5, 2.5, max(2, rim - 1))

    # Gold "brow pinch" at the very top of the rim — the dapper tell of a
    # monocle that grips under the brow. A short thick stub of gold, capped
    # with a bright bead so it reads even at tiny scale.
    bx = lx + f * int(r * 0.22)
    by = ly - r
    pygame.draw.line(surf, _RIM_D, (bx, by + 1),
                     (bx + f * int(r * 0.34), by - int(r * 0.30) + 1),
                     max(2, rim))
    pygame.draw.line(surf, _RIM, (bx, by),
                     (bx + f * int(r * 0.34), by - int(r * 0.30)),
                     max(2, rim))
    pygame.draw.circle(surf, _RIM_H,
                       (bx + f * int(r * 0.34), by - int(r * 0.30)),
                       max(1, rim - 1))

    # One pinprick glint on the lens — sells the glossy round glass.
    pygame.draw.circle(surf, _GLINT, (lx - f * (r // 2), ly - r // 2),
                       max(1, int(eye_w * 0.055)))

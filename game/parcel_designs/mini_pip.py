"""MINI-PIP — a faithful chibi of Pip carried as the parcel (his baby).

The read must survive the gameplay rotozoom carried BELOW Pip on both day and
night sky, and stay unmistakably a tiny scarlet-macaw of Pip's own family — same
red body / blue wing / green-tipped feathers / yellow hooked beak / dark-faced
eye palette as the parent in parrot.py. So this is built from Pip's exact
colours, but re-proportioned as a baby: an oversized round head over a small
upright body, looking UP at the parent, with ONE big bright eye and NO sunglasses
(it's a baby, not styled Pip).

HIGH-FIDELITY approach (WHY): the whole baby is composed at 6× the output on a
168px work surface — so the parent's real detail (hooked two-tone beak, a layered
blue wing with the green macaw tip + a feather divider, a bright bare-skin eye
with catch-light, cheek/crown shaping, a short layered tail) all antialiases
crisply when smoothscaled DOWN to the parcel, instead of collapsing to flat
masses. Output is bumped to 28px (a touch over PARCEL_SIZE; the draw code
centre-anchors and parcels may run larger) so the beak + eye + wing detail
actually resolves on-screen without growing the footprint much.

A baked dark OUTLINE drawn first (inflated silhouette) carries the shape on both
day and night sky — it is deliberately the ONLY rim, so the head and body read as
one bird rather than two outlined circles. Everything is held in toward centre
with off-edge margins so the rotozoom across Pip's bank arc never clips the
crest, beak, or tail against the surface edge.
"""
import pygame

# Pip's own palette (mirrored from game.draw / game.parrot) so the baby reads as
# kin by colour alone, before silhouette even resolves.
BIRD_RED    = (240,  55,  55)
BIRD_RED_D  = (170,  25,  25)
BIRD_RED_HI = (255, 120, 120)   # cheek / crown lift
BIRD_WING   = ( 40, 100, 255)
BIRD_WING_D = ( 20,  55, 180)
BIRD_WING_HI= (170, 210, 255)   # crisp top-edge feather highlight
BIRD_TIP    = ( 50, 220, 100)   # macaw green wing-tip flash
BIRD_TIP_Y  = (255, 200,  60)   # the yellow secondary stripe between blue & green
BIRD_BELLY  = (255, 170,  50)
BIRD_BEAK   = (255, 185,   0)
BIRD_BEAK_D = (200, 130,   0)
BIRD_BEAK_HI= (255, 232, 150)
EYE_PATCH   = (250, 243, 236)   # scarlet-macaw bare-skin facial patch
EYE_DARK    = ( 26,  18,  24)
WHITE       = (255, 255, 255)
OUTLINE     = ( 30,  12,  16)   # dark, warm — pops on bright day stone

# 6× supersample: compose the whole baby at SS px, smoothscale DOWN to OUT.
OUT = 28
SS  = 6
S   = OUT * SS                  # 168px work surface


def _S(v):  return int(round(v * SS))
def _P(p):  return (_S(p[0]), _S(p[1]))
def _L(pts): return [_P(p) for p in pts]
def _w(v):  return max(1, _S(v))


def _ellipse(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color,
                        pygame.Rect(_S(cx - rx), _S(cy - ry),
                                    _S(rx * 2), _S(ry * 2)))


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static baby-Pip for every parent skin.
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    # All geometry below is in OUT-px (28px) space; _S()/_ellipse scale to SS.
    # Chibi proportions: an oversized head high on the canvas, a small compact
    # body below, both biased toward centre so the rotozoom envelope never clips
    # the crest / beak / tail against the 28px edge.
    cx = OUT / 2
    head_cx, head_cy, head_rx, head_ry = cx + 0.5, 11.0, 8.5, 8.0
    body_cx, body_cy, body_rx, body_ry = cx - 1.0, 20.5, 6.0, 5.5

    # ── Baked dark OUTLINE (drawn first, inflated) — the DAY silhouette read. ──
    # An outline-coloured underlay under every mass so the whole baby carries a
    # crisp 1px-equivalent rim after downscale, regardless of what it sits on.
    _ellipse(surf, OUTLINE, body_cx, body_cy, body_rx + 1.4, body_ry + 1.4)
    _ellipse(surf, OUTLINE, head_cx, head_cy, head_rx + 1.4, head_ry + 1.4)

    # ── Tail: a short layered red→orange→yellow fan below the body (Pip's tail
    # in baby scale — three stacked wedges instead of the parent's four). ──
    tail_colors = ((BIRD_RED_D, 0.0), ((240, 95, 40), 0.9), (BIRD_BELLY, 1.8))
    base = (body_cx - 4.5, body_cy + 3.0)
    pygame.draw.polygon(surf, OUTLINE, _L([
        (base[0] - 4.6, base[1] + 0.6), (base[0] + 1.0, base[1] - 0.6),
        (base[0] + 1.4, base[1] + 5.6), (base[0] - 4.2, base[1] + 7.6)]))
    for c, o in tail_colors:
        pygame.draw.polygon(surf, c, _L([
            (base[0] - 4.0 + o, base[1] + 0.4 + o * 0.4),
            (base[0] + 0.6 + o * 0.3, base[1] - 0.2 + o * 0.4),
            (base[0] + 1.0 + o * 0.3, base[1] + 4.0 + o * 0.6),
            (base[0] - 3.6 + o, base[1] + 5.8 + o * 0.5)]))

    # ── Body: small red ellipse, dark underside, warm two-tone belly. ──
    _ellipse(surf, BIRD_RED,    body_cx, body_cy, body_rx, body_ry)
    _ellipse(surf, BIRD_RED_D,  body_cx - 1.0, body_cy + 2.2, body_rx - 1.6, body_ry - 2.0)
    _ellipse(surf, BIRD_BELLY,  body_cx - 0.6, body_cy + 1.8, 3.6, 2.6)
    _ellipse(surf, BIRD_RED_HI, body_cx - 1.6, body_cy - 2.2, 2.8, 1.6)  # chest sheen

    # ── Folded wing: a layered blue patch on the body's far side with the green
    # macaw tip + a yellow secondary stripe + a feather divider + a bright top
    # edge — the parent's wing signature, kept legible at baby scale. ──
    wing = [(body_cx + 0.5, body_cy - 3.6), (body_cx + 6.4, body_cy - 1.6),
            (body_cx + 5.0, body_cy + 4.2), (body_cx + 0.2, body_cy + 3.0)]
    pygame.draw.polygon(surf, OUTLINE, _L([(p[0] + 0.7, p[1] + 0.7) for p in wing]))
    pygame.draw.polygon(surf, BIRD_WING, _L(wing))
    pygame.draw.polygon(surf, BIRD_WING_D, _L([   # darker underside wedge
        (body_cx + 0.2, body_cy + 3.0), (body_cx + 5.0, body_cy + 4.2),
        (body_cx + 2.6, body_cy + 3.6)]))
    pygame.draw.polygon(surf, BIRD_TIP_Y, _L([     # yellow secondary stripe
        (body_cx + 4.4, body_cy - 1.8), (body_cx + 6.0, body_cy - 0.8),
        (body_cx + 5.6, body_cy + 1.4), (body_cx + 4.0, body_cy + 0.6)]))
    pygame.draw.polygon(surf, BIRD_TIP, _L([       # green macaw tip flash
        (body_cx + 5.2, body_cy - 1.4), (body_cx + 7.0, body_cy + 0.2),
        (body_cx + 5.8, body_cy + 2.2)]))
    pygame.draw.line(surf, BIRD_WING_D,            # feather divider
                     _P((body_cx + 1.4, body_cy - 1.2)),
                     _P((body_cx + 5.2, body_cy + 0.4)), _w(0.7))
    pygame.draw.line(surf, BIRD_WING_HI,           # crisp top-edge highlight
                     _P((body_cx + 1.2, body_cy - 3.0)),
                     _P((body_cx + 5.6, body_cy - 1.2)), _w(0.7))

    # ── Head: big red dome with brighter crown + cheek flush; a small upward
    # crest tuft sells "baby parrot". ──
    _ellipse(surf, BIRD_RED,    head_cx, head_cy, head_rx, head_ry)
    _ellipse(surf, BIRD_RED_HI, head_cx - 1.4, head_cy - 3.4, 4.0, 2.4)   # crown lift
    _ellipse(surf, BIRD_RED_HI, head_cx - 3.6, head_cy + 0.8, 2.0, 1.8)   # cheek flush
    # Crest: two short up-pointing red flicks at the crown, each outlined.
    for dx in (-2.4, 0.8):
        pygame.draw.polygon(surf, OUTLINE, _L([
            (head_cx + dx - 1.6, head_cy - head_ry + 1.4),
            (head_cx + dx + 0.6, head_cy - head_ry - 2.8),
            (head_cx + dx + 1.6, head_cy - head_ry + 1.4)]))
        pygame.draw.polygon(surf, BIRD_RED, _L([
            (head_cx + dx - 0.8, head_cy - head_ry + 1.4),
            (head_cx + dx + 0.6, head_cy - head_ry - 2.0),
            (head_cx + dx + 1.4, head_cy - head_ry + 1.4)]))

    # ── Eye: ONE big bright eye on a pale bare-skin facial patch (the scarlet
    # macaw's signature) with feather-streak lines + a hot white catch-light.
    # Pushed forward + slightly up because the baby is looking UP at its parent;
    # this is the dominant face cue at true size. ──
    eye_cx, eye_cy = head_cx + 2.2, head_cy - 0.4
    _ellipse(surf, EYE_PATCH, eye_cx, eye_cy, 4.2, 4.0)
    pygame.draw.line(surf, (236, 210, 205),
                     _P((eye_cx - 3.4, eye_cy - 1.6)), _P((eye_cx + 3.4, eye_cy - 1.6)), _w(0.6))
    pygame.draw.line(surf, (236, 210, 205),
                     _P((eye_cx - 3.4, eye_cy + 1.6)), _P((eye_cx + 3.4, eye_cy + 1.6)), _w(0.6))
    pygame.draw.circle(surf, EYE_DARK, _P((eye_cx + 0.4, eye_cy)), _S(2.7))   # iris
    pygame.draw.circle(surf, (8, 6, 10), _P((eye_cx + 0.4, eye_cy)), _S(2.7), _w(0.6))
    pygame.draw.circle(surf, WHITE, _P((eye_cx - 0.8, eye_cy - 1.0)), _S(1.1))  # catch-light
    pygame.draw.circle(surf, (255, 255, 255), _P((eye_cx + 1.4, eye_cy + 1.4)), _S(0.5))

    # ── Beak: short two-tone hooked yellow beak under the eye, angled up toward
    # the parent (geometry ported from the parent's hooked beak, baby-scaled). ──
    beak = [(head_cx + 5.0, head_cy + 0.8), (head_cx + 9.2, head_cy + 1.8),
            (head_cx + 7.6, head_cy + 5.0), (head_cx + 4.8, head_cy + 4.0)]
    pygame.draw.polygon(surf, OUTLINE, _L([(p[0] + 0.7, p[1] + 0.7) for p in beak]))
    pygame.draw.polygon(surf, BIRD_BEAK, _L(beak))
    pygame.draw.polygon(surf, BIRD_BEAK_D, _L([   # lower mandible / hook shadow
        (head_cx + 4.8, head_cy + 3.4), (head_cx + 7.6, head_cy + 5.0),
        (head_cx + 4.8, head_cy + 4.0)]))
    pygame.draw.line(surf, BIRD_BEAK_D,            # mandible split line
                     _P((head_cx + 5.0, head_cy + 2.8)),
                     _P((head_cx + 8.4, head_cy + 3.2)), _w(0.6))
    pygame.draw.line(surf, BIRD_BEAK_HI,           # top gloss
                     _P((head_cx + 5.4, head_cy + 1.6)),
                     _P((head_cx + 8.6, head_cy + 2.2)), _w(0.6))

    # ── Tiny tucked feet under the body so the baby reads as perched upright. ──
    for fx in (-2.2, 2.0):
        pygame.draw.line(surf, BIRD_BEAK_D,
                         _P((body_cx + fx, body_cy + body_ry - 0.6)),
                         _P((body_cx + fx, body_cy + body_ry + 2.2)), _w(1.4))

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (OUT, OUT))

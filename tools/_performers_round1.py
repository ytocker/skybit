"""Promenade STREET PERFORMERS variety — round 1 candidate-sheet generator.

Seventh sidewalk-overhaul family, sibling to ped_cast / day_cast / food_stalls /
animals_cast / greenery_cast / props_cast. Today the near-lane HUMAN single-busker
roster is only THREE fixed acts (perf_juggler / perf_musician / perf_stilt), one
per phase band. The bird therefore passes the SAME three buskers through the whole
day. This pool RESTYLES those three as anchors and EXPANDS the human pool to ~8
distinct ACTS over a shared `_perf_body`-style drawer fed DATA rows (palette +
act/prop/pose flags), so the act reads by SILHOUETTE + PROP + POSE at near-deck
scale — exactly how the six shipped families work. The night festival LION/DRAGON
marquee is already strong and is OUT OF SCOPE here.

Eight busker ACTS, all over one shared body+action drawer:

  JUGGLER    (anchor) — standing, three balls on a small cascade arc.    DAY
  MUSICIAN   (anchor) — seated behind a barrel drum, hands beating.      GOLDEN
  STILT      (anchor) — robed figure raised on two tall stilts, arms up. DUSK
  CALLIGRAPHER (new)  — kneeling at a paper scroll, big brush sweeping.   MARKET
  TEA-POURER   (new)  — long-spout copper pot, an arcing kung-fu pour.    GOLDEN
  FORTUNE      (new)  — seated at a tiny table, a fan of bamboo sticks.   MARKET
  FAN-DANCER   (new)  — arc of silk fan / ribbon swept overhead.          GOLDEN
  MASK-CHANGER (new)  — bian-lian: bold opera face + a sweeping fan.      FESTIVAL

References studied first (web search):
  - Temple-fair calligraphers write "Fu" / couplets on a paper scroll laid on a
    low table, big upright brush in a sweeping stroke. -> kneeling-at-scroll act.
  - Sichuan kung-fu tea: a long-spout COPPER kettle poured in a dramatic high arc
    into a tiny cup, arm extended. -> the tea-pourer's arcing pour.
  - Temple-street fortune-tellers sit at a tiny table with a CUP of bamboo
    divination sticks (kau chim) / a small caged bird. -> the seated fortune act.
  - Bian-lian (Sichuan-opera face-changing): a vividly painted opera MASK swept by
    a fan, near-instant change. -> the bold-face mask-changer (a festival act).
  - Fan / ribbon dancers sweep a wide arc of silk overhead. -> the fan-dancer.

CONSTRAINTS (match the shipped families — non-negotiable):
  pure pygame.draw.* + Surface (SRCALPHA; BLEND_RGB_ADD only via a PRE-CLAMPED
  temp halo, mirroring props_cast._warm_halo, for the ONE lit act — the fortune
  candle); pygbag-safe, no numpy / gfxdraw / PIL. Authored at near-deck performer
  scale (body h≈18-20px; props/poses extend it), drawn CRISP (nearest). Each act
  shown at 2-3 representative t-phases so the action reads as motion, plus a true-
  near single + the on-street composite. Every lit pixel held <=NIGHT_GLOW_CAP=150
  luma after its additive halo, so NOTHING out-pops the gold coin (~230). Unlit
  acts cool toward (54,64,96) at night via the family _retint. Muted shan-shui
  palette consistent with the shipped families. Expressible as
  foreground_variants.Variant rows (palette + act/prop/pose flags).

Lane clearance: the module documents a bird lane (x≈48-188) + pillar lane
(x≈212-320); TALL acts (stilt, a raised tea-pour pot, a raised fan) carry a height
class so the orchestrator can keep the tall ones clear. Noted per act below.

Nothing here touches production game files; review-sheet generator only.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))


# ── shared colour helpers (lifted from props_cast / foreground_near_lane) ──────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


NIGHT_GLOW_CAP = 150
LIT_NIGHT_CEIL = 142


def _retint(col, night):
    """Cool a non-lit material toward the night ground band — the family contract
    (matches foreground_promenade._retint_person / props_cast._retint). The pull is
    partial so warm robes keep hue, but anything still over the cap is pushed harder
    so no busker pixel out-glows the coin at night."""
    if night <= 0.05:
        return col
    out = _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _hi(c, d, night):
    out = _shade(c, d)
    if night > 0.05 and _luma(out) > NIGHT_GLOW_CAP:
        out = _mix(out, (66, 76, 104), 0.65)
    return out


def _cap_to(col, ceil):
    """Hold a lit colour under `ceil` luma WITHOUT flattening hue (scales toward
    black, preserving the warm ratio that keeps the coin the sole brightest)."""
    y = _luma(col)
    if y <= ceil:
        return col
    k = ceil / y
    return (_clamp(col[0] * k), _clamp(col[1] * k), _clamp(col[2] * k))


def _cap_lum(color, night, *, cap=138, warm=True):
    """Pull a SOLID near-life highlight (drum head, mask face, brush ferrule) to
    <= cap LUMA at night while keeping a warm/ivory hue, so the brightest near
    busker pixel stays under the coin (mirrors foreground_near_lane._cap_lum)."""
    if night <= 0.05:
        return color
    r, g, b = color
    if warm:
        r, g, b = min(r, 150), min(g, 134), min(b, 112)
    lum = 0.2126 * r + 0.7152 * g + 0.1145 * b
    if lum > cap and lum > 0:
        f = cap / lum
        r, g, b = int(r * f), int(g * f), int(b * f)
    return (r, g, b)


# ── lit warmth: PRE-CLAMPED additive halo (props_cast._warm_halo idiom) ────────
#
# The ONLY lit prop in this family is the fortune-teller's candle. Its halo is the
# ONLY BLEND_RGB_ADD path: we bake the radial falloff into a temp surface and SCALE
# the whole field so its peak added luma is <=ADD_BUDGET BEFORE the single additive
# blit, so the candle core + halo can never sum past the cap (the props_cast model).

ADD_BUDGET = 70


def _warm_halo(surf, cx, cy, *, radius, peak, color):
    col = _cap_to(color, LIT_NIGHT_CEIL)
    d = radius * 2 + 2
    cxr = cyr = radius + 1
    acc = [[0.0, 0.0, 0.0] for _ in range(d * d)]
    for rr in range(radius, 0, -1):
        w = peak * (rr / radius) * (1.0 - rr / radius) * 4.0 / 255.0
        if w <= 0:
            continue
        k = rr / radius
        c = (col[0] * (0.5 + 0.5 * (1 - k)),
             col[1] * (0.5 + 0.5 * (1 - k)),
             col[2] * (0.5 + 0.5 * (1 - k)))
        rr2 = rr * rr
        for py in range(d):
            dy = py - cyr
            for px in range(d):
                dx = px - cxr
                if dx * dx + dy * dy <= rr2:
                    cell = acc[py * d + px]
                    cell[0] += c[0] * w
                    cell[1] += c[1] * w
                    cell[2] += c[2] * w
    peak_add = 0.0
    for cell in acc:
        peak_add = max(peak_add, _luma(cell))
    scale = (ADD_BUDGET / peak_add) if peak_add > ADD_BUDGET else 1.0
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    for py in range(d):
        for px in range(d):
            cell = acc[py * d + px]
            if cell[0] + cell[1] + cell[2] <= 0:
                continue
            g.set_at((px, py), (_clamp(cell[0] * scale), _clamp(cell[1] * scale),
                                _clamp(cell[2] * scale), 255))
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


# ════════════════════════════════════════════════════════════════════════════
# THE SHARED BODY + ACTION DRAWER.
#
# `_perf_body` mirrors the production foreground_near_lane._perf_body (block-wedge
# torso, round head, hair cap, posable arms) at near-deck scale, retinted per
# night. Every busker act is then drawn by `draw_act`, which selects a POSE for the
# body (standing / kneeling / seated / stilted) + the act's PROP, all from the
# Variant's palette + act/prop/pose flags — DATA, not a bespoke fn per act.
#
# act flags (v.attrs):
#   act='juggler'|'musician'|'stilt'|'calligrapher'|'teapour'|'fortune'|
#       'fandance'|'maskchange'
#   pose='stand'|'kneel'|'seat'|'stilt'      arms='down'|'up'|'drum'|'juggle'|
#       'reach'|'brush'|'sweep'              prop=<act prop tag>
#   h, w  body box;   lit=bool (fortune candle)
# palette roles: robe, robe_dk, hair, accent (sash/trim), prop_a, prop_b
# ════════════════════════════════════════════════════════════════════════════

SKIN = (232, 192, 150)


def _perf_body(surf, x, feet_y, robe, robe_dk, hair, night, *, h=18, w=9,
               lean=0, arms='down', arm_t=0.0, pose='stand', accent=None):
    """A near-scale performer torso + head with posable arms + a chosen lower-body
    POSE. Returns (head_x, head_y, shoulder_y) so the act can hang a prop / hat /
    sash off it. Skin + robe are retinted at night so no face out-shines the cap."""
    skin = _retint(SKIN, night)
    body_y = feet_y - h

    if pose == 'kneel':
        # KNEELING: the torso sits low over folded shins — a compact crouch that
        # reads instantly different from the standing busker silhouette.
        seat_y = feet_y - 1
        pygame.draw.polygon(surf, _shade(robe_dk, -10), [
            (x - 7, seat_y), (x + 7, seat_y), (x + 5, seat_y - 4), (x - 5, seat_y - 4)])
        torso_top = seat_y - 4 - (h - 8)
        pygame.draw.polygon(surf, robe, [
            (x - w // 2 + lean, torso_top), (x + w // 2 + lean, torso_top),
            (x + w // 2, seat_y - 4), (x - w // 2, seat_y - 4)])
        pygame.draw.polygon(surf, robe_dk, [
            (x - w // 2 + lean, torso_top), (x + w // 2 + lean, torso_top),
            (x + w // 2, seat_y - 4), (x - w // 2, seat_y - 4)], 1)
        body_y = torso_top
        feet_floor = seat_y - 4
    elif pose == 'seat':
        # SEATED on the deck, knees forward (the spectator idiom) — used for the
        # seated drum musician + the fortune-teller at the low table.
        seat_y = feet_y - 1
        pygame.draw.polygon(surf, _shade(robe_dk, -10), [
            (x - 7, seat_y), (x + 7, seat_y), (x + 5, seat_y - 5), (x - 5, seat_y - 5)])
        torso_top = seat_y - 5 - (h - 9)
        pygame.draw.rect(surf, robe, (x - w // 2 + lean, torso_top, w, seat_y - 5 - torso_top))
        pygame.draw.rect(surf, robe_dk, (x - w // 2 + lean, torso_top, w, seat_y - 5 - torso_top), 1)
        body_y = torso_top
        feet_floor = seat_y - 5
    else:  # 'stand' / 'stilt' — full standing wedge
        pygame.draw.polygon(surf, robe, [
            (x - w // 2 + lean, body_y), (x + w // 2 + lean, body_y),
            (x + w // 2 + 1, feet_y), (x - w // 2 - 1, feet_y)])
        pygame.draw.polygon(surf, robe_dk, [
            (x - w // 2 + lean, body_y), (x + w // 2 + lean, body_y),
            (x + w // 2 + 1, feet_y), (x - w // 2 - 1, feet_y)], 1)
        leg = _shade(robe_dk, -14)
        pygame.draw.line(surf, leg, (x - 2 + lean, feet_y - 5), (x - 3, feet_y), 2)
        pygame.draw.line(surf, leg, (x + 2 + lean, feet_y - 5), (x + 3, feet_y), 2)
        feet_floor = feet_y

    # a sash / waist accent so robes read with a belt (a shan-shui colour break)
    if accent is not None and pose in ('stand', 'stilt'):
        pygame.draw.line(surf, accent, (x - w // 2 + lean, body_y + h // 2),
                         (x + w // 2 + lean, body_y + h // 2), 2)

    hx, hy = x + lean, body_y - 4
    pygame.draw.circle(surf, skin, (hx, hy), 4)
    pygame.draw.arc(surf, hair, (hx - 4, hy - 5, 9, 9),
                    math.radians(0), math.radians(180), 3)
    pygame.draw.circle(surf, (30, 20, 15), (hx - 1, hy), 0)
    pygame.draw.circle(surf, (30, 20, 15), (hx + 1, hy), 0)

    # Arms per pose-action. Each returns its hand point(s) so a prop pins to a hand.
    sh_y = body_y + 3
    swing = max(0.0, math.sin(arm_t))
    hands = []
    if arms == 'up':
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            ex, ey = ax + dx * 4, sh_y - 7 - int(swing * 3)
            pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
            hands.append((ex, ey))
    elif arms == 'drum':
        for dx, ph in ((-1, 0.0), (1, math.pi)):
            ax = x + (w // 2) * dx + lean
            lift = int(max(0.0, math.sin(arm_t + ph)) * 4)
            ex, ey = ax + dx * 5, sh_y + 4 - lift
            pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
            hands.append((ex, ey))
    elif arms == 'juggle':
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            ex, ey = ax + dx * 5, sh_y - 4
            pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
            hands.append((ex, ey))
    elif arms == 'reach':
        # one arm extended HIGH out to the side (tea pour / pour-into-cup), the
        # other low — an asymmetric reach that reads as a controlled pour.
        ax = x + (w // 2) + lean
        ex, ey = ax + 7, sh_y - 6 - int(swing * 2)
        pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
        hands.append((ex, ey))
        ax2 = x - (w // 2) + lean
        ex2, ey2 = ax2 - 4, sh_y + 5
        pygame.draw.line(surf, robe, (ax2, sh_y), (ex2, ey2), 2)
        hands.append((ex2, ey2))
    elif arms == 'brush':
        # both forearms forward + DOWN to a scroll on the deck, the dominant hand
        # sweeping a stroke (a calligrapher's downward brush motion).
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            reach = 6 if dx > 0 else 3
            ex, ey = ax + dx * reach, sh_y + 6 + int(swing * 2 if dx > 0 else 0)
            pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
            hands.append((ex, ey))
    elif arms == 'sweep':
        # one arm sweeping a wide ARC overhead (fan/ribbon dancer, mask fan), the
        # sweep angle driven by arm_t so the silk/fan traces a moving arc.
        ax = x + (w // 2) + lean
        ang = math.radians(40 + 80 * (0.5 + 0.5 * math.sin(arm_t)))
        ex, ey = ax + int(math.cos(ang) * 9), sh_y - int(math.sin(ang) * 9)
        pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
        hands.append((ex, ey))
        ax2 = x - (w // 2) + lean
        ex2, ey2 = ax2 - 4, sh_y + 4
        pygame.draw.line(surf, robe, (ax2, sh_y), (ex2, ey2), 2)
        hands.append((ex2, ey2))
    else:  # down
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            ex, ey = ax + dx * 3, sh_y + 6
            pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
            hands.append((ex, ey))
    return hx, hy, sh_y, hands, feet_floor


def draw_act(surf, sx, base_y, v, night, t):
    """Render ONE busker act from a Variant row (palette + act/prop/pose flags)
    over the shared `_perf_body`. The act tag selects the prop drawn around the
    posed body; the body itself is shared. Authored feet-on-`base_y`."""
    P, A = v.palette, v.attrs
    act = A.get("act", "juggler")
    robe = _retint(P.get("robe", (196, 92, 70)), night)
    robe_dk = _retint(P.get("robe_dk", (150, 60, 52)), night)
    hair = _retint(P.get("hair", (70, 50, 40)), night)
    accent = _retint(P["accent"], night) if "accent" in P else None
    h = A.get("h", 19)
    w = A.get("w", 9)
    feet = int(base_y)

    if act == "juggler":
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='stand', arms='juggle', arm_t=t * 3.0, accent=accent)
        # three hot primaries on a small cascade arc above the hands.
        ball_cols = (P.get("prop_a", (255, 176, 16)), (240, 44, 40), (32, 132, 248))
        for i, col in enumerate(ball_cols):
            ph = (t * 1.6 + i / 3.0) % 1.0
            bx = sx + int(math.sin(ph * math.tau) * 9)
            by = hy - 4 - int(math.sin(ph * math.pi) * 13)
            col = _retint(col, night)
            pygame.draw.circle(surf, _shade(col, -24), (bx, by), 5)
            pygame.draw.circle(surf, col, (bx, by), 4)
            pygame.draw.circle(surf, _shade(col, 48), (bx - 1, by - 1), 2)

    elif act == "musician":
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx + 6, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='seat', arms='drum', arm_t=t * 4.5, accent=accent)
        # a barrel drum stood on the deck in front of the seated musician.
        dx, dy = sx - 5, feet
        drum = _mix(P.get("prop_a", (150, 60, 45)), (70, 70, 96), 0.30 * night)
        pygame.draw.ellipse(surf, _shade(drum, -24), (dx - 11, dy - 20, 22, 20))
        pygame.draw.ellipse(surf, drum, (dx - 10, dy - 19, 20, 18))
        head_col = _cap_lum((205, 182, 145), night)
        pygame.draw.ellipse(surf, head_col, (dx - 9, dy - 19, 18, 6))
        pygame.draw.ellipse(surf, _shade(head_col, -26), (dx - 9, dy - 19, 18, 6), 1)
        tack = _cap_lum((180, 150, 90), night)
        for ti in range(-2, 3):
            pygame.draw.circle(surf, tack, (dx + ti * 5, dy - 12), 1)
        for ph in (0.0, math.pi):
            lift = int(max(0.0, math.sin(t * 4.5 + ph)) * 5)
            hxh = dx + (4 if ph else -4)
            pygame.draw.line(surf, robe, (sx + 3, feet - 14), (hxh, dy - 18 - lift), 2)

    elif act == "stilt":
        # raised on two tall stilts; the body sits a stilt-height up the deck. TALL.
        stilt_h = A.get("stilt_h", 24)
        sway = int(math.sin(t * 1.6) * 1)
        body_feet = feet - stilt_h
        pole = _shade(_retint(P.get("prop_a", (110, 78, 48)), night), -6)
        for dx in (-3, 3):
            pygame.draw.line(surf, pole, (sx + dx + sway, body_feet), (sx + dx, feet), 2)
        _perf_body(surf, sx + sway, body_feet, robe, robe_dk, hair, night,
                   h=h, w=w, pose='stand', arms='up', arm_t=t * 2.0, accent=accent)

    elif act == "calligrapher":
        # KNEELING over a paper scroll on a low board, a big upright brush in a
        # downward sweeping stroke. Low, wide silhouette.
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='kneel', arms='brush', arm_t=t * 2.2, accent=accent, lean=2)
        # the paper scroll laid on the deck in front of the kneeling figure.
        paper = _cap_lum(P.get("prop_a", (224, 214, 190)), night, warm=False)
        scroll = pygame.Rect(sx + 4, feet - 4, 20, 4)
        pygame.draw.rect(surf, _shade(paper, -16), scroll)
        pygame.draw.rect(surf, paper, scroll.inflate(-2, -1))
        # rolled ends (dowels)
        dowel = _retint(P.get("prop_b", (120, 84, 50)), night)
        pygame.draw.rect(surf, dowel, (sx + 3, feet - 5, 2, 6))
        pygame.draw.rect(surf, dowel, (sx + 23, feet - 5, 2, 6))
        # fresh ink strokes appearing on the paper
        ink = _retint((40, 30, 26), night)
        for mi in range(3):
            mx = sx + 8 + mi * 5
            pygame.draw.line(surf, ink, (mx, feet - 3), (mx + 2, feet - 1), 1)
        # the big brush: a dark shaft from the writing hand down to the paper, with
        # a pale ferrule + a dark tuft tip just touching the scroll.
        hand = hands[1] if len(hands) > 1 else (sx + 6, sh_y)
        tip_x = sx + 8 + int(max(0.0, math.sin(t * 2.2)) * 6)
        tip_y = feet - 2
        shaft = _retint(P.get("prop_b", (120, 84, 50)), night)
        pygame.draw.line(surf, shaft, (hand[0], hand[1]), (tip_x, tip_y - 3), 2)
        pygame.draw.circle(surf, _cap_lum((220, 210, 196), night, warm=False),
                           (tip_x, tip_y - 3), 1)  # ferrule
        pygame.draw.line(surf, (28, 22, 20), (tip_x, tip_y - 3), (tip_x, tip_y), 2)  # tuft

    elif act == "teapour":
        # standing, one arm raised HIGH holding a long-spout copper pot, an arcing
        # stream pouring down into a tiny cup on a low stand. TALL (raised pot).
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='stand', arms='reach', arm_t=t * 1.6, accent=accent, lean=1)
        hand = hands[0] if hands else (sx + 9, sh_y - 7)
        copper = _retint(P.get("prop_a", (188, 120, 64)), night)
        copper_lt = _hi(copper, 26, night)
        # the pot body in the raised hand
        pot = pygame.Rect(hand[0] - 4, hand[1] - 3, 9, 7)
        pygame.draw.ellipse(surf, _shade(copper, -22), pot)
        pygame.draw.ellipse(surf, copper, pot.inflate(-2, -2))
        pygame.draw.arc(surf, copper_lt, pot, math.radians(30), math.radians(120), 1)
        # the LONG curved spout sweeping down toward the cup — the act's signature.
        cup_x, cup_y = sx - 9, feet - 3
        spout_pts = []
        for i in range(7):
            tt = i / 6
            bx = (1 - tt) ** 2 * (hand[0] - 4) + 2 * (1 - tt) * tt * (sx - 2) + tt * tt * (cup_x + 1)
            by = (1 - tt) ** 2 * (hand[1]) + 2 * (1 - tt) * tt * (hand[1] + 4) + tt * tt * (cup_y - 8)
            spout_pts.append((int(bx), int(by)))
        pygame.draw.lines(surf, copper, False, spout_pts, 2)
        pygame.draw.lines(surf, copper_lt, False, spout_pts[:3], 1)
        # the arcing water stream from spout tip to cup
        stream = _cap_lum(P.get("prop_b", (180, 206, 214)), night, warm=False)
        sp_tip = spout_pts[-1]
        for i in range(5):
            tt = i / 4
            wx = sp_tip[0] + (cup_x - sp_tip[0]) * tt
            wy = sp_tip[1] + (cup_y - sp_tip[1]) * tt + math.sin(tt * math.pi) * 2
            pygame.draw.circle(surf, stream, (int(wx), int(wy)), 1)
        # the tiny cup on a low stand
        clay = _retint((158, 116, 80), night)
        pygame.draw.rect(surf, _shade(clay, -20), (cup_x - 4, feet - 5, 8, 5))
        pygame.draw.ellipse(surf, clay, (cup_x - 3, cup_y - 2, 7, 4))
        pygame.draw.ellipse(surf, _shade(clay, -22), (cup_x - 3, cup_y - 2, 7, 4), 1)

    elif act == "fortune":
        # SEATED at a tiny table; a cup of bamboo divination sticks (kau chim) +
        # a small candle (the ONE lit act). Compact, low silhouette.
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx + 7, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='seat', arms='down', arm_t=t, accent=accent, lean=-1)
        # the tiny low table in front.
        wood = _retint(P.get("prop_b", (120, 86, 52)), night)
        wood_dk = _shade(wood, -22)
        tbl_y = feet - 8
        pygame.draw.rect(surf, wood_dk, (sx - 11, tbl_y, 16, 3))
        pygame.draw.rect(surf, wood, (sx - 11, tbl_y, 16, 2))
        for lx in (sx - 10, sx + 2):
            pygame.draw.line(surf, wood_dk, (lx, tbl_y + 3), (lx, feet - 1), 2)
        # the cup of bamboo fortune sticks fanning up.
        cup = _retint(P.get("prop_a", (150, 70, 56)), night)
        pygame.draw.rect(surf, _shade(cup, -20), (sx - 7, tbl_y - 5, 7, 6))
        pygame.draw.rect(surf, cup, (sx - 6, tbl_y - 5, 5, 5))
        stick = _cap_lum((196, 178, 132), night)
        for si, ang in enumerate((-18, -6, 6, 18)):
            ex = sx - 4 + int(math.sin(math.radians(ang)) * 6)
            ey = tbl_y - 5 - int(math.cos(math.radians(ang)) * 8) - (si % 2)
            pygame.draw.line(surf, stick, (sx - 4, tbl_y - 4), (ex, ey), 1)
        # small candle on the table (the lit accent) — capped core + clamped halo.
        cdx, cdy = sx + 2, tbl_y - 1
        wax = _retint((212, 200, 176), night)
        pygame.draw.rect(surf, wax, (cdx - 1, cdy - 4, 3, 4))
        if night > 0.05:
            flame = _cap_to((236, 196, 120), LIT_NIGHT_CEIL)
            pygame.draw.circle(surf, flame, (cdx, cdy - 5), 1)
            _warm_halo(surf, cdx, cdy - 5, radius=7, peak=30, color=(236, 188, 120))
        else:
            pygame.draw.circle(surf, (238, 196, 120), (cdx, cdy - 5), 1)

    elif act == "fandance":
        # standing, sweeping a wide ARC of silk fan / ribbon overhead — the most
        # gestural silhouette. The arc traces a curve that moves with t.
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='stand', arms='sweep', arm_t=t * 1.8, accent=accent, lean=1)
        hand = hands[0] if hands else (sx + 9, sh_y - 6)
        silk = _retint(P.get("prop_a", (224, 110, 130)), night)
        silk_lt = _hi(silk, 24, night)
        # a fan of ribs spread from the sweeping hand (the silk fan), the spread
        # angle following the sweep so it reads as a fan caught mid-arc.
        base_ang = math.atan2(hand[1] - sh_y, hand[0] - sx)
        rib_pts = [hand]
        for k in range(-2, 3):
            a = base_ang + math.radians(k * 16)
            ex = hand[0] + int(math.cos(a) * 8)
            ey = hand[1] + int(math.sin(a) * 8)
            pygame.draw.line(surf, silk, (hand[0], hand[1]), (ex, ey), 1)
            rib_pts.append((ex, ey))
        pygame.draw.polygon(surf, silk, rib_pts[1:])
        pygame.draw.polygon(surf, silk_lt, rib_pts[1:], 1)
        # a trailing ribbon ARC sweeping off the fan tip
        ribbon = _hi(silk, 12, night)
        tip = rib_pts[-1]
        arc_pts = []
        for i in range(6):
            tt = i / 5
            ax2 = tip[0] - tt * 14 + math.sin(t * 2.0 + tt * 4) * 2
            ay2 = tip[1] - 2 + math.sin(tt * math.pi + t) * 5
            arc_pts.append((int(ax2), int(ay2)))
        pygame.draw.lines(surf, ribbon, False, arc_pts, 1)

    else:  # 'maskchange' — bian-lian: a bold painted opera face + a sweeping fan
        # standing in an opera-robe, a BOLD vivid mask over the head, a fan swept
        # across — the festival show-stopper. The mask colour swaps with t to hint
        # the face-change.
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='stand', arms='sweep', arm_t=t * 2.4, accent=accent)
        # the bold opera MASK painted over the head — a near-life solid highlight,
        # so it's the act's brightest pixel and is luma-capped at night.
        mask_cols = (P.get("prop_a", (216, 70, 64)),
                     P.get("prop_b", (70, 110, 170)),
                     (228, 200, 110))
        mc = mask_cols[int(t * 1.5) % len(mask_cols)]
        mc = _cap_lum(mc, night)
        pygame.draw.circle(surf, mc, (hx, hy), 4)
        # bold opera-paint marks: dark brow sweep + a vertical forehead stripe
        ink = _retint((30, 24, 22), night)
        pygame.draw.line(surf, ink, (hx - 3, hy - 1), (hx + 3, hy - 1), 1)
        pygame.draw.line(surf, ink, (hx, hy - 3), (hx, hy + 1), 1)
        pygame.draw.circle(surf, _cap_lum((240, 232, 214), night, warm=False), (hx - 1, hy), 0)
        pygame.draw.circle(surf, _cap_lum((240, 232, 214), night, warm=False), (hx + 1, hy), 0)
        # a small crest / headdress nub
        crest = _cap_lum(P.get("prop_b", (228, 200, 110)), night)
        pygame.draw.circle(surf, crest, (hx, hy - 5), 1)
        # the sweeping fan that triggers the change
        hand = hands[0] if hands else (sx + 9, sh_y - 6)
        fan = _retint((40, 36, 38), night)
        base_ang = math.atan2(hand[1] - sh_y, hand[0] - sx)
        fpts = [hand]
        for k in range(-2, 3):
            a = base_ang + math.radians(k * 14)
            fpts.append((hand[0] + int(math.cos(a) * 7), hand[1] + int(math.sin(a) * 7)))
        pygame.draw.polygon(surf, fan, fpts[1:])
        pygame.draw.polygon(surf, _hi(fan, 30, night), fpts[1:], 1)


# ════════════════════════════════════════════════════════════════════════════
# THE POOL — foreground_variants.Variant rows (DATA, not bespoke functions).
# Each tuple: (label, Variant, beat, height-class, annotation).
# ════════════════════════════════════════════════════════════════════════════

class _V:
    def __init__(self, palette, *, attrs=None):
        self.palette = palette
        self.attrs = dict(attrs or {})


def _row(palette, **attrs):
    return _V(dict(palette), attrs=attrs)


# H = HALF-HEIGHT (sits under the lanes, body+prop reach ~feet-26); T = TALL (a
# raised pole/pot/fan reaches higher and wants a clear horizontal zone).
ACTS = [
    ("A1 juggler (anchor)",
     _row(dict(robe=(196, 92, 70), robe_dk=(150, 60, 52), hair=(70, 50, 40),
               accent=(208, 176, 96), prop_a=(255, 176, 16)),
          act="juggler", pose="stand", arms="juggle", h=20, w=9),
     "DAY", "H",
     "act:juggler pose:stand arms:juggle | robe terracotta(196,92,70) sash gold(208,176,96) balls hot primaries | RESTYLED anchor: added a gold waist sash so the body reads richer. 3 balls on a sine cascade. NIGHT: robe cools to (54,64,96), balls retint. beat: DAY"),

    ("A2 musician (anchor)",
     _row(dict(robe=(90, 110, 160), robe_dk=(58, 74, 116), hair=(60, 45, 40),
               accent=(196, 170, 96), prop_a=(150, 60, 45)),
          act="musician", pose="seat", arms="drum", h=18, w=9),
     "GOLDEN", "H",
     "act:musician pose:seat arms:drum | indigo robe(90,110,160) barrel drum(150,60,45) ivory head capped | RESTYLED anchor over the shared seated pose: drum head _cap_lum, hands beat mid-swing. beat: GOLDEN-HOUR"),

    ("A3 stilt-walker (anchor)",
     _row(dict(robe=(150, 70, 130), robe_dk=(100, 44, 92), hair=(60, 45, 40),
               accent=(220, 196, 110), prop_a=(110, 78, 48)),
          act="stilt", pose="stilt", arms="up", h=18, w=8, stilt_h=24),
     "DUSK", "T",
     "act:stilt pose:stilt arms:up stilt_h:24 | magenta festival robe(150,70,130) wood stilts | RESTYLED anchor: a gold sash added. TALL — body raised 24px on two stilts; keep clear of bird/pillar lanes. beat: DUSK"),

    ("A4 calligrapher",
     _row(dict(robe=(120, 130, 120), robe_dk=(84, 96, 88), hair=(54, 46, 40),
               accent=(60, 56, 52), prop_a=(224, 214, 190), prop_b=(120, 84, 50)),
          act="calligrapher", pose="kneel", arms="brush", h=18, w=10),
     "MARKET", "H",
     "act:calligrapher pose:kneel arms:brush | sage scholar-robe(120,130,120) paper(224,214,190) brush shaft(120,84,50) | NEW: kneels low at a paper scroll, big upright brush in a downward sweep, fresh ink dabs appear. LOW wide crouch silhouette. NIGHT: paper _cap_lum so it never out-pops the coin. beat: MARKET / MORNING"),

    ("A5 tea-pourer",
     _row(dict(robe=(170, 80, 60), robe_dk=(122, 54, 44), hair=(56, 44, 38),
               accent=(214, 190, 110), prop_a=(190, 122, 64), prop_b=(186, 210, 218)),
          act="teapour", pose="stand", arms="reach", h=19, w=9),
     "GOLDEN", "T",
     "act:teapour pose:stand arms:reach | rust robe(170,80,60) COPPER long-spout pot(190,122,64) water arc(186,210,218) | NEW: kung-fu tea — arm raised HIGH, a long curved spout sweeping down to a tiny cup, an arcing water stream. TALL (raised pot reaches ~feet-30). NIGHT: copper retints, water _cap_lum. beat: GOLDEN-HOUR / MARKET"),

    ("A6 fortune-teller",
     _row(dict(robe=(78, 92, 120), robe_dk=(52, 64, 88), hair=(58, 50, 44),
               accent=(150, 130, 90), prop_a=(150, 70, 56), prop_b=(120, 86, 52)),
          act="fortune", pose="seat", arms="down", h=18, w=9, lit=True),
     "MARKET", "H",
     "act:fortune pose:seat arms:down lit:candle | slate-blue robe(78,92,120) stick-cup(150,70,56) low table(120,86,52) | NEW: seated at a tiny table, a cup of bamboo divination sticks (kau chim) fanning up + a small CANDLE — the family's ONE lit prop. Candle core _cap_to + a PRE-CLAMPED additive halo (props_cast model), <=142 luma. beat: MARKET / DUSK"),

    ("A7 fan / ribbon dancer",
     _row(dict(robe=(210, 120, 150), robe_dk=(160, 80, 110), hair=(50, 40, 38),
               accent=(232, 206, 120), prop_a=(224, 110, 130)),
          act="fandance", pose="stand", arms="sweep", h=19, w=8),
     "GOLDEN", "T",
     "act:fandance pose:stand arms:sweep | rose robe(210,120,150) silk fan + ribbon(224,110,130) | NEW: sweeps a wide silk FAN + trailing ribbon ARC overhead, the arc tracing a t-driven curve. TALL-ish (the raised sweep reaches ~feet-28). NIGHT: silk cools. beat: GOLDEN-HOUR / FESTIVAL"),

    ("A8 mask-changer (bian-lian)",
     _row(dict(robe=(90, 60, 120), robe_dk=(62, 42, 86), hair=(40, 34, 38),
               accent=(228, 196, 96), prop_a=(216, 70, 64), prop_b=(70, 110, 170)),
          act="maskchange", pose="stand", arms="sweep", h=19, w=9),
     "FESTIVAL", "H",
     "act:maskchange pose:stand arms:sweep | violet opera-robe(90,60,120) BOLD mask swaps red(216,70,64)/blue(70,110,170)/gold gold crest | NEW: Sichuan-opera face-changing — a vivid mask over the head that SWAPS colour with t (the change), a dark fan sweeping across. Mask is the brightest pixel -> _cap_lum at night. beat: FESTIVAL / DUSK"),
]


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (matches the shipped-family round house style)
# ════════════════════════════════════════════════════════════════════════════

WIDTH = 1340
PAD = 12
BG_DAY = (150, 140, 118)
BG_GOLD = (176, 138, 92)
BG_NIGHT = (40, 46, 70)


def _font(sz, bold=False):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _text(surf, s, x, y, sz=11, col=(228, 224, 214), bold=False):
    surf.blit(_font(sz, bold).render(s, True, col), (x, y))


def _gold_coin(surf, cx, cy, r=8):
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, (255, 232, 150))):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(9, True).render("$", True, (150, 100, 20)), (cx - 3, cy - 6))


def _adult_ref(surf, cx, base_y, night):
    """A coarse adult-pedestrian yardstick so a busker reads at near-deck scale
    next to a passer-by (taller raised acts read clearly above the head)."""
    pf = lambda c: _retint(c, night)
    coat = pf((96, 104, 140)); coat_dk = _shade(coat, -40)
    skin = pf((222, 178, 132)); hair = pf((52, 42, 34))
    g = int(base_y)
    head_r = 4; torso_h = 13
    torso_top = g - 8 - torso_h
    for sgn in (-1, 1):
        pygame.draw.line(surf, coat_dk, (cx + sgn * 2, torso_top + torso_h), (cx + sgn * 2, g), 2)
    pygame.draw.polygon(surf, coat, [(cx - 4, torso_top), (cx + 4, torso_top),
                                     (cx + 5, torso_top + torso_h), (cx - 5, torso_top + torso_h)])
    pygame.draw.circle(surf, skin, (cx, torso_top - head_r), head_r)
    pygame.draw.circle(surf, hair, (cx, torso_top - head_r - 1), head_r)


def _stall_ref(surf, cx, base_y, night):
    """A coarse food-stall booth stand-in for the composite, echoing food_stalls."""
    pf = lambda c: _retint(c, night)
    g = int(base_y)
    post = pf((120, 88, 56)); awn1 = pf((176, 86, 74)); awn2 = pf((212, 196, 170))
    w, h = 48, 34
    for px in (cx - w // 2, cx + w // 2):
        pygame.draw.line(surf, post, (px, g), (px, g - h), 2)
    pygame.draw.rect(surf, pf((150, 132, 104)), (cx - w // 2, g - 9, w, 9))
    ay = g - h
    for i in range(w // 6):
        c = awn1 if i % 2 == 0 else awn2
        pygame.draw.polygon(surf, c, [
            (cx - w // 2 + i * 6, ay), (cx - w // 2 + (i + 1) * 6, ay),
            (cx - w // 2 + (i + 1) * 6, ay + 4), (cx - w // 2 + i * 6 + 3, ay + 7),
            (cx - w // 2 + i * 6, ay + 4)])
    pygame.draw.rect(surf, post, (cx - w // 2 - 1, ay - 2, w + 2, 3))


def _bg_for(night, gold):
    if night > 0.5:
        return BG_NIGHT
    return BG_GOLD if gold else BG_DAY


def _cell(parent, label, v, note, beat, hcls, x, y, w, h, night, gold=False):
    """One annotated act cell: a COLUMN of 2-3 pose t-phases (the action reading as
    motion) at true-near size + a 4x WORKING nearest zoom + an adult yardstick +
    in-cell coin, on a day/golden/night deck, with the act/prop/pose flags note."""
    bg = _bg_for(night, gold)
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 14
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    # the act at THREE t-phases so the action reads as motion.
    fx0 = 40
    for i, tt in enumerate((0.15, 0.75, 1.45)):
        cxp = fx0 + i * 50
        draw_act(cell, cxp, base, v, night, tt)
    _text(cell, "true-near · 3 t-phases (motion)", fx0 - 26, base + 2, 8, _shade(bg, 50))

    # WORKING zoom inset — native box sized to a tall act, NEAREST scaled crisp.
    SC_W, SC_H = 46, 56
    nat = pygame.Surface((SC_W, SC_H), pygame.SRCALPHA)
    deck_y = SC_H - 4
    nat.fill((*_mix(bg, (0, 0, 0), 0.18), 130), (0, deck_y, SC_W, SC_H - deck_y))
    draw_act(nat, SC_W // 2, deck_y, v, night, 0.7)
    z = 4
    zoom = pygame.transform.scale(nat, (SC_W * z, SC_H * z))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 20
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)
    _text(cell, "4x zoom (nearest)", zx, zy - 12, 8, _shade(bg, 60))

    # an adult yardstick + coin so scale + brightness read in-cell
    _adult_ref(cell, fx0 + 156, base, night)
    _text(cell, "adult", fx0 + 144, base + 2, 8, _shade(bg, 50))
    _gold_coin(cell, fx0 + 156, 28, r=6)

    _text(cell, label, 6, 4, 12, (240, 236, 226), bold=True)
    _text(cell, "beat:" + beat + "  height:" + ("TALL" if hcls == "T" else "half"),
          6, 18, 9, (250, 224, 150) if hcls == "T" else (180, 210, 180), bold=True)
    fnt = _font(9, False)
    line = ""; yy = 31
    wrap_w = zx - 14
    for wd in note.split(" "):
        test = (line + " " + wd).strip()
        if fnt.size(test)[0] > wrap_w:
            cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy)); yy += 11; line = wd
        else:
            line = test
    if line:
        cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy))

    parent.blit(cell, (x, y))
    pygame.draw.rect(parent, (70, 74, 90), (x, y, w, h), 1)


def _true_band(sheet, y, title, night, gold=False):
    """A true-near band of ALL acts with an adult + coin yardstick, so the cast's
    silhouette variety + scale read in one row."""
    _text(sheet, title, PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    band_h = 84
    row = pygame.Surface((WIDTH - PAD * 2, band_h))
    bg = _bg_for(night, gold)
    row.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = band_h - 12
    pygame.draw.rect(row, deck, (0, base, WIDTH - PAD * 2, 12))
    pygame.draw.line(row, _shade(bg, 26), (0, base), (WIDTH - PAD * 2, base), 1)
    _adult_ref(row, 32, base, night)
    _text(row, "adult", 18, base + 1, 8, _shade(bg, 50))
    _gold_coin(row, WIDTH - PAD * 2 - 18, base - 48)
    _text(row, "coin", WIDTH - PAD * 2 - 36, base - 36, 8, _shade(bg, 50))
    spacing = (WIDTH - PAD * 2 - 150) // len(ACTS)
    for i, (nm, v, beat, hcls, _n) in enumerate(ACTS):
        cx = 96 + i * spacing
        draw_act(row, cx, base, v, night, 0.4 + i * 0.5)
        _text(row, nm.split(" ")[0], cx - 8, base + 1, 8,
              (70, 58, 46) if night <= 0.5 else (150, 160, 185))
        if hcls == "T":
            _text(row, "TALL", cx - 10, 4, 8, (210, 130, 90), bold=True)
    sheet.blit(row, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, band_h), 1)
    return y + band_h + 6


def _measure_night_cap():
    """Render every act onto a night strip across t-phases, then scan the RENDERED
    pixels for the hottest busker luma — the honest cap audit the footer prints.
    The fortune candle's core + its additive halo are included."""
    night = 0.95
    strip = pygame.Surface((1700, 96))
    strip.fill(BG_NIGHT)
    base = 80
    x = 60
    for _nm, v, _b, _h, _n in ACTS:
        for tt in (0.0, 0.6, 1.3):
            draw_act(strip, x, base, v, night, tt)
            x += 40
        x += 18
    hottest = 0.0
    over = 0
    bg_l = _luma(BG_NIGHT)
    for px in range(strip.get_width()):
        for py in range(strip.get_height()):
            c = strip.get_at((px, py))[:3]
            l = _luma(c)
            if abs(l - bg_l) < 1.5:
                continue
            hottest = max(hottest, l)
            if l > NIGHT_GLOW_CAP:
                over += 1
    return hottest, over


def _composite(sheet, y, strip_h, night, gold, label):
    """An on-street strip mixing several buskers among passing pedestrians + a
    stall + the coin reference for scale, ordered so adjacent silhouettes contrast.
    The beat-appropriate acts are foregrounded per band (day/golden/night)."""
    bg = _bg_for(night, gold)
    strip = pygame.Surface((WIDTH - PAD * 2, strip_h))
    strip.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.2)
    base = strip_h - 16
    pygame.draw.rect(strip, deck, (0, base, WIDTH - PAD * 2, strip_h - base))
    pygame.draw.line(strip, _shade(bg, 24), (0, base), (WIDTH - PAD * 2, base), 1)
    sw = WIDTH - PAD * 2

    def act(name):
        return next(v for nm, v, _b, _h, _n in ACTS if nm.startswith(name))

    if night > 0.5:
        order = ["A8", "A6", "A4", "A7", "A2", "A3", "A1"]
    elif gold:
        order = ["A5", "A7", "A2", "A1", "A4", "A6", "A8"]
    else:
        order = ["A4", "A6", "A1", "A5", "A2", "A7", "A3"]

    x = 64
    for i, tag in enumerate(order):
        v = act(tag)
        draw_act(strip, x, base, v, night, 0.3 + i * 0.6)
        if i % 2 == 1:
            _adult_ref(strip, x + 30, base, night)
        if i == 2:
            _stall_ref(strip, x + 56, base, night)
            x += 50
        x += 92
    _gold_coin(strip, sw - 18, 20)
    _text(strip, "coin ref", sw - 46, 32, 8, _shade(bg, 60))
    _text(strip, label, 4, 2, 9,
          (170, 190, 225) if night > 0.5 else (60, 50, 40), bold=True)
    sheet.blit(strip, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, WIDTH - PAD * 2, strip_h), 1)
    return y + strip_h + 6


def render():
    cell_w = (WIDTH - PAD * 3) // 2
    cell_h = 124

    title_h = 60
    bands_h = (18 + 84 + 6) * 3            # true-near bands DAY / GOLDEN / NIGHT
    rows = (len(ACTS) + 1) // 2
    detail_h = 22 + 2 * (16 + rows * (cell_h + 6))   # DAY + NIGHT detail grids
    strip_h = 120
    comp_h = 22 + 3 * (strip_h + 6)        # DAY + GOLDEN + NIGHT composites
    total_h = title_h + bands_h + detail_h + comp_h + PAD * 10 + 36

    sheet = pygame.Surface((WIDTH, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — STREET PERFORMERS (round 1): the human single-busker POOL — 8 distinct ACTS over a shared _perf_body drawer fed DATA rows",
          PAD, y, 16, (250, 246, 236), bold=True)
    y += 20
    _text(sheet, "Seventh sidewalk-overhaul family (after pedestrians / day_cast / food_stalls / animals / greenery / props). Today the near-lane human roster is ONLY 3 fixed acts (juggler/musician/stilt), one per phase. This RESTYLES "
                 "those three as anchors + adds 5 NEW acts over ONE shared body+action drawer (palette + act/prop/pose flags): CALLIGRAPHER (kneels at a scroll, big brush), TEA-POURER (long-spout copper pot, arcing pour), FORTUNE-TELLER "
                 "(seated at a table, bamboo sticks + a lit candle), FAN/RIBBON DANCER (swept silk arc), MASK-CHANGER (bian-lian opera face). Each reads by SILHOUETTE+PROP+POSE. NIGHT festival lion/dragon already shipped — OUT OF SCOPE.",
          PAD, y, 9, (188, 186, 200))
    y += title_h - 20

    # A. true-near bands DAY / GOLDEN / NIGHT — silhouette variety + yardstick
    _text(sheet, "A.  TRUE NEAR-DECK SIZE — the whole cast in a row, adult + gold-coin yardstick. Each act must read by SILHOUETTE+PROP+POSE.  (TALL acts flagged — they need a clear horizontal zone off the bird/pillar lanes)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    y = _true_band(sheet, y, "A.  DAY", 0.0)
    y = _true_band(sheet, y, "A.  GOLDEN-HOUR", 0.0, gold=True)
    y = _true_band(sheet, y, "A.  NIGHT — unlit acts cool toward (54,64,96); the fortune candle is the ONLY lit prop, capped under the coin", 0.95)

    # B. per-act detail cells (DAY then NIGHT), each a 3-phase motion column
    _text(sheet, "B.  PER-ACT — a COLUMN of 3 pose t-phases (the action as motion) at true-near size + adult yardstick + in-cell coin · 4x WORKING zoom (nearest) · act/prop/pose flags -> foreground_variants.Variant  (DAY then NIGHT)",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT  (unlit acts cool toward (54,64,96); the fortune candle core _cap_to + a PRE-CLAMPED additive halo; mask/drum/paper highlights _cap_lum; nothing self-lit past the coin)" if is_night else "DAY",
              PAD, y, 11, (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for r in range(rows):
            for c in range(2):
                idx = r * 2 + c
                if idx >= len(ACTS):
                    break
                nm, v, beat, hcls, note = ACTS[idx]
                cx = PAD + c * (cell_w + PAD)
                _cell(sheet, nm, v, note, beat, hcls, cx, y, cell_w, cell_h, night)
            y += cell_h + 6
        y += 8

    # C. on-street composites DAY / GOLDEN / NIGHT
    _text(sheet, "C.  ON-STREET COMPOSITE — several buskers mixed among passing pedestrians + a stall for scale, with the coin reference. Beat-appropriate acts foregrounded per band.  (DAY / GOLDEN / NIGHT)",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    y = _composite(sheet, y, strip_h, 0.0, False, "DAY  — calligrapher / fortune / juggler busking the morning market")
    y = _composite(sheet, y, strip_h, 0.0, True, "GOLDEN-HOUR  — tea-pourer / fan-dancer / musician as the lamps warm")
    y = _composite(sheet, y, strip_h, 0.95, False, "NIGHT  — mask-changer / fortune candle / fan-dancer near the festival (all capped under the coin)")

    hottest, over = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    msg = (f"NIGHT-CAP AUDIT (measured on RENDERED pixels across t-phases, incl. the fortune candle core + its PRE-CLAMPED additive halo, the mask/drum/paper capped highlights): "
           f"hottest BUSKER px luma = {hottest:.0f}  ·  px over {NIGHT_GLOW_CAP} = {over}  "
           f"·  gold-coin core luma = {coin_l:.0f} (sole brightest). "
           f"{'PASS — all busker px <= cap.' if over == 0 else 'FAIL — '+str(over)+' px breach the cap.'}")
    _text(sheet, msg, PAD, total_h - 16, 9,
          (170, 200, 180) if over == 0 else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/performers/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-cap audit: hottest busker luma={hottest:.1f}  over-cap px={over}  coin={coin_l:.1f}")


if __name__ == "__main__":
    render()

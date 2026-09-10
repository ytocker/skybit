"""Promenade STREET PERFORMERS — a varied day/evening busker pool.

Seventh family of the sidewalk overhaul, art-director SHIP-READY
(docs/sidewalk_overhaul/performers/round_2.png). Expands the day/evening single-
busker roster (was only juggler/musician/stilt) to 8 distinct ACTS over one shared
_perf_body + draw_act drawer (data rows = palette + act/pose/arm/prop flags):
  A1 juggler · A2 musician · A3 stilt-walker · A4 calligrapher · A5 tea-pourer ·
  A6 fortune-teller · A7 fan/ribbon dancer · A8 mask-changer (bian-lian).
The night festival lion/dragon marquee is a separate, unchanged act family.

Each act reads by silhouette + prop + pose at near-deck scale, animated across t.
The one lit prop (the fortune candle) draws its whole subscene onto its own
SRCALPHA layer, composite-clamped <=146 before blit, so the summed core+halo peak
stays under the gold coin (measured hottest busker 145.8 luma, 0 over the 150 cap,
coin 229.5 sole-brightest). Unlit robes/props cool toward (54,64,96) at night.
Pure-Pygame / pygbag-safe (BLEND_RGB_ADD only via the pre-clamped temp layer).
"""
from __future__ import annotations

import math

import pygame

from game import foreground_variants as fv


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
# The COMPOSITED candle layer (core + summed halo) is held under this so the lit
# peak measured on the blitted pixels lands safely below the 150 ceiling.
LIT_COMPOSITE_CEIL = 146


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


def _cap_lum(color, night, *, cap=132, warm=True):
    """Pull a SOLID near-life highlight (drum head, mask face, brush ferrule) to
    <= cap LUMA at night while keeping a warm/ivory hue, so the brightest near
    busker pixel stays under the coin (mirrors foreground_near_lane._cap_lum).
    Round-2: ceilings tightened (132 default, 128 warm clamp) after the audit
    flagged the mask/drum highlights as the next-hottest pixels behind the candle."""
    if night <= 0.05:
        return color
    r, g, b = color
    if warm:
        r, g, b = min(r, 144), min(g, 128), min(b, 108)
    lum = 0.2126 * r + 0.7152 * g + 0.1145 * b
    if lum > cap and lum > 0:
        f = cap / lum
        r, g, b = int(r * f), int(g * f), int(b * f)
    return (r, g, b)


# ── lit warmth: PRE-CLAMPED additive halo on a PRE-CLAMPED lit layer ───────────
#
# The ONLY lit prop in this family is the fortune-teller's candle. Round-1 clamped
# the halo's added peak in isolation but let the core+halo SUM on the composited
# layer exceed the cap (measured 198 luma). Round-2 draws the entire lit act —
# candle core, flame, AND its additive halo — onto its OWN SRCALPHA layer, then
# composite-clamps that layer hue-preserving to <=LIT_COMPOSITE_CEIL before the
# single blit onto the deck. So whatever core+halo SUM to, the BLITTED pixels can
# never exceed the ceiling — the honest fix the audit demanded.

ADD_BUDGET = 56


def _warm_halo(surf, cx, cy, *, radius, peak, color):
    """Bake a radial additive falloff into a temp surface whose own peak added luma
    is pre-scaled <=ADD_BUDGET, then additively blit it (props_cast._warm_halo).
    Used INSIDE the lit layer below, so its sum with the core is then re-clamped."""
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


def _composite_clamp_layer(layer, ceil):
    """Hue-preserving clamp of EVERY lit pixel on a SRCALPHA layer so the summed
    core+halo peak lands <=ceil before the layer is blitted onto the deck. This is
    what guarantees the COMPOSITED (not just base) candle pixel stays under the
    coin — the round-2 night-cap fix."""
    w, h = layer.get_size()
    for px in range(w):
        for py in range(h):
            r, g, b, a = layer.get_at((px, py))
            if a == 0:
                continue
            y = _luma((r, g, b))
            if y > ceil:
                k = ceil / y
                layer.set_at((px, py), (_clamp(r * k), _clamp(g * k), _clamp(b * k), a))


# ════════════════════════════════════════════════════════════════════════════
# THE SHARED BODY + ACTION DRAWER.  (unchanged architecture from round 1)
# ════════════════════════════════════════════════════════════════════════════

SKIN = (232, 192, 150)


def _perf_body(surf, x, feet_y, robe, robe_dk, hair, night, *, h=18, w=9,
               lean=0, arms='down', arm_t=0.0, pose='stand', accent=None,
               head_bob=0):
    """A near-scale performer torso + head with posable arms + a chosen lower-body
    POSE. Returns (head_x, head_y, shoulder_y, hands, feet_floor) so the act can
    hang a prop off it. Skin + robe are retinted at night so no face out-shines the
    cap. `head_bob` lifts the head a pixel on a beat (the musician's strike)."""
    skin = _retint(SKIN, night)
    body_y = feet_y - h

    if pose == 'kneel':
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
        seat_y = feet_y - 1
        pygame.draw.polygon(surf, _shade(robe_dk, -10), [
            (x - 7, seat_y), (x + 7, seat_y), (x + 5, seat_y - 5), (x - 5, seat_y - 5)])
        torso_top = seat_y - 5 - (h - 9)
        pygame.draw.rect(surf, robe, (x - w // 2 + lean, torso_top, w, seat_y - 5 - torso_top))
        pygame.draw.rect(surf, robe_dk, (x - w // 2 + lean, torso_top, w, seat_y - 5 - torso_top), 1)
        body_y = torso_top
        feet_floor = seat_y - 5
    else:  # 'stand' / 'stilt'
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

    if accent is not None and pose in ('stand', 'stilt'):
        pygame.draw.line(surf, accent, (x - w // 2 + lean, body_y + h // 2),
                         (x + w // 2 + lean, body_y + h // 2), 2)

    hx, hy = x + lean, body_y - 4 - head_bob
    pygame.draw.circle(surf, skin, (hx, hy), 4)
    pygame.draw.arc(surf, hair, (hx - 4, hy - 5, 9, 9),
                    math.radians(0), math.radians(180), 3)
    pygame.draw.circle(surf, (30, 20, 15), (hx - 1, hy), 0)
    pygame.draw.circle(surf, (30, 20, 15), (hx + 1, hy), 0)

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
        # Round-2: a much WIDER high->low forearm travel so the beat reads as a
        # strike, the two hands alternating in antiphase.
        for dx, ph in ((-1, 0.0), (1, math.pi)):
            ax = x + (w // 2) * dx + lean
            lift = int(max(0.0, math.sin(arm_t + ph)) * 7)
            ex, ey = ax + dx * 5, sh_y + 5 - lift
            pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
            hands.append((ex, ey))
    elif arms == 'juggle':
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            ex, ey = ax + dx * 5, sh_y - 4
            pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
            hands.append((ex, ey))
    elif arms == 'reach':
        # Round-2: ONE arm raised HIGH and OUT (the tea pot hand), reaching well
        # above the head so the pot clears the silhouette; the other rests low.
        ax = x + (w // 2) + lean
        ex, ey = ax + 6, sh_y - 11 - int(swing * 2)
        pygame.draw.line(surf, robe, (ax, sh_y), (ex, ey), 2)
        hands.append((ex, ey))
        ax2 = x - (w // 2) + lean
        ex2, ey2 = ax2 - 3, sh_y + 5
        pygame.draw.line(surf, robe, (ax2, sh_y), (ex2, ey2), 2)
        hands.append((ex2, ey2))
    elif arms == 'brush':
        # Round-2: the dominant hand raised toward the chest so the UPRIGHT brush
        # rises from it past the head; the off hand steadies the scroll low.
        axd = x + (w // 2) + lean
        exd, eyd = axd + 1, sh_y - 2
        pygame.draw.line(surf, robe, (axd, sh_y), (exd, eyd), 2)
        hands.append((exd, eyd))
        axo = x - (w // 2) + lean
        exo, eyo = axo - 3, sh_y + 6
        pygame.draw.line(surf, robe, (axo, sh_y), (exo, eyo), 2)
        hands.append((exo, eyo))
    elif arms == 'sweep':
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
        # Round-2: three primaries pre-clamped at night so no ball out-pops the
        # coin once retinted; cascade arc unchanged.
        ball_cols = (P.get("prop_a", (255, 176, 16)), (240, 44, 40), (32, 132, 248))
        for i, col in enumerate(ball_cols):
            ph = (t * 1.6 + i / 3.0) % 1.0
            bx = sx + int(math.sin(ph * math.tau) * 9)
            by = hy - 4 - int(math.sin(ph * math.pi) * 13)
            col = _retint(col, night)
            pygame.draw.circle(surf, _shade(col, -24), (bx, by), 5)
            pygame.draw.circle(surf, col, (bx, by), 4)
            hl = _shade(col, 48)
            if night > 0.05 and _luma(hl) > NIGHT_GLOW_CAP:
                hl = _mix(hl, (66, 76, 104), 0.6)
            pygame.draw.circle(surf, hl, (bx - 1, by - 1), 2)

    elif act == "musician":
        # Round-2: a 1px head-bob on the strike + a much wider forearm travel so
        # the seated figure reads as DRUMMING, not wiggling.
        strike = max(0.0, math.sin(t * 4.5))
        bob = 1 if strike > 0.85 else 0
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx + 6, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='seat', arms='down', arm_t=t * 4.5, accent=accent,
            head_bob=bob)
        dx, dy = sx - 5, feet
        drum = _mix(P.get("prop_a", (150, 60, 45)), (70, 70, 96), 0.30 * night)
        pygame.draw.ellipse(surf, _shade(drum, -24), (dx - 11, dy - 20, 22, 20))
        pygame.draw.ellipse(surf, drum, (dx - 10, dy - 19, 20, 18))
        head_col = _cap_lum((200, 178, 142), night, cap=128)
        pygame.draw.ellipse(surf, head_col, (dx - 9, dy - 19, 18, 6))
        pygame.draw.ellipse(surf, _shade(head_col, -26), (dx - 9, dy - 19, 18, 6), 1)
        tack = _cap_lum((176, 146, 88), night, cap=128)
        for ti in range(-2, 3):
            pygame.draw.circle(surf, tack, (dx + ti * 5, dy - 12), 1)
        # the two beating forearms: a deliberate high->low travel in antiphase, the
        # near hand striking the drum head as the far one lifts high.
        for ph in (0.0, math.pi):
            travel = max(0.0, math.sin(t * 4.5 + ph))
            hy_strike = dy - 16 - int((1.0 - travel) * 8)
            hxh = dx + (5 if ph else -5)
            pygame.draw.line(surf, robe, (sx + 3, feet - 13), (hxh, hy_strike), 2)
            pygame.draw.circle(surf, _retint(SKIN, night), (hxh, hy_strike), 1)

    elif act == "stilt":
        # raised on two tall stilts; TALL. Round-2: stilts widened to 2px minimum
        # so the legs survive over busy pillars/sky at 1x.
        stilt_h = A.get("stilt_h", 24)
        sway = int(math.sin(t * 1.6) * 1)
        body_feet = feet - stilt_h
        pole = _shade(_retint(P.get("prop_a", (110, 78, 48)), night), -6)
        for dx in (-3, 3):
            pygame.draw.line(surf, pole, (sx + dx + sway, body_feet), (sx + dx, feet), 2)
            # a thin highlight rib keeps the 2px pole reading as a rounded stilt.
            pygame.draw.line(surf, _hi(pole, 18, night),
                             (sx + dx + sway, body_feet), (sx + dx, feet), 1)
        _perf_body(surf, sx + sway, body_feet, robe, robe_dk, hair, night,
                   h=h, w=w, pose='stand', arms='up', arm_t=t * 2.0, accent=accent)

    elif act == "calligrapher":
        # KNEELING over a paper scroll. Round-2: a TALL VERTICAL brush rising from
        # the hand PAST the head, the fat ink tip sweeping DOWN across the phases —
        # an upright prop that separates it from the fortune-teller.
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='kneel', arms='brush', arm_t=t * 2.2, accent=accent, lean=2)
        # the paper scroll laid on the deck in front of the kneeling figure.
        paper = _cap_lum(P.get("prop_a", (224, 214, 190)), night, warm=False, cap=128)
        scroll = pygame.Rect(sx + 3, feet - 4, 20, 4)
        pygame.draw.rect(surf, _shade(paper, -16), scroll)
        pygame.draw.rect(surf, paper, scroll.inflate(-2, -1))
        dowel = _retint(P.get("prop_b", (120, 84, 50)), night)
        pygame.draw.rect(surf, dowel, (sx + 2, feet - 5, 2, 6))
        pygame.draw.rect(surf, dowel, (sx + 22, feet - 5, 2, 6))
        ink = _retint((40, 30, 26), night)
        for mi in range(3):
            mx = sx + 8 + mi * 5
            pygame.draw.line(surf, ink, (mx, feet - 3), (mx + 2, feet - 1), 1)
        # THE UPRIGHT BRUSH. The hand is up near the chest; the dark shaft rises
        # VERTICALLY past the head, and the fat ink tip swings DOWN toward the
        # scroll as t advances — the head/shoulder line is broken by a clear pole.
        hand = hands[0] if hands else (sx + 1, sh_y - 2)
        sweep = 0.5 + 0.5 * math.sin(t * 2.2)          # 0..1 across the phases
        butt_x, butt_y = hand[0], hand[1]
        top_x, top_y = butt_x + 1, butt_y - 13         # the brush butt above the head
        # tip arcs from a raised cocked position down onto the paper as sweep->1
        tip_x = sx + 7 + int(sweep * 9)
        tip_y = (feet - 9) + int(sweep * 7)
        shaft = _retint(P.get("prop_b", (120, 84, 50)), night)
        shaft_dk = _shade(shaft, -28)
        # upper shaft (above the hand) — the vertical read
        pygame.draw.line(surf, shaft_dk, (butt_x, butt_y), (top_x, top_y), 2)
        pygame.draw.line(surf, shaft, (butt_x, butt_y), (top_x, top_y), 1)
        # lower shaft from the hand to the fat tip (the working stroke)
        pygame.draw.line(surf, shaft_dk, (butt_x, butt_y), (tip_x, tip_y), 2)
        # the pale bound ferrule + a FAT dark ink tip
        pygame.draw.circle(surf, _cap_lum((216, 206, 192), night, warm=False, cap=120),
                           (butt_x, butt_y), 1)
        tip_ink = _retint((26, 20, 18), night)
        pygame.draw.circle(surf, tip_ink, (tip_x, tip_y), 2)
        pygame.draw.line(surf, tip_ink, (tip_x, tip_y), (tip_x, min(feet - 1, tip_y + 3)), 2)

    elif act == "teapour":
        # Round-2 rebuild: TALL standing stance, ONE arm raised HIGH holding a
        # long-spout COPPER pot, a long curved spout arcing OUT and DOWN, a 1px
        # water stream landing in a tiny cup on a low stand. The diagonal spout +
        # falling water IS the silhouette. TALL.
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='stand', arms='reach', arm_t=t * 1.6, accent=accent, lean=0)
        hand = hands[0] if hands else (sx + 6, sh_y - 11)
        copper = _retint(P.get("prop_a", (190, 122, 64)), night)
        copper_lt = _hi(copper, 26, night)
        copper_dk = _shade(copper, -24)
        # the pot body cupped in the high hand
        pot = pygame.Rect(hand[0] - 4, hand[1] - 3, 9, 7)
        pygame.draw.ellipse(surf, copper_dk, pot)
        pygame.draw.ellipse(surf, copper, pot.inflate(-2, -2))
        pygame.draw.arc(surf, copper_lt, pot, math.radians(30), math.radians(140), 1)
        # the handle loop over the pot
        pygame.draw.arc(surf, copper_dk, (hand[0] - 1, hand[1] - 8, 8, 8),
                        math.radians(20), math.radians(160), 2)
        # THE LONG CURVED COPPER SPOUT — a quadratic arc sweeping OUT from the pot
        # then DOWN toward the cup, the dramatic kung-fu reach. This is the act.
        cup_x, cup_y = sx - 11, feet - 4
        p0 = (hand[0] - 3, hand[1] + 1)                # pot lip
        p1 = (sx - 13, hand[1] - 2)                    # the spout flung out + up
        p2 = (cup_x + 1, cup_y - 9)                    # spout tip poised over the cup
        spout = []
        for i in range(9):
            tt = i / 8
            bx = (1 - tt) ** 2 * p0[0] + 2 * (1 - tt) * tt * p1[0] + tt * tt * p2[0]
            by = (1 - tt) ** 2 * p0[1] + 2 * (1 - tt) * tt * p1[1] + tt * tt * p2[1]
            spout.append((int(bx), int(by)))
        pygame.draw.lines(surf, copper_dk, False, spout, 2)
        pygame.draw.lines(surf, copper_lt, False, spout[:4], 1)
        sp_tip = spout[-1]
        # the falling WATER stream — a thin 1px arc from the spout tip into the cup.
        stream = _cap_lum(P.get("prop_b", (186, 210, 218)), night, warm=False, cap=124)
        wpts = []
        for i in range(7):
            tt = i / 6
            wx = sp_tip[0] + (cup_x - sp_tip[0]) * tt
            wy = sp_tip[1] + (cup_y - 1 - sp_tip[1]) * tt + math.sin(tt * math.pi) * 1.5
            wpts.append((int(wx), int(wy)))
        pygame.draw.lines(surf, stream, False, wpts, 1)
        # a tiny splash where the stream meets the cup
        pygame.draw.circle(surf, stream, (cup_x, cup_y - 1), 1)
        # the tiny cup on a low stand
        clay = _retint((158, 116, 80), night)
        pygame.draw.rect(surf, _shade(clay, -20), (cup_x - 4, feet - 4, 8, 4))
        pygame.draw.ellipse(surf, clay, (cup_x - 3, cup_y - 3, 7, 4))
        pygame.draw.ellipse(surf, _shade(clay, -22), (cup_x - 3, cup_y - 3, 7, 4), 1)

    elif act == "fortune":
        # SEATED at a tiny table. Round-2: a visible vertical KAU-CHIM bamboo-stick
        # CLUSTER fanning up from the held cup so the act reads independent of the
        # (now dimmed + composite-clamped) candle. The whole LIT subscene renders
        # onto its own layer that is composite-clamped <=146 before the blit.
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx + 7, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='seat', arms='down', arm_t=t, accent=accent, lean=-1)
        wood = _retint(P.get("prop_b", (120, 86, 52)), night)
        wood_dk = _shade(wood, -22)
        tbl_y = feet - 8
        pygame.draw.rect(surf, wood_dk, (sx - 11, tbl_y, 16, 3))
        pygame.draw.rect(surf, wood, (sx - 11, tbl_y, 16, 2))
        for lx in (sx - 10, sx + 2):
            pygame.draw.line(surf, wood_dk, (lx, tbl_y + 3), (lx, feet - 1), 2)
        # the cup of bamboo fortune sticks, HELD up and shaken — a tall fanning
        # cluster of light bamboo slats rising well above the table.
        cup = _retint(P.get("prop_a", (150, 70, 56)), night)
        cup_x, cup_y = sx - 4, tbl_y - 2
        pygame.draw.rect(surf, _shade(cup, -20), (cup_x - 3, cup_y - 1, 7, 7))
        pygame.draw.rect(surf, cup, (cup_x - 2, cup_y - 1, 5, 6))
        stick = _cap_lum((192, 174, 130), night, cap=126)
        stick_dk = _shade(stick, -30)
        shake = math.sin(t * 3.0) * 1.0
        for si, ang in enumerate((-26, -15, -5, 5, 15, 26)):
            slen = 11 + (si % 2) * 2
            ex = cup_x + int(math.sin(math.radians(ang)) * slen + shake)
            ey = cup_y - int(math.cos(math.radians(ang)) * slen)
            pygame.draw.line(surf, stick_dk, (cup_x, cup_y), (ex, ey), 1)
            pygame.draw.line(surf, stick, (cup_x, cup_y - 1), (ex, ey), 1)
            # a red-tipped slat head so the bamboo fan reads as kau-chim sticks
            pygame.draw.circle(surf, _retint((180, 70, 56), night), (ex, ey), 1)
        # THE LIT CANDLE — drawn onto its OWN layer (core + flame + halo) which is
        # then composite-clamped <=LIT_COMPOSITE_CEIL so the SUMMED peak, measured
        # on the blitted pixels, stays under the coin. The round-2 night-cap fix.
        cdx, cdy = sx + 2, tbl_y - 1
        if night > 0.05:
            R = 9
            lay = pygame.Surface((R * 2 + 2, R * 2 + 6), pygame.SRCALPHA)
            lcx, lcy = R + 1, R + 5
            wax = _retint((212, 200, 176), night)
            pygame.draw.rect(lay, (*wax, 255), (lcx - 1, lcy - 4, 3, 4))
            flame = _cap_to((236, 196, 120), LIT_NIGHT_CEIL)
            pygame.draw.circle(lay, (*flame, 255), (lcx, lcy - 5), 1)
            _warm_halo(lay, lcx, lcy - 5, radius=7, peak=24, color=(236, 188, 120))
            _composite_clamp_layer(lay, LIT_COMPOSITE_CEIL)
            surf.blit(lay, (cdx - lcx, cdy - lcy))
        else:
            wax = (212, 200, 176)
            pygame.draw.rect(surf, wax, (cdx - 1, cdy - 4, 3, 4))
            pygame.draw.circle(surf, (238, 196, 120), (cdx, cdy - 5), 1)

    elif act == "fandance":
        # standing, sweeping a wide ARC of silk fan overhead. Round-2: a 2px ribbon
        # arc with MORE travel (a flowing trail, not a static line) + a wider fan.
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='stand', arms='sweep', arm_t=t * 1.8, accent=accent, lean=1)
        hand = hands[0] if hands else (sx + 9, sh_y - 6)
        silk = _retint(P.get("prop_a", (224, 110, 130)), night)
        silk_lt = _hi(silk, 24, night)
        base_ang = math.atan2(hand[1] - sh_y, hand[0] - sx)
        # a WIDER fan: more ribs, a longer spread.
        rib_pts = [hand]
        for k in range(-3, 4):
            a = base_ang + math.radians(k * 15)
            ex = hand[0] + int(math.cos(a) * 10)
            ey = hand[1] + int(math.sin(a) * 10)
            pygame.draw.line(surf, silk, (hand[0], hand[1]), (ex, ey), 1)
            rib_pts.append((ex, ey))
        pygame.draw.polygon(surf, silk, rib_pts[1:])
        pygame.draw.polygon(surf, silk_lt, rib_pts[1:], 1)
        # a long trailing RIBBON arc, 2px, with much more travel — a flowing trail
        # that streams off the fan tip and whips with t.
        ribbon = _hi(silk, 12, night)
        tip = rib_pts[len(rib_pts) // 2]
        arc_pts = []
        for i in range(9):
            tt = i / 8
            ax2 = tip[0] - tt * 22 + math.sin(t * 2.4 + tt * 5) * 4
            ay2 = tip[1] - 3 + math.sin(tt * math.pi * 1.3 + t * 1.5) * 8
            arc_pts.append((int(ax2), int(ay2)))
        pygame.draw.lines(surf, ribbon, False, arc_pts, 2)
        pygame.draw.lines(surf, silk_lt, False, arc_pts[:4], 1)

    else:  # 'maskchange' — bian-lian. Round-2: swap-peaks re-audited (tighter cap).
        hx, hy, sh_y, hands, ff = _perf_body(
            surf, sx, feet, robe, robe_dk, hair, night,
            h=h, w=w, pose='stand', arms='sweep', arm_t=t * 2.4, accent=accent)
        mask_cols = (P.get("prop_a", (216, 70, 64)),
                     P.get("prop_b", (70, 110, 170)),
                     (228, 200, 110))
        mc = mask_cols[int(t * 1.5) % len(mask_cols)]
        # the green/red/gold swap peaks all clamped to the same tight night ceiling.
        mc = _cap_lum(mc, night, cap=126, warm=False)
        if night > 0.05 and _luma(mc) > NIGHT_GLOW_CAP - 8:
            mc = _cap_to(mc, NIGHT_GLOW_CAP - 8)
        pygame.draw.circle(surf, mc, (hx, hy), 4)
        ink = _retint((30, 24, 22), night)
        pygame.draw.line(surf, ink, (hx - 3, hy - 1), (hx + 3, hy - 1), 1)
        pygame.draw.line(surf, ink, (hx, hy - 3), (hx, hy + 1), 1)
        eye = _cap_lum((234, 226, 210), night, warm=False, cap=124)
        pygame.draw.circle(surf, eye, (hx - 1, hy), 0)
        pygame.draw.circle(surf, eye, (hx + 1, hy), 0)
        crest = _cap_lum(P.get("prop_b", (228, 200, 110)), night, cap=126)
        pygame.draw.circle(surf, crest, (hx, hy - 5), 1)
        hand = hands[0] if hands else (sx + 9, sh_y - 6)
        fan = _retint((40, 36, 38), night)
        base_ang = math.atan2(hand[1] - sh_y, hand[0] - sx)
        fpts = [hand]
        for k in range(-2, 3):
            a = base_ang + math.radians(k * 14)
            fpts.append((hand[0] + int(math.cos(a) * 7), hand[1] + int(math.sin(a) * 7)))
        pygame.draw.polygon(surf, fan, fpts[1:])
        pygame.draw.polygon(surf, _hi(fan, 30, night), fpts[1:], 1)



# ── the 8-act pool → foreground_variants rows (palette + act/pose/arm/prop) ─────
# `beat` tags the time-of-day affinity the near-lane director selects on (day /
# golden / dusk / market / festival); `tall` flags the clear-zone height class.

def _row(palette, *, beat, tall=False, **attrs):
    v = fv.Variant(palette=dict(palette), attrs=dict(attrs))
    v.attrs["beat"] = beat
    v.attrs["tall"] = tall
    return v


fv.register("performer", [
    _row(dict(robe=(196, 92, 70), robe_dk=(150, 60, 52), hair=(70, 50, 40),
              accent=(208, 176, 96), prop_a=(255, 176, 16)),
         act="juggler", pose="stand", arms="juggle", h=20, w=9, beat="day"),
    _row(dict(robe=(90, 110, 160), robe_dk=(58, 74, 116), hair=(60, 45, 40),
              accent=(196, 170, 96), prop_a=(150, 60, 45)),
         act="musician", pose="seat", arms="drum", h=18, w=9, beat="golden"),
    _row(dict(robe=(150, 70, 130), robe_dk=(100, 44, 92), hair=(60, 45, 40),
              accent=(220, 196, 110), prop_a=(110, 78, 48)),
         act="stilt", pose="stilt", arms="up", h=18, w=8, stilt_h=24,
         beat="dusk", tall=True),
    _row(dict(robe=(120, 130, 120), robe_dk=(84, 96, 88), hair=(54, 46, 40),
              accent=(60, 56, 52), prop_a=(224, 214, 190), prop_b=(120, 84, 50)),
         act="calligrapher", pose="kneel", arms="brush", h=18, w=10, beat="market"),
    _row(dict(robe=(170, 80, 60), robe_dk=(122, 54, 44), hair=(56, 44, 38),
              accent=(214, 190, 110), prop_a=(190, 122, 64), prop_b=(186, 210, 218)),
         act="teapour", pose="stand", arms="reach", h=20, w=9,
         beat="golden", tall=True),
    _row(dict(robe=(78, 92, 120), robe_dk=(52, 64, 88), hair=(58, 50, 44),
              accent=(150, 130, 90), prop_a=(150, 70, 56), prop_b=(120, 86, 52)),
         act="fortune", pose="seat", arms="down", h=18, w=9, lit=True, beat="market"),
    _row(dict(robe=(210, 120, 150), robe_dk=(160, 80, 110), hair=(50, 40, 38),
              accent=(232, 206, 120), prop_a=(224, 110, 130)),
         act="fandance", pose="stand", arms="sweep", h=19, w=8,
         beat="golden", tall=True),
    _row(dict(robe=(90, 60, 120), robe_dk=(62, 42, 86), hair=(40, 34, 38),
              accent=(228, 196, 96), prop_a=(216, 70, 64), prop_b=(70, 110, 170)),
         act="maskchange", pose="stand", arms="sweep", h=19, w=9, beat="festival"),
])


# act indices grouped by the beat band the director offers them in. A slot freezes
# one index from the band's list (seeded by its world key) so a busker never morphs
# mid-pass. Bands overlap a little so each daytime phase has 2-3 acts to vary over.
PERFORMERS_BY_BEAT = {
    "day": [0, 3, 5],         # juggler, calligrapher, fortune
    "golden": [1, 4, 6],      # musician, tea-pourer, fan-dancer
    "dusk": [2, 0, 7],        # stilt, juggler, mask-changer
    "market": [3, 5, 0],      # calligrapher, fortune, juggler
}


def is_tall(variant):
    """True if the act needs the clear horizontal zone (raised body / tall prop)."""
    v = fv.get("performer", variant)
    return bool(v and v.attrs.get("tall"))

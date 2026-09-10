"""Promenade STREET PERFORMERS variety — round 2 candidate-sheet generator.

Seventh sidewalk-overhaul family, sibling to ped_cast / day_cast / food_stalls /
animals_cast / greenery_cast / props_cast. Today the near-lane HUMAN single-busker
roster is only THREE fixed acts (perf_juggler / perf_musician / perf_stilt), one
per phase band. This pool RESTYLES those three as anchors and EXPANDS the human
pool to 8 distinct ACTS over a shared `_perf_body`-style drawer fed DATA rows
(palette + act/prop/pose flags), so the act reads by SILHOUETTE + PROP + POSE at
near-deck scale — exactly how the six shipped families work.

Round-2 revisions (art-director ITERATE — KEEP all 8 acts; A8/A1/A3/A7 approved):

  1. (BLOCKER) NIGHT-CAP. The hottest busker measured 198 luma (78 over the 150
     ceiling) — culprit the fortune candle CORE + its additive halo summing past
     the cap on the composited layer. FIX: the ONE lit act now renders onto its
     OWN SRCALPHA layer, the layer is hue-preserving composite-clamped <=146
     (core+halo summed), THEN blitted — so the COMPOSITED peak, not just the
     base, lands under the cap. A8 mask swap-peaks / A1 ball primaries / A2 ivory
     drum head re-audited in the same pass (tighter _cap_lum ceilings).
  2. A5 TEA-POURER rebuilt: TALL stance, ONE arm raised HIGH holding the pot, a
     long curved COPPER SPOUT arcing OUT and DOWN, a 1px water-stream arc landing
     in a tiny cup. The diagonal spout + falling water IS the silhouette.
  3. A4 CALLIGRAPHER: a TALL VERTICAL brush shaft (dark) + a fatter ink tip that
     BREAKS the head/shoulder line and visibly SWEEPS DOWN across the 3 phases.
  4. A2 MUSICIAN: exaggerated forearm travel high->low across phases + a 1px
     head-bob on the strike, so it reads as drumming.
  5. A6 FORTUNE-TELLER: a visible vertical KAU-CHIM bamboo-stick cluster fanning
     up from the hand, so the act reads independent of the dimmed candle.
  6. A7 FAN/RIBBON DANCER: a 2px ribbon arc with MORE travel (a flowing trail) +
     a slightly wider fan.
  7. A3 STILT-WALKER: 2px MIN stilt width confirmed at 1x.
  8. Composite re-checked: TALL acts keep clear headroom beside stall+pedestrians;
     the half acts sit low and don't read as one crouch in a row.

References studied first (web search):
  - Temple-fair calligraphers write on a paper scroll, big UPRIGHT brush sweeping.
  - Sichuan kung-fu tea: a long-spout COPPER kettle poured in a dramatic high arc
    into a tiny cup, arm extended HIGH.
  - Temple-street fortune-tellers sit at a tiny table with a CUP of bamboo kau-chim
    sticks held / fanned upward.
  - Bian-lian (Sichuan-opera face-changing): a vivid opera MASK swept by a fan.
  - Fan / ribbon dancers sweep a wide arc of silk overhead with a long trailing tail.

CONSTRAINTS (match the shipped families — non-negotiable):
  pure pygame.draw.* + Surface (SRCALPHA; BLEND_RGB_ADD only via a PRE-CLAMPED
  temp halo on a PRE-CLAMPED lit layer, mirroring props_cast._warm_halo, for the
  ONE lit act — the fortune candle); pygbag-safe, no numpy / gfxdraw / PIL.
  Authored at near-deck performer scale (body h≈18-20px; props/poses extend it),
  drawn CRISP (nearest). Each act shown at 3 t-phases so the action reads as
  motion, plus a true-near single + the on-street composite. Every lit pixel held
  <=NIGHT_GLOW_CAP=150 luma after its additive halo, so NOTHING out-pops the gold
  coin (~230). Unlit acts cool toward (54,64,96) at night via the family _retint.
  Muted shan-shui palette. Expressible as foreground_variants.Variant rows.

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


# ════════════════════════════════════════════════════════════════════════════
# THE POOL — foreground_variants.Variant rows (DATA, not bespoke functions).
# ════════════════════════════════════════════════════════════════════════════

class _V:
    def __init__(self, palette, *, attrs=None):
        self.palette = palette
        self.attrs = dict(attrs or {})


def _row(palette, **attrs):
    return _V(dict(palette), attrs=attrs)


ACTS = [
    ("A1 juggler (anchor)",
     _row(dict(robe=(196, 92, 70), robe_dk=(150, 60, 52), hair=(70, 50, 40),
               accent=(208, 176, 96), prop_a=(255, 176, 16)),
          act="juggler", pose="stand", arms="juggle", h=20, w=9),
     "DAY", "H",
     "act:juggler pose:stand arms:juggle | robe terracotta(196,92,70) sash gold(208,176,96) balls hot primaries | APPROVED anchor — held. 3 balls on a sine cascade; night ball highlights pre-clamped under the coin. beat: DAY"),

    ("A2 musician (anchor)",
     _row(dict(robe=(90, 110, 160), robe_dk=(58, 74, 116), hair=(60, 45, 40),
               accent=(196, 170, 96), prop_a=(150, 60, 45)),
          act="musician", pose="seat", arms="drum", h=18, w=9),
     "GOLDEN", "H",
     "act:musician pose:seat | indigo robe(90,110,160) barrel drum(150,60,45) ivory head capped128 | R2 FIX: BEAT now reads — forearms travel HIGH->LOW in antiphase + a 1px head-bob on the strike. drum head re-capped. beat: GOLDEN-HOUR"),

    ("A3 stilt-walker (anchor)",
     _row(dict(robe=(150, 70, 130), robe_dk=(100, 44, 92), hair=(60, 45, 40),
               accent=(220, 196, 110), prop_a=(110, 78, 48)),
          act="stilt", pose="stilt", arms="up", h=18, w=8, stilt_h=24),
     "DUSK", "T",
     "act:stilt pose:stilt arms:up stilt_h:24 | magenta robe(150,70,130) wood stilts | APPROVED silhouette — held. R2: stilts 2px MIN + a highlight rib so the legs survive over busy pillars/sky at 1x. TALL. beat: DUSK"),

    ("A4 calligrapher",
     _row(dict(robe=(120, 130, 120), robe_dk=(84, 96, 88), hair=(54, 46, 40),
               accent=(60, 56, 52), prop_a=(224, 214, 190), prop_b=(120, 84, 50)),
          act="calligrapher", pose="kneel", arms="brush", h=18, w=10),
     "MARKET", "H",
     "act:calligrapher pose:kneel arms:brush | sage robe(120,130,120) paper(224,214,190) brush shaft(120,84,50) | R2 FIX: a TALL VERTICAL brush rises past the head (breaks the head/shoulder line) + a FAT ink tip sweeping DOWN across the 3 phases — the upright pole separates it from A6. NIGHT: paper/ferrule _cap_lum. beat: MARKET"),

    ("A5 tea-pourer",
     _row(dict(robe=(170, 80, 60), robe_dk=(122, 54, 44), hair=(56, 44, 38),
               accent=(214, 190, 110), prop_a=(190, 122, 64), prop_b=(186, 210, 218)),
          act="teapour", pose="stand", arms="reach", h=20, w=9),
     "GOLDEN", "T",
     "act:teapour pose:stand arms:reach | rust robe(170,80,60) COPPER long-spout pot(190,122,64) water arc(186,210,218) | R2 REBUILD: TALL stance, ONE arm raised HIGH with the pot, a long curved spout arcing OUT+DOWN, a 1px water stream landing in a tiny cup — the diagonal spout+falling water IS the silhouette. TALL. beat: GOLDEN-HOUR"),

    ("A6 fortune-teller",
     _row(dict(robe=(78, 92, 120), robe_dk=(52, 64, 88), hair=(58, 50, 44),
               accent=(150, 130, 90), prop_a=(150, 70, 56), prop_b=(120, 86, 52)),
          act="fortune", pose="seat", arms="down", h=18, w=9, lit=True),
     "MARKET", "H",
     "act:fortune pose:seat lit:candle | slate robe(78,92,120) kau-chim stick-cup(150,70,56) low table(120,86,52) | R2 FIX: a TALL vertical bamboo KAU-CHIM stick cluster fans up from the cup (red-tipped slats) so the act reads WITHOUT the candle. NIGHT-CAP FIX: the lit candle (core+flame+halo) renders on its OWN layer, composite-clamped <=146, then blit. beat: MARKET"),

    ("A7 fan / ribbon dancer",
     _row(dict(robe=(210, 120, 150), robe_dk=(160, 80, 110), hair=(50, 40, 38),
               accent=(232, 206, 120), prop_a=(224, 110, 130)),
          act="fandance", pose="stand", arms="sweep", h=19, w=8),
     "GOLDEN", "T",
     "act:fandance pose:stand arms:sweep | rose robe(210,120,150) silk fan + ribbon(224,110,130) | APPROVED separation from A8 — held. R2: ribbon thickened to 2px with MORE travel (a flowing whipping trail) + the fan widened (7 ribs). TALL-ish. beat: GOLDEN-HOUR"),

    ("A8 mask-changer (bian-lian)",
     _row(dict(robe=(90, 60, 120), robe_dk=(62, 42, 86), hair=(40, 34, 38),
               accent=(228, 196, 96), prop_a=(216, 70, 64), prop_b=(70, 110, 170)),
          act="maskchange", pose="stand", arms="sweep", h=19, w=9),
     "FESTIVAL", "H",
     "act:maskchange pose:stand arms:sweep | violet opera-robe(90,60,120) BOLD mask swaps red(216,70,64)/blue(70,110,170)/gold | APPROVED — the bar. R2: only the swap-peaks re-audited — all three faces clamped to the same tight night ceiling so no swap frame out-pops the coin. beat: FESTIVAL"),
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
    bg = _bg_for(night, gold)
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 14
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    fx0 = 40
    for i, tt in enumerate((0.15, 0.75, 1.45)):
        cxp = fx0 + i * 50
        draw_act(cell, cxp, base, v, night, tt)
    _text(cell, "true-near · 3 t-phases (motion)", fx0 - 26, base + 2, 8, _shade(bg, 50))

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
    _text(sheet, title, PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    band_h = 90
    row = pygame.Surface((WIDTH - PAD * 2, band_h))
    bg = _bg_for(night, gold)
    row.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = band_h - 12
    pygame.draw.rect(row, deck, (0, base, WIDTH - PAD * 2, 12))
    pygame.draw.line(row, _shade(bg, 26), (0, base), (WIDTH - PAD * 2, base), 1)
    _adult_ref(row, 32, base, night)
    _text(row, "adult", 18, base + 1, 8, _shade(bg, 50))
    _gold_coin(row, WIDTH - PAD * 2 - 18, base - 52)
    _text(row, "coin", WIDTH - PAD * 2 - 36, base - 40, 8, _shade(bg, 50))
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
    The fortune candle's COMPOSITED (core + halo on its own clamped layer) pixels
    are included, as is every mask-swap / ball / drum-head frame."""
    night = 0.95
    base = 92
    hot_by_act = {}
    bg_l = _luma(BG_NIGHT)
    hottest = 0.0
    over = 0
    for nm, v, _b, _h, _n in ACTS:
        # render each act on its OWN cleared band so the per-act readout never
        # bleeds a neighbour's prop into the measurement window, and so the strip
        # width can't overflow regardless of act count.
        band = pygame.Surface((12 * 40 + 60, 110))
        band.fill(BG_NIGHT)
        bx = 30
        for k in range(12):
            tt = k * 0.21
            draw_act(band, bx, base, v, night, tt)
            bx += 40
        act_hot = 0.0
        for px in range(band.get_width()):
            for py in range(band.get_height()):
                c = band.get_at((px, py))[:3]
                l = _luma(c)
                if abs(l - bg_l) < 1.5:
                    continue
                act_hot = max(act_hot, l)
                hottest = max(hottest, l)
                if l > NIGHT_GLOW_CAP:
                    over += 1
        hot_by_act[nm.split(" ")[0]] = act_hot
    return hottest, over, hot_by_act


def _composite(sheet, y, strip_h, night, gold, label):
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

    def is_tall(name):
        return next(h for nm, v, _b, h, _n in ACTS if nm.startswith(name)) == "T"

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
        # TALL acts keep clear headroom — flag the clear-zone in the composite.
        if is_tall(tag):
            _text(strip, "TALL", x - 10, base - 56, 7,
                  (210, 140, 90) if night <= 0.5 else (200, 150, 120), bold=True)
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
    bands_h = (18 + 90 + 6) * 3
    rows = (len(ACTS) + 1) // 2
    detail_h = 22 + 2 * (16 + rows * (cell_h + 6))
    strip_h = 120
    comp_h = 22 + 3 * (strip_h + 6)
    total_h = title_h + bands_h + detail_h + comp_h + PAD * 10 + 36

    sheet = pygame.Surface((WIDTH, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — STREET PERFORMERS (round 2): all 8 ACTS kept; motion/props rebuilt + the night-cap BLOCKER fixed (composite-clamped lit layer)",
          PAD, y, 16, (250, 246, 236), bold=True)
    y += 20
    _text(sheet, "R2 changes vs round 1: (1 BLOCKER) the fortune candle is now drawn on its OWN layer (core+flame+halo) composite-clamped <=146 before blit, so the SUMMED lit peak lands under the coin; mask/drum/ball/paper highlights re-capped. "
                 "(2) A5 TEA-POURER rebuilt — TALL, arm raised HIGH, a long copper spout arcing OUT+DOWN, a 1px water stream into a cup. (3) A4 CALLIGRAPHER — a TALL vertical brush breaking the head line, fat tip sweeping down. (4) A2 MUSICIAN — high->low forearm "
                 "travel + a head-bob = a real beat. (5) A6 FORTUNE — a tall bamboo kau-chim stick fan, so it reads without the candle. (6) A7 ribbon 2px + more travel, wider fan. (7) A3 stilts 2px min. KEPT/approved: A8 mask, A1 juggler, A3 silhouette, A7 separation.",
          PAD, y, 9, (188, 186, 200))
    y += title_h - 20

    _text(sheet, "A.  TRUE NEAR-DECK SIZE — the whole cast in a row, adult + gold-coin yardstick. Each act must read by SILHOUETTE+PROP+POSE.  (TALL acts flagged — they need a clear horizontal zone off the bird/pillar lanes)",
          PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    y = _true_band(sheet, y, "A.  DAY", 0.0)
    y = _true_band(sheet, y, "A.  GOLDEN-HOUR", 0.0, gold=True)
    y = _true_band(sheet, y, "A.  NIGHT — unlit acts cool toward (54,64,96); the fortune candle (on its own composite-clamped layer) is the ONLY lit prop, held under the coin", 0.95)

    _text(sheet, "B.  PER-ACT — a COLUMN of 3 pose t-phases (the action as motion) at true-near size + adult yardstick + in-cell coin · 4x WORKING zoom (nearest) · act/prop/pose flags -> foreground_variants.Variant  (DAY then NIGHT)",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT  (unlit acts cool toward (54,64,96); the fortune candle core+flame+halo on its OWN layer composite-clamped <=146; mask/drum/paper/ball highlights _cap_lum; nothing self-lit past the coin)" if is_night else "DAY",
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

    _text(sheet, "C.  ON-STREET COMPOSITE — several buskers mixed among passing pedestrians + a stall for scale, with the coin reference. TALL acts keep clear headroom; half acts sit low and read distinct.  (DAY / GOLDEN / NIGHT)",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    y = _composite(sheet, y, strip_h, 0.0, False, "DAY  — calligrapher / fortune / juggler busking the morning market")
    y = _composite(sheet, y, strip_h, 0.0, True, "GOLDEN-HOUR  — tea-pourer / fan-dancer / musician as the lamps warm")
    y = _composite(sheet, y, strip_h, 0.95, False, "NIGHT  — mask-changer / fortune candle / fan-dancer near the festival (all capped under the coin)")

    hottest, over, hot_by_act = _measure_night_cap()
    coin_l = _luma((255, 232, 150))
    per_act = "  ".join(f"{k}={vv:.0f}" for k, vv in hot_by_act.items())
    passed = (over == 0) and (hottest <= NIGHT_GLOW_CAP) and (hottest < coin_l)
    msg = (f"NIGHT-CAP AUDIT (measured on RENDERED pixels across 12 t-phases/act, incl. the candle core+flame+halo COMPOSITED on its own clamped layer): "
           f"hottest BUSKER px luma = {hottest:.0f}  ·  px over {NIGHT_GLOW_CAP} = {over}  ·  coin core luma = {coin_l:.0f} (sole brightest). "
           f"per-act hottest: {per_act}.  "
           f"{'PASS — hottest busker <= 150, coin sole-brightest.' if passed else 'FAIL — '+str(over)+' px breach the cap (hottest '+f'{hottest:.0f}'+').'}")
    _text(sheet, msg, PAD, total_h - 16, 9,
          (170, 200, 180) if passed else (220, 140, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/performers/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print(f"night-cap audit: hottest busker luma={hottest:.1f}  over-cap px={over}  coin={coin_l:.1f}")
    print("per-act hottest:", {k: round(vv, 1) for k, vv in hot_by_act.items()})


if __name__ == "__main__":
    render()

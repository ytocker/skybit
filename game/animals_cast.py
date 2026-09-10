"""Promenade ANIMALS — a varied dog pool + street critters.

Replaces the single repeated street dog with a 5-strong 'dog' pool (lean hound /
short-leg dash / fluffy spitz / stocky shiba / droopy long-ear pup) whose breed
read lives entirely in the OUTLINE (proportion + tail + ear + muzzle), plus a
'critter' pool (sitting cat / pecking hen / pigeon trio / waddling duck), each
with its own t-driven idle motion. Art-director SHIP-READY
(docs/sidewalk_overhaul/animals/round_2.png), sibling to the ped_cast / day_cast /
food_stalls families.

Drawn CRISP at native size (no smoothscale). Night cooling toward (54,64,96) with
an extra pull on pale coats so nothing breaches the 150 luma cap — the gold coin
stays the sole brightest element (measured hottest animal pixel 144.5 vs coin
231). Pure-Pygame / pygbag-safe.
"""
from __future__ import annotations

import math

import pygame

from game.foreground_props import _mix, _shade, _clamp
from game import foreground_variants as fv

NIGHT_GLOW_CAP = 150
DOG_H = 12      # shoulder height of a 1.0-build dog (~2/3 of an adult, PED_H 18)


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _retint(col, night):
    """Cool toward the night ground band (matches ped_cast._retint_person), with a
    second stronger pull on any PALE coat still above the cap — so a near-white
    coat (+ its highlight) can never out-glow the gold coin at night."""
    if night <= 0.05:
        return col
    out = _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _hi(c, d, night):
    """A highlight d above c, but clamped under the night cap so _shade can't push
    a pale night coat past the coin."""
    out = _shade(c, d)
    if night > 0.05 and _luma(out) > NIGHT_GLOW_CAP:
        out = _mix(out, (66, 76, 104), 0.65)
    return out


# ── DOGS — one shared drawer; breed = the OUTLINE. Feet on base_y, facing LEFT ──

def draw_dog(surf, cx, base_y, v, night, t):
    P, A = v.palette, v.attrs
    pf = lambda c: _retint(c, night)
    coat = pf(P["coat"])
    coat_dk = pf(P.get("coat_dk", _shade(P["coat"], -40)))
    coat_lt = _hi(coat, 16, night)
    belly = pf(P.get("belly", _shade(P["coat"], 22)))
    nose_c = pf((40, 32, 30))

    build = A.get("build", 1.0)
    legf = A.get("leg", 1.0)
    lengthf = A.get("length", 1.0)
    chestf = A.get("chest", 1.0)
    headf = A.get("head", 1.0)
    fluffy = A.get("fluffy", False)
    tail = A.get("tail", "low")
    ear = A.get("ear", "drop")
    muzzle = A.get("muzzle", "med")

    sh_h = max(8, int(DOG_H * build))
    leg_h = max(2, int(sh_h * 0.40 * legf))
    body_h = max(5, int((sh_h - leg_h) * 0.92 * chestf))
    body_w = max(9, int(sh_h * 1.15 * lengthf))
    head_r = max(3, int(sh_h * 0.27 * headf))

    ground = int(base_y)
    body_top0 = ground - leg_h - body_h
    body_left = cx - body_w // 2
    body_right = cx + body_w // 2
    body_cy0 = body_top0 + body_h // 2

    gait = math.sin(t * 6.0)
    bob = int(round(abs(gait) * (sh_h * 0.05)))
    body_top = body_top0 - bob
    body_cy = body_cy0 - bob

    leg_col = coat_dk
    paw = _shade(coat_dk, -16)
    fx_front = body_left + max(2, body_w // 5)
    fx_rear = body_right - max(2, body_w // 5)
    swing = gait * max(1.5, body_w * 0.11)
    lw = max(2, sh_h // 6)
    for fx, ph in ((fx_front, 1), (fx_rear, -1)):
        for off, s in ((0, ph), (2, -ph)):
            sw = swing * s
            top_y = body_cy + body_h // 5
            foot_x = int(fx + off + sw)
            pygame.draw.line(surf, leg_col, (fx + off, top_y), (foot_x, ground), lw)
            pygame.draw.line(surf, paw, (foot_x - 1, ground), (foot_x + 1, ground), lw)

    tx = body_right - 1
    sway = int(round(gait * 1.4))
    tcol = coat
    tw = max(2, sh_h // 5)
    if tail == "low":
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.55), body_cy + int(sh_h * 0.22)),
            (tx + int(sh_h * 0.80), body_cy + int(sh_h * 0.60) + sway)], tw)
        pygame.draw.lines(surf, coat_dk, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.55), body_cy + int(sh_h * 0.22)),
            (tx + int(sh_h * 0.80), body_cy + int(sh_h * 0.60) + sway)], 1)
    elif tail == "lowpup":
        pygame.draw.lines(surf, tcol, False, [
            (tx - 1, body_cy), (tx + int(sh_h * 0.32), body_cy + int(sh_h * 0.20)),
            (tx + int(sh_h * 0.38), body_cy + sway)], tw)
    elif tail == "plume":
        ax, ay = tx - 1, body_cy
        pygame.draw.lines(surf, tcol, False, [
            (ax, ay), (ax + int(sh_h * 0.45), body_top - int(sh_h * 0.1)),
            (ax + int(sh_h * 0.3), body_top - int(sh_h * 0.55)),
            (ax - int(sh_h * 0.1) + sway, body_top - int(sh_h * 0.75))],
            max(3, sh_h // 4))
        pygame.draw.lines(surf, coat_lt, False, [
            (ax + int(sh_h * 0.45), body_top - int(sh_h * 0.1)),
            (ax + int(sh_h * 0.3), body_top - int(sh_h * 0.55))], 1)
    elif tail == "tightcurl":
        cxr, cyr = tx - 1, body_top - 1
        rr = max(2, int(sh_h * 0.26))
        pygame.draw.arc(surf, tcol, (cxr - rr, cyr - rr, rr * 2, rr * 2),
                        math.radians(-60), math.radians(250), max(2, sh_h // 5))
        pygame.draw.arc(surf, coat_lt, (cxr - rr, cyr - rr, rr * 2, rr * 2),
                        math.radians(20), math.radians(160), 1)
    elif tail == "stub":
        pygame.draw.line(surf, tcol, (tx - 1, body_cy), (tx + 2 + sway, body_top - 1), max(2, sh_h // 4))

    body_rect = pygame.Rect(body_left, body_top, body_w, body_h)
    pygame.draw.ellipse(surf, coat, body_rect)
    pygame.draw.ellipse(surf, coat_dk, body_rect, 1)
    pygame.draw.arc(surf, belly, body_rect, math.radians(200), math.radians(340), 1)
    pygame.draw.arc(surf, coat_lt, body_rect, math.radians(35), math.radians(145), 1)
    if fluffy:
        for bxp in range(body_left + 2, body_right - 1, 2):
            pygame.draw.circle(surf, coat_lt, (bxp, body_top + 1), 1)

    hx = body_left - max(1, int(head_r * 0.3))
    hy = body_top + max(1, int(body_h * 0.1)) - max(1, int(sh_h * 0.18))
    pygame.draw.polygon(surf, coat, [
        (body_left + head_r, body_top), (body_left + 1, body_top + body_h - 1),
        (hx, hy + head_r), (hx - 1, hy - head_r // 2)])
    if fluffy:
        pygame.draw.circle(surf, coat_lt, (body_left + 1, body_cy), max(2, head_r - 1))
    pygame.draw.circle(surf, coat, (hx, hy), head_r)
    pygame.draw.circle(surf, coat_dk, (hx, hy), head_r, 1)

    if muzzle == "long":
        mlen = int(head_r * 1.4); mh = max(2, head_r - 1)
    elif muzzle == "short":
        mlen = max(2, int(head_r * 0.6)); mh = max(2, head_r)
    else:
        mlen = max(3, int(head_r * 1.0)); mh = max(2, head_r - 1)
    mx = hx - head_r // 2 - mlen
    pygame.draw.polygon(surf, coat, [
        (hx - head_r // 3, hy - mh // 2), (mx, hy - 1),
        (mx, hy + 1), (hx - head_r // 3, hy + mh // 2 + 1)])
    pygame.draw.circle(surf, nose_c, (mx, hy), 1)
    pygame.draw.circle(surf, (28, 22, 20), (hx - head_r // 3, hy - head_r // 3), 1)

    if ear == "prick":
        pygame.draw.polygon(surf, coat_dk, [
            (hx + 1, hy - head_r), (hx + head_r + 1, hy - head_r - 2), (hx + head_r, hy - head_r // 3)])
    elif ear == "bigprick":
        pygame.draw.polygon(surf, coat_dk, [
            (hx, hy - head_r), (hx + head_r, hy - int(head_r * 2.2)), (hx + head_r + 1, hy - head_r // 3)])
        pygame.draw.polygon(surf, _mix(coat, belly, 0.5), [
            (hx + 1, hy - head_r), (hx + head_r - 1, hy - int(head_r * 1.7)), (hx + head_r, hy - head_r // 2)])
    elif ear == "drop":
        pygame.draw.polygon(surf, coat_dk, [
            (hx + head_r // 2, hy - head_r + 1), (hx + head_r + 1, hy - head_r // 2), (hx + head_r - 1, hy + head_r)])
    elif ear == "longdrop":
        sway2 = int(round(gait * 0.8))
        for depth, fx_off, shade in ((2.7, 1, 0), (2.4, -1, -16)):
            ex0 = hx + (head_r // 2 if fx_off > 0 else -head_r // 3)
            tip_y = hy + int(head_r * depth)
            pygame.draw.polygon(surf, _shade(coat_dk, shade), [
                (ex0, hy - head_r + 1),
                (hx + head_r + 1, hy - head_r // 3),
                (hx + (head_r if fx_off > 0 else 1) + sway2, tip_y),
                (ex0 - 1, hy + head_r // 2)])


# ── CRITTERS — one shared drawer dispatched by kind; each its own motion ───────

def draw_critter(surf, cx, base_y, v, night, t):
    kind = v.attrs.get("kind", "hen")
    {"cat": _crit_cat, "hen": _crit_hen, "pigeons": _crit_pigeons,
     "duck": _crit_duck}[kind](surf, cx, base_y, v, night, t)


def _crit_cat(surf, cx, base_y, v, night, t):
    pf = lambda c: _retint(c, night)
    P = v.palette
    fur = pf(P.get("body", (120, 112, 104)))
    fur_dk = pf(P.get("body_dk", _shade(P["body"], -34)))
    fur_lt = _hi(fur, 18, night)
    ear_in = pf(P.get("accent", (150, 110, 110)))
    g = int(base_y)
    body_h = 7
    body = pygame.Rect(cx - 3, g - body_h, 6, body_h)
    pygame.draw.ellipse(surf, fur, body)
    pygame.draw.ellipse(surf, fur_dk, body, 1)
    pygame.draw.ellipse(surf, fur, (cx - 4, g - 3, 8, 3))
    hx, hy = cx - 1, g - body_h - 1
    pygame.draw.circle(surf, fur, (hx, hy), 3)
    pygame.draw.circle(surf, fur_dk, (hx, hy), 3, 1)
    swiv = int(round(math.sin(t * 1.3) * 1))
    for ex in (-2, 2):
        pygame.draw.polygon(surf, fur, [
            (hx + ex, hy - 1), (hx + ex + (1 if ex < 0 else -1), hy - 4 + (swiv if ex > 0 else 0)),
            (hx + ex + (2 if ex < 0 else -2), hy - 1)])
        pygame.draw.line(surf, ear_in, (hx + ex, hy - 1), (hx + ex + (1 if ex < 0 else -1), hy - 3), 1)
    pygame.draw.circle(surf, (40, 70, 50), (hx - 1, hy), 1)
    pygame.draw.circle(surf, fur_lt, (hx - 2, hy + 1), 1)
    flick = int(round(math.sin(t * 2.2) * 2))
    pygame.draw.lines(surf, fur, False, [
        (cx + 3, g - 1), (cx + 5, g - 2), (cx + 5, g - 5),
        (cx + 3 + flick, g - 6 - max(0, flick))], 2)
    pygame.draw.circle(surf, fur_dk, (cx + 3 + flick, g - 6 - max(0, flick)), 1)


def _crit_hen(surf, cx, base_y, v, night, t):
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (200, 188, 170)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -38)))
    body_lt = _hi(body, 16, night)
    comb = pf(P.get("accent", (176, 70, 60)))
    beak = pf((196, 158, 80))
    leg = pf((176, 140, 88))
    g = int(base_y)
    peck = max(0.0, math.sin(t * 3.2))
    bw, bh = 8, 6
    by = g - bh - 1
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, body_lt, (cx - bw // 2, by, bw, bh), math.radians(40), math.radians(150), 1)
    pygame.draw.polygon(surf, body_dk, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 3, by - 3), (cx + bw // 2 + 2, by + 2)])
    pygame.draw.polygon(surf, body, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 2, by - 1), (cx + bw // 2, by + 3)])
    for lx in (cx - 1, cx + 2):
        pygame.draw.line(surf, leg, (lx, by + bh - 1), (lx, g), 1)
        pygame.draw.line(surf, leg, (lx - 1, g), (lx + 1, g), 1)
    hx0, hy0 = cx - bw // 2, by
    hx = hx0 - 1 - int(peck * 1)
    hy = hy0 - 2 + int(peck * 5)
    pygame.draw.line(surf, body, (hx0, by + 1), (hx, hy), 2)
    pygame.draw.circle(surf, body, (hx, hy), 2)
    pygame.draw.circle(surf, comb, (hx, hy - 2), 1)
    pygame.draw.circle(surf, comb, (hx - 1, hy + 1), 1)
    pygame.draw.polygon(surf, beak, [(hx - 2, hy), (hx - 4, hy), (hx - 2, hy + 1)])
    pygame.draw.circle(surf, (24, 18, 16), (hx - 1, hy - 1), 1)


def _crit_pigeons(surf, cx, base_y, v, night, t):
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (140, 142, 152)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -34)))
    neck = pf(P.get("accent", (110, 120, 150)))
    beak = pf((120, 110, 110))
    g = int(base_y)
    specs = ((-3, 0.0, False, True), (3, 0.6, True, False), (6, 1.1, False, False))
    for dx, ph, hops, lead in specs:
        bx = cx + dx
        peck = max(0.0, math.sin(t * 3.0 + ph * 6))
        hop = max(0.0, math.sin(t * 1.6 + ph * 6)) if hops else 0.0
        lift = int(hop * 4)
        gb = g - lift
        bw, bh = (7, 5) if lead else (5, 4)
        by = gb - bh - 1
        pygame.draw.ellipse(surf, body, (bx - bw // 2, by, bw, bh))
        pygame.draw.ellipse(surf, body_dk, (bx - bw // 2, by, bw, bh), 1)
        pygame.draw.line(surf, body_dk, (bx + bw // 2 - 1, by + 1), (bx + bw // 2 + 2, by + 2), 1)
        if lift <= 0:
            for lx in (bx - 1, bx + 1):
                pygame.draw.line(surf, beak, (lx, by + bh - 1), (lx, g), 1)
        hr = 2 if lead else 1
        hx = bx - bw // 2 - int(peck * 1)
        hy = by - 1 + int(peck * 3)
        pygame.draw.line(surf, neck, (bx - bw // 2 + 1, by + 1), (hx, hy), 2)
        pygame.draw.circle(surf, body, (hx, hy), hr)
        pygame.draw.polygon(surf, beak, [(hx - hr, hy), (hx - hr - 1, hy), (hx - hr, hy + 1)])
        pygame.draw.circle(surf, (24, 20, 22), (hx - 1, hy - 1), 1)
    for sx in (cx - 2, cx + 4):
        pygame.draw.circle(surf, pf((150, 130, 90)), (sx, g), 1)


def _crit_duck(surf, cx, base_y, v, night, t):
    pf = lambda c: _retint(c, night)
    P = v.palette
    body = pf(P.get("body", (210, 204, 190)))
    body_dk = pf(P.get("body_dk", _shade(P["body"], -36)))
    body_lt = _hi(body, 16, night)
    head_c = pf(P.get("accent", (96, 120, 96)))
    bill = pf((196, 168, 90))
    foot = pf((200, 150, 80))
    g = int(base_y)
    waddle = math.sin(t * 3.4)
    rock = int(round(waddle * 1))
    bobh = int(round(math.sin(t * 3.4 + 1.2) * 1))
    bw, bh = 9, 4
    by = g - bh - 1
    pygame.draw.ellipse(surf, body, (cx - bw // 2, by, bw, bh))
    pygame.draw.ellipse(surf, body_dk, (cx - bw // 2, by, bw, bh), 1)
    pygame.draw.arc(surf, body_lt, (cx - bw // 2, by, bw, bh), math.radians(30), math.radians(150), 1)
    pygame.draw.polygon(surf, body, [
        (cx + bw // 2 - 1, by + 1), (cx + bw // 2 + 2, by - 2), (cx + bw // 2, by + 2)])
    for lx, phase in ((cx - 1, 0), (cx + 2, math.pi)):
        step = int(round(math.sin(t * 3.4 + phase) * 1))
        pygame.draw.line(surf, foot, (lx, by + bh - 1), (lx + step, g), 1)
        pygame.draw.line(surf, foot, (lx + step - 1, g), (lx + step + 1, g), 1)
    hx = cx - bw // 2 - 1 + rock
    hy = by - 3 + bobh
    pygame.draw.line(surf, head_c, (cx - bw // 2 + 1, by + 1), (hx, hy), 2)
    pygame.draw.circle(surf, head_c, (hx, hy), 2)
    pygame.draw.polygon(surf, bill, [(hx - 2, hy), (hx - 4, hy - 1), (hx - 4, hy + 1), (hx - 2, hy + 1)])
    pygame.draw.circle(surf, (22, 20, 18), (hx - 1, hy - 1), 1)


# ── pools → foreground_variants rows ──────────────────────────────────────────

def _V(palette, **attrs):
    return fv.Variant(palette=palette, attrs=dict(attrs))


def _build_dogs():
    return [
        _V(dict(coat=(176, 150, 110), coat_dk=(120, 98, 66), belly=(206, 188, 150)),
           build=1.05, leg=1.15, length=1.30, chest=0.85, head=0.92, tail="low", ear="drop", muzzle="long"),
        _V(dict(coat=(150, 102, 64), coat_dk=(104, 68, 42), belly=(196, 160, 110)),
           build=0.95, leg=0.52, length=1.45, chest=1.05, head=1.0, tail="stub", ear="bigprick", muzzle="med"),
        _V(dict(coat=(214, 208, 196), coat_dk=(150, 144, 132), belly=(226, 222, 212)),
           build=0.80, leg=0.92, length=0.98, chest=1.10, head=0.90, fluffy=True, tail="plume", ear="prick", muzzle="med"),
        _V(dict(coat=(196, 130, 74), coat_dk=(140, 86, 46), belly=(228, 206, 172)),
           build=0.98, leg=0.80, length=1.0, chest=1.12, head=0.92, fluffy=True, tail="tightcurl", ear="prick", muzzle="short"),
        _V(dict(coat=(150, 124, 96), coat_dk=(104, 84, 64), belly=(186, 166, 142)),
           build=0.94, leg=0.74, length=1.06, chest=1.02, head=1.10, tail="lowpup", ear="longdrop", muzzle="short"),
    ]


def _build_critters():
    return [
        _V(dict(body=(120, 112, 104), body_dk=(76, 70, 66), accent=(168, 120, 118)), kind="cat"),
        _V(dict(body=(204, 190, 170), body_dk=(150, 130, 104), accent=(176, 70, 60)), kind="hen"),
        _V(dict(body=(142, 144, 154), body_dk=(96, 98, 108), accent=(108, 120, 152)), kind="pigeons"),
        _V(dict(body=(212, 206, 192), body_dk=(150, 140, 120), accent=(96, 120, 96)), kind="duck"),
    ]


_CRITTER_KINDS = ("cat", "hen", "pigeons", "duck")


def critter_index(kind):
    """Pool index of a critter by kind, so scenes can place a specific animal."""
    return _CRITTER_KINDS.index(kind)


fv.register("dog", _build_dogs())
fv.register("critter", _build_critters())

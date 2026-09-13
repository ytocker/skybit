"""PUFFERFISH store skin — a spiky, googly-eyed blowfish.

A round inflated body studded with short blunt spines, a big two-eyed beaky
face, and a forked tail + pectoral fins. The tail + oriented face give a clear
front→back axis and the spines are short/irregular with a clear gap over the
face, so the shape reads as a FISH rather than a radial sun. The inflate gag
plays on the down-stroke: the body swells, the spines flare a touch, and the
whole ball brightens, then deflates on the up-stroke.

Contract (mirrors game/animal_skins.py so it slots into the merged registry):
  * `build_pufferfish(wing_angle_deg) -> pygame.Surface` — one flat frame on a
    64×84 SRCALPHA canvas, body mass pinned at (BCX,BCY)=(32,44) every frame so
    the fixed collision circle stays fair even fully inflated.
  * `get_pufferfish = _make_prebuilt_skin(build_pufferfish)` — cached getter.
  * `BUILDERS = {"skin_pufferfish": get_pufferfish}`.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse,
)

# ── tall-canvas constants (match game/animal_skins.py exactly) ───────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # body centre → (32, 44); fixed every frame


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter (local copy)."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(angle_deg):
    """0..1 'wing is up' factor. _WING_ANGLES runs 50 (down) → -40 (up)."""
    return (angle_deg + 40) / 90.0


def _inflate(angle_deg):
    """1.0 fully INFLATED on the down-pose → ~0.0 deflated on the up-pose."""
    return 1.0 - _flap(angle_deg)


def _shade(col, f):
    return tuple(max(0, min(255, int(c * f))) for c in col)


def _eye(surf, cx, cy, r, *, iris=(52, 36, 14), white=(255, 250, 240)):
    """Friendly round eye: a real white margin (iris r-2 so the sclera shows all
    around, never a black socket) + a fat top-left catchlight."""
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    pygame.draw.circle(surf, (255, 255, 255),
                       (cx - r // 3, cy - r // 3), max(1, r // 2))


def _radial_body(surf, cx, cy, rx, ry, core, mid, edge):
    """Sphere value structure: dark rim → mid mass → light core (up-left) + a
    crisp specular, so the ball reads as a volume, not a flat disc."""
    _aaellipse(surf, edge, (cx + 1, cy + 1), rx, ry)
    _aaellipse(surf, mid,  (cx, cy), rx - 1, ry - 1)
    _aaellipse(surf, core, (cx - 2, cy - 2), rx - 5, ry - 5)
    _aaellipse(surf, _shade(core, 1.10), (cx - 5, cy - 6), 4, 3)


def _tail_fin(surf, x, y, size, col_dark, col_light, *, flip=False, ribs=True):
    """A FORKED fan tail fin sweeping back with a V-notch trailing edge — the
    front→back axis that keeps the puffer reading as a fish, not a sun."""
    s = -1 if flip else 1
    bx = x - s * size
    notch = x - s * int(size * 0.5)
    pygame.draw.polygon(surf, col_dark, [
        (x, y - size // 2), (bx, y - size), (notch, y),
        (bx, y + size), (x, y + size // 2)])
    pygame.draw.polygon(surf, col_light, [
        (x, y - size // 3), (x - s * (size - 2), y - size + 2),
        (notch + s, y), (x - s * (size - 2), y + size - 2),
        (x, y + size // 3)])
    if ribs:
        for ry in (-size + 3, 0, size - 3):
            pygame.draw.line(surf, col_dark, (x, y + ry // 3),
                             (x - s * (size - 1), y + ry), 1)


def _side_fin(surf, x, y, size, col_dark, col_light, *, flip=False):
    """A small pectoral fin flicking out from the body side."""
    s = -1 if flip else 1
    pygame.draw.polygon(surf, col_dark, [(x, y - size), (x + s * size, y), (x, y + size)])
    pygame.draw.polygon(surf, col_light,
                        [(x, y - size + 1), (x + s * (size - 1), y),
                         (x, y + size - 1)])


def _spots(surf, cx, cy, col, seed_pts):
    """A few small dark spots (the aquatic tell). Fixed offsets → stable frames."""
    for dx, dy, rr in seed_pts:
        pygame.draw.circle(surf, col, (cx + dx, cy + dy), rr)


def _spike_field(n, *, base=0.7, var=0.5, gap=(-0.6, 0.6), seed=0):
    """`n` stub-spike placements wrapped around the body with a deterministic
    length jitter (irregular bumpy skin, never even rays) and a clear angular
    `gap` over the face so the studs never close into a radial halo. Angles in
    radians: 0 = front (+x), -pi/2 = top. No RNG → the 4 cached frames are stable."""
    out = []
    glo, ghi = gap if gap else (1.0, -1.0)
    for i in range(n):
        a = -math.pi + (2 * math.pi) * (i + 0.5) / n
        if gap and glo <= a <= ghi:
            continue
        ls = base + var * (((i * 5 + seed * 3) % 7) / 6.0)
        out.append((a, ls))
    return out


def _stub_spikes(surf, cx, cy, rx, ry, length, col_base, col_tip, placements):
    """Short, BLUNT cone spines at fixed (angle, scale) placements — stubby and
    staggered so they read as bumpy puffer skin, never as solar rays."""
    for a, ls in placements:
        bx, by = math.cos(a), math.sin(a)
        root = (cx + bx * (rx - 2), cy + by * (ry - 2))
        ln = length * ls
        tx, ty = -by, bx
        w = 2.4
        p_l = (root[0] + tx * w, root[1] + ty * w)
        p_r = (root[0] - tx * w, root[1] - ty * w)
        tip = (cx + bx * (rx + ln), cy + by * (ry + ln))
        pygame.draw.polygon(surf, col_base, [p_l, p_r, tip])
        pygame.draw.line(surf, col_tip, root, tip, 1)


# ── palette ──────────────────────────────────────────────────────────────────
_CORE = (248, 210, 128)         # warm sandy-amber body core
_MID  = (224, 162, 80)
_EDGE = (190, 124, 44)
_BELLY = (248, 228, 184)
_SPIKE_D = (176, 116, 26)
_SPIKE_T = (248, 206, 110)
_SPOT  = (150, 100, 26)
_FIN_D = (176, 116, 26)
_FIN_L = (236, 186, 90)
_DARK  = (58, 42, 18)
_TEETH = (255, 243, 214)
_BLUSH = (255, 168, 120)

# Short spikes wrapping the body with the front face kept clear.
_SPK = _spike_field(13, base=0.55, var=0.4, gap=(-0.8, 0.6), seed=5)


def build_pufferfish(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    f = _flap(wing_angle_deg)
    r = 14 + int(inf * 2)
    cx, cy = BCX, BCY
    bf = 0.92 + 0.16 * inf
    core, mid, edge = _shade(_CORE, bf), _shade(_MID, bf), _shade(_EDGE, bf)
    fin_d, fin_l = _shade(_FIN_D, bf), _shade(_FIN_L, bf)

    # Swishy forked tail (back) sways with the flap + far pectoral fin.
    _tail_fin(surf, cx - r + 1, cy + 2 + int(f * 2), 10, fin_d, fin_l)
    _side_fin(surf, cx - 5, cy - 2, 4, fin_d, fin_l, flip=True)

    # Spikes wrapping the body — inflate length bonus capped so the puffed frame
    # never closes into a full radial halo.
    spk = 4 + int(inf * 2)
    _stub_spikes(surf, cx, cy, r, r, spk, _shade(_SPIKE_D, bf),
                 _shade(_SPIKE_T, bf), _SPK)

    # Body + belly + a couple of dark spots.
    _radial_body(surf, cx, cy, r, r, core, mid, edge)
    _aaellipse(surf, _shade(_BELLY, bf), (cx - 1, cy + 5), r - 6, r - 7)
    _spots(surf, cx, cy, _shade(_SPOT, bf), [(-6, 7, 1), (5, 7, 1)])

    # Near pectoral fin.
    _side_fin(surf, cx + r - 4, cy + 6, 5, fin_d, fin_l)

    # ── Face: oversized convergent googly eyes + a bold two-tooth beak ──
    fx, fy = cx + 1, cy - 3
    for sx in (-9, 9):                       # blush with a darker rim for night
        pygame.draw.circle(surf, _BLUSH, (fx + sx, fy + 6), 2)
        pygame.draw.circle(surf, (220, 130, 90), (fx + sx, fy + 6), 2, 1)
    _eye(surf, fx - 5, fy, 5, iris=_DARK)
    _eye(surf, fx + 5, fy, 5, iris=_DARK)
    pygame.draw.circle(surf, _DARK, (fx - 4, fy + 1), 2)     # pupils converged in
    pygame.draw.circle(surf, _DARK, (fx + 4, fy + 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), (fx - 6, fy - 1), 1)
    pygame.draw.circle(surf, (255, 255, 255), (fx + 4, fy - 1), 1)
    # Beak: one bold lip line + two outlined teeth that punch at 40px.
    pygame.draw.line(surf, (96, 60, 34), (fx - 5, fy + 7), (fx + 5, fy + 7), 2)
    for tx in (fx - 4, fx + 1):
        pygame.draw.rect(surf, _TEETH, (tx, fy + 8, 3, 3))
        pygame.draw.rect(surf, (120, 78, 44), (tx, fy + 8, 3, 3), 1)
    return surf


get_pufferfish = _make_prebuilt_skin(build_pufferfish)


BUILDERS = {
    "skin_pufferfish": get_pufferfish,
}

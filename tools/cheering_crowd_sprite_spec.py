"""CelebrationCrowd — sprite + layout spec, round-3 SHIP-READY package.

Drop-in helpers for ``game/entities.py``. The orchestrator wires spawn /
scroll / cull / render around this module; everything below is the
PURE drawing surface — no entity-state coupling — so it can be lifted
verbatim into a ``CelebrationCrowd`` class without rewiring.

Contents
--------
* Palette constants (sourced from ``CelebrationBunting`` so the crowd
  shares the cycle-finale colour story).
* Eight per-parrot plumage rolls.
* Seven instrument primitives (drum / trumpet / flag / pom-pom /
  tambourine / megaphone / party-horn). The megaphone carries the
  round-3 cream rim highlight.
* ``draw_parrot`` — the macaw figure with mirror + jump + raise/wave
  pose + optional instrument callable.
* ``CROWD_LAYOUT`` — the round-3 R2-1 composition, with per-parrot
  ``dx`` (offset from the finish-line stripe), plumage index, base
  jump height, pose, mirror flag, instrument kind, and bob phase
  offset for the animation callback.
* ``draw_crowd`` — convenience that walks ``CROWD_LAYOUT`` and renders
  every parrot at the right offsets. Animated callers should compute
  per-frame ``jump = base_jump + sin(t * 2π * BOB_HZ + phase) * BOB_AMP``
  and pass that into ``draw_parrot``.

All silhouettes were sized to survive 1× during the ~5 s post-chest
celebration window. Round-3 fixes baked in:

  1. Leftmost flag pole shifted -2 px (``dx=-2`` on the flag instrument).
  2. Megaphone carries a cream rim highlight on the outer cone edge
     plus a 1-px bell-corner specular so the cone reads at 1×.
  3. Right-side jump rhythm staggered — bob phases now span the
     unit circle (0, π·2/3, π·4/3, π·1/3 across the 4 right parrots)
     so apex beats don't pair up.
"""
from __future__ import annotations

import math
from typing import Callable, Optional, Tuple

import pygame

# Bunting family — these are the canonical cycle-finale colours.
# In the integrated class, source these from
# ``CelebrationBunting.COLOURS`` / ``.INK`` instead of redefining them.
GOLD  = (255, 220, 110)
RED   = (220,  64,  32)
BLUE  = ( 96, 176, 232)
CREAM = (252, 244, 218)
INK   = ( 30,  20,   8)


# ── colour helper ─────────────────────────────────────────────────────────

def _shade(col: Tuple[int, int, int], d: int) -> Tuple[int, int, int]:
    return (
        max(0, min(255, col[0] + d)),
        max(0, min(255, col[1] + d)),
        max(0, min(255, col[2] + d)),
    )


# ── instrument primitives ──────────────────────────────────────────────────
# Each takes (surf, anchor_x, anchor_y) where the anchor is the parrot's
# inside-wing-tip in world coords. Sizes are tuned so each silhouette
# reads at 1× during the post-chest scroll.

def draw_pompom(surf: pygame.Surface, cx: int, cy: int,
                fluff=GOLD, accent=RED) -> None:
    """Pom-pom — 5-px cluster with radial spikes so the fuzzy edge
    survives at 1×. Two-tone reads as a bunting-coloured cheer prop."""
    spikes = (
        (-3, 0), (3, 0), (0, -3), (0, 3),
        (-2, -2), (2, -2), (-2, 2), (2, 2),
    )
    for dx, dy in spikes:
        pygame.draw.circle(surf, fluff, (cx + dx, cy + dy), 1)
    pygame.draw.circle(surf, fluff, (cx, cy), 3)
    pygame.draw.circle(surf, accent, (cx - 1, cy - 1), 1)
    pygame.draw.circle(surf, _shade(fluff, -50), (cx, cy), 3, 1)


def draw_trumpet(surf: pygame.Surface, x: int, y: int, body=GOLD) -> None:
    """Tiny upraised trumpet — bell ~4 px so the funnel reads at 1×."""
    pygame.draw.line(surf, body, (x, y), (x + 5, y - 5), 2)
    bell = [
        (x + 5, y - 5),
        (x + 10, y - 9),
        (x + 9, y - 11),
        (x + 4, y - 7),
    ]
    pygame.draw.polygon(surf, body, bell)
    pygame.draw.polygon(surf, _shade(body, -70), bell, 1)
    pygame.draw.circle(surf, CREAM, (x + 5, y - 5), 1)


def draw_drum(surf: pygame.Surface, cx: int, cy: int,
              shell=RED, rim=CREAM, stick=INK) -> None:
    """Snare drum slung at the waist. Two crossed sticks above the rim
    sell ``percussion`` at 1×."""
    w, h = 16, 10
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surf, shell, rect, border_radius=2)
    pygame.draw.rect(surf, rim, (rect.x, rect.y, rect.w, 2))
    pygame.draw.rect(surf, rim, (rect.x, rect.y + rect.h - 2, rect.w, 2))
    for k in range(4):
        kx = rect.x + 2 + k * 4
        pygame.draw.line(surf, _shade(shell, -50),
                         (kx, rect.y + 2),
                         (kx + 1, rect.y + rect.h - 2), 1)
    pygame.draw.circle(surf, _shade(shell, -25), (cx, cy), 3)
    pygame.draw.circle(surf, INK, (cx, cy), 3, 1)
    pygame.draw.rect(surf, INK, rect, 1, border_radius=2)
    pygame.draw.line(surf, stick, (cx - 5, cy - 8), (cx - 1, cy - 2), 1)
    pygame.draw.line(surf, stick, (cx + 5, cy - 8), (cx + 1, cy - 2), 1)


def draw_megaphone(surf: pygame.Surface, x: int, y: int,
                   body=RED, mouth=CREAM) -> None:
    """Megaphone pointed up-and-right. Round-3 polish: 1-px CREAM
    highlight along the outer cone edge + a 1-px CREAM specular on
    the bell rim corner so the cone reads as a cone at 1× scale."""
    pts = [
        (x, y),
        (x + 11, y - 8),
        (x + 13, y - 4),
        (x + 3, y + 3),
    ]
    pygame.draw.polygon(surf, body, pts)
    pygame.draw.polygon(surf, INK, pts, 1)
    # Round-3 fix: CREAM highlight on the OUTER (upper) cone edge.
    pygame.draw.line(surf, mouth, (x + 1, y - 1), (x + 11, y - 8), 1)
    # Mouthpiece (CREAM) ring at the open end.
    pygame.draw.line(surf, mouth, (x + 11, y - 8), (x + 13, y - 4), 2)
    # Round-3 fix: 1-px CREAM specular on the bell-corner so the bell
    # opening catches the eye at 1×.
    if 0 <= x + 12 < surf.get_width() and 0 <= y - 7 < surf.get_height():
        surf.set_at((x + 12, y - 7), mouth)
    # Grip stripe across the throat — hand-anchor cue.
    pygame.draw.line(surf, _shade(body, -55), (x + 2, y), (x + 7, y - 4), 1)


def draw_flag(surf: pygame.Surface, x_base: int, y_base: int,
              pole_h: int = 20, banner=GOLD, pole=CREAM) -> None:
    """Festive flag — banner droops 5-verts so the trailing edge
    catches wind, not a rectangle on a stick."""
    pygame.draw.line(surf, pole, (x_base, y_base),
                     (x_base, y_base - pole_h), 2)
    pygame.draw.line(surf, _shade(pole, -60), (x_base, y_base),
                     (x_base, y_base - pole_h), 1)
    banner_pts = [
        (x_base, y_base - pole_h),
        (x_base + 11, y_base - pole_h + 2),
        (x_base + 10, y_base - pole_h + 4),
        (x_base + 11, y_base - pole_h + 7),
        (x_base, y_base - pole_h + 6),
    ]
    pygame.draw.polygon(surf, banner, banner_pts)
    pygame.draw.polygon(surf, _shade(banner, -60), banner_pts, 1)


def draw_tambourine(surf: pygame.Surface, cx: int, cy: int,
                    rim=CREAM, jingle=GOLD) -> None:
    """Tambourine — CREAM rim + 4 GOLD jingles around the disc."""
    pygame.draw.circle(surf, rim, (cx, cy), 6)
    pygame.draw.circle(surf, _shade(rim, -60), (cx, cy), 6, 1)
    pygame.draw.circle(surf, CREAM, (cx, cy), 3)
    pygame.draw.circle(surf, _shade(rim, -40), (cx, cy), 3, 1)
    for k in range(4):
        ang = k * (math.pi / 2) + 0.4
        jx = cx + int(math.cos(ang) * 6)
        jy = cy + int(math.sin(ang) * 6)
        pygame.draw.circle(surf, jingle, (jx, jy), 2)
        pygame.draw.circle(surf, _shade(jingle, -70), (jx, jy), 2, 1)


def draw_party_horn(surf: pygame.Surface, x: int, y: int,
                    body=GOLD, tip=RED, streamer=CREAM) -> None:
    """Party horn — GOLD blowpipe + RED curled tip + CREAM streamer."""
    pygame.draw.line(surf, body, (x, y), (x + 8, y - 3), 3)
    pygame.draw.line(surf, _shade(body, -60), (x, y), (x + 8, y - 3), 1)
    pygame.draw.line(surf, tip, (x + 8, y - 3), (x + 12, y - 6), 2)
    pygame.draw.line(surf, streamer, (x + 12, y - 6), (x + 14, y - 4), 2)
    pygame.draw.line(surf, streamer, (x + 14, y - 4), (x + 16, y - 7), 1)
    pygame.draw.circle(surf, streamer, (x + 16, y - 7), 1)


# ── plumage rolls ──────────────────────────────────────────────────────────
# (body, belly, wing_accent, beak) — varying these per parrot makes the
# crowd read as a flock instead of clones.

PLUMAGE: Tuple[Tuple[Tuple[int, int, int], ...], ...] = (
    (RED,   CREAM, GOLD,  GOLD),
    (BLUE,  CREAM, GOLD,  GOLD),
    (GOLD,  RED,   BLUE,  RED),
    (CREAM, RED,   BLUE,  RED),
    (RED,   GOLD,  CREAM, GOLD),
    (BLUE,  GOLD,  CREAM, GOLD),
    (GOLD,  CREAM, RED,   RED),
    (CREAM, BLUE,  RED,   GOLD),
)


# ── parrot figure ─────────────────────────────────────────────────────────

def draw_parrot(surf: pygame.Surface, x: int, ground_y: int,
                plumage_idx: int = 0, jump: int = 0,
                pose: str = "raise",
                instrument: Optional[Callable[[pygame.Surface, int, int], None]] = None,
                mirror: bool = False) -> None:
    """Round-bodied macaw (Pip cousin). ~22 px wide × 28 px tall.

    ``jump`` = pixel lift above ``ground_y`` (the runtime animator should
    pass the integer ``base_jump + sin(...)`` so the bob is per-frame).
    ``pose`` ∈ {"raise", "wave"} — both wings up vs one out / one up.
    ``mirror`` flips beak + near-wing + eye so the figure faces the
    finish-line stripe; use mirror=True for crowd parrots LEFT of the
    stripe.
    """
    body, belly, wing_accent, beak = PLUMAGE[plumage_idx % len(PLUMAGE)]
    feet_y = ground_y - 1 - jump

    # Shadow softer + smaller on jumping figures so the lift reads.
    shadow_alpha = 90 if jump == 0 else 55
    shadow = pygame.Surface((24, 5), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, shadow_alpha), (0, 0, 24, 5))
    surf.blit(shadow, (x - 12, ground_y))

    body_h = 18
    body_top = feet_y - body_h

    # Feet — beak-coloured toes; spread so the stance reads at 1×.
    foot_col = _shade(beak, -20) if beak != INK else INK
    pygame.draw.line(surf, foot_col, (x - 3, feet_y - 1),
                     (x - 4, feet_y + 1), 2)
    pygame.draw.line(surf, foot_col, (x + 3, feet_y - 1),
                     (x + 4, feet_y + 1), 2)

    # Round body.
    pygame.draw.ellipse(surf, body, (x - 8, body_top, 16, body_h))
    pygame.draw.ellipse(surf, _shade(body, -55),
                        (x - 8, body_top, 16, body_h), 1)

    # Belly patch.
    pygame.draw.ellipse(surf, belly, (x - 5, body_top + 7, 10, 10))
    pygame.draw.ellipse(surf, _shade(belly, -40),
                        (x - 5, body_top + 7, 10, 10), 1)

    # Head.
    head_cy = body_top + 3
    pygame.draw.ellipse(surf, body, (x - 7, head_cy - 7, 14, 12))
    pygame.draw.ellipse(surf, _shade(body, -65),
                        (x - 7, head_cy - 7, 14, 12), 1)

    # Beak — direction depends on ``mirror``.
    if mirror:
        beak_pts = [
            (x - 6, head_cy),
            (x - 11, head_cy + 1),
            (x - 6, head_cy + 3),
        ]
    else:
        beak_pts = [
            (x + 6, head_cy),
            (x + 11, head_cy + 1),
            (x + 6, head_cy + 3),
        ]
    pygame.draw.polygon(surf, beak, beak_pts)
    pygame.draw.polygon(surf, _shade(beak, -70), beak_pts, 1)

    # Eye — CREAM whites + INK pupil, off-centre toward the beak.
    eye_x = x - 3 if mirror else x + 3
    pygame.draw.circle(surf, CREAM, (eye_x, head_cy - 1), 2)
    pygame.draw.circle(surf, INK, (eye_x + (-1 if mirror else 1),
                                   head_cy - 1), 1)

    # Shouting mouth — short ink notch at the beak base.
    mouth_x = x - 5 if mirror else x + 5
    pygame.draw.line(surf, INK, (mouth_x, head_cy + 2),
                     (mouth_x + (-1 if mirror else 1), head_cy + 3), 1)

    # Wings act as arms. "raise" → both up; "wave" → outside wing held
    # out / inside wing raised.
    near_x = x - 6 if mirror else x + 6
    near_dir = -1 if mirror else 1
    far_x = -near_x + 2 * x

    if pose == "raise":
        pygame.draw.polygon(surf, _shade(body, -25), [
            (far_x, body_top + 4),
            (far_x + (-near_dir) * 4, body_top - 5),
            (far_x + (-near_dir), body_top - 4),
            (far_x + near_dir * 2, body_top + 5),
        ])
        pygame.draw.line(surf, wing_accent,
                         (far_x + (-near_dir) * 4, body_top - 5),
                         (far_x + (-near_dir), body_top - 4), 2)
        pygame.draw.polygon(surf, _shade(body, -25), [
            (near_x, body_top + 4),
            (near_x + near_dir * 4, body_top - 5),
            (near_x + near_dir, body_top - 4),
            (near_x + (-near_dir) * 2, body_top + 5),
        ])
        pygame.draw.line(surf, wing_accent,
                         (near_x + near_dir * 4, body_top - 5),
                         (near_x + near_dir, body_top - 4), 2)
        if instrument is not None:
            instrument(surf, near_x + near_dir * 4, body_top - 5)
    else:  # wave
        pygame.draw.polygon(surf, _shade(body, -25), [
            (far_x, body_top + 4),
            (far_x + (-near_dir) * 5, body_top + 2),
            (far_x + (-near_dir) * 3, body_top + 5),
            (far_x + near_dir, body_top + 8),
        ])
        pygame.draw.polygon(surf, _shade(body, -25), [
            (near_x, body_top + 4),
            (near_x + near_dir * 4, body_top - 6),
            (near_x + near_dir, body_top - 5),
            (near_x + (-near_dir) * 2, body_top + 5),
        ])
        pygame.draw.line(surf, wing_accent,
                         (near_x + near_dir * 4, body_top - 6),
                         (near_x + near_dir, body_top - 5), 2)
        if instrument is not None:
            instrument(surf, near_x + near_dir * 4, body_top - 6)


# ── composite layout — round-3 polished R2-1 ────────────────────────────────
# Each entry feeds straight into ``draw_parrot``. ``dx`` is the world-x
# offset from the finish-line stripe (negative = LEFT of stripe). The
# orchestrator should anchor the crowd at the stripe world-x and pass
# ``stripe_x + dx`` as the parrot ``x``.
#
# ``base_jump`` is the static lift in pixels. For the live animation,
# add a sinusoidal bob:
#     jump = base_jump + int(round(sin(t * 2π * BOB_HZ + bob_phase) * BOB_AMP))
# with ``BOB_HZ ≈ 1.2`` (cheering cadence) and ``BOB_AMP ≈ 2`` px.
#
# ``instrument`` is a label; the runtime maps label → callable via
# ``INSTRUMENT_FACTORIES`` below so the spec stays JSON-friendly.

# Round-3 fix #1: leftmost flag's instrument carries ``flag_dx=-2`` so
#   the pole sits 2 px LEFT of the parrot's wing-tip anchor.
# Round-3 fix #3: right-side bob_phase values span the unit circle
#   (0, π·2/3, π·4/3, π·1/3 across the 4 right parrots) so apex beats
#   don't pair up — combined with the staggered base_jumps (0/5/3/4)
#   the bob rhythm reads as ``crowd``, not metronome.

CROWD_LAYOUT: Tuple[dict, ...] = (
    # LEFT (mirrored, facing the stripe) — flag · pom · drum.
    {
        "dx": -130, "plumage_idx": 0, "base_jump": 4, "pose": "raise",
        "mirror": True, "instrument": "flag",
        "instrument_kwargs": {"flag_dx": -2, "pole_h": 20, "banner": GOLD},
        "bob_phase": 0.0,
    },
    {
        "dx": -95, "plumage_idx": 5, "base_jump": 0, "pose": "wave",
        "mirror": True, "instrument": "pompom",
        "instrument_kwargs": {"fluff": GOLD, "accent": RED},
        "bob_phase": math.pi * (2 / 3),
    },
    {
        "dx": -60, "plumage_idx": 2, "base_jump": 3, "pose": "raise",
        "mirror": True, "instrument": "drum",
        "instrument_kwargs": {"shell": RED, "rim": CREAM},
        "bob_phase": math.pi * (4 / 3),
    },
    # RIGHT (facing the stripe naturally) — tambourine · trumpet ·
    # megaphone · party-horn.
    {
        "dx": 24, "plumage_idx": 1, "base_jump": 0, "pose": "raise",
        "mirror": False, "instrument": "tambourine",
        "instrument_kwargs": {"rim": CREAM, "jingle": GOLD},
        "bob_phase": 0.0,
    },
    {
        "dx": 60, "plumage_idx": 6, "base_jump": 5, "pose": "raise",
        "mirror": False, "instrument": "trumpet",
        "instrument_kwargs": {"body": GOLD},
        "bob_phase": math.pi * (2 / 3),
    },
    {
        # Round-3 fix #3 lives here: base_jump 0→3 so the megaphone
        # parrot no longer shares a jump=0 doublet with the tambourine.
        "dx": 100, "plumage_idx": 3, "base_jump": 3, "pose": "wave",
        "mirror": False, "instrument": "megaphone",
        "instrument_kwargs": {"body": RED, "mouth": CREAM},
        "bob_phase": math.pi * (4 / 3),
    },
    {
        "dx": 140, "plumage_idx": 7, "base_jump": 4, "pose": "raise",
        "mirror": False, "instrument": "party_horn",
        "instrument_kwargs": {"body": GOLD, "tip": RED, "streamer": CREAM},
        "bob_phase": math.pi * (1 / 3),
    },
)


# Anchor offsets baked into each instrument call so the prop sits in the
# right spot relative to the parrot's wing-tip. The orchestrator should
# resolve the label via this map before calling ``draw_parrot``.

def _flag_factory(kwargs):
    flag_dx = kwargs.get("flag_dx", 0)
    pole_h = kwargs.get("pole_h", 20)
    banner = kwargs.get("banner", GOLD)
    return lambda s, hx, hy: draw_flag(s, hx + flag_dx, hy + 6,
                                       pole_h=pole_h, banner=banner)


def _pompom_factory(kwargs):
    fluff = kwargs.get("fluff", GOLD)
    accent = kwargs.get("accent", RED)
    return lambda s, hx, hy: draw_pompom(s, hx - 1, hy - 1, fluff, accent)


def _drum_factory(kwargs):
    shell = kwargs.get("shell", RED)
    rim = kwargs.get("rim", CREAM)
    return lambda s, hx, hy: draw_drum(s, hx + 4, hy + 12, shell, rim)


def _tambourine_factory(kwargs):
    rim = kwargs.get("rim", CREAM)
    jingle = kwargs.get("jingle", GOLD)
    return lambda s, hx, hy: draw_tambourine(s, hx + 2, hy - 1, rim, jingle)


def _trumpet_factory(kwargs):
    body = kwargs.get("body", GOLD)
    return lambda s, hx, hy: draw_trumpet(s, hx, hy, body)


def _megaphone_factory(kwargs):
    body = kwargs.get("body", RED)
    mouth = kwargs.get("mouth", CREAM)
    return lambda s, hx, hy: draw_megaphone(s, hx, hy + 2, body, mouth)


def _party_horn_factory(kwargs):
    body = kwargs.get("body", GOLD)
    tip = kwargs.get("tip", RED)
    streamer = kwargs.get("streamer", CREAM)
    return lambda s, hx, hy: draw_party_horn(s, hx, hy, body, tip, streamer)


INSTRUMENT_FACTORIES = {
    "flag":       _flag_factory,
    "pompom":     _pompom_factory,
    "drum":       _drum_factory,
    "tambourine": _tambourine_factory,
    "trumpet":    _trumpet_factory,
    "megaphone":  _megaphone_factory,
    "party_horn": _party_horn_factory,
}


# Animation constants — feed these into the per-frame jump calc when
# ``CelebrationCrowd.draw`` runs. Tuned so the crowd feels alive without
# vibrating; matches the ``raise`` pose's 1-px arm bob at the wing-tips.
BOB_HZ = 1.2
BOB_AMP = 2


def draw_crowd(surf: pygame.Surface, stripe_x: int, ground_y: int,
               t: float = 0.0) -> None:
    """Walk ``CROWD_LAYOUT`` and render every parrot. ``t`` is the
    elapsed time in seconds — pass 0.0 for a static screenshot, or the
    live world clock for the cheering bob animation.

    The integrated ``CelebrationCrowd`` class will own ``t`` as
    ``self.t`` and tick it in ``update(dt)``; this function is the
    single-shot draw path it should delegate to.
    """
    for spec in CROWD_LAYOUT:
        bob = int(round(math.sin(t * 2 * math.pi * BOB_HZ
                                 + spec["bob_phase"]) * BOB_AMP))
        jump = spec["base_jump"] + bob
        factory = INSTRUMENT_FACTORIES[spec["instrument"]]
        instrument = factory(spec["instrument_kwargs"])
        draw_parrot(surf,
                    x=stripe_x + spec["dx"],
                    ground_y=ground_y,
                    plumage_idx=spec["plumage_idx"],
                    jump=jump,
                    pose=spec["pose"],
                    instrument=instrument,
                    mirror=spec["mirror"])

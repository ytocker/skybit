"""
Skybit intro cinematic — a calm 12-second journey that introduces Pip, his
employer Mr. Garrick, and the day-cycle world before the menu fades in.

Played once on first launch (gated by the `intro_seen` flag in
`skybit_save.json`), and skippable on any tap/click/key.

Everything is drawn procedurally with the same primitives the game uses, so
the cut into the menu is seamless. No new asset files. No new dependencies.

Composition is structured as five gentle beats dispatched by elapsed-time:
  0.0–2.5  "Dawn"        – mist + pillar + parcel + mailbag, light grows
  2.5–4.5  "The hand-off" – Mr. Garrick on a neighbour pillar, parcel appears
  4.5–10.0 "The journey"  – flight through golden hour → night → sunrise
  10.0–11.0 "Arrival"     – Pip alights at a sunlit pillar with a mailbox
  11.0–12.0 "Title"       – Skybit logotype + "TAP TO FLY"

The brief asks for an MP4 deliverable; this codebase has no video pipeline,
so we ship the in-engine cinematic and let downstream marketing record it
externally if a literal MP4 is needed.
"""
from __future__ import annotations

import math
import pygame

from game.config import W, H, GROUND_Y
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    blit_glow, lerp_color,
    UI_GOLD, UI_CREAM, WHITE, NEAR_BLACK,
)
from game import biome as _biome
from game import parrot as _parrot
from game.pillar_variants import draw_pillar_pair
from game.hud import draw_skybit_wordmark, _font
from game import audio as _audio


DURATION = 12.0


# ── small easing helpers ─────────────────────────────────────────────────────

def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def _smoothstep(t: float) -> float:
    t = _clamp01(t)
    return t * t * (3.0 - 2.0 * t)


def _ease_out_cubic(t: float) -> float:
    t = _clamp01(t)
    inv = 1.0 - t
    return 1.0 - inv * inv * inv


# ── procedural sprites (built lazily, then cached) ───────────────────────────

_SPRITES: dict = {}


def _build_parcel() -> pygame.Surface:
    """A wrapped-present courier package: kraft-tan box with a red ribbon
    cross and a red bow. Ported from v2_skybit's surprise-box drawing
    geometry but with the question-mark glyph stripped out and a courier
    colour palette."""
    BOX_BASE   = (180, 130,  80)   # warm kraft tan
    BOX_SHADE  = (110,  75,  40)
    BOX_HI     = (220, 175, 120)
    RIBBON     = (200,  50,  60)
    RIBBON_HI  = (255, 110, 100)
    BOW_FILL   = (200,  50,  60)
    BOW_HI     = (255, 130, 120)
    DK_OUTLINE = ( 26,  10,  12)

    SIZE = 56
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    BOX_W, BOX_H = 40, 34
    cx, cy = SIZE // 2, SIZE // 2 + 2
    rect = pygame.Rect(cx - BOX_W // 2, cy - BOX_H // 2 + 2, BOX_W, BOX_H)

    # Drop shadow
    sh = pygame.Surface((BOX_W + 8, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 22, 130), sh.get_rect())
    surf.blit(sh, (cx - (BOX_W + 8) // 2, rect.bottom - 4))

    # Box body: dark frame, vertical-gradient fill, top sheen — same trick
    # as the surprise-box reference.
    pygame.draw.rect(surf, DK_OUTLINE, rect.inflate(4, 4), border_radius=8)
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        col = lerp_color(BOX_BASE, BOX_SHADE, t) + (255,)
        body.fill(col, pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=6)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)
    pygame.draw.line(surf, BOX_HI,
                     (rect.x + 4, rect.y + 3),
                     (rect.right - 5, rect.y + 3), 2)

    # Ribbon: vertical stripe down the middle
    rv_w = 6
    rvx = rect.centerx - rv_w // 2
    pygame.draw.rect(surf, RIBBON, (rvx, rect.y, rv_w, rect.h))
    pygame.draw.line(surf, RIBBON_HI,
                     (rvx + 1, rect.y), (rvx + 1, rect.bottom - 1), 1)

    # Ribbon: horizontal stripe across the middle
    rh_w = 6
    rhy = rect.y + rect.h // 2 - rh_w // 2
    pygame.draw.rect(surf, RIBBON, (rect.x, rhy, rect.w, rh_w))
    pygame.draw.line(surf, RIBBON_HI, (rect.x, rhy + 1),
                     (rect.right - 1, rhy + 1), 1)

    # Bow on top — puffy two-loop with a knot and trailing tails
    bx, by = cx, rect.y - 6
    pygame.draw.ellipse(surf, DK_OUTLINE,
                        pygame.Rect(bx - 13, by - 6, 13, 12))
    pygame.draw.ellipse(surf, BOW_FILL,
                        pygame.Rect(bx - 12, by - 5, 11, 10))
    pygame.draw.ellipse(surf, DK_OUTLINE,
                        pygame.Rect(bx,       by - 6, 13, 12))
    pygame.draw.ellipse(surf, BOW_FILL,
                        pygame.Rect(bx + 1,   by - 5, 11, 10))
    pygame.draw.ellipse(surf, BOW_HI, pygame.Rect(bx - 10, by - 4, 4, 3))
    pygame.draw.ellipse(surf, BOW_HI, pygame.Rect(bx + 6,  by - 4, 4, 3))
    pygame.draw.rect(surf, DK_OUTLINE, pygame.Rect(bx - 4, by - 6, 9, 12),
                     border_radius=2)
    pygame.draw.rect(surf, BOW_FILL,  pygame.Rect(bx - 3, by - 5, 7, 10),
                     border_radius=2)
    pygame.draw.line(surf, BOW_HI, (bx - 1, by - 4), (bx - 1, by + 3), 1)
    # Trailing tails into the box
    pygame.draw.line(surf, DK_OUTLINE, (bx - 2, by + 4), (bx - 7, by + 11), 4)
    pygame.draw.line(surf, DK_OUTLINE, (bx + 2, by + 4), (bx + 7, by + 11), 4)
    pygame.draw.line(surf, BOW_FILL,   (bx - 2, by + 4), (bx - 6, by + 10), 2)
    pygame.draw.line(surf, BOW_FILL,   (bx + 2, by + 4), (bx + 6, by + 10), 2)

    # Render at full detail above, then downscale once so the parcel reads
    # tiny enough to fit under Pip while keeping a single shared size at every
    # use site (ledge / hand-off / journey carry / mailbox).
    return pygame.transform.smoothscale(surf, (22, 22))


def _build_mailbag() -> pygame.Surface:
    """A canvas satchel with a leather strap and a small brass buckle."""
    surf = pygame.Surface((48, 38), pygame.SRCALPHA)
    # Drop shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 90), (4, 30, 40, 6))
    # Body — soft canvas
    pygame.draw.ellipse(surf, (170, 145, 100), (4, 12, 40, 22))
    pygame.draw.rect(surf, (170, 145, 100), (4, 16, 40, 14))
    # Flap
    pygame.draw.polygon(surf, (140, 115, 75),
                        [(6, 12), (42, 12), (40, 22), (8, 22)])
    # Strap
    pygame.draw.line(surf, (90, 55, 35), (10, 16), (4, 6), 2)
    pygame.draw.line(surf, (90, 55, 35), (38, 16), (44, 6), 2)
    # Buckle
    pygame.draw.circle(surf, (220, 180, 70), (24, 22), 3)
    pygame.draw.circle(surf, (140, 100, 30), (24, 22), 3, 1)
    return surf


def _build_mailbox() -> pygame.Surface:
    """A small wooden mailbox on a short post, with a red flag raised."""
    surf = pygame.Surface((40, 44), pygame.SRCALPHA)
    # Post
    pygame.draw.rect(surf, (95, 70, 45), (18, 24, 4, 20))
    # Box body
    pygame.draw.rect(surf, (170, 130, 90), (8, 14, 24, 14), border_radius=3)
    # Door panel
    pygame.draw.rect(surf, (130, 95, 60), (12, 17, 16, 8), border_radius=2)
    pygame.draw.circle(surf, (220, 180, 70), (26, 21), 1)  # latch
    # Flag pole + flag (raised)
    pygame.draw.line(surf, (60, 40, 25), (32, 6), (32, 18), 2)
    pygame.draw.polygon(surf, (220, 60, 60),
                        [(32, 6), (32, 13), (24, 9)])
    return surf


def _build_garrick() -> pygame.Surface:
    """Mr. Garrick: a calm pelican silhouette in pale-pink with a white shirt
    collar and a perpetual frown beak. Simple — he's a quiet supporting role
    in the cinematic."""
    surf = pygame.Surface((64, 72), pygame.SRCALPHA)
    # Drop shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 90), (10, 60, 44, 8))
    # Tail — small
    pygame.draw.polygon(surf, (210, 175, 175),
                        [(8, 50), (20, 46), (18, 56)])
    # Body — pale pink ovate
    pygame.draw.ellipse(surf, (240, 200, 200), (10, 30, 44, 32))
    # Belly highlight
    pygame.draw.ellipse(surf, (255, 220, 220), (16, 40, 30, 20))
    # White shirt collar — two wedges meeting at a V under the head
    pygame.draw.polygon(surf, (255, 255, 255),
                        [(28, 38), (36, 38), (32, 50)])
    pygame.draw.polygon(surf, (220, 220, 220),
                        [(28, 38), (32, 50), (24, 44)])
    pygame.draw.polygon(surf, (220, 220, 220),
                        [(36, 38), (32, 50), (40, 44)])
    # Head — round dome
    pygame.draw.ellipse(surf, (240, 200, 200), (20, 12, 26, 24))
    # Eye — beady black with a tiny eye-bag arc to read "tired manager"
    pygame.draw.circle(surf, (20, 20, 30), (38, 22), 2)
    pygame.draw.arc(surf, (160, 110, 110),
                    pygame.Rect(34, 23, 10, 6), 0.0, math.pi, 1)
    # Beak — long, hooked, frown set
    pygame.draw.polygon(surf, (255, 200, 90),
                        [(40, 22), (60, 26), (58, 31), (40, 28)])
    # Lower beak (slightly drooped)
    pygame.draw.polygon(surf, (220, 160, 60),
                        [(40, 28), (58, 31), (54, 33), (40, 31)])
    # Microphone — small dark stem + bulb on the breast, suggesting the
    # "endless orders into Pip's earpiece" without dialogue.
    pygame.draw.line(surf, (40, 40, 50), (28, 50), (22, 56), 2)
    pygame.draw.circle(surf, (60, 60, 70), (22, 56), 3)
    return surf


def _get_sprite(name: str) -> pygame.Surface:
    s = _SPRITES.get(name)
    if s is None:
        if name == "parcel":   s = _build_parcel()
        elif name == "mailbag": s = _build_mailbag()
        elif name == "mailbox": s = _build_mailbox()
        elif name == "garrick": s = _build_garrick()
        else: raise KeyError(name)
        _SPRITES[name] = s
    return s


class IntroScene:
    """Owns the entire frame for the intro state.

    The scene must never compose with `World` — the App's `_render` skips its
    background/entity passes whenever `state == STATE_INTRO`.
    """

    DURATION = DURATION

    def __init__(self):
        self.t = 0.0
        self.done = False
        self._pad_started = False
        self._crackle_t = -1.0  # earpiece crackle scheduled inside beat 2
        self._title_t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        self._title_t += dt
        # Kick off the ambient pad once on the first frame so it has the full
        # length of the cinematic to breathe.
        if not self._pad_started:
            try:
                _audio.play_intro_pad()
            except Exception:
                pass
            self._pad_started = True
        # One earpiece crackle during beat 2 (the hand-off).
        if 3.0 <= self.t < 3.05 and self._crackle_t < 0:
            try:
                _audio.play_intro_crackle()
            except Exception:
                pass
            self._crackle_t = self.t
        if self.t >= self.DURATION:
            self.done = True

    def skip(self) -> None:
        self.done = True

    def render(self, surf: pygame.Surface) -> None:
        # Fallback fill in case a beat draws nothing (defensive).
        surf.fill((10, 12, 30))
        # Beats are dispatched in render() — see slices D + E.
        _dispatch_beat(self, surf)
        # SKIP affordance fades in at t=1.5 s, top-right.
        _draw_skip_pill(surf, self.t)


# ── world-paint helpers used by every beat ───────────────────────────────────

def _draw_sky(surf: pygame.Surface, phase: float) -> None:
    """Paint the biome-aware sky for `phase`, blending two adjacent buckets so
    a slowly-changing phase reads as a continuous fade. Mirrors the trick in
    `scenes.py:_draw_background`."""
    buckets = _biome.PHASE_BUCKETS
    pf = phase % 1.0
    bucket_f = pf * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    t = bucket_f - int(bucket_f)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)


def _draw_world(surf: pygame.Surface, phase: float, scroll: float,
                cloud_phase: float, ground: bool = True) -> None:
    """Sky + mountains + ground for the given phase. The journey beat keeps
    `ground=False` and lets the ground slip below frame so the camera reads
    as floating high in the sky."""
    palette = _biome.palette_for_phase(phase)
    _draw_sky(surf, phase)
    # Three drifting clouds for ambient depth
    for i, (bx, by, sc, variant) in enumerate((
            (40, 110, 0.85, 0), (220, 70, 0.7, 2), (120, 200, 1.0, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W,
                   palette['mtn_far'], palette['mtn_near'])
    if ground:
        draw_ground(surf, GROUND_Y, W, H, scroll,
                    palette['ground_top'], palette['ground_mid'], (60, 40, 25))


def _draw_distant_pillar(surf: pygame.Surface, x_center: int,
                         palette: dict, h_top: int, h_bot: int) -> None:
    """A single pillar pair drawn as a soft silhouette in the distance."""
    w = 36
    top_rect = pygame.Rect(x_center - w // 2, 0, w, h_top)
    bot_rect = pygame.Rect(x_center - w // 2, GROUND_Y - h_bot, w, h_bot)
    draw_pillar_pair(surf, top_rect, bot_rect, palette, seed=x_center * 31)


def _draw_pip(surf: pygame.Surface, x: float, y: float, frame_t: float,
              tilt_deg: float, scale: float = 1.0, alpha: int = 255) -> None:
    """Draw the macaw at (x, y) using the cached parrot rotation."""
    frame_idx = int(frame_t) % len(_parrot.FRAMES)
    img = _parrot.get_parrot(frame_idx, tilt_deg)
    if scale != 1.0:
        sw = max(2, int(img.get_width() * scale))
        sh = max(2, int(img.get_height() * scale))
        img = pygame.transform.smoothscale(img, (sw, sh))
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    r = img.get_rect(center=(int(x), int(y)))
    surf.blit(img, r.topleft)


def _draw_glow_motes(surf: pygame.Surface, t: float,
                     count: int = 10, color=(255, 230, 180)) -> None:
    """Drifting motes — like dust in a beam of sun. Quiet depth that never
    reads as gameplay coins. Kept small and dim by design."""
    for i in range(count):
        seed = i * 137
        speed = 18.0 + (seed % 13) * 1.5
        x = ((seed * 7 % W) + t * speed) % (W + 40) - 20
        y = (seed * 53 % (H - 200)) + math.sin(t * 0.8 + i) * 10
        r = 4 + (seed % 3) * 2
        a = 30 + int(18 * math.sin(t * 1.3 + i * 0.8))
        a = max(15, min(60, a))
        blit_glow(surf, int(x), int(y), r, color, a)


def _draw_distant_flock(surf: pygame.Surface, t: float, x_off: float) -> None:
    """A small V-formation of birds, drifting once across the journey beat."""
    # Anchor x slides from off-screen-right to off-screen-left across ~5 s.
    cx = int(x_off)
    if cx < -40 or cx > W + 40:
        return
    cy = 130
    color = (40, 50, 75)
    for i, (dx, dy) in enumerate(((0, 0), (-8, 4), (8, 4), (-16, 8), (16, 8))):
        bob = math.sin(t * 4.5 + i) * 1.0
        bx = cx + dx
        by = cy + dy + bob
        pygame.draw.polygon(surf, color, [
            (bx - 4, by), (bx, by - 2), (bx + 4, by),
            (bx + 1, by + 1), (bx - 1, by + 1),
        ])


# ── beat 1: Dawn at the perch (0.0 – 2.5) ────────────────────────────────────

def _beat_dawn(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """Predawn → first light. A single weathered pillar holds the mailbag and
    a softly-glowing parcel. No characters yet; the world simply wakes up."""
    # Sky lerps predawn (0.78) → day (0.00 / equivalently 1.00 wrapping).
    phase = 0.78 + _smoothstep(u) * 0.22
    _draw_world(surf, phase, scroll=u * 4.0, cloud_phase=scene.t,
                ground=False)
    # Soft mist band along the bottom — fades as light grows.
    mist_a = int(180 * (1.0 - _smoothstep(u)))
    if mist_a > 0:
        mist = pygame.Surface((W, 220), pygame.SRCALPHA)
        for i in range(220):
            t = i / 219.0
            a = int(mist_a * (1.0 - t) ** 1.4)
            pygame.draw.line(mist, (235, 220, 230, a), (0, i), (W, i))
        surf.blit(mist, (0, GROUND_Y - 200))
    # The hero pillar — central, near-camera. Anchored slightly right of
    # centre so the parcel reads "on a ledge" rather than "balanced on a
    # spike". `draw_pillar_pair` only paints the half it's given a non-zero
    # rect for, so we draw just the bottom pillar to keep the sky open.
    pal = _biome.palette_for_phase(phase)
    pillar_w = 64
    pillar_h = 200
    pillar_x = W // 2 - pillar_w // 2 + 30
    pillar_y = GROUND_Y - pillar_h
    draw_pillar_pair(
        surf,
        pygame.Rect(0, 0, 0, 0),  # no top pillar
        pygame.Rect(pillar_x, pillar_y, pillar_w, pillar_h),
        pal, seed=0,  # variant 0 — basic undecorated pillar (no flags/banners/lanterns)
    )
    # Mailbag + parcel rest on the ledge.
    bag = _get_sprite("mailbag")
    par = _get_sprite("parcel")
    ledge_y = pillar_y - 6
    surf.blit(bag, (pillar_x - 4, ledge_y - bag.get_height() + 8))
    par_x = pillar_x + pillar_w - par.get_width() + 6
    par_y = ledge_y - par.get_height() + 8
    # Parcel glow — small and warm, just kissing the parcel edges so the
    # paper-and-ribbon detail still reads.
    glow_a = 50 + int(20 * math.sin(scene.t * 2.4))
    blit_glow(surf, par_x + par.get_width() // 2,
              par_y + par.get_height() // 2, 14, (255, 215, 110), glow_a)
    surf.blit(par, (par_x, par_y))


# ── beat 2: The hand-off (2.5 – 4.5) ─────────────────────────────────────────

def _beat_handoff(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """Pip stays perched on the same pillar from beat 1. Mr. Garrick flies in
    from the left, hovers beside the pillar, gestures, and a fresh parcel
    arcs across into Pip's mailbag. Earpiece crackle plays once during this
    beat (scheduled in `update`)."""
    sky_phase = 0.00 + _smoothstep(u) * 0.10  # day → just into golden warmth
    _draw_world(surf, sky_phase, scroll=10.0 + u * 6.0,
                cloud_phase=scene.t, ground=False)
    pal = _biome.palette_for_phase(sky_phase)

    # Reuse the EXACT pillar from beat 1 — same dims, same x, same seed.
    pillar_w, pillar_h = 64, 200
    pillar_x = W // 2 - pillar_w // 2 + 30
    pillar_y = GROUND_Y - pillar_h
    draw_pillar_pair(surf, pygame.Rect(0, 0, 0, 0),
                     pygame.Rect(pillar_x, pillar_y, pillar_w, pillar_h),
                     pal, seed=0)  # variant 0 — basic undecorated pillar

    # Mailbag on the ledge.
    bag = _get_sprite("mailbag")
    surf.blit(bag, (pillar_x - 4, pillar_y - bag.get_height() + 8))

    # Pip — perched on the ledge, tiny breath bob.
    pip_x = pillar_x + pillar_w // 2 + 4
    pip_y = pillar_y - 18 + math.sin(scene.t * 2.0) * 1.0
    _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 1.5,
              tilt_deg=-4.0, scale=0.9)

    # Mr. Garrick — hovering in the air to the left of the pillar with a
    # slow sin-bob. Wing flap is drawn as a small wing polygon overlay that
    # toggles up/down on a 4 Hz cycle.
    g = _get_sprite("garrick")
    g_x = 50
    g_base_y = pillar_y - 30
    bob = int(math.sin(scene.t * 1.5) * 6)
    g_y = g_base_y + bob
    surf.blit(g, (g_x, g_y))
    # Flapping wing — a small angular polygon that rises and falls.
    wing_up = math.sin(scene.t * 8.0) > 0
    if wing_up:
        wing_pts = [(g_x + 22, g_y + 38), (g_x + 6, g_y + 24),
                    (g_x + 18, g_y + 30), (g_x + 30, g_y + 36)]
    else:
        wing_pts = [(g_x + 22, g_y + 38), (g_x + 6, g_y + 50),
                    (g_x + 18, g_y + 44), (g_x + 30, g_y + 38)]
    pygame.draw.polygon(surf, (240, 200, 200), wing_pts)
    pygame.draw.polygon(surf, (200, 150, 160), wing_pts, 1)

    # Speech-soundwave arc beside Garrick's beak.
    if 0.20 < u < 0.70:
        wave_t = (u - 0.20) / 0.50
        n = int(_clamp01(wave_t * 3.5)) + 1
        for i in range(n):
            radius = 7 + i * 5
            alpha = max(0, 200 - i * 60)
            arc = pygame.Surface((radius * 2 + 4, radius + 4), pygame.SRCALPHA)
            pygame.draw.arc(arc, (255, 240, 220, alpha),
                            arc.get_rect(), math.pi * 0.15, math.pi * 0.85, 2)
            surf.blit(arc, (g_x + g.get_width() - 6, g_y - radius // 2))

    # Parcel arcs from Garrick's beak across to the mailbag on Pip's ledge.
    par = _get_sprite("parcel")
    target_x = pillar_x + pillar_w - par.get_width() + 6
    target_y = pillar_y - par.get_height() + 8
    if u < 0.45:
        # Parcel still beside Garrick (his "outbox")
        carry_x = g_x + g.get_width() - 18
        carry_y = g_y + 14
        surf.blit(par, (carry_x, carry_y))
    elif u < 0.95:
        a = (u - 0.45) / 0.50
        ea = _ease_out_cubic(a)
        sx = g_x + g.get_width() - 18
        sy = g_y + 14
        cx = sx + (target_x - sx) * ea
        cy = sy + (target_y - sy) * ea - int(math.sin(a * math.pi) * 22)
        surf.blit(par, (int(cx), int(cy)))
    else:
        glow_a = int(80 * (u - 0.95) / 0.05)
        blit_glow(surf, target_x + par.get_width() // 2,
                  target_y + par.get_height() // 2,
                  22, (255, 215, 110), glow_a)
        surf.blit(par, (target_x, target_y))


# ── beat 3: The journey (4.5 – 10.0) ─────────────────────────────────────────

# Phase waypoints across the beat: golden hour → sunset → night → sunrise.
_JOURNEY_WAYPOINTS = (
    (0.00, 0.10),  # u=0.00, just past day, warming
    (0.20, 0.18),  # golden hour
    (0.45, 0.32),  # sunset
    (0.70, 0.62),  # night
    (1.00, 0.90),  # sunrise
)


def _journey_phase(u: float) -> float:
    u = _clamp01(u)
    for i in range(len(_JOURNEY_WAYPOINTS) - 1):
        u0, p0 = _JOURNEY_WAYPOINTS[i]
        u1, p1 = _JOURNEY_WAYPOINTS[i + 1]
        if u <= u1:
            seg = 0.0 if u1 <= u0 else (u - u0) / (u1 - u0)
            seg = _smoothstep(seg)
            return p0 + (p1 - p0) * seg
    return _JOURNEY_WAYPOINTS[-1][1]


def _beat_journey(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """The heart of the cinematic. Pip glides serenely while the world cycles
    around him. Camera floats high — no ground in frame."""
    phase = _journey_phase(u)
    # Scroll accelerates gently across the beat — a sense of forward progress
    # without ever feeling fast.
    scroll = 60.0 + u * 280.0 + scene.t * 30.0
    _draw_world(surf, phase, scroll=scroll, cloud_phase=scene.t, ground=False)

    pal = _biome.palette_for_phase(phase)

    # No pillars in the journey beat — pillars appear only at pickup (beats
    # 1 + 2) and delivery (beat 4). Sky, clouds, mountains, motes, sun/moon,
    # the flock and Pip carry the journey.

    # Distant V-formation flock — drifts across once during the beat (u 0.55..0.85)
    if 0.55 < u < 0.85:
        flock_u = (u - 0.55) / 0.30
        fx = W + 40 - flock_u * (W + 80)
        _draw_distant_flock(surf, scene.t, fx)

    # Drifting glow motes — like dust in the light. Color tint follows phase.
    # Cool blueish stars at night, warm gold at sunrise/golden hour.
    if phase > 0.5 and phase < 0.78:
        mote_color = (200, 215, 255)  # night moonlight
        mote_count = 14
    else:
        mote_color = (255, 220, 160)
        mote_count = 10
    _draw_glow_motes(surf, scene.t, count=mote_count, color=mote_color)

    # Pip — gentle sin-bob path centred at H*0.45, slow flap, almost-level
    # tilt. He carries the parcel: a tiny golden glow follows just below him
    # to suggest the bundle in his talons.
    pip_x = W * 0.48 + math.sin(scene.t * 0.8) * 18
    pip_y = H * 0.45 + math.sin(scene.t * 1.5) * 14
    tilt = math.sin(scene.t * 1.5) * -6.0
    # Carried parcel — tucked beneath Pip with a faint glow.
    par = _get_sprite("parcel")
    blit_glow(surf, int(pip_x) + 4, int(pip_y) + 18, 10,
              (255, 215, 110), 55)
    surf.blit(par, (int(pip_x) - par.get_width() // 2,
                    int(pip_y) + 10))
    _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 5.0, tilt_deg=tilt,
              scale=1.0)


# ── beat 4: Arrival (10.0 – 11.0) ────────────────────────────────────────────

def _beat_arrival(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """Pip alights at a sunlit pillar. The mailbox waits. He sets the parcel
    down and a soft gold glow spreads. No slam, no fanfare."""
    phase = 0.92 + u * 0.06  # locked into morning sunrise
    _draw_world(surf, phase, scroll=400.0 + u * 30.0,
                cloud_phase=scene.t, ground=False)
    pal = _biome.palette_for_phase(phase)

    # The destination pillar sits centre frame.
    pillar_w, pillar_h = 70, 230
    pillar_x = W // 2 - pillar_w // 2
    pillar_y = GROUND_Y - pillar_h
    draw_pillar_pair(surf, pygame.Rect(0, 0, 0, 0),
                     pygame.Rect(pillar_x, pillar_y, pillar_w, pillar_h),
                     pal, seed=0)  # variant 0 — basic undecorated pillar

    # Mailbox on the ledge.
    mb = _get_sprite("mailbox")
    mb_x = pillar_x + pillar_w // 2 - mb.get_width() // 2
    mb_y = pillar_y - mb.get_height() + 6
    surf.blit(mb, (mb_x, mb_y))

    # Pip glides in from upper-right and slows to a hover by the mailbox.
    pip_t = _ease_out_cubic(u)
    start_x, start_y = W + 60, 120
    end_x, end_y = pillar_x + pillar_w + 22, mb_y - 4
    pip_x = start_x + (end_x - start_x) * pip_t
    pip_y = start_y + (end_y - start_y) * pip_t
    tilt = -10.0 * (1.0 - pip_t)
    _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 4.0, tilt_deg=tilt)

    # Parcel transitions from "in talons" to "delivered". After u≈0.55 the
    # parcel sits on top of the mailbox and glows.
    par = _get_sprite("parcel")
    if u < 0.55:
        carry_x = int(pip_x) - par.get_width() // 2
        carry_y = int(pip_y) + 10
        surf.blit(par, (carry_x, carry_y))
    else:
        deliv_t = (u - 0.55) / 0.45
        rest_x = mb_x + (mb.get_width() - par.get_width()) // 2
        rest_y = mb_y - par.get_height() + 6
        glow_a = int(180 * deliv_t)
        blit_glow(surf, rest_x + par.get_width() // 2,
                  rest_y + par.get_height() // 2, 26,
                  (255, 215, 110), glow_a)
        surf.blit(par, (rest_x, rest_y))


# ── beat 5: Title (11.0 – 12.0) ──────────────────────────────────────────────

def _beat_title(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """Skybit logotype + subtitle + pulsing 'TAP TO FLY'. Pip drifts quietly
    across the lower frame. The pulse formula matches the menu so the cut is
    rhythm-continuous."""
    # Sunrise sky frozen. Slight zoom-out illusion via gentle scroll.
    phase = 0.95
    _draw_world(surf, phase, scroll=440.0 + scene.t * 12.0,
                cloud_phase=scene.t, ground=False)

    # Soft warm overlay behind the logo so the text reads on any sky tint.
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 20, int(80 * _smoothstep(u))))
    surf.blit(overlay, (0, 0))

    # Logo fade-in over the first 0.5 s of the beat.
    logo_a = int(255 * _smoothstep(_clamp01(u / 0.5)))
    pulse = 1.0 + math.sin(scene._title_t * 2.4) * 0.04
    draw_skybit_wordmark(surf, W // 2, 200, scale=pulse, alpha=logo_a)

    # Subtitle.
    if u > 0.20:
        sub_a = int(255 * _smoothstep((u - 0.20) / 0.30))
        f = _font(18, True)
        sub = f.render("A Pip the Punctual Adventure", True, UI_CREAM)
        sub.set_alpha(sub_a)
        sr = sub.get_rect(center=(W // 2, 250))
        surf.blit(sub, sr.topleft)

    # "TAP TO FLY" pulse — uses the menu's exact cadence (hud.py:323).
    if u > 0.40:
        prompt_fade = _smoothstep((u - 0.40) / 0.40)
        alpha = int((160 + math.sin(scene._title_t * 3.6) * 90) * prompt_fade)
        alpha = max(0, min(255, alpha))
        f2 = _font(24, True)
        prompt = f2.render("TAP TO FLY", True, WHITE)
        prompt.set_alpha(alpha)
        pr = prompt.get_rect(center=(W // 2, H - 170))
        surf.blit(prompt, pr.topleft)

    # Pip drifts quietly across the lower third — a small recurring presence.
    pip_x = (scene.t * 22.0) % (W + 80) - 40
    pip_y = H - 120 + math.sin(scene.t * 1.6) * 8
    _draw_pip(surf, pip_x, pip_y,
              frame_t=scene.t * 5.0, tilt_deg=-3.0, scale=0.7)


# ── final beat dispatcher ────────────────────────────────────────────────────

def _dispatch_beat(scene: "IntroScene", surf: pygame.Surface) -> None:
    t = scene.t
    if t < 2.5:
        _beat_dawn(scene, surf, t / 2.5)
    elif t < 4.5:
        _beat_handoff(scene, surf, (t - 2.5) / 2.0)
    elif t < 10.0:
        _beat_journey(scene, surf, (t - 4.5) / 5.5)
    elif t < 11.0:
        _beat_arrival(scene, surf, (t - 10.0) / 1.0)
    elif t < DURATION:
        _beat_title(scene, surf, (t - 11.0) / 1.0)
    else:
        _beat_title(scene, surf, 1.0)


def _draw_skip_pill(surf: pygame.Surface, t: float) -> None:
    if t < 1.5:
        return
    fade = _clamp01((t - 1.5) / 0.4)
    alpha = int(140 * fade)
    if alpha <= 0:
        return
    f = _font(12, True)
    label = f.render("SKIP", True, WHITE)
    label.set_alpha(alpha)
    pad_w, pad_h = label.get_width() + 18, label.get_height() + 8
    pill = pygame.Surface((pad_w, pad_h), pygame.SRCALPHA)
    pygame.draw.ellipse(pill, (0, 0, 20, int(120 * fade)), pill.get_rect())
    px = W - pad_w - 14
    py = 18
    surf.blit(pill, (px, py))
    surf.blit(label, (px + 9, py + 4))

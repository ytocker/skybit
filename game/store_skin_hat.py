"""Hat-composite builders for all store skins (clean + first_hit + last_life).

Mirrors store_skin_hurt.py but composes the stovepipe hat on top of each skin's
own body frame, so hat-powerup users see their chosen skin's accessories under
the hat.

Exports
-------
SKIN_HAT_GETTERS : dict[str, tuple[callable, callable, callable]]
    skin_id -> (get_clean(frame_idx, tilt_deg),
                get_first_hit(frame_idx, tilt_deg),
                get_last_life(frame_idx, tilt_deg))
"""
import pygame

from game.parrot import (
    _h_draw_bandaids, _h_draw_headwrap, _h_draw_chest_dressing,
    _h_draw_ragged_cuts, _h_draw_cracked_lens, _fh_draw_single_crack,
    _add_outline, _H_HURT_ANGLES, _WING_ANGLES,
)
from game.dollar_parrot_ghost import _build_parrot_with_palette, _draw_lenses
from game.dollar_parrot_hat import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY,
    draw_stovepipe,
)
from game.store_skins import (
    P_DISCO, P_BLUEGOLD, P_AMAZON, P_SUNCONURE, P_HYACINTH,
    P_COCKATOO, P_LORIKEET, P_PRISM, P_THORNCREST, P_EMBERMOTH,
    _AURORA_PAL, P_MOONBLOOM, P_TEMPEST, P_BINKY, P_CHROME,
    _build_voodoo_zombie,
    _paint_disco, _paint_cockatoo_crest, _paint_prism,
    _paint_thorncrest, _paint_embermoth, _paint_binky,
    _aurora_front,    _aurora_back,
    _moonbloom_front, _moonbloom_back, _MB_OUTLINE,
    _tempest_front,   _tempest_back,   _TP_OUTLINE,
    _chrome_front,    _chrome_back,
    _zb_hex_aura, _zb_rim_halo,
    _ZB_STITCH, _ZB_CURSED, _ZB_CURSED_H,
)
from game.skeleton_skin import _flesh_base, _paint as _skeleton_paint, _eye_socket


# ── shared helpers ─────────────────────────────────────────────────────────────

def _open_beak(surf, P):
    """Open two-part beak for hurt states (sprite-space coords)."""
    beak_lo = tuple(int(c * 0.87) for c in P['beak_main'])
    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    pygame.draw.polygon(surf, P['beak_main'], upper)
    pygame.draw.polygon(surf, P['beak_dark'], upper, 1)
    pygame.draw.polygon(surf, beak_lo, lower)
    pygame.draw.polygon(surf, P['beak_dark'], lower, 1)
    pygame.draw.line(surf, P['beak_gloss'], (55, 22), (59, 24), 1)


def _composite_hat_with_back(comp, back_fn, outline_color):
    """Draw stovepipe hat on comp, outline, then composite back_fn behind."""
    draw_stovepipe(comp, HAT_HX, HAT_HY)
    kw = {"outline_color": outline_color} if outline_color else {}
    bird = _add_outline(comp, **kw)
    if back_fn is None:
        return bird
    pad = (bird.get_width() - COMPOSITE_W) // 2
    result = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
    back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    back_fn(back, 10.0)
    result.blit(back, (pad, pad))
    result.blit(bird, (0, 0))
    return result


# ── per-state builders for pure-palette skins ─────────────────────────────────

def _hat_simple(palette, angle_deg):
    """Clean hat frame for pure-palette skins."""
    body = _build_parrot_with_palette(angle_deg, palette)
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    return _composite_hat_with_back(comp, None, None)


def _hat_ll_simple(palette, angle_deg):
    """Last-life hat frame for pure-palette skins."""
    body = _build_parrot_with_palette(angle_deg, palette, draw_lenses=False)
    _h_draw_bandaids(body)
    _h_draw_headwrap(body)
    _draw_lenses(body, 50, 20, palette)
    _open_beak(body, palette)
    _h_draw_chest_dressing(body)
    _h_draw_ragged_cuts(body)
    _h_draw_cracked_lens(body)
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    return _composite_hat_with_back(comp, None, None)


def _hat_fh_simple(palette, angle_deg):
    """First-hit hat frame for pure-palette skins."""
    body = _build_parrot_with_palette(angle_deg, palette)
    _open_beak(body, palette)
    _h_draw_bandaids(body)
    _fh_draw_single_crack(body)
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    return _composite_hat_with_back(comp, None, None)


# ── per-state builders for composite (paint_fn/back_fn) skins ─────────────────

def _hat_composite(palette, paint_fn, back_fn, outline_color, draw_std_lenses,
                   angle_deg):
    """Clean hat frame for composite skins."""
    body = _build_parrot_with_palette(angle_deg, palette)
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    if paint_fn:
        paint_fn(comp, angle_deg)
    return _composite_hat_with_back(comp, back_fn, outline_color)


def _hat_ll_composite(palette, paint_fn, back_fn, outline_color, draw_std_lenses,
                      angle_deg):
    """Last-life hat frame for composite skins."""
    body = _build_parrot_with_palette(angle_deg, palette, draw_lenses=False)
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    if paint_fn:
        paint_fn(comp, angle_deg)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _h_draw_bandaids(sprite)
    _h_draw_headwrap(sprite)
    if draw_std_lenses:
        _draw_lenses(sprite, 50, 20, palette)
    _open_beak(sprite, palette)
    _h_draw_chest_dressing(sprite)
    _h_draw_ragged_cuts(sprite)
    _h_draw_cracked_lens(sprite)
    return _composite_hat_with_back(comp, back_fn, outline_color)


def _hat_fh_composite(palette, paint_fn, back_fn, outline_color, draw_std_lenses,
                      angle_deg):
    """First-hit hat frame for composite skins."""
    body = _build_parrot_with_palette(angle_deg, palette)
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    if paint_fn:
        paint_fn(comp, angle_deg)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _open_beak(sprite, palette)
    _h_draw_bandaids(sprite)
    _fh_draw_single_crack(sprite)
    return _composite_hat_with_back(comp, back_fn, outline_color)


# ── skeleton ──────────────────────────────────────────────────────────────────

def _hat_clean_skeleton(angle_deg):
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(_flesh_base(angle_deg), (0, PARROT_DY))
    _skeleton_paint(comp, angle_deg)
    _eye_socket(comp)
    return _composite_hat_with_back(comp, None, None)


def _hat_ll_skeleton(angle_deg):
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(_flesh_base(angle_deg), (0, PARROT_DY))
    _skeleton_paint(comp, angle_deg)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _h_draw_bandaids(sprite)
    _h_draw_headwrap(sprite)
    _eye_socket(comp)
    _h_draw_chest_dressing(sprite)
    _h_draw_ragged_cuts(sprite)
    return _composite_hat_with_back(comp, None, None)


def _hat_fh_skeleton(angle_deg):
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(_flesh_base(angle_deg), (0, PARROT_DY))
    _skeleton_paint(comp, angle_deg)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _h_draw_bandaids(sprite)
    _fh_draw_single_crack(sprite)
    return _composite_hat_with_back(comp, None, None)


# ── zombie ────────────────────────────────────────────────────────────────────

def _zombie_hat_with_aura(body, angle_deg):
    """Composite voodoo body + hat, outline, add green hex aura ring."""
    comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    draw_stovepipe(comp, HAT_HX, HAT_HY)
    core = _add_outline(comp)
    pad = 16
    cw, ch = core.get_size()
    out = pygame.Surface((cw + pad * 2, ch + pad * 2), pygame.SRCALPHA)
    _zb_hex_aura(out, out.get_width() // 2, out.get_height() // 2 + 4,
                 max(cw, ch) // 2 + 6)
    ring = _zb_rim_halo(core)
    out.blit(ring, (pad - 2, pad - 2))
    out.blit(core, (pad, pad))
    return out


def _hat_clean_zombie(angle_deg):
    return _zombie_hat_with_aura(_build_voodoo_zombie(angle_deg), angle_deg)


def _hat_ll_zombie(angle_deg):
    base = _build_voodoo_zombie(angle_deg)
    _h_draw_bandaids(base)
    _h_draw_headwrap(base)
    pygame.draw.line(base, _ZB_STITCH, (41, 21), (47, 21), 2)
    for vx in (42, 44, 46):
        pygame.draw.line(base, _ZB_STITCH, (vx, 19), (vx, 23), 1)
    _zb_hex_aura(base, 50, 19, 7)
    pygame.draw.circle(base, _ZB_STITCH, (50, 19), 5)
    pygame.draw.circle(base, _ZB_CURSED, (50, 19), 4)
    pygame.draw.circle(base, _ZB_CURSED_H, (49, 18), 1)
    _h_draw_chest_dressing(base)
    _h_draw_ragged_cuts(base)
    return _zombie_hat_with_aura(base, angle_deg)


def _hat_fh_zombie(angle_deg):
    base = _build_voodoo_zombie(angle_deg)
    _h_draw_bandaids(base)
    _fh_draw_single_crack(base)
    return _zombie_hat_with_aura(base, angle_deg)


# ── frame cache factory ────────────────────────────────────────────────────────

def _make_getter(frames, rot_cache):
    def get(frame_idx, tilt_deg):
        key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
        s = rot_cache.get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
            rot_cache[key] = s
        return s
    return get


def _prebuild_triple(clean_fn, fh_fn, ll_fn):
    """Return lazy (clean, fh, ll) getters; frames built on first call per state."""
    clean_state: dict = {}
    fh_state:    dict = {}
    ll_state:    dict = {}

    def clean_getter(frame_idx, tilt_deg):
        if "g" not in clean_state:
            clean_state["g"] = _make_getter([clean_fn(a) for a in _WING_ANGLES], {})
        return clean_state["g"](frame_idx, tilt_deg)

    def fh_getter(frame_idx, tilt_deg):
        if "g" not in fh_state:
            fh_state["g"] = _make_getter([fh_fn(a) for a in _H_HURT_ANGLES], {})
        return fh_state["g"](frame_idx, tilt_deg)

    def ll_getter(frame_idx, tilt_deg):
        if "g" not in ll_state:
            ll_state["g"] = _make_getter([ll_fn(a) for a in _H_HURT_ANGLES], {})
        return ll_state["g"](frame_idx, tilt_deg)

    return (clean_getter, fh_getter, ll_getter)


# ── skin registry ──────────────────────────────────────────────────────────────

def _build_registry():
    reg = {}

    def _simple(pal):
        return _prebuild_triple(
            lambda a: _hat_simple(pal, a),
            lambda a: _hat_fh_simple(pal, a),
            lambda a: _hat_ll_simple(pal, a),
        )

    def _composite(pal, paint_fn, back_fn, outline_color, draw_std_lenses):
        return _prebuild_triple(
            lambda a: _hat_composite(pal, paint_fn, back_fn, outline_color,
                                     draw_std_lenses, a),
            lambda a: _hat_fh_composite(pal, paint_fn, back_fn, outline_color,
                                        draw_std_lenses, a),
            lambda a: _hat_ll_composite(pal, paint_fn, back_fn, outline_color,
                                        draw_std_lenses, a),
        )

    reg["skin_skeleton"] = _prebuild_triple(
        _hat_clean_skeleton, _hat_fh_skeleton, _hat_ll_skeleton)
    reg["skin_zombie"] = _prebuild_triple(
        _hat_clean_zombie, _hat_fh_zombie, _hat_ll_zombie)

    reg["skin_bluegold"]  = _simple(P_BLUEGOLD)
    reg["skin_amazon"]    = _simple(P_AMAZON)
    reg["skin_sunconure"] = _simple(P_SUNCONURE)
    reg["skin_hyacinth"]  = _simple(P_HYACINTH)
    reg["skin_lorikeet"]  = _simple(P_LORIKEET)

    reg["skin_disco"]      = _composite(P_DISCO,      _paint_disco,      None,
                                        None,       True)
    reg["skin_prism"]      = _composite(P_PRISM,      _paint_prism,      None,
                                        None,       True)
    reg["skin_thorncrest"] = _composite(P_THORNCREST, _paint_thorncrest, None,
                                        None,       True)
    reg["skin_embermoth"]  = _composite(P_EMBERMOTH,  _paint_embermoth,  None,
                                        None,       True)
    reg["skin_binky"]      = _composite(P_BINKY,      _paint_binky,      None,
                                        None,       True)
    reg["skin_cockatoo"]   = _composite(P_COCKATOO,   None, _paint_cockatoo_crest,
                                        None,       True)
    reg["skin_aurora"]     = _composite(_AURORA_PAL,  _aurora_front,   _aurora_back,
                                        None,       True)
    reg["skin_moonbloom"]  = _composite(P_MOONBLOOM,  _moonbloom_front, _moonbloom_back,
                                        _MB_OUTLINE, True)
    reg["skin_tempest"]    = _composite(P_TEMPEST,    _tempest_front,  _tempest_back,
                                        _TP_OUTLINE, True)
    reg["skin_chrome"]     = _composite(P_CHROME,     _chrome_front,   _chrome_back,
                                        None,       False)

    return reg


SKIN_HAT_GETTERS: dict = _build_registry()

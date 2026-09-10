"""
Hurt-state builders for all store skins (first_hit + last_life).

Mirrors docs/render_store_parrot_lives_grid.py but parameterises on angle_deg
so every wing-angle frame can be pre-built and cached.

Exports
-------
SKIN_HURT_GETTERS : dict[str, tuple[callable, callable]]
    skin_id -> (get_last_life(frame_idx, tilt_deg),
                get_first_hit(frame_idx, tilt_deg))
"""
import pygame

from game.parrot import (
    _h_draw_bandaids, _h_draw_headwrap, _h_draw_chest_dressing,
    _h_draw_ragged_cuts, _h_draw_cracked_lens, _fh_draw_single_crack,
    _add_outline, _H_HURT_ANGLES,
    _h_build_hurt_frame, _fh_build_hurt_frame,
)
from game.dollar_parrot_ghost import _build_parrot_with_palette, _draw_lenses
from game.store_skins import (
    PARROT_DY,
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
    P_NINJA, _paint_ninja,
    _TH_BODY, _paint_tophat,
    _MU_BODY, _paint_mummy,
    P_ASTRONAUT, _paint_astronaut,
    P_PILOT, _paint_pilot,
    _VK_PAL, _VK_OUTLINE,
    _viking_axe, _viking_back, _viking_helm, _viking_face,
    _paint_pirate, _paint_cowboy, _paint_pharaoh, _paint_crown,
    _paint_baseball, _paint_tennis, _paint_wizard,
)
from game.skeleton_skin import _flesh_base, _paint as _skeleton_paint, _eye_socket


# ── shared helpers ─────────────────────────────────────────────────────────────

def _open_beak(surf, P):
    """Open two-part beak matching the hurt-frame anatomy."""
    beak_lo = tuple(int(c * 0.87) for c in P['beak_main'])
    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    pygame.draw.polygon(surf, P['beak_main'], upper)
    pygame.draw.polygon(surf, P['beak_dark'], upper, 1)
    pygame.draw.polygon(surf, beak_lo, lower)
    pygame.draw.polygon(surf, P['beak_dark'], lower, 1)
    pygame.draw.line(surf, P['beak_gloss'], (55, 22), (59, 24), 1)


def _composite_with_back(comp, back_fn, outline_color):
    """Outline comp, composite back_fn behind it, return final surface."""
    kw = {"outline_color": outline_color} if outline_color else {}
    bird = _add_outline(comp, **kw)
    if back_fn is None:
        return bird
    pad = (bird.get_width() - 64) // 2
    result = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
    back = pygame.Surface((64, 100), pygame.SRCALPHA)
    back_fn(back, 10.0)
    result.blit(back, (pad, pad))
    result.blit(bird, (0, 0))
    return result


# ── per-state builders ─────────────────────────────────────────────────────────

def _hurt_simple(palette, angle_deg):
    """Last_life for pure-palette skins (no accessories, no back layer)."""
    base = _build_parrot_with_palette(angle_deg, palette, draw_lenses=False)
    _h_draw_bandaids(base)
    _h_draw_headwrap(base)
    _draw_lenses(base, 50, 20, palette)
    _open_beak(base, palette)
    _h_draw_chest_dressing(base)
    _h_draw_ragged_cuts(base)
    _h_draw_cracked_lens(base)
    return _add_outline(base)


def _fh_simple(palette, angle_deg):
    """First_hit for pure-palette skins."""
    base = _build_parrot_with_palette(angle_deg, palette)
    _open_beak(base, palette)
    _h_draw_bandaids(base)
    _fh_draw_single_crack(base)
    return _add_outline(base)


def _hurt_composite(palette, paint_fn, back_fn, outline_color, draw_std_lenses, angle_deg):
    """Last_life for composite (paint_fn / back_fn) skins."""
    body = _build_parrot_with_palette(angle_deg, palette, draw_lenses=False)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
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
    return _composite_with_back(comp, back_fn, outline_color)


def _fh_composite(palette, paint_fn, back_fn, outline_color, draw_std_lenses, angle_deg):
    """First_hit for composite skins."""
    body = _build_parrot_with_palette(angle_deg, palette)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    if paint_fn:
        paint_fn(comp, angle_deg)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _open_beak(sprite, palette)
    _h_draw_bandaids(sprite)
    _fh_draw_single_crack(sprite)
    return _composite_with_back(comp, back_fn, outline_color)


def _hurt_skeleton(angle_deg):
    """Skeleton last_life: bones present via composite, eyes over headwrap."""
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(_flesh_base(angle_deg), (0, PARROT_DY))
    _skeleton_paint(comp, angle_deg)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _h_draw_bandaids(sprite)
    _h_draw_headwrap(sprite)
    _eye_socket(comp)
    _h_draw_chest_dressing(sprite)
    _h_draw_ragged_cuts(sprite)
    return _add_outline(comp)


def _fh_skeleton(angle_deg):
    """Skeleton first_hit."""
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(_flesh_base(angle_deg), (0, PARROT_DY))
    _skeleton_paint(comp, angle_deg)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _h_draw_bandaids(sprite)
    _fh_draw_single_crack(sprite)
    return _add_outline(comp)


def _hurt_zombie(angle_deg):
    """Zombie last_life: headwrap + eyes redrawn over headwrap + cursed aura."""
    base = _build_voodoo_zombie(angle_deg)
    _h_draw_bandaids(base)
    _h_draw_headwrap(base)
    # dead eye stitch
    pygame.draw.line(base, _ZB_STITCH, (41, 21), (47, 21), 2)
    for vx in (42, 44, 46):
        pygame.draw.line(base, _ZB_STITCH, (vx, 19), (vx, 23), 1)
    # cursed eye over headwrap
    _zb_hex_aura(base, 50, 19, 7)
    pygame.draw.circle(base, _ZB_STITCH, (50, 19), 5)
    pygame.draw.circle(base, _ZB_CURSED, (50, 19), 4)
    pygame.draw.circle(base, _ZB_CURSED_H, (49, 18), 1)
    _h_draw_chest_dressing(base)
    _h_draw_ragged_cuts(base)
    core = _add_outline(base)
    pad = 16
    cw, ch = core.get_size()
    out = pygame.Surface((cw + pad * 2, ch + pad * 2), pygame.SRCALPHA)
    _zb_hex_aura(out, out.get_width() // 2, out.get_height() // 2 + 4,
                 max(cw, ch) // 2 + 6)
    ring = _zb_rim_halo(core)
    out.blit(ring, (pad - 2, pad - 2))
    out.blit(core, (pad, pad))
    return out


def _fh_zombie(angle_deg):
    """Zombie first_hit."""
    base = _build_voodoo_zombie(angle_deg)
    _h_draw_bandaids(base)
    _fh_draw_single_crack(base)
    core = _add_outline(base)
    pad = 16
    cw, ch = core.get_size()
    out = pygame.Surface((cw + pad * 2, ch + pad * 2), pygame.SRCALPHA)
    _zb_hex_aura(out, out.get_width() // 2, out.get_height() // 2 + 4,
                 max(cw, ch) // 2 + 6)
    ring = _zb_rim_halo(core)
    out.blit(ring, (pad - 2, pad - 2))
    out.blit(core, (pad, pad))
    return out


# ── costume builders ──────────────────────────────────────────────────────────

def _hurt_std_accessory(paint_fn, angle_deg):
    """Last_life for standard-macaw costumes: baked hurt body + costume on top."""
    body = _h_build_hurt_frame(angle_deg)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    if paint_fn:
        paint_fn(comp, angle_deg)
    return _add_outline(comp)


def _fh_std_accessory(paint_fn, angle_deg):
    """First_hit for standard-macaw costumes."""
    body = _fh_build_hurt_frame(angle_deg)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    if paint_fn:
        paint_fn(comp, angle_deg)
    return _add_outline(comp)


def _hurt_costume_composite(palette, paint_fn, draw_std_lenses, damage_over_costume, angle_deg):
    """Last_life for palette-based costume skins.
    damage_over_costume=True: paint_fn first, dressings on top (mummy).
    damage_over_costume=False: dressings first, paint_fn (hat/hood) on top."""
    body = _build_parrot_with_palette(angle_deg, palette, draw_lenses=False)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    if damage_over_costume and paint_fn:
        paint_fn(comp, angle_deg)
    _h_draw_bandaids(sprite)
    _h_draw_headwrap(sprite)
    _h_draw_chest_dressing(sprite)
    _h_draw_ragged_cuts(sprite)
    if draw_std_lenses:
        _draw_lenses(sprite, 50, 20, palette)
    _open_beak(sprite, palette)
    _h_draw_cracked_lens(sprite)
    if not damage_over_costume and paint_fn:
        paint_fn(comp, angle_deg)
    return _add_outline(comp)


def _fh_costume_composite(palette, paint_fn, draw_std_lenses, damage_over_costume, angle_deg):
    """First_hit for palette-based costume skins."""
    body = _build_parrot_with_palette(angle_deg, palette, draw_lenses=False)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    comp.blit(body, (0, PARROT_DY))
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    if damage_over_costume and paint_fn:
        paint_fn(comp, angle_deg)
    _open_beak(sprite, palette)
    _h_draw_bandaids(sprite)
    if draw_std_lenses:
        _draw_lenses(sprite, 50, 20, palette)
    _fh_draw_single_crack(sprite)
    if not damage_over_costume and paint_fn:
        paint_fn(comp, angle_deg)
    return _add_outline(comp)


def _hurt_viking(angle_deg):
    """Viking last_life: axe behind body, helm + face over dressings."""
    body = _build_parrot_with_palette(angle_deg, _VK_PAL, draw_lenses=False)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    _viking_axe(comp)
    comp.blit(body, (0, PARROT_DY))
    _viking_back(comp)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _h_draw_bandaids(sprite)
    _h_draw_headwrap(sprite)
    _viking_helm(comp)
    _viking_face(comp)
    _h_draw_chest_dressing(sprite)
    _h_draw_ragged_cuts(sprite)
    _h_draw_cracked_lens(sprite)
    return _add_outline(comp, outline_color=_VK_OUTLINE)


def _fh_viking(angle_deg):
    """Viking first_hit."""
    body = _build_parrot_with_palette(angle_deg, _VK_PAL, draw_lenses=False)
    comp = pygame.Surface((64, 100), pygame.SRCALPHA)
    _viking_axe(comp)
    comp.blit(body, (0, PARROT_DY))
    _viking_back(comp)
    sprite = comp.subsurface((0, PARROT_DY, 64, 60))
    _h_draw_bandaids(sprite)
    _viking_helm(comp)
    _viking_face(comp)
    _fh_draw_single_crack(sprite)
    return _add_outline(comp, outline_color=_VK_OUTLINE)


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


def _prebuild_pair(ll_fn, fh_fn):
    """Return lazy (ll_getter, fh_getter); frames built on first call per state."""
    ll_state: dict = {}
    fh_state: dict = {}

    def ll_getter(frame_idx, tilt_deg):
        if "g" not in ll_state:
            ll_state["g"] = _make_getter([ll_fn(a) for a in _H_HURT_ANGLES], {})
        return ll_state["g"](frame_idx, tilt_deg)

    def fh_getter(frame_idx, tilt_deg):
        if "g" not in fh_state:
            fh_state["g"] = _make_getter([fh_fn(a) for a in _H_HURT_ANGLES], {})
        return fh_state["g"](frame_idx, tilt_deg)

    return (ll_getter, fh_getter)


# ── skin registry ──────────────────────────────────────────────────────────────
# Each entry: skin_id -> (ll_getter, fh_getter)
# Getters are built lazily on first import of this module.

def _build_registry():
    reg = {}

    # helper lambdas capture the palette/fn args at definition time
    def _simple(pal):
        return _prebuild_pair(
            lambda a: _hurt_simple(pal, a),
            lambda a: _fh_simple(pal, a),
        )

    def _composite(pal, paint_fn, back_fn, outline_color, draw_std_lenses):
        return _prebuild_pair(
            lambda a: _hurt_composite(pal, paint_fn, back_fn, outline_color,
                                      draw_std_lenses, a),
            lambda a: _fh_composite(pal, paint_fn, back_fn, outline_color,
                                    draw_std_lenses, a),
        )

    # Special skins
    reg["skin_skeleton"] = _prebuild_pair(_hurt_skeleton, _fh_skeleton)
    reg["skin_zombie"]   = _prebuild_pair(_hurt_zombie,   _fh_zombie)

    # Pure-palette skins
    reg["skin_bluegold"]  = _simple(P_BLUEGOLD)
    reg["skin_amazon"]    = _simple(P_AMAZON)
    reg["skin_sunconure"] = _simple(P_SUNCONURE)
    reg["skin_hyacinth"]  = _simple(P_HYACINTH)
    reg["skin_lorikeet"]  = _simple(P_LORIKEET)

    # Composite skins — paint_fn only (no back layer)
    reg["skin_disco"]      = _composite(P_DISCO,     _paint_disco,      None, None, True)
    reg["skin_prism"]      = _composite(P_PRISM,     _paint_prism,      None, None, True)
    reg["skin_thorncrest"] = _composite(P_THORNCREST,_paint_thorncrest, None, None, True)
    reg["skin_embermoth"]  = _composite(P_EMBERMOTH, _paint_embermoth,  None, None, True)
    reg["skin_binky"]      = _composite(P_BINKY,     _paint_binky,      None, None, True)

    # Cockatoo — back_fn only (crest composited behind body in all states)
    reg["skin_cockatoo"] = _composite(P_COCKATOO, None, _paint_cockatoo_crest, None, True)

    # Composite skins — both paint_fn + back_fn
    reg["skin_aurora"]    = _composite(_AURORA_PAL, _aurora_front,    _aurora_back,    None,       True)
    reg["skin_moonbloom"] = _composite(P_MOONBLOOM, _moonbloom_front, _moonbloom_back, _MB_OUTLINE, True)
    reg["skin_tempest"]   = _composite(P_TEMPEST,   _tempest_front,   _tempest_back,   _TP_OUTLINE, True)

    # Chrome — composite, draw_std_lenses=False (chrome_front owns lenses)
    reg["skin_chrome"] = _composite(P_CHROME, _chrome_front, _chrome_back, None, False)

    def _std(paint_fn):
        return _prebuild_pair(
            lambda a: _hurt_std_accessory(paint_fn, a),
            lambda a: _fh_std_accessory(paint_fn, a),
        )

    def _costume(pal, paint_fn, draw_std_lenses, damage_over_costume=False):
        return _prebuild_pair(
            lambda a: _hurt_costume_composite(pal, paint_fn, draw_std_lenses,
                                              damage_over_costume, a),
            lambda a: _fh_costume_composite(pal, paint_fn, draw_std_lenses,
                                            damage_over_costume, a),
        )

    # Group A — standard macaw + costume accessory
    reg["skin_pirate"]     = _std(_paint_pirate)
    reg["skin_cowboy"]     = _std(_paint_cowboy)
    reg["skin_pharaoh"]    = _std(_paint_pharaoh)
    reg["skin_crown"]      = _std(_paint_crown)
    reg["skin_baseball"]   = _std(_paint_baseball)
    reg["skin_tennis"]     = _std(_paint_tennis)
    reg["skin_wizard"]     = _std(_paint_wizard)

    # skin_basketball: stub store_data if missing (branch without STORE_FILE)
    import sys, types  # noqa: PLC0415
    if 'game.store_data' not in sys.modules:
        sys.modules['game.store_data'] = types.ModuleType('game.store_data')
    from game.skin_basketball import _paint_laker  # noqa: PLC0415
    reg["skin_basketball"] = _std(_paint_laker)

    # Group B — custom palette, no lenses
    reg["skin_tophat"]    = _costume(_TH_BODY,    _paint_tophat,    False)
    reg["skin_ninja"]     = _costume(P_NINJA,     _paint_ninja,     False)
    reg["skin_mummy"]     = _costume(_MU_BODY,    _paint_mummy,     False, True)
    reg["skin_astronaut"] = _costume(P_ASTRONAUT, _paint_astronaut, False)

    # Group C — custom palette, with lenses
    reg["skin_pilot"] = _costume(P_PILOT, _paint_pilot, True)

    # Group D — full custom composite
    reg["skin_viking"] = _prebuild_pair(_hurt_viking, _fh_viking)

    return reg


SKIN_HURT_GETTERS: dict = _build_registry()

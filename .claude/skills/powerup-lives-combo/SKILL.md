---
name: powerup-lives-combo
description: >-
  Reference for rendering a Pip sprite that combines a power-up effect with a
  lives state (first_hit or last_life) outside of Bird.draw() — e.g. grid
  visualisations, store card thumbnails, or any standalone renderer.
  Covers the three effect categories (palette-based, scale-only, hat composite),
  the correct draw order for lenses vs. headwrap, parcel rules per effect,
  and copy-paste code snippets for ghost tint and hat compositing.
  Use whenever a rendering surface other than Bird.draw() must show a
  power-up + lives-state combination.
---

# Power-up × lives-state combo rendering

Use this skill when:
- Building a new preview grid or store card thumbnail that shows power-up + lives combinations
- Extending `docs/render_lives_powerup_grid.py` with a new effect column
- Porting the pattern to a new rendering surface (e.g. store card dome thumbnails)

The canonical live implementations are the special-case branches inside `render_cell()` in
`docs/render_store_skin_powerup_lives_grid.py`. Read those as ground truth.

---

## The three effect categories

### A. Palette-based (`_build_parrot_with_palette` with a non-red palette)

| Effect | Palette | Lenses | Special overlay | Parcel |
|---|---|---|---|---|
| `ghost` | `P_SPECTRAL` | Deferred for `last_life` (manual after headwrap); default (`draw_lenses=True`) for `first_hit` | numpy 60/40 blend toward `(140,200,230)`, then `set_alpha(170)` | `"ghost"` mode, `set_alpha(170)`, at `BIRD_Y+12` |
| `poison` | `P_CHARTREUSE` | Always `draw_lenses=False` (all states, all skins) | Skin-aware dispatch: no-element skins → `_build_poison_hurt`; element skins → `_build_poison_skin` with `_poison_tint` (see section below) | None |

### B. Scale-only (red hurt frame, scaled after `_add_outline`)

| Effect | Frame builder | Scale | Parcel |
|---|---|---|---|
| `grow` | `_h_build_hurt_frame(angle)` / `_fh_build_hurt_frame(angle)` | `GROW_SCALE=1.4` via `pygame.transform.smoothscale` after `_add_outline` | `"normal"` mode, scaled × `GROW_SCALE`, at `BIRD_Y + int(PARCEL_Y_OFFSET × GROW_SCALE)` |

### C. Hat composite (hurt frame on taller canvas, hat drawn last)

Canvas layout from `dollar_parrot_hat.py`: `COMPOSITE_W=64`, `COMPOSITE_H=100`, parrot blitted at `(0, PARROT_DY=20)`, hat anchor at `(HAT_HX=47, HAT_HY=30)`.

| Effect | Base frame | Hat function | Ghost processing | Parcel |
|---|---|---|---|---|
| `triple` | red hurt/first_hit | `draw_stovepipe(canvas, HAT_HX, HAT_HY)` | None | `"normal"`, at `BIRD_Y+12` |
| `ghost_triple` | P_SPECTRAL hurt/first_hit | `draw_stovepipe_ghost(canvas, HAT_HX, HAT_HY)` | numpy blend + `set_alpha(170)` on composite | `"ghost"`, `set_alpha(170)`, at `BIRD_Y+12` |

---

## Palette-based last_life draw order

```python
base = _build_parrot_with_palette(angle, PALETTE, draw_lenses=False)
_h_draw_bandaids(base)
_h_draw_headwrap(base)
# Ghost only:  _draw_lenses(base, 50, 20, PALETTE)   ← lenses after headwrap
_h_draw_chest_dressing(base)
_h_draw_ragged_cuts(base)
_h_draw_cracked_lens(base)
# Poison only: _draw_b_x_eyes(base)                  ← X-eyes on top of everything
img = _add_outline(base)
# Ghost only: apply numpy tint + set_alpha(170)
```

**Critical:** headwrap must precede lenses. Ghost re-adds lenses manually after headwrap
(matching `_h_build_hurt_frame`'s draw order). Poison never adds lenses — X-eyes
replace them and must be drawn last so they overlay all dressings.

---

## Palette-based first_hit draw order

```python
base = _build_parrot_with_palette(angle, PALETTE, draw_lenses=False)
_h_draw_bandaids(base)
_fh_draw_single_crack(base)   # omit for poison: crack sits on the lens; no lens → no crack
# Poison only: _draw_b_x_eyes(base)
img = _add_outline(base)
# Ghost only: apply numpy tint + set_alpha(170)
```

---

## Ghost tint snippet (copy verbatim)

Luminance remap to spectral blue, alpha scaled to 170/255:

```python
import numpy as np
import pygame.surfarray as sa

def _ghost_tint(img):
    arr = sa.pixels3d(img)
    f = arr.astype(np.float32)
    lum = f[:,:,0]*0.299 + f[:,:,1]*0.587 + f[:,:,2]*0.114
    lum_n = lum / 255.0
    dark   = np.array([ 50,  95, 145], np.float32)
    bright = np.array([200, 230, 245], np.float32)
    for c in range(3):
        f[:,:,c] = dark[c] + lum_n * (bright[c] - dark[c])
    arr[:] = f.clip(0, 255).astype(np.uint8)
    del arr
    if img.get_flags() & pygame.SRCALPHA:
        alpha = sa.pixels_alpha(img)
        alpha[:] = (alpha.astype(np.float32) * (170/255)).clip(0, 255).astype(np.uint8)
        del alpha
    else:
        img.set_alpha(170)
```

---

## Skin-aware poison rendering

Poison is unique: not only the body but all skin accessories (bones, zombie aura,
`paint_fn` sparkles, `back_fn` wings) must remap to chartreuse. This requires a
two-stage dispatch based on whether the skin has element accessories.

### Dispatch

```python
has_elements = (paint_fn is not None or back_fn is not None or special is not None)
if not has_elements:
    # Plain P_CHARTREUSE body + lives dressings + X-eyes
    if lives_state == "clean":
        img = get_poisoned_parrot(1, 0.0)
    else:
        img = _build_poison_hurt(lives_state)
else:
    img = _build_poison_skin(palette, paint_fn, back_fn, outline_color,
                             draw_std_lenses, special, lives_state)
```

### _poison_tint snippet

```python
def _poison_tint(img):
    arr = sa.pixels3d(img)
    f = arr.astype(np.float32)
    lum = f[:,:,0]*0.299 + f[:,:,1]*0.587 + f[:,:,2]*0.114
    lum_n = lum / 255.0
    dark   = np.array([ 30,  75, 10], np.float32)
    bright = np.array([200, 240, 75], np.float32)
    for c in range(3):
        f[:,:,c] = dark[c] + lum_n * (bright[c] - dark[c])
    arr[:] = f.clip(0, 255).astype(np.uint8)
    del arr
    # No alpha scaling — elements keep full opacity
```

### Standard composite path (paint_fn / back_fn skins)

Unified flow regardless of `lives_state` — never split into separate clean / hurt branches:

1. `body = _build_parrot_with_palette(10.0, P_CHARTREUSE, draw_lenses=False)`
2. Blit body into 64×100 `comp` at `(0, PARROT_DY)`
3. `if paint_fn: paint_fn(comp, 10.0)`
4. `_poison_tint(comp)` — tints body + accessories together
5. `sprite = comp.subsurface((0, PARROT_DY, 64, 60))`
6. If `last_life`: bandaids → headwrap → chest dressing → ragged cuts → cracked lens
7. If `first_hit`: bandaids → single crack
8. `_draw_b_x_eyes(sprite)` — always last; ink stays dark because tint ran first
9. `outlined = _add_outline(comp, outline_color=…)`
10. If `back_fn`: build 64×100 back, call `back_fn(back, 10.0)`, `_poison_tint(back)`,
    then blit behind `outlined` in a padded result surface

**Never use `_open_beak` or `_draw_lenses` in any poison path.**

### Skeleton special path

1. Build P_CHARTREUSE body `draw_lenses=False`, blit at `(0, PARROT_DY)` into 64×100 comp
2. `_skeleton_paint(comp, 10.0)` — draws bones over body
3. `_poison_tint(comp)` — tints bones + body chartreuse together
4. Get sprite subsurface; apply dressings / `_eye_socket` by `lives_state`
5. `_draw_b_x_eyes(sprite)` last

### Zombie special path

1. Build P_CHARTREUSE body `draw_lenses=False`; apply dressings by `lives_state`; `_draw_b_x_eyes`
2. `core = _add_outline(base)`
3. Build padded outer surface; `_zb_hex_aura(out, …)` draws the aura into `out`
4. `_poison_tint(out)` — tints the hex aura chartreuse; core is not yet on the surface
5. Blit `_zb_rim_halo(core)` then `core` on top of the now-tinted outer surface

---

## Hat composite snippet (copy verbatim)

```python
from game.dollar_parrot_hat import COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY
canvas = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
canvas.blit(base, (0, PARROT_DY))
draw_stovepipe(canvas, HAT_HX, HAT_HY)          # triple
# draw_stovepipe_ghost(canvas, HAT_HX, HAT_HY)  # ghost_triple
img = _add_outline(canvas)
```

For `ghost_triple`: apply the ghost tint snippet to `img` after `_add_outline`.

---

## Key imports

| Symbol | Module |
|---|---|
| `_build_parrot_with_palette`, `P_SPECTRAL`, `_draw_lenses` | `game.dollar_parrot_ghost` |
| `P_CHARTREUSE`, `_draw_b_x_eyes` | `game.dollar_parrot_dead` |
| `draw_stovepipe`, `draw_stovepipe_ghost`, `COMPOSITE_W`, `COMPOSITE_H`, `PARROT_DY`, `HAT_HX`, `HAT_HY` | `game.dollar_parrot_hat` |
| `_h_build_hurt_frame`, `_fh_build_hurt_frame`, `_h_draw_bandaids`, `_h_draw_headwrap`, `_h_draw_chest_dressing`, `_h_draw_ragged_cuts`, `_h_draw_cracked_lens`, `_fh_draw_single_crack`, `_add_outline`, `get_parcel` | `game.parrot` |
| `GROW_SCALE`, `PARCEL_Y_OFFSET` | `game.config` |

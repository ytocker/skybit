---
name: parrot-lives-skin
description: >-
  Reference for adding or modifying a Pip the Parrot appearance for a lives-phase
  skin (clean → first-hit → last-life, or any future state). Covers the 64×60 px
  canvas anatomy, every colour constant, the correct drawing order, dressing
  primitives (_stamp_clipped pattern, bandaids, cracks, headwrap), and the
  three-file wiring pattern (parrot.py + entities.py + world.py).
  Use whenever you need to design, build, or change a lives-phase parrot skin.
---

# Parrot lives-skin reference

Use this skill when:
- Adding a new skin for a new `lives_remaining` value
- Modifying an existing skin (first-hit or last-life)
- Debugging positioning of a dressing element

The canonical reference implementations are:
- **Last-life (ace-headwrap):** `docs/hurt-parrot-v5-plus2/ace-headwrap/design.py`
- **First-hit:** `docs/hurt-parrot-v5-first-life/first-hit/design.py`
- **In-game skins:** `game/parrot.py` (all `_h_*` and `_fh_*` helpers + public `get_*` functions)

---

## Canvas and coordinate system

- **Sprite size:** 64 × 60 px, `pygame.SRCALPHA`, origin top-left, y increases downward
- **After `_add_outline`:** 68 × 64 px (2 px dark halo on each side)
- **Wing angles for hurt skins:** `_H_HURT_ANGLES = (10, -5, -20, -35)` degrees
  (shallower than the clean bird's (50, 20, -10, -40) — reads as laboured flap)
- **Sheet layout for `docs/` preview:** 4-frame strip starting at `(x=20, y=20)`,
  `gap=10`, dark BG `(8,8,20)`. The hero frame (angle=10°) is always top-left.

---

## Body anatomy — pixel coordinates

| Part | Key coordinates / sizes |
|---|---|
| **Tail** | Fan of 4 polygons, each shifted `i*3 x, i*2 y` (i=0–3); spans x≈2–20, y≈26–36 |
| **Body shadow** | Ellipse center (34,35) rx=19 ry=14 |
| **Body main** | Ellipse center (32,32) rx=19 ry=14 |
| **Chest highlight** | Ellipse center (30,29) rx=13 ry=8 |
| **Belly** | Ellipse center (28,38) rx=12 ry=6 |
| **Sheen strip** | 28×6 surface blitted at (22,21), alpha=120 |
| **Wing anchor** | Built on 50×50 surface, blitted with center at **(34,28)** |
| **Head shadow** | Ellipse center (48,24) rx=12 ry=11 |
| **Head main** | Ellipse center (47,22) rx=12 ry=11 |
| **Cheek flush** | Ellipse center (44,24) rx=4 ry=3 |
| **Crown highlight** | Ellipse center (46,17) rx=7 ry=3 |
| **Sunglasses anchor** | `_h_draw_sunglasses(surf, cx=50, cy=20)` |
| **Left lens centre** | (46, 22) — `cx-4, cy+2` in hurt skins |
| **Right lens centre** | (56, 19) — `cx+6, cy-1` |
| **Beak upper jaw** | `[(55,21),(61,24),(58,26),(52,25)]` |
| **Beak lower jaw** | `[(52,26),(58,27),(59,30),(54,31)]` |
| **Left foot** | Line (28,45)→(26,49) width=2 |
| **Right foot** | Line (34,45)→(36,49) width=2 |

---

## Colour constants (all in `game/parrot.py`, prefix `_H_`)

| Constant | RGB | Role |
|---|---|---|
| `_H_GAUZE` | (198,190,172) | Dressing pad fill — bandaids, chest pad, headwrap cap |
| `_H_HEM` | (120,108,95) | Dressing border/seam lines |
| `_H_STITCH` | (180,170,160) | Adhesive tab stitch marks |
| `_H_CROSS` | (190,20,35) | Red cross on chest dressing |
| `_H_CRACK` | (150,175,205) | Lens crack lines (pale steel-blue) |
| `_H_SCRATCH_D` | (100,10,10) | Wound gash dark core |
| `_H_SCRATCH_HL` | (245,165,150) | Wound gash highlight lip |
| `_H_SCRATCH_PALE` | (180,90,80) | Wound on dark background / seep under headwrap |
| `_H_SHADE_BLACK` | (15,15,25) | Lens body fill |
| `_H_SHADE_GLINT` | (255,255,255) | Lens white glint dot |
| `_H_SHADE_FRAME` | (220,175,40) | Gold aviator frame rim |

Body colours (local to each `_build_hurt_frame` function — copy as-is):

| Name | RGB |
|---|---|
| BODY | (205,28,28) |
| BODY_SH | (130,12,12) |
| CHEST | (235,80,80) |
| BELLY | (215,140,45) |
| BEAK / BEAK_LO / BEAK_D | (235,168,0) / (205,138,0) / (140,92,0) |

---

## Correct drawing order

Draw in this order inside any `_build_hurt_frame` function:

1. `_h_draw_tail(surf)` — tail goes behind everything
2. Body shadow → body → chest → belly → sheen strip
3. Wing (build with `_h_build_wing(angle)`, blit with center=(34,28))
4. Ragged cuts, if any (last-life only) — must be under bandaids
5. Bandaids — via `_h_stamp_clipped` (see below)
6. Head shadow → head → cheek → crown highlight
7. Headwrap cap — via `_h_stamp_clipped`; knot tails direct to `surf` (last-life only)
8. Sunglasses — `_h_draw_sunglasses(surf, 50, 20)` — direct to `surf`
9. Lens cracks — direct to `surf`
10. Chest dressing — via `_h_stamp_clipped` (last-life only)
11. Beak upper jaw → lower jaw → gloss line
12. Feet lines

Then call `_add_outline(surf)` — this returns a NEW 68×64 surface; it does not modify in-place.

---

## Tinted palette variants (e.g. poison)

When a status effect replaces the body palette (e.g. poison → `P_CHARTREUSE`):

- Always pass `draw_lenses=False` to `_build_parrot_with_palette` — no sunglasses on
  any tinted hurt skin; X-eyes replace them.
- Draw dressings (bandaids, headwrap, chest dressing, cuts) **AFTER** the tint step
  so GAUZE/HEM/CROSS retain their original colours.
- Draw `_draw_b_x_eyes(surf)` **LAST** — after all dressings — so the ink stays dark.
- For element skins (skins with `paint_fn`, `back_fn`, or `special` accessories),
  apply a luminance-remap tint function (e.g. `_poison_tint`) **AFTER** element
  accessories are composited and **BEFORE** dressings/X-eyes. This ensures accessories
  match the tinted palette without affecting the dressings drawn afterward.
- For `back_fn` elements (wings, aura that sit behind the bird), apply the same tint
  to the back surface before compositing it behind the outlined bird.
- Never call `_open_beak` or `_draw_lenses` in a tinted hurt path.

Luminance remap pattern (copy and adjust `dark`/`bright` for the target palette):

```python
def _<effect>_tint(img):
    arr = sa.pixels3d(img)
    f = arr.astype(np.float32)
    lum = f[:,:,0]*0.299 + f[:,:,1]*0.587 + f[:,:,2]*0.114
    lum_n = lum / 255.0
    dark   = np.array([R_dark,  G_dark,  B_dark ], np.float32)
    bright = np.array([R_bright, G_bright, B_bright], np.float32)
    for c in range(3):
        f[:,:,c] = dark[c] + lum_n * (bright[c] - dark[c])
    arr[:] = f.clip(0, 255).astype(np.uint8)
    del arr
    # Add alpha scaling here if the effect requires transparency (e.g. ghost)
```

Canonical reference: `_build_poison_hurt` and `_build_poison_skin` in
`docs/render_store_skin_powerup_lives_grid.py`.

---

## Dressing primitives

### `_h_stamp_clipped(surf, layer)`

Clips a dressing layer to the existing bird silhouette. For every pixel where
**both** `surf` and `layer` have alpha > 8, it replaces `surf`'s RGB with `layer`'s
RGB while preserving `surf`'s alpha. Use for bandaids, chest dressing, headwrap cap.
Do NOT use for elements that should extend outside the silhouette (e.g. headwrap
knot tails — draw those directly on `surf`).

### Bandaid positions (used by `_h_draw_bandaids`)

Three bandaids; bounding box as (x0, y0, x1, y1):

| Slug | Bounding box | Side tabs face |
|---|---|---|
| BANDAID_L (left flank) | (12,40,24,46) | left |
| BANDAID_R (right lower body) | (33,37,44,43) | right |
| BANDAID_3 (upper-right body) | (38,33,47,38) | right |

Drawing per bandaid: stitch-tab lines in `_H_STITCH` → GAUZE filled rect →
HEM 1-px outline → composite via `_h_stamp_clipped`.

### Lens cracks

- **Single crack (first-hit):** `pygame.draw.line(surf, _H_CRACK, (45,21), (47,26), 1)`
- **Full spiderweb (last-life):** three lines from (45,21) to (41,17), (50,18), (47,26);
  plus cross (43,19)→(47,23). All width=1.

### Chest dressing

Quadrilateral polygon `[(20,23),(30,21),(31,34),(21,36)]`, filled GAUZE with HEM
border; red cross at center; four STITCH corner ticks. Last-life only.

### Headwrap cap

Cap polygon follows the crown arc from (36,21) to (59,21). Filled GAUZE with HEM
border, two interior seams, an occipital knot. Knot tails extend past silhouette —
draw them directly to `surf` after `_h_stamp_clipped`. Last-life only.

---

## Wiring a new skin into the game (3 files)

### 1. `game/parrot.py`

Add after the existing `get_hurt_parrot` / `get_first_hit_parrot` block:

```python
# ── <phase> parrot (lives_remaining == N) ────────────────────────────────────

def _<prefix>_build_hurt_frame(wing_angle_deg: float) -> pygame.Surface:
    surf = pygame.Surface((64, 60), pygame.SRCALPHA)
    # ... draw tail, body, wing, dressings, head, beak, feet ...
    return surf

_<prefix>_frames: list | None = None
_<prefix>_rot_cache: dict = {}

def _get_<prefix>_frames() -> list:
    global _<prefix>_frames
    if _<prefix>_frames is None:
        _<prefix>_frames = [_add_outline(_<prefix>_build_hurt_frame(a))
                            for a in _H_HURT_ANGLES]
    return _<prefix>_frames

def get_<prefix>_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _get_<prefix>_frames()
    key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _<prefix>_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _<prefix>_rot_cache[key] = s
    return s
```

### 2. `game/entities.py`

**`Bird.__init__`** — add a flag after the other `on_*` flags near line 532:
```python
self.on_<phase> = False
```

**`Bird.draw()`** — insert a new branch in the skin cascade (after `on_last_life`,
before the clean-parrot `else`):
```python
elif self.on_<phase>:
    img = parrot.get_<prefix>_parrot(frame_idx, tilt)
```

Priority: `on_last_life` → `on_first_hit` → … → clean. Always put the most severe
skin highest in the cascade.

### 3. `game/world.py`

**`_revive_life()`** — extend the `lives_remaining` check:
```python
if self.lives_remaining == 0:
    self.bird.on_last_life = True
    self.bird.on_first_hit = False   # clear less-severe skin
elif self.lives_remaining == 1:
    self.bird.on_first_hit = True
# elif self.lives_remaining == N:
#     self.bird.on_<phase> = True
```

---

## Verification

After wiring a new skin:

```bash
# 1. Headless import check
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=offscreen python -c "
import game.parrot as p
s = p.get_<prefix>_parrot(0, 10.0)
print('sprite size:', s.get_size())   # expect ~(78, 74) after _add_outline
"

# 2. Run the standalone design script if one exists
python docs/<feature>/<slug>/design.py

# 3. Render a comparison figure
python docs/build_<feature>_comparison.py
```

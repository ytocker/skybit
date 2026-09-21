# The Iron Flower — removed

`states.png` is the record of night event **N2, The Iron Flower**, a
molten-iron fire show (*dashuhua*) that ran once per festival night until it
was removed at the user's request.

It was never only its 8-second act. One object, `festival.draw_scaffold`,
carried it through the whole day in three states — and all three are gone:

| Panel | State | When it ran |
|---|---|---|
| 1 | `'bare'` — a scaffold planted on the street, ~6 blocks a day | φ0.483 – 0.680 |
| 2 | the same rig standing dark through the evening storm | φ0.610 |
| 3 | `'manned'`/`'burst'` — the show itself, 8 s | φ0.706 – 0.727 |
| 4 | `'cold'` — the burnt rig + scorch fan at dawn, ~1 night in 3 | φ0.820 – 0.924 |

The dawn residue survives as the troupe's dropped paper masks only; nothing
on the street scorches any more. The figure was rendered from the live build
by `tools/iron_flower_states.py`, which was deleted in the same change
because it drives drawers that no longer exist — recover it from the history
alongside this file if the show is ever wanted back.

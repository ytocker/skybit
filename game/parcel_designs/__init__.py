"""Procedural PARCEL designs — one self-contained module per look.

Each module exposes ``build(mode="normal") -> Surface`` returning a square
sprite (``PARCEL_SIZE`` px, a couple larger for a glow skirt), drawn entirely
from code. ``game.parcel_skins`` imports these and registers them in the
PARCELS-tab builder/icon registries; ``parrot.get_parcel`` dispatches to them
by equipped id. Matured on per-design art-director loops under docs/parcels/.
"""

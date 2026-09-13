"""GAME COIN parcel — the EXACT in-game collectible coin, carried as the gift.

Reuses entities._get_coin_face() (the real face-on coin: rope rim, gold
gradient, embossed parrot, specular) so the parcel is pixel-identical to the
coins Pip collects, just smoothscaled to the parcel footprint. Mode-agnostic.
"""
import pygame

_SIZE = 22   # standard parcel footprint (PARCEL_SIZE) — no larger than a parcel


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    from game import entities          # lazy: avoid an import cycle at load
    face = entities._get_coin_face()    # the real coin sprite (super-sampled)
    if icon_size:
        return pygame.transform.smoothscale(face, (icon_size, icon_size))
    return pygame.transform.smoothscale(face, (_SIZE, _SIZE))

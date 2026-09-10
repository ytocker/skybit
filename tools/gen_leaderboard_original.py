"""Throwaway: render the CURRENT (pre-change) leaderboard screen as a baseline
"original" for side-by-side comparison with the tabbed-leaderboard explorations.
Run: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/gen_leaderboard_original.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.hud import HUD, _font, _GOLD_MUTED

S = 3
scores = [
    {"name": "OG_FLAP",   "score": 410},
    {"name": "GrandPaw",  "score": 366},
    {"name": "DodoKing",  "score": 318},
    {"name": "AceWings",  "score": 275},
    {"name": "RubyBeak",  "score": 240},
    {"name": "OldGuard",  "score": 205},
    {"name": "Comet",     "score": 178},
    {"name": "Vinyl",     "score": 152},
    {"name": "Bramble",   "score": 134},
    {"name": "Marble",    "score": 120},
]

hd = pygame.Surface((W * S, H * S), pygame.SRCALPHA)
# _render_leaderboard never reads self; call it unbound with self=None.
HUD._render_leaderboard(None, hd, scores, -1, "", S)

# Add the pulsing TAP TO MENU prompt at a static mid-pulse alpha so the
# baseline matches what a player actually sees.
f2 = _font(16 * S, True)
prompt = f2.render("TAP  TO  MENU", True, _GOLD_MUTED)
prompt.set_alpha(210)
hd.blit(prompt, prompt.get_rect(center=(W * S // 2, H * S - 28 * S)))

out = pygame.transform.smoothscale(hd, (W, H))
os.makedirs("docs/leaderboard", exist_ok=True)
path = "docs/leaderboard/original_leaderboard.png"
pygame.image.save(out, path)
print("wrote", os.path.abspath(path), out.get_size())

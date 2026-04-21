import pyxel
from .config import TRIPLE_DURATION
from .palette import INK, CREAM, GOLD, ORNG, NAVY, WHITE, DKRED, GREEN, RED
from .sprites import draw_text, draw_text_c, text_w, draw_mushroom, draw_coin


def draw_hud(world, high_score):
    W = pyxel.width

    # Score (large, top-centre)
    s  = str(world.score)
    sw = text_w(s, 2)
    draw_text(s, (W - sw) // 2, 8, WHITE, 2, shadow_col=INK)

    # High score (top-left)
    draw_text(f'HI {high_score}', 4, 4, CREAM, 1, shadow_col=INK)

    # Coin count (top-right, with tiny coin icon)
    cs  = f'x{world.coin_count}'
    cw  = text_w(cs)
    cx  = W - cw - 14
    pyxel.circ(W - cw - 10, 6, 3, GOLD)
    pyxel.pset(W - cw - 11, 5, CREAM)
    draw_text(cs, cx + 3, 4, GOLD, 1, shadow_col=INK)

    # Pause button (top-right)
    px, py = W - 14, 14
    pyxel.rect(px, py, 11, 11, INK)
    pyxel.rect(px + 1, py + 1, 9, 9, NAVY)
    pyxel.rect(px + 3, py + 3, 2, 5, CREAM)
    pyxel.rect(px + 6, py + 3, 2, 5, CREAM)

    # Triple-score timer bar
    if world.triple_t > 0:
        bw = 70; bh = 4
        bx = (W - bw) // 2; by = 24
        pyxel.rect(bx - 1, by - 1, bw + 2, bh + 2, INK)
        pyxel.rect(bx, by, bw, bh, NAVY)
        fill = max(0, min(bw, int(bw * world.triple_t / TRIPLE_DURATION)))
        pyxel.rect(bx, by, fill, bh, ORNG)
        draw_text_c('3X POWER', by - 8, CREAM, 1, shadow_col=INK)

    # Combo badge
    if world.combo >= 2:
        lbl = f'X{world.combo} COMBO!'
        draw_text_c(lbl, pyxel.height - 28, ORNG, 1, shadow_col=INK)

    # Floating "+1"/"+3" texts
    for f in world.floats:
        lw = text_w(f.text)
        draw_text(f.text, int(f.x) - lw//2, int(f.y), f.col, 1, shadow_col=INK)

    # Pause-button hit rect returned for input
    return (px, py, 11, 11)


def draw_title(t):
    W = pyxel.width
    bob = int(2 * pyxel.sin(t * 60 * 0.4))   # pyxel.sin is degree-based
    y   = 52 + bob

    # Shadow
    draw_text('SKYBIT', (W - text_w('SKYBIT', 3))//2 + 2, y + 2, INK, 3)
    # Gold layer
    draw_text('SKYBIT', (W - text_w('SKYBIT', 3))//2 + 1, y - 1, GOLD, 3)
    # Orange layer
    draw_text('SKYBIT', (W - text_w('SKYBIT', 3))//2,     y,     ORNG, 3)

    draw_text_c('A RETRO PIXEL FLYER', y + 24, CREAM, 1, shadow_col=INK)

    # Preview parrot + coins
    from .sprites import draw_parrot_tilt, draw_coin
    draw_parrot_tilt(40, 155, int(t * 4) % 4, -50)
    draw_coin(85,  158, t)
    draw_coin(100, 152, t + 1.0)
    draw_mushroom_small(130, 162, t)


def draw_mushroom_small(x, y, t):
    from .sprites import draw_mushroom
    draw_mushroom(x, y, t)


def draw_start_hint():
    W = pyxel.width
    y1, y2 = 178, 194
    draw_text_c('TAP TO FLAP',             y1, WHITE, 1, shadow_col=INK)
    draw_text_c('COLLECT COINS',           y2, GOLD,  1, shadow_col=INK)
    draw_text_c('GRAB MUSHROOM FOR 3X!', y2+12, ORNG,  1, shadow_col=INK)


def draw_game_over(score, high, new_best):
    W = pyxel.width
    y = 82
    draw_text_c('GAME OVER', y,     DKRED, 2, shadow_col=INK)
    draw_text_c(f'SCORE {score}',   y+24, WHITE, 1, shadow_col=INK)
    draw_text_c(f'BEST  {high}',    y+36, GOLD,  1, shadow_col=INK)
    if new_best:
        draw_text_c('NEW BEST!',    y+50, ORNG,  1, shadow_col=INK)
    draw_text_c('TAP TO RETRY',     y+70, CREAM, 1, shadow_col=INK)


def draw_paused():
    # Dim the screen
    pyxel.dither(0.5)
    pyxel.rect(0, 0, pyxel.width, pyxel.height, INK)
    pyxel.dither(1.0)
    draw_text_c('PAUSED',     pyxel.height//2 - 12, WHITE, 2, shadow_col=INK)
    draw_text_c('TAP RESUME', pyxel.height//2 + 10, CREAM, 1, shadow_col=INK)

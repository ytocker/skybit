import pyxel

# 16-colour palette tuned for this game.
# Set once at init; referenced by index throughout.
COLORS = [
    0x050D1A,  #  0  ink-black   (outline, darkest bg)
    0x122040,  #  1  deep navy   (night sky)
    0x1F3F78,  #  2  mid blue    (dusk sky)
    0x3A72CC,  #  3  sky blue
    0x7EC8F0,  #  4  pale cyan   (horizon glow)
    0x194D14,  #  5  dark green  (pipe body)
    0x3CC43C,  #  6  vivid green (pipe cap / grass)
    0xF4F0DC,  #  7  cream/white (clouds, eye, highlight)
    0xE81818,  #  8  vivid scarlet  (parrot body)
    0xFF7800,  #  9  orange      (parrot belly / beak)
    0xFFD700,  # 10  gold        (coin, beak tip)
    0x1A4FFF,  # 11  royal blue  (parrot wing primary)
    0x22CC55,  # 12  bright green (parrot wing tip)
    0x7A4010,  # 13  dark amber  (ground dirt)
    0xB02020,  # 14  dark scarlet (parrot shadow / mushroom)
    0xFFFFFF,  # 15  pure white  (flash, coin shine)
]

# Named aliases
INK   =  0
NAVY  =  1
BLUE  =  2
SKY   =  3
CYAN  =  4
DKGRN =  5
GREEN =  6
CREAM =  7
RED   =  8
ORNG  =  9
GOLD  = 10
RBLU  = 11
WGRN  = 12
DIRT  = 13
DKRED = 14
WHITE = 15


def apply():
    for i, c in enumerate(COLORS):
        pyxel.colors[i] = c

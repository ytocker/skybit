"""
Main Pyxel App: wires input, scenes, and the world together.
"""
import pyxel
from .config import W, H, FPS, TITLE, GROUND_Y
from .palette import apply as apply_palette, INK
from .world import World
from .hud import (draw_hud, draw_title, draw_start_hint,
                  draw_game_over, draw_paused)
from .storage import load_high, save_high


class App:
    def __init__(self):
        pyxel.init(W, H, title=TITLE, fps=FPS, display_scale=3)
        apply_palette()
        pyxel.mouse(True)

        self.world     = World()
        self.high      = load_high()
        self.new_best  = False
        self.scene     = 'menu'   # 'menu' | 'play' | 'gameover'
        self.paused    = False
        self._pause_rect = (W - 14, 14, 11, 11)
        self._menu_t   = 0.0
        self._go_timer = 0.0     # delay before gameover screen shows

        pyxel.run(self.update, self.draw)

    # ── input helpers ─────────────────────────────────────────────────────

    def _tapped(self):
        """True on the first frame of any tap/click/key press."""
        return (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
                or pyxel.btnp(pyxel.KEY_SPACE)
                or pyxel.btnp(pyxel.KEY_UP)
                or pyxel.btnp(pyxel.KEY_W))

    def _pause_tapped(self):
        if not (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
                or pyxel.btnp(pyxel.KEY_P)
                or pyxel.btnp(pyxel.KEY_ESCAPE)):
            return False
        px, py, pw, ph = self._pause_rect
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        return (px <= mx <= px + pw and py <= my <= py + ph
                or pyxel.btnp(pyxel.KEY_P)
                or pyxel.btnp(pyxel.KEY_ESCAPE))

    # ── scenes ────────────────────────────────────────────────────────────

    def _to_menu(self):
        self.scene    = 'menu'
        self.new_best = False
        self._menu_t  = 0.0
        self.world.full_reset()

    def _to_play(self):
        self.scene  = 'play'
        self.paused = False
        self.world.full_reset()

    def _to_gameover(self):
        self.scene = 'gameover'
        if self.world.score > self.high:
            self.high     = self.world.score
            self.new_best = True
            save_high(self.high)

    # ── update ────────────────────────────────────────────────────────────

    def update(self):
        dt = 1 / FPS

        if self.scene == 'menu':
            self._menu_t += dt
            # Gently animate parallax on menu
            self.world.world_idle_tick(dt)
            if self._tapped():
                self._to_play()
                self.world.bird.flap()
            return

        if self.scene == 'gameover':
            self._go_timer += dt
            self.world.update(dt)     # keep particles alive
            if self._go_timer > 0.55 and self._tapped():
                self._to_menu()
            return

        # ── play ──
        if self._pause_tapped():
            self.paused = not self.paused
            return

        if self.paused:
            if self._tapped():
                self.paused = False
            return

        if self._tapped():
            if not self.world.started:
                self.world.started = True
            self.world.bird.flap()

        self.world.update(dt)

        if self.world.game_over:
            self._go_timer = 0.0
            self._to_gameover()

    # ── draw ──────────────────────────────────────────────────────────────

    def draw(self):
        pyxel.cls(INK)
        self.world.draw()

        if self.scene == 'menu':
            draw_title(self._menu_t)
            draw_start_hint()

        elif self.scene == 'play':
            if not self.world.started:
                draw_start_hint()
            self._pause_rect = draw_hud(self.world, self.high)
            if self.paused:
                draw_paused()

        elif self.scene == 'gameover':
            draw_hud(self.world, self.high)
            draw_game_over(self.world.score, self.high, self.new_best)

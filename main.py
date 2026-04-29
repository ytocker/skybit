"""Skybit entry point — runs natively and as a pygbag/WASM browser bundle.

If the game raises during init or the main loop, paint the exception onto
the canvas so the browser isn't just a silent gray rectangle. Saves a
round trip through pygbag's hidden terminal.
"""
import asyncio
import sys
import traceback


async def _run_game():
    from game.scenes import App
    await App().async_run()


async def _show_error(tb_text: str):
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((360, 640))
    pygame.display.set_caption("Skybit — error")
    font = pygame.font.Font(None, 16)
    screen.fill((25, 15, 30))
    header = font.render("Skybit crashed at startup:", True, (255, 180, 180))
    screen.blit(header, (10, 10))
    y = 36
    for line in tb_text.splitlines():
        # Wrap long lines so the whole traceback is visible on 360 px.
        while line:
            chunk, line = line[:60], line[60:]
            img = font.render(chunk, True, (240, 210, 210))
            screen.blit(img, (10, y))
            y += 18
            if y > 620:
                return await _hold(screen)
        y += 2
    await _hold(screen)


async def _hold(screen):
    import pygame
    pygame.display.flip()
    while True:
        for _ in pygame.event.get():
            pass
        await asyncio.sleep(0.1)


async def main():
    try:
        await _run_game()
    except Exception:
        import os as _os
        tb = traceback.format_exc()
        # Always log the full trace to stderr (devtools / pygbag console).
        print(tb, file=sys.stderr)
        # In production builds (no SKYBIT_DEV env var) DON'T paint the full
        # traceback onto the canvas — that's an info leak: file paths, code
        # snippets, library versions can all aid an attacker. Show a generic
        # message instead.
        is_dev = _os.environ.get("SKYBIT_DEV") == "1"
        on_canvas = tb if is_dev else (
            "Skybit hit an unexpected error.\n"
            "Please refresh / relaunch.\n"
            "If the problem persists, contact the developer."
        )
        try:
            await _show_error(on_canvas)
        except Exception:
            # If even the error screen fails, at least stdout has the trace.
            print("(also failed to render the error screen)", file=sys.stderr)


asyncio.run(main())

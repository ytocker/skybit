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
    if sys.platform == "emscripten":
        # One-time leaderboard probe at startup. Exercises the Python ↔ JS
        # bridge handshake (`window.__sk('fetch')`) before the player
        # reaches the top-10 view, so a regression in the bridge shows up
        # in the browser console immediately on page load rather than
        # being silent until the first death. Fires as an async task so
        # it doesn't block the game loop.
        try:
            from game import leaderboard as _lb
            asyncio.create_task(_probe_leaderboard(_lb))
        except Exception:
            pass
    await App().async_run()


async def _probe_leaderboard(lb_module) -> None:
    try:
        rows = await lb_module.fetch_top10()
        try:
            import js  # type: ignore
            js.console.log(
                "[skybit/py/main] startup leaderboard probe → ",
                len(rows), " rows; last_fetch_error=",
                lb_module.last_fetch_error() or "(none)",
            )
        except Exception:
            pass
    except Exception:
        pass


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
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        try:
            await _show_error(tb)
        except Exception:
            # If even the error screen fails, at least stdout has the trace.
            print("(also failed to render the error screen)", file=sys.stderr)


asyncio.run(main())

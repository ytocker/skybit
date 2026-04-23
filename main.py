"""Skybit entry point — runs natively and as a pygbag/WASM browser bundle."""
import asyncio
import sys
import traceback


async def main():
    try:
        from game.scenes import App
        app = App()
        await app.async_run()
    except Exception:
        # In pygbag the browser canvas would just stay gray on a silent
        # exception. Dump the traceback to stdout so it shows up in the
        # browser devtools console, then idle so the user can read it.
        print("=" * 60, flush=True)
        print("Skybit crashed during startup / main loop:", flush=True)
        traceback.print_exc()
        print("=" * 60, flush=True)
        sys.stdout.flush()
        while True:
            await asyncio.sleep(1)


asyncio.run(main())

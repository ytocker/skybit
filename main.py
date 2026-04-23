"""Skybit entry point — runs natively and as a pygbag/WASM browser bundle."""
import asyncio

from game.scenes import App


async def main():
    await App().async_run()


asyncio.run(main())

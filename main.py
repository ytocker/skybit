"""Skybit entry point. Uses asyncio so pygbag can export to WebAssembly."""
import asyncio

from game.scenes import App


async def main():
    await App().run()


asyncio.run(main())

"""Render the new intro cinematic to an MP4 file for review.

Drives `game.intro.IntroScene` headlessly at fixed dt = 1/60 s for the
full DURATION + a 0.3 s tail, captures every frame as RGB, and writes
the result to `docs/intro_preview/intro_v2.mp4` via imageio's bundled
ffmpeg. Falls back to an animated GIF if ffmpeg encoding fails.

Run from repo root:
    python3 tools/render_intro_video.py
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys

import pygame
pygame.init()
pygame.display.set_mode((360, 640))   # IntroScene needs a real-ish display

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H
from game.intro import IntroScene, DURATION


FPS = 60
TAIL_SECONDS = 0.3   # extra frames after DURATION so the last beat's
                     # final pose is visible before the clip ends

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "intro_preview")
os.makedirs(OUT_DIR, exist_ok=True)
MP4_PATH = os.path.join(OUT_DIR, "intro_v2.mp4")
GIF_PATH = os.path.join(OUT_DIR, "intro_v2.gif")


def _capture_frames():
    scene = IntroScene()
    surf = pygame.Surface((W, H))
    total_frames = int((DURATION + TAIL_SECONDS) * FPS)
    frames = []
    for i in range(total_frames):
        scene.update(1 / FPS)
        scene.render(surf)
        # pygame surfaces are width-major; convert to (H, W, 3) RGB.
        rgb = pygame.surfarray.pixels3d(surf).copy()
        # surfarray returns (W, H, 3); transpose for imageio.
        rgb = rgb.swapaxes(0, 1)
        frames.append(rgb)
        if (i + 1) % 60 == 0:
            print(f"  captured {i + 1}/{total_frames} frames "
                  f"(t={(i + 1) / FPS:.2f}s)")
    return frames


def _save_mp4(frames):
    import imageio.v2 as imageio
    writer = imageio.get_writer(
        MP4_PATH, fps=FPS, codec="libx264",
        quality=8, macro_block_size=1,
    )
    try:
        for f in frames:
            writer.append_data(f)
    finally:
        writer.close()
    print(f"  wrote {MP4_PATH}  ({os.path.getsize(MP4_PATH) / 1024:.1f} KiB)")


def _save_gif(frames):
    import imageio.v2 as imageio
    # Pick every other frame to keep the GIF size reasonable while still
    # reading as smooth motion (~30 fps GIF).
    decimated = frames[::2]
    imageio.mimsave(GIF_PATH, decimated, fps=FPS // 2, loop=0)
    print(f"  wrote {GIF_PATH}  ({os.path.getsize(GIF_PATH) / 1024:.1f} KiB)")


def main():
    print(f"Rendering intro at {FPS} fps for "
          f"{DURATION + TAIL_SECONDS:.1f}s "
          f"({int((DURATION + TAIL_SECONDS) * FPS)} frames)…")
    frames = _capture_frames()
    print(f"Captured {len(frames)} frames. Encoding…")

    try:
        _save_mp4(frames)
    except Exception as exc:
        print(f"  MP4 encode failed ({exc!r}); falling back to GIF.")
        _save_gif(frames)

    pygame.quit()
    print("Done.")


if __name__ == "__main__":
    main()

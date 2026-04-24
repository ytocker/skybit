"""Simulate many rounds of pipe spawning and tally which variants actually get used.
If the dispatch works, all 8 should appear roughly 12.5% of the time."""
import os, sys, pathlib, random, time, collections
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from game.entities import Pipe

# Case 1: fresh random (time-seeded) across many pipes
random.seed()
tally = collections.Counter()
for _ in range(2000):
    p = Pipe(100, 320, 170)
    tally[p.seed % 8] += 1
print("time-seeded random.randint (2000 pipes):", dict(sorted(tally.items())))

# Case 2: seeded for reproducibility
random.seed(1)
tally = collections.Counter()
for _ in range(2000):
    p = Pipe(100, 320, 170)
    tally[p.seed % 8] += 1
print("seeded(1) random.randint (2000 pipes):   ", dict(sorted(tally.items())))

# Case 3: what the actual game sees — each pipe's seed mod 8
# If the global random has poor distribution (unlikely but possible), or if
# something else resets random between pipes, we'd see a skewed tally here.
random.seed()
variants_seen = [Pipe(100, 320, 170).seed % 8 for _ in range(8)]
print("first 8 pipes (time-seeded):            ", variants_seen)

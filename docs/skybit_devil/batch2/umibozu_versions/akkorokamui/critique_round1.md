# Akkorokamui — sunset-red kraken-deity — ROUND 1 critique

VERDICT: ITERATE

Strong, charming, on-thesis first pass. The one-eyed sea-god hook lands hard,
the house style is faithful, and the cross-set lanes are clean. It does NOT
ship as-is because of one decisive low-res failure (the arm-bloom is so
symmetric/even it reads as a thrown starfish, not an octopus deity) plus a
night-legibility deficit and a too-pretty pillar cap. All fixable in one round.

---

## Ranking of issues (most important fix first)

### 1. RULE ON THE 32px ARM-FUSE — it is NOT acceptable as drawn, but the fix is NOT thinning to 7 arms.
The GD framed the choice as "accept the fused warm bloom" vs "thin to ~7 fatter
arms for a countable read." Both miss the real problem. At true 32px nobody will
ever count arms on ANY radial creature — that was never the bar, and the brief
never asked for a countable arm-count (it asks the read to be "octopus deity").
The actual defect is that the big-scale hero arranges the nine arms in a near-
even, near-radially-symmetric pinwheel of equal-length, equal-curl rays. That
even ring is exactly what makes the grayscale chip read as a STARFISH / flung
splat, and it flirts with Tzitzimitl's rigid star-corona — the one read the
RE-SPEC explicitly pins away from. Do NOT reduce arm count. Keep 8-9 arms.
FIX it with ASYMMETRY and DEPTH instead:
- Vary arm length and curl per the brief's own word "asymmetric" — right now
  curl direction and length are too uniform. Make 2-3 arms long and trailing,
  2-3 mid, the rest short stubs reading as behind the head.
- Push 3-4 arms clearly BEHIND the mantle (darker wine-oxblood shade value,
  partly occluded) so the silhouette is a head-forward octopus, not a flat
  pinwheel. Octopus deity = head-dominant mass with arms cascading DOWN and
  FORWARD, not arms radiating evenly at 12/3/6/9 o'clock like a compass.
- This single change (uneven, depth-layered curl) is what converts the gray
  chip from "starfish" to "octopus" — far more than arm count ever would.

### 2. NIGHT LEGIBILITY — the body value is too close to the night sky; the gold eye is doing 100% of the work.
On the night chip the sunset-vermilion mass sinks toward the deep-red/indigo
night field and the form goes muddy; only the gold cyclops eye survives. That's
fragile — if the eye is ever occluded or small, the creature vanishes. The
brief's accessibility spirit (don't let one pip carry the read) is violated at
night.
- Lift the top-left rim-sheen `(238,150,120)` warm-coral so there's a brighter
  value edge wrapping the mantle crown and the leading arms — give the
  silhouette a luminous top rim that survives on a dark field.
- Make the 1px grown outline slightly warmer/lighter on the night variant so the
  whole shape pops off the dark-red sky as a value, not just as a hue.
- Target ~15-20% more top-rim value contrast on the mantle so the head reads as
  a domed mass even with the eye covered.

### 3. PILLAR CAP is too ornate / loses the "curled arm-TIP" read and is mildly top-heavy.
The arm-column shaft with banded cream sucker-dots is excellent — clean,
on-axis, obviously repeatable, clearly "tentacle." But the gap-cap coil reads as
a fat cinnamon-roll spiral with a bright gold blob, not as a tapering arm TIP
curling in. At a glance the cap looks like a separate object stuck on the shaft
rather than the same arm finishing in a coil.
- Taper the cap: the coil should visibly NARROW as it curls (arm-tip), so mass
  drops toward the gap line and it never reads top-heavy.
- The gold glow-sucker at the cap is currently a big solid disc that competes
  with the hero's eye as a second focal — shrink it to a single clear glow-pip
  and let it RADIATE into the gap rather than sit as a flat coin.
- Confirm the cap silhouette still reads as "tentacle tip," not "snail shell."

### 4. EYE / FACE — strong, but the cyclops eye is slightly over-rendered for chibi.
The single gold cyclops eye + ink beak is a great, memorable, scary-CUTE focal
and the right call. One nit: the eye's inner shading has a faceted/airbrushed
quality that's a touch realistic for the flat triad. Keep it FLAT — dark-core
pupil, flat gold iris, one top-left sheen dot. Resist gradient banding inside
the iris.

---

## KEEP (working — do not lose these)
- One-eyed benevolent-but-deadly sea-god hook: instantly likable, clearly EPIC,
  clearly a CHARACTER. This is the win.
- House-style fidelity: chibi mantle, flat triad, ink keyline, 1px outline all
  present and correct. Elevated, not grim.
- CROSS-SET lanes are clean: sunset-vermilion owns the sole RED lane; divine-gold
  eye is the focal; reads nothing like the source Umibozu jelly-dome, nothing
  like Tzitzimitl's bone corona, nothing like Raijin's drum-ring. No twinning
  with chochin-anko's coral-BELLY (this is full-body red, correctly).
- Pillar SHAFT: banded sucker-dot tentacle column is a clean, bottom-rooted,
  obviously-repeatable body-as-pillar. Mirror discipline is good.
- Sucker-dots on the hero arms read as cute charm at big scale without becoming
  noise — good restraint.

## FIX (summary punch-list)
1. Re-pose the hero arms ASYMMETRIC + depth-layered (vary length/curl, push 3-4
   behind the head) so the gray chip reads "octopus deity," not "starfish."
   Keep 8-9 arms — do NOT thin to 7.
2. Lift mantle top-rim sheen + warm/lighten the night outline ~15-20% so the
   form survives on the dark-red night sky without relying on the eye alone.
3. Taper the pillar coil-cap to a true narrowing arm-TIP; shrink the gold
   glow-sucker to a single radiating pip so it doesn't rival the hero eye.
4. Keep the cyclops iris FLAT (dark-core / flat gold / one sheen dot) — kill the
   faceted internal shading.

## References
- Octopus silhouette logic: head-dominant mass, arms cascading down/forward and
  layered front-to-back (not even radial) — the standard mobile-readable octopus
  read (e.g. casual match-3 sea bosses). Asymmetry is what sells "live creature"
  over "symmetrical icon."

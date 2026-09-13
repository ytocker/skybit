# Wandjina — white-clay radial rain-ancestor — ROUND 1 critique

VERDICT: ITERATE

Strong, characterful first round. The KIND is unmistakable, the flat-graphic
house style is honoured, the inverted-value (pipeclay-light dominant) read is
locked, and the true-32 + grayscale tell genuinely survive. Two real problems
keep it off ship: (1) at true 32px the eyes blow out into two solid black
sockets and the face loses its scary-CUTE personality — it skews toward a
generic skull/owl; and (2) the halo starburst, while crisp, is heavier and
busier than it needs to be, eating into the white-disk focal area at small
scale. Both are fixable in one round.

---

## Ranking — strongest / weakest

**Strongest aspect: KIND clarity + value inversion.** The radial-halo-face
silhouette is the cleanest, most instantly-legible KIND in this brood. The
pipeclay-white disk reads as the LIGHT dominant against the charcoal keyline
and brick-ochre rays exactly as briefed — it correctly inverts the source
Mokoi's charcoal-dominant ground, and it does NOT read as a Raijin drum-ring
or a soft glow. The grayscale tell holds: white disk + dark eyes + spiked
silhouette survives full desaturation. This is a memorable character.

**Weakest aspect: the 32px eye read.** At true 32px (and even in the 64px
audit) the two eyes collapse to flat black ovals with no iris/ring structure,
killing the calm-stare personality and pushing the silhouette toward
"skull/owl emoji." The hero eyes (concentric charcoal ring + ochre iris + dark
pupil) are lovely; almost none of that ring structure survives the downscale,
so the elevated, watchful character is a big-scale-only luxury right now.

---

## Per-aspect KEEP / FIX

### 1. FLAT-GRAPHIC fidelity — PASS (keep)
- KEEP: Saturated flat fills, hard charcoal keyline + 1px outline, zero 3D
  triad. Detail is carried by PATTERN DENSITY (pipeclay rain-dot rows on the
  brow/cheeks, red-ochre ray-hatch on the board) exactly as the lineage
  demands. Nothing here is fighting the medium.
- KEEP: pipeclay-white (232,226,212) is decisively the light dominant; the
  inversion off the source ground is the correct, distinct move.
- Minor FIX: the soft yellow-ochre dot-field on the face is a touch low in
  contrast against the pipeclay white at big scale and vanishes entirely by
  32px. Either accept it as hero-only seasoning or nudge the dot value/size up
  ~one step so a hint of the dot-row survives to 64px (see directive 5).

### 2. Memorable character + true-32 legibility — PARTIAL (fix)
- KEEP: At 32px the haloed-white-face-disk + dark-eye + red-starburst read DOES
  hold as the GD reported — the grayscale tell confirms a clean hue-blind read.
- FIX (top priority): the eyes go solid black with no internal structure, so
  the personality flattens to a generic skull/owl. The calm mouthless stare is
  the whole character — it must not read as empty sockets. Carry at least a
  one-pixel pipeclay catch-ring or a single pipeclay highlight pip inside each
  eye down to 32px so the eye reads as a watching EYE, not a hole.
- FIX: the eyes are slightly too large and too close-set at small scale,
  reinforcing the skull read. Shrinking them ~10-15% and adding a hair more
  inter-ocular gap will recover the "face" read and leave room for the
  catch-ring.

### 3. Head-dominant read at 32px — RULING: ACCEPTABLE
- The GD flagged that at true 32px the rain-board pillar-stub nearly vanishes
  under the dominant halo+face, so the icon reads almost purely as the haloed
  face-disk. That is the correct and intended read for the boss icon — a
  radial-halo KIND should resolve to its halo+face at gameplay scale; the
  pillar-stub doing the heavy lifting at 32px would actually be wrong. The
  pillar-tell still reads at pillar scale (confirmed in panel b), which is
  where it needs to. No change required. Keep the head dominant.

### 4. Halo = crisp graphic STARBURST — PASS, but TRIM
- CONFIRM: this is a hard-edged graphic starburst with alternating long/short
  ray-tips, NOT a soft glow-ring and NOT a Raijin drum-ring. Brief satisfied.
- FIX: the ray COUNT is too high and the rays too uniform in width, so at 32px
  the halo reads as a slightly fuzzy spiky blob rather than a crisp burst, and
  it crowds the white disk. Drop the ray count ~20-25% and exaggerate the
  long/short alternation (make the long tips clearly longer and the short tips
  clearly stubbier). A bolder, lower-count burst will read MORE graphic and
  MORE legible small, and will give the white disk more breathing room as the
  focal anchor.
- Minor FIX: a couple of ray-tips clip into the board-stub junction and muddy
  the neck transition (visible in the hero and pillar-cap). Clean that seam so
  the disk sits cleanly on the board.

### 5. Pillar (rain-streak board shaft) — PASS (keep)
- KEEP: clean on-axis mirror, bottom-rooted, one pipeclay rain-dot column band
  + one red-ochre ray-hatch band per repeat — reads as rain on a painted
  board, distinct from the source Mokoi's dot/cross-hatch bark strip and from
  the rest of the roster.
- KEEP: ember stays cap-confined at the disk rim.
- Minor FIX: the rain-dot columns are a regular grid; nudging them into a
  slightly looser/offset "falling rain" rhythm (or a faint diagonal lean) would
  sell the rain read harder and further separate it from a plain dot-band. Nice
  -to-have, not blocking.

### 6. Feasibility — PASS
- Everything here is flat fills + polygons + dot/hatch loops + a starburst ray
  loop. Fully procedural, no sprite-sheet thinking. SS=5-6 -> smoothscale is
  appropriate.

### 7. Accessibility — PASS
- Grayscale tell confirms the read does not rely on the red/ochre hue. White
  disk vs dark eyes vs dark rays gives strong value separation. Good.

### 8. Polish — close
- Big-scale finish is high. The only polish gaps are the small-scale eye
  blowout and the halo busyness above. Edge quality and glow restraint (ember
  cap-rim only) are good.

---

## Iteration directives (prioritized punch list)

1. Fix the 32px eye blowout. Carry a 1px pipeclay catch-ring or a single
   pipeclay highlight pip inside each eye all the way down to true 32px so the
   eyes read as watching eyes, not empty sockets. This is the #1 thing keeping
   the character from shipping — right now it skews skull/owl at gameplay scale.
2. Shrink + space the eyes ~10-15%. Slightly smaller, slightly wider-set eyes
   recover the "face" over "skull" read and make room for the catch-ring.
3. Trim the halo. Cut ray count ~20-25% and exaggerate the long/short
   alternation for a bolder, crisper burst that reads more graphic at 32px and
   gives the white disk more focal breathing room. Confirm it never softens
   toward a glow/drum-ring.
4. Clean the disk<->board seam where a few ray-tips clip the neck junction.
5. (Nice-to-have) Nudge the face dot-field up ~one value/size step so a hint of
   the rain-dot rows survives to 64px; loosen the pillar rain-dot rhythm into a
   less-gridded "falling rain" cadence.

Keep everything else — the KIND, the value inversion, the head-dominant 32px
read, the starburst-not-glow halo, the bottom-rooted mirrored board, and the
cap-confined ember are all correct.

## References
- Source Mokoi for separation check: docs/skybit_devil/batch2/leyak_epic/mokoi/round_2.png
- Eye-structure-survives-downscale benchmark: Rayman Adventures / Angry Birds
  boss icons keep a single catch-light so eyes stay alive at thumbnail size.

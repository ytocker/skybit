# Skybit — Intro Animation Brief

**For:** Graphic designer / motion artist
**Project:** Skybit (casual flappy-style mobile/desktop arcade game)
**Asset:** Short pre-game intro animation introducing the protagonist, *Pip the Punctual*
**Status:** Brief v1 — open to creative interpretation

---

## 1. The 30-second elevator pitch

Skybit is a polished, casual sky-flying arcade game. Players tap to flap a
goggles-wearing scarlet macaw between sandstone cloud-pillars, scooping
golden coins through a continuous day-and-night cycle.

The game's narrative is a goofy delivery-courier sitcom (full bible in
`docs/story.md`):

> **Pip** is the only courier at *Skybit Express*, a sky-mail service that
> delivers parcels between cloud-temples nobody else can reach. His boss,
> **Mr. Garrick** — a perpetually-disappointed pelican — squawks endless
> orders into Pip's earpiece. The day-night cycle is one impossibly long
> shift. Coins are tips. Pillars are mailboxes.

**Tone:** warm, gently absurd, zero peril. Iago energy meets a workplace
sitcom. Pip *loves* this job. He just wishes Mr. Garrick would stop
talking.

---

## 2. What this intro must do

In order of priority:

1. **Hook the player in under three seconds** so the skip impulse never lands.
2. **Introduce Pip's name and personality** — daredevil-cheerful, goggles
   too big, slightly underslept, very employed.
3. **Establish the world** — sky, pillars, a parcel, a tip jar. The player
   should understand "I deliver mail through these pillars" without a single
   line of expository text.
4. **End on the Skybit logo + a tap-to-start prompt** so the cut into
   gameplay is seamless.

**Non-goals:** worldbuilding, lore dumps, character backstory, villains,
stakes. The intro is a smile, not a saga.

---

## 3. Specs & deliverables

| Spec | Value |
|---|---|
| Duration | **10–14 seconds** (target 12s) |
| Frame rate | 30 fps (60 fps if vector workflow allows) |
| Primary aspect | **9:16 portrait, 1080×1920** (mobile-first) |
| Secondary aspect | 16:9 landscape, 1920×1080 (desktop fallback) |
| File format | MP4 (H.264, AAC audio), plus a silent fallback (no audio track) |
| Color space | sRGB |
| Audio | Stereo, target -14 LUFS, embedded; also deliver a stem-free silent cut |
| Loop-friendliness | Final frame should hold cleanly on the Skybit title card |
| Skippability | Single tap/click anywhere skips to title card; designer does not implement, but motion should feel okay if cut at any point |
| Accessibility | No essential information conveyed by audio alone; reduced-motion alt cut if practical |

**Final delivery package:**
1. `skybit_intro_portrait.mp4` (primary, with audio)
2. `skybit_intro_landscape.mp4` (secondary, with audio)
3. `skybit_intro_silent.mp4` (no audio track, portrait)
4. Source project file (After Effects, Rive, Lottie, or equivalent)
5. Title card as a single PNG (transparent BG, 2048×2048) for static fallback

---

## 4. Art direction

The in-game art is **smooth procedural 2D**: flat-shaded silhouettes with
soft gradients, anti-aliased edges, gentle glows, painterly skies. **Not
pixel art. Not 3D. Not photoreal.** The intro must feel like the same world
the game opens into.

### Palette (matches in-game)
- Sky: cyan day → amber golden hour → rose sunset → indigo dusk → black-night → violet predawn → warm pink sunrise
- Pillars: warm sandstone tans, weathered with small foliage caps and prayer-flag color pops (red / saffron / teal)
- Pip: vivid scarlet red body, blue and green wing flashes, gold goggle frames with dark lenses
- Coins: bright gold with a soft glow
- Mr. Garrick: pale-pink pelican, white shirt collar, perpetual-frown beak

### Motion feel
- Snappy, springy, slightly cartoony — squash-and-stretch on Pip, anticipation poses, big takeoff burst.
- **No** stiff corporate-explainer easing. **No** hyper-realistic physics.
- Camera is allowed to move — quick whip-pans between beats are encouraged.
- One graceful slow moment in the middle (the "biomes flicker past" beat) to let the world breathe.

### Visual references
The designer is encouraged to ride the line between:
- *Alto's Odyssey* / *Monument Valley* — minimal, painterly, atmospheric
- *Kiki's Delivery Service* takeoff sequence — workplace-cute, joyful flight
- *Up* — opening (warm, wordless, fast, emotionally clear)
- *A Short Hike* / *Frog Detective* — flat-shaded indie cuteness
- *Wallace & Gromit* — workplace comedy timing without dialogue
- Modern mobile-game intros (*Crossy Road*, *Alto's*, *Sky: Children of the Light*)

---

## 5. The 12-second story

**Beat 1 — "Clock in" (0.0s → 2.0s)**
Open on a single weathered sky-pillar at dawn. A canvas mailbag and a glowing
golden parcel sit on the ledge. Crackle of a radio earpiece. **Pip** flies
in, lands, and pulls oversized aviator goggles down over his eyes — the
goggles slip, he nudges them up with one wing. He grins.

**Beat 2 — "The boss" (2.0s → 3.5s)**
Quick cut: **Mr. Garrick**, side profile, holding a clipboard, beak to
microphone. A speech bubble or stylized soundwave shows him squawking. On
his side: a stack of parcels grows from three to thirty in a single bounce.
Pip's eyes widen.

**Beat 3 — "Takeoff" (3.5s → 5.0s)**
Pip grabs the parcel, springs off the pillar with an exaggerated
anticipation-crouch, leaves a single feather behind. The camera whip-pans
upward and follows him as he punches through a cloud.

**Beat 4 — "The route" (5.0s → 9.0s)**
A continuous flight montage: Pip threads two pillars (day), banks past a
prayer-flag monastery (golden hour), dives through rose-stone ruins
(sunset), zips past a lantern (night), bursts into pink sunrise. Coins
streak past and into a small magnetized tip jar on his belt. The biomes
crossfade smoothly. This is the longest beat — let the world sell itself.

**Beat 5 — "Delivery" (9.0s → 10.5s)**
Pip slam-dunks the parcel into a pillar-top mailbox. A satisfied sky-creature
(designer's choice — moth, owl, flamingo) waves a wing. A single coin pings
into the tip jar with a *clink* that fills the frame in gold light.

**Beat 6 — "Title card" (10.5s → 12.0s)**
The gold flash transitions into the Skybit logotype, hand-drawn with a
slight tilt. Below: a small subtitle *"A Pip the Punctual Adventure."*
Below that, a pulsing prompt: **TAP TO FLY**.

A final beat: Pip's earpiece crackles in the background — *"Pip. Pip.
Are you flying. You should be flying."* — Pip rolls his eyes at the camera
and the loop holds.

---

## 6. Audio direction

- **No dialogue track in the primary cut.** Pip never speaks. Garrick may have
  one muffled, indecipherable squawk through earpiece static — comedic, not
  intelligible.
- Music: a 12-second cue, ukulele or acoustic-guitar driven, light percussion,
  one cheeky brass stab on the parcel-stack reveal. Tempo lifts at takeoff,
  resolves on the title card.
- SFX: feather flutter, takeoff *whoosh*, coin *ting*, parcel *thunk*, gentle
  earpiece crackle.
- The silent cut must work on muted phones — all story beats must read
  visually.

---

## 7. Typography & logo

- **Skybit** wordmark: rounded, slightly hand-drawn sans, with a subtle wing
  or feather flourish on the *S* or *t*. Color: deep sky-blue with a gold
  inner-stroke highlight.
- Subtitle font: same family, lighter weight, ~40% the size of the wordmark.
- Tap prompt: same family, all caps, gentle alpha pulse (0.4 → 1.0 over
  ~1.2s, looping).
- Designer is welcome to propose alternate logo treatments; final logo
  selection is a separate approval gate (see §10).

---

## 8. UX integration notes (for context)

- The intro plays once on first launch, then is reachable from the menu's
  "About" / settings. It does **not** play on every launch.
- A skip affordance ("SKIP") fades in at 1.5s, top-right, 60% alpha. Tap
  anywhere else also skips. Designer doesn't build the skip UI, but should
  be aware the top-right corner of the portrait cut should remain visually
  uncluttered.
- The intro hands off cleanly to the menu screen, which already pulses
  *"TAP · SPACE · CLICK / to flap and start"* — the intro's *"TAP TO FLY"*
  should match that prompt's rhythm.

---

## 9. What NOT to do

- No on-screen narration, voice-over, or text crawl explaining the premise.
  The premise is *felt*, not *told*.
- No villains, danger, or peril. Pip is never in trouble — he is at *work*.
- No realistic feathers, photoreal sky, or 3D shading.
- No pixel art or retro CRT effects.
- No emoji, internet jokes, or topical references that will date the
  animation.
- No watermarks, logos, or studio branding other than the Skybit logotype.
- Do not deviate from the scarlet-macaw design or remove the aviator goggles
  — both are gameplay-recognizable.

---

## 10. Timeline & approval gates

Suggested cadence (designer to confirm/adjust):

| Gate | Deliverable | Window |
|---|---|---|
| G1 | Style frames (3 stills: takeoff, mid-route, title card) | Day 3 |
| G2 | Animatic / rough boards with timing | Day 7 |
| G3 | First animation pass (silent) | Day 12 |
| G4 | Audio-locked draft | Day 16 |
| G5 | Final delivery package (all formats) | Day 20 |

Each gate is a single round of feedback. Major direction changes after G2
will reset the schedule.

---

## 11. Reference materials shipped with this brief

- `docs/story.md` — full Skybit story bible (cast, tone, sample dialogue,
  region roster). Read this before storyboarding.
- `docs/screenshots/` — four in-game screenshots showing the four primary
  biome phases. Match this color language.
- `README.md` — game mechanics overview (for context on what happens
  *after* the intro).

---

## 12. Single-line creative brief

If everything else in this document evaporates, the designer should still
be able to deliver from this one sentence:

> *Twelve seconds of a goggles-wearing scarlet macaw clocking in at the
> world's most overworked sky-mail service, set to a ukulele cue, ending
> on a logo and a tap-to-fly prompt.*

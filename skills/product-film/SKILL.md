---
name: product-film
description: Make short promo, teaser and launch films of a software product from its real UI. The film is one HTML page on one clock, rendered frame-exact to 60fps MP4 with headless Chrome. Then splice in clips or GIFs (meme remixes with a caption), land a music track's drop on a picture cue, and master the loudness. Use when asked to make a product teaser / promo / launch / demo video, turn an HTML or CSS animation into an MP4, put music under a cut so the drop hits a moment, or remix a GIF or clip with an end card.
---

# product-film

Short films (10–40 s) of a real software product, made the way a front-end engineer would make them: the film is a
web page. Every motion is an animation scheduled on one clock, so a renderer can seek the page to any frame and
screenshot it. That buys three things a generated video can't:

- **The real product.** Port the product's own components, CSS and keyframes into the page. A video model would
  invent a different UI, logo or mascot.
- **Frame-exact timing.** Every cue (a reveal, a send, the end card) is a known time, so cuts and music land on it.
- **Cheap revisions.** A wording change is an edit and a re-render, not a re-shoot.

## Setup (once)

- `npm install --prefix <this skill's directory>/scripts` installs puppeteer-core, which drives your installed
  Chrome. Set `CHROME_PATH` if Chrome isn't in a standard place.
- `ffmpeg` (with the `ebur128` filter), Python 3.8+ with `numpy`.
- Fonts from Google Fonts load at render time, so rendering needs a network connection.

## Workflow

1. **Brief.** Write down what a viewer must understand **with the sound off**, the one action you want, and the
   claims. Every claim on screen must be true today. On-screen people and data are a test persona, never a real
   user. Pick the length and aspect (1920×1080, or 1080×1920 for vertical).
2. **Build the film.** Copy `templates/film.html`, a working 8.7 s film: a line, a product card that types and
   sends, an end card. Replace its scenes with the product's real components. **Read
   `references/one-clock.md` before writing motion**: its rules are what make every frame reproducible.
3. **Look before rendering the whole film.** Run `node scripts/render.js film.html stills 1.2,4.5,8` and lay the
   stills side by side (`ffmpeg … xstack`). Fix what's wrong, then render `video`, then `timeline`, which writes
   the page's cue times for the steps below.
4. **Splice (optional).** Use `scripts/splice.py` to join a clip, a GIF or a screen recording with the rendered
   film, frame-exact, with a caption PNG over any segment. Make captions from `templates/caption.html`. For
   remixing a popular GIF or clip, read `references/remix.md`. To get clips from X, use the `x-media-download` skill.
5. **Music.** Generate several takes (`scripts/music_openrouter.py`; describe the *shape*, not timestamps). List
   drop candidates with `scripts/drops.py`, choose one by reading the curve and listening, then run
   `scripts/align_mix.py --drop <take time> --cue <cut time>`. Read `references/music.md` first.
6. **Verify by measurement, then by ear.** See the checklist below. You can't hear the result, so never claim it
   "sounds right". Report the numbers, and say that a person needs to listen before it's posted.
7. **Deliver.** The cut with music, the silent cut (for re-scoring), the page source, `timeline.json`, and the
   music stem. Report what was measured, and that the listening is still owed.

## Commands

| Script | Does |
|---|---|
| `node scripts/render.js page.html stills 1.2,4.5` | Frames at those times → `stills/t_<s>.png` next to the page |
| `node scripts/render.js page.html video out.mp4` | The whole film at 60 fps (needs `window.DURATION`); 5–10 frames rendered per second on a laptop, depending on the page |
| `node scripts/render.js page.html timeline` | `window.TIMELINE` + `DURATION` → `timeline.json` |
| `node scripts/render.js caption.html png cap.png --query "text=Line one%0Aline two"` | One transparent frame (captions, overlays) |
| `python3 scripts/splice.py -o cut.mp4 clip.mp4::11.5:cap.png film.mp4:5.0` | Segments `path[:in[:out[:overlay]]]` joined frame-exact; writes `cut.timeline.json` (each segment's `at` and `in`) |
| `python3 scripts/drops.py takes/*.mp3 --curve` | Drop candidates per take, best take first, plus each take's loudness curve |
| `python3 scripts/align_mix.py cut.mp4 take.mp3 --drop 7.62 --cue 12.1 -o final.mp4` | Places the take so its drop lands on the cue, lifts the build, fades, masters to −14 LUFS, muxes |
| `python3 scripts/music_openrouter.py --prompt-file p.txt --seed 7 -o takes/s7` | One generated take (OpenRouter, default Lyria 3 Clip; billed per call, the cost is printed) |

Common options: `render.js --size 1080x1920` for vertical (the templates are 16:9: change their `html,body`
size from 960×540 to 540×960 first), `--query "line=…"` (pass copy into the page, e.g. to draft
end-card lines without editing it), `--fps`. Mapping a cue through a splice: a source time `s` in a segment is at
`at + (s - in)` in the cut.

## Checks before calling it done

- The frame count equals duration × fps (`ffprobe -show_entries stream=nb_frames`).
- Look at a still on both sides of every cut, and at every cue (pop, send, end card). No half-loaded fonts, no
  overlapping text, no element left on screen from the previous scene.
- Loudness is −14 LUFS ±0.5, with a true peak at or under −1 dBTP (`align_mix.py` prints both).
- The level strip `align_mix.py` prints jumps at the `|`, which is the cue. If it doesn't, `--drop` is wrong.
- Every claim is still true, and a viewer with the sound off can say what the product does and what to do next.
- A person listens before it's posted.

For creative review (is it good, not just correct), have a fresh reviewer judge the render, never the builder.
That rule and the sound-off test come from [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit),
which has a full critic loop and prompts for it.

## Rules

1. **True today.** No invented results, users, ratings or features. Fictional data is a labelled persona.
2. **Real, not generated.** Port the product's components. Use generated footage only where it is labelled as such.
3. **One clock.** Nothing in the page moves on its own: no `requestAnimationFrame` loops, timers, `Date.now()` or
   unseeded randomness (`references/one-clock.md`).
4. **Measure, then listen.** Numbers first, then a human ear. Never claim an audio quality you didn't measure.
5. **Clips you don't own are for organic posts only.** Never run them in paid ads.

# One clock

The film is a page whose every visible change is an animation scheduled on one timeline. `render.js` pauses all
of the document's animations and sets each one's `currentTime` to the frame's time, waits two animation frames,
and screenshots. Anything that changes the page some *other* way (a timer, a loop, the wall clock) is invisible to
that seek. It either never shows or shows on the wrong frame.

## The page contract

| Name | Required | What |
|---|---|---|
| `window.DURATION` | for `video` | Length in seconds. Frames rendered = round(DURATION × fps) |
| `window.TIMELINE` | no | `{ CUE: seconds, … }`. `render.js timeline` writes it out, for splicing and music cues |
| `window.__setup()` | no | Runs once, after every font has loaded and before the first frame. Put layout measurement here |
| `window.seek(ms)` | no | Overrides the default seek. Use it when the page also draws something itself (a canvas): seek the animations, then `draw(ms)` |

`?query` parameters reach the page (`render.js --query "line=Try it free"`). Use them to draft copy variants
without editing the file.

## Scheduling

- **Web Animations:** `el.animate(keyframes, { delay: t * 1000, duration, fill: 'forwards', easing })`, created
  once at load. `templates/film.html` wraps it in a small kit: `A`, `on`, `off`, `rise`, `words`, `type`.
- **CSS animations work too.** Put the time in `animation-delay`. A clean way is to set the cue times as CSS
  variables from the script (`--te: 11.3s`) and write `animation-delay: calc(var(--te) + .4s)`. `getAnimations()`
  returns CSS animations as well, so the same seek moves them.
- Iterating animations (a blinking caret, a pulsing dot) are fine. Give them a delay and an iteration count, and
  the seek lands mid-iteration correctly.
- Name the cue times once at the top of the script (`REVEAL`, `SEND`, `END`) and derive everything from them. A
  timing change is then one number, and `timeline` exports the new cues for the music.

## Gotchas

- **One property, several animations:** create them in time order with `fill: 'forwards'`, and set the starting
  value inline (`style="opacity:0"`). An animation with `fill: 'backwards'` or `'both'` applies its first keyframe
  *before it starts*, and wins over earlier animations of the same property.
- **Typing:** one span per character, each cut in on its own frame (`type()` in the template). Don't change
  `textContent` from a timer.
- **No transitions on class changes.** A CSS `transition` fires when a class flips at runtime, which the seek never
  does. Write it as an animation.
- **Layout-dependent motion** (move X to where Y is): measure in `__setup()`, after fonts load, and set CSS
  variables. You can `seek(ms)` inside setup to measure the page as it stands at a given time.
- **Fonts:** `render.js` force-loads every declared `@font-face` before setup and warns about any that failed.
  A fallback face changes text widths, and with them every measured position.
- **Video elements and rAF-driven canvases/WebGL** don't follow the seek. Splice real footage in with `splice.py`
  instead, and drive a canvas from `window.seek`.
- **Randomness** (particles, jitter): use a seeded generator, so frame N is the same on every render.

## Porting the real product

Copy the component's markup or SVG, its CSS and its `@keyframes` from the product's codebase **verbatim**, and
change only *when* things happen, by mapping each animation's delay onto the film's clock. Add a comment naming
the source file, so the film can be refreshed when the product changes. If the product animates with JavaScript
(a spring library, state machines), re-express the motion as keyframes sampled from it. Don't re-run the library
live.

## Size and speed

Author at 960×540 CSS pixels and render at `--scale 2` (the default) for 1920×1080. For vertical, size the page's
`html,body` to 540×960 (the templates hardcode 960×540) and render with `--size 1080x1920`. Rendering runs at 5–10 frames per second on a laptop, depending on the page (measured:
522 frames in 53 s, 967 frames in 110 s, a 1080×1920 phone-UI film 1260 frames in about 4 minutes), so render stills
first and the full film when the stills are right.

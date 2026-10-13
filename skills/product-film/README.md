# product-film

An agent skill for making short promo, teaser and launch films of a software product **from its real UI**, the
way a front-end engineer would: the film is one HTML page on one clock, rendered frame-exact to a 60 fps MP4 with
headless Chrome. Then:

- splice in clips, screen recordings or a popular GIF with a caption (meme remixes), frame-exact
- generate music, find the drop, and land it on the picture's big moment
- master to −14 LUFS without flattening the build-to-drop contrast

It came out of making launch films for our own product, where generated video kept inventing a different UI and
mascot. Rendering the product's own components is what fixed it.

## What's inside

```
SKILL.md                 the workflow, the commands, the checks, the rules
references/
  one-clock.md           how to write a page every frame of which is reproducible (and porting real components)
  music.md               generating takes, choosing the drop, aligning, lifting the build, mastering
  remix.md               GIF / clip remixes: caption, cut, rights
scripts/
  render.js              page → stills / 60 fps MP4 / timeline.json / transparent PNG (puppeteer-core + your Chrome)
  splice.py              frame-exact join of segments, scaled onto one canvas, with caption overlays
  drops.py               drop candidates per music take, plus loudness curves
  align_mix.py           put the take's drop on a cue, lift the build, fade, master, mux
  music_openrouter.py    one generated take via OpenRouter (Lyria 3 Clip by default)
templates/
  film.html              a working 8.7 s film to start from
  caption.html           a meme caption, rendered to a transparent PNG
  music_prompt.txt       a prompt that describes a drop's shape
```

## Install

```bash
git clone https://github.com/askdestava/claude-skills
cp -R claude-skills/skills/product-film ~/.claude/skills/
npm install --prefix ~/.claude/skills/product-film/scripts      # puppeteer-core only; it drives your installed Chrome
```

You also need `ffmpeg` (with the `ebur128` filter) and Python 3.8+ with `numpy`. `music_openrouter.py` needs an
OpenRouter key (`OPENROUTER_API_KEY`), and each generation is billed.

Then ask Claude Code for a teaser, a launch video, or "this GIF, then our product, with the drop on the reveal".

## Try it without an agent

```bash
mkdir -p ~/film-test && cp ~/.claude/skills/product-film/templates/film.html ~/film-test/
node ~/.claude/skills/product-film/scripts/render.js ~/film-test/film.html stills 1.2,4.6,8 --query "line=Start free today."
node ~/.claude/skills/product-film/scripts/render.js ~/film-test/film.html video ~/film-test/film.mp4
```

## Tested

The scripts were checked against films made by hand before they existed:

- `render.js` matches the hand-built renderer: the same frame pixel for pixel on the same Chrome, except 20 pixels
  of a cursor sized from a font that the old renderer didn't wait for and this one does.
- `splice.py` reproduces a 22.6 s GIF remix pixel for pixel (1357 frames).
- `align_mix.py` reproduces its music stem sample for sample.
- `drops.py` was run on takes whose drops were chosen by ear. Its results, including the miss, are in the script's
  docstring.

## See also

[echris6/motion-video-kit](https://github.com/echris6/motion-video-kit): an independent-critic review loop, motion
principles from 28 launch films, a quality bar and sound design for business commercials. It covers judging a film
well; this skill covers making one from the real product and landing the music.

## Licence

MIT. See [LICENSE](LICENSE).

# Music: a drop that lands on the picture

The edit rests on one moment: the picture's big beat (the product appears, the logo lands, the cut into the app)
and the music's drop hitting on the same frame. Generated music can't be told *when* to drop, so you generate,
measure, choose, and move the track.

## 1. Generate several takes

`scripts/music_openrouter.py` makes one take per call (default model: Google Lyria 3 Clip, about 30 s, billed per
call; the script prints the cost). **Lyria ignores timestamps in the prompt.** Describe the shape instead: a quiet
build, one beat of silence, a big drop, a steady end. `templates/music_prompt.txt` is a starting point.

Generate 3–6 seeds (`--seed 1`, `--seed 2`, …). Run one first to check the prompt does roughly the right thing
before paying for the rest.

## 2. Find and choose the drop

`scripts/drops.py takes/*.mp3 --curve` lists each take's top drop candidates (a step up in level and in the bass
band) and prints its loudness curve. They are candidates, not answers:

- A track can step twice: the bass enters, then the full drop comes a beat later. Which one should sit on the
  picture's beat is a musical choice.
- A riser into the drop is loud too. The drop is where the riser *ends* and the kick and bass begin.
- Read the curve around each candidate. Then listen to the top two takes from a couple of seconds before their
  candidate, or ask an audio-capable model to describe what happens at that time.

## 3. Align, lift, master

```bash
python3 scripts/align_mix.py cut.mp4 takes/s7.mp3 --drop 15.36 --cue 12.10 --in 6.5 -o cut_music.mp4 --stem music.wav
```

- **Placement** is exact: take time τ plays at cut time τ + (cue − drop). If the drop comes later in the take
  than the cue in the cut, the take's opening is trimmed; if earlier, the music starts partway into the cut.
- **`--in`** decides how much build plays. A take's own first seconds can be louder than its build (an intro
  hit), so often you want the music to come in a set time before the cue, e.g. the 5–6 s of build the picture
  has room for, not wherever the take happens to begin.
- **`--lift`** (default +10 dB) raises everything before the cue. Generated builds often sit ~25 dB under the
  drop, which is inaudible on a phone speaker. The lift ramps back to 0 dB over the 80 ms before the cue, so the
  drop keeps its full contrast.
- **Mastering** is one linear gain to −14 LUFS (the reference most platforms normalise to) and a peak limiter,
  with true peak at or under −1 dBTP. Never use dynamic loudness normalisation (`loudnorm`) here: it pushes the
  build up and the drop down, which is the opposite of the point.
- **`--fade-from`**: fade under the end card after the headline has been read, so the music doesn't cut off.

## 4. Check

- `align_mix.py` prints a level strip in 20 ms steps around the cue. It should jump at the `|`. If the jump is a
  beat early or late, `--drop` is wrong; the placement maths isn't.
- It prints integrated loudness and true peak; check them against the targets above.
- A person listens on a phone speaker and on headphones before posting. Measurement shows the drop is *where* it
  should be, not that the music suits the film.

## Sound effects

Not in this kit. Keep them sparse: one soft whoosh per real transition, a click only on a real action, all well
under the music. [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit) has a thorough guide and
scripts for SFX levels.

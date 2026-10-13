# Remixing a GIF or clip

A familiar clip, a caption that turns its joke toward your audience's situation, a hard cut to the product, and an
end card that pays off the caption. It borrows attention the clip has already earned. The product half is the
rendered film, so it stays real.

## Getting the clip

- From X: the `x-media-download` skill (`--gif` also writes a real `.gif`). It keeps a JSON record of the source
  post. Keep that record next to the remix.
- X "GIFs" are silent MP4s, often 10 fps and about 640 px wide. `splice.py` repeats frames up to 60 fps (no
  interpolation, which smears faces) and scales with lanczos. At 3× it's soft, which is acceptable for a meme.

## Writing the caption

- Cast the clip's characters as your viewer's situation. The caption names who the viewer is in the scene ("My
  manager when…", "Recruiters when…", "Me after…"). The clip's action is the punchline.
- The end card answers the caption. When the caption and the end line share a word or an idea, the joke closes
  on the product instead of just stopping.
- Keep it true. The joke can exaggerate the *situation*; the product's claim on the end card can't exaggerate
  anything.
- **Break the lines yourself** (`%0A` in the `--query`). An automatic wrap splits phrases ("could have been /
  an email").
- Render the caption over the clip's busiest frame, and its emptiest, before committing.

## The cut

- End the clip right after its punchline lands. Trim slow openings; a remix has about one second to hook.
- Cut into the film where its screen is simple (a mark on a plain background), so the hard cut reads as a turn.
- Put the music's drop on the product's first big moment, a fraction after the cut, rather than on the cut itself.
  The silence before a drop works well across the cut. `--in` lets the build play under the clip's tension.

```bash
node scripts/render.js caption.html png cap.png --query "text=Me when the standup%0Ahits minute 45"
python3 scripts/splice.py -o remix.mp4 --bg 0B0F19 clip.mp4::11.5:cap.png film.mp4:5.0
python3 scripts/align_mix.py remix.mp4 take.mp3 --drop 7.62 --cue 12.1 --in 6.5 -o remix_music.mp4
```

## Rights

The clip belongs to someone else, usually a studio. Post remixes **organically only** (X, Threads, LinkedIn,
Reels, Shorts). **Never run one as a paid ad.** Ad platforms review the rights in a creative, and a paid placement
is the clearest case of commercial use. Also check what's in the frames: weapons, violence or alcohol trip ad
policies, and some brands won't want them anywhere near their name.

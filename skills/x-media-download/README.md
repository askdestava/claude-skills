# x-media-download

An agent skill (Claude Code, and any agent that reads `SKILL.md` skills) for downloading the videos, GIFs and
photos attached to public X (Twitter) posts. Give it a post URL and it saves:

- every video and GIF as the highest-bitrate MP4 X offers (up to 1920×1080), and optionally a real `.gif`
- every photo at original size
- a JSON sidecar with the post's URL, author, text and the source URL of each file

It reads X's public embed endpoint (`cdn.syndication.twimg.com`, the one behind embedded posts), so it needs no
login, no API key and no third-party package: one Python 3.8+ standard-library script. `ffmpeg` is used only to make
`.gif` files.

## Install

From a clone of [askdestava/claude-skills](https://github.com/askdestava/claude-skills), copy the skill folder into
your skills directory:

```bash
git clone https://github.com/askdestava/claude-skills
cp -R claude-skills/skills/x-media-download ~/.claude/skills/
```

(To pick up later changes with a `git pull`, link the folder instead of copying it:
`ln -s "$PWD/claude-skills/skills/x-media-download" ~/.claude/skills/x-media-download`.)

New Claude Code sessions will list the skill. Then ask in plain words: *"download the video from
https://x.com/…/status/…"*, *"save this GIF as a real gif"*, *"grab the images in this post"*.

## Use it without an agent

```bash
python3 scripts/x_media.py https://x.com/<user>/status/<id> -o downloads/
python3 scripts/x_media.py <id> --gif            # X GIFs are MP4s; also write a .gif
python3 scripts/x_media.py <id> --quoted         # also the media of the post it quotes
python3 scripts/x_media.py <id> --list           # show what's there, download nothing
```

Files are named `<author>_<id>_<n>.<ext>`, with the sidecar at `<author>_<id>.json`.

Exit status: `0` saved; `1` unavailable (deleted, protected, withheld from embeds, or X unreachable); `3` the post
has no downloadable media. [`SKILL.md`](SKILL.md) has the details and a `yt-dlp` fallback for posts that need a
login.

## Limits

- Only posts X serves to logged-out embeds. Protected accounts, deleted posts, and posts X withholds from embeds
  (age-restricted or sensitive media) return exit `1` with X's reason.
- Spaces, live broadcasts and media inside link cards are not downloaded.
- The endpoint is undocumented. If X changes it, this breaks; the request is in one function (`fetch_post`).

## Rights

The media belongs to whoever posted it. This tool downloads only what X already serves publicly, and it does not
get around any access control. Whether you may reuse what you download is up to you and the rights holder.

## Licence

MIT. See [LICENSE](LICENSE).

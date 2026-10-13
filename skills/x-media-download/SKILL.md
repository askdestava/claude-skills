---
name: x-media-download
description: Download the videos, GIFs and photos attached to a public X (Twitter) post from its URL or id. Saves the best-quality MP4 of each video or GIF (optionally a real .gif), every photo at original size, and a JSON sidecar recording the post's author, text and source URLs. Use when the user shares an x.com or twitter.com status link and wants its media saved, e.g. "download this video from X", "save the GIF from this tweet", "grab the images in this post".
---

# x-media-download

Saves the media attached to public X posts using X's own embed endpoint (`cdn.syndication.twimg.com`, the one
behind embedded posts). No login, API key, browser or third-party package — `scripts/x_media.py` is Python 3.8+
standard library. `ffmpeg` is needed only for `--gif`.

## Run it

```bash
python3 <this skill's directory>/scripts/x_media.py <URL or id> [more ...] -o <output dir>
```

Accepts any post URL form (`x.com`, `twitter.com`, `mobile.twitter.com`, `/i/status/…`, `/i/web/status/…`,
fxtwitter/vxtwitter mirrors, with `/photo/1`, `/video/1`, `?s=…`) or a bare numeric id. Several posts in one call
are fine; each is handled independently.

| Flag | Does |
|---|---|
| `-o DIR` | Where to save (created if missing). Default: the current directory. Ask the user, or pick the folder their project keeps assets in. |
| `--gif` | Also convert X GIFs to real `.gif` files. **X serves GIFs as silent MP4s**, so without this flag a "GIF" arrives as `.mp4`. |
| `--quoted` | Also save the media of the post it quotes. |
| `--list` | Print each media item as a JSON line and download nothing. Use it to preview a large video first. |

## What you get

For each post, in the output directory:

- `<author>_<id>_<n>.mp4` — a video or GIF: the highest-bitrate MP4 X offers (up to 1920×1080 for video).
- `<author>_<id>_<n>.jpg|png` — a photo at original size (`?name=orig`).
- `<author>_<id>_<n>.gif` — with `--gif`, next to the GIF's MP4.
- `<author>_<id>.json` — the sidecar: post URL, author, `created_at`, text, and for each file its `source_url`, type,
  size and bitrate, plus `fetched_at`. Keep it with the files; it is the record of where they came from.

`n` counts from 1 in the post's order. Each saved file prints as `saved <path> (<type>, <W>x<H>)`.

## When it fails

Read the exit status, not just the output:

| Exit | Meaning | What to do |
|---|---|---|
| `0` | Every post saved | — |
| `1` | Unavailable: deleted, protected, wrong id, withheld from embeds (age-restricted / sensitive), or X unreachable. The message gives X's reason when it gives one. | If the user can see it while logged in, fall back to `yt-dlp` with their browser's cookies (below). |
| `3` | The post has no downloadable media (text only, a link card, or a poll). If the post it **quotes** has media, the message says so — re-run with `--quoted`. | — |

With several posts, every post is still attempted; the exit status is the first failure's.

**Fallback for posts the embed endpoint won't serve** (needs `yt-dlp` installed; it reads the user's logged-in
X session from their browser, so say so and ask before running it):

```bash
yt-dlp --cookies-from-browser chrome -o '%(uploader_id)s_%(id)s.%(ext)s' '<post URL>'
```

## Notes

- The endpoint takes a `token` parameter that X's embed script derives from the id; any value is accepted today.
  If every request starts failing with HTTP 400/403, that `TOKEN` constant at the top of the script is the first
  thing to check.
- Spaces (audio rooms), live broadcasts and media inside link cards are not post media and are not downloaded.
- The media belongs to whoever posted it. This tool downloads only what X serves publicly to anyone, and it does
  not get around any protection. Whether you may reuse a file — in a remix, a post or an ad — is a separate question
  that the download doesn't settle. Paid placements are the strictest case.

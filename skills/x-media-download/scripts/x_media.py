#!/usr/bin/env python3
"""Download the videos, GIFs and photos attached to public X (Twitter) posts.

Reads X's public embed endpoint (cdn.syndication.twimg.com, the one behind embedded posts), so it needs no
login, API key or third-party package. Python 3.8+ standard library only; ffmpeg only for --gif.

    x_media.py URL_OR_ID [URL_OR_ID ...] [-o DIR] [--gif] [--quoted] [--list]

For each post it saves the best MP4 of every video and GIF, every photo at original size, and a JSON
sidecar (<author>_<id>.json) recording the post's URL, author, text, and where each file came from.

Exit status: 0 = every post saved; 1 = a post is unavailable (deleted, protected, withheld) or a request
failed; 3 = a post has no downloadable media. With several posts, the first failure's code is returned.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ENDPOINT = "https://cdn.syndication.twimg.com/tweet-result"
# The endpoint requires a `token` parameter. X's embed script derives one from the id, but the endpoint
# accepts any value today. If X starts checking it, this is the one line to change.
TOKEN = "4"
USER_AGENT = "Mozilla/5.0 (compatible; x-media-download/1.0)"
TIMEOUT = 60

EXIT_UNAVAILABLE = 1
EXIT_NO_MEDIA = 3


class Unavailable(Exception):
    pass


def parse_id(value):
    """A post id from a bare id or any URL with /status/<id> (x.com, twitter.com, mobile, i/web, fx/vx mirrors)."""
    value = value.strip()
    if value.isdigit():
        return value
    url = urllib.parse.urlparse(value if "://" in value else "https://" + value)
    match = re.search(r"/status(?:es)?/(\d+)", url.path)
    if not match:
        raise ValueError(f"not an X post URL or id: {value}")
    return match.group(1)


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(request, timeout=TIMEOUT)


def fetch_post(post_id):
    query = urllib.parse.urlencode({"id": post_id, "lang": "en", "token": TOKEN})
    try:
        with get(f"{ENDPOINT}?{query}") as response:
            body = response.read()
    except urllib.error.HTTPError as e:
        if e.code in (400, 404):
            raise Unavailable(f"X has no public post {post_id} (HTTP {e.code}): deleted, protected, or a wrong id")
        raise Unavailable(f"X answered HTTP {e.code} for post {post_id}")
    except urllib.error.URLError as e:
        raise Unavailable(f"could not reach X: {e.reason}")
    if not body.strip():
        raise Unavailable(f"X returned an empty answer for post {post_id}: it is not publicly embeddable")
    post = json.loads(body)
    if post.get("__typename") == "TweetTombstone":
        reason = ((post.get("tombstone") or {}).get("text") or {}).get("text") or "no reason given"
        raise Unavailable(f"X withholds post {post_id} from embeds: {reason}")
    return post


def media_of(post):
    """The downloadable media of one post: the highest-bitrate MP4 of each video or GIF, photos at original size."""
    items = []
    for m in post.get("mediaDetails") or []:
        kind = m.get("type")
        size = m.get("original_info") or {}
        if kind in ("video", "animated_gif"):
            mp4s = [v for v in (m.get("video_info") or {}).get("variants") or [] if v.get("content_type") == "video/mp4"]
            if not mp4s:
                continue
            best = max(mp4s, key=lambda v: v.get("bitrate") or 0)
            items.append({"type": kind, "source_url": best["url"], "ext": "mp4", "bitrate": best.get("bitrate"),
                          "width": size.get("width"), "height": size.get("height")})
        elif kind == "photo" and m.get("media_url_https"):
            base = m["media_url_https"]
            ext = os.path.splitext(urllib.parse.urlparse(base).path)[1].lstrip(".") or "jpg"
            items.append({"type": "photo", "source_url": f"{base}?name=orig", "ext": ext,
                          "width": size.get("width"), "height": size.get("height")})
    return items


def download(url, path):
    part = path + ".part"
    with get(url) as response, open(part, "wb") as out:
        shutil.copyfileobj(response, out)
    os.replace(part, path)


def to_gif(mp4, gif):
    """A real .gif from X's GIF MP4: one palette for the whole clip, source frame rate and size."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-filter_complex",
                    "[0:v]split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5",
                    gif], check=True)


def save_post(post, out_dir, make_gif):
    """Download one post's media and write its sidecar. Returns the sidecar dict."""
    author = (post.get("user") or {}).get("screen_name") or "unknown"
    post_id = post["id_str"]
    stem = f"{author}_{post_id}"
    files = []
    for n, item in enumerate(media_of(post), start=1):
        path = os.path.join(out_dir, f"{stem}_{n}.{item['ext']}")
        download(item["source_url"], path)
        entry = {"file": os.path.basename(path), **{k: v for k, v in item.items() if k != "ext" and v is not None}}
        files.append(entry)
        print(f"saved {path}  ({item['type']}, {item.get('width')}x{item.get('height')})")
        if make_gif and item["type"] == "animated_gif":
            if shutil.which("ffmpeg"):
                gif = path[:-4] + ".gif"
                to_gif(path, gif)
                entry["gif"] = os.path.basename(gif)
                print(f"saved {gif}  (converted with ffmpeg)")
            else:
                print("warning: --gif needs ffmpeg on PATH; kept the MP4 only", file=sys.stderr)
    sidecar = {
        "id": post_id,
        "url": f"https://x.com/{author}/status/{post_id}",
        "author": {"screen_name": author, "name": (post.get("user") or {}).get("name")},
        "created_at": post.get("created_at"),
        "text": post.get("text"),
        "media": files,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "via": ENDPOINT,
    }
    with open(os.path.join(out_dir, f"{stem}.json"), "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return sidecar


def run(value, out_dir, make_gif, quoted, list_only):
    """One input → 0 or an exit code. Prints what it did, or why not."""
    try:
        post = fetch_post(parse_id(value))
    except (ValueError, Unavailable) as e:
        print(f"error: {e}", file=sys.stderr)
        return EXIT_UNAVAILABLE
    posts = [post]
    inner = post.get("quoted_tweet")
    if quoted and inner:
        posts.append(inner)
    if not any(media_of(p) for p in posts):
        hint = " (the post it quotes has media: add --quoted)" if inner and media_of(inner) else ""
        print(f"error: post {post['id_str']} has no downloadable media{hint}", file=sys.stderr)
        return EXIT_NO_MEDIA
    if list_only:
        for p in posts:
            for item in media_of(p):
                print(json.dumps({"post": p["id_str"], **{k: v for k, v in item.items() if k != "ext"}}))
        return 0
    os.makedirs(out_dir, exist_ok=True)
    try:
        for p in posts:
            if media_of(p):
                save_post(p, out_dir, make_gif)
    except (urllib.error.URLError, OSError, subprocess.CalledProcessError) as e:
        print(f"error: download failed for post {post['id_str']}: {e}", file=sys.stderr)
        return EXIT_UNAVAILABLE
    return 0


def main():
    parser = argparse.ArgumentParser(description="Download the videos, GIFs and photos attached to public X posts.")
    parser.add_argument("posts", nargs="+", metavar="URL_OR_ID", help="x.com / twitter.com post URL, or a post id")
    parser.add_argument("-o", "--out", default=".", help="directory to save into (default: current directory)")
    parser.add_argument("--gif", action="store_true", help="also convert X GIFs (which are MP4s) to real .gif files")
    parser.add_argument("--quoted", action="store_true", help="also save the media of the post it quotes")
    parser.add_argument("--list", action="store_true", help="print the media as JSON lines; download nothing")
    args = parser.parse_args()
    code = 0
    for value in args.posts:
        result = run(value, args.out, args.gif, args.quoted, args.list)
        code = code or result
    sys.exit(code)


if __name__ == "__main__":
    main()

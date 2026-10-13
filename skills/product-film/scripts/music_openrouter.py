#!/usr/bin/env python3
"""Generate one music take with a music model on OpenRouter (default: Google Lyria 3 Clip, ~30 s).

    music_openrouter.py --prompt-file prompt.txt --seed 11 -o takes/drop_s11 [--model google/lyria-3-clip-preview]

The API key comes from $OPENROUTER_API_KEY, or from the file named by --key-file (read here, never printed).
Writes <out>.mp3 (or .wav, as the model returns it). Each call is billed: Lyria 3 Clip was $0.04 per clip when
this was written. Generate a handful of seeds, rank them with drops.py, keep the best.

Lyria ignores timestamps in the prompt. Describe the shape instead (a quiet build, one beat of silence, a big drop)
and choose among seeds by measurement.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.request

URL = "https://openrouter.ai/api/v1/chat/completions"


def main():
    p = argparse.ArgumentParser(description="Generate one music take via OpenRouter.")
    p.add_argument("--prompt-file", required=True)
    p.add_argument("-o", "--out", required=True, help="output path without extension")
    p.add_argument("--seed", type=int)
    p.add_argument("--model", default="google/lyria-3-clip-preview")
    p.add_argument("--key-file", help="file holding the OpenRouter key (default: $OPENROUTER_API_KEY)")
    a = p.parse_args()
    key = open(os.path.expanduser(a.key_file)).read().strip() if a.key_file else os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("error: set OPENROUTER_API_KEY or pass --key-file")
    body = {"model": a.model, "messages": [{"role": "user", "content": open(a.prompt_file).read()}],
            "modalities": ["text", "audio"], "stream": True}
    if a.seed is not None:
        body["seed"] = a.seed
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    started = time.time(); chunks = []; fmt = None; usage = None; text = []
    with urllib.request.urlopen(req, timeout=300) as response:
        for line in response:
            line = line.decode().strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            event = json.loads(data)
            usage = event.get("usage") or usage
            for choice in event.get("choices", []):
                delta = choice.get("delta") or {}
                if delta.get("content"):
                    text.append(delta["content"])
                audio = delta.get("audio")
                if isinstance(audio, dict):
                    if audio.get("data"):
                        chunks.append(audio["data"])
                    fmt = audio.get("format") or fmt
    if not chunks:
        sys.exit(f"error: no audio came back ({time.time() - started:.0f}s). Model text: {''.join(text)[:300]!r}")
    ext = {"mp3": "mp3", "wav": "wav"}.get(fmt or "", "mp3")
    path = f"{a.out}.{ext}"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        f.write(base64.b64decode("".join(chunks)))
    cost = (usage or {}).get("cost")
    print(f"wrote {path} in {time.time() - started:.0f}s" + (f", cost ${cost}" if cost is not None else ""))


if __name__ == "__main__":
    main()

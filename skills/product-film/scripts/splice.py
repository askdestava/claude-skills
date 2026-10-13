#!/usr/bin/env python3
"""Join video segments into one cut, frame-exact, with one re-encode.

    splice.py -o cut.mp4 SEGMENT [SEGMENT ...] [--size 1920x1080] [--fps 60] [--bg 000000]

A SEGMENT is  path[:in[:out[:overlay.png]]]  with times in seconds; leave a field empty to use the start or end:
    meme.mp4::11.5:caption.png     the first 11.5 s of a GIF's MP4, with a transparent caption PNG over it
    film.mp4:5.0                   a rendered film from 5.0 s to its end

Each segment is converted to --fps first (a 10 fps GIF repeats frames; nothing is interpolated), scaled to fit the
canvas with lanczos and centred on --bg, then trimmed by frame number, so every cut lands on an exact frame.
Picture only: audio is dropped (lay music afterwards with align_mix.py). Paths can't contain ':' (so no Windows
drive letters): run it from the folder and use relative paths.

Writes <cut>.timeline.json: where each segment starts in the cut ("at") and which source time it starts from ("in").
A cue at source time s of a segment is at  at + (s - in)  in the cut.
"""
import argparse
import json
import os
import subprocess
import sys


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def parse_segment(spec):
    parts = spec.split(":")
    path = parts[0]
    if not os.path.exists(path):
        sys.exit(f"error: no such file: {path}")
    t_in = float(parts[1]) if len(parts) > 1 and parts[1] else 0.0
    t_out = float(parts[2]) if len(parts) > 2 and parts[2] else probe_duration(path)
    overlay = parts[3] if len(parts) > 3 and parts[3] else None
    if overlay and not os.path.exists(overlay):
        sys.exit(f"error: no such overlay: {overlay}")
    if t_out <= t_in:
        sys.exit(f"error: segment {spec}: out ({t_out}) must be after in ({t_in})")
    return {"file": path, "in": t_in, "out": t_out, "overlay": overlay}


def main():
    p = argparse.ArgumentParser(description="Join video segments frame-exact into one cut.")
    p.add_argument("segments", nargs="+", metavar="SEGMENT", help="path[:in[:out[:overlay.png]]]")
    p.add_argument("-o", "--out", required=True, help="output MP4")
    p.add_argument("--size", default="1920x1080", help="canvas WxH (default 1920x1080)")
    p.add_argument("--fps", type=int, default=60, help="output frame rate (default 60)")
    p.add_argument("--bg", default="000000", help="hex colour behind segments that don't fill the canvas")
    p.add_argument("--crf", default="16", help="x264 quality (default 16)")
    a = p.parse_args()
    w, h = map(int, a.size.lower().split("x"))
    segs = [parse_segment(s) for s in a.segments]

    inputs, chains, labels, n_in = [], [], [], 0
    at = 0.0
    for i, s in enumerate(segs):
        inputs += ["-i", s["file"]]
        v = n_in; n_in += 1
        f0, f1 = round(s["in"] * a.fps), round(s["out"] * a.fps)
        chain = (f"[{v}:v]fps={a.fps},scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,"
                 f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x{a.bg},setsar=1")
        if s["overlay"]:
            inputs += ["-i", s["overlay"]]
            o = n_in; n_in += 1
            chain += f"[b{i}];[{o}:v]scale={w}:{h}[o{i}];[b{i}][o{i}]overlay=0:0"
        chain += f",trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS,format=yuv420p[s{i}]"
        chains.append(chain); labels.append(f"[s{i}]")
        s["at"] = round(at, 4); s["frames"] = f1 - f0
        at += (f1 - f0) / a.fps
    graph = ";".join(chains) + ";" + "".join(labels) + f"concat=n={len(segs)}:v=1:a=0,fps={a.fps},format=yuv420p[v]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[v]",
                    "-c:v", "libx264", "-preset", "slow", "-crf", a.crf, "-movflags", "+faststart", a.out], check=True)

    frames = sum(s["frames"] for s in segs)
    timeline = {"DURATION": round(frames / a.fps, 4), "fps": a.fps, "frames": frames,
                "segments": [{k: s[k] for k in ("file", "in", "out", "at", "frames", "overlay") if s[k] is not None}
                             for s in segs]}
    tl_path = os.path.splitext(a.out)[0] + ".timeline.json"
    with open(tl_path, "w") as f:
        json.dump(timeline, f, indent=1)
        f.write("\n")
    for s in segs:
        print(f"{s['at']:8.3f}s  {s['file']}  [{s['in']:.3f}–{s['out']:.3f}]  {s['frames']} frames"
              + (f"  + {s['overlay']}" if s["overlay"] else ""))
    print(f"wrote {a.out} ({frames} frames, {frames / a.fps:.3f}s) and {tl_path}")


if __name__ == "__main__":
    main()

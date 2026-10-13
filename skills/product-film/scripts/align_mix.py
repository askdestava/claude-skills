#!/usr/bin/env python3
"""Lay a music take under a silent cut so its drop lands on a picture cue, then master and mux it.

    align_mix.py cut.mp4 take.mp3 --drop 7.62 --cue 12.10 -o cut_music.mp4 [--in 6.5] [--lift 10]
                 [--fade-from 20.1] [--lufs -14] [--limit 0.72] [--stem music.wav]

--drop  where the drop is in the take (drops.py lists candidates; confirm by ear)
--cue   where it must land in the cut: the frame the picture hits (a reveal, a cut, a logo)
--in    when the music starts in the cut (default: as early as the take allows). It fades in over 0.35 s
--lift  dB added to everything before the cue. A generated build often sits ~25 dB under its drop, which is
        silence on a phone speaker; the lift ramps back to 0 dB over the 80 ms before the cue (default 10)
--fade-from  start of the fade-out (default: 2.5 s before the end)

Mastering is a linear gain to --lufs and a peak limiter (--limit is its ceiling as a sample amplitude), not
dynamic loudness normalisation, which would flatten the build-to-drop contrast the whole edit depends on.
The placement is exact (take time + (cue - drop), to the sample), so the one thing that can be wrong is --drop
itself: the level strip printed around the cue should jump at the "|". Prints integrated
loudness and the measured true peak (aim for -1 dBTP or lower; lower --limit if it's higher).
Needs ffmpeg (with ebur128) and numpy.
"""
import argparse
import json
import os
import re
import subprocess
import tempfile
import numpy as np

SR = 48000


def video_duration(path):
    s = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=nb_frames,r_frame_rate,duration", "-of", "json", path],
                                  capture_output=True, text=True, check=True).stdout)["streams"][0]
    num, den = map(int, s["r_frame_rate"].split("/"))
    if s.get("nb_frames", "N/A") != "N/A":
        return int(s["nb_frames"]) * den / num
    return float(s["duration"])


def load(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, 2).astype(np.float64)


def loudness(args, stdin=None):
    err = subprocess.run(["ffmpeg", "-v", "info", "-nostats", *args, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         input=stdin, capture_output=True).stderr.decode()
    summary = err[err.rfind("Summary:"):]
    return (float(re.search(r"I:\s+(-?[\d.]+) LUFS", summary).group(1)),
            float(re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", summary).group(1)))


def ramp(t, t0, t1, v0, v1):
    """Smoothstep from v0 at t0 to v1 at t1."""
    u = np.clip((t - t0) / max(t1 - t0, 1e-9), 0, 1)
    u = u * u * (3 - 2 * u)
    return v0 + (v1 - v0) * u


def around(stem, cue):
    """The mastered music's level in 20 ms steps from 0.2 s before the cue to 0.3 s after, as one line to eyeball."""
    x = load(stem).mean(axis=1)
    cells = []
    for t in np.arange(cue - 0.2, cue + 0.3, 0.02):
        seg = x[int(max(t, 0) * SR):int(max(t + 0.02, 0) * SR)]
        db = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) if len(seg) else -99
        cells.append(f"{'|' if abs(t - cue) < 0.01 else ''}{db:.0f}")
    return " ".join(cells)


def main():
    p = argparse.ArgumentParser(description="Land a music take's drop on a picture cue, master, and mux.")
    p.add_argument("video"); p.add_argument("take")
    p.add_argument("--drop", type=float, required=True, help="the drop's time in the take (s)")
    p.add_argument("--cue", type=float, required=True, help="the time in the cut the drop must land on (s)")
    p.add_argument("-o", "--out", required=True, help="output MP4 (picture copied, AAC 192k)")
    p.add_argument("--in", dest="t_in", type=float, help="when the music fades in, in cut time (s)")
    p.add_argument("--lift", type=float, default=10.0, help="dB lift for the build before the cue (default 10)")
    p.add_argument("--fade-from", type=float, help="fade-out start in cut time (default: 2.5 s before the end)")
    p.add_argument("--lufs", type=float, default=-14.0, help="integrated loudness target (default -14)")
    p.add_argument("--limit", type=float, default=0.72, help="limiter ceiling, sample amplitude (default 0.72)")
    p.add_argument("--stem", help="also keep the mastered music as this 24-bit WAV")
    a = p.parse_args()

    dur = video_duration(a.video)
    take = load(a.take)
    shift = a.cue - a.drop                                   # take time τ plays at cut time τ + shift
    music = np.zeros((int(round(dur * SR)), 2))
    j0 = max(0, int(round(shift * SR))); k0 = max(0, -int(round(shift * SR)))
    n = max(0, min(len(music) - j0, len(take) - k0))
    music[j0:j0 + n] = take[k0:k0 + n]
    t = np.arange(len(music)) / SR

    t_in = max(a.t_in if a.t_in is not None else 0.0, shift, 0.0)
    fade_from = a.fade_from if a.fade_from is not None else dur - 2.5
    g = 10 ** (ramp(t, a.cue - 0.08, a.cue, a.lift, 0.0) / 20)
    g *= ramp(t, t_in, t_in + 0.35, 0, 1)
    g *= ramp(t, fade_from, dur - 0.05, 1, 0)
    pre = (music * g[:, None]).astype(np.float32).tobytes()

    raw = ["-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "pipe:"]
    i_pre, _ = loudness(raw, pre)
    with tempfile.TemporaryDirectory() as tmp:
        stem = a.stem or os.path.join(tmp, "music.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", *raw, "-af",
                        f"volume={a.lufs - i_pre:.2f}dB,alimiter=limit={a.limit}:attack=2:release=60:level=disabled",
                        "-ar", str(SR), "-c:a", "pcm_s24le", stem], input=pre, check=True)
        i_out, tp = loudness(["-i", stem])
        strip = around(stem, a.cue)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-i", stem, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out],
                       check=True)
    print(f"take {a.take}: its {a.drop:.3f}s drop → cut {a.cue:.3f}s; music in at {t_in:.3f}s, fade from {fade_from:.3f}s")
    print(f"loudness {i_pre:.1f} → {i_out:.1f} LUFS, true peak {tp:.1f} dBTP, {dur:.3f}s")
    print(f"level around the cue (dB per 20 ms, | = the cue): {strip}")
    print("wrote", a.out + (f" and {a.stem}" if a.stem else ""))


if __name__ == "__main__":
    main()

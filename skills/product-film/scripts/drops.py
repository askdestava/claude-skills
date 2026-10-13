#!/usr/bin/env python3
"""Find drop candidates in music takes, and rank the takes by how hard their best drop lands.

    drops.py take1.mp3 take2.mp3 ... [--curve] [--top 3]

A drop is scored at every 10 ms as the step from the 1.5 s before to the 1.5 s after: in overall level, in the
bass band (< 150 Hz, where a drop's kick and sub usually enter), and in the onset itself. Levels are floored 60 dB
under the take's peak, so digital silence in a build doesn't swamp the averages. It prints the --top candidates per
take (at least 0.5 s apart), best take first. --curve adds the loudness curve (0.25 s bins) to read them against.

These are CANDIDATES. A track can have more than one step (the bass enters, then the full drop a beat later), and
which one is "the drop" is a musical call: read the curve, listen, then give the chosen time to align_mix.py --drop.
On three takes whose drops were chosen by ear: a build → silence → drop take ranked it first (7.60 s, by ear
7.62 s); a two-step take listed its bass entry (3.41 s) and put a candidate 0.19 s before its full drop (3.97 s vs
4.16 s); a take used for its first hit near the start (1.95 s) was not found at all. Needs ffmpeg and numpy.
"""
import argparse
import subprocess
import numpy as np

SR = 48000
HOP = 480      # 10 ms
WIN = 2048


def mono(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32)


def levels(x):
    """Full-band and bass-band level per 10 ms frame (dB), floored 60 dB under each band's peak."""
    frames = np.lib.stride_tricks.sliding_window_view(x, WIN)[::HOP] * np.hanning(WIN)
    power = np.abs(np.fft.rfft(frames, axis=1)) ** 2
    freqs = np.fft.rfftfreq(WIN, 1 / SR)
    full = 10 * np.log10(power.sum(axis=1) + 1e-12)
    bass = 10 * np.log10(power[:, freqs < 150].sum(axis=1) + 1e-12)
    return np.maximum(full, full.max() - 60), np.maximum(bass, bass.max() - 60)


def candidates(x, top):
    full, bass = levels(x)
    k = 150                                                     # 1.5 s either side
    scored = []
    for i in range(k, len(full) - k):
        step = (np.median(full[i:i + k]) - np.median(full[i - k:i])) + (np.median(bass[i:i + k]) - np.median(bass[i - k:i]))
        onset = full[i:i + 3].max() - full[i - 5:i].max()
        bass_onset = bass[i:i + 3].max() - bass[i - 5:i].max()
        scored.append((step + 0.5 * np.clip(onset, 0, 20) + 0.5 * np.clip(bass_onset, 0, 20), i / 100))
    picked = []
    for score, t in sorted(scored, reverse=True):
        if all(abs(t - q) > 0.5 for _, q in picked):
            picked.append((score, t))
        if len(picked) == top:
            break
    return picked


def curve(x, path):
    hop = int(SR * 0.25); n = len(x) // hop
    db = 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9)
    print(f"\n{path}  {len(x) / SR:.2f}s, peak {20 * np.log10(np.abs(x).max() + 1e-12):.1f} dBFS  (dB RMS per 0.25 s)")
    for i in range(0, n, 8):
        print(f"  {i * 0.25:6.2f}s " + " ".join(f"{v:6.1f}" for v in db[i:i + 8]))


def main():
    p = argparse.ArgumentParser(description="Find drop candidates in music takes and rank the takes.")
    p.add_argument("takes", nargs="+")
    p.add_argument("--top", type=int, default=3, help="candidates per take (default 3)")
    p.add_argument("--curve", action="store_true", help="also print each take's loudness curve")
    a = p.parse_args()
    rows = []
    for path in a.takes:
        x = mono(path)
        if len(x) < 4 * SR:
            print(f"{path}: too short to score ({len(x) / SR:.1f}s)")
            continue
        if a.curve:
            curve(x, path)
        rows.append((path, len(x) / SR, candidates(x, a.top)))
    print()
    for path, dur, picks in sorted(rows, key=lambda r: -r[2][0][0]):
        print(f"{path}  {dur:.1f}s | drop candidates: " + "  ".join(f"{t:.2f}s (score {s:.0f})" for s, t in picks))


if __name__ == "__main__":
    main()

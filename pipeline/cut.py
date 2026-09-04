#!/usr/bin/env python3
"""
cut.py - turn a raw talking-head recording (silences, retakes) into an edit.json
that the Remotion "Reel" composition renders as a 1080x1920 Instagram reel.

Steps
  1. Probe the source and transcode a Chromium-friendly H.264 proxy to
     public/edit/source.mp4 (auto-rotates phone/camera footage, long side <= 1920,
     yuv420p, 30 fps, loudness-normalised audio).
  2. Detect silences with ffmpeg silencedetect and split into speech segments (takes).
  3. Optional transcript: faster-whisper if installed (--whisper small), or a
     words JSON from any STT tool (--transcript words.json). With a script
     (--script, one beat per line) every take is matched to a beat and the best
     take per beat is chosen (cleanest match, fewest fillers/restarts, later take
     wins ties). Without a transcript every take is kept in order.
  4. Optional b-roll manifest (--broll manifest.json). Each clip is attached to a
     beat (explicit "line", or keyword overlap with the script) and placed on that
     beat's take. Clips with no beat are spread evenly across the timeline.
  5. Writes public/edit/edit.json, public/edit/takes.md (take sheet) and
     public/edit/thumbs/*.jpg so the picks can be reviewed before rendering.

Usage
  python3 pipeline/cut.py raw/C0011.MP4 --script scripts/02-ochra/script.txt \
      --broll scripts/02-ochra/broll.json [--transcript words.json | --whisper small]
  npx remotion render src/index.ts Reel out/reel.mp4
"""
import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
EDIT_DIR = PUBLIC / "edit"
FILLERS = {"um", "uh", "erm", "er", "hmm", "basically", "literally", "yeah", "okay", "ok"}


# ---------------------------------------------------------------- ffmpeg helpers
def ffmpeg_exe() -> str:
    p = shutil.which("ffmpeg")
    if p:
        return p
    try:
        import imageio_ffmpeg  # type: ignore
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found. Install ffmpeg or run: pip install imageio-ffmpeg")


def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True)


def probe(ff, src):
    out = run([ff, "-hide_banner", "-i", str(src)]).stderr
    dur = 0.0
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", out)
    if m:
        dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    m = re.search(r"Video:.*?\b(\d{2,5})x(\d{2,5})\b", out)
    w, h = (int(m[1]), int(m[2])) if m else (0, 0)
    rot = 0
    m = re.search(r"rotation of (-?\d+(?:\.\d+)?) degrees", out) or re.search(r"rotate\s*:\s*(-?\d+)", out)
    if m:
        rot = int(float(m[1]))
    return {"duration": dur, "width": w, "height": h, "rotation": rot, "has_audio": "Audio:" in out}


def transcode(ff, src, dst, fps, loudnorm=True):
    vf = ("scale=w='if(gt(iw,ih),min(1920,iw),-2)':h='if(gt(iw,ih),-2,min(1920,ih))':flags=lanczos,"
          "format=yuv420p")
    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", vf, "-r", str(fps),
           "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    if loudnorm:
        cmd += ["-af", "loudnorm=I=-16:TP=-1.5:LRA=11"]
    cmd += ["-movflags", "+faststart", str(dst)]
    r = run(cmd)
    if r.returncode:
        sys.exit("transcode failed:\n" + r.stderr)


def detect_speech(ff, src, duration, noise_db, min_sil, pad, min_take):
    r = run([ff, "-hide_banner", "-nostats", "-i", str(src), "-af",
             f"silencedetect=noise={noise_db}dB:d={min_sil}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?\d+(?:\.\d+)?)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?\d+(?:\.\d+)?)", r.stderr)]
    silences = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else duration
        silences.append((max(0.0, s), min(duration, e)))
    speech, cursor = [], 0.0
    for s, e in silences:
        if s - cursor >= min_take:
            speech.append((cursor, s))
        cursor = e
    if duration - cursor >= min_take:
        speech.append((cursor, duration))
    padded = []
    for s, e in speech:
        s, e = max(0.0, s - pad), min(duration, e + pad)
        if padded and s <= padded[-1][1]:
            padded[-1] = (padded[-1][0], e)
        else:
            padded.append((s, e))
    return padded


def thumbnail(ff, src, t, dst):
    run([ff, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(src),
         "-frames:v", "1", "-vf", "scale=270:-2", str(dst)])


# ---------------------------------------------------------------- transcript
def load_transcript(path):
    data = json.loads(Path(path).read_text())
    words = []
    if isinstance(data, dict) and "words" in data:
        src = data["words"]
    elif isinstance(data, dict) and "segments" in data:
        src = [w for s in data["segments"] for w in s.get("words", [])]
    else:
        src = data
    for w in src:
        text = (w.get("word") or w.get("w") or w.get("text") or "").strip()
        if not text:
            continue
        words.append({"w": text, "s": float(w.get("start", w.get("s"))), "e": float(w.get("end", w.get("e")))})
    return words


def transcribe_whisper(src, model_name):
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        sys.exit("faster-whisper not installed: pip install faster-whisper")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(src), word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"w": w.word.strip(), "s": float(w.start), "e": float(w.end)})
    return words


def tokens(text):
    return re.findall(r"[a-z0-9']+", text.lower().replace("’", "'"))


def restarts(toks):
    n = 0
    for k in (2, 3):
        for i in range(len(toks) - 2 * k + 1):
            if toks[i:i + k] == toks[i + k:i + 2 * k]:
                n += 1
    return n


# ---------------------------------------------------------------- take selection
def build_takes(speech, words):
    takes = []
    for i, (s, e) in enumerate(speech, 1):
        tw = [w for w in words if s <= (w["s"] + w["e"]) / 2 <= e] if words else []
        text = " ".join(w["w"] for w in tw)
        takes.append({"id": i, "start": round(s, 3), "end": round(e, 3), "words": tw, "text": text})
    return takes


def select_takes(takes, script_lines, max_span=3, min_ratio=0.45):
    """Return (chosen takes in script order, per-line report)."""
    line_toks = [tokens(l) for l in script_lines]
    for t in takes:
        toks = tokens(t["text"])
        best = (0.0, None)
        for i in range(len(line_toks)):
            for j in range(i, min(len(line_toks), i + max_span)):
                span = [x for k in range(i, j + 1) for x in line_toks[k]]
                if not span:
                    continue
                ratio = difflib.SequenceMatcher(None, toks, span).ratio()
                if ratio > best[0]:
                    best = (ratio, (i, j))
        ratio, span = best
        expected = sum(len(line_toks[k]) for k in range(span[0], span[1] + 1)) if span else 0
        fill = sum(1 for x in toks if x in FILLERS)
        score = ratio - 0.04 * fill - 0.08 * restarts(toks)
        if expected and len(toks) < 0.5 * expected:
            score -= 0.15
        t.update({"span": span, "ratio": round(ratio, 3), "fillers": fill, "restarts": restarts(toks),
                  "score": round(score, 3)})
    chosen, report, used, li = [], [], set(), 0
    while li < len(script_lines):
        cands = [t for t in takes if t["span"] and t["span"][0] <= li <= t["span"][1]
                 and t["ratio"] >= min_ratio and t["id"] not in used]
        if not cands:
            report.append({"line": li, "status": "missing", "text": script_lines[li]})
            li += 1
            continue
        best = sorted(cands, key=lambda t: (t["score"], t["start"]))[-1]
        used.add(best["id"])
        best["line"] = li
        chosen.append(best)
        report.append({"line": li, "status": "ok", "take": best["id"], "text": script_lines[li],
                       "alternatives": [t["id"] for t in cands if t["id"] != best["id"]]})
        li = best["span"][1] + 1
    return chosen, report


# ---------------------------------------------------------------- b-roll
def place_broll(manifest, chosen, script_lines, fps):
    clips = manifest.get("clips", manifest if isinstance(manifest, list) else [])
    timeline, cursor = {}, 0.0
    for seg in chosen:
        seg["t0"] = round(cursor, 3)
        cursor += seg["end"] - seg["start"]
    total = cursor
    line_toks = [set(tokens(l)) for l in script_lines]
    placed, unplaced, used_lines = [], [], set()
    for c in clips:
        src = c.get("src")
        if src and not (PUBLIC / src).exists() and c.get("url"):
            src = c["url"]
        elif not src:
            src = c.get("url")
        if not src:
            continue
        entry = {"src": src, "kind": c.get("kind", "video"), "mode": c.get("mode", "cutaway"),
                 "offset": float(c.get("offset", 0.3)), "duration": float(c.get("duration", 5.0)),
                 "label": c.get("label", "")}
        line = c.get("line")
        if line is None and c.get("keywords") and script_lines:
            kw = set(tokens(" ".join(c["keywords"])))
            scored = sorted(((len(kw & lt), -abs(i - 0)), i) for i, lt in enumerate(line_toks))
            best = scored[-1]
            if best[0][0] > 0:
                line = best[1]
        seg = next((s for s in chosen if line is not None and s.get("line") is not None
                    and s["span"][0] <= line <= s["span"][1]), None) if script_lines else None
        if seg is None and c.get("at") is not None:
            entry["t"] = float(c["at"])
            placed.append(entry)
            continue
        if seg is None:
            unplaced.append(entry)
            continue
        seg_len = seg["end"] - seg["start"]
        taken = sum(p["duration"] for p in placed if p.get("segment") == seg["id"])
        off = entry["offset"] + taken
        dur = min(entry["duration"], seg_len - off - 0.2)
        if dur < 1.0:
            unplaced.append(entry)
            continue
        entry.update({"segment": seg["id"], "offset": round(off, 3), "duration": round(dur, 3), "line": line})
        placed.append(entry)
    if unplaced and total > 0:
        gap = total / (len(unplaced) + 1)
        for k, entry in enumerate(unplaced, 1):
            entry["t"] = round(gap * k - entry["duration"] / 2, 3)
            placed.append(entry)
    for entry in placed:
        if "t" in entry:
            seg = next((s for s in chosen if s["t0"] <= entry["t"] < s["t0"] + (s["end"] - s["start"])), None)
            if seg is None:
                continue
            entry["segment"] = seg["id"]
            entry["offset"] = round(max(0.0, entry["t"] - seg["t0"]), 3)
            entry["duration"] = round(min(entry["duration"], (seg["end"] - seg["start"]) - entry["offset"] - 0.1), 3)
            del entry["t"]
    return [p for p in placed if p.get("segment") is not None and p["duration"] >= 0.5]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("--script", help="text file, one script beat per line")
    ap.add_argument("--broll", help="b-roll manifest JSON")
    ap.add_argument("--transcript", help="words JSON from any STT tool (word/start/end)")
    ap.add_argument("--whisper", metavar="MODEL", help="transcribe with faster-whisper (e.g. small, medium)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--noise", type=float, default=-35.0, help="silence threshold dB")
    ap.add_argument("--min-silence", type=float, default=0.6)
    ap.add_argument("--min-take", type=float, default=0.6)
    ap.add_argument("--pad", type=float, default=0.12)
    ap.add_argument("--focus", default="50,40", help="crop focus x,y percent for portrait framing")
    ap.add_argument("--punch", type=float, default=0.08, help="punch-in zoom alternated on cuts")
    ap.add_argument("--keep-all", action="store_true", help="keep every take, skip selection")
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--no-loudnorm", action="store_true")
    ap.add_argument("--reuse-proxy", action="store_true", help="skip transcode if source.mp4 exists")
    args = ap.parse_args()

    ff = ffmpeg_exe()
    src = Path(args.source)
    if not src.exists():
        sys.exit(f"no such file: {src}")
    EDIT_DIR.mkdir(parents=True, exist_ok=True)
    (EDIT_DIR / "thumbs").mkdir(exist_ok=True)
    proxy = EDIT_DIR / "source.mp4"
    info = probe(ff, src)
    print(f"source: {info['width']}x{info['height']} rot={info['rotation']} {info['duration']:.1f}s audio={info['has_audio']}")
    if not (args.reuse_proxy and proxy.exists()):
        print("transcoding proxy ->", proxy.relative_to(ROOT))
        transcode(ff, src, proxy, args.fps, loudnorm=not args.no_loudnorm and info["has_audio"])
    pinfo = probe(ff, proxy)

    speech = detect_speech(ff, proxy, pinfo["duration"], args.noise, args.min_silence, args.pad, args.min_take)
    print(f"speech segments: {len(speech)}")

    words = []
    if args.transcript:
        words = load_transcript(args.transcript)
    elif args.whisper:
        words = transcribe_whisper(proxy, args.whisper)
    takes = build_takes(speech, words)
    for t in takes:
        thumbnail(ff, proxy, (t["start"] + t["end"]) / 2, EDIT_DIR / "thumbs" / f"take_{t['id']:02d}.jpg")

    script_lines = []
    if args.script:
        script_lines = [l.strip() for l in Path(args.script).read_text().splitlines() if l.strip()]

    report = []
    if script_lines and words and not args.keep_all:
        chosen, report = select_takes(takes, script_lines)
    else:
        chosen = takes
        for t in chosen:
            t["span"] = None
    if not chosen:
        sys.exit("no takes selected; lower --noise or check the audio")

    broll = []
    if args.broll:
        manifest = json.loads(Path(args.broll).read_text())
        broll = place_broll(manifest, chosen, script_lines, args.fps)
    else:
        cursor = 0.0
        for seg in chosen:
            seg["t0"] = round(cursor, 3)
            cursor += seg["end"] - seg["start"]

    fx, fy = (float(x) for x in args.focus.split(","))
    edit = {
        "fps": args.fps, "width": 1080, "height": 1920,
        "source": "edit/source.mp4", "sourceInfo": pinfo,
        "focus": {"x": fx, "y": fy}, "punchIn": args.punch,
        "captions": not args.no_captions and bool(words),
        "segments": [{"id": s["id"], "start": s["start"], "end": s["end"], "t0": s.get("t0", 0.0),
                      "line": s.get("line"), "text": s["text"],
                      "words": [{"w": w["w"], "s": round(w["s"], 3), "e": round(w["e"], 3)} for w in s["words"]]}
                     for s in chosen],
        "broll": broll,
    }
    (EDIT_DIR / "edit.json").write_text(json.dumps(edit, indent=1))
    total = sum(s["end"] - s["start"] for s in chosen)

    lines = [f"# Take sheet\n", f"Source: `{src}`  proxy: `{proxy.relative_to(ROOT)}`  ",
             f"Takes found: {len(takes)}  chosen: {len(chosen)}  cut length: {total:.1f}s\n",
             "| take | in | out | len | score | line | chosen | text |", "|---|---|---|---|---|---|---|---|"]
    chosen_ids = {s["id"] for s in chosen}
    for t in takes:
        lines.append(f"| {t['id']} | {t['start']:.2f} | {t['end']:.2f} | {t['end'] - t['start']:.1f}s | "
                     f"{t.get('score', '')} | {t.get('line', '') if t['id'] in chosen_ids else ''} | "
                     f"{'yes' if t['id'] in chosen_ids else ''} | {t['text'][:90]} |")
    if report:
        lines += ["\n## Script coverage\n", "| line | status | take | alternatives | beat |", "|---|---|---|---|---|"]
        for r in report:
            lines.append(f"| {r['line']} | {r['status']} | {r.get('take', '')} | "
                         f"{','.join(str(a) for a in r.get('alternatives', []))} | {r['text'][:80]} |")
    if broll:
        lines += ["\n## B-roll placement\n", "| clip | on take | offset | dur | mode | line |", "|---|---|---|---|---|---|"]
        for b in broll:
            lines.append(f"| {b.get('label') or b['src']} | {b['segment']} | {b['offset']} | {b['duration']} | {b['mode']} | {b.get('line', '')} |")
    lines.append("\nThumbnails: public/edit/thumbs/take_XX.jpg. Edit public/edit/edit.json by hand to override, then render.")
    (EDIT_DIR / "takes.md").write_text("\n".join(lines))
    print(f"chosen {len(chosen)} takes, {total:.1f}s, {len(broll)} b-roll placements")
    print("wrote", (EDIT_DIR / "edit.json").relative_to(ROOT), "and", (EDIT_DIR / "takes.md").relative_to(ROOT))
    if report:
        missing = [r for r in report if r["status"] == "missing"]
        if missing:
            print(f"WARNING: {len(missing)} script line(s) had no matching take: {[r['line'] for r in missing]}")


if __name__ == "__main__":
    main()

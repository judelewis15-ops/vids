#!/usr/bin/env python3
"""Burns the map labels into the OpenArt map clip with real type, no model.

    python3 maria-sabina/build/tools/label-map.py \
        --in  maria-sabina/exports/map/HO01_02-03_MAP_zoom.mp4 \
        --out maria-sabina/exports/map/HO01_02-03_MAP_zoom_labelled.mp4 \
        [--overlay maria-sabina/exports/map/HO01_02-03_MAP_labels.mov]   # ProRes 4444 alpha, labels only
        [--ny-until 2.0] [--land-at -1.0] [--text-scale 2.0] [--no-oaxaca]

What it does
  1. Reads the clip, finds the glowing violet New York marker in the opening
     frames and the cream ring marker in the closing frames (colour tracking,
     nothing guessed), and smooths the positions.
  2. Sets the labels in JetBrains Mono (bundled in build/fonts): uppercase,
     0.18 em tracking, cream, drop shadow 0 1px 6px rgba(0,0,0,0.9), fade plus
     6 px slide from the left over 300 ms. NEW YORK follows its marker until
     --ny-until seconds and fades out; HUAUTLA DE JIMÉNEZ then SIERRA MAZATECA
     (smaller, 60%) land at --land-at seconds (negative = seconds before the
     end, default the final second, the settle); OAXACA sits lower in the lit
     state at 60%.
  3. Writes the labelled MP4 (H.264, CRF 14) and optionally an alpha overlay.

Sizes follow the brief (11 px city, 9 px region at 1080 scale) multiplied by
--text-scale so they survive the STACKED composition; pass 1 for the literal
sizes.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FONT = os.path.join(ROOT, "maria-sabina", "build", "fonts", "JetBrainsMono-VF.ttf")
FFMPEG = next((p for p in [os.path.join(ROOT, "node_modules/@remotion/compositor-linux-x64-gnu/ffmpeg"), shutil.which("ffmpeg") or ""] if p and os.path.exists(p)), "ffmpeg")
FFPROBE = FFMPEG.replace("ffmpeg", "ffprobe") if FFMPEG.endswith("ffmpeg") else "ffprobe"
CREAM = (250, 247, 242)

def probe(path):
    out = subprocess.check_output([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,r_frame_rate,nb_frames,duration", "-of", "json", path])
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    n = int(s.get("nb_frames") or 0)
    dur = float(s.get("duration") or 0)
    if not n:
        n = int(round(dur * fps))
    return int(s["width"]), int(s["height"]), fps, n

def extract(path, outdir, width):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", path, "-vf", f"scale={width}:-2", os.path.join(outdir, "f_%05d.png")], check=True)
    return sorted(os.listdir(outdir))

def blob_centroid(mask, min_px=4):
    """Largest 4-connected blob centroid in a boolean mask, or None."""
    ys, xs = np.nonzero(mask)
    if len(xs) < min_px:
        return None
    # cheap connected components: bucket by coarse grid, pick densest cell, refine around it
    h, w = mask.shape
    cell = max(4, min(h, w) // 40)
    grid = {}
    for x, y in zip(xs, ys):
        grid.setdefault((x // cell, y // cell), []).append((x, y))
    (cx, cy), pts = max(grid.items(), key=lambda kv: len(kv[1]))
    sel = [(x, y) for x, y in zip(xs, ys) if abs(x // cell - cx) <= 1 and abs(y // cell - cy) <= 1]
    if len(sel) < min_px:
        return None
    a = np.array(sel, dtype=float)
    return float(a[:, 0].mean()), float(a[:, 1].mean())

def find_violet(img, prev=None, region=(0.5, 0.0, 1.0, 0.6)):
    """Glowing violet marker (#7C3AED family): strong blue and red, weak green, bright.
    Searches the upper-right region (New York sits there on the start frame) or,
    once found, a window around the previous position so the arc's violet line
    and the destination marker never steal it."""
    a = np.asarray(img.convert("RGB")).astype(int)
    h, w = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mask = (b > 150) & (r > 70) & (g < 120) & (b - g > 70) & (r + b > 260)
    win = np.zeros_like(mask)
    if prev is not None:
        x0, y0 = int(prev[0]), int(prev[1]); k = max(12, w // 24)
        win[max(0, y0 - k): y0 + k, max(0, x0 - k): x0 + k] = True
    else:
        win[int(h * region[1]): int(h * region[3]), int(w * region[0]): int(w * region[2])] = True
    return blob_centroid(mask & win, min_px=3)

def find_cream_ring(img):
    """Cream ring marker: near-white, neutral pixels in a small cluster."""
    a = np.asarray(img.convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mask = (r > 215) & (g > 210) & (b > 200) & (abs(r - b) < 40) & (abs(r - g) < 30)
    return blob_centroid(mask, min_px=3)

def smooth(track):
    """Median-smooth a list of (x, y) or None over a 5-frame window."""
    out = []
    for i in range(len(track)):
        win = [t for t in track[max(0, i - 2): i + 3] if t is not None]
        if not win:
            out.append(None); continue
        xs, ys = sorted(p[0] for p in win), sorted(p[1] for p in win)
        out.append((xs[len(xs) // 2], ys[len(ys) // 2]))
    return out

def ease_out(t):
    t = min(1.0, max(0.0, t)); return 1 - (1 - t) ** 3

def draw_label(layer, text, x, y, size, alpha, scale, anchor="l"):
    """Tracked uppercase mono label with a soft shadow, drawn onto an RGBA layer."""
    font = ImageFont.truetype(FONT, size)
    try:
        font.set_variation_by_axes([500])
    except Exception:
        pass
    text = text.upper()
    track = size * 0.18
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    W_, H_ = layer.size
    margin = size * 1.2
    # keep the label in frame: flip to the other side of its marker when there is no room
    if anchor == "l" and x + total > W_ - margin:
        x = x - total - 2 * 14 * scale; anchor = "flipped"
    if anchor == "r":
        x -= total
        if x < margin:
            x = x + total + 2 * 14 * scale
    elif anchor == "c":
        x -= total / 2
    x = min(max(x, margin), W_ - margin - total)
    y = min(max(y, margin), H_ - margin - size * 1.6)
    pad = int(size * 1.5)
    box = Image.new("RGBA", (int(total) + pad * 2, int(size * 1.6) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    cx = pad
    for ch, w in zip(text, widths):
        d.text((cx, pad), ch, font=font, fill=(0, 0, 0, int(230 * alpha)))
        cx += w + track
    shadow = box.filter(ImageFilter.GaussianBlur(3 * scale))
    # shadow offset 1px (at 1080 scale)
    txt = Image.new("RGBA", box.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    cx = pad
    for ch, w in zip(text, widths):
        d.text((cx, pad), ch, font=font, fill=CREAM + (int(255 * alpha),))
        cx += w + track
    layer.alpha_composite(shadow, (int(x) - pad, int(y) - pad + int(1 * scale)))
    layer.alpha_composite(txt, (int(x) - pad, int(y) - pad))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--overlay", dest="overlay", default=None, help="also write a ProRes 4444 alpha overlay (labels only)")
    ap.add_argument("--ny-until", type=float, default=2.0, help="seconds: NEW YORK label gone by here (brief: exits by 0:09)")
    ap.add_argument("--land-at", type=float, default=-1.0, help="seconds when the Huautla labels land; negative counts from the end")
    ap.add_argument("--text-scale", type=float, default=2.0)
    ap.add_argument("--no-oaxaca", action="store_true")
    ap.add_argument("--keep-frames", action="store_true")
    a = ap.parse_args()

    W, H, fps, N = probe(a.src)
    dur = N / fps
    land = a.land_at if a.land_at >= 0 else dur + a.land_at
    S = (H / 1080.0) * a.text_scale                    # brief sizes are given at 1080 scale
    city, region = int(round(11 * S)), int(round(9 * S))
    tmp = tempfile.mkdtemp(prefix="labelmap_")
    fr_dir, ov_dir = os.path.join(tmp, "frames"), os.path.join(tmp, "overlay")
    os.makedirs(fr_dir); os.makedirs(ov_dir)
    track_w = 960
    frames = extract(a.src, fr_dir, track_w)
    k = W / track_w
    print(f"{W}x{H} {fps:.3f} fps {N} frames {dur:.2f} s; tracking at {track_w} px")

    # 1. track the markers
    ny, prev = [], None
    for i, f in enumerate(frames):
        if i / fps > a.ny_until + 0.3:
            ny.append(None); continue
        im = Image.open(os.path.join(fr_dir, f))
        pos = find_violet(im, prev)
        if pos is not None:
            prev = pos
        ny.append(pos)
    ny = smooth(ny)
    ring = []
    for i, f in enumerate(frames):
        if i / fps < land - 0.6:
            ring.append(None); continue
        im = Image.open(os.path.join(fr_dir, f))
        ring.append(find_cream_ring(im))
    ring = smooth(ring)
    last_ring = next((r for r in reversed(ring) if r is not None), None)
    first_ny = next((r for r in ny if r is not None), None)
    print("New York marker:", "found" if first_ny else "NOT FOUND (label skipped)",
          "| ring marker:", "found" if last_ring else "NOT FOUND (labels placed centre-frame)")

    # 2. render overlay frames
    for i in range(N):
        t = i / fps
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        # NEW YORK: in over 300 ms from t=0, out over 300 ms ending at ny_until, follows the marker
        pos = ny[i] if i < len(ny) else None
        if pos is not None and t < a.ny_until:
            ain = ease_out(t / 0.3)
            aout = 1 - ease_out((t - (a.ny_until - 0.3)) / 0.3) if t > a.ny_until - 0.3 else 1
            al = ain * aout
            if al > 0:
                slide = (1 - ain) * 6 * S
                draw_label(layer, "New York", pos[0] * k + 14 * S - slide, pos[1] * k - city * 0.6, city, al, S)
        # Huautla labels on the settle, staggered 200 ms; OAXACA lower in the lit state
        if t >= land:
            base = (last_ring[0] * k, last_ring[1] * k) if last_ring else (W * 0.5, H * 0.45)
            a1 = ease_out((t - land) / 0.3)
            draw_label(layer, "Huautla de Jiménez", base[0] - 14 * S - (1 - a1) * 6 * S, base[1] - city * 2.1, city, a1, S, anchor="r")
            a2 = ease_out((t - land - 0.2) / 0.3)
            if a2 > 0:
                draw_label(layer, "Sierra Mazateca", base[0] - 14 * S - (1 - a2) * 6 * S, base[1] - city * 0.7, region, 0.6 * a2, S, anchor="r")
            a3 = ease_out((t - land - 0.4) / 0.3)
            if a3 > 0 and not a.no_oaxaca:
                draw_label(layer, "Oaxaca", W * 0.5 - (1 - a3) * 6 * S, H * 0.80, region, 0.6 * a3, S, anchor="c")
        layer.save(os.path.join(ov_dir, f"o_{i:05d}.png"))

    # 3. burn in, and optionally the alpha overlay. Compositing is done in
    # Python so this also works with minimal ffmpeg builds (no overlay filter);
    # ffmpeg only decodes and encodes.
    pattern = os.path.join(ov_dir, "o_%05d.png")
    full_dir, out_dir = os.path.join(tmp, "full"), os.path.join(tmp, "out")
    os.makedirs(full_dir); os.makedirs(out_dir)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", a.src, os.path.join(full_dir, "f_%05d.png")], check=True)
    for i in range(N):
        src_f = os.path.join(full_dir, f"f_{i + 1:05d}.png")
        if not os.path.exists(src_f):
            break
        base = Image.open(src_f).convert("RGBA")
        base.alpha_composite(Image.open(os.path.join(ov_dir, f"o_{i:05d}.png")))
        base.convert("RGB").save(os.path.join(out_dir, f"c_{i:05d}.png"))
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(out_dir, "c_%05d.png"),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], check=True)
    print("wrote", a.out)
    if a.overlay:
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", str(fps), "-i", pattern, "-c:v", "prores_ks",
                        "-profile:v", "4444", "-pix_fmt", "yuva444p10le", a.overlay], check=True)
        print("wrote", a.overlay)
    if a.keep_frames:
        print("frames kept in", tmp)
    else:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Highlighter swipe and highlight-box elements for the document shots (brief
section 7): a rough-edged marker stroke that draws on left to right over 400 ms,
and a box highlight whose surroundings dim to 40%. Transparent, so they sit on
top of any document in Premiere (Multiply blend for the marker stroke).

    python3 maria-sabina/build/tools/highlight-element.py            # all presets
    python3 maria-sabina/build/tools/highlight-element.py --colour neon  # neon variant

Outputs in exports/elements/:
  HL_swipe_<colour>_<w>x<h>.mov      ProRes 4444 alpha, 60 fps, 1.0 s (draws on in 0.4 s, holds)
  HL_swipe_<colour>_<w>x<h>/         PNG sequence of the same
  HL_box-dim_<w>x<h>.mov             box highlight with dim outside, 60 fps, 1.0 s
"""
import argparse, math, os, random, shutil, subprocess
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "maria-sabina", "exports", "elements")
FFMPEG = next((p for p in [os.path.join(ROOT, "node_modules/@remotion/compositor-linux-x64-gnu/ffmpeg"), shutil.which("ffmpeg") or ""] if p and os.path.exists(p)), "ffmpeg")
COLOURS = {"marker": (245, 217, 10, 0.55), "neon": (204, 255, 0, 0.75), "cream": (250, 247, 242, 0.5)}
FPS, DUR, DRAW = 60, 1.0, 0.4

def ease_out(t): t = min(1, max(0, t)); return 1 - (1 - t) ** 3

def rough_stroke(w, h, progress, rgb, alpha, seed=7):
    """A marker stroke of the element's full width, revealed to `progress`, with
    a wobbly top and bottom edge and a slightly darker, drier tail."""
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    reveal = int(w * ease_out(progress))
    if reveal <= 0:
        return layer
    step = max(2, w // 120)
    top, bot = [], []
    for x in range(0, w + step, step):
        wob = math.sin(x / (w * 0.09) + seed) * h * 0.06 + rnd.uniform(-1, 1) * h * 0.04
        top.append((x, h * 0.18 + wob)); bot.append((x, h * 0.82 + wob * 0.8))
    poly = top + bot[::-1]
    d.polygon(poly, fill=rgb + (int(255 * alpha),))
    # dry, streaky texture along the stroke
    tex = Image.new("L", (w, h), 255)
    td = ImageDraw.Draw(tex)
    for _ in range(int(w / 12)):
        x0 = rnd.uniform(0, w); y0 = rnd.uniform(h * 0.2, h * 0.8)
        td.line([(x0, y0), (x0 + rnd.uniform(w * 0.02, w * 0.1), y0 + rnd.uniform(-2, 2))], fill=int(rnd.uniform(150, 235)), width=max(1, h // 40))
    tex = tex.filter(ImageFilter.GaussianBlur(1))
    a = layer.split()[3]
    a = Image.eval(a, lambda v: v)  # copy
    a = Image.composite(a, Image.new("L", (w, h), 0), tex.point(lambda v: 255 if v > 0 else 0))
    a = Image.fromarray((__import__("numpy").asarray(a).astype(float) * (__import__("numpy").asarray(tex).astype(float) / 255)).astype("uint8"))
    layer.putalpha(a)
    # reveal left to right with a soft, slightly ragged leading edge
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rectangle([0, 0, reveal, h], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(1, w // 200)))
    layer.putalpha(Image.fromarray((__import__("numpy").asarray(layer.split()[3]).astype(float) * __import__("numpy").asarray(mask).astype(float) / 255).astype("uint8")))
    return layer

def encode(seq_dir, pattern, mov):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(seq_dir, pattern),
                    "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", mov], check=True)

def swipe(colour, w, h):
    rgb, alpha = COLOURS[colour][:3], COLOURS[colour][3]
    name = f"HL_swipe_{colour}_{w}x{h}"
    seq = os.path.join(OUT, name); os.makedirs(seq, exist_ok=True)
    n = int(FPS * DUR)
    for i in range(n):
        p = (i / FPS) / DRAW
        rough_stroke(w, h, p, rgb, alpha).save(os.path.join(seq, f"{name}_{i:04d}.png"))
    encode(seq, f"{name}_%04d.png", os.path.join(OUT, name + ".mov"))
    print("wrote", name)

def box_dim(w, h, box=(0.18, 0.30, 0.64, 0.40)):
    """Full-frame element: yellow box fill at 35% inside `box` (fractions), dim to 40% outside, draws on in 400 ms."""
    name = f"HL_box-dim_{w}x{h}"
    seq = os.path.join(OUT, name); os.makedirs(seq, exist_ok=True)
    n = int(FPS * DUR)
    bx, by, bw, bh = int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)
    for i in range(n):
        p = ease_out((i / FPS) / DRAW)
        layer = Image.new("RGBA", (w, h), (10, 4, 18, int(255 * 0.6 * p)))   # outside dims to 40%
        d = ImageDraw.Draw(layer)
        d.rectangle([bx, by, bx + bw, by + bh], fill=(245, 217, 10, int(255 * 0.35 * p)))
        d.rectangle([bx, by, bx + bw, by + bh], outline=(245, 217, 10, int(255 * 0.9 * p)), width=max(2, w // 600))
        layer.save(os.path.join(seq, f"{name}_{i:04d}.png"))
    encode(seq, f"{name}_%04d.png", os.path.join(OUT, name + ".mov"))
    print("wrote", name)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--colour", choices=list(COLOURS), default=None, help="one colour only; default renders marker and neon")
    ap.add_argument("--size", default="1600x160", help="swipe element size, e.g. 1600x160 (scale it over the word in Premiere)")
    ap.add_argument("--frame", default="2160x3840", help="full-frame size for the box element")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    sw, sh = map(int, a.size.split("x")); fw, fh = map(int, a.frame.split("x"))
    for c in ([a.colour] if a.colour else ["marker", "neon"]):
        swipe(c, sw, sh)
    box_dim(fw, fh)

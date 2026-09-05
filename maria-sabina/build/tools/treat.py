#!/usr/bin/env python3
"""Document and photo treatments from brief section 7, rendered deterministically
from a still. No model, no motion invented: a camera move over a real image.

    # photo: 2.5D-style push 100 -> 108%, archive grade, source label
    python3 maria-sabina/build/tools/treat.py --mode photo --in assets/HO01_01_PHOTO_portrait.jpg \
        --out work/HO01_01_PHOTO_portrait_push.mp4 --dur 7 --label "INAH · NACHO LÓPEZ · c.1975"

    # document: on the dark surface, 3 degrees off square, soft shadow, parallax,
    # light sweep, camera drifts, highlighter swipe on a word box, source label
    python3 maria-sabina/build/tools/treat.py --mode doc --in assets/HO01_10_DOC_life-village-name.jpg \
        --out work/HO01_10_DOC_village-name.mp4 --dur 3 --push 1.6 --focus 0.42,0.61 \
        --swipe 0.36,0.585,0.14,0.035 --swipe-at 0.6 --label "LIFE · 13 MAY 1957"

    # document: highlight box with the outside dimmed to 40%
    python3 maria-sabina/build/tools/treat.py --mode doc --in assets/HO01_09_DOC_life-spread.jpg \
        --out work/HO01_09_DOC_spread.mp4 --dur 3 --drift 0,0.12 --box 0.1,0.3,0.8,0.18 --box-at 0.8

Boxes are fractions of the source image: x,y,w,h. Use --grid to write a PNG of
the source with a numbered 10x10 grid so boxes can be read off by eye.
Output size defaults to the 9:16 master (2160x3840); pass --size 3840x2160 for a
STACKED asset. Frame rate 60. Archive grade = desaturate, lift blacks a touch,
soft contrast; grain is added in Premiere per section 8, not here.
"""
import argparse, math, os, shutil, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FONT = os.path.join(ROOT, "maria-sabina", "build", "fonts", "JetBrainsMono-VF.ttf")
FFMPEG = next((p for p in [os.path.join(ROOT, "node_modules/@remotion/compositor-linux-x64-gnu/ffmpeg"), shutil.which("ffmpeg") or ""] if p and os.path.exists(p)), "ffmpeg")
SURFACE = (10, 4, 18)
CREAM = (250, 247, 242)
YELLOW = (245, 217, 10)
FPS = 60

def ease_out(t): t = min(1, max(0, t)); return 1 - (1 - t) ** 3

def archive_grade(im):
    g = ImageOps.grayscale(im)
    g = ImageEnhance.Contrast(g).enhance(1.12)
    arr = np.asarray(g).astype(float)
    arr = 18 + arr * (1 - 18 / 255)          # lift blacks a touch
    return Image.fromarray(arr.clip(0, 255).astype("uint8")).convert("RGB")

def label(layer, text, scale, alpha=0.7):
    """Source label, bottom right: JetBrains Mono, uppercase, 9 px at 1080 scale x2 for legibility."""
    if not text: return
    size = int(round(9 * scale * 2))
    font = ImageFont.truetype(FONT, size)
    try: font.set_variation_by_axes([500])
    except Exception: pass
    text = text.upper(); track = size * 0.18
    widths = [font.getlength(c) for c in text]; total = sum(widths) + track * (len(text) - 1)
    W, H = layer.size; x = W - total - 48 * scale; y = H - size * 2.4 - 48 * scale
    d = ImageDraw.Draw(layer); cx = x
    for c, w in zip(text, widths):
        d.text((cx + 1, y + 1), c, font=font, fill=(0, 0, 0, int(200 * alpha)))
        d.text((cx, y), c, font=font, fill=CREAM + (int(255 * alpha),)); cx += w + track

def swipe_layer(size, box, progress, seed=7):
    """Rough marker stroke inside `box` (pixels), revealed left to right."""
    import random
    rnd = random.Random(seed)
    W, H = size; x, y, w, h = box
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if progress <= 0 or w < 2 or h < 2: return layer
    d = ImageDraw.Draw(layer)
    step = max(2, int(w // 80)); top, bot = [], []
    for i in range(0, int(w) + step, step):
        wob = math.sin(i / (w * 0.09) + seed) * h * 0.08 + rnd.uniform(-1, 1) * h * 0.05
        top.append((x + i, y - h * 0.15 + wob)); bot.append((x + i, y + h * 1.15 + wob * 0.8))
    d.polygon(top + bot[::-1], fill=YELLOW + (int(255 * 0.55),))
    reveal = x + w * ease_out(progress)
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rectangle([0, 0, reveal, H], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(1, w // 60)))
    a = (np.asarray(layer.split()[3]).astype(float) * np.asarray(mask).astype(float) / 255).astype("uint8")
    layer.putalpha(Image.fromarray(a))
    return layer

def multiply(base, layer):
    b = np.asarray(base.convert("RGB")).astype(float) / 255
    o = np.asarray(layer).astype(float) / 255
    a = o[..., 3:4]
    out = b * (1 - a) + (b * o[..., :3]) * a
    return Image.fromarray((out * 255).clip(0, 255).astype("uint8"))

def render(a):
    W, H = map(int, a.size.split("x"))
    src = Image.open(a.src).convert("RGB")
    if a.grid:
        g = src.copy(); d = ImageDraw.Draw(g); font = ImageFont.truetype(FONT, max(12, src.width // 60))
        for i in range(1, 10):
            d.line([(src.width * i / 10, 0), (src.width * i / 10, src.height)], fill=(255, 0, 0), width=2)
            d.line([(0, src.height * i / 10), (src.width, src.height * i / 10)], fill=(255, 0, 0), width=2)
            d.text((src.width * i / 10 + 4, 4), f"x{i / 10:.1f}", font=font, fill=(255, 0, 0))
            d.text((4, src.height * i / 10 + 4), f"y{i / 10:.1f}", font=font, fill=(255, 0, 0))
        g.save(a.grid); print("grid", a.grid); return
    if a.mode == "photo" or a.grade:
        src = archive_grade(src)
    n = int(a.dur * FPS); scale = H / 1080.0 if H >= W else H / 1080.0 * (H / W) * (16 / 9)
    scale = max(scale, W / 1080.0 * 0.5625) if W > H else H / 1920.0 * 1.777
    scale = H / 1080.0 if W < H else W / 1920.0   # label/shadow scale relative to a 1080-tall landscape
    tmp = tempfile.mkdtemp(prefix="treat_"); out_dir = os.path.join(tmp, "f"); os.makedirs(out_dir)
    fx, fy = map(float, a.focus.split(",")) if a.focus else (0.5, 0.5)
    dx, dy = map(float, a.drift.split(",")) if a.drift else (0.0, 0.0)
    sw = list(map(float, a.swipe.split(","))) if a.swipe else None
    bx = list(map(float, a.box.split(","))) if a.box else None
    for i in range(n):
        t = i / FPS; p = ease_out(t / a.dur)          # cubic out over the shot, ends on a hold
        frame = Image.new("RGB", (W, H), SURFACE if a.mode == "doc" else (0, 0, 0))
        zoom = 1 + (a.push - 1) * p
        if a.mode == "photo":
            # cover the frame, then push toward the focus point
            s = max(W / src.width, H / src.height) * zoom
            iw, ih = int(src.width * s), int(src.height * s)
            im = src.resize((iw, ih), Image.LANCZOS)
            cx = fx * iw + (dx * iw) * p; cy = fy * ih + (dy * ih) * p
            x0 = int(min(max(0, cx - W / 2), iw - W)); y0 = int(min(max(0, cy - H / 2), ih - H))
            frame.paste(im.crop((x0, y0, x0 + W, y0 + H)), (0, 0))
            comp = frame.convert("RGBA")
        else:
            # document on the dark surface: 2-4 degrees off square, soft shadow, parallax
            fit = min(W * 0.86 / src.width, H * 0.86 / src.height) * zoom
            iw, ih = int(src.width * fit), int(src.height * fit)
            page = src.resize((iw, ih), Image.LANCZOS).convert("RGBA")
            # highlights live on the page so they move with it
            if sw:
                sp = (t - a.swipe_at) / 0.4
                page = multiply(page, swipe_layer(page.size, (sw[0] * iw, sw[1] * ih, sw[2] * iw, sw[3] * ih), sp)).convert("RGBA")
            if bx:
                bp = ease_out((t - a.box_at) / 0.4)
                if bp > 0:
                    dim = Image.new("RGBA", page.size, (10, 4, 18, int(255 * 0.6 * bp)))
                    ImageDraw.Draw(dim).rectangle([bx[0] * iw, bx[1] * ih, (bx[0] + bx[2]) * iw, (bx[1] + bx[3]) * ih], fill=(245, 217, 10, int(255 * 0.35 * bp)))
                    page.alpha_composite(dim)
            # light sweep: soft white gradient at 8% drifting across once
            sweep = Image.new("L", page.size, 0); sd = ImageDraw.Draw(sweep)
            sx = -iw * 0.4 + (iw * 1.8) * p
            for k in range(-int(iw * 0.18), int(iw * 0.18), max(1, iw // 200)):
                v = int(255 * 0.08 * (1 - abs(k) / (iw * 0.18)))
                sd.line([(sx + k, 0), (sx + k - ih * 0.35, ih)], fill=v, width=max(1, iw // 200))
            page.alpha_composite(Image.merge("RGBA", [Image.new("L", page.size, 255)] * 3 + [sweep]))
            angle = a.angle
            rot = page.rotate(angle, resample=Image.BICUBIC, expand=True)
            shadow = Image.new("RGBA", rot.size, (0, 0, 0, 0))
            shadow.paste((0, 0, 0, 150), (0, 0, rot.width, rot.height), rot.split()[3])
            shadow = shadow.filter(ImageFilter.GaussianBlur(28 * scale))
            comp = frame.convert("RGBA")
            # camera drift toward the focus point, parallax: page moves a few px against its shadow
            cxp = W / 2 - rot.width * fx + (rot.width * 0.5 - rot.width * fx) * 0 - dx * rot.width * p
            cyp = H / 2 - rot.height * fy - dy * rot.height * p
            comp.alpha_composite(shadow, (int(cxp + 18 * scale), int(cyp + 26 * scale)))
            comp.alpha_composite(rot, (int(cxp + 3 * scale * p), int(cyp + 2 * scale * p)))
        label(comp, a.label, scale)
        comp.convert("RGB").save(os.path.join(out_dir, f"c_{i:05d}.png"))
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(out_dir, "c_%05d.png"),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], check=True)
    if a.keep: print("frames in", out_dir)
    else: shutil.rmtree(tmp, ignore_errors=True)
    print("wrote", a.out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["photo", "doc"], required=True)
    ap.add_argument("--in", dest="src", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--size", default="2160x3840"); ap.add_argument("--dur", type=float, default=3.0)
    ap.add_argument("--push", type=float, default=None, help="end scale; photo default 1.08, doc default 1.25")
    ap.add_argument("--focus", default=None, help="x,y fraction the camera pushes toward (default centre)")
    ap.add_argument("--drift", default=None, help="x,y fraction of camera drift over the shot")
    ap.add_argument("--angle", type=float, default=3.0, help="document rotation in degrees")
    ap.add_argument("--swipe", default=None, help="x,y,w,h fraction of the source: highlighter swipe box")
    ap.add_argument("--swipe-at", dest="swipe_at", type=float, default=0.5)
    ap.add_argument("--box", default=None, help="x,y,w,h fraction: highlight box, outside dims to 40%%")
    ap.add_argument("--box-at", dest="box_at", type=float, default=0.5)
    ap.add_argument("--label", default="")
    ap.add_argument("--grade", action="store_true", help="archive grade a document too")
    ap.add_argument("--grid", default=None, help="write a numbered grid PNG of the source and exit")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    if a.push is None: a.push = 1.08 if a.mode == "photo" else 1.25
    render(a)

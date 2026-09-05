#!/usr/bin/env python3
"""Contact sheet: every HO01 asset against its shot number, so the edit can be
checked before anything is cut. Videos are sampled at one second in; missing
assets get a placeholder tile with the sourcing note so the gaps are visible.

    python3 maria-sabina/build/tools/contact-sheet.py
    -> maria-sabina/exports/HO01_contact-sheet.png
"""
import csv, glob, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
A = os.path.join(ROOT, "maria-sabina", "assets")
E = os.path.join(ROOT, "maria-sabina", "exports")
FONTS = os.path.join(ROOT, "public", "fonts")
FFMPEG = next((p for p in [os.path.join(ROOT, "node_modules/@remotion/compositor-linux-x64-gnu/ffmpeg"), "ffmpeg"]
               if p == "ffmpeg" or os.path.exists(p)), "ffmpeg")

CREAM, AUB, VIOLET, INK60, LINE = "#FAF7F2", "#1A0B2E", "#7C3AED", (26, 11, 46, 153), (26, 11, 46, 40)

# shot, timecode, duration, type, title, expected asset (glob), placeholder note
SHOTS = [
    ("01", "0:00-0:07", "7s", "ARC", "Portrait, slow push 100-108%. Eyebrow overlay.", "HO01_01_ARC_*", "Real archive only. See SOURCES.csv (INAH / Commons / LIFE Picture Collection). Not retrievable from the build container."),
    ("02-04", "0:07-0:15", "8s", "MAP", "NY wide -> Sierra Mazateca, Huautla label.", "map-sequence/HO01_map_*", "Render with npm run ho01:map (2160x3840, 480 frames)"),
    ("05", "0:15-0:19", "4s", "AI", "Aerial, mountain ridges in cloud.", "HO01_05_AI_sierra-aerial*", "Generated on OpenArt. Run fetch-assets.sh ai"),
    ("06", "0:19-0:23", "4s", "AI/ARC", "1950s village, slow push.", "HO01_06_*", "Generated on OpenArt. Run fetch-assets.sh ai"),
    ("07", "0:23-0:26", "3s", "ARC", "LIFE cover, 13 May 1957. Slam cut.", "HO01_07_ARC_*", "Internet Archive scan. Run fetch-assets.sh life, crop cover. In copyright."),
    ("08", "0:26-0:28", "2s", "TXT", "Date card.", "HO01_08_TXT_*", "npm run ho01:cards"),
    ("09", "0:28-0:31", "3s", "ARC", "Spread, slow drift.", "HO01_09_ARC_*", "Internet Archive scan. Run fetch-assets.sh life, crop spread. In copyright."),
    ("10", "0:31-0:34", "3s", "ARC", "Push in on the village name. The turn.", "HO01_10_ARC_*", "Same scan, page with the village name. In copyright."),
    ("11", "0:34-0:37", "3s", "AI", "1960s bus on a mountain road.", "HO01_11_AI_*", "Generated on OpenArt. Run fetch-assets.sh ai"),
    ("12", "0:37-0:40", "3s", "AI", "1960s backpackers into a village.", "HO01_12_*", "Generated on OpenArt. Run fetch-assets.sh ai"),
    ("13", "0:40-0:42", "2s", "AI", "1960s police, village square.", "HO01_13_AI_*", "Generated on OpenArt. Run fetch-assets.sh ai"),
    ("14a", "0:42-0:44", "2s", "AI", "Dusk street, one lit doorway.", "HO01_14a_AI_*", "Generated on OpenArt. Run fetch-assets.sh ai"),
    ("14b", "0:44-0:46", "2s", "AI", "Burnt-out house.", "HO01_14b_AI_*", "Generated on OpenArt. Run fetch-assets.sh ai"),
    ("14c", "0:46-0:48", "2s", "AI", "Mountainside into fog.", "HO01_14c_AI_*", "Generated on OpenArt. Run fetch-assets.sh ai"),
    ("15", "0:48-0:53", "5s", "ARC", "Portrait again, wider, static.", "HO01_15_ARC_*", "Same source as shot 01, wider crop."),
    ("16", "0:53-0:55", "2s", "BLACK", "Full black, no logo.", None, "Nothing to build."),
    ("17", "0:55-1:00", "5s", "BRL", "Own macro footage. Lower third at 0:57.", "HO01_17_*", "Own footage only. Overlay: HO01_17_TXT_lower-third_alpha.mov"),
    ("18", "1:00-1:02", "2s", "TXT", "End card.", "HO01_18_TXT_*", "npm run ho01:cards"),
]

def font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, name), size)
    except OSError:
        return ImageFont.load_default()

def find(pattern):
    if not pattern:
        return []
    hits = []
    for base in (A, E):
        hits += glob.glob(os.path.join(base, pattern))
    # prefer stills/frames, then video; drop sequences down to a few frames
    hits = sorted(h for h in hits if os.path.isfile(h) and "_candidates" not in h)
    frames = [h for h in hits if h.endswith(".png") and "MAP_" in h]
    if frames:
        pick = [frames[i] for i in sorted({0, len(frames) // 3, (2 * len(frames)) // 3, len(frames) - 1})]
        return pick + [h for h in hits if h.endswith((".mp4", ".mov"))][:1]
    order = {".png": 0, ".jpg": 0, ".jpeg": 0, ".mp4": 1, ".mov": 1}
    return sorted(hits, key=lambda h: order.get(os.path.splitext(h)[1].lower(), 2))[:4]

def thumb(path, size):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".mp4", ".mov"):
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", "1", "-i", path, "-frames:v", "1", tmp], check=False)
        img = Image.open(tmp).convert("RGBA") if os.path.exists(tmp) and os.path.getsize(tmp) else None
    else:
        img = Image.open(path).convert("RGBA")
    if img is None:
        return None
    # transparent overlays get a dark card behind them so they read
    bg = Image.new("RGBA", img.size, AUB)
    bg.alpha_composite(img)
    img = bg
    img.thumbnail(size, Image.LANCZOS)
    return img

def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def main():
    cols, tile_w, tile_h, pad = 3, 400, 720, 28
    hdr = 150
    rows = (len(SHOTS) + cols - 1) // cols
    W = cols * (tile_w + pad) + pad
    Hh = hdr + rows * (tile_h + pad) + pad
    sheet = Image.new("RGBA", (W, Hh), CREAM)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 34), "HYPHA ORIGINS · 01 — MARÍA SABINA", font=font("BebasNeue-Regular.ttf", 64), fill=AUB)
    d.text((pad, 104), "CONTACT SHEET · 1080x1920 · 60 FPS · ASSETS AGAINST SHOT NUMBER", font=font("JetBrainsMono-VF.ttf", 18), fill=INK60)
    mono, mono_s, beb = font("JetBrainsMono-VF.ttf", 17), font("JetBrainsMono-VF.ttf", 14), font("BebasNeue-Regular.ttf", 44)
    for i, (shot, tc, dur, typ, title, pat, note) in enumerate(SHOTS):
        x = pad + (i % cols) * (tile_w + pad)
        y = hdr + (i // cols) * (tile_h + pad)
        d.rectangle([x, y, x + tile_w, y + tile_h], outline=LINE, width=2)
        d.text((x + 16, y + 10), shot, font=beb, fill=AUB)
        d.text((x + 16 + d.textlength(shot, font=beb) + 16, y + 26), f"{tc}  {dur}  {typ}", font=mono, fill=VIOLET)
        ty = y + 64
        for line in wrap(d, title, mono_s, tile_w - 32)[:2]:
            d.text((x + 16, ty), line, font=mono_s, fill=AUB); ty += 18
        box = (x + 16, y + 110, x + tile_w - 16, y + tile_h - 16)
        files = find(pat)
        if typ == "BLACK":
            d.rectangle(box, fill="#000000")
            continue
        if not files:
            d.rectangle(box, fill="#F0EAF7")
            ny = box[1] + 24
            d.text((box[0] + 16, ny), "NOT YET IN /assets", font=mono, fill=VIOLET); ny += 34
            for line in wrap(d, note, mono_s, tile_w - 64)[:9]:
                d.text((box[0] + 16, ny), line, font=mono_s, fill=AUB); ny += 19
            continue
        n = len(files)
        if n == 1:
            slots = [box]
        else:
            bw, bh = (box[2] - box[0]), (box[3] - box[1])
            slots = [(box[0] + (k % 2) * (bw // 2 + 4), box[1] + (k // 2) * (bh // 2 + 4),
                      box[0] + (k % 2) * (bw // 2 + 4) + bw // 2 - 4, box[1] + (k // 2) * (bh // 2 + 4) + bh // 2 - 4)
                     for k in range(min(n, 4))]
        for f, s in zip(files, slots):
            im = thumb(f, (s[2] - s[0], s[3] - s[1] - 22))
            if im is None:
                continue
            sheet.alpha_composite(im, (s[0] + ((s[2] - s[0]) - im.width) // 2, s[1]))
            d.text((s[0], s[3] - 18), os.path.basename(f)[:48], font=mono_s, fill=INK60)
    out = os.path.join(E, "HO01_contact-sheet.png")
    sheet.convert("RGB").save(out, optimize=True)
    print("wrote", out)

if __name__ == "__main__":
    main()

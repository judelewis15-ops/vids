#!/usr/bin/env python3
"""Contact sheet for HYPHA ORIGINS 01, built from the master brief v6 shot list.
Every shot 01-18 gets a tile. A tile shows the asset if one is in assets/ or
exports/; otherwise it says what is missing and why, taken from SOURCES.csv
(rows whose `retrieved` is NEEDS_MANUAL or similar).

    python3 maria-sabina/build/tools/contact-sheet.py
    -> maria-sabina/exports/contact-sheet.png
"""
import csv, glob, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MS = os.path.join(ROOT, "maria-sabina")
A, E, WORK = os.path.join(MS, "assets"), os.path.join(MS, "exports"), os.path.join(MS, "work")
FFMPEG = next((p for p in [os.path.join(ROOT, "node_modules/@remotion/compositor-linux-x64-gnu/ffmpeg"), "ffmpeg"]
               if p == "ffmpeg" or os.path.exists(p)), "ffmpeg")
CREAM, AUB, VIOLET = "#FAF7F2", "#1A0B2E", "#7C3AED"
INK60, LINE, YELLOW = (26, 11, 46, 153), (26, 11, 46, 40), "#F5D90A"

# shot, timecode, dur, type, mode, title, asset glob(s)
SHOTS = [
    ("01", "0:00-0:07", "7s", "PHOTO", "FULL BLEED", "Portrait of María Sabina, 2.5D slow push. Eyebrow at 0:01.", ["HO01_01_PHOTO_*"]),
    ("02", "0:07-0:09", "2s", "MAP", "STACKED", "Map clip start. Wide North America, marker at New York.", ["map/HO01_02_MAP_start.*", "map/HO01_02-03_MAP_zoom.*"]),
    ("03", "0:09-0:12", "3s", "MAP", "STACKED", "Zoom continues, arc draws toward Oaxaca.", ["map/HO01_03_MAP_end.*", "map/HO01_02-03_MAP_zoom.*"]),
    ("04", "0:12-0:15", "3s", "SAT", "FULL BLEED", "Google Earth Studio satellite, match cut, lands on Huautla.", ["HO01_04_SAT_*", "satellite/*.png"]),
    ("05", "0:15-0:21", "6s", "STOCK", "FULL BLEED", "Real drone, Sierra Mazateca or Oaxaca highlands, cloud in valleys.", ["HO01_05_STOCK_*"]),
    ("06", "0:21-0:25", "4s", "PHOTO", "FULL BLEED", "Allan Richardson's 1955 ceremony photographs (Life). Slow push.", ["HO01_06_PHOTO_*"]),
    ("07", "0:25-0:28", "3s", "DOC", "STACKED", "Life cover, 13 May 1957. Whip zoom from black, one white frame.", ["HO01_07_DOC_*"]),
    ("08", "0:28-0:30", "2s", "DOC", "FULL BLEED", "Tight on the masthead date. Yellow highlighter swipe, 400ms.", ["HO01_08_DOC_*", "HO01_07_DOC_*"]),
    ("09", "0:30-0:33", "3s", "DOC", "FULL BLEED", "Spread punched into one column. Highlight box on the false-name passage.", ["HO01_09_DOC_*"]),
    ("10", "0:33-0:36", "3s", "DOC", "FULL BLEED", "Tight on the printed village name. Yellow swipe. Hold a beat too long.", ["HO01_10_DOC_*"]),
    ("11", "0:36-0:39", "3s", "DOC", "STACKED", "Five or six clippings fan out, late-1960s coverage. One pulls forward.", ["HO01_11_DOC_*"]),
    ("12", "0:39-0:42", "3s", "PHOTO", "FULL BLEED", "Archive photo of foreign visitors in Huautla, 1960s-70s. 2.5D push.", ["HO01_12_PHOTO_*"]),
    ("13", "0:42-0:44", "2s", "DOC", "FULL BLEED", "Clipping on the army or police closing the town, 1969-70.", ["HO01_13_DOC_*"]),
    ("14", "0:44-0:51", "7s", "PHOTO x3", "FULL BLEED", "Later-life stills, three, 2.5D, held long. Echevarría 1979 primary.", ["HO01_14*_PHOTO_*"]),
    ("15", "0:51-0:56", "5s", "TEXT/PHOTO", "FULL BLEED", "Last still dimmed to 30%. Her words typewriter in. Estrada book cover as source.", ["HO01_15_PHOTO_*", "HO01_15_DOC_*"]),
    ("16", "0:56-0:59", "3s", "PTC", "PTC FULL", "Jude, full frame. Death line. No graphics.", ["HO01_16_PTC_*"]),
    ("17", "0:59-1:03", "4s", "DOC", "STACKED", "Vendor listings and forum screenshots fan out. Names, prices, species blurred.", ["HO01_17_DOC_*"]),
    ("18", "1:03-1:05", "2s", "PTC", "PTC FULL", "Jude. Hard cut to black on the last syllable. Nothing after.", ["HO01_18_PTC_*"]),
]

def font(name, size):
    for p in [os.path.join(MS, "build", "fonts", name), os.path.join(ROOT, "public", "fonts", name),
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()

def sources():
    """shot -> list of (filename, retrieved, source_url, publication) from SOURCES.csv"""
    out = {}
    p = os.path.join(A, "SOURCES.csv")
    if not os.path.exists(p):
        return out
    for r in csv.DictReader(open(p, encoding="utf-8")):
        for s in str(r.get("shot", "")).replace(";", ",").split(","):
            s = s.strip()
            if s:
                out.setdefault(s, []).append(r)
    return out

def find(globs):
    hits = []
    for g in globs:
        for base in (A, E, WORK):
            hits += glob.glob(os.path.join(base, g))
    hits = sorted({h for h in hits if os.path.isfile(h)})
    order = {".png": 0, ".jpg": 0, ".jpeg": 0, ".webp": 0, ".tif": 0, ".mp4": 1, ".mov": 1}
    return sorted(hits, key=lambda h: order.get(os.path.splitext(h)[1].lower(), 2))[:4]

def thumb(path, size):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".mp4", ".mov"):
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", "1", "-i", path, "-frames:v", "1", tmp], check=False)
        if not (os.path.exists(tmp) and os.path.getsize(tmp)):
            return None
        img = Image.open(tmp).convert("RGBA")
    else:
        img = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", img.size, AUB); bg.alpha_composite(img); img = bg
    img.thumbnail(size, Image.LANCZOS)
    return img

def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for w in text.split():
        # a single token wider than the tile (a URL) is broken by character
        while d.textlength(w, font=fnt) > width:
            k = len(w)
            while k > 1 and d.textlength(w[:k], font=fnt) > width: k -= 1
            if cur: lines.append(cur); cur = ""
            lines.append(w[:k]); w = w[k:]
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def main():
    cols, tw, th, pad, hdr = 3, 420, 640, 26, 150
    rows = (len(SHOTS) + cols - 1) // cols
    W, H = cols * (tw + pad) + pad, hdr + rows * (th + pad) + pad
    sheet = Image.new("RGBA", (W, H), CREAM); d = ImageDraw.Draw(sheet)
    d.text((pad, 30), "HYPHA ORIGINS · 01 — MARÍA SABINA", font=font("BebasNeue-Regular.ttf", 60), fill=AUB)
    d.text((pad, 100), "CONTACT SHEET · MASTER BRIEF V6 · 9:16 2160x3840 60FPS · EVERY SHOT AGAINST ITS ASSET", font=font("JetBrainsMono-VF.ttf", 16), fill=INK60)
    mono, mono_s, beb = font("JetBrainsMono-VF.ttf", 16), font("JetBrainsMono-VF.ttf", 13), font("BebasNeue-Regular.ttf", 42)
    src = sources()
    for i, (shot, tc, dur, typ, mode, title, globs) in enumerate(SHOTS):
        x, y = pad + (i % cols) * (tw + pad), hdr + (i // cols) * (th + pad)
        d.rectangle([x, y, x + tw, y + th], outline=LINE, width=2)
        d.text((x + 14, y + 8), shot, font=beb, fill=AUB)
        d.text((x + 14 + d.textlength(shot, font=beb) + 14, y + 22), f"{tc}  {dur}  {typ}", font=mono, fill=VIOLET)
        d.text((x + 14, y + 52), mode, font=mono_s, fill=INK60)
        ty = y + 72
        for line in wrap(d, title, mono_s, tw - 28)[:3]:
            d.text((x + 14, ty), line, font=mono_s, fill=AUB); ty += 17
        box = (x + 14, y + 128, x + tw - 14, y + th - 14)
        if typ == "PTC":
            d.rectangle(box, fill="#12081F")
            d.text((box[0] + 14, box[1] + 14), "PIECE TO CAMERA", font=mono, fill=CREAM)
            d.text((box[0] + 14, box[1] + 40), "Shot by Jude. Not an asset.", font=mono_s, fill=(250, 247, 242, 160))
            continue
        files = find(globs)
        if files:
            n = len(files)
            bw, bh = box[2] - box[0], box[3] - box[1]
            slots = [box] if n == 1 else [(box[0] + (k % 2) * (bw // 2 + 4), box[1] + (k // 2) * (bh // 2 + 4),
                                            box[0] + (k % 2) * (bw // 2 + 4) + bw // 2 - 4, box[1] + (k // 2) * (bh // 2 + 4) + bh // 2 - 4)
                                           for k in range(min(n, 4))]
            for f, s in zip(files, slots):
                im = thumb(f, (s[2] - s[0], s[3] - s[1] - 20))
                if im is None: continue
                sheet.alpha_composite(im, (s[0] + ((s[2] - s[0]) - im.width) // 2, s[1]))
                d.text((s[0], s[3] - 16), os.path.basename(f)[:46], font=mono_s, fill=INK60)
            continue
        # missing: say what and why, from the sources log
        d.rectangle(box, fill="#F1ECF8")
        ny = box[1] + 12
        d.text((box[0] + 12, ny), "NOT IN /assets", font=mono, fill=VIOLET); ny += 26
        rows_ = src.get(shot, [])
        if not rows_:
            for line in wrap(d, "No source logged yet.", mono_s, tw - 56)[:2]:
                d.text((box[0] + 12, ny), line, font=mono_s, fill=AUB); ny += 16
        for r in rows_[:4]:
            status = (r.get("retrieved") or "").strip() or "?"
            head = f"{status}: {r.get('publication','')}".strip()
            for line in wrap(d, head, mono_s, tw - 56)[:2]:
                d.text((box[0] + 12, ny), line, font=mono_s, fill=AUB); ny += 16
            for line in wrap(d, (r.get("source_url") or "")[:120], mono_s, tw - 56)[:2]:
                d.text((box[0] + 12, ny), line, font=mono_s, fill=INK60); ny += 15
            ny += 6
            if ny > box[3] - 30: break
    out = os.path.join(E, "contact-sheet.png")
    sheet.convert("RGB").save(out, optimize=True)
    print("wrote", out)

if __name__ == "__main__":
    main()

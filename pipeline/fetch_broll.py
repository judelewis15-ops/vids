#!/usr/bin/env python3
"""Download the clips in a b-roll manifest into public/<src>. Skips files already present.
Usage: python3 pipeline/fetch_broll.py scripts/02-ochra/broll.json
Needs network access to cdn.openart.ai (blocked in some Claude Code web environments;
run locally or allow the domain in the environment's network policy)."""
import json, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads(Path(sys.argv[1]).read_text())
ok = fail = 0
for c in manifest["clips"]:
    dst = ROOT / "public" / c["src"]
    if dst.exists():
        ok += 1
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(c["url"], dst)
        print("fetched", c["src"])
        ok += 1
    except Exception as e:  # noqa: BLE001
        print("FAILED", c["src"], e)
        fail += 1
print(f"{ok} present, {fail} failed")
sys.exit(1 if fail else 0)

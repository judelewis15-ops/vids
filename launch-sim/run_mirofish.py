#!/usr/bin/env python3
"""Drive a full MiroFish run headlessly against a local backend.

Usage:
    python3 run_mirofish.py --seed seed.md --question question.txt [--rounds 30]

Expects the MiroFish backend on http://localhost:5001 (``npm run backend`` in
the MiroFish checkout). Steps: ontology -> graph build -> simulation create ->
prepare personas -> run -> report. Writes the report to ./out/.
"""

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

API = os.environ.get("MIROFISH_API", "http://localhost:5001/api")
HEADERS = {"Accept-Language": "en"}


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = dict(HEADERS)
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> HTTP {e.code}: {e.read().decode()[:2000]}")
    if not payload.get("success", False):
        sys.exit(f"{method} {path} failed: {json.dumps(payload)[:2000]}")
    return payload["data"]


def upload(path, fields, files):
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        )
    for fp in files:
        ctype = mimetypes.guess_type(fp)[0] or "text/plain"
        with open(fp, "rb") as f:
            content = f.read()
        parts.append(
            (
                f'--{boundary}\r\nContent-Disposition: form-data; name="files"; '
                f'filename="{os.path.basename(fp)}"\r\nContent-Type: {ctype}\r\n\r\n'
            ).encode()
            + content
            + b"\r\n"
        )
    parts.append(f"--{boundary}--\r\n".encode())
    headers = dict(HEADERS)
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(API + path, data=b"".join(parts), method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=1800) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"POST {path} -> HTTP {e.code}: {e.read().decode()[:2000]}")
    if not payload.get("success", False):
        sys.exit(f"POST {path} failed: {json.dumps(payload)[:2000]}")
    return payload["data"]


def wait(label, poll, done, failed, every=10):
    last = None
    while True:
        d = poll()
        msg = f"{label}: {d.get('status') or d.get('runner_status')} {d.get('progress', d.get('progress_percent', ''))} {d.get('message', '')}"
        if msg != last:
            print(msg, flush=True)
            last = msg
        if failed(d):
            sys.exit(f"{label} failed: {json.dumps(d)[:2000]}")
        if done(d):
            return d
        time.sleep(every)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", nargs="+", required=True, help="seed files (md/txt/pdf)")
    ap.add_argument("--question", required=True, help="file with the prediction question")
    ap.add_argument("--name", default="Hypha app launch")
    ap.add_argument("--rounds", type=int, default=30, help="cap on simulation rounds")
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    with open(args.question, encoding="utf-8") as f:
        question = f.read().strip()
    os.makedirs(args.out, exist_ok=True)

    print("1/6 Generating ontology from seed...", flush=True)
    onto = upload(
        "/graph/ontology/generate",
        {"simulation_requirement": question, "project_name": args.name},
        args.seed,
    )
    project_id = onto["project_id"]
    print(f"    project {project_id}", flush=True)

    print("2/6 Building knowledge graph (Zep)...", flush=True)
    build = call("POST", "/graph/build", {"project_id": project_id})
    wait(
        "    graph",
        lambda: call("GET", f"/graph/task/{build['task_id']}"),
        lambda d: d["status"] == "completed",
        lambda d: d["status"] == "failed",
    )

    print("3/6 Creating simulation...", flush=True)
    sim = call("POST", "/simulation/create", {"project_id": project_id})
    sim_id = sim["simulation_id"]
    print(f"    simulation {sim_id}", flush=True)

    print("4/6 Generating personas and config...", flush=True)
    prep = call("POST", "/simulation/prepare", {"simulation_id": sim_id})
    if not prep.get("already_prepared"):
        wait(
            "    prepare",
            lambda: call(
                "POST",
                "/simulation/prepare/status",
                {"task_id": prep.get("task_id"), "simulation_id": sim_id},
            ),
            lambda d: d.get("status") in ("completed", "ready") or d.get("already_prepared"),
            lambda d: d.get("status") == "failed",
        )

    print(f"5/6 Running simulation (max {args.rounds} rounds)...", flush=True)
    call("POST", "/simulation/start", {"simulation_id": sim_id, "max_rounds": args.rounds})
    wait(
        "    run",
        lambda: call("GET", f"/simulation/{sim_id}/run-status"),
        lambda d: d.get("runner_status") in ("completed", "stopped"),
        lambda d: d.get("runner_status") == "failed",
        every=20,
    )

    print("6/6 Writing report...", flush=True)
    rep = call("POST", "/report/generate", {"simulation_id": sim_id})
    wait(
        "    report",
        lambda: call(
            "POST",
            "/report/generate/status",
            {"task_id": rep.get("task_id"), "simulation_id": sim_id},
        ),
        lambda d: d.get("status") == "completed",
        lambda d: d.get("status") == "failed",
    )
    report = call("GET", f"/report/by-simulation/{sim_id}")
    with open(os.path.join(args.out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    md = report.get("markdown_content") or report.get("content") or ""
    if md:
        with open(os.path.join(args.out, "report.md"), "w", encoding="utf-8") as f:
            f.write(md)
    print(f"Done. Simulation {sim_id}; report in {args.out}/", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Copy finished eval work into evals/runs/<case>/ and re-verify each final page independently.

Usage: python3 evals/collect.py <work-root> [case-id ...]
<work-root>/<case>/ holds shot.png, index.html, assets/ and .verify/round-N/ from the agent's run
(React cases: app/, a Vite project, instead of index.html). Naming case ids re-collects only those
and keeps the other entries in results.json.
Writes evals/runs/<case>/ and evals/results.json. The table in RESULTS.md is written by hand from results.json.
"""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

EVALS = Path(__file__).resolve().parent
S2C = EVALS.parent / "plugins/shotproof/skills/shotproof/scripts/s2c.py"
REACT_PORT = 8791


def main(work_root: str, only: list[str]) -> int:
    old = {r["case"]: r for r in json.loads((EVALS / "results.json").read_text())} if only else {}
    results = []
    for case in json.loads((EVALS / "cases.json").read_text()):
        cid, work = case["id"], Path(work_root) / case["id"]
        if only and cid not in only:
            if cid in old:
                results.append(old[cid])
            continue
        dest = EVALS / "runs" / cid
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        server = None
        if case["kind"] == "react":
            # keep the agent's source; build it and serve the build on loopback for the re-check
            shutil.copytree(work / "app/src", dest / "src")
            subprocess.run(["npm", "run", "build"], cwd=work / "app", check=True, capture_output=True)
            server = subprocess.Popen([sys.executable, "-m", "http.server", str(REACT_PORT), "--bind", "127.0.0.1",
                                       "--directory", str(work / "app/dist")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
            page = f"http://127.0.0.1:{REACT_PORT}/"
        elif not (work / "index.html").is_file():
            results.append({"case": cid, "error": "no index.html"})
            continue
        else:
            shutil.copy2(work / "index.html", dest / "index.html")
            page = str(dest / "index.html")
        if (work / "assets").is_dir():
            shutil.copytree(work / "assets", dest / "assets")
        rounds = sorted((work / ".verify").glob("round-*"), key=lambda p: int(p.name.split("-")[1]))
        scores = []
        for r in rounds:
            if (r / "verify.json").is_file():
                v = json.loads((r / "verify.json").read_text())
                scores.append(v["ssim"])
                v.pop("files", None)  # absolute machine paths
                (dest / "rounds").mkdir(exist_ok=True)
                (dest / "rounds" / f"{r.name}.json").write_text(json.dumps(v, indent=1))
        # independent re-check of the final page, never trusting the agent's own numbers
        shot = EVALS / "fixtures/screens" / f"{cid}.png"
        cmd = [sys.executable, str(S2C), "verify", str(shot), page, "--out-dir", str(dest / "final"),
               "--dpr", str(case["dpr"]), "--threshold", str(case["threshold"])]
        if case["kind"] == "public":
            cmd.append("--offline")
        out = subprocess.run(cmd, capture_output=True, text=True)
        if server:
            server.terminate()
        final = json.loads(out.stdout)
        final.pop("files", None)
        (dest / "final" / "verify.json").write_text(json.dumps(final, indent=1))
        for name in ("render.png", "page-snapshot.html"):  # side-by-side already holds the render
            (dest / "final" / name).unlink(missing_ok=True)
        proof = None
        if server is None and "data-private-proof" in (dest / "index.html").read_text():
            p = subprocess.run(["python3", str(S2C), "proof-check", str(dest / "index.html")], capture_output=True, text=True)
            proof = json.loads(p.stdout)["passed"]
        results.append({
            "case": cid, "kind": case["kind"], "threshold": case["threshold"],
            "round1_ssim": scores[0] if scores else None, "agent_final_ssim": scores[-1] if scores else None,
            "rounds": len(scores), "recheck_ssim": final["ssim"], "recheck_passed": final["passed"],
            "console_errors": len(final["console_errors"]) + len(final["page_errors"]),
            "failed_requests": len(final["failed_requests"]), "external_requests": len(final["external_requests"]),
            "proof_check_passed": proof,
        })
    (EVALS / "results.json").write_text(json.dumps(results, indent=1))
    for r in results:
        print(json.dumps(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2:]))

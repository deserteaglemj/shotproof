#!/usr/bin/env python3
"""shotproof helper: render, compare, crop and private-proof checks.

Uses only what is already on the Mac: Python Playwright (Chromium), Pillow and numpy.
No model calls, no network except what a page you render asks for.

  s2c.py render  PAGE --out shot.png --width 1280 --height 800 [--dpr 1]
  s2c.py verify  REF.png PAGE --out-dir DIR [--dpr 1] [--offline] [--threshold 0.9]
  s2c.py crop    REF.png --box x,y,w,h --out assets/logo.png
  s2c.py palette REF.png [--at 10,20 300,40]
  s2c.py proof-check page.html

PAGE is a local .html path or an http(s)://127.0.0.1 / localhost URL.
"""

from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    sys.exit(f"s2c needs Pillow and numpy for python3: {exc}")

LOCAL_HOSTS = ("127.0.0.1", "localhost", "[::1]")


# ---------- rendering ----------

def page_url(page: str) -> str:
    if re.match(r"(?i)^https?://", page):
        return page
    path = Path(page).expanduser().resolve()
    if not path.is_file():
        sys.exit(f"no such page: {path}")
    return path.as_uri()


def render(page: str, out: Path, width: int, height: int, dpr: float = 1.0,
           offline: bool = False, viewport_height: int | None = None) -> dict:
    """Screenshot PAGE at a CSS viewport of width x height. Returns console/network findings."""
    from playwright.sync_api import sync_playwright

    url = page_url(page)
    findings = {"console_errors": [], "page_errors": [], "failed_requests": [], "external_requests": []}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": width, "height": viewport_height or height},
                                  device_scale_factor=dpr)
        pg = ctx.new_page()
        def on_console(m):
            if m.type == "error":
                findings["console_errors"].append(m.text)

        pg.on("console", on_console)
        pg.on("pageerror", lambda e: findings["page_errors"].append(str(e)))
        pg.on("requestfailed", lambda r: findings["failed_requests"].append(r.url))

        def route(r):
            u = r.request.url
            local = u.startswith(("file:", "data:", "blob:", "about:")) or any(
                re.match(rf"(?i)^https?://{re.escape(h)}(:\d+)?/", u) for h in LOCAL_HOSTS)
            if not local:
                findings["external_requests"].append(u)
                if offline:
                    return r.abort()
            return r.continue_()

        pg.route("**/*", route)
        pg.goto(url, wait_until="load")
        try:
            pg.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        pg.evaluate("document.fonts ? document.fonts.ready.then(() => true) : true")
        pg.wait_for_timeout(300)
        out.parent.mkdir(parents=True, exist_ok=True)
        if viewport_height and viewport_height != height:
            pg.screenshot(path=str(out), full_page=True, clip={"x": 0, "y": 0, "width": width, "height": height})
        else:
            pg.screenshot(path=str(out))
        browser.close()
    if offline:
        # aborted external requests also show up as failed; keep one list
        findings["failed_requests"] = [u for u in findings["failed_requests"] if u not in findings["external_requests"]]
    return findings


# ---------- scoring ----------

def _box_mean(a: np.ndarray, k: int) -> np.ndarray:
    """Mean over k x k windows (valid region) via an integral image."""
    c = np.pad(a, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def ssim_map(x: np.ndarray, y: np.ndarray, k: int = 7) -> np.ndarray:
    """Grayscale SSIM with a uniform k x k window (Wang et al. 2004 constants)."""
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mx, my = _box_mean(x, k), _box_mean(y, k)
    vx = _box_mean(x * x, k) - mx * mx
    vy = _box_mean(y * y, k) - my * my
    cov = _box_mean(x * y, k) - mx * my
    return ((2 * mx * my + c1) * (2 * cov + c2)) / ((mx * mx + my * my + c1) * (vx + vy + c2))


def band_shifts(ref: np.ndarray, cand: np.ndarray, bands: int = 8, max_shift: int = 40) -> list[int]:
    """Per band, the vertical offset (px) that best aligns the candidate's row profile with the reference.
    Positive means the candidate's content sits lower than the reference."""
    prof = lambda m: m.std(axis=1)  # rows with text or edges have high spread
    pr, pc = prof(ref), prof(cand)
    h, out = len(pr), []
    for i in range(bands):
        lo, hi = i * h // bands, (i + 1) * h // bands
        seg = pr[lo:hi] - pr[lo:hi].mean()
        best, best_err = 0, None
        for d in range(-max_shift, max_shift + 1):
            if lo + d < 0 or hi + d > h:
                continue
            err = float(np.abs(seg - (pc[lo + d:hi + d] - pc[lo + d:hi + d].mean())).mean())
            if best_err is None or err < best_err - 1e-9 or (abs(err - best_err) < 1e-9 and abs(d) < abs(best)):
                best, best_err = d, err
        out.append(best)
    return out


def compare(ref_path: Path, cand_path: Path, bands: int = 8) -> dict:
    ref = Image.open(ref_path).convert("RGB")
    cand = Image.open(cand_path).convert("RGB")
    resized = cand.size != ref.size
    if resized:
        cand = cand.resize(ref.size, Image.Resampling.LANCZOS)
    a = np.asarray(ref, dtype=np.float64)
    b = np.asarray(cand, dtype=np.float64)
    gray = lambda m: m @ np.array([0.299, 0.587, 0.114])
    smap = ssim_map(gray(a), gray(b))
    diff = np.abs(a - b).max(axis=2)
    h = smap.shape[0]
    band_scores = []
    for i in range(bands):
        lo, hi = i * h // bands, (i + 1) * h // bands
        if hi > lo:
            band_scores.append(round(float(smap[lo:hi].mean()), 4))
    return {
        "ssim": round(float(smap.mean()), 4),
        "band_shift_px": band_shifts(gray(a), gray(b), bands),
        "pixel_match": round(float((diff <= 16).mean()), 4),
        "mean_color_delta": round(float(np.abs(a - b).mean()), 2),
        "band_ssim_top_to_bottom": band_scores,
        "size_ref": list(ref.size),
        "size_candidate": list(Image.open(cand_path).size),
        "candidate_resized": resized,
        "_diff": diff,
        "_ref": ref,
        "_cand": cand,
    }


def write_visuals(result: dict, out_dir: Path) -> None:
    ref, cand, diff = result["_ref"], result["_cand"], result["_diff"]
    w, h = ref.size
    side = Image.new("RGB", (w * 2 + 16, h), "white")
    side.paste(ref, (0, 0))
    side.paste(cand, (w + 16, 0))
    side.save(out_dir / "side-by-side.png")
    heat = np.zeros((h, w, 3), dtype=np.uint8)
    heat[..., 0] = np.clip(diff * 2, 0, 255).astype(np.uint8)
    base = np.asarray(ref.convert("L"), dtype=np.uint8) // 3
    heat[..., 1] = base
    heat[..., 2] = base
    Image.fromarray(heat).save(out_dir / "diff.png")


# ---------- private proof contract ----------

EXTERNAL_URI = re.compile(r"(?i)^\s*(?:[a-z][a-z0-9+.-]*:|//)")
URI_ATTR = re.compile(r"""(?is)\b(?:href|src|action|srcset|poster|xlink:href|formaction|data)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""")
CSS_URL = re.compile(r"""(?is)url\(\s*(?:"([^"]*)"|'([^']*)'|([^)]*))\s*\)""")
BANNED_TAG = re.compile(r"(?is)<\s*(script|iframe|frame|object|embed|form|base|link|portal|applet)\b")
EVENT_ATTR = re.compile(r"(?i)[\s\"'/]on[a-z]+\s*=")
META_REFRESH = re.compile(r"(?is)<meta\b[^>]*http-equiv\s*=\s*['\"]?refresh")
ROBOTS = re.compile(r"""(?is)<meta\s+name\s*=\s*["']robots["']\s+content\s*=\s*["']noindex,\s*nofollow["']""")
BANNER = re.compile(r"(?is)<[a-z]+\b[^>]*\bdata-private-proof\b")


def proof_problems(doc: str) -> list[str]:
    """Return every way DOC breaks the private client-proof contract (empty list = pass)."""
    problems = []
    decoded = htmllib.unescape(doc)
    if not ROBOTS.search(doc):
        problems.append('missing <meta name="robots" content="noindex,nofollow">')
    if not BANNER.search(doc):
        problems.append("missing visible private banner element with data-private-proof")
    if m := BANNED_TAG.search(decoded):
        problems.append(f"active or remote-capable tag <{m.group(1).lower()}>")
    if EVENT_ATTR.search(re.sub(r"(?is)<style\b.*?</style>", "", decoded)):
        problems.append("inline event handler attribute (on...=)")
    if META_REFRESH.search(decoded):
        problems.append("meta refresh redirect")
    if re.search(r"(?i)@import\b", decoded):
        problems.append("CSS @import")
    if re.search(r"\\[0-9a-fA-F]{1,6}", decoded):
        problems.append("CSS escape sequence (can hide URLs)")
    if re.search(r"(?i)javascript\s*:", decoded):
        problems.append("javascript: URI")
    for rx in (URI_ATTR, CSS_URL):
        for m in rx.finditer(decoded):
            value = re.sub(r"[\x00-\x20]+", "", next(g for g in m.groups() if g is not None))
            if not value or value.startswith("#"):
                continue
            parts = [s.strip().split(" ")[0] for s in value.split(",")] if "srcset" in m.group(0).lower() else [value]
            for v in parts:
                if EXTERNAL_URI.search(v):
                    problems.append(f"non-relative URI: {v[:80]}")
                elif v.startswith("/") or ".." in v.split("/"):
                    problems.append(f"URI leaves the proof folder: {v[:80]}")
    if "$" in decoded:
        problems.append("dollar sign (no price or money claims in proofs)")
    return sorted(set(problems))


# ---------- commands ----------

def cmd_render(args) -> int:
    f = render(args.page, Path(args.out), args.width, args.height, args.dpr, args.offline)
    print(json.dumps({"out": args.out, **f}, indent=1))
    return 0


def cmd_verify(args) -> int:
    ref = Path(args.ref)
    if not ref.is_file():
        sys.exit(f"no such screenshot: {ref}")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    w_px, h_px = Image.open(ref).size
    width, height = round(w_px / args.dpr), round(h_px / args.dpr)
    shot = out_dir / "render.png"
    findings = render(args.page, shot, width, height, args.dpr, args.offline, args.viewport_height)
    result = compare(ref, shot)
    write_visuals(result, out_dir)
    report = {k: v for k, v in result.items() if not k.startswith("_")}
    report.update(findings)
    report["viewport_css"] = [width, args.viewport_height or height]
    report["dpr"] = args.dpr
    report["threshold"] = args.threshold
    clean = not (findings["console_errors"] or findings["page_errors"] or findings["failed_requests"])
    report["passed"] = bool(report["ssim"] >= args.threshold and clean)
    worst = sorted(range(len(report["band_ssim_top_to_bottom"])), key=lambda i: report["band_ssim_top_to_bottom"][i])[:3]
    report["worst_bands"] = [f"band {i + 1}/{len(report['band_ssim_top_to_bottom'])} (y {i * h_px // 8}-{(i + 1) * h_px // 8}px)" for i in worst]
    report["files"] = {n: str(out_dir / n) for n in ("render.png", "side-by-side.png", "diff.png")}
    (out_dir / "verify.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0 if report["passed"] else 1


def cmd_crop(args) -> int:
    x, y, w, h = (int(v) for v in args.box.split(","))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.open(args.ref).crop((x, y, x + w, y + h)).save(out)
    print(out)
    return 0


def cmd_palette(args) -> int:
    img = Image.open(args.ref).convert("RGB")
    hexc = lambda c: "#%02x%02x%02x" % tuple(c)
    out = {}
    if args.at:
        px = np.asarray(img)
        for p in args.at:
            x, y = (int(v) for v in p.split(","))
            if not (0 <= x < img.width and 0 <= y < img.height):
                sys.exit(f"--at {p} is outside the {img.width}x{img.height} image (x 0-{img.width - 1}, y 0-{img.height - 1})")
        out["samples"] = {p: hexc(px[int(p.split(",")[1]), int(p.split(",")[0])]) for p in args.at}
    q = img.quantize(colors=args.colors, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette() or []
    idx = np.asarray(q).ravel()
    counts = np.bincount(idx, minlength=args.colors)
    total = idx.size
    out["dominant"] = [{"hex": hexc(pal[i * 3:i * 3 + 3]), "share": round(int(counts[i]) / total, 3)}
                       for i in np.argsort(-counts) if counts[i]]
    print(json.dumps(out, indent=1))
    return 0


def cmd_proof_check(args) -> int:
    problems = proof_problems(Path(args.page).read_text(encoding="utf-8"))
    print(json.dumps({"page": args.page, "passed": not problems, "problems": problems}, indent=1))
    return 0 if not problems else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="screenshot a page at a viewport")
    r.add_argument("page")
    r.add_argument("--out", required=True)
    r.add_argument("--width", type=int, default=1280)
    r.add_argument("--height", type=int, default=800)
    r.add_argument("--dpr", type=float, default=1.0)
    r.add_argument("--offline", action="store_true", help="block every non-local request")
    r.set_defaults(fn=cmd_render)

    v = sub.add_parser("verify", help="render PAGE at REF's size and score it against REF")
    v.add_argument("ref")
    v.add_argument("page")
    v.add_argument("--out-dir", required=True)
    v.add_argument("--dpr", type=float, default=1.0, help="device pixel ratio of REF (2 for most Mac screenshots)")
    v.add_argument("--viewport-height", type=int, help="CSS viewport height when REF is a tall full-page capture")
    v.add_argument("--threshold", type=float, default=0.90, help="SSIM needed to pass (default 0.90)")
    v.add_argument("--offline", action="store_true", help="block every non-local request")
    v.set_defaults(fn=cmd_verify)

    c = sub.add_parser("crop", help="cut a region (logo, photo) out of REF as a local asset")
    c.add_argument("ref")
    c.add_argument("--box", required=True, help="x,y,w,h in screenshot pixels")
    c.add_argument("--out", required=True)
    c.set_defaults(fn=cmd_crop)

    pl = sub.add_parser("palette", help="dominant colors of REF, plus exact pixels with --at x,y")
    pl.add_argument("ref")
    pl.add_argument("--colors", type=int, default=12)
    pl.add_argument("--at", nargs="*", help="x,y points to sample exactly")
    pl.set_defaults(fn=cmd_palette)

    pc = sub.add_parser("proof-check", help="check an HTML file against the private client-proof contract")
    pc.add_argument("page")
    pc.set_defaults(fn=cmd_proof_check)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())

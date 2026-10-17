#!/usr/bin/env python3
"""Regenerate README assets from eval results: scores.svg and the before/after gallery.

Run from the repo root: python3 assets/make_assets.py
"""

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
LABELS = {
    "01-saas-landing": "Landing page",
    "02-pricing": "Pricing (dark)",
    "03-dashboard": "Dashboard",
    "04-mobile-login": "Mobile login, 2x",
    "05-article": "Serif article",
    "06-hacker-news": "Hacker News",
    "07-gov-uk": "GOV.UK (proof mode)",
}


def scores_svg(results: list[dict]) -> str:
    # Dumbbell chart: first build -> final, per case, with each case's pass line.
    lo, hi = 0.70, 1.00
    left, right, top, row = 190, 820, 92, 46
    width, height = 900, top + row * len(results) + 56
    x = lambda v: left + (v - lo) / (hi - lo) * (right - left)
    out = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="t d">
<title id="t">Eval scores: first build vs after the fix loop</title>
<desc id="d">SSIM per eval case. Every case improves after the render-compare-fix loop and ends above its pass line.</desc>
<style>
  .bg{{fill:#fcfcfb;stroke:#e6e4df}} .ink{{fill:#1d1d1b}} .muted{{fill:#6b6a66}} .grid{{stroke:#e6e4df}} .pass{{stroke:#1d1d1b}}
  .first{{fill:#c9691c}} .final{{fill:#5b4ff0}} .link{{stroke:#b9b6ae}} .ring{{stroke:#fcfcfb}}
  text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
  @media (prefers-color-scheme: dark){{
    .bg{{fill:#1a1a19;stroke:#33332f}} .ink{{fill:#f2f1ec}} .muted{{fill:#a3a19a}} .grid{{stroke:#33332f}} .pass{{stroke:#f2f1ec}}
    .first{{fill:#c97326}} .final{{fill:#8a80ff}} .link{{stroke:#55534d}} .ring{{stroke:#1a1a19}}
  }}
</style>
<rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14"/>
<text class="ink" x="28" y="38" font-size="18" font-weight="650">Every eval screen got closer after the fix loop</text>
<text class="muted" x="28" y="60" font-size="13">SSIM vs the input screenshot (1.0 = identical). Re-scored independently; 7 of 7 pass.</text>
<circle class="first" cx="{right - 250}" cy="34" r="6"/><text class="ink" x="{right - 238}" y="38" font-size="13">First build</text>
<circle class="final" cx="{right - 150}" cy="34" r="6"/><text class="ink" x="{right - 138}" y="38" font-size="13">After fix loop</text>
<line class="pass" x1="{right - 250}" y1="56" x2="{right - 250}" y2="68" stroke-width="2" stroke-dasharray="3 2"/><text class="ink" x="{right - 238}" y="66" font-size="13">Pass line</text>''']
    for t in (0.70, 0.80, 0.90, 1.00):
        out.append(f'<line class="grid" x1="{x(t):.1f}" y1="{top - 14}" x2="{x(t):.1f}" y2="{top + row * len(results) - 18}"/>')
        out.append(f'<text class="muted" x="{x(t):.1f}" y="{top + row * len(results) + 4}" font-size="12" text-anchor="middle">{t:.2f}</text>')
    for i, r in enumerate(results):
        y = top + i * row
        a, b, th = r["round1_ssim"], r["recheck_ssim"], r["threshold"]
        out.append(f'<text class="ink" x="28" y="{y + 5}" font-size="14">{LABELS[r["case"]]}</text>')
        out.append(f'<line class="pass" x1="{x(th):.1f}" y1="{y - 13}" x2="{x(th):.1f}" y2="{y + 13}" stroke-width="2" stroke-dasharray="3 2"/>')
        out.append(f'<line class="link" x1="{x(a):.1f}" y1="{y}" x2="{x(b):.1f}" y2="{y}" stroke-width="3" stroke-linecap="round"/>')
        out.append(f'<circle class="first ring" cx="{x(a):.1f}" cy="{y}" r="6" stroke-width="2"/>')
        out.append(f'<circle class="final ring" cx="{x(b):.1f}" cy="{y}" r="7" stroke-width="2"/>')
        out.append(f'<text class="ink" x="{x(b) + 14:.1f}" y="{y + 5}" font-size="13" font-weight="600">{b:.3f}</text>')
        out.append(f'<text class="muted" x="{x(a) - 12:.1f}" y="{y + 5}" font-size="12" text-anchor="end">{a:.3f}</text>')
    out.append(f'<text class="muted" x="{(left + right) / 2:.0f}" y="{height - 16}" font-size="12" text-anchor="middle">SSIM (structural similarity)</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def gallery(results: list[dict]) -> None:
    out = ASSETS / "gallery"
    out.mkdir(exist_ok=True)
    for r in results:
        img = Image.open(ROOT / "evals/runs" / r["case"] / "final/side-by-side.png").convert("RGB")
        img.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
        img.save(out / f"{r['case']}.jpg", quality=84, optimize=True, progressive=True)


if __name__ == "__main__":
    res = json.loads((ROOT / "evals/results.json").read_text())
    assert all(r["recheck_passed"] for r in res), "an eval case is failing; fix before publishing the chart"
    (ASSETS / "scores.svg").write_text(scores_svg(res))
    gallery(res)
    print("wrote assets/scores.svg and assets/gallery/*.jpg")

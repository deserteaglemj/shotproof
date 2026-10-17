# Eval results (2026-10-17)

Each case was built blind by a fresh Claude Opus agent that saw only the screenshot and the skill (no fixture source, no network), then every final page was re-rendered and re-scored independently by `evals/collect.py`. Score is grayscale SSIM against the input screenshot. Pass means SSIM at or above the threshold with zero console errors, page errors and failed requests. Thresholds were set before the runs: 0.90 for own pages, 0.80 for real public sites.

| Case | Kind | Round 1 SSIM | Final SSIM | Rounds | Threshold | Pass | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01-saas-landing | own page, 1280x800 | 0.948 | 0.976 | 3 | 0.90 | yes | headline font class guessed |
| 02-pricing | own page, dark, 1280x900 | 0.848 | 0.951 | 2 | 0.90 | yes | |
| 03-dashboard | own page, 1440x900 | 0.937 | 0.980 | 2 | 0.90 | yes | |
| 04-mobile-login | own page, 390x844 at 2x | 0.824 | 0.983 | 4 | 0.90 | yes | agent detected dpr 2 itself |
| 05-article | own page, serif, 1024x1000 | 0.833 | 0.930 | 5 | 0.90 | yes | hit the 5-round cap |
| 06-hacker-news | public site, 1280x900 | 0.780 | 0.865 | 3 | 0.80 | yes | logo and arrows redrawn in CSS |
| 07-gov-uk | public site, private proof mode | 0.724 | 0.886 | 5 | 0.80 | yes | proof-check passed, 0 external requests, offline verify |

All 7 pass. Mean gain from the fix loop: +0.097 SSIM (round 1 mean 0.842, final mean 0.939). Independent re-check scores matched the agents' own final scores exactly in every case.

## Per-case files

For cases 01 to 05: `runs/<case>/index.html` (the built page), `runs/<case>/assets/` (screenshot crops, when used), `runs/<case>/rounds/round-N.json` (each verify round), `runs/<case>/final/` (independent re-check: `verify.json`, `side-by-side.png`, `diff.png`). Summary data for all 7: `results.json`. Cases 06 and 07 (real sites) keep their screenshots, built pages and crops out of the public repo, because they contain third-party marks (the GOV.UK crown) and real users' posts; only their scores are published. Ground truth: `fixtures/screens/` (screenshots) and `fixtures/src/` (own-page sources, never shown to the agents).

## Known limits

- Fonts: every agent fell back to a system stack of the right class; heading bands score lowest for that reason.
- Interactive states (hover, focus, menus) cannot be seen in a screenshot, so they are the agent's choice.
- The 375px reflow has no reference screenshot, so it gets a hard check instead of a score. Re-checked with 0.3.0's `verify` (2026-10-17): all 7 final pages have 0px sideways scroll at 375px, no image covering more than 3% of the page, and no blank render, so all 7 still pass the stricter check.
- No React + Tailwind case yet (listed in TODO).
- Public-site screenshots are a snapshot taken read-only on 2026-10-17; the live sites will drift.

## Changes made from eval feedback (after these runs)

These landed after the runs above, so the scores reflect the skill before them:

1. Five of seven agents found `python3` on PATH was a shim or lacked numpy; the skill now picks a working interpreter up front.
2. `verify` now reports `band_shift_px` (how far each band's content is shifted vertically), which the article agent had to compute by hand.
3. `palette --at` gives a clear error for out-of-range points instead of a traceback.
4. Private proof mode now says how to absorb the banner's height.

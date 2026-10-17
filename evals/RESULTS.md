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
| 08-react-settings | own page, React + Tailwind, 1280x900 | 0.999 | 1.000 (0.9996) | 2 | 0.90 | yes | added with 0.4.2; see note below |

All 8 pass. Mean gain from the fix loop: +0.085 SSIM (round 1 mean 0.862, final mean 0.946). Cases 01 to 07 alone: +0.097 (0.842 to 0.939). Independent re-check scores matched the agents' own final scores exactly in every case.

**About case 08.** The source is a small Vite + React 18 + Tailwind v4 app (`fixtures/src/08-react-settings/`). The agent got the same scaffold with an empty `App.jsx`, built the screen as React components with Tailwind classes, and verified against the Vite dev server; `collect.py` then built the agent's app and re-scored the production build served on 127.0.0.1. Its transcript shows no access to `evals/`. The near-perfect score is real but easy to over-read: the source also used Tailwind's default scale, colors and system font stack, so an agent that picks the right utilities reproduces the exact pixels. It shows the React mode works end to end (dev server, verify, edit loop); it does not show how React mode does on a design built outside Tailwind's defaults.

## Per-case files

For cases 01 to 05: `runs/<case>/index.html` (the built page), `runs/<case>/assets/` (screenshot crops, when used), `runs/<case>/rounds/round-N.json` (each verify round), `runs/<case>/final/` (independent re-check: `verify.json`, `side-by-side.png`, `diff.png`). Case 08: `runs/08-react-settings/src/` (the agent's React source) plus the same `rounds/` and `final/`. Summary data for all 8: `results.json`. Cases 06 and 07 (real sites) keep their screenshots, built pages and crops out of the public repo, because they contain third-party marks (the GOV.UK crown) and real users' posts; only their scores are published. Ground truth: `fixtures/screens/` (screenshots) and `fixtures/src/` (own-page sources, never shown to the agents).

## Known limits

- Fonts: every agent fell back to a system stack of the right class; heading bands score lowest for that reason.
- Interactive states (hover, focus, menus) cannot be seen in a screenshot, so they are the agent's choice.
- The 375px reflow has no reference screenshot, so it gets a hard check instead of a score. Re-checked with 0.4.0's `verify` (2026-10-17): all 8 final pages have 0px sideways scroll at 375px, no image covering more than 3% of the page, and no blank render.
- One React + Tailwind case only, and an easy one (see the case 08 note).
- Public-site screenshots are a snapshot taken read-only on 2026-10-17; the live sites will drift.

## Changes made from eval feedback (after these runs)

These landed after the runs above, so the scores reflect the skill before them:

1. Five of seven agents found `python3` on PATH was a shim or lacked numpy; the skill now picks a working interpreter up front.
2. `verify` now reports `band_shift_px` (how far each band's content is shifted vertically), which the article agent had to compute by hand.
3. `palette --at` gives a clear error for out-of-range points instead of a traceback.
4. Private proof mode now says how to absorb the banner's height.

# Changelog

## 0.4.0 (2026-10-17)

- `verify` fails a blank render (flat color or no text), a page where one image covers more than a quarter of it (`--max-image-ratio`, so pasting the screenshot cannot win the score), and sideways scroll at 375px wide (`--mobile-width`, writes `render-375.png`).
- `verify` reports `page_stats`, `mobile` and a plain-words `failures` list, and saves `page-snapshot.html` each round.
- Skill: crop browser chrome and device frames off the screenshot first; after round 1 make targeted edits only; keep the best-scoring round, not the last.
- README comparison corrected: abi/screenshot-to-code does render desktop and mobile previews for its model, with no score or pass line.
- All 7 eval pages re-checked under the new rules and still pass.

## 0.3.0 (2026-10-17)

- Renamed to **shotproof** so it is not confused with abi/screenshot-to-code. The plugin, skill, slash command (`/shotproof`) and marketplace are all `shotproof` now; install with `shotproof@shotproof`. The helper script is still `s2c.py`.

## 0.2.0 (2026-10-17)

Public release.

- Skill picks a Python interpreter that has Playwright, Pillow and numpy before starting, and gives the one-line setup command when none does (5 of 7 eval agents hit a PATH `python3` without numpy).
- `verify` reports `band_shift_px`: how far each band's content sits above or below the screenshot, so vertical drift is found without hand measurement.
- `palette --at` gives a clear error for points outside the image.
- Private proof mode: generic folders and banner text for any studio, plus guidance on absorbing the banner's height.
- README rebuilt with a demo video, hero, how-it-works diagram, score chart, before/after gallery and a comparison table. CI runs the self-tests on every push.

## 0.1.0 (2026-10-17)

First release, private.

- `screenshot-to-code` skill: intake (dpr, mode), builder-style read of the screenshot (sections, exact text, sampled colors, type, spacing, media), section-by-section build, render-compare-fix loop capped at 5 rounds, honest score report.
- Modes: single-file HTML (default), React + Tailwind, private client proof (`references/private-proof.md`).
- `/screenshot-to-code` slash command (Claude Code).
- `s2c.py` helper: `render`, `verify` (SSIM, per-band SSIM, pixel match, side-by-side and diff images, console, page and request errors, optional offline mode), `crop`, `palette`, `proof-check`. Uses Python Playwright, Pillow and numpy that were already installed.
- Unit and end-to-end self-tests (`plugins/screenshot-to-code/tests`).
- Eval set of 7 cases (5 own pages, 2 public sites) with results in `evals/RESULTS.md`.
- Local marketplace `quis-screenshot-to-code` for Claude Code and Codex.

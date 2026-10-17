# AGENTS.md

shotproof: a Claude Code and Codex plugin that turns a screenshot into matching HTML + CSS (or React + Tailwind) using the host agent's own model (no API key), then renders the result, scores it against the screenshot with SSIM and fixes it until it passes. MIT.

## Install

- Claude Code: `/plugin marketplace add deserteaglemj/shotproof`, then `/plugin install shotproof@shotproof`
- Codex: `codex plugin marketplace add deserteaglemj/shotproof`, then `codex plugin add shotproof@shotproof`
- Helper dependencies (Python 3): `python3 -m pip install playwright pillow numpy && python3 -m playwright install chromium`

## Use

- `/shotproof ./screenshot.png` (HTML), `/shotproof ./app.png react` (React + Tailwind), `/shotproof ./site.png proof <slug>` (private client proof)
- Or ask: "turn this screenshot into code"
- The workflow the agent follows is `plugins/shotproof/skills/shotproof/SKILL.md`. Read it before changing behavior.
- Helper: `python3 plugins/shotproof/skills/shotproof/scripts/s2c.py verify REF.png PAGE --out-dir DIR [--dpr 2] [--offline] [--threshold 0.9]`. Exit code 0 means pass.

## Test (same commands as CI, `.github/workflows/tests.yml`)

```bash
python -m pip install playwright pillow numpy
python -m playwright install --with-deps chromium
python -c "import json; [json.load(open(p)) for p in ['.claude-plugin/marketplace.json','plugins/shotproof/.claude-plugin/plugin.json','plugins/shotproof/.codex-plugin/plugin.json']]"
python -m unittest discover -s plugins/shotproof/tests -v
```

Also used before releases: `claude plugin validate --strict ./plugins/shotproof` and `claude plugin validate --strict .`

## Layout

- `.claude-plugin/marketplace.json`: marketplace `shotproof`, read by Claude Code and Codex
- `plugins/shotproof/.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`: plugin manifests (keep versions in sync)
- `plugins/shotproof/skills/shotproof/SKILL.md`: the skill; `references/private-proof.md`: proof-mode rules
- `plugins/shotproof/skills/shotproof/scripts/s2c.py`: render, verify, crop, palette, proof-check
- `plugins/shotproof/commands/shotproof.md`: the `/shotproof` slash command
- `plugins/shotproof/tests/test_s2c.py`: self-tests
- `evals/`: `cases.json`, fixtures, `collect.py` (independent re-check), `results.json`, `RESULTS.md`, `runs/`
- `assets/`: README images, demo video; `assets/make_assets.py` regenerates `scores.svg` and the gallery from `evals/results.json`
- `docs/`: GitHub Pages landing page; `docs/launch/LISTINGS.md`: draft directory listings (not submitted)
- `llms.txt`: summary for language-model crawlers

## Rules for changes

- Claims in README or docs must match `evals/RESULTS.md`. Do not write "first", "only" or "best".
- No text or code copied from abi/screenshot-to-code (README credits say so).
- HTML mode output stays free of CDNs, web fonts and remote images; proof mode must pass `s2c.py proof-check`.
- Bump the version in both plugin.json files and add a CHANGELOG entry for each release.

## Unknown

- Contribution and code-review policy: unknown (no CONTRIBUTING file).
- Supported Python versions beyond 3.12 (CI) and the maintainer's local 3.x: unknown.

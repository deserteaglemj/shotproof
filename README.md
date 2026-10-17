<p align="center">
  <img src="assets/hero.svg" alt="screenshot-to-code: turns a screenshot into code, then proves it matches" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-5b4ff0"></a>
  <a href="evals/RESULTS.md"><img alt="Evals: 7 of 7 pass" src="https://img.shields.io/badge/evals-7%2F7%20pass-2f8f62"></a>
  <a href="https://github.com/deserteaglemj/screenshot-to-code/actions/workflows/tests.yml"><img alt="Tests" src="https://github.com/deserteaglemj/screenshot-to-code/actions/workflows/tests.yml/badge.svg"></a>
  <img alt="Works with Claude Code and Codex" src="https://img.shields.io/badge/works%20with-Claude%20Code%20%7C%20Codex-1d1d1b">
</p>

Drop in a screenshot of any website or app screen. Your agent rebuilds it as one clean HTML + CSS file (or React + Tailwind), opens the result in Chromium at the screenshot's exact size, scores it against your image, and fixes the worst-matching part. It repeats until the score passes, then tells you the number and what it could not match.

It runs on the model you already use in Claude Code or Codex. There is nothing else to sign up for and no API key to paste.

<p align="center">
  <img src="assets/demo.gif" alt="20-second demo: screenshot in, code out, scored and fixed until it passes" width="100%">
  <br><sub><a href="assets/demo.mp4">Watch the full-quality video with sound (MP4)</a></sub>
</p>

## Install in 30 seconds

**Claude Code**

```text
/plugin marketplace add deserteaglemj/screenshot-to-code
/plugin install screenshot-to-code@quis-screenshot-to-code
```

**Codex**

```bash
codex plugin marketplace add deserteaglemj/screenshot-to-code
codex plugin add screenshot-to-code@quis-screenshot-to-code
```

**One-time helper setup** (the checker uses Playwright, Pillow and numpy; skip if you have them):

```bash
python3 -m pip install playwright pillow numpy && python3 -m playwright install chromium
```

Then:

```text
/screenshot-to-code ~/Desktop/landing.png
/screenshot-to-code ~/Desktop/app.png react
/screenshot-to-code ~/Desktop/prospect.png proof acme-plumbing
```

Or just say "turn this screenshot into code". Codex picks the skill up the same way.

## What a run looks like

```text
  ┌─────────────┐     ┌──────────────┐     ┌───────────────┐
  │  shot.png   │ ──▶ │  index.html  │ ──▶ │  render.png   │ ──▶  score, fix, repeat
  └─────────────┘     └──────────────┘     └───────────────┘

  $ /screenshot-to-code login.png          390 x 844 CSS px, dpr 2 (detected)

  round 1   ████████████████░░░░   0.824   worst: band 5/8 (y 844-1055px)
  round 2   █████████████████░░░   0.849   worst: band 5/8 (y 844-1055px)
  round 3   ████████████████████   0.979   PASS
  round 4   ████████████████████   0.983   PASS

  wrote   login/index.html
  gaps    font is a system stack (real font unknown); hover and focus states inferred
```

Those are the real scores from the mobile-login eval case. The bar is SSIM, a standard 0-to-1 measure of how alike two images look.

## How it works

<p align="center"><img src="assets/how-it-works.svg" alt="Read, build, render, compare, then fix and repeat up to five rounds, then report" width="100%"></p>

1. **Read like a builder.** Sections with pixel ranges, every word copied exactly, colors sampled from real pixels (not guessed), type sizes measured from glyph heights, spacing grid, components, images.
2. **Build section by section.** Semantic HTML, CSS variables for the sampled palette, flexbox and grid, real text, visible focus states, a sensible phone layout.
3. **Render and compare.** `s2c.py verify` screenshots the page with Chromium and writes a side-by-side image, a red diff heatmap, the overall score, a score for each of 8 horizontal bands, and how many pixels each band is shifted up or down.
4. **Fix the worst band first**, re-check, and stop at the pass line or after 5 rounds. Console errors and failed requests fail the check no matter how good the score looks.
5. **Report honestly**: files written, first and final score, and the gaps it could not close.

## The proof

<p align="center"><img src="assets/scores.svg" alt="Dumbbell chart: every eval case improved after the fix loop and ended above its pass line" width="100%"></p>

Seven test screens. Five are pages written for the test (so the true answer is known) and two are real public sites captured read-only. Each was rebuilt by a fresh agent that saw only the screenshot and the skill, and every final page was then re-scored by a separate script. All 7 pass; the fix loop added 0.097 SSIM on average. Full numbers, per-round logs and limits: [evals/RESULTS.md](evals/RESULTS.md).

**Left: the input screenshot. Right: what the agent built.**

<p align="center"><img src="assets/gallery/04-mobile-login.jpg" alt="Mobile login screen: input vs rebuilt, SSIM 0.983" width="70%"></p>
<p align="center"><img src="assets/gallery/03-dashboard.jpg" alt="Orders dashboard: input vs rebuilt, SSIM 0.980" width="100%"></p>
<p align="center"><img src="assets/gallery/01-saas-landing.jpg" alt="Landing page: input vs rebuilt, SSIM 0.976" width="100%"></p>

<details>
<summary>Two more cases</summary>

<p align="center"><img src="assets/gallery/02-pricing.jpg" alt="Dark pricing table: input vs rebuilt, SSIM 0.951" width="100%"></p>
<p align="center"><img src="assets/gallery/05-article.jpg" alt="Serif article: input vs rebuilt, SSIM 0.930" width="100%"></p>

</details>

The two real-site cases (Hacker News, and GOV.UK rebuilt in private proof mode) passed too; their images stay out of this repo because they show third-party logos and real users' posts.

## Three modes

| Mode | When | Output |
| --- | --- | --- |
| **HTML** (default) | Anything | One `index.html` with inline CSS. No build step, no CDN, no web fonts, so it renders the same everywhere. |
| **React + Tailwind** | You ask, or the project already uses React | Components written into your project, following its existing conventions, checked against your local dev server. |
| **Private client proof** | Redesign pitches and agency outreach | A locked-down concept page: `noindex,nofollow`, a visible "private concept" banner, no scripts, iframes, forms or remote URLs, no price claims, checked offline and previewed on 127.0.0.1 only. `s2c.py proof-check` enforces all of it. |

## How it compares

| | screenshot-to-code (this plugin) | [abi/screenshot-to-code](https://github.com/abi/screenshot-to-code) | Asking your agent with no plugin |
| --- | --- | --- | --- |
| Where it runs | Inside Claude Code or Codex | Its own web app (React + FastAPI) | Inside your agent |
| Model and keys | Your agent's own model, no extra key | Bring an OpenAI, Anthropic or Gemini API key | Your agent's own model |
| Checks its own output | Renders, scores (SSIM per band) and fixes in a loop | Previews the result | Only if you ask, and with no score |
| Output | HTML + CSS, or React + Tailwind in your repo | Many stacks, plus video input | Whatever it decides |
| Published evals | 7 cases, scored independently | 16-screenshot eval set with a rating UI | None |

abi/screenshot-to-code is a great standalone app with more stacks and models. This plugin is for people who already work in an agent and want the result checked, measured and fixed without leaving it.

## The helper script

`s2c.py` (inside the skill) works on its own too:

| Command | Does |
| --- | --- |
| `verify REF.png PAGE --out-dir DIR [--dpr 2] [--offline] [--threshold 0.9]` | Render PAGE at REF's size, score it, write visuals. Exits 0 only on a pass with no errors. |
| `render PAGE --out x.png --width W --height H [--dpr 2]` | Screenshot a local file or localhost URL |
| `palette REF.png [--at x,y ...]` | Dominant colors, plus exact pixel samples |
| `crop REF.png --box x,y,w,h --out assets/logo.png` | Cut a logo or photo out of the screenshot |
| `proof-check page.html` | Check the private client-proof rules |

Tests: `python3 -m unittest discover -s plugins/screenshot-to-code/tests` (scoring, shift detection, palette, every proof rule, and a real end-to-end render).

## FAQ

**Does it send my screenshot anywhere?** Only to the model your agent already uses. The checker runs locally in headless Chromium. Proof mode verifies with the network blocked.

**What score counts as a pass?** 0.90 SSIM for clean UI screenshots and 0.80 for real sites, where custom fonts, photos and icon art cannot be copied exactly. Both were set before the evals ran. You can change it with `--threshold`.

**Will it match pixel for pixel?** No, and it will not claim to. Fonts are the usual gap: it picks a system font of the same style and tells you which real font it thinks the design uses.

**Retina screenshots?** Detected. A 2x Mac screenshot is rendered at half its pixel size with device scale 2.

**Can it do a whole page from several screenshots?** Yes: the same page at different widths becomes one responsive page; different pages share one set of CSS tokens.

## Credits

The quality rules were inspired by a shared `image-to-code` agent skill, and the prompt and evaluation ideas by [abi/screenshot-to-code](https://github.com/abi/screenshot-to-code) (MIT). No text or code was copied from either. The two public-site cases were captured read-only; only their scores are published here.

Made by Marquis Jackson at M Studio. MIT licensed.

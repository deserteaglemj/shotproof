---
name: screenshot-to-code
description: Turn one or more screenshots of a website or app screen into faithful, production-quality code, then check the result visually against the screenshot and fix it until it matches. Default output is one self-contained HTML + CSS file; React + Tailwind when the user asks or the target project already uses it; a locked-down private client proof (noindex, no scripts, no remote URLs, preview on 127.0.0.1 only) for agency outreach and redesign pitches. Uses the running agent's own vision, no local model and no API keys. Use for "turn this screenshot into code", "rebuild this page from the image", "clone this screen", "make an HTML version of this site", or "make a private proof from this screenshot".
---

# Screenshot to code

You read the screenshot with your own vision, write the code, render it, compare it with the screenshot, and fix what differs. The compare step is not optional: a build that was never rendered and compared is not done.

Helper script (Python 3 with Playwright, Pillow and numpy; no installs): `scripts/s2c.py` next to this file. Call it with its absolute path, written here as `S2C`.

Pick the interpreter once before starting, since `python3` on PATH may be a different install without these modules. Use the first that prints a path, as `PY` below. If none does, stop and give the user the one-time setup command, `python3 -m pip install playwright pillow numpy && python3 -m playwright install chromium`; never install it without their OK:

```bash
for p in python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do $p -c 'import numpy, PIL, playwright' 2>/dev/null && command -v $p && break; done
```

## 1. Intake

1. Open every screenshot. Note pixel size. Mac screenshots are usually 2x: if text looks normal size at half the pixel width, use `--dpr 2` everywhere below. The CSS viewport is pixel size divided by dpr.
2. Pick the mode:
   - **HTML** (default): one `index.html` with an inline `<style>`, no build step, no framework, no CDN. Use it unless one of the next two applies.
   - **React + Tailwind**: the user asks for it, or the target project already has React (check `package.json`). Write components into that project, follow its conventions and existing components, and verify against its local dev server URL (127.0.0.1 or localhost only). When the project has its own frontend skill or rules, follow them too.
   - **Private client proof**: the user says proof, outreach, pitch or prospect (M Studio uses this for prospects), or the screenshot is a real business's site being redone as a pitch. Read `references/private-proof.md` before writing anything; its rules override the rest of this file where they differ.
3. Output folder: what the user named; otherwise next to the screenshot in a folder named after it. Never write into `~` top level.
4. Several screenshots: same page at different widths means one responsive page (verify each width); different pages means one file per page sharing one CSS block of tokens; states of one screen (hover, open menu) means one page with those states built in.

## 2. Read the screenshot like a builder

Do this before writing code, and write the inventory down in your working notes:

- **Sections, top to bottom**: name each band (nav, hero, logo strip, features, footer...) with its pixel y-range. This list drives the build order and the fix loop.
- **Exact text**: copy every visible word as written, including casing and punctuation. Never paraphrase, never add copy the screenshot does not show. Unreadable text: zoom by cropping (`PY S2C crop`) and look again; if still unreadable, use a neutral stand-in of the same length and list it as a gap.
- **Colors**: run `PY S2C palette shot.png` for the dominant colors, and `--at x,y ...` to sample exact pixels for backgrounds, buttons, text and borders. Do not guess hex values by eye.
- **Type**: for each text style estimate font size from cap or x-height in pixels divided by dpr, weight, line-height, letter-spacing, and family class (geometric sans, humanist sans, serif, mono). Use a system stack that matches the class; name the likely real font in a comment.
- **Spacing and grid**: container width, column count, gutters, section padding, gaps between repeated items. Measure in pixels, convert to CSS px. Look for a spacing step (4 or 8) and use it.
- **Components**: buttons (height, radius, padding, border), inputs, cards, badges, icons, dividers, shadows. Note which are repeated so they become one class.
- **Media**: logos, photos, illustrations, icons. Decide per item: CSS (simple shapes, gradients), inline SVG (simple icons and logos you can draw cleanly), or a crop of the screenshot (`PY S2C crop shot.png --box x,y,w,h --out assets/name.png`) for photos and complex logos. Never hotlink images from the live site. Crops at 2x should be shown at half size.

## 3. Build

- Semantic HTML: `header`, `nav`, `main`, `section`, `footer`, one `h1`, headings in order, `button` for actions, `a` for links, `alt` on every image (empty for decoration).
- CSS custom properties for the sampled colors, font stacks and spacing step at the top of the stylesheet. Flexbox and grid for layout. No absolute positioning of whole sections and no fixed pixel heights on text containers; those break the moment text wraps.
- Build section by section in the inventory order, matching each one before polishing the next.
- Real text, never pictures of text. Real buttons and links with hover and visible `:focus-visible` states even though the screenshot cannot show them.
- Responsive: match the screenshot exactly at its own viewport, and make the layout reflow sensibly at 375px wide (stack columns, wrap nav) without horizontal scroll.
- No external requests in HTML mode: no CDN, no web fonts, no remote images. That keeps the file portable and the render deterministic.

### Quality bar

The goal is the screenshot rebuilt, not a redesign of it. Hold to these:

- Match structure and proportion first, then color, then type detail, then small decoration.
- Keep a hero as clean as the source: same headline line breaks, same breathing room. Do not add badges, pills, eyebrow labels, stats or gradients that are not there.
- Do not wrap sections in extra boxes, and never nest cards inside cards unless the screenshot clearly does.
- No invented content: no fake testimonials, metrics, prices, logos or links. Missing detail gets the plainest faithful stand-in and a line in the gaps list.
- No decorative effects the source does not have (glows, glassmorphism, blobs, animated gradients).
- Accessible by default: landmarks, alt text, labelled controls, focus states. Keep the source's contrast; if source text fails 4.5:1, match it and note it as a gap rather than silently changing the design.

## 4. Verify and fix (the loop)

Run after the first full build:

```bash
PY S2C verify shot.png path/to/index.html --out-dir path/to/.verify/round-1 --dpr 2
```

(For React mode pass the dev server URL instead of the file. For a tall full-page capture add `--viewport-height <css px of a normal screen>`.)

It renders the page at the screenshot's viewport with Chromium, then writes `render.png`, `side-by-side.png`, `diff.png` (red = different) and `verify.json` with:

- `ssim` (0 to 1, structural similarity, the main score) and `band_ssim_top_to_bottom` (8 horizontal bands) plus `worst_bands`
- `band_shift_px`: per band, how many pixels your content sits lower (positive) or higher (negative) than the screenshot. A run of equal non-zero shifts means something above that band is too tall or short; fix the first band where the shift appears.
- `pixel_match`, `mean_color_delta`
- `console_errors`, `page_errors`, `failed_requests`, `external_requests`
- `passed`: ssim at or above `--threshold` (default 0.90) and no console, page or request errors

Then:

1. Look at `side-by-side.png` and `diff.png` yourself. The numbers say where; your eyes say what.
2. Fix the worst band first. Typical causes, in order: wrong section height or padding, wrong font size or line-height (text wraps differently and shifts everything below), wrong container width, wrong colors, missing element.
3. Re-run verify into `round-2`, `round-3`... Keep every round's `verify.json`.
4. Stop when `passed` is true and another round would not visibly improve anything, or after **5 rounds**, whichever comes first. Do not tune numbers blindly to chase the score; every change should make the side-by-side look more like the source.
5. Fix every console error and failed request regardless of score.

Scores to expect: a clean UI screenshot rebuilt well lands at 0.90 to 0.97. Photos replaced by crops still score high; photos replaced by placeholders, dense text in a different font, or anti-aliasing differences cap the score lower. Below 0.80 after the loop means something structural is still wrong.

## 5. Report

Finish with a short report:

- Files written (paths) and the mode used.
- Score table: round 1 ssim and final ssim, plus pass or fail at the threshold.
- Gaps that remain and why (unreadable text, unknown font, photo placeholders, interactive states the screenshot does not show).
- Anything the user must decide (real images or copy to swap in, fonts to license).

Never claim a pixel-perfect match. Report the measured score and the gaps.

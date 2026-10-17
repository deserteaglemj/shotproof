# shotproof plugin

Turns a screenshot of a website or app screen into one HTML + CSS file (or React + Tailwind), renders it in Chromium at the screenshot's size, scores it with SSIM and fixes the worst-matching part until it passes. Runs on the agent's own model: no API key.

Install (Claude Code):

```text
/plugin marketplace add deserteaglemj/shotproof
/plugin install shotproof@shotproof
```

Install (Codex):

```bash
codex plugin marketplace add deserteaglemj/shotproof
codex plugin add shotproof@shotproof
```

Use: `/shotproof ./landing.png`, or ask "turn this screenshot into code".

Contents: `skills/shotproof/SKILL.md` (the workflow), `skills/shotproof/scripts/s2c.py` (render, verify, crop, palette, proof-check), `commands/shotproof.md`, `tests/`.

Full docs, evals and limitations: https://github.com/deserteaglemj/shotproof

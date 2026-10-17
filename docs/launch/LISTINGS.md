# Directory listings (drafts, not submitted)

Ready-to-paste text for the places agents and people look for Claude Code and Codex tools. **Nothing here has been submitted.** Whether and when to submit is the maintainer's decision. Entry rules were read on 2026-10-17 and can change; re-read each target's CONTRIBUTING file before submitting.

Repo: https://github.com/deserteaglemj/shotproof (public since 2026-10-17)
Landing page: https://deserteaglemj.github.io/shotproof/

## Shared copy

- **Name:** shotproof
- **One line (under 10 words):** Screenshot to HTML or React, scored and fixed until matching.
- **Short (about 25 words):** Claude Code and Codex plugin that turns a screenshot into HTML/CSS or React + Tailwind with no API key, then renders, scores (SSIM) and fixes it until it matches.
- **Long:** shotproof turns a screenshot of any website or app screen into one self-contained HTML + CSS file, or React + Tailwind components in your project, using the model your Claude Code or Codex session already runs (no API key). It renders the result in Chromium at the screenshot's own size, scores it with SSIM overall and per band, and fixes the worst band for up to 5 rounds against a fixed pass line. Console errors, failed requests, blank pages, pasted screenshots and sideways scroll at 375px fail the check. 8 of 8 published eval cases pass, re-scored independently (evals/RESULTS.md). MIT.
- **Install:** `/plugin marketplace add deserteaglemj/shotproof` then `/plugin install shotproof@shotproof` (Claude Code); `codex plugin marketplace add deserteaglemj/shotproof` then `codex plugin add shotproof@shotproof` (Codex).
- **Tags:** screenshot-to-code, image-to-code, design-to-code, html, tailwind, react, playwright, ssim, claude-code-plugin, codex-plugin, agent-skills, no-api-key

## 1. awesome-claude-code (hesreallyhim/awesome-claude-code)

- **Where:** https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml (web issue form only; PRs and CLI-made issues risk a temporary block)
- **Eligibility:** resource must be at least 14 days old with continued commits, or have 100+ stars. One recommendation at a time. **shotproof's first public commit is 2026-10-17, so the earliest eligible date is 2026-10-31** unless it reaches 100 stars first.
- **Category:** Agent Skills (or Tooling)
- **Display name:** shotproof
- **Link:** https://github.com/deserteaglemj/shotproof
- **Author:** Marquis Jackson (https://github.com/deserteaglemj)
- **License:** MIT
- **Description to paste:** Claude Code plugin that turns a screenshot into HTML/CSS or React + Tailwind using Claude's own vision (no API key), then renders it in Chromium, scores it against the screenshot with SSIM per band and fixes the worst band for up to 5 rounds. Ships 8 independently re-scored eval cases.

## 2. Agent-skill lists

### VoltAgent/awesome-agent-skills
- **Where:** pull request to https://github.com/VoltAgent/awesome-agent-skills (add to the end of "Community Skills > Development and Testing")
- **Eligibility:** "Brand new skills that were just created are not accepted"; needs real community usage first. Not eligible yet.
- **Entry to paste:** `- [deserteaglemj/shotproof](https://github.com/deserteaglemj/shotproof) - Screenshot to HTML or React, scored and fixed until matching`

### ComposioHQ/awesome-claude-skills
- **Where:** pull request to https://github.com/ComposioHQ/awesome-claude-skills (their CONTRIBUTING asks for a skill folder with examples)
- **Eligibility:** must solve a real problem based on actual usage and include examples. Read their folder format before opening a PR.
- **Example prompt to include:** "Turn ./landing.png into a single HTML file and verify it matches." Output: `index.html`, per-round `verify.json`, side-by-side and diff images, final SSIM and a gaps list.

### travisvn/awesome-claude-skills
- **Where:** pull request to https://github.com/travisvn/awesome-claude-skills
- **Eligibility:** requires "social proof" for skill submissions and non-promotional wording. Not eligible until there is outside usage.
- **Entry to paste:** `- [shotproof](https://github.com/deserteaglemj/shotproof) - Turns a screenshot into HTML/CSS or React + Tailwind, then scores it with SSIM and fixes it until it matches. No API key.`

## 3. Skill registries

### skills.sh
- **Where:** https://skills.sh (listing is driven by installs through the `skills` CLI; no submission form was confirmed)
- **Command people would run:** `npx skills add deserteaglemj/shotproof`
- **Status:** unverified whether the CLI finds `plugins/shotproof/skills/shotproof/SKILL.md` in this layout. Test on a clean machine before promoting this command.

## 4. Claude plugin directory

- **Where:** the official submission portal URL could not be confirmed. Candidates seen in secondary sources: https://clau.de/plugin-directory-submission and https://claude.ai/directory/manage . Check the live link from https://code.claude.com/docs/en/plugins before submitting.
- **Requirements seen in docs:** public GitHub repo, valid `.claude-plugin` manifest (passes `claude plugin validate --strict`, which shotproof does), README, LICENSE.
- **Fields to paste:**
  - Name: shotproof
  - Repository: https://github.com/deserteaglemj/shotproof
  - Install: `/plugin marketplace add deserteaglemj/shotproof` then `/plugin install shotproof@shotproof`
  - Description: the "Short" copy above
  - Category: Development / Frontend
  - Homepage: https://deserteaglemj.github.io/shotproof/

## 5. Codex listings

### hashgraph-online/awesome-codex-plugins
- **Where:** pull request adding one line to `README.md` at https://github.com/hashgraph-online/awesome-codex-plugins (alphabetical by display name)
- **Eligibility:** their scanner (`plugin-scanner scan .`) must score 80/130 or higher with no critical or high findings, and the output goes in the PR description. **Not run yet.**
- **Entry to paste:** `- [shotproof](https://github.com/deserteaglemj/shotproof) - Turn a screenshot into HTML/CSS or React + Tailwind, then render, score (SSIM) and fix until it matches. No API key.`

### Official Codex plugin directory
- **Where:** no verified self-serve submission path as of 2026-10-17. Until one exists, the documented route is the self-hosted marketplace: `codex plugin marketplace add deserteaglemj/shotproof`.

## 6. Launch posts (also the maintainer's call)

- **Show HN title:** Show HN: shotproof, a Claude Code and Codex plugin that turns a screenshot into HTML and checks the render against it
- **First comment outline:** why (agents write plausible UI nobody checks), how (render, SSIM in 8 bands, up to 5 fix rounds, errors fail the check, no key), results (8 of 8, 0.865 to 0.9996, link to evals/RESULTS.md), limits (SSIM only, static frame, local Python and Chromium), ask (which screenshots break it).

---
description: Turn a screenshot of a website or app screen into matching code, then render, compare and fix it until it matches
argument-hint: <screenshot path(s)> [react] [proof <slug>] [out <folder>]
---

Use the `shotproof` skill from this plugin and follow it end to end, including the verify-and-fix loop and the final report with scores.

Request: $ARGUMENTS

- Screenshot paths are the image files in the request. If none are given, use the images attached to the conversation; if there are none at all, ask for one.
- `react` means React + Tailwind mode. `proof <slug>` means private client proof mode with that slug. `out <folder>` sets the output folder.
- Otherwise use the default single-file HTML mode.

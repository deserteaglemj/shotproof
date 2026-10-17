# Private client proof mode

Use this when the screenshot is a real business's website being redone as a private pitch (agency outreach, a redesign concept for a prospect), or when the user says proof, outreach or prospect. A proof shows the prospect what their site could look like. It must never look like, or act like, their live site, and it never leaves the machine unless the user sends it themselves.

These rules override the main skill where they differ.

## Where files go

- Folder: the one the user or the project's instructions (AGENTS.md, CLAUDE.md) name; otherwise `proofs/<slug>/index.html` under the current working folder, where `<slug>` is the business name in lowercase-hyphen form.
- Assets (crops) go in `<slug>/assets/` and are referenced as `assets/<name>.png`.
- Verify rounds go in `<slug>/.verify/`.
- The input screenshot stays where it is. Do not upload it, paste it into a web tool, or send it anywhere.

## The contract (checked by `PY S2C proof-check`)

The page must have:

- `<meta name="robots" content="noindex,nofollow">` in the head, written exactly like that.
- A visible banner as the first element in `body`, carrying the `data-private-proof` attribute, with text such as: "PRIVATE concept by <your studio>. Not the live site. Nothing here is published." Style it so it cannot be hidden by the page's own CSS (normal flow, solid background, high z-index, not inside any other element). Keep it slim (about 24px) and take its height back from the first section's top padding so the rest of the page lines up with the screenshot; the verify score will still dip slightly in the top band, which is expected.

The page must not have:

- `<script>`, `<iframe>`, `<frame>`, `<object>`, `<embed>`, `<form>`, `<base>`, `<link>`, `<portal>`, `<applet>`, or any `on...=` event attribute.
- `<meta http-equiv="refresh">`.
- Any absolute or remote URL: no `http:`, `https:`, `//`, `data:`, `mailto:`, `tel:`, `javascript:` in `href`, `src`, `srcset`, `poster`, or CSS `url()`. Links use `#section` anchors. Images use relative `assets/...` paths only, and never `..` or a leading `/`.
- CSS `@import` or CSS escape sequences (`\66` style), which can hide URLs.
- A `$` character anywhere. No prices, savings, revenue or money claims of any kind.
- Invented reviews, ratings, awards, client logos, phone numbers or addresses. Use only facts visible in the screenshot, and leave contact details as visible text, not links.
- Web fonts. System font stacks only.

Run it before calling the proof done:

```bash
PY S2C proof-check proofs/<slug>/index.html
```

Exit code 0 and `"passed": true` are required. Fix every problem it lists; never weaken the check.

## Verify offline

Run the visual loop with network blocked so nothing is fetched:

```bash
PY S2C verify shot.png proofs/<slug>/index.html --out-dir proofs/<slug>/.verify/round-1 --dpr 2 --offline
```

`external_requests` must be empty.

## Previewing

Preview only on the loopback address, never on `0.0.0.0` or a LAN IP, and stop the server when done:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory proofs/<slug>
```

Opening the `index.html` file directly in a browser also works and needs no server.

## Never

- Publish, deploy, upload, email or message the proof. Sending is the user's call, every time.
- Use the hosted screenshottocode.com app, a paid API, or any remote model for a real business's screenshot.
- Copy the proof into a public repo or a shared template pack.

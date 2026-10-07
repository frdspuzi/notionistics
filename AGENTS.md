# Notionistics

Landing page for notionistics.com: one static `index.html`, no build step, served by GitHub Pages (`CNAME`).

## HANDOFF.md is the project state

`HANDOFF.md` is the single source of truth for where the project stands. Read it first. A task is done only when `HANDOFF.md` reflects it: update its **Current state** section with what changed, what is pending, and any open decision waiting on the owner. Replace stale lines rather than appending history; git holds the history.

## Identity and voice

Notionistics is an **entity**, a startup team, not a solo freelancer. Write copy in the team voice ("we", "our team"). The team is **led by Firdaus** (frdspuzi); name him as a person in the hero ("led by Firdaus") and the About section only. First integration job completed June 2023.

Services, in priority order: software solutions (Zapier / Notion / Typeform integrations, and full project delivery priced by discussion), then Notion-styled avatars. We do not offer a scripting service (removed by the owner). No em dashes anywhere on the page; use commas, colons or full stops.

## Claims and sources

Every number or quote on the page traces to one of these files. Check the source before changing a claim:

- `HANDOFF.md`: Fiverr gigs, prices, rating breakdown.
- `ORDERS_REFERENCE.md`: Fiverr order counts by service and year.
- `fiverr_reviews.csv`: verbatim review text, country, gig.
- `order-confirmations-handoff.md`: orders from the old Notionistics store.
- `integration_orders.csv`: what each integration job was and what was delivered (source for "Problems we fix" and "Selected work"; describe work generally, never name the client).

These five files are **private**: they hold client and business data. They stay out of git and off the page.

## Client privacy

Client portraits and names are personal data. Clients appear on the page only with their consent, credited as "First name L." plus a country flag. Without consent a quote is credited by a masked Fiverr username: first 2 and last 2 characters, the middle replaced by asterisks in the HTML (`.mask` blurs them on screen). The full username never appears in the source. The client archive (`G:\My Drive\Notion\<client name>\`) is source material only. Featuring a public figure's avatar (the "Seen in the wild" card) needs the client's or the person's OK: state only what is visible, never imply a commission or endorsement, and keep order numbers, prices and buyer names off the page.

## Reviews are generated

The reviews marquee between `<!-- reviews:start -->` and `<!-- reviews:end -->` in `index.html` is built from `fiverr_reviews.csv`. To change reviews, edit the CSV (or the rules in the script) and run `python -I tools/build_reviews.py fiverr_reviews.csv index.html`. A reviewer's country needs a flag symbol in the sprite and an entry in the script's `FLAGS` map to be included.

Client avatars on review cards come from `assets/clients/cNN.svg` (neutral names, slimmed copies of the owner's deliveries in `G:\My Drive\Notion\<username>\`, approved by the owner on 2026-10-07). The username → file mapping lives in the private, git-ignored `clients_map.csv`, which the generator reads. Only exact folder-name = username matches are used; a folder holding several people is skipped. Reviews from Israel are excluded by owner decision (Israel is left out of `FLAGS`).

## Fan art is generated

`tools/build_fan_art.py` traces footballer drawings from the owner's Drive folder `.football` (under `G:\My Drive\Notion`) into `assets/fan/*.svg` (vtracer) and rebuilds the wall between `<!-- fan:start -->` and `<!-- fan:end -->`. Add a drawing by listing it in the script's `PICKS` and re-running it. The page shows a quiet strip of 7 (4 on phones), in a random order on each visit; keep it small and faint, it is only fan art.

## Screenshots

`firdaus_fiverr_reference_pack/` (git-ignored, private: copies of the data files plus `screenshots/` of delivered Zaps) is source material. Before publishing a screenshot, look at it: use Zapier flow screenshots that show only step names; skip any that show email addresses, names or inbox contents. Copy used ones to `assets/work/` under neutral names (never a username).

## Front-end conventions

- Font: Notion's system stack (`ui-sans-serif, -apple-system, "Segoe UI", …`). No web fonts.
- Icons and flags: inline SVG `<symbol>`s in the sprite at the top of `<body>`, used with `<use href="#i-…">` or `#f-<country>`. Draw a new flag as a symbol. Windows has no flag-emoji glyphs, and the `country-flag-emoji-polyfill` build on jsdelivr was serving injected code (`alert(5)`).
- External code: none. Keep the page dependency-free.

## Motion

Scroll-driven CSS only (`animation-timeline: view()` / `scroll()`), inside `prefers-reduced-motion: no-preference` and `@supports`, so unsupported browsers get a static page.

- System: every section has its own entrance (`--enter` on the section) and shares one exit (`push-out`). Entrances animate `transform` / `clip-path`; the exit animates the separate `scale` + `opacity` properties so the two layers compose.
- `overflow: clip`, never `hidden`, on any ancestor of an animated element: `hidden` makes a scroll container and freezes `view()`.
- Headless Edge does not advance scroll timelines reliably, so screenshots and probes can't verify motion. Verify by scrolling in a real browser (Edge/Chrome).

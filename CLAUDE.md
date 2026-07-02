# sergeynasyrow-site — Project context for Claude

## What this is
Personal consulting website for Sergey Nasyrov (marketing practitioner, SMB niche).
Published at sergey-nasyrov.ru via Netlify, auto-deployed from this GitHub repo
(https://github.com/sergeynasyrov13-boop/sergeynasyrow-site). `index.html` is the live
production page — it assembles all 11 blocks into one page. `blocks/*.html` are the
original Tilda Zero-block exports, kept as design reference only; they are not deployed
and not part of the live build.

## File structure
```
index.html          — full assembled page (primary working file)
offer.html           — public offer (contract), served at /offer
privacy.html         — personal data processing policy, served at /privacy
sitemap.xml, robots.txt
blocks/             — individual Tilda Zero-block HTML files (reference; don't edit)
  nav.html, hero.html, dlya-kogo.html, about.html, audit.html,
  services.html, cases.html, how.html, faq.html, cta-final.html, footer.html,
  contact.html      — lead form, wired to Telegram Bot API (currently disabled in index.html)
assets/
  avatar.png        — Sergey's cutout photo (no background), used in hero
```
Netlify serves clean paths (`/offer`, `/privacy`) for the matching `.html` files
automatically — no `_redirects`/`netlify.toml` needed for this.

## Design system
- Background: `#F9F9F9` (page) / `#FFFFFF` (white cards)
- Accent: `#F0902C` orange
- Dark: `#1A1A1A` (audit section bg, footer)
- Font: Montserrat (400/500/600/700/800)
- Max-width: `1200px`, padding desktop `96px 64px`, tablet `72px 32px`, mobile `56px 20px`
- Breakpoints: 1200px / 900px / 768px / 560px / 480px

## Animation systems (all in index.html `<script>`)
1. **Scroll reveal** — `.reveal` (fade-up single), `.reveal-stagger` (nth-child cascade)
2. **Number counters** — hero trust bar: `animateCount(el, from, to, suffix, duration)`
3. **Ticker** — dark strip between hero and for-whom, CSS `@keyframes ticker-run`
4. **Audit cascade** — `.audit-cascade` + `.audit-item` slide in left-to-right on scroll
5. **Clock** — `.clock-hand` on SVG line in about section, CSS spin
6. **How steps** — `.how__steps` cascade + `num-glow` pulse on step numbers
7. **Cases carousel** — 3-up, arrow navigation, `animateMetric()` per card
8. **Pulse rings** — `.pulse-wrap` on CTA buttons (audit + hero + final)

## Cases carousel (index.html ~line 1940–2050 JS block)
- 5 cards, show 3 at a time, max index = 2
- `go(n)` sets `transform: translateX` on `#casesTrack`
- `data-count / data-prefix / data-suffix` on `.case-card__metric` drive counters
- 3 dots (one per scroll position)
- On resize: `go(idx)` recalculates step width

## Completed animation work (as of 2026-06-17)
- [x] Hero title `<br>` fix + CTA pulse ring
- [x] Counter animation (hero trust bar): 8 лет / ROMI 120%+ / 20+
- [x] Ticker strip
- [x] Middle pain card orange glow (`.pain-card--featured`)
- [x] Clock SVG hand animation
- [x] Audit text updated ("Разберём..." no "За 2 часа")
- [x] Audit cascade animation (4 checkmarks appear top-to-bottom)
- [x] Cases carousel redesigned (3-up, arrows, counter animation on metrics)
- [x] How steps cascade fade-in + num-glow on circles

## Pending (as of 2026-06-17)
- [ ] How block: sliding spotlight (orange highlight travels 01→02→03→04)
- [ ] Consistent block widths across all sections
- [ ] Mobile QA pass

## Status (as of 2026-07-02)
- [x] Public offer (`offer.html`) and privacy policy (`privacy.html`) written and live
      at `/offer` and `/privacy`. Real requisites: ИП Насыров Сергей Дамирович,
      ОГРНИП 326366800063559, ИНН 360206536641, НПД (4%/6%), счёт в Точке.
      Adapted from a public template (chipsanov.pro) with added clauses not in the
      source: confidentiality/NDA (art. 7 of the offer — relevant because Sergey gets
      access to clients' ad accounts), liability cap, force majeure, offer term/amendment
      clause, and a corrected 152-ФЗ response-time clause (10 рабочих, not calendar, days).
      Footer and the contact-form consent checkbox both link to these.
- [ ] **Contact form is intentionally disabled** (`blocks/contact.html` / the wired-up
      version in `index.html`) — it was turned off pending these legal docs, per commit
      `1f345c9 Disable contact form temporarily (pending legal docs)`. The docs now
      exist, but **do not re-enable the form without the user explicitly asking** — he
      said so directly on 2026-07-02.
- [ ] User still needs to file a personal-data-processing notification with Roskomnadzor
      (pd.rkn.gov.ru) — required before the form goes live and before adding any
      analytics (Метрика etc.), since the site collects leads pre-contract, which likely
      doesn't qualify for the "processing only for contract execution" exemption in
      ст. 22 ч.2 152-ФЗ. Not yet confirmed filed — check with the user before assuming
      this is settled.
- Domain across the whole repo/docs is `sergey-nasyrov.ru` (with hyphen) — an earlier
  session mixed this up with `sergeynasyrow.ru`; if you see that spelling anywhere, it's
  a leftover mistake, not a second domain.

## Tools installed (macOS)
| Tool | Command |
|------|---------|
| puppeteer | `node ~/screenshot.mjs` or inline script |
| rembg | `python3 -c "from rembg import remove..."` |
| pillow | `from PIL import Image` |
| sips | built-in macOS |

## Screenshot pattern (puppeteer inline)
```js
const puppeteer = require('/Users/sergey.nasyrov13/node_modules/puppeteer');
// setViewport 1280×800, goto file://.../index.html, networkidle0
// page.evaluate(() => el.scrollIntoView({ block: 'start' }))
// await new Promise(r => setTimeout(r, 600))
// page.screenshot({ path: '/tmp/out.png' })
```

## GitHub
repo: https://github.com/sergeynasyrow13-boop/sergeynasyrow-site
branch: main

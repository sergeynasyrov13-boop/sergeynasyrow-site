# sergeynasyrow-site — Project context for Claude

## What this is
Personal consulting website for Sergey Nasyrov (marketing practitioner, SMB niche).
Published at sergeynasyrow.ru via Tilda CMS (Zero-blocks). The repo is also used as a
standalone single-page preview: `index.html` assembles all 11 blocks into one page.

## File structure
```
index.html          — full assembled page (primary working file)
blocks/             — individual Tilda Zero-block HTML files (reference; don't edit)
  nav.html, hero.html, dlya-kogo.html, about.html, audit.html,
  services.html, cases.html, how.html, faq.html, cta-final.html, footer.html
assets/
  avatar.png        — Sergey's cutout photo (no background), used in hero
```

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

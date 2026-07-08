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
  contact.html      — lead form markup (currently disabled in index.html via FORM_ENABLED)
netlify/functions/send-lead.js — serverless function the form posts to (see Status below)
netlify.toml        — points Netlify at netlify/functions
assets/
  avatar.png        — original hero photo source (rembg output), kept for future edits
  avatar.webp       — actual deployed hero image (94KB, resized from the 2.4MB png)
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

## Status (as of 2026-07-08)

### Security incident — resolved
Commit `0aab8be` (predates this session) hardcoded a live Telegram bot token directly in
client-side JS in `index.html`, in this **public** repo. Confirmed exposed. User revoked
it via @BotFather and generated a new one same day. Fixed in commit `dc79d1b`:
- New token lives **only** in the Netlify env var `TELEGRAM_BOT_TOKEN` — never in code.
- Old token string still exists in earlier git history (harmless now that it's revoked,
  but if anyone asks, history rewrite is the cleanup — not done yet, low priority).
- If you ever touch `netlify/functions/send-lead.js` or the form's `submitContactForm`,
  do **not** reintroduce a hardcoded token/chat_id — always `process.env.*`.

### Lead form backend — rebuilt for 152-ФЗ data localization
The form (still `FORM_ENABLED = false`, still hidden — do not flip without the user
explicitly asking) now posts to `/.netlify/functions/send-lead` instead of calling
Telegram directly from the browser. That function:
1. Writes the lead first to a **Yandex Object Storage** bucket (`nasyrov-leads`,
   RF-hosted) via hand-rolled AWS SigV4 signing in `send-lead.js` — zero npm
   dependencies, don't add the AWS SDK, it's unnecessary.
2. Only then sends a Telegram notification, best-effort (failure there doesn't fail
   the request — the RF write is the record of truth).

Required Netlify env vars (all set by the user on 2026-07-08, confirmed working via a
direct `curl` test to the function returning 200): `TELEGRAM_BOT_TOKEN`,
`TELEGRAM_CHAT_ID`, `YC_ACCESS_KEY_ID`, `YC_SECRET_ACCESS_KEY`, `YC_BUCKET`.

Why this exists: the site's data flow was flagged as likely non-compliant with the
152-ФЗ art. 18 ч.5 requirement that personal data of RF citizens be primarily recorded
in an RF-located database — Telegram-only (foreign infra) didn't satisfy that. This fix
is a prerequisite for filing the Roskomnadzor notification (see next item) — the
notification should describe the corrected architecture, not the old one.

### Roskomnadzor notification — still not filed
Full field-by-field guide for pd.rkn.gov.ru was researched and saved to
`~/Downloads/РКН-чек-лист и заполнение уведомления.md` (user reads it in Obsidian).
Covers: what purposes/legal-basis/data-category checkboxes to select, and the
cross-border-transfer field (now answerable more favorably since primary storage is
RF-based, Telegram is just a secondary notification copy). Not yet confirmed submitted —
ask before assuming it's done.

### Domain/hosting confusion — resolved, was never a real problem
Spent a long thread debugging why `nasyrov.pro` seemed unreachable/slow. Root cause had
nothing to do with the site: a zombie WireGuard VPN tunnel (`utun6`) on the user's own
Mac was hijacking the default route. Fixed client-side via `sudo pkill -f wireguard`.
For the record: `nasyrov.pro` and `sergey-nasyrov.ru` both correctly point to this same
Netlify project (AWS Global Accelerator IP `75.2.60.5`) — confirmed via check-host.net
from Moscow/SPb nodes, both fast, no blocking. `sergeynasyrow.ru` (different spelling,
ends in "w") is a **separate, unrelated old Tilda-hosted site** — different ASN, not
part of this repo, don't touch it or assume it needs to match.

### Performance
`avatar.png` (2.4MB) → `avatar.webp` (94KB) shipped in `dc79d1b`, all references
(`<img>`, og:image, twitter:image, schema.org) updated. `avatar.png` kept in repo as the
rembg source for future re-edits, just no longer referenced by the live page.

### Open items
- [ ] Roskomnadzor notification — not filed
- [ ] Form still disabled — needs explicit user go-ahead to flip `FORM_ENABLED`
- [ ] Google Fonts loads from fonts.googleapis.com (foreign resource / minor cross-border
      exposure) — self-hosting the woff2 files would close this, not done
- [ ] Cookie banner — not needed yet (no analytics installed), will be needed if Яндекс.Метрика
      or similar gets added later
- [ ] Old exposed Telegram token still sits in git history — cosmetic cleanup, not urgent
      since it's revoked

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
repo: https://github.com/sergeynasyrov13-boop/sergeynasyrow-site
branch: main

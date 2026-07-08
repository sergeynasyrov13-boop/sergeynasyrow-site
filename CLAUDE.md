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

## Status (as of 2026-07-08, end of day)

Huge single-day session. The MAX/analytics work was already pushed (commits `82e169a`,
`103d6a6` — the latter fixed a Netlify secrets-scan build failure caused by an env var
value being written literally into this file; **never paste actual secret/ID values into
CLAUDE.md**, describe them instead). The form-enable + self-hosted-fonts work below is a
second batch, prepared locally, not yet pushed as of this writing — the user asked to
batch changes to conserve Netlify's monthly build-minute quota rather than pushing after
every small edit. Ask before pushing if it's unclear whether this batch already went out.

### Security incident — resolved
Commit `0aab8be` (predates this session) hardcoded a live Telegram bot token directly in
client-side JS in `index.html`, in this **public** repo. Confirmed exposed. User revoked
it via @BotFather and generated a new one. Old token string still exists in earlier git
history (harmless now that it's revoked; history rewrite would be the cosmetic cleanup,
not done, low priority). If you ever touch `netlify/functions/send-lead.js`, do **not**
reintroduce a hardcoded token — always `process.env.*`.

### Lead form backend — RF-only data flow (Telegram fully removed from this path)
The form (still `FORM_ENABLED = false` in `index.html`, still hidden — do not flip
without the user explicitly asking) posts to `/.netlify/functions/send-lead`. Current
architecture, after several iterations:
1. Full lead record (name/task/contact) written to a **Yandex Object Storage** bucket
   (`nasyrov-leads`, RF-hosted) via hand-rolled AWS SigV4 signing in `send-lead.js` —
   zero npm dependencies, don't add the AWS SDK.
2. Full record also sent as a **MAX messenger** notification (RF-jurisdiction, replaced
   Telegram for this specific internal-notification purpose) via `platform-api2.max.ru`.
   MAX's API serves a Mintsifry-issued TLS cert that Node doesn't trust by default — the
   two "Russian Trusted Root/Sub CA" PEM certs are pinned directly in `send-lead.js`.
   **The sub CA expires 2027-03-06** — if MAX notifications silently stop working after
   that date, refresh both PEM blocks from gu-st.ru (see comment in the file for exact
   URLs).

Required Netlify env vars: `YC_ACCESS_KEY_ID`, `YC_SECRET_ACCESS_KEY`, `YC_BUCKET` (set
2026-07-08, confirmed working) + `MAX_BOT_TOKEN`, `MAX_USER_ID` (bot: `zayavki_site` /
`id360206536641_2_bot`, recipient is Sergey's own MAX account — see Netlify env var for
the actual ID, deliberately not repeated here since Netlify's build-time secret scanner
flags env var values found anywhere in repo files; both confirmed working via a direct
round-trip test, message delivered). `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` are no
longer read by any code — vestigial, safe to leave set or delete in Netlify, doesn't
matter.

Why MAX instead of just anonymizing the Telegram ping: the user wants the whole pipeline
on RF infrastructure, not just PII-stripped. Telegram is still used elsewhere on the site
(footer/hero "message me" CTA linking to `@sergeynasyrov_bot`) — that's a separate,
user-initiated direct-contact channel, unrelated to the automated lead pipeline, and
was intentionally left alone.

### Roskomnadzor notification — filed, but needs a follow-up amendment
Base notification filed 2026-07-08, confirmation **№ 100345764**. Field-by-field guide
(with the values actually used) is saved to
`~/Downloads/РКН-чек-лист и заполнение уведомления.md` (user reads it in Obsidian) —
keep that file in sync if anything here changes again.

**Follow-up required:** Yandex.Metrika + Webvisor were added to the site *after* the
notification was filed, introducing a data category (IP address, cookies, behavioral/
session data) not covered in the original filing. An **«Уведомление об изменении
сведений»** (amendment, not a new filing — `pd.rkn.gov.ru/operators-registry/notification/updateform/`)
is needed, deadline **2026-07-23** (15 working days from 2026-07-08). As of end of
session the original notification is still "на рассмотрении" (under review) — the
amendment form likely won't accept edits until that review completes; the 15-day
deadline runs from when the new data started being collected, not from registration, so
there's slack. Check with the user whether this has been filed before assuming so.

### Cookie consent + Yandex.Metrika — added 2026-07-08
`index.html` now has a cookie-banner (`#cookieBanner`, bottom-fixed, dark card matching
site design system) that gates Metrika behind explicit accept/decline, stored in
`localStorage['cookie_consent']`. Counter ID `110507843`, `webvisor: true` (session
recording — user explicitly requested it after being told what it does). Deliberately
**no `<noscript>` pixel fallback** — that path would fire unconditionally for no-JS
visitors, bypassing the consent banner (which itself needs JS to render). `privacy.html`
was updated to disclose Webvisor explicitly and to correctly describe the split between
Telegram (public contact channel) and MAX (internal lead notifications) — see the
`#analytics` section. `privacy.html`'s publish date bumped to 2026-07-08 to match.

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
`avatar.png` (2.4MB) → `avatar.webp` (94KB), all references (`<img>`, og:image,
twitter:image, schema.org) updated. `avatar.png` kept in repo as the rembg source for
future re-edits, just no longer referenced by the live page.

### Fonts — self-hosted, Google Fonts fully removed
Earlier in the session, self-hosting was deferred because a fetch of the Google Fonts
CSS looked wrong (identical woff2 URL across all 5 weight declarations). Turned out that
was correct, not a bug: Montserrat v31 on Google Fonts is served as a **variable font**
(has `fvar`/`gvar`/`avar`/`STAT` tables — verified with `fonttools ttx -l`), so one file
legitimately covers the whole 400-800 weight range via the `wght` axis. Downloaded the 4
subsets actually needed (cyrillic, cyrillic-ext, latin, latin-ext — skipped vietnamese)
into `assets/fonts/*.woff2` (~145KB total) and replaced the `<link
href="fonts.googleapis.com/...">` in all three HTML files with local `@font-face`
declarations using `font-weight: 400 800` (a range, not a single value — that's what
makes one file serve every weight). Verified via a local `python3 -m http.server` (not
`file://`, which breaks absolute `/assets/...` paths) that fonts load with 200s and no
Google network calls happen at all anymore.

### Form — enabled
`FORM_ENABLED` flipped to `true` in commit after this Status section was last written.
Backend (Yandex Object Storage + MAX) was already verified end-to-end before flipping.

### Git history — user declined cleanup, leave it
Old (revoked, dead) Telegram token is still visible in early commits of the public repo.
Asked the user whether to rewrite history to scrub it — they declined (force-push to
main risk not worth it for a token that no longer works). **Don't rewrite history for
this on your own initiative** — it's a settled decision, not an oversight.

### Design/copy polish round — deployed 2026-07-08 (commit `3f7ffb3`)
- Favicon added: cropped from the hero photo, orange brand circle for browser tabs
  (`favicon.ico`, `favicon-32x32.png`, `favicon-16x16.png` — transparent corners, real
  circle), but `apple-touch-icon.png` is a plain **square** on purpose — iOS applies its
  own rounding and handles alpha transparency on touch icons poorly. If it still looks
  square in someone's tab, it's almost always favicon caching (very sticky, browser-level,
  separate from normal page cache) — check in an incognito window before assuming the
  files are wrong.
- Hero: no longer has the "Маркетолог-практик · МСБ" eyebrow label.
- `.pain-card` (the "Узнаёте свою ситуацию?" cards) are now `<a href="#contact"
  data-modal="contact">`, not `<div>` — they were visually card-like but did nothing
  when clicked. Has a hover lift now too.
- `.how` section has a `.section-cta` button after the steps (same pattern as after
  `#services`).
- `.cta-final__note` ("Одновременно работаю не более чем с 4 проектами") was removed
  entirely, not just hidden.
- Footer copyright line now includes "ИП Насыров С.Д. · ОГРНИП 326366800063559" next to
  the `/offer` link — required by ЗоЗПП to have operator info near the public offer,
  no strict rule on exact placement (footer/header/offer page all satisfy it).
- `.svc__example` ("Пример →" links on 4 service cards) moved from inline after the tag
  row to `position: absolute; top: 20px; right: 20px` — a corner badge. It used to blend
  into the orange `.svc__tag` pills right above it and effectively disappeared visually.
  `.svc` needed `position: relative` added for this to anchor correctly.
- Niches list copy: "Beauty" → "EdTech SaaS". SMM card tags gained "MAX".
- Several hanging prepositions/conjunctions (висячие предлоги) fixed with `&nbsp;` per
  user request — this is an ongoing site convention, already used extensively; when
  adding new copy, glue short prepositions/conjunctions (а, и, с, от, не, etc.) forward
  to the next word rather than leaving them to risk dangling at a line end.

### Open items
- [ ] RKN "уведомление об изменении сведений" for the analytics data category — deadline
      2026-07-23, blocked on the base notification leaving "на рассмотрении" status.
      Check with the user whether this has been filed before assuming so.

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

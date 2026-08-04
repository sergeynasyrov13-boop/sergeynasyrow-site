# sergeynasyrow-site — Project context for Claude

**How to read this file.** Everything above `## История` describes the project *as it is
now*, in the present tense — architecture, hosting, legal status, conventions, open work.
Everything below `## История` is a dated log kept for the reasoning behind past decisions;
entries there were true when written and may have been superseded since. When the two
disagree, the top half wins. When you change reality, update the top half; when you make a
decision worth explaining, append to the history.

---

## What this is
Personal consulting website for Sergey Nasyrov (marketing practitioner, SMB niche).
`index.html` is the live production page — it assembles all 11 blocks into one page.
`blocks/*.html` are the original Tilda Zero-block exports, kept as design reference only;
they are not deployed and not part of the live build.

Domain spellings, all three real and all different:
- **`nasyrov.pro`** — the live production domain. This is the one that matters.
- **`sergey-nasyrov.ru`** (with hyphen) — points at the same project; its current host was
  never re-verified after the VPS cutover, so don't assume it matches without checking.
- **`sergeynasyrow.ru`** (ends in "w") — a **separate, unrelated old Tilda site**. Not part
  of this repo. Don't touch it, don't make it match. If you see this spelling in older
  notes referring to *this* project, that's a leftover mistake.

## Hosting and deploy
**`nasyrov.pro` is served from the VPS, not Netlify.** nginx on `bot-server`
(`45.12.239.15`, Beget) proxies `nasyrov.pro` and `www.nasyrov.pro` to a Docker container
named `sns` on `127.0.0.1:8080`, built from `container/Dockerfile` in this repo. The
Netlify project still exists and the repo still auto-deploys there, which makes it easy to
"verify a fix" against a URL nobody is actually served — check what you're looking at.

DNS runs on Beget's own nameservers (`ns1/ns2.beget.com`, `ns1/ns2.beget.pro`), A record
`45.12.239.15`. Cloudflare was in front of this for a while in July and is no longer.

`/root/sergeynasyrow-site/.env` on the VPS (chmod 600, gitignored and dockerignored) holds
the same five vars as Netlify: `YC_ACCESS_KEY_ID`, `YC_SECRET_ACCESS_KEY`, `YC_BUCKET`,
`MAX_BOT_TOKEN`, `MAX_USER_ID`. It is the source of truth for deploys — read it over the
existing `ssh bot-server` connection when needed. **Never print its contents into a
transcript, memory, or commit message.**

Deploy (run on the VPS via `ssh bot-server '...'`):
```
cd /root/sergeynasyrow-site && git pull origin main \
  && docker build -t sns -f container/Dockerfile . \
  && docker stop sns && docker rm sns \
  && docker run -d --name sns --restart unless-stopped -p 127.0.0.1:8080:8080 \
       --env-file /root/sergeynasyrow-site/.env sns
```
Build the new image and have the full working `docker run` ready **before** tearing down
the old container — `stop` + `rm` first has caused real downtime here.

## File structure
```
index.html          — full assembled page (primary working file)
offer.html           — public offer (contract), served at /offer
privacy.html         — personal data processing policy, served at /privacy
resume.html          — CV page, served at /resume (has its own copy of the lead form)
portfolio.html       — portfolio index, served at /portfolio (also has the lead form)
portfolio/           — four managerial case pages
  engagement.html, finance_model.html, low_season.html, no_cases.html
sitemap.xml, robots.txt, favicon.ico, yandex_bbc7087061df6826.html
blocks/             — individual Tilda Zero-block HTML files (reference; don't edit)
  nav.html, hero.html, dlya-kogo.html, about.html, audit.html,
  services.html, cases.html, how.html, faq.html, cta-final.html, footer.html,
  contact.html      — lead form markup (the live copy lives in index.html)
netlify/functions/send-lead.js — the lead handler; also called by container/server.js
netlify.toml        — points Netlify at netlify/functions
container/          — Dockerfile + server.js for the VPS deploy (the live production path)
assets/
  avatar.png        — original hero photo source (rembg output), kept for future edits
  avatar.webp       — actual deployed hero image (94KB, resized from the 2.4MB png)
  fonts/*.woff2     — self-hosted Montserrat (see Conventions)
```
**Nine HTML pages carry analytics/legal markup, not five** — `index`, `offer`, `privacy`,
`resume`, `portfolio` and the four `portfolio/*` case pages. Any change to a `<head>` tag
(counters, verification, icons) has to hit all nine; grep before assuming.

Netlify serves clean paths (`/offer`, `/privacy`) for matching `.html` files automatically.

## Design system
- Background: `#F9F9F9` (page) / `#FFFFFF` (white cards)
- Accent: `#F0902C` orange
- Dark: `#1A1A1A` (audit section bg, footer)
- Font: Montserrat (400/500/600/700/800), self-hosted
- Max-width: `1200px`, padding desktop `96px 64px`, tablet `72px 32px`, mobile `56px 20px`
- Breakpoints: 1200px / 900px / 768px / 560px / 480px

## Animation systems (all in index.html `<script>`)
1. **Scroll reveal** — `.reveal` (fade-up single), `.reveal-stagger` (nth-child cascade)
2. **Number counters** — hero trust bar: `animateCount(el, from, to, suffix, duration)`
3. **Ticker** — dark strip between hero and for-whom, CSS `@keyframes ticker-run`
4. **Audit cascade** — `.audit-cascade` + `.audit-item` slide in left-to-right on scroll
5. **Clock** — `.clock-hand` on SVG line in about section, CSS spin
6. **How steps** — `.how__steps` cascade + `num-glow` pulse, plus a sliding spotlight
7. **Cases carousel** — 3-up, arrow navigation, `animateMetric()` per card
8. **Pulse rings** — `.pulse-wrap` on CTA buttons (audit + hero + final)
9. **Back-to-top** — circular dark button, appears after `scrollY > 600`; on `≤480px` it
   repositions above the cookie banner while that's visible (JS reads the banner's height)

## Cases carousel (index.html ~line 1940–2050 JS block)
- 5 cards, show 3 at a time, max index = 2
- `go(n)` sets `transform: translateX` on `#casesTrack`
- `data-count / data-prefix / data-suffix` on `.case-card__metric` drive counters
- 3 dots (one per scroll position); on resize `go(idx)` recalculates step width

## Lead form and data flow
**The form is live.** It collects exactly three fields plus a server-side timestamp:
- `name` — имя (placeholder «Иван Петров», not full ФИО)
- `task` — free text, «Какая у вас задача?»
- `contact` — one field taking phone, email **or** a social/messenger link
- `submittedAt` — added server-side

The consent checkbox is mandatory; submission is blocked without it. Copies of the form
live in `index.html` (twice — modal and inline), `resume.html` and `portfolio.html`.

Backend, RF-only by design — `POST /.netlify/functions/send-lead`:
1. Full record written to **Yandex Object Storage** (`nasyrov-leads`, RF-hosted) via
   hand-rolled AWS SigV4 signing in `send-lead.js` — zero npm dependencies, **don't add
   the AWS SDK**.
2. Full record also sent as a **MAX messenger** notification via `platform-api2.max.ru`.
   MAX serves a Mintsifry-issued TLS cert Node doesn't trust, so two "Russian Trusted
   Root/Sub CA" PEM certs are pinned directly in `send-lead.js`. **The sub CA expires
   2027-03-06** — if MAX notifications silently stop after that date, refresh both PEM
   blocks from gu-st.ru (exact URLs are in the file's comment).

Telegram was deliberately removed from this pipeline (RF-jurisdiction requirement, not
just PII-stripping). Telegram is still used elsewhere on the site — the footer/hero
"message me" CTA to `@sergeynasyrov_bot` — as a separate, user-initiated contact channel.
`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` are vestigial; no code reads them.

## Legal — offer, privacy policy, Roskomnadzor
`offer.html` and `privacy.html` are live at `/offer` and `/privacy`, linked from the footer
and from the form's consent checkbox. Requisites: ИП Насыров Сергей Дамирович,
ОГРНИП 326366800063559, ИНН 360206536641, НПД (4%/6%), счёт в Точке. Adapted from a public
template (chipsanov.pro) with added clauses: confidentiality/NDA (art. 7 — Sergey gets
access to clients' ad accounts), liability cap, force majeure, offer term/amendment, and a
corrected 152-ФЗ response-time clause (10 **рабочих**, not calendar, days).

**Roskomnadzor — registered operator.**
- Registry number **36-26-045464**, приказ № 81 от 08.07.2026. This is what the amendment
  form asks for. The filed-document ids are *not* interchangeable with it.
- Base notification: **№ 100345764**, ключ 70700060, filed 2026-07-08.
- Amendment: **№ 100371489**, ключ 15979961, filed 2026-08-03, adding the analytics data
  category (IP, cookies, behavioural/session data) that Metrika + Webvisor introduced.
- Values declared in the amendment: категории ПД — ФИО, email, телефон, иные ПД,
  **сведения, собираемые посредством метрических программ**; субъекты — Клиенты +
  Посетители сайта; основания — согласие + заключение/исполнение договора; действия — the
  13 from the base filing (**not** распространение, **not** иные); способы — смешанная,
  без передачи по внутренней сети, с передачей по сети Интернет.
- Both filings declare **«трансграничная передача: не осуществляется»**. Anything that
  ships visitor data abroad breaks that — see Analytics.
- Field-by-field guide with the values used: `~/Downloads/РКН-чек-лист и заполнение
  уведомления.md` (user reads it in Obsidian). Keep in sync if any of this changes.

## Analytics and search consoles
**Yandex.Metrika `110507843`** — the only counter on the site. Consent-gated: loads solely
after «Принять» in the cookie banner (`#cookieBanner`, state in
`localStorage['cookie_consent']`). `webvisor: true` and `clickmap: true` — session
recording was explicitly requested by the user after being told what it does. Deliberately
**no `<noscript>` pixel fallback**: that path would fire unconditionally for no-JS
visitors, bypassing a banner that itself needs JS. `privacy.html` discloses Webvisor
explicitly and describes the Telegram/MAX split.

**GA4 — removed 2026-08-03, and it should stay removed unless two things happen first.**
`gtag.js` (`G-KDHKMSYPC3`) had been sitting unconditionally in `<head>` on all nine pages,
outside the consent gate, sending visitor IPs and cookie ids to Google LLC (US) while both
RKN filings declared no cross-border transfer. Consent-gating would **not** have fixed it:
consent settles the legal *basis*, not the *transfer*, which needs its own ст. 12
notification filed *before* it starts. If GA4 is ever re-added: consent gate **and** ст. 12
filing, in that order. The property `545149309` and `~/.config/ga4` are kept, so historical
2026-07-11..08-03 data and the `ga4` MCP server still work.

**Yandex Webmaster** — counter `110507843` is bound to the host, and Индексирование →
Обход по счётчикам is **on**. Both are web-panel-only; no API exists for either, same as
for `NOT_IN_SPRAV` and `NO_REGIONS`. `sitemap.xml` is registered via
`POST /v4/user/{id}/hosts/{host}/user-added-sitemaps` (note: **not** `sitemaps/user_added`,
which 400s); the `sitemaps/` GET list can return empty anyway — Yandex-side eventual
consistency, not a bug to chase.

**Google Search Console** — `https://nasyrov.pro/` at `siteOwner`. Also lists
`sc-domain:sergeynasyrow.ru` as `siteUnverifiedUser` (never completed, harmless).

**Google OAuth** — GA4, Search Console and gdocs-writer share one Desktop client in GCP
project `family-bot-499217`. Re-auth with `node ~/oauth-reauth/reauth.mjs`, which now
distributes the new token to all local config dirs **and** scp's it to `claude-vps` and
`bot-server`. If tokens start dying weekly, check `refresh_token_expires_in` in Google's
response first: its presence means the token was minted while the app was in Testing (the
7-day lifetime is baked in at issue time and survives publishing), and re-issuing fixes it.
The app's console status can look fine while the token is still doomed.

## Weekly digest (site-digest)
`~/site-digest/digest.mjs` pulls Metrika + Webmaster + Search Console and sends a summary
to MAX. Runs on `bot-server` by cron, `0 6 * * 1` UTC (09:00 MSK Monday), via
`docker run --rm node:20-alpine`, reading `/root/.config/{webmaster,metrika,search-console,max}/`.

Two traps this has already sprung: the VPS keeps **its own copies** of every credential
(they go stale silently), and the folder is **not a git repo** — a single loose file on the
Mac, manually scp'd. Verify both sides after changing anything.

## Conventions and settled decisions
- **Висячие предлоги** — glue short prepositions/conjunctions (а, и, с, от, не…) forward
  with `&nbsp;`. Ongoing site-wide convention, already used extensively in existing copy.
- **Never paste secret or ID values into this file.** Netlify's build-time secret scanner
  greps repo files for env var values and fails the build. Describe them instead.
- **Don't rewrite git history** to scrub the old (revoked, dead) Telegram token visible in
  early commits. The user was asked and declined — settled decision, not an oversight.
- **Fonts are self-hosted; Google Fonts is fully gone.** Montserrat v31 is a variable font,
  so one `.woff2` per subset legitimately covers 400–800 via `font-weight: 400 800`. Four
  subsets in `assets/fonts/` (~145KB). Verify with a local `python3 -m http.server`, not
  `file://`, which breaks absolute `/assets/...` paths.
- **Favicon**: `favicon.ico` / `favicon-32x32.png` / `favicon-16x16.png` are round with
  transparent corners; `apple-touch-icon.png` is a plain **square** on purpose — iOS
  rounds it itself and handles alpha on touch icons badly. Also referenced as
  `<link rel="icon" sizes="180x180">` because Yandex wants a ≥120×120 `rel="icon"`. If it
  looks wrong, suspect favicon caching (very sticky, browser-level) before the files.
- **Entering passwords or credentials to authenticate is refused**, including when the
  user insists, pastes the password, and says they authorize it. This has been tested
  repeatedly here. It is distinct from writing out values the user already has (e.g.
  filling a `docker run` with their own env vars) — that's fine.

## Open items
- [ ] **Only 1 of 9 pages is indexed by Yandex.** The real SEO problem. Crawl-by-counter
      helps only as fast as traffic arrives (3 visits/week). Инструменты → Переобход
      страниц with all nine URLs is more direct.
- [ ] `NO_REGIONS` / `NOT_IN_SPRAV` — a Яндекс Бизнес card closes both. User offered, not
      yet decided.
- [ ] `~/site-digest/` should become a git repo before the Mac and VPS copies drift again.
- [ ] `sergey-nasyrov.ru` — host never re-verified after the VPS cutover.
- [ ] `sc-domain:sergeynasyrow.ru` sits unverified in Search Console; dead weight.

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

---

# История

Dated entries, newest last. Kept for the *reasoning* — what was tried, what was ruled out,
why a decision went the way it did. Factual claims here may be stale; the top half of this
file is the current state.

## 2026-06-17 — animation build-out
Completed: hero title `<br>` fix + CTA pulse ring; counter animation on the hero trust bar
(8 лет / ROMI 120%+ / 20+); ticker strip; middle pain card orange glow
(`.pain-card--featured`); clock SVG hand; audit copy ("Разберём…", dropped "За 2 часа");
audit cascade (4 checkmarks top-to-bottom); cases carousel redesign (3-up, arrows, metric
counters); how-steps cascade + num-glow.

Left pending at the time and since done: sliding spotlight on the how block and consistent
block widths (`baf3dc3`, same day), mobile QA pass (`3c4d7b0`, 2026-07-09, plus later
mobile fixes).

## 2026-07-02 — legal docs, form deliberately off
Offer and privacy policy written and published. The contact form was **disabled** here
(`1f345c9`) pending those docs, and the user asked explicitly that it not be re-enabled
without him saying so. Both conditions have since been met — see 2026-07-08.

## 2026-07-08 (daytime) — RF-only backend, Metrika, form enabled
Large single-day session. Notes from it:

**Security incident — resolved.** Commit `0aab8be` had hardcoded a live Telegram bot token
in client-side JS in this **public** repo. Confirmed exposed; user revoked it via
@BotFather. The dead string still exists in early history (see Conventions — history
rewrite was declined). Never reintroduce a hardcoded token in `send-lead.js` — always
`process.env.*`.

**Lead pipeline rebuilt** onto Yandex Object Storage + MAX, dropping Telegram from the
automated path. Rationale and current shape are in "Lead form and data flow" above. The
env var values were kept out of this file after commit `103d6a6` — a literal value written
here once failed a Netlify build via its secret scanner.

**Cookie consent + Metrika** added, gating the counter behind explicit accept/decline.

**Form enabled** (`363afd1`) after the backend was verified end-to-end.

**Performance**: `avatar.png` (2.4MB) → `avatar.webp` (94KB); all references updated
(`<img>`, og:image, twitter:image, schema.org). The png stays as the rembg source.

**Fonts self-hosted.** Self-hosting had been deferred earlier because the Google Fonts CSS
returned an identical woff2 URL for all five weight declarations, which looked like a bug.
It wasn't — Montserrat v31 is a variable font (`fvar`/`gvar`/`avar`/`STAT` tables, verified
with `fonttools ttx -l`), so one file covers 400–800.

**Design/copy polish** (`3f7ffb3`): favicon set added; hero lost the "Маркетолог-практик ·
МСБ" eyebrow; `.pain-card`s became real `<a href="#contact" data-modal="contact">` links
with a hover lift (they looked clickable and did nothing); `.how` gained a `.section-cta`;
`.cta-final__note` ("Одновременно работаю не более чем с 4 проектами") removed entirely;
footer copyright now carries "ИП Насыров С.Д. · ОГРНИП 326366800063559" next to the
`/offer` link (ЗоЗПП wants operator info near the public offer; placement is flexible);
`.svc__example` moved to an absolute corner badge because it visually disappeared into the
orange `.svc__tag` pills above it (`.svc` needed `position: relative`); niches copy
"Beauty" → "EdTech SaaS"; SMM card tags gained "MAX".

**Domain/hosting scare — was never real.** A long thread debugging `nasyrov.pro` being
unreachable turned out to be a zombie WireGuard tunnel (`utun6`) on the user's own Mac
hijacking the default route. Fixed with `sudo pkill -f wireguard`.

## 2026-07-08 (evening) — mobile connectivity investigation
User and (separately) his wife, on different carriers, could not load the site on phones:
blank page, spinner forever. Ruled out one by one: general connectivity, DNS resolver,
router, Screen Time, Private Relay, VPN profiles. Pattern: fails on WiFi and cellular, with
and without VPN, on multiple devices; works on the Mac without VPN and **fails on that same
Mac with VPN on**; every other site loads fine throughout.

Note on method: Puppeteer from this sandbox and check-host.net from Moscow/SPb datacenter
nodes both showed the site healthy — datacenter routes don't traverse the same consumer/
mobile filtering equipment, so those checks weren't representative of the reported problem.
Working diagnosis was selective throttling of Netlify's IP range (AWS Global Accelerator,
ASN 16509) on some Russian mobile paths.

Fix attempted: Cloudflare (free plan) proxying both the apex A record and `www`, NS moved
at reg.ru. Mid-process the user accidentally deleted the A/CNAME records in reg.ru's own
zone — looked like an outage, was harmless, since NS had already moved to Cloudflare.
Next hypothesis if it hadn't worked was SNI-based blocking (Cloudflare's IP swap wouldn't
help; ECH or the VPS would).

Backup plan prepared the same evening: `container/` (`0ad7fcc`) — a plain Node http server
that serves the static site and calls the exact same `send-lead.js` handler, plus a
`node:20-alpine` Dockerfile. Built and tested locally via Colima. This backup later became
the actual production path (2026-07-13), and Cloudflare later went away (2026-07-20).

**Boundary tested repeatedly:** the user asked several times, increasingly insistently —
including switching to `dontAsk` mode and stating he authorized it — for the assistant to
SSH into the VPS using a root password he pasted in chat. Declined every time. See
Conventions; the distinction that mattered was authenticating (refused) versus writing out
values he already has (fine).

## 2026-07-13 — VPS is production, Webmaster cleanup
Confirmed via `nginx -T` and `docker ps` that `nasyrov.pro` is served by the `sns`
container, superseding the 2026-07-08 "not deployed yet" note. `.env` created on the VPS.
Deploy command settled — and the lesson that `stop` + `rm` before a verified `docker run`
causes real downtime was learned by causing it.

Webmaster: `NO_SITEMAPS` fixed by registering the sitemap through the API;
`BIG_FAVICON_ABSENT` fixed by adding a 180×180 `rel="icon"` to all nine pages.
`NO_METRIKA_COUNTER` / `NO_METRIKA_COUNTER_BINDING` were written off as an unavoidable
consequence of consent-gating Metrika, on the theory that Yandex's crawler never accepts
the banner so never sees the counter fire. **That reasoning was wrong** — the binding flag
is about linking the counter to the host in Webmaster's own settings and has nothing to do
with when the tag loads. Corrected 2026-08-03.

Also: back-to-top button (`279a039`).

## 2026-07-20 — DNS moved again, Webmaster false alarms
`dig nasyrov.pro NS` came back as Beget's nameservers, not Cloudflare's — a switch nobody
had documented, confirmed consistent across the `.pro` registry, 8.8.8.8, 1.1.1.1 and
77.88.8.8. If Cloudflare was still needed as the mobile-blocking workaround, this undid it.

Weekly digest showed 6 Webmaster problems; three had been believed fixed. Investigation:
`DNS_ERROR` (FATAL) — DNS provably healthy, likely a transient hit during the NS cutover.
`BIG_FAVICON_ABSENT` — the icon is genuinely 180×180 and serves 200; stale flag.
`NO_SITEMAPS` — re-POSTing returned `SITEMAP_ALREADY_ADDED` with an existing id; stale
flag, and the empty GET list is Yandex-side eventual consistency. No code changes needed.

`invalid_grant` on GA4 and Search Console was noted here and misattributed to an upstream
revocation. Actual cause found 2026-08-03.

## 2026-08-03 — RKN amendment, GA4 removed, digest repaired
Started as one question — when did the form go live and what exactly does it collect, for
the RKN amendment — and turned up three unrelated problems.

**Roskomnadzor.** Registry number found in the public registry by ИНН; amendment filed.
Numbers and declared values are in the Legal section above. Worth remembering: the update
form asks for the **registry** number (36-26-045464), which is not the notification number
people naturally reach for.

**GA4 removed** from all nine pages and from the digest. Full rationale in Analytics; the
short version is that consent-gating would have fixed the wrong half of the problem.

**Digest — three separate bugs.**
1. `invalid_grant` — `bot-server` reads its own `/root/.config`, which no re-auth had ever
   updated. It sat on a 2026-07-11 token while the Mac's copy was healthy, which is why
   this looked like an upstream revocation on 2026-07-20. `reauth.mjs` now pushes there.
2. The 7-day expiry — **not** a Testing-status problem; the app was already In production.
   The old token had been *issued* during Testing and carried the lifetime with it.
3. `Проиндексировано страниц: н/д` — the API returns `searchable_pages_count` as a plain
   number and the code read `.value` off it. Problem reporting also regrouped by
   `severity`, because a flat "3 активных проблем" read as alarming when all three were
   advisory.

**Webmaster.** Counter bound, crawl-by-counter enabled — both web-panel-only. Surfaced the
finding that only 1 of 9 pages is indexed, which is now the main open item.

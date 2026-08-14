---
description: How to find job postings matching a person's master resume and search preferences - two-tier search (direct ATS API lookup first, WebSearch/WebFetch fallback), fit filtering, recording every shortlisted job, and the feedback loop for refining future searches. Use during /find-jobs.
---

# Job Search

## Prerequisites
- Master resume must exist and be approved (per the `intake` skill) — job search draws on it for search terms and fit judgment.
- `job_search_preferences.md` should exist. If it doesn't yet, capture it first (see `/find-jobs`'s flow) before searching — target titles, location constraints, deal-breakers, comp floor if shared.

## Two-Tier Search Strategy
Prefer direct API lookup over scraping wherever possible — real testing found API lookups return clean, reliable data at a much higher hit rate than scraping HTML career pages (roughly 15-20% hit rate scraping vs. near-zero request failures via direct API, once pointed at a working endpoint).

### Tier 1: Direct ATS API lookup (preferred)
For any company already known by name (from the person's preferences, a prior search, or general knowledge), query its job-board API directly via `scripts/job_search/query_job_boards.py`. Supported platforms: Greenhouse, Lever, Workable, SmartRecruiters, Ashby — see `JOB_SEARCH_API_ENDPOINTS.md` (Resume Workspace project) for the full endpoint reference, field names, and known issues per platform.

Run it via Bash with config built from that person's `job_search_preferences.md`:
```
python scripts/job_search/query_job_boards.py --config <path-to-a-generated-config.json>
```
Never hardcode company names, keywords, or location when building that config — always derive it from the person's own preferences file. The script already handles freshness filtering and local-area-or-remote filtering (on by default) — don't reimplement that logic conversationally, just feed it correct input and read its output.

If a company 404s on a platform it visibly uses (the public API isn't enabled for every account — see the endpoints doc), that's inconclusive, not a sign the company/slug is wrong. Fall through to Tier 2 for that company.

### Tier 2: WebSearch + WebFetch fallback
For companies not resolvable via a known ATS, fall back to a layered search:
1. Broad `WebSearch` (credentials + role + location/remote) to surface **named companies/opportunities** — filter out obvious aggregator listing pages by title alone as a cheap first pass.
2. For each promising named lead, search specifically for **that company's own careers page** — more stable and authoritative than an aggregator's copy.
3. If the company's own careers page doesn't show postings directly, follow through to whatever **underlying ATS platform** it links to — and if that's one of the Tier 1 platforms, switch back to Tier 1 for it.
4. Every candidate that survives gets `WebFetch`'d and judged before being recorded — three outcomes:
   - Reads as one genuine single-posting job description → record it.
   - Reads as a listings/aggregator page (multiple jobs mixed together) → **discard entirely.** Not recorded, not shown, not logged — pure junk for this purpose.
   - Fetch fails outright (404, JS-shell, cookie-gated, blocked) but was clearly a link to one specific posting → still record it, with an empty `Job Descriptions/<Company>.txt` for the person to paste into later. **Expect this to be common, not rare** — tell the person up front, same spirit as the PDF-formatting expectation-setting in `pdf-layout-standards`.

**Keep searching until enough good matches are found** — across both tiers, one company or one query is not enough. Query multiple companies, issue additional searches, until a reasonable shortlist exists.

## Fit Filtering
Judge every candidate against the master resume with the same honesty as `resume-tailoring`'s fit/gap gate — don't pad the shortlist with weak matches just to have more to show. Flag real mismatches explicitly (wrong location even on an otherwise strong match, credential gaps, experience-level stretches like "requires 6+ years of X the person doesn't have") rather than silently omitting them or including them without comment.

## Recording — Every Shortlisted Job, Immediately
This happens *before* presenting the shortlist to the person, not conditional on their reaction:
1. Get the JD text — directly from the API response if the platform includes full descriptions (Lever does; most others don't and still need a `WebFetch`/visit to the posting URL), or via `WebFetch` (Tier 2).
2. Write it to `Job Descriptions/<Company>.txt` — or an empty file if the text couldn't be captured (the fetch-fails outcome above). If a second role at the same company is also being logged, use `<Company> - <Title>.txt` instead to avoid a naming collision.
3. Add a row to `JOB_SEARCH_LOG.md` (copy `scripts/templates/JOB_SEARCH_LOG_TEMPLATE.md` to `JOB_SEARCH_LOG.md` first if it doesn't exist yet) with status `Viewed`. Source is the specific ATS platform (Tier 1) or `websearch` (Tier 2).

## Presenting the Shortlist
Stop and wait, same checkpoint discipline as everything else in this plugin. Show title / company / location / one-line fit note / link per posting, referencing what's now already recorded — don't just describe them, they're real files at this point.

## Feedback Loop — Learned Preferences
When the person reacts to the shortlist (approves some, dismisses others, explains why), watch for anything that sounds like a standing preference ("I don't want staffing agencies," "too far, I need something within 20 minutes of home"). **Ask before writing it as a rule in `job_search_preferences.md`'s "Learned from feedback" section — never infer silently from behavior alone.** Once confirmed, timestamp and note *why* (e.g. "excludes staffing agencies (confirmed 2026-08-15, after being shown a contract-to-hire staffing post)"), and factor it into future search query construction and result filtering.

## Guardrails
- **Never auto-apply, never submit anything, never fill out a form on the person's behalf.** This skill only ever surfaces, records, and shortlists.
- **Respect platform terms of service.** Prefer `WebSearch` (normal search) and fetching public job posting pages (normal browsing) over anything requiring login, bypassing a paywall, or scraping against a site's terms.
- **Every company name, keyword, and location value is external configuration from that person's own workspace — never hardcode any of it in this skill or in `query_job_boards.py`.** A real mistake caught and corrected during this plugin's development: an early draft of the query script had a specific person's location and company list hardcoded as defaults. Don't repeat it.
- **A freshness filter is mandatory, even against a clean API response.** A working, structured API can still return years-stale postings (confirmed firsthand — see `JOB_SEARCH_API_ENDPOINTS.md`'s Known Issues). "The request succeeded" and "the data is current" are different questions.
- **Local-area-or-remote only, by default.** Exclude onsite postings outside the person's local area unless they've asked to see relocation options too.

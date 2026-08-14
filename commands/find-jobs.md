---
description: Search for job postings matching this person's profile and preferences, record every good match, and present a shortlist.
argument-hint: [optional: a specific company to check, or a search focus]
---

Run a job search for this person, following the `job-search` skill.

1. Check for `job_search_preferences.md` in the workspace root. If it doesn't exist yet, run `/job-search-preferences` first — don't search with no criteria. If it exists but looks thin (e.g. no target titles), confirm with the person whether it's ready to search from before proceeding.
2. Build search input from the master resume + `job_search_preferences.md` (target titles/roles as keywords, location as local area, any companies already known from preferences or prior search rounds).
3. Tier 1: for known companies, query `scripts/job_search/query_job_boards.py` directly (see the `job-search` skill for exact invocation). Tier 2: `WebSearch`/`WebFetch` fallback for anything not resolvable via a known ATS. Keep searching — multiple companies, multiple queries — until a reasonable shortlist exists, not just one call's worth of results.
4. Record every job that survives fit filtering **before** presenting anything: JD text (or empty placeholder) into `Job Descriptions/<Company>.txt`, plus a row in `JOB_SEARCH_LOG.md` with status `Viewed`.
5. Present the shortlist and stop — title / company / location / one-line fit note / link per posting. Encourage the next step (per the momentum principle) without chaining automatically into anything else.
6. As the person reacts, apply the feedback loop: ask before writing any new standing preference into `job_search_preferences.md`'s "Learned from feedback" section.
7. For anything the person wants to move forward on, hand off to the normal per-application loop (`/evaluate-jd` → `/tailor-resume` → `/generate-pdf`) — this command's job ends at the shortlist, it doesn't chain into tailoring automatically.

Arguments (if provided) can narrow the search — e.g. a specific company name to check via Tier 1, or a focus area: $ARGUMENTS

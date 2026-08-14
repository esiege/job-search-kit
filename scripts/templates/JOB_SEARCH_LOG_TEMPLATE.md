# Job Search Log

Tracks every job posting surfaced by `/find-jobs` (or the `job-search` skill more generally): where it came from, what its current status is, and where its saved JD text lives.

## Rule going forward
1. **Every job that makes the shortlist gets a row here immediately** — the moment it's recorded (JD text or empty placeholder in `Job Descriptions/<Company>.txt`), not only if the person decides to pursue it. See `skills/job-search/SKILL.md`.
2. **Status starts at `Viewed`** and updates to **`Resume Created`** automatically once `/tailor-resume`/`/generate-pdf` completes for that company — this happens as part of those commands, not as a separate manual step.
3. **Never delete a row**, even for a company the person passed on. This is the record that keeps re-runs of `/find-jobs` from re-surfacing the same postings as if they were new.
4. **Source** records which lookup found it — a specific ATS platform (`greenhouse`, `lever`, `workable`, `smartrecruiters`, `ashby`) via direct API lookup, or `websearch` for the `WebSearch`/`WebFetch` fallback path. See `JOB_SEARCH_API_ENDPOINTS.md` in the Resume Workspace project for what each platform source means.
5. If two different roles at the same company both get logged, disambiguate the `Job Descriptions/` filename as `<Company> - <Title>.txt` rather than colliding on `<Company>.txt`.

## Postings

| Title | Company | Location | Link | Source | Date Found | Status | Notes |
|---|---|---|---|---|---|---|---|

"""
Query known ATS job-board APIs directly for a configured list of companies,
normalize results to a common shape, filter by keyword relevance, posting
recency, and local/remote scope, and print a results table.

This script has NO person-specific defaults on purpose - companies,
keywords, and local area always come from --config (or the individual
--keywords/--local-area flags). Per the plugin's data-separation rule,
nothing about any specific person's job search belongs in job-search-kit
itself; that data lives in that person's own workspace and gets passed in
at call time (eventually via the /find-jobs skill reading their
job_search_preferences.md).

See JOB_SEARCH_API_ENDPOINTS.md (Resume Workspace project) for the
endpoint reference this was built from - field names were confirmed
against real API responses, not guessed from docs alone.

Config file shape (JSON), passed via --config:
{
  "companies": {
    "greenhouse": ["<board_token>", ...],
    "lever": ["<site>", ...],
    "workable": ["<account>", ...],
    "smartrecruiters": ["<company>", ...],
    "ashby": ["<company>", ...]
  },
  "keywords": ["<title keyword>", ...],
  "local_area": ["<place name>", ...]
}
All top-level keys optional except "companies"; keywords/local_area can
also be passed as --keywords/--local-area instead.

Usage:
  python query_job_boards.py --config path/to/config.json
  python query_job_boards.py --companies-json '{"greenhouse":["acme"]}' --keywords "cpc,billing" --local-area "Anytown,YourState"
"""
import argparse
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

USER_AGENT = "job-search-kit/0.1 (job board API aggregation)"


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)


def parse_date(value):
    """Best-effort parse across the date shapes seen: ISO8601 with offset,
    epoch millis, or plain YYYY-MM-DD. Returns a UTC datetime or None."""
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
            return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
        s = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(s)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (ValueError, TypeError, OSError):
        return None


def query_greenhouse(token):
    data, err = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs")
    if err:
        return [], err
    results = []
    for job in data.get("jobs", []):
        location = (job.get("location") or {}).get("name")
        results.append({
            "title": job.get("title"),
            "company": job.get("company_name") or token,
            "location": location,
            # No explicit remote flag from Greenhouse - location text is the only signal.
            "is_remote": "remote" in (location or "").lower(),
            "url": job.get("absolute_url"),
            "posted": parse_date(job.get("updated_at") or job.get("first_published")),
            "source": "greenhouse",
        })
    return results, None


def query_lever(site):
    data, err = fetch_json(f"https://api.lever.co/v0/postings/{site}?mode=json")
    if err:
        return [], err
    results = []
    for job in data:
        cats = job.get("categories", {}) or {}
        results.append({
            "title": job.get("text"),
            "company": site,
            "location": cats.get("location"),
            "is_remote": (job.get("workplaceType") or "").lower() == "remote",
            "url": job.get("hostedUrl"),
            "posted": parse_date(job.get("createdAt")),
            "source": "lever",
        })
    return results, None


def query_workable(account):
    data, err = fetch_json(f"https://apply.workable.com/api/v1/widget/accounts/{account}")
    if err:
        return [], err
    results = []
    for job in data.get("jobs", []):
        loc_parts = [p for p in (job.get("city"), job.get("state"), job.get("country")) if p]
        is_remote = bool(job.get("telecommuting"))
        results.append({
            "title": job.get("title"),
            "company": data.get("name") or account,
            "location": ", ".join(loc_parts) if loc_parts else ("Remote" if is_remote else None),
            "is_remote": is_remote,
            "url": job.get("url") or job.get("shortlink"),
            "posted": parse_date(job.get("published_on") or job.get("created_at")),
            "source": "workable",
        })
    return results, None


def query_smartrecruiters(company):
    data, err = fetch_json(f"https://api.smartrecruiters.com/v1/companies/{company}/postings")
    if err:
        return [], err
    results = []
    for job in data.get("content", []):
        loc = job.get("location", {}) or {}
        is_remote = bool(loc.get("remote"))
        results.append({
            "title": job.get("name"),
            "company": (job.get("company") or {}).get("name") or company,
            "location": loc.get("fullLocation") or ("Remote" if is_remote else None),
            "is_remote": is_remote,
            "url": f"https://api.smartrecruiters.com/v1/companies/{company}/postings/{job.get('id')}",
            "posted": parse_date(job.get("releasedDate")),
            "source": "smartrecruiters",
        })
    return results, None


def query_ashby(company):
    data, err = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{company}?includeCompensation=true")
    if err:
        return [], err
    results = []
    for job in data.get("jobs", []):
        is_remote = bool(job.get("isRemote"))
        results.append({
            "title": job.get("title"),
            "company": company,
            "location": job.get("location") or ("Remote" if is_remote else None),
            "is_remote": is_remote,
            "url": job.get("jobUrl"),
            "posted": parse_date(job.get("publishedAt")),
            "source": "ashby",
        })
    return results, None


QUERY_FUNCS = {
    "greenhouse": query_greenhouse,
    "lever": query_lever,
    "workable": query_workable,
    "smartrecruiters": query_smartrecruiters,
    "ashby": query_ashby,
}


def is_relevant(title, keywords):
    if not keywords:
        return True
    t = (title or "").lower()
    return any(k.lower() in t for k in keywords)


def is_fresh(posted, max_age_days):
    if posted is None:
        return True  # unknown date - don't discard, just can't confirm freshness
    age = datetime.now(timezone.utc) - posted
    return age <= timedelta(days=max_age_days)


def is_local_or_remote(result, local_area):
    if result.get("is_remote"):
        return True
    if not local_area:
        return True  # no local area configured - don't filter on location at all
    location = (result.get("location") or "").lower()
    return any(area.lower() in location for area in local_area)


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default=None, help="Path to a JSON config file (see module docstring for shape)")
    parser.add_argument("--companies-json", default=None, help="Inline JSON, same shape as config's 'companies' key - alternative to --config")
    parser.add_argument("--keywords", default=None, help="Comma-separated title keywords to filter to")
    parser.add_argument("--local-area", default=None, help="Comma-separated place names to treat as local, alongside anything remote")
    parser.add_argument("--max-age-days", type=int, default=545, help="Discard postings older than this (default ~18 months)")
    parser.add_argument("--include-relocation", action="store_true", help="Don't filter out onsite postings outside the local area")
    args = parser.parse_args()

    config = load_config(args.config) if args.config else {}

    companies = config.get("companies") or (json.loads(args.companies_json) if args.companies_json else None)
    if not companies:
        parser.error("No companies configured - pass --config or --companies-json. This script has no built-in company list on purpose (see module docstring).")

    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else config.get("keywords") or []
    local_area = [a.strip() for a in args.local_area.split(",")] if args.local_area else config.get("local_area") or []

    all_results = []
    errors = []
    for platform, tokens in companies.items():
        func = QUERY_FUNCS.get(platform)
        if func is None:
            errors.append((platform, "(config)", f"unknown platform, must be one of {list(QUERY_FUNCS)}"))
            continue
        for token in tokens:
            results, err = func(token)
            if err:
                errors.append((platform, token, err))
                continue
            all_results.extend(results)

    relevant = [r for r in all_results if is_relevant(r["title"], keywords)]
    fresh_relevant = [r for r in relevant if is_fresh(r["posted"], args.max_age_days)]
    stale_relevant = [r for r in relevant if not is_fresh(r["posted"], args.max_age_days)]

    if args.include_relocation:
        in_scope, relocation_only = fresh_relevant, []
    else:
        in_scope = [r for r in fresh_relevant if is_local_or_remote(r, local_area)]
        relocation_only = [r for r in fresh_relevant if not is_local_or_remote(r, local_area)]

    total_companies = sum(len(v) for v in companies.values())
    print(f"Total postings fetched across {total_companies} companies: {len(all_results)}")
    print(f"Keyword-relevant: {len(relevant)}" + (" (no keyword filter applied)" if not keywords else ""))
    print(f"  -> fresh (<= {args.max_age_days} days old or undated): {len(fresh_relevant)}")
    print(f"  -> discarded as stale: {len(stale_relevant)}")
    if not args.include_relocation:
        note = " (no local area configured - remote-only filter applied)" if not local_area else ""
        print(f"  -> local/remote (shown by default): {len(in_scope)}{note}")
        print(f"  -> discarded as relocation-only (use --include-relocation to see): {len(relocation_only)}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for platform, token, err in errors:
            print(f"  - {platform}/{token}: {err}")
    print()

    in_scope.sort(key=lambda r: (r["posted"] is None, r["posted"]), reverse=True)

    col_widths = {"title": 48, "company": 20, "location": 22, "posted": 12, "source": 15}
    header = f"{'Title':<{col_widths['title']}} {'Company':<{col_widths['company']}} {'Location':<{col_widths['location']}} {'Posted':<{col_widths['posted']}} {'Source':<{col_widths['source']}}"
    print(header)
    print("-" * len(header))
    for r in in_scope:
        title = (r["title"] or "")[:col_widths["title"] - 1]
        company = (r["company"] or "")[:col_widths["company"] - 1]
        location = (r["location"] or "")[:col_widths["location"] - 1]
        posted = r["posted"].strftime("%Y-%m-%d") if r["posted"] else "unknown"
        print(f"{title:<{col_widths['title']}} {company:<{col_widths['company']}} {location:<{col_widths['location']}} {posted:<{col_widths['posted']}} {r['source']:<{col_widths['source']}}")
        print(f"  {r['url']}")

    if relocation_only:
        print(f"\nDiscarded as relocation-only ({len(relocation_only)}):")
        for r in relocation_only:
            print(f"  - {r['title']} @ {r['company']} ({r['location']}, {r['source']})")

    if stale_relevant:
        print(f"\nDiscarded as stale ({len(stale_relevant)}):")
        for r in stale_relevant:
            posted = r["posted"].strftime("%Y-%m-%d") if r["posted"] else "unknown"
            print(f"  - {r['title']} @ {r['company']} ({posted}, {r['source']})")


if __name__ == "__main__":
    main()

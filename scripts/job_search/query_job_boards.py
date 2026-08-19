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
against real API responses, not guessed from docs alone. That includes
Workday and the three aggregators below (Remotive, RemoteOK, The Muse),
each hit live against a real company/search during development.

Two kinds of source:
- "companies": per-company lookup. You already know the company name;
  this asks its ATS "what jobs do you have." No cross-company search
  exists on any of these platforms - that's what "aggregators" is for.
- "aggregators": keyword-first search across many companies at once.
  Use this when you DON'T have a company list yet.

Config file shape (JSON), passed via --config:
{
  "companies": {
    "greenhouse": ["<board_token>", ...],
    "lever": ["<site>", ...],
    "workable": ["<account>", ...],
    "smartrecruiters": ["<company>", ...],
    "ashby": ["<company>", ...],
    "workday": [{"tenant": "<tenant>", "wd": "<shard, e.g. wd5>", "site": "<career site slug>"}, ...]
  },
  "aggregators": {
    "remotive": true,
    "remoteok": true,
    "themuse": {"category": "<optional Muse category>", "location": "<optional Muse location filter>"},
    "adzuna": {"app_id": "<from developer.adzuna.com>", "app_key": "<...>", "country": "us"},
    "jsearch": {"api_key": "<RapidAPI key for the JSearch API>"}
  },
  "keywords": ["<title keyword>", ...],
  "local_area": ["<place name>", ...]
}
All top-level keys optional except "companies" or "aggregators" (need at
least one source). keywords/local_area can also be passed as
--keywords/--local-area instead.

Notes on the aggregators:
- remotive/remoteok/themuse need no credentials and are queried directly.
- adzuna requires a free app_id/app_key (developer.adzuna.com) - omit it
  (or leave app_id/app_key blank) and it's silently skipped, no error.
- remotive and remoteok are 100%-remote job boards by construction, so
  every result from them is treated as remote regardless of listed location.
- themuse has no full-text search param in its public API - it's filtered
  by category/location server-side (both optional) and by keyword
  client-side same as everything else, so an unfiltered call pulls from
  a very large (400k+) catalog a few pages at a time. Fine as a
  supplementary source; don't expect it to be exhaustive.
- Workday tenants need three values, not one slug (tenant, shard number
  like "wd5", and a career-site slug) since its API URL encodes all
  three - see the config shape above.
- jsearch (via RapidAPI, jsearch.p.rapidapi.com) is the one aggregator
  here that actually surfaces LinkedIn and Indeed postings - it's a paid
  third party that scrapes those platforms itself and resells the
  result as a clean API, credentials required (a free RapidAPI tier
  exists). Field names below are from public documentation, NOT a live
  response - this project has no RapidAPI key to test with. Using it
  means relying on a source that is itself scraping LinkedIn/Indeed
  against those platforms' terms of service, one step removed - a
  deliberate, discussed tradeoff, not an oversight. Skipped silently if
  api_key isn't configured, same as adzuna.

Usage:
  python query_job_boards.py --config path/to/config.json
  python query_job_boards.py --companies-json '{"greenhouse":["acme"]}' --keywords "cpc,billing" --local-area "Anytown,YourState"
"""
import argparse
import json
import re
import urllib.request
import urllib.error
import urllib.parse
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


def fetch_json_with_headers(url, extra_headers):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json", **extra_headers})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)


def fetch_json_post(url, payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
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


def parse_workday_relative_date(text):
    """Workday's list endpoint gives relative text ("Posted Today",
    "Posted 3 Days Ago", "Posted 30+ Days Ago") instead of a real
    timestamp - only the detail endpoint has an actual date, and hitting
    that per-posting isn't worth it for a freshness check. Best-effort
    parse relative to now; "30+ Days Ago" is treated as exactly 30 days
    out (a conservative floor, not the true age) so it still clears a
    typical max-age-days filter rather than being silently dropped."""
    if not text:
        return None
    t = text.strip().lower()
    if "today" in t:
        return datetime.now(timezone.utc)
    if "yesterday" in t:
        return datetime.now(timezone.utc) - timedelta(days=1)
    m = re.search(r"(\d+)\+?\s*day", t)
    if m:
        return datetime.now(timezone.utc) - timedelta(days=int(m.group(1)))
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


def query_workday(entry, max_postings=100):
    """entry is {"tenant":..., "wd":..., "site":...} - Workday's API needs
    all three to build the URL, unlike the single-slug platforms above.
    Confirmed live against a real tenant (nvidia.wd5.myworkdayjobs.com)
    during development - including that its page size caps at 20 per
    request (21+ returns HTTP 400), so this paginates rather than asking
    for one big page like the other platforms do."""
    tenant, wd, site = entry.get("tenant"), entry.get("wd"), entry.get("site")
    if not (tenant and wd and site):
        return [], "workday config entry needs tenant, wd, and site"
    url = f"https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    page_size = 20
    results = []
    for offset in range(0, max_postings, page_size):
        data, err = fetch_json_post(url, {"appliedFacets": {}, "limit": page_size, "offset": offset, "searchText": ""})
        if err:
            return results, err
        postings = data.get("jobPostings", [])
        if not postings:
            break
        for job in postings:
            location = job.get("locationsText")
            external_path = job.get("externalPath") or ""
            results.append({
                "title": job.get("title"),
                "company": tenant,
                "location": location,
                # No explicit remote flag - same signal-from-text approach as Greenhouse.
                "is_remote": "remote" in (location or "").lower(),
                "url": f"https://{tenant}.{wd}.myworkdayjobs.com/{site}{external_path}",
                "posted": parse_workday_relative_date(job.get("postedOn")),
                "source": "workday",
            })
        if len(postings) < page_size:
            break
    return results, None


QUERY_FUNCS = {
    "greenhouse": query_greenhouse,
    "lever": query_lever,
    "workable": query_workable,
    "smartrecruiters": query_smartrecruiters,
    "ashby": query_ashby,
    "workday": query_workday,
}


def query_remotive(keyword):
    """Remotive is a 100%-remote job board - every result is remote by
    construction, so is_remote is hardcoded True rather than inferred."""
    url = f"https://remotive.com/api/remote-jobs?search={urllib.parse.quote(keyword)}&limit=50"
    data, err = fetch_json(url)
    if err:
        return [], err
    results = []
    for job in data.get("jobs", []):
        results.append({
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("candidate_required_location"),
            "is_remote": True,
            "url": job.get("url"),
            "posted": parse_date(job.get("publication_date")),
            "source": "remotive",
        })
    return results, None


def query_remoteok(keyword):
    """Same 100%-remote-by-construction reasoning as Remotive. RemoteOK's
    ?tags= filter wants a hyphenated single tag, not free text - a
    multi-word keyword is joined with hyphens as a best-effort mapping."""
    tag = keyword.strip().lower().replace(" ", "-")
    url = f"https://remoteok.com/api?tags={urllib.parse.quote(tag)}"
    data, err = fetch_json(url)
    if err:
        return [], err
    results = []
    for job in data:
        if not job.get("id") or not job.get("position"):
            continue  # first element of RemoteOK's response is a legal-notice object, not a job
        results.append({
            "title": job.get("position"),
            "company": job.get("company"),
            "location": job.get("location"),
            "is_remote": True,
            "url": job.get("url") or job.get("apply_url"),
            "posted": parse_date(job.get("date")),
            "source": "remoteok",
        })
    return results, None


def query_themuse(category=None, location=None, pages=3):
    """The Muse's public API has no full-text search param - only
    category/location filters - so this leans on the same downstream
    keyword filter as everything else. Its catalog is large (400k+
    postings), so this is a bounded sample (a few pages), not exhaustive."""
    results = []
    for page in range(1, pages + 1):
        params = {"page": str(page)}
        if category:
            params["category"] = category
        if location:
            params["location"] = location
        url = "https://www.themuse.com/api/public/jobs?" + urllib.parse.urlencode(params)
        data, err = fetch_json(url)
        if err:
            return results, err
        for job in data.get("results", []):
            locations = job.get("locations") or []
            loc_text = ", ".join(l.get("name", "") for l in locations if l.get("name"))
            results.append({
                "title": job.get("name"),
                "company": (job.get("company") or {}).get("name"),
                "location": loc_text or None,
                "is_remote": "remote" in loc_text.lower(),
                "url": (job.get("refs") or {}).get("landing_page"),
                "posted": parse_date(job.get("publication_date")),
                "source": "themuse",
            })
        if not data.get("results"):
            break
    return results, None


def query_adzuna(keyword, location, app_id, app_key, country="us"):
    """Documented per Adzuna's published API spec (developer.adzuna.com);
    unlike the other three aggregators this was NOT hit live during
    development since it requires a registered app_id/app_key this
    session didn't have - verify field names against a real response
    before leaning on this one. Silently unusable (returns an error, not
    an exception) without credentials, by design - see the caller."""
    if not (app_id and app_key):
        return [], "adzuna app_id/app_key not configured - skipped"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": keyword,
        "results_per_page": "50",
    }
    if location:
        params["where"] = location
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1?" + urllib.parse.urlencode(params)
    data, err = fetch_json(url)
    if err:
        return [], err
    results = []
    for job in data.get("results", []):
        loc = (job.get("location") or {}).get("display_name")
        results.append({
            "title": job.get("title"),
            "company": (job.get("company") or {}).get("display_name"),
            "location": loc,
            "is_remote": "remote" in (loc or "").lower(),
            "url": job.get("redirect_url"),
            "posted": parse_date(job.get("created")),
            "source": "adzuna",
        })
    return results, None


def query_jsearch(keyword, location, api_key):
    """Confirmed live against jsearch.p.rapidapi.com with a real,
    subscribed key. The endpoint is /search-v2, NOT /search - every
    third-party writeup this was originally built from (including
    RapidAPI's own docs-page example) said /search, which 404s
    ("Endpoint '/search' does not exist"); /search-v2 is what actually
    works and nests jobs under data.jobs (with a data.cursor for
    pagination), not directly under data. This is the one aggregator
    here that reaches LinkedIn/Indeed postings, because JSearch scrapes
    them itself and resells the result - see the module docstring for
    the ToS tradeoff that implies."""
    if not api_key:
        return [], "jsearch api_key not configured - skipped"
    query = f"{keyword} in {location}" if location else keyword
    url = "https://jsearch.p.rapidapi.com/search-v2?" + urllib.parse.urlencode({"query": query, "page": "1", "num_pages": "1"})
    data, err = fetch_json_with_headers(url, {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    })
    if err:
        return [], err
    results = []
    for job in (data.get("data") or {}).get("jobs", []):
        posted_ts = job.get("job_posted_at_timestamp")
        # job_is_remote was reliably a real boolean on /search-v2 in testing,
        # but work_arrangement (present on /job-details, absent here) is
        # checked first anyway in case it shows up in a future response.
        is_remote = job.get("work_arrangement") == "remote" or bool(job.get("job_is_remote"))
        results.append({
            "title": job.get("job_title"),
            "company": job.get("employer_name"),
            "location": job.get("job_location") or job.get("job_city"),
            "is_remote": is_remote,
            "url": job.get("job_apply_link"),
            "posted": datetime.fromtimestamp(posted_ts, tz=timezone.utc) if posted_ts else None,
            "source": f"jsearch/{job.get('job_publisher') or 'unknown'}",
        })
    return results, None


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

    companies = config.get("companies") or (json.loads(args.companies_json) if args.companies_json else None) or {}
    aggregators = config.get("aggregators") or {}
    if not companies and not aggregators:
        parser.error("No companies or aggregators configured - pass --config (with 'companies' and/or 'aggregators') or --companies-json. This script has no built-in company list on purpose (see module docstring).")

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
                token_label = token.get("tenant", str(token)) if isinstance(token, dict) else token
                errors.append((platform, token_label, err))
                continue
            all_results.extend(results)

    # Aggregators are keyword-first (that's the point - no company name needed),
    # so without keywords, remotive/remoteok/adzuna have nothing meaningful to
    # search and are skipped rather than pulling their entire unfiltered feed.
    if aggregators.get("remotive") and keywords:
        for kw in keywords:
            results, err = query_remotive(kw)
            if err:
                errors.append(("remotive", kw, err))
            all_results.extend(results)
    if aggregators.get("remoteok") and keywords:
        for kw in keywords:
            results, err = query_remoteok(kw)
            if err:
                errors.append(("remoteok", kw, err))
            all_results.extend(results)
    if "themuse" in aggregators:
        muse_cfg = aggregators["themuse"] if isinstance(aggregators["themuse"], dict) else {}
        results, err = query_themuse(category=muse_cfg.get("category"), location=muse_cfg.get("location"))
        if err:
            errors.append(("themuse", "(config)", err))
        all_results.extend(results)
    adzuna_cfg = aggregators.get("adzuna")
    if adzuna_cfg and keywords:
        for kw in keywords:
            results, err = query_adzuna(kw, local_area[0] if local_area else None,
                                         adzuna_cfg.get("app_id"), adzuna_cfg.get("app_key"),
                                         adzuna_cfg.get("country", "us"))
            if err:
                errors.append(("adzuna", kw, err))
            all_results.extend(results)
    jsearch_cfg = aggregators.get("jsearch")
    if jsearch_cfg and keywords:
        for kw in keywords:
            results, err = query_jsearch(kw, local_area[0] if local_area else None, jsearch_cfg.get("api_key"))
            if err:
                errors.append(("jsearch", kw, err))
            all_results.extend(results)

    # Same posting can surface from more than one source (e.g. a company
    # queried directly AND turned up by an aggregator) - dedupe by URL,
    # first occurrence wins.
    seen_urls = set()
    deduped = []
    for r in all_results:
        key = r.get("url") or (r.get("title"), r.get("company"))
        if key in seen_urls:
            continue
        seen_urls.add(key)
        deduped.append(r)
    all_results = deduped

    relevant = [r for r in all_results if is_relevant(r["title"], keywords)]
    fresh_relevant = [r for r in relevant if is_fresh(r["posted"], args.max_age_days)]
    stale_relevant = [r for r in relevant if not is_fresh(r["posted"], args.max_age_days)]

    if args.include_relocation:
        in_scope, relocation_only = fresh_relevant, []
    else:
        in_scope = [r for r in fresh_relevant if is_local_or_remote(r, local_area)]
        relocation_only = [r for r in fresh_relevant if not is_local_or_remote(r, local_area)]

    total_companies = sum(len(v) for v in companies.values())
    active_aggregators = [name for name in ("remotive", "remoteok", "adzuna", "jsearch") if aggregators.get(name)]
    if "themuse" in aggregators:
        active_aggregators.append("themuse")
    source_note = f"{total_companies} companies" + (f" + {len(active_aggregators)} aggregators ({', '.join(active_aggregators)})" if active_aggregators else "")
    print(f"Total postings fetched across {source_note}: {len(all_results)}")
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

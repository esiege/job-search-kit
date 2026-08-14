# Getting Started

`job-search-kit` is a Claude Code plugin for an AI-assisted job search: fit/gap feedback on job descriptions, tailored resumes with branded PDF generation, and (planned) interview-prep artifacts. It reframes a person's real experience per job description — it never fabricates.

See `STARTER_KIT_OVERVIEW.md` and `STARTER_KIT_IMPLEMENTATION_PLAN.md` in the Resume Workspace project (`C:\Users\esieg\OneDrive\Documents\Resume Workspace`) for the full design rationale and build phases. This doc is the practical "how do I actually run this" reference.

## Requirements
- Python 3.10+, with `pip install -r requirements.txt` (`fpdf2`, `python-docx`, `pdfplumber`, `beautifulsoup4`, `striprtf`)
- Claude Code

## Data separation (important)
This repo is the plugin's **logic only** — skills, commands, hooks, agents, templates. It contains no one's personal data and nothing in it is ever committed here. Each person gets their own separate, plain folder (no git) for their actual resumes/facts/job descriptions. Never point this repo itself at a person's real material.

## Setting up a new person's workspace
The goal is that the person never has to know a slash command exists — the workspace itself guides them from the first message.

**For Claude Code, this is genuinely zero-config** — no per-workspace file copying needed. `hooks/session-start-check.ps1` runs automatically on `SessionStart` for every workspace where the plugin is loaded: it checks whether a master resume exists, whether it has a matching PDF, and injects the right instruction into context accordingly (ask for source material / offer to generate the missing PDF / offer both continuing the baseline or starting a tailored application). This only works because it's a real plugin hook, not a file that has to be copied in — see the note below on why an earlier version of this used a `CLAUDE.md` template and why that was a workaround, not the real mechanism.

### Install the plugin once (recommended — non-interactive, user scope)
`claude plugin marketplace add` and `claude plugin install` are real CLI subcommands, not just in-chat slash commands — they work from an ordinary terminal without ever opening an interactive Claude Code session:

```
claude plugin marketplace add esiege/job-search-kit
claude plugin install job-search-kit@job-search-kit
```

Installing this way puts the plugin at **user scope** — available to every workspace and every future session (CLI or VSCode extension), not just one folder. So this only needs to be run **once ever** on a given machine, not per new person's workspace. Run it from VSCode's integrated terminal too if that's the surface being used — it's the same underlying CLI either way.

**The catch:** plugins attach at session start. If a Claude Code session (CLI or VSCode extension) is already running when this is installed, that session won't pick it up — it'll be live starting with the next fresh session.

### Per-workspace / interactive alternatives
If a one-time user-scope install isn't what's wanted (e.g. testing local, unpushed plugin changes for just one workspace), the interactive per-session methods still work:

1. Create an empty folder for the person (e.g. sibling to this repo, like `C:\Users\esieg\source\repos\<person>-resume`). Nothing needs to be copied into it.
2. Open that folder with the plugin loaded — steps differ depending on which Claude Code surface is being used:

   **Terminal CLI:**
   - From the marketplace (published):
     ```
     cd "C:\Users\esieg\source\repos\<person>-resume"
     claude
     /plugin marketplace add esiege/job-search-kit
     /plugin install job-search-kit@job-search-kit
     ```
   - By local path (for developing/testing the plugin itself):
     ```
     cd "C:\Users\esieg\source\repos\<person>-resume"
     claude --plugin-dir "C:\Users\esieg\source\repos\job-search-kit"
     ```

   **VSCode extension** (no `--plugin-dir` equivalent flag exists here — a local path has to be added as a marketplace source instead):
   - File → Open Folder → the person's workspace folder.
   - In the chat panel, type `/plugins` to open the graphical "Manage plugins" panel (or type the commands directly — both work).
   - From the marketplace (published):
     ```
     /plugin marketplace add esiege/job-search-kit
     /plugin install job-search-kit@job-search-kit
     ```
   - By local path (for developing/testing the plugin itself):
     ```
     /plugin marketplace add C:\Users\esieg\source\repos\job-search-kit
     /plugin install job-search-kit@job-search-kit
     ```
   - Recent versions activate immediately; if the install summary says "Run `/reload-plugins` to activate," run that in the chat (not a VSCode restart).

Either way (one-time user-scope install, or per-workspace): once the plugin is loaded, the `SessionStart` hook fires before the first message, so the agent already knows whether the workspace is empty and asks for source material (LinkedIn export, old resumes, project notes, anything relevant), tells the person to drop it in `Intake/`, and works through it conversationally (via the `intake` skill/`/job-search-kit:intake` command) before drafting a master resume. Nothing downstream happens until that's reviewed and confirmed — that's the most important step to get right.

### Command invocation — use the namespaced form
**Confirmed real-world behavior (VSCode extension): commands need the plugin-name prefix, e.g. `/job-search-kit:find-jobs`, not bare `/find-jobs`.** The bare form appearing in a plugin's own command list/autocomplete is not the same as it being invokable directly — traced this down after `/find-jobs` and every other command silently didn't exist in an otherwise correctly-installed, correctly-loaded plugin (confirmed installed and enabled in `/plugins`, confirmed present and current in the local plugin cache on disk, confirmed a genuinely fresh session) — typing `/job-search-kit:` and letting autocomplete finish it was what actually worked. Use the namespaced form for every command below; if a bare form also happens to work in a given environment, treat that as a bonus, not something to rely on.

**For GitHub Copilot**, there's no plugin/hook system to hook into, so the onboarding instructions do have to be a real file in the workspace — copy the template in before the first session:
```
mkdir "C:\Users\esieg\source\repos\<person>-resume\.github"
copy "C:\Users\esieg\source\repos\job-search-kit\scripts\templates\copilot-instructions_TEMPLATE.md" "C:\Users\esieg\source\repos\<person>-resume\.github\copilot-instructions.md"
```

If the plugin gets edited during a Claude Code session, run `/reload-plugins` to pick up changes without restarting.

**Why a hook instead of a `CLAUDE.md` template:** an earlier version of this plugin shipped a `CLAUDE_TEMPLATE.md` that had to be manually copied into each new workspace as `CLAUDE.md`. That worked, but it wasn't actually "part of the plugin" in any enforced sense — Claude Code plugins can't ship a `CLAUDE.md` that auto-loads into project context, so the behavior silently didn't happen for anyone who created a workspace without following this exact runbook. The `SessionStart` hook is the real plugin-native mechanism: it's guaranteed to fire for every session wherever the plugin is installed, with no per-workspace setup step to forget.

## Finding jobs to apply to
1. `/job-search-kit:job-search-preferences` — one-time (then update as needed): target titles, location/remote constraints, deal-breakers, comp floor if shared. Stored in `job_search_preferences.md`, separate from the resume-tone facts file.
2. `/job-search-kit:find-jobs` — searches for matching postings using a two-tier approach: direct lookup against known companies' ATS APIs (Greenhouse, Lever, Workable, SmartRecruiters, Ashby — see `JOB_SEARCH_API_ENDPOINTS.md` in the Resume Workspace project) first, falling back to `WebSearch`/`WebFetch` for anything not resolvable that way. Every job that makes the shortlist gets recorded immediately (JD file + a row in `JOB_SEARCH_LOG.md`, status `Viewed`) before it's even presented — this isn't conditional on the person deciding to pursue it.
3. As the person reacts to the shortlist, confirmed standing preferences ("skip staffing agencies") get written into `job_search_preferences.md`'s "Learned from feedback" section — never inferred silently.

This is genuinely two-tier by design, not scraping-only: real testing found direct ATS API lookups dramatically more reliable than scraping HTML career pages (see `JOB_SEARCH_IMPLEMENTATION_PLAN.md`'s Phase 0 findings), so `WebSearch`/`WebFetch` is the fallback, not the primary method.

## Per-application loop
Once the master resume is confirmed (and optionally, a job found via `/job-search-kit:find-jobs`), for each job:
1. `/job-search-kit:evaluate-jd` — fit/gap feedback, stops and waits for a go-ahead
2. `/job-search-kit:tailor-resume` — drafts the tailored resume, stops and waits for approval. If the job came from `/job-search-kit:find-jobs`, its `JOB_SEARCH_LOG.md` status updates to `Resume Created` automatically at this point.
3. `/job-search-kit:generate-pdf` — copies the template generator to a new `generate_pdf_<company>.py`, runs it, logs it to `PDF_GENERATION_LOG.md`

Each step is a deliberate checkpoint — there's no "do everything" command on purpose, so a human approves every artifact before it's created.

## Publishing / updating the marketplace listing
`.claude-plugin/marketplace.json` makes this repo self-hosting as a single-plugin marketplace — no separate marketplace repo needed. It has no `version` pinned on purpose, so `/plugin install` always tracks the latest commit on `master` rather than requiring a version bump to pick up changes; that's the right tradeoff while this is under active development. Revisit that once things stabilize and updates should be more deliberate.

## Known gaps (as of v1)
- **PDF generation is consistently sloppy** (cut-off lines, bad margins/padding, overlapping text) — tracked in `KNOWN_ISSUES.md`, not yet fixed. The workflow is designed around this (upfront expectation-setting, versioned correction rounds), but the underlying generator itself still needs work.
- `.doc`/`.docx` files can't be trusted by extension alone — a real intake run found a `.doc` that was actually RTF. `extract_docx.py` failing is the signal to fall back to `extract_rtf.py` (see `skills/intake/SKILL.md`).
- Interview-prep artifacts (cheatsheet, TMAY, mock Q&A) aren't built yet — planned as v1.1, after the core loop has real-world use.
- **`/find-jobs` hasn't had a real dry run against an actual person's preferences yet.** The search logic (`job-search` skill, `query_job_boards.py`) was validated extensively in Phase 0 with real companies and real API calls, but always run manually/conversationally, not yet through the actual `/find-jobs`/`/job-search-preferences` commands end to end. That dry run is the next real gate before this is considered done (see `JOB_SEARCH_IMPLEMENTATION_PLAN.md`'s build order) — same spirit as the intake dry run was for the original resume pipeline.
- `/find-jobs` scheduling and email notifications (v2/v3) aren't built yet — see `JOB_SEARCH_IMPLEMENTATION_PLAN.md`.

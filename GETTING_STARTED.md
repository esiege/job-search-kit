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

1. Create an empty folder for them (e.g. sibling to this repo, like `C:\Users\esieg\source\repos\<person>-resume`).
2. Copy the onboarding templates in **before the first session opens**, since they're what make the agent ask for source material automatically:
   ```
   copy "C:\Users\esieg\source\repos\job-search-kit\scripts\templates\CLAUDE_TEMPLATE.md" "C:\Users\esieg\source\repos\<person>-resume\CLAUDE.md"
   mkdir "C:\Users\esieg\source\repos\<person>-resume\.github"
   copy "C:\Users\esieg\source\repos\job-search-kit\scripts\templates\copilot-instructions_TEMPLATE.md" "C:\Users\esieg\source\repos\<person>-resume\.github\copilot-instructions.md"
   ```
3. Open a Claude Code session rooted in that folder with this plugin loaded. Either works:
   - **From the marketplace** (published — see below):
     ```
     cd "C:\Users\esieg\source\repos\<person>-resume"
     claude
     /plugin marketplace add esiege/job-search-kit
     /plugin install job-search-kit@job-search-kit
     ```
   - **By local path** (for developing/testing the plugin itself):
     ```
     cd "C:\Users\esieg\source\repos\<person>-resume"
     claude --plugin-dir "C:\Users\esieg\source\repos\job-search-kit"
     ```
4. That's it — `CLAUDE.md` takes it from there. The agent immediately asks whether the person has source material ready (LinkedIn export, old resumes, project notes, anything relevant), tells them to drop it in `Intake/`, and works through it conversationally before drafting a master resume. If the plugin's `/intake` command is available it'll use that; if not, it follows the same steps directly from `CLAUDE.md`. Either way, nothing downstream happens until the master resume is reviewed and confirmed — that's the most important step to get right.

If the plugin gets edited during a session, run `/reload-plugins` to pick up changes without restarting.

## Per-application loop
Once the master resume is confirmed, for each job:
1. `/evaluate-jd` — fit/gap feedback, stops and waits for a go-ahead
2. `/tailor-resume` — drafts the tailored resume, stops and waits for approval
3. `/generate-pdf` — copies the template generator to a new `generate_pdf_<company>.py`, runs it, logs it to `PDF_GENERATION_LOG.md`

Each step is a deliberate checkpoint — there's no "do everything" command on purpose, so a human approves every artifact before it's created.

## Publishing / updating the marketplace listing
`.claude-plugin/marketplace.json` makes this repo self-hosting as a single-plugin marketplace — no separate marketplace repo needed. It has no `version` pinned on purpose, so `/plugin install` always tracks the latest commit on `master` rather than requiring a version bump to pick up changes; that's the right tradeoff while this is under active development. Revisit that once things stabilize and updates should be more deliberate.

## Known gaps (as of v1)
- **PDF generation is consistently sloppy** (cut-off lines, bad margins/padding, overlapping text) — tracked in `KNOWN_ISSUES.md`, not yet fixed. The workflow is designed around this (upfront expectation-setting, versioned correction rounds), but the underlying generator itself still needs work.
- `.doc`/`.docx` files can't be trusted by extension alone — a real intake run found a `.doc` that was actually RTF. `extract_docx.py` failing is the signal to fall back to `extract_rtf.py` (see `skills/intake/SKILL.md`).
- Interview-prep artifacts (cheatsheet, TMAY, mock Q&A) aren't built yet — planned as v1.1, after the core loop has real-world use.

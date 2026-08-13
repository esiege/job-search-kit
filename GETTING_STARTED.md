# Getting Started

`job-search-kit` is a Claude Code plugin for an AI-assisted job search: fit/gap feedback on job descriptions, tailored resumes with branded PDF generation, and (planned) interview-prep artifacts. It reframes a person's real experience per job description — it never fabricates.

See `STARTER_KIT_OVERVIEW.md` and `STARTER_KIT_IMPLEMENTATION_PLAN.md` in the Resume Workspace project (`C:\Users\esieg\OneDrive\Documents\Resume Workspace`) for the full design rationale and build phases. This doc is the practical "how do I actually run this" reference.

## Requirements
- Python 3.10+, with `pip install -r requirements.txt` (`fpdf2`, `python-docx`, `pdfplumber`, `beautifulsoup4`, `striprtf`)
- Claude Code

## Data separation (important)
This repo is the plugin's **logic only** — skills, commands, hooks, agents, templates. It contains no one's personal data and nothing in it is ever committed here. Each person gets their own separate, plain folder (no git) for their actual resumes/facts/job descriptions. Never point this repo itself at a person's real material.

## Setting up a new person's workspace
1. Create an empty folder for them (e.g. sibling to this repo, like `C:\Users\esieg\source\repos\<person>-resume`).
2. Drop their zip of raw material (old resumes, LinkedIn export, cover letters, notes — whatever they have) into an `Intake/` subfolder there.
3. Open a Claude Code session rooted in that folder with this plugin loaded:
   ```
   cd "C:\Users\esieg\source\repos\<person>-resume"
   claude --plugin-dir "C:\Users\esieg\source\repos\job-search-kit"
   ```
4. Run `/intake`. It scaffolds the rest of the folder structure, extracts text from the source material, and drafts a master resume, seeded facts/preferences, and a flagged gaps checklist — then stops and waits for review. Nothing downstream happens until that review is done; this is the most important step to get right.

If the plugin gets edited during a session, run `/reload-plugins` to pick up changes without restarting.

## Per-application loop
Once the master resume is confirmed, for each job:
1. `/evaluate-jd` — fit/gap feedback, stops and waits for a go-ahead
2. `/tailor-resume` — drafts the tailored resume, stops and waits for approval
3. `/generate-pdf` — copies the template generator to a new `generate_pdf_<company>.py`, runs it, logs it to `PDF_GENERATION_LOG.md`

Each step is a deliberate checkpoint — there's no "do everything" command on purpose, so a human approves every artifact before it's created.

## Known gaps (as of v1)
- `.doc`/`.docx` files can't be trusted by extension alone — a real intake run found a `.doc` that was actually RTF. `extract_docx.py` failing is the signal to fall back to `extract_rtf.py` (see `skills/intake/SKILL.md`).
- Interview-prep artifacts (cheatsheet, TMAY, mock Q&A) aren't built yet — planned as v1.1, after the core loop has real-world use.
- Not yet published to a marketplace; local `--plugin-dir` loading is the only install path for now.

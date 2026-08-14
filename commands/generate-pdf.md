---
description: Generate the branded PDF for an already-approved tailored resume.
argument-hint: [company or job description reference, if not obvious from context]
---

Generate the PDF for the approved tailored resume for $ARGUMENTS, following `skills/pdf-layout-standards/SKILL.md`. (`scripts/...` paths below are bundled inside this plugin — resolve against the plugin root from your session's `SessionStart` context, not relative to the workspace.)

**First run for this resume:**
1. Copy `scripts/templates/generate_pdf_TEMPLATE.py` to a **new** file `generate_pdf_<company-or-theme>.py` in the person's workspace. Never edit an existing `generate_pdf_*.py` in place — the guard hook will block this anyway, but don't attempt it.
2. Fill in `IDENTITY` from the person's facts file and the `build_resume()` content from the approved tailored resume text. Do not introduce content that wasn't in the approved draft.
3. Run the script to produce the PDF into `Resumes/`.
4. Add a row to `PDF_GENERATION_LOG.md` (script name, output path, source content description, date/notes) — follow the existing table format in that file.
5. Show the result and stop. Tell the user upfront that formatting can come out rough on the first pass (cut-off lines, margin/padding issues) — that's a known limitation, not something they did wrong.

**Formatting correction round for this same resume** (see `pdf-layout-standards`'s versioning section):
1. Rename the current `generate_pdf_<company-or-theme>.py` and its output PDF to add a `vN` stamp (next number up from whatever already exists for this theme).
2. Write the corrected script to the original unversioned filename and regenerate.
3. Log the new version in `PDF_GENERATION_LOG.md`.
4. Show the result, encourage the user to flag anything still off, and stop.

Either way: do not chain into generating any interview-prep artifact automatically — those are only built when the user explicitly asks for one, one at a time.

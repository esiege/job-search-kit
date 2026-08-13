---
description: Generate the branded PDF for an already-approved tailored resume.
argument-hint: [company or job description reference, if not obvious from context]
---

Generate the PDF for the approved tailored resume for $ARGUMENTS, following `skills/pdf-layout-standards/SKILL.md`.

1. Copy `scripts/templates/generate_pdf_TEMPLATE.py` to a **new** file `generate_pdf_<company-or-theme>.py` in the person's workspace. Never edit an existing `generate_pdf_*.py` in place — the guard hook will block this anyway, but don't attempt it.
2. Fill in `IDENTITY` from the person's facts file and the `build_resume()` content from the approved tailored resume text. Do not introduce content that wasn't in the approved draft.
3. Run the script to produce the PDF into `Resumes/`.
4. Add a row to `PDF_GENERATION_LOG.md` (script name, output path, source content description, date/notes) — follow the existing table format in that file.
5. Show the result and stop. Do not chain into generating any interview-prep artifact automatically — those are only built when the user explicitly asks for one, one at a time.

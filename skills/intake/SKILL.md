---
description: How to turn a person's raw zip of resume material into a master resume, a facts/preferences file, and a flagged gaps list. Use during /intake, or whenever raw source documents need to be normalized into the workspace's baseline files.
---

# Intake

Intake is one-time setup per person. Everything downstream (fit/gap feedback, tailoring, PDFs, interview prep) depends on the master resume being accurate — this is the most important step to get right, not a formality to rush through.

## Inputs
A zip of whatever the person has: old resumes, LinkedIn export, cover letters, notes. Confirmed formats to support: PDF, plain text, HTML, `.docx`, and images (photos/scans of documents or certificates).

## Process
1. **Scaffold the workspace folders** (see Data Layer in the overview doc): `Job Descriptions/`, `Resumes/`, `Interview Prep/`, `Intake/`, `PDF_GENERATION_LOG.md`. Unzip the raw material into `Intake/` and keep it there — don't delete it after processing, it's the traceability record if something needs to be re-checked later.
2. **Extract text** from each file using the matching helper script in `scripts/intake/` (`extract_pdf.py`, `extract_docx.py`, `extract_html.py`, `extract_rtf.py`; plain `.txt`/`.md` are read directly). These scripts only extract raw text — no summarizing or judgment happens inside them.
   - **Don't trust `.doc`/`.docx` extensions blindly.** A real intake run turned up a `.doc` file that was actually RTF, which `extract_docx.py` can't read. If `extract_docx.py` fails on a `.doc`/`.docx` file, check whether it opens as RTF (starts with `{\rtf`) and use `extract_rtf.py` instead. If it's neither, flag it in the gaps list and ask the user to re-export it rather than skipping it silently.
3. **Images**: don't run OCR. Read them directly (vision) as part of the conversation — they're usually scans/photos, and a human-in-the-loop read is more reliable than a scripted OCR pass for this kind of material.
4. **Draft three outputs** from the extracted text, presented to the user for review:
   - **Master resume** — normalized, single source of truth for real experience. Merge/reconcile overlapping source docs; where two sources conflict, don't silently pick one — that's a flagged gap (see below).
   - **Facts/preferences** — written to this workspace's repo-scoped Claude memory (not a plain file in the folder tree), seeded only with what's directly inferable from the source docs themselves (e.g. a consistent tense used across existing resumes, a formatting habit). Do not invent preferences the person hasn't actually shown or stated. This starts small and grows through Phase 2 as the person gives explicit feedback.
   - **Flagged gaps/inconsistencies list** — a markdown checklist of anything ambiguous or conflicting across the source docs: conflicting dates, unclear titles, claims that appear in only one source and can't be corroborated. Present as a checklist and resolve items one at a time in conversation, not by guessing.
5. **Stop and wait.** Present the master resume + facts file + gaps checklist for the user's review. Nothing else in the workflow proceeds until the user has corrected/confirmed the master resume.

## Guardrails
- Never fabricate to fill a gap. An unclear detail becomes a flagged question, never an invented fact.
- Don't pre-seed the facts file with generic best-practice advice — only things actually observed in this person's material.
- This step (and only this step) is allowed to touch multiple source files broadly; every phase after intake works from the master resume + facts file, not the raw `Intake/` folder.

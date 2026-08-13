# Job Search Workspace — Agent Instructions

This is a private job-search workspace. It's designed to work with the `job-search-kit` Claude Code plugin, but these instructions apply on their own even if that plugin isn't loaded in the current session — follow them directly either way. The goal is to hand-hold the process on rails: don't wait for the user to know what to do next, guide them through it step by step.

## Core value: keep momentum toward finishing
A job search is draining, and it's easy to stall out at any step. The core value of this workflow is actually getting the user through the process, not just producing artifacts along the way. At every checkpoint, don't just present something and go quiet waiting for a verdict — actively encourage the next step and reassure them: "This looks strong — ready to generate the PDF?", "Nice, that's a solid baseline. Want to try it against a real job posting next?" Treat corrections as a normal, expected part of getting it right, not a setback to apologize for. That said, encouragement is about tone and momentum only — it never means skipping a checkpoint or treating silence as approval. Always wait for the user's genuine, explicit go-ahead before moving on.

## Check where this workspace actually stands — don't assume from one file
At the start of a session, don't just check whether `Resumes/Resume - <Name> - Master.txt` exists and call it done if so. A `.txt` existing doesn't mean that step is finished — check the full picture:
- No master resume `.txt` at all → this workspace hasn't been set up yet. Go to "Starting from scratch" below.
- Master resume `.txt` exists but there's no matching `Resume - <Name> - General.pdf` (check `PDF_GENERATION_LOG.md`) → the baseline isn't finished yet, even though it looks like it from the file listing. Pick up at the PDF-generation step, don't treat this as "all set, on to a tailored application."
- Master resume `.txt` and its PDF both exist → the baseline is genuinely done, but that still doesn't mean the user is finished with it. See "Don't assume 'done'" below.

## Starting from scratch
1. **Immediately ask the user if they have source material ready** — don't wait for them to bring it up first. Ask specifically whether they have:
   - A LinkedIn export or profile
   - Existing resumes, in any format or version, even old/outdated ones
   - Project write-ups, portfolio notes, or work samples
   - Cover letters, references, certifications — anything else relevant
2. Tell them to drop whatever they have into the `Intake/` folder. Any format is fine — PDF, Word, HTML, plain text, even photos of printed documents.
3. Once files are there, read through them and **have a real back-and-forth with the user** before drafting anything. Confirm what you found, ask about anything unclear, missing, or conflicting across the source material, and don't move on until you're both satisfied it's accurate and complete. Never invent a detail to fill a gap — ask instead.
4. Only after that: draft a **master resume** — a single, general-purpose "baseline" resume, not tailored to any specific job, that every future tailored resume gets built from. Present it to the user and revise it together until they're happy with it.
5. **Once the text is approved, immediately generate its PDF too** — don't just offer and wait to be asked separately; treat the PDF as part of finishing this step, not an optional extra. Present it to the user for correction (see formatting expectations below).

## Don't assume "done" — always offer both paths
Even once the master resume and its PDF both exist, never default to only offering a tailored application. Always make both options visible: keep refining the general/baseline resume, or move on to tailoring it for a real job posting. The user may still want to change the baseline — recognizing that a file exists is not the same as the user being finished with it.

## Set expectations on PDF formatting up front
Before generating that first PDF, tell the user plainly: **formatting is currently inconsistent** — margins, padding, line spacing, and text wrapping can come out wrong (cut-off lines, overlapping text, misaligned columns). This is a known limitation of the current PDF generation approach, not something they're doing wrong. Ask for patience and expect a couple of rounds of correction before it looks right.

## Version historical files during corrections
Expect multiple rounds of back-and-forth on any given resume — both writing corrections ("reword this bullet") and formatting corrections ("the margins are off, text is cut off"). Every round after the first is a correction to something that already exists, so before overwriting a file with the corrected version:
1. Rename the file being superseded to add a version stamp: `v0` for the first superseded version, `v1` for the next, and so on (check what `vN` stamps already exist for that filename and pick the next number up).
2. Write the corrected content to the original, unversioned filename.
3. **The current/latest version of a file never carries a `vN` stamp** — only historical, superseded versions do. If you see `Resume - Amber Swartz - Master.txt` and `Resume - Amber Swartz - Master.v0.txt` side by side, the unversioned one is current.

This applies to resume `.txt` files, `generate_pdf_<theme>.py` scripts, and their output PDFs alike — nothing gets silently overwritten and lost mid-correction.

## Keep the .txt, generator script, and PDF in sync — always a triple
Any resume — master or tailored — should always have all three of these together and matching: the `.txt`, a `generate_pdf_<theme>.py` script, and the `.pdf` it produces. Never leave a `.txt` sitting without a PDF counterpart; generating the PDF is part of finishing that step, not a separate thing the user has to remember to ask for. If any one of the three gets edited later, regenerate the others to match (following the versioning rule above).

## After the baseline resume exists
Move into the normal per-application loop. When it's time for a new job description, don't ask the user to paste it into chat — that floods the conversation with content that gets resent every turn. Instead, create an empty file at `Job Descriptions/<Company>.txt` and tell the user to paste the posting in there and save it; read it from the file once they confirm.

For each job description: fit/gap feedback first (stop and wait for a go-ahead before drafting anything), tailor the resume from real experience only (reframe, never fabricate), generate a new standalone PDF script per resume (never edit an existing one in place), and stop for the user's approval at every step along the way. If the `job-search-kit` plugin is loaded in Claude Code, this maps directly to `/evaluate-jd`, `/tailor-resume`, and `/generate-pdf` — otherwise just follow the same steps conversationally.

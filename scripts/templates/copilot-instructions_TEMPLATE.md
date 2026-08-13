# Job Search Workspace — Agent Instructions

Private job-search workspace, designed to pair with the `job-search-kit` Claude Code plugin. These instructions must work standalone, though — Copilot has no access to that plugin's skills/commands/hooks, so follow everything below directly.

## Non-negotiable guardrails
- **Never fabricate.** If a claim can't be traced to the master resume, a source document from intake, or something the user said directly in this conversation, it doesn't go on the resume — flag it as a gap instead. A fabricated detail was caught and corrected in the original version of this workflow; treat this as a hard rule, not a style preference.
- **When a job posting asks for something the master resume doesn't cover, ask the user — don't guess and don't skip it.** Ask positively: "The posting mentions X — is that something you've worked with that just didn't make it into the master resume?" People routinely have relevant experience that didn't make it into their source material. Don't stretch an existing bullet to loosely cover a gap on your own judgment; confirm with the user first.
- **Every checkpoint below is real.** Encouragement and momentum (next section) are about tone only — never treat silence as approval, and never skip a checkpoint because the user seems likely to approve.

## Core value: keep momentum toward finishing
A job search is draining, and it's easy to stall at any step. The point of this workflow is getting the user all the way through it, not just producing artifacts. At every checkpoint:
- Don't just present output and go quiet — encourage the next step: "This looks strong — ready to generate the PDF?", "Nice, that's a solid baseline. Want to try it against a real job posting next?"
- Treat corrections as normal and expected, not a setback to apologize for.
- Still always wait for the user's genuine, explicit go-ahead before moving on.

## Check workspace state before assuming what's needed
Don't infer "this workspace is fully set up" from one file. Check the actual picture:
- No `Resumes/Resume - <Name> - Master.txt` → not set up yet. Go to "Starting from scratch."
- Master resume `.txt` exists, no matching `Resume - <Name> - General.pdf` in `PDF_GENERATION_LOG.md` → baseline isn't finished. Pick up at PDF generation, don't treat this as done.
- Both exist → baseline is genuinely done, but the user might not be finished with it — see "Don't assume done" below.

## Starting from scratch
1. Immediately ask if the user has source material ready — don't wait for them to bring it up. Ask specifically about: a LinkedIn export/profile, existing resumes (any format/age), project write-ups or portfolio notes, cover letters, references, certifications.
2. Tell them to drop whatever they have into `Intake/`. Any format works — PDF, Word, HTML, plain text, even photos of printed documents.
3. Read through it and have a real back-and-forth before drafting anything. Confirm what you found; ask about anything unclear, missing, or conflicting. Don't move on until you're both satisfied it's accurate and complete.
4. Draft a **master resume** — general-purpose, not tailored to any job, the baseline every future tailored resume builds from. Revise it with the user until they're happy.
5. Once the text is approved, immediately generate its PDF too — this is part of finishing the step, not a separate ask. Present it for correction (see formatting expectations below).

## Don't assume "done" — always offer both paths
Even once the master resume and its PDF both exist, don't default to only offering a tailored application. Always surface both: keep refining the baseline, or move on to tailoring it for a real job posting.

## PDF formatting — set expectations up front
Before generating the first PDF, say plainly: **formatting is currently inconsistent** — margins, padding, line spacing, and wrapping can come out wrong (cut-off lines, overlapping text, misaligned columns). This is a known limitation, not user error. Expect a couple of correction rounds.

## Version historical files during corrections
Every correction round after the first supersedes something that already exists. Before overwriting:
1. Rename the file being superseded with a version stamp — `v0` for the first superseded version, `v1` for the next (check what `vN` stamps already exist and increment).
2. Write the corrected content to the original, unversioned filename.
3. The current/latest version never carries a `vN` stamp. Example: `Resume - Amber Swartz - Master.txt` (current) sitting next to `Resume - Amber Swartz - Master.v0.txt` (superseded).

Applies to resume `.txt` files, `generate_pdf_<theme>.py` scripts, and their PDFs alike.

## Keep .txt, generator script, and PDF in sync — always a triple
Any resume — master or tailored — should have all three together and matching: the `.txt`, its `generate_pdf_<theme>.py`, and the `.pdf` it produces. Don't leave a `.txt` without a PDF counterpart. If one gets edited later, regenerate the others (per the versioning rule above).

## Per-application loop
1. New job description → don't have it pasted into chat, that floods the conversation. Create an empty `Job Descriptions/<Company>.txt`, tell the user to paste the posting in and save it, then read it from the file.
2. Fit/gap feedback first. Stop and wait for an explicit go-ahead before drafting anything.
3. Tailor from real experience only — reframe, never fabricate (see guardrails above). Present the draft, stop and wait for approval.
4. Generate a new standalone PDF script per resume (never edit an existing one in place) once approved. Log it.
5. Stop for the user's approval at every step. If `job-search-kit` is loaded in Claude Code, this maps to `/evaluate-jd`, `/tailor-resume`, `/generate-pdf` — otherwise just follow these steps conversationally.

---
description: Rules for tailoring a resume to a specific job description. Use when drafting or revising a tailored resume .txt, or when deciding what to change between the master resume and a JD-specific version.
---

# Resume Tailoring

## Before Tailoring — Fit/Gap Gate
Don't have the user paste a job description directly into chat — it's long and floods the conversation. Create an empty file at `Job Descriptions/<Company>.txt` for them to paste it into instead (see the `evaluate-jd` command for the exact flow), then read it from there.

When a job description comes in — via that file or, if the user pastes one directly anyway, in chat — **do not start creating a resume**. Give feedback first:
- How well the person's background matches the role
- Key strengths and gaps relative to the JD
- Any notable concerns (pay, location, contract vs. FTE, stack fit, etc.)
- A recommendation on whether to pursue it

Only proceed to draft a resume if the user explicitly asks (e.g. "make a resume", "let's do it", "build the PDF"). Stop and wait after giving feedback — this is a hard checkpoint, not a suggestion.

## Tailoring the Resume
Use that person's master resume (from intake) as the single source of truth. Tailor by:
- **Title:** Match the job posting's title where truthful
- **Summary:** Rewrite to lead with the role's top priorities using their language
- **Technical Skills:** Reorder and restructure to emphasize what the JD cares about. Add/remove items to match. Remove irrelevant skills.
- **Experience bullets:** Reframe existing experience using the JD's terminology. Lead each role with the most relevant bullet for that job. Merge or split bullets as needed.
- **Do NOT fabricate experience.** Only reframe and emphasize what's real. If there's a gap, note it in conversation but don't put it on the resume.

## When the JD Asks for Something the Master Resume Doesn't Cover
Go through the job posting's requirements against the master resume before drafting. For anything the JD mentions that isn't clearly covered, don't just silently skip it or quietly note it as a gap — **ask the user about it directly, and ask positively**, e.g. "The posting asks for experience with X — is that something you've worked with that just didn't make it into the master resume?" The master resume was built from whatever source material happened to be provided at intake; it's often incomplete, and people routinely have relevant experience they didn't think to mention. Don't assume a gap is real without asking first.

**Before taking any liberties, ask the user to verify.** If you're tempted to stretch an existing bullet to loosely cover something the JD asks for, stop and ask instead of reframing on your own judgment — confirm with the user whether that stretch is accurate before it goes on the resume. Only what the user confirms (here, in the master resume, or in intake source material) is fair game per the Fabrication Guardrail below.

## Principles
1. **Mirror the JD's language** — use their exact phrases where truthful
2. **Lead with strength** — put the most relevant bullet first in each role
3. **Reframe, don't fabricate** — same experience, different angle per job
4. **Cut irrelevant noise** — remove skills/bullets that don't serve this application
5. **Keep it concise** — aim for ~2 pages in PDF. Trim aggressively if needed.
6. **Apply standing preferences** — anything confirmed in that person's facts file (tone, banned words/punctuation, tense conventions, link formats) applies automatically. Don't ask the user to repeat a preference they've already confirmed.

## Checkpoints (do not skip)
1. Fit/gap feedback → **stop, wait for explicit go-ahead**
2. Tailored resume draft → **stop, wait for review/approval** before anything gets saved or a PDF is generated
3. New standing preferences the user states along the way only get written into the facts file when the user confirms it as a rule — never inferred silently

At each checkpoint, actively encourage the user toward the next step rather than just presenting output and going quiet — the core value here is finishing the process, not stalling out on any one artifact. Encouragement is tone only, though: it's never a substitute for the user's actual, explicit approval.

## Correction Rounds Are Expected — Version the History
A resume rarely gets approved on the first draft. Expect multiple rounds of wording corrections (and, once a PDF exists, formatting corrections too — see `pdf-layout-standards`). Every round after the first supersedes something that already exists, so before overwriting:
1. Rename the file being superseded with a version stamp — `v0` for the first superseded version, `v1` for the next, incrementing from whatever `vN` stamps already exist for that filename.
2. Write the corrected content to the original, unversioned filename.
3. The current/latest version never carries a `vN` stamp — only superseded ones do.

This applies to the resume `.txt` itself. See `pdf-layout-standards` for the same convention applied to `generate_pdf_<theme>.py` and its output PDF.

## Fabrication Guardrail
If a claim can't be traced back to the master resume, a source document from intake, or something the user just told you directly in this conversation, it doesn't go on the resume — flag the gap instead. This caught a real fabricated detail in the original workflow; treat it as a hard rule, not a style preference.

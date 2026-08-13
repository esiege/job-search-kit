---
description: Give fit/gap feedback on a job description before any tailoring work starts.
argument-hint: [company or role name, if known]
---

Job descriptions are long — don't ask the user to paste one directly into chat, that floods the conversation with content that has to get resent every turn. Instead:

1. Ask for the company/role name if you don't already have it (used to name the file).
2. If `Job Descriptions/<Company>.txt` doesn't exist yet, create it empty.
3. Tell the user to paste the job posting into that file, save it, and let you know when it's ready. Encourage this rather than just issuing the instruction flatly — e.g. "Go ahead and paste it into `Job Descriptions/<Company>.txt` whenever you're set, and I'll take it from there."
4. Once the user confirms, read the file. If it already existed with content (e.g. re-running for the same company), just read it directly instead of re-creating it empty.
5. Using the `resume-tailoring` skill's fit/gap gate and this person's master resume + facts file, evaluate it:
   - How well their background matches the role
   - Key strengths and gaps relative to the JD
   - Any notable concerns (pay, location, contract vs. FTE, stack fit, etc.)
   - A clear recommendation on whether to pursue it

Stop after giving this feedback. Do not draft a resume, generate a PDF, or take any further action until the user explicitly says to proceed — but do encourage them toward that next step rather than just going quiet (see the core-value note on momentum in this workspace's `CLAUDE.md`).

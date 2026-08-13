---
description: Draft a tailored resume for a job description that's already been evaluated with /evaluate-jd.
argument-hint: [company or job description reference, if not obvious from context]
---

Using the `resume-tailoring` skill, draft a tailored resume for $ARGUMENTS based on this person's master resume and facts file.

1. Apply the tailoring rules (title match, summary rewrite, skills reordering, bullet reframing) — reframe only, never fabricate.
2. Present the full draft as plain text for review.
3. Stop and wait. Do not save `Job Descriptions/<Company>.txt` or `Resumes/Resume - <Name> - <Company>.txt`, and do not generate a PDF, until the user explicitly approves this draft. Both files are written together only at that point, once approved.
4. If the user gives a correction that sounds like a standing preference (not just a one-off edit to this resume), ask whether it should be written into the facts file as a rule — don't add it silently.

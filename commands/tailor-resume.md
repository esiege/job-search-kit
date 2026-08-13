---
description: Draft a tailored resume for a job description that's already been evaluated with /evaluate-jd.
argument-hint: [company or job description reference, if not obvious from context]
---

Using the `resume-tailoring` skill, draft a tailored resume for $ARGUMENTS based on this person's master resume and facts file.

1. Compare the JD's requirements against the master resume first. For anything the JD asks for that isn't clearly covered, ask the user about it directly and positively before drafting — see `resume-tailoring`'s section on this. Don't stretch existing bullets to cover a gap on your own judgment.
2. Apply the tailoring rules (title match, summary rewrite, skills reordering, bullet reframing) — reframe only, never fabricate.
3. Present the full draft as plain text for review.
4. Stop and wait. Do not save `Job Descriptions/<Company>.txt` or `Resumes/Resume - <Name> - <Company>.txt`, and do not generate a PDF, until the user explicitly approves this draft. Both files are written together only at that point, once approved.
5. If the user gives a correction that sounds like a standing preference (not just a one-off edit to this resume), ask whether it should be written into the facts file as a rule — don't add it silently.
6. If this resume was already saved and approved before, and the user is now asking for a further correction: apply the `resume-tailoring` skill's versioning rule (`vN` stamp on the superseded `.txt`, corrected content goes to the unversioned filename) rather than editing it in place. Corrections made *before* the first save (in-chat drafting, per step 3 above) don't need versioning — nothing's been written yet.

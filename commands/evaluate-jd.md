---
description: Give fit/gap feedback on a job description before any tailoring work starts.
argument-hint: [pasted job description or recruiter message]
---

Using the `resume-tailoring` skill's fit/gap gate and this person's master resume + facts file, evaluate the job description in $ARGUMENTS:

- How well their background matches the role
- Key strengths and gaps relative to the JD
- Any notable concerns (pay, location, contract vs. FTE, stack fit, etc.)
- A clear recommendation on whether to pursue it

Save the JD to `Job Descriptions/<Company>.txt` only once the user decides to move forward — not before.

Stop after giving this feedback. Do not draft a resume, generate a PDF, or take any further action until the user explicitly says to proceed.

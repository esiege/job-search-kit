---
description: One-time setup - turn a person's raw zip of resume material into a master resume, facts file, and flagged gaps list.
argument-hint: [path to workspace folder containing the zip, or path to the zip itself]
---

Run intake for this person's workspace, following the `intake` skill.

1. Confirm the workspace folder (create `Job Descriptions/`, `Resumes/`, `Interview Prep/`, `Intake/` if they don't exist yet, and copy `scripts/templates/PDF_GENERATION_LOG_TEMPLATE.md` to `PDF_GENERATION_LOG.md` if it doesn't exist yet) and unzip the provided material into `Intake/` if it isn't already unpacked. Also copy `scripts/templates/copilot-instructions_TEMPLATE.md` to `.github/copilot-instructions.md` if it isn't already there (fallback — normally already done per `GETTING_STARTED.md`; only needed for GitHub Copilot, since Claude Code gets this automatically via the `SessionStart` hook).
2. Dispatch the `intake-research-agent` subagent to extract and organize raw text from everything in `Intake/`.
3. Using that extracted material, draft: a master resume, a seeded facts/preferences file, and a flagged gaps/inconsistencies checklist — per the `intake` skill's rules on what belongs in each and the fabrication guardrail.
4. Present all three to the user and stop. Do not proceed to any other command or generate any other artifact until the user has reviewed and corrected the master resume — this baseline is what every later step depends on.

Arguments (if provided): $ARGUMENTS

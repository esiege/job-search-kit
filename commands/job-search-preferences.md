---
description: Capture or update this person's job-search targeting preferences - what job they're looking for, not resume-writing style.
argument-hint: []
---

1. If `job_search_preferences.md` doesn't exist yet, copy `scripts/templates/JOB_SEARCH_PREFERENCES_TEMPLATE.md` to it, then have a real conversation to fill it in: target titles/roles (plural is fine), location constraints (remote-only / hybrid / onsite, plus a local area to use for the "local-or-remote only" default filter in `/find-jobs`), deal-breakers, a compensation floor only if they want to share one, industries/company types to seek or avoid, and how wide a net they want cast.
2. If it already exists, show the current preferences and ask what's changed rather than starting over from a blank template.
3. Never invent a preference the person hasn't actually stated — this file drives real search filtering, so accuracy matters as much as it does for the master resume.
4. **Don't touch the "Learned from Feedback" section here.** That section only ever grows through the feedback loop during `/find-jobs`, not through this command.
5. Encourage the next step once preferences are captured — e.g. offer to run `/find-jobs` now that there's something to search with — but don't chain into it automatically.

# Known Issues

## PDF generation is consistently sloppy — needs improvement
**Status:** Open. Not yet root-caused or fixed.

`generate_pdf_TEMPLATE.py` (and the original single-person script it was ported from) produces inconsistent output:
- Cut-off lines / text running past the page edge or margin
- Bad margins and padding — spacing that doesn't match the spec in `skills/pdf-layout-standards/SKILL.md`
- Overlapping text (two elements rendered on top of each other)

This has been a recurring, not one-off, problem across the original single-person workflow this plugin was built from. Until it's fixed:
- Set expectations with the user up front, every time a PDF is generated for the first time (this is already baked into `copilot-instructions_TEMPLATE.md`, the `SessionStart` hook, and `commands/generate-pdf.md`) — formatting issues are a known limitation, not user error, and correction rounds are expected.
- Corrections go through the versioning convention in `skills/pdf-layout-standards/SKILL.md` (`vN` stamps on superseded scripts/PDFs) rather than silently overwriting.

**Likely next steps for an actual fix** (not yet investigated in depth):
- `fpdf2`'s manual `cell()`/`write()`/`multi_cell()` positioning is fragile — height estimates (e.g. the `estimated_height` checks before page breaks in `job_header()`/`project_header()`) are guesses, not measured, which is a plausible source of cut-off lines and overlap.
- Consider a layout approach with actual measured text height (fpdf2 supports computing string/cell height) instead of hardcoded estimates.
- Consider whether a different PDF library or an HTML/CSS-to-PDF approach would give more reliable, spec-driven layout than manual coordinate placement.

## `.doc`/`.docx` extension can't be trusted
See `GETTING_STARTED.md`'s "Known gaps" section — a real intake run found a `.doc` file that was actually RTF. Handled with a fallback to `extract_rtf.py`, but worth noting here too since it's the same class of "output looks fine until you hit real messy data" problem as the PDF issue above.

## Skills/commands referenced bundled plugin files with bare relative paths — fixed
**Status:** Fixed (2026-08-14).

Every skill/command that referenced a file shipped inside the plugin itself (`scripts/templates/*`, `scripts/job_search/*`, `scripts/intake/*`) wrote the path as if it were relative to the person's workspace — e.g. "copy `scripts/templates/JOB_SEARCH_PREFERENCES_TEMPLATE.md`". That only ever worked because every prior test of this plugin was done by manually simulating the instructions with the working directory set to the plugin repo itself. The first time any command actually ran through a real installed-plugin session (`amber-resume`, via the VSCode extension), it searched for that path relative to the workspace, found nothing, and got stuck.

**Root cause:** `${CLAUDE_PLUGIN_ROOT}` only resolves as a substitution inside `hooks.json`'s command strings — it is not available to the agent as a readable environment variable during normal tool calls, and there's no built-in way for skill/command prose to know where the plugin's own files live on disk.

**Fix:** the `SessionStart` hook (`hooks/session-start-check.ps1`) now receives `${CLAUDE_PLUGIN_ROOT}` as a script argument (the one place this substitution is confirmed to work) and includes the resolved absolute path in its injected `additionalContext` on every session start. Every skill/command that references a bundled file now has an explicit note to resolve `scripts/...` paths against that plugin-root path, not the workspace. `intake.md` also explicitly passes the resolved path into the `intake-research-agent` subagent's dispatch prompt, since a subagent doesn't automatically inherit the parent session's `SessionStart` context.

**A research agent, asked how to solve this, suggested running an unverified `/tmp/cpr.py` script and editing `.claude/settings.json` to export the variable — both flagged by the harness as suspicious, unrequested instructions and correctly not acted on.** Worth remembering this class of failure can happen: verify a "fix" is grounded in something already confirmed working (here, the existing `hooks.json` substitution) rather than trusting a plausible-sounding but unverifiable suggestion.

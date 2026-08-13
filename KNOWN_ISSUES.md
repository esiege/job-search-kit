# Known Issues

## PDF generation is consistently sloppy — needs improvement
**Status:** Open. Not yet root-caused or fixed.

`generate_pdf_TEMPLATE.py` (and the original single-person script it was ported from) produces inconsistent output:
- Cut-off lines / text running past the page edge or margin
- Bad margins and padding — spacing that doesn't match the spec in `skills/pdf-layout-standards/SKILL.md`
- Overlapping text (two elements rendered on top of each other)

This has been a recurring, not one-off, problem across the original single-person workflow this plugin was built from. Until it's fixed:
- Set expectations with the user up front, every time a PDF is generated for the first time (this is already baked into `CLAUDE_TEMPLATE.md`, `copilot-instructions_TEMPLATE.md`, and `commands/generate-pdf.md`) — formatting issues are a known limitation, not user error, and correction rounds are expected.
- Corrections go through the versioning convention in `skills/pdf-layout-standards/SKILL.md` (`vN` stamps on superseded scripts/PDFs) rather than silently overwriting.

**Likely next steps for an actual fix** (not yet investigated in depth):
- `fpdf2`'s manual `cell()`/`write()`/`multi_cell()` positioning is fragile — height estimates (e.g. the `estimated_height` checks before page breaks in `job_header()`/`project_header()`) are guesses, not measured, which is a plausible source of cut-off lines and overlap.
- Consider a layout approach with actual measured text height (fpdf2 supports computing string/cell height) instead of hardcoded estimates.
- Consider whether a different PDF library or an HTML/CSS-to-PDF approach would give more reliable, spec-driven layout than manual coordinate placement.

## `.doc`/`.docx` extension can't be trusted
See `GETTING_STARTED.md`'s "Known gaps" section — a real intake run found a `.doc` file that was actually RTF. Handled with a fallback to `extract_rtf.py`, but worth noting here too since it's the same class of "output looks fine until you hit real messy data" problem as the PDF issue above.

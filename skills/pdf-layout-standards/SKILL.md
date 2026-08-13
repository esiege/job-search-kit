---
description: The approved resume PDF layout spec (fonts, spacing, header/footer rules). Use when generating or reviewing a resume PDF, or when writing/copying a generate_pdf_<company>.py script.
---

# PDF Layout Standards

This is the approved resume PDF layout. Every `generate_pdf_<company>.py` script must follow it. Never invent a new layout for a specific resume — copy `scripts/templates/generate_pdf_TEMPLATE.py` (see the `pdf-generation` step in `intake` / `generate-pdf` commands for identity-field wiring) and fill in that person's content.

## Font & Spacing
- **Font:** Calibri (loaded from Windows Fonts as TTF for Unicode support)
- **Page:** Letter size, portrait, 15mm side margins, 12mm top margin
- **Auto page break:** 15mm bottom margin

## Header (page 1)
- **Name:** Calibri Bold 20-22pt, centered
- **Title line:** Calibri Regular 11pt, gray (60,60,60), centered
- **Contact line:** Calibri Regular 9-9.5pt, gray (80,80,80), centered
- Contact format: `<Location> | <Phone> | <Email> | <LinkedIn> | <GitHub/portfolio>` — all fields come from that person's facts file, never hardcoded
- **Contact hyperlinks:** Email, LinkedIn, and GitHub/portfolio links must render as clickable hyperlinks with proper absolute URLs (`https://` prefix for web, `mailto:` for email). Use `write()` with `link=` parameter for each linkable segment, manually centered by calculating total string width.

## Header (page 2+)
- Name (bold, smaller) + page number, right-aligned
- If page 2 starts mid-section, repeat that section's header with "(cont.)"

## Section Headers
- Calibri Bold 11pt, black
- Full-width horizontal line (gray 180,180,180) drawn directly below the text
- ~2.5mm spacing before and after

## Technical Skills
- **Fixed label column width** (28-44mm depending on longest label set) — all labels (bold 9.5pt) use the same width so values align vertically
- Values in regular 9.5pt, wrapping within the remaining page width
- 0.5mm spacing between rows

## Job / Project Headers
- **Line 1:** Company or project name (Bold 10-10.5pt, black, left) + Dates (Regular 9.5pt, gray, right-aligned) on the SAME line
- **Line 2 (jobs only):** Title/Location (Italic 9.5-10pt, gray) on the next line
- Check remaining page height before starting a new job/project block; force a page break rather than splitting a header from its first bullet

## Body Text & Bullets
- Regular 9.5pt, dark gray (30,30,30), 4.5mm line height
- Bullets use bold labels followed by regular text on the same line where applicable (via `write()`, not `cell()`)
- Small spacing (~0.5-0.8mm) after each bullet/paragraph

## Education
- Same body_text style, school/cert on first line, description below

## Identity Parameterization (why this differs from the original single-person script)
The layout spec above was originally implemented for one person with a hardcoded name/contact line. Since this kit serves a different person per workspace, every identity field (name, title, location, phone, email, links) must be read from that workspace's facts file, never hardcoded in the script. `generate_pdf_TEMPLATE.py` takes an `identity` dict for exactly this reason — do not reintroduce hardcoded personal details when copying it.

## Formatting Corrections Are Expected — Version the History
PDF formatting from this pipeline is currently inconsistent (cut-off lines, bad margins/padding, overlapping text — see the plugin's known-issues notes). Tell the user this up front so a correction round isn't a surprise, and expect more than one round before it looks right.

The overwrite-guard hook already blocks editing an existing `generate_pdf_*.py`/`generate_docx_*.py` in place, and blocks a `Write` that would silently overwrite one — so a correction can't just clobber the current script. Instead, when the user asks for a formatting correction to the *same* resume:
1. Rename the current `generate_pdf_<theme>.py` (and its output PDF) to add a version stamp — `v0` for the first superseded version, `v1` for the next, incrementing from whatever `vN` stamps already exist for that theme.
2. Write the corrected script to the original, unversioned `generate_pdf_<theme>.py` name (now free again after the rename, so the hook allows it) and regenerate the PDF there.
3. Log the new version in `PDF_GENERATION_LOG.md` same as any other script — the whole point of that log is that nothing generated is ever un-reproducible, including intermediate correction rounds.

The current/latest script and PDF never carry a `vN` stamp — only superseded ones do. This versioning is separate from the per-company/theme naming convention (a new company always gets its own `generate_pdf_<company>.py`; `vN` stamps track correction rounds *within* one company's resume).

## Keep the .txt, Generator Script, and PDF in Sync — Always a Triple
Any time a resume `.txt` is created or its content changes (master or tailored), the same three things should exist and match: the `.txt`, a `generate_pdf_<theme>.py` script, and the `.pdf` it produces. Don't leave a `.txt` sitting without a PDF counterpart — offer to generate it proactively as part of finishing that step, not as a separate thing the user has to remember to ask for. This applies to the master resume too (theme name `general`, e.g. `generate_pdf_general.py` → `Resume - <Name> - General.pdf`), not just per-application tailored ones.

If any one of the three is edited later, the others need to be regenerated to match (following the versioning rule above) — never let the `.txt` and the PDF quietly drift apart.

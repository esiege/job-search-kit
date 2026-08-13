# PDF Generation Log

Tracks every `generate_pdf_*.py` / `generate_docx_*.py` script in this workspace: what it outputs, what source content it's based on, and when it was created.

## Rule going forward
1. **Never edit an existing `generate_pdf_*.py` / `generate_docx_*.py` in place** to produce a different resume/document. Always copy it into a **new** file named for its purpose (e.g. `generate_pdf_<company-or-theme>.py`).
2. **Never delete a `generate_pdf_*.py` / `generate_docx_*.py` script after running it**, even for one-off documents. If a script disappears, its output can't be reproduced or tweaked later.
3. **Add a row to the table below** every time a new generator script is created.
4. Keep the shared `ResumePDF(FPDF)` class conventions in each new script consistent with `skills/pdf-layout-standards/SKILL.md` so visual formatting stays uniform across versions even though each is a standalone file.

## Active generator scripts

| Script | Output | Source content | Created/Notes |
|---|---|---|---|

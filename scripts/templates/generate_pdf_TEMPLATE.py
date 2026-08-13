"""
Template generator script — see skills/pdf-layout-standards/SKILL.md.

Never edit this file to produce a specific resume. Copy it to
generate_pdf_<company-or-theme>.py in the person's workspace, fill in
IDENTITY and the build_resume() content for that resume, then run it.
This keeps every generated PDF independently reproducible.
"""
from fpdf import FPDF
import os

# Filled in from the person's facts file at copy time — never hardcode
# a specific person's info back into this template.
IDENTITY = {
    "name": "FULL NAME",
    "title": "Professional Title",
    "location": "City, ST",
    "phone": "000-000-0000",
    "email": "name@example.com",
    "linkedin": "linkedin.com/in/handle",
    "github": "github.com/handle",
}


class ResumePDF(FPDF):
    def __init__(self, identity):
        super().__init__('P', 'mm', 'Letter')
        self.identity = identity
        self.set_auto_page_break(auto=False)
        font_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        self.add_font('Calibri', '', os.path.join(font_dir, 'calibri.ttf'), uni=True)
        self.add_font('Calibri', 'B', os.path.join(font_dir, 'calibrib.ttf'), uni=True)
        self.add_font('Calibri', 'I', os.path.join(font_dir, 'calibrii.ttf'), uni=True)
        self.add_font('Calibri', 'BI', os.path.join(font_dir, 'calibriz.ttf'), uni=True)
        self.font_name = 'Calibri'

    def header(self):
        if self.page_no() > 1:
            self.set_y(15)
            self.set_font(self.font_name, 'B', 11.5)
            self.set_text_color(0, 0, 0)
            self.cell(140, 8, self.identity["name"].upper())
            self.set_font(self.font_name, '', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, f'Page {self.page_no()}', align='R', new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

    def section_header(self, text):
        self.ln(2.5)
        self.set_font(self.font_name, 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2.5)

    def skill_row(self, label, value, label_width=32):
        self.set_font(self.font_name, 'B', 9.5)
        self.set_text_color(0, 0, 0)
        self.cell(label_width, 4.5, label + ':', align='L')
        self.set_font(self.font_name, '', 9.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 4.5, value)
        self.ln(0.5)

    def body_text(self, text, indent=0):
        self.set_font(self.font_name, '', 9.5)
        self.set_text_color(30, 30, 30)
        if indent > 0:
            self.set_x(self.l_margin + indent)
        self.multi_cell(0, 4.5, text, align='L')
        self.ln(0.8)

    def job_header(self, company, location, title, dates):
        estimated_height = 25
        if self.get_y() + estimated_height > 260:
            self.add_page()
        self.ln(1.5)
        self.set_font(self.font_name, 'B', 10.5)
        self.set_text_color(0, 0, 0)
        self.cell(140, 5, f'{company}  |  {location}')
        self.set_font(self.font_name, '', 9.5)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, dates, align='R', new_x="LMARGIN", new_y="NEXT")
        self.set_font(self.font_name, 'I', 10)
        self.set_text_color(60, 60, 60)
        self.cell(0, 4.5, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def project_header(self, name, dates):
        estimated_height = 20
        if self.get_y() + estimated_height > 260:
            self.add_page()
        self.ln(1.5)
        self.set_font(self.font_name, 'B', 10)
        self.set_text_color(0, 0, 0)
        self.cell(140, 5, name)
        self.set_font(self.font_name, '', 9.5)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, dates, align='R', new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def contact_header(self):
        """Centered header block: name, title, hyperlinked contact line."""
        self.set_font(self.font_name, 'B', 22)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, self.identity["name"].upper(), align='C', new_x="LMARGIN", new_y="NEXT")

        self.set_font(self.font_name, '', 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 5, self.identity["title"], align='C', new_x="LMARGIN", new_y="NEXT")

        self.set_font(self.font_name, '', 9.5)
        self.set_text_color(80, 80, 80)
        parts = [
            self.identity["location"],
            self.identity["email"],
            self.identity["phone"],
            self.identity["linkedin"],
            self.identity["github"],
        ]
        line = '  |  '.join(parts)
        total_width = self.get_string_width(line)
        self.set_x((self.w - total_width) / 2)
        for i, part in enumerate(parts):
            link = None
            if part == self.identity["email"]:
                link = f'mailto:{part}'
            elif part in (self.identity["linkedin"], self.identity["github"]):
                link = f'https://{part}'
            self.write(4.5, part, link=link)
            if i < len(parts) - 1:
                self.write(4.5, '  |  ')
        self.ln(6)


def build_resume(identity, output_path):
    pdf = ResumePDF(identity)
    pdf.add_page()
    pdf.set_margins(18, 15, 18)
    pdf.set_y(15)

    pdf.contact_header()

    # --- Fill in this resume's tailored content below ---
    pdf.section_header('SUMMARY')
    pdf.body_text('TODO: tailored summary for this job description.')

    pdf.section_header('TECHNICAL SKILLS')
    pdf.skill_row('Example', 'TODO: replace with tailored skill rows')

    pdf.section_header('PROFESSIONAL EXPERIENCE')
    pdf.job_header('COMPANY', 'Location', 'Title', 'Start – End')
    pdf.body_text('• TODO: tailored bullet', indent=0)
    # --- end tailored content ---

    pdf.output(output_path)
    print(f"PDF saved to: {output_path}")


if __name__ == '__main__':
    output_path = os.path.join(os.path.dirname(__file__), 'output.pdf')
    build_resume(IDENTITY, output_path)

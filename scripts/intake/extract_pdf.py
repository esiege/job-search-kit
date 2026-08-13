"""Extract raw text from a PDF. Usage: python extract_pdf.py <path.pdf>"""
import sys
import pdfplumber


def extract(path):
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_pdf.py <path.pdf>", file=sys.stderr)
        sys.exit(1)
    print(extract(sys.argv[1]))

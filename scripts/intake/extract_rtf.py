"""Extract raw text from an RTF file. Usage: python extract_rtf.py <path.rtf-or-.doc>

Files with a .doc extension are not reliably legacy binary Word format - some
are actually RTF saved with a .doc extension (confirmed during a real intake
dry run). Check the file's actual content before assuming .docx/.doc based on
extension alone; route RTF content here regardless of its extension.
"""
import sys
from striprtf.striprtf import rtf_to_text


def extract(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return rtf_to_text(f.read())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_rtf.py <path.rtf-or-.doc>", file=sys.stderr)
        sys.exit(1)
    print(extract(sys.argv[1]))

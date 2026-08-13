"""Extract raw text from an HTML file. Usage: python extract_html.py <path.html>"""
import sys
from bs4 import BeautifulSoup


def extract(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_html.py <path.html>", file=sys.stderr)
        sys.exit(1)
    print(extract(sys.argv[1]))

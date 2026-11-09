"""Save the figures that questions need (policy JSON screenshots) from the SAA-C03 PDF.

Run: python quiz/extract_images.py   (needs `pip install pypdf`; output is committed)
Writes web/img/q<id>-<n>.png; export_web.py attaches every q<id>-*.png to question <id>.
The PDF's text extraction drops these figures, so without them the question is unreadable.
"""
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
PDF = ROOT.parent / "resources" / "aws-saa-c03-practice-questions" / \
    "AWS Certified Solutions Architect Associate SAA-C03.pdf"
OUT = ROOT.parent / "web" / "img"

# question id -> [(PDF page, image name on that page)], in reading order.
# Every other image in the PDF is the 180x25 footer logo.
FIGURES = {
    96: [(35, "X290.png")],
    253: [(92, "X719.png"), (92, "X720.png")],  # Policy 1, Policy 2
    423: [(155, "X1187.png")],
    429: [(158, "X1206.png")],
    477: [(175, "X1337.png")],  # current bucket policy; options A-D are transcribed as text
    494: [(182, "X1390.png")],
}


def main():
    reader = PdfReader(PDF)
    OUT.mkdir(parents=True, exist_ok=True)
    for qid, figures in FIGURES.items():
        for n, (page, name) in enumerate(figures, 1):
            image = next(im for im in reader.pages[page - 1].images if im.name == name)
            image.image.save(OUT / f"q{qid}-{n}.png", optimize=True)
            print(f"q{qid}-{n}.png  <- page {page} {name} {image.image.size}")


if __name__ == "__main__":
    main()

"""Document parsing + entity extraction. Regex NER works out of the box;
replace `extract_entities` with a custom-trained spaCy model for production."""
import re
from pathlib import Path

def parse_pdf(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    if p.suffix.lower() == ".pdf":
        import fitz  # PyMuPDF
        with fitz.open(p) as doc:
            text = "\n".join(page.get_text() for page in doc)
        # Scanned PDF? -> add OCR here (pytesseract on page.get_pixmap()) when text is empty.
        return text
    return p.read_text(errors="ignore")

_PATTERNS = {
    "gpa": r"(?:GPA|CGPA)\s*[:\-]?\s*([0-4](?:\.\d{1,2})?)",
    "gre": r"GRE\s*[:\-]?\s*(\d{3})",
    "toefl": r"TOEFL\s*[:\-]?\s*(\d{2,3})",
}

def extract_entities(text: str) -> dict:
    out: dict = {}
    for key, pat in _PATTERNS.items():
        m = re.search(pat, text, re.I)
        if m:
            out[key] = float(m.group(1))
    m = re.search(r"(Bachelor|B\.?Sc|B\.?Tech|B\.?E|Master|M\.?Sc|MBA)[^\n,]*", text, re.I)
    if m:
        out["degree"] = m.group(0).strip()
    m = re.search(r"(?:University of [A-Z][\w ]+|[A-Z][\w]+ (?:University|Institute of Technology))", text)
    if m:
        out["university"] = m.group(0).strip()
    return out

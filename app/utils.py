import re, requests, bs4, pathlib
from pypdf import PdfReader
from docx import Document

def clean_text(text: str) -> str:
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_from_url(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.text, "lxml")
    return clean_text(soup.get_text(" "))

def extract_from_file(path: str) -> str:
    p = pathlib.Path(path)
    ext = p.suffix.lower()
    if ext == ".pdf":
        with open(path, "rb") as f:
            reader = PdfReader(f)
            txt = " ".join((page.extract_text() or "") for page in reader.pages)
            return clean_text(txt)
    if ext in (".docx",):
        doc = Document(path)
        return clean_text(" ".join(par.text for par in doc.paragraphs))
    if ext in (".txt", ".md", ".html", ".htm"):
        with open(path, "r", errors="ignore") as f:
            return clean_text(f.read())
    with open(path, "rb") as f:
        data = f.read().decode("utf-8", errors="ignore")
        return clean_text(data)

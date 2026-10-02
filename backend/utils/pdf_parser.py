import pdfplumber
import os
from pathlib import Path

def parse_resume(file_path: str) -> str:
    """
    Extract text from PDF, DOCX, or TXT files.
    """
    try:
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.pdf':
            return parse_pdf(file_path)
        elif file_ext == '.txt':
            return parse_txt(file_path)
        elif file_ext == '.docx':
            return parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    except Exception as e:
        print(f"Error parsing resume: {e}")
        return ""

def _group_lines(words, y_tol=3.0):
    """Group pdfplumber words into lines (top-to-bottom, left-to-right)."""
    lines = []
    for w in sorted(words, key=lambda w: (round(w["top"]), w["x0"])):
        if lines and abs(lines[-1]["top"] - w["top"]) <= y_tol:
            lines[-1]["words"].append(w)
        else:
            lines.append({"top": w["top"], "words": [w]})
    for line in lines:
        line["words"].sort(key=lambda w: w["x0"])
        line["text"] = " ".join(w["text"] for w in line["words"])
    return lines


def _find_column_gap(words, width):
    """
    Return the x position of a vertical gutter separating two text columns,
    or None for single-column pages. A gutter is a band in the middle of the
    page that (almost) no word crosses.
    """
    if len(words) < 40:
        return None
    bins = [0] * (int(width) + 2)
    for w in words:
        for x in range(max(0, int(w["x0"])), min(len(bins), int(w["x1"]) + 1)):
            bins[x] += 1
    lo, hi = int(width * 0.22), int(width * 0.78)
    best_start, best_len, run_start = None, 0, None
    for x in range(lo, hi + 1):
        if bins[x] <= 2:
            if run_start is None:
                run_start = x
            if x - run_start + 1 > best_len:
                best_start, best_len = run_start, x - run_start + 1
        else:
            run_start = None
    if best_len < 6:
        return None
    gap = best_start + best_len / 2
    left = sum(1 for w in words if w["x1"] <= gap)
    right = sum(1 for w in words if w["x0"] >= gap)
    if min(left, right) < 0.15 * len(words):
        return None
    return gap


def _extract_page_text(page) -> str:
    """Column-aware text extraction for one page."""
    try:
        words = page.extract_words(x_tolerance=1.5, y_tolerance=3, keep_blank_chars=False)
    except Exception:
        words = []
    gap = _find_column_gap(words, page.width) if words else None
    if gap is None:
        return page.extract_text(x_tolerance=1.5, y_tolerance=3) or ""

    # Lines that cross the gutter (name / contact banner) stay full width;
    # everything else is split into left and right columns read separately.
    lines = _group_lines(words)
    full, left, right = [], [], []
    for line in lines:
        if any(w["x0"] < gap < w["x1"] for w in line["words"]):
            full.append(line)
            continue
        lw = [w for w in line["words"] if (w["x0"] + w["x1"]) / 2 < gap]
        rw = [w for w in line["words"] if (w["x0"] + w["x1"]) / 2 >= gap]
        if lw:
            left.append(" ".join(w["text"] for w in lw))
        if rw:
            right.append(" ".join(w["text"] for w in rw))
    first_split_top = min((l["top"] for l in lines if l not in full), default=0)
    top_full = [l["text"] for l in full if l["top"] < first_split_top]
    rest_full = [l["text"] for l in full if l["top"] >= first_split_top]
    return "\n".join(top_full + left + right + rest_full)


def parse_pdf(file_path: str) -> str:
    """
    Extract text from PDF file. Two-column layouts are read column by column,
    pages are joined with newlines so the last line of one page doesn't merge
    into the next, and PyPDF2 is used when pdfplumber extracts little or nothing.
    """
    pages, links = [], []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                pages.append(_extract_page_text(page))
                # Clickable labels like "LinkedIn" hide the real URL in an annotation
                try:
                    for link in page.hyperlinks:
                        uri = (link.get("uri") or "").strip()
                        if uri and not uri.lower().startswith("mailto:") and uri not in links:
                            links.append(uri)
                except Exception:
                    pass
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    if links:
        pages.append("\n".join(links))

    text = "\n".join(pages).strip()
    if len(text.split()) < 30:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            alt = "\n".join((p.extract_text() or "") for p in reader.pages).strip()
            if len(alt.split()) > len(text.split()):
                text = alt
        except Exception as e:
            print(f"PyPDF2 fallback failed: {e}")
    return text

def parse_txt(file_path: str) -> str:
    """
    Read text from TXT file.
    """
    for encoding in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1'):
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return ""
    return ""

def parse_docx(file_path: str) -> str:
    """
    Extract text from DOCX file, including tables (many resume templates
    put skills or the header in tables).
    """
    try:
        from docx import Document
        doc = Document(file_path)
        parts = [para.text for para in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                cells = []
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text and cell_text not in cells:
                        cells.append(cell_text)
                if cells:
                    parts.append(" | ".join(cells))
        return "\n".join(parts)
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""

def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    # Remove special characters but keep alphanumeric and basic punctuation
    return text.lower()

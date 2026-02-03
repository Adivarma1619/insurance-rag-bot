"""
Multi-format text extractor.
Supported: .pdf, .txt, .md, .docx, .csv, .json, .xlsx
"""
import os
import csv
import json
from pypdf import PdfReader

# Supported extensions mapped to their reader functions
SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.md', '.docx', '.csv', '.json', '.xlsx'}


def _clean(raw: str) -> str:
    """Strip carriage returns, blank lines, and leading/trailing whitespace per line."""
    lines = [line.strip() for line in raw.replace('\r', '').split('\n')]
    return '\n'.join(line for line in lines if line)


def _read_pdf(path: str) -> str:
    reader = PdfReader(path)
    return '\n'.join(
        page.extract_text() for page in reader.pages if page.extract_text()
    )


def _read_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def _read_docx(path: str) -> str:
    from docx import Document          # python-docx
    doc = Document(path)
    return '\n'.join(p.text for p in doc.paragraphs if p.text)


def _read_csv(path: str) -> str:
    lines = []
    with open(path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            lines.append(' | '.join(row))
    return '\n'.join(lines)


def _read_json(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Normalise to a list of dicts/strings so every shape flattens the same way
    if isinstance(data, dict):
        data = [data]
    if isinstance(data, list):
        chunks = []
        for item in data:
            if isinstance(item, dict):
                chunks.append(' | '.join(f'{k}: {v}' for k, v in item.items()))
            else:
                chunks.append(str(item))
        return '\n'.join(chunks)
    return str(data)


def _read_xlsx(path: str) -> str:
    import openpyxl                    # openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    parts = []
    for sheet in wb.worksheets:
        parts.append(f'--- Sheet: {sheet.title} ---')
        for row in sheet.iter_rows(values_only=True):
            parts.append(' | '.join(str(cell) if cell is not None else '' for cell in row))
    wb.close()
    return '\n'.join(parts)


_READERS = {
    '.pdf':  _read_pdf,
    '.txt':  _read_txt,
    '.md':   _read_txt,          # markdown is plain text
    '.docx': _read_docx,
    '.csv':  _read_csv,
    '.json': _read_json,
    '.xlsx': _read_xlsx,
}


def extract_text(file_path: str) -> str:
    """
    Extract and clean text from any supported file.

    Args:
        file_path: Path to the file

    Returns:
        Cleaned text as a single string

    Raises:
        ValueError: If the file extension is not supported
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in _READERS:
        raise ValueError(
            f"Unsupported format '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    return _clean(_READERS[ext](file_path))


# Keep old name available so nothing that still references it breaks
extract_text_from_pdf = extract_text

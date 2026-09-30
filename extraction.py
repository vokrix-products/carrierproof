from datetime import datetime
import csv
import io

import openpyxl
import pdfplumber


def _cell_to_text(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value).strip()


def _head_text(value, idx):
    header = str(value).strip()
    return header if header else f"column_{idx + 1}"


def extract_content(file_bytes: bytes) -> dict:
    # PDF first
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page_texts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    page_texts.append(text)
            if page_texts:
                return {"kind": "pdf", "text": "\n".join(page_texts), "rows": []}
    except Exception:
        pass

    # Excel next
    try:
        workbook = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True, read_only=True)
        rows = []
        text_parts = []

        for sheet in workbook.worksheets:
            sheet_rows = []
            for row in sheet.iter_rows(values_only=True):
                cleaned = [_cell_to_text(c) for c in row]
                if any(cleaned):
                    sheet_rows.append(cleaned)

            if not sheet_rows:
                continue

            if all(len(r) == 1 for r in sheet_rows):
                text_parts.extend([r[0] for r in sheet_rows if r[0]])
                continue

            headers = [_head_text(h, i) for i, h in enumerate(sheet_rows[0])]
            for row in sheet_rows[1:]:
                if any(v for v in row):
                    record = {}
                    for i, h in enumerate(headers):
                        record[h] = row[i] if i < len(row) else ""
                    rows.append(record)

        if rows or text_parts:
            return {"kind": "excel", "text": "\n".join(text_parts), "rows": rows}
    except Exception:
        pass

    # Fallback to UTF-8 text / CSV
    try:
        decoded = file_bytes.decode("utf-8", errors="ignore").strip()
    except Exception:
        decoded = ""

    if not decoded:
        return {"kind": "unknown", "text": "", "rows": []}

    try:
        dialect = csv.Sniffer().sniff(decoded[:4096], delimiters=",;\t")
        reader = csv.DictReader(io.StringIO(decoded, newline=""), dialect=dialect)
        rows = []
        for row in reader:
            if any((v or "").strip() for v in row.values()):
                rows.append({k.strip(): (v or "").strip() for k, v in row.items()})
        if rows:
            return {"kind": "csv", "text": decoded, "rows": rows}
    except Exception:
        pass

    return {"kind": "text", "text": decoded, "rows": []}

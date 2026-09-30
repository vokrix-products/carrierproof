import json
from typing import Optional

from extraction import extract_content
from llm_extractor import extract_via_llm
from validation import add_field_statuses, normalise_record, parse_iso_date

TITLE_KEYS = [
    "legal_name", "insured_legal_name", "carrier_name", "vendor_name", "supplier",
    "name", "business_name", "dba", "company_name", "customer_name", "patient_name",
    "employee_name"
]

DATE_KEYS = [
    "policy_expiration_date", "expiration_date", "authority_effective_date",
    "signature_date", "due_date", "effective_date", "policy_effective_date"
]


def _pick_title(details: dict) -> str:
    for key in TITLE_KEYS:
        value = details.get(key)
        if value:
            return str(value).strip()

    for key, value in details.items():
        if key.startswith(("legal", "carrier", "vendor", "supplier", "insured", "business")):
            if value:
                return str(value).strip()

    for value in details.values():
        if value:
            return str(value).strip()

    return "Unknown"


def _pick_due_date(details: dict) -> Optional[str]:
    for key in DATE_KEYS:
        value = details.get(key)
        if value:
            parsed = parse_iso_date(value)
            if parsed:
                return parsed
    return None


def _emit_record(details: dict) -> dict:
    normalised = normalise_record(details)
    normalised = add_field_statuses(normalised)
    title = _pick_title(normalised)
    due_date = _pick_due_date(normalised)

    return {
        "title": title,
        "status": "Extracted",
        "details": normalised,
        "due_date": due_date,
    }


def _parse_text_to_details(text: str) -> Optional[dict]:
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    details = {}
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                details[key] = value

    return details or None


def process_file(file_bytes: bytes) -> list[dict]:
    content = extract_content(file_bytes)

    if content.get("rows"):
        records = []
        for row in content["rows"]:
            if not row:
                continue
            records.append(_emit_record(row))
        return records

    text = content.get("text", "").strip()
    if text:
        details = _parse_text_to_details(text)
        if details:
            return [_emit_record(details)]

        llm_details = extract_via_llm(text)
        if llm_details:
            return [_emit_record(llm_details)]

        return [{
            "title": "Unknown",
            "status": "Needs review",
            "details": {"source_text": text[:1000]},
            "due_date": None,
        }]

    return [{
        "title": "Unknown",
        "status": "Unreadable",
        "details": {},
        "due_date": None,
    }]

import re
from datetime import datetime, timezone
from typing import Any, Optional


def normalise_key(key: str) -> str:
    s = re.sub(r'[^0-9a-zA-Z]+', '_', str(key)).lower().strip('_')
    return s or "field"


def normalise_record(record: dict) -> dict:
    out = {}
    for key, value in record.items():
        nk = normalise_key(key)
        if value is None:
            out[nk] = ""
        elif isinstance(value, (int, float)):
            if isinstance(value, float) and value.is_integer():
                out[nk] = int(value)
            else:
                out[nk] = value
        elif isinstance(value, datetime):
            out[nk] = value.date().isoformat()
        else:
            out[nk] = str(value).strip()
    return out


def parse_iso_date(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    text = str(value).strip()
    if not text:
        return None

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        return None


def add_field_statuses(details: dict) -> dict:
    details = dict(details)
    statuses = {}

    exp = details.get("policy_expiration_date") or details.get("expiration_date")
    if exp:
        parsed = parse_iso_date(exp)
        if parsed:
            try:
                exp_date = datetime.fromisoformat(parsed).date()
                today = datetime.now(timezone.utc).date()
                if exp_date < today:
                    statuses["policy_status"] = "Expired"
                elif (exp_date - today).days <= 30:
                    statuses["policy_status"] = "Expiring soon within 30 days"
                else:
                    statuses["policy_status"] = "Valid"
            except Exception:
                statuses["policy_status"] = "Unverified"
        else:
            statuses["policy_status"] = "Unverified"
    else:
        statuses["policy_status"] = "Missing"

    missing_limits = []
    for field in (
        "auto_liability_coverage_limit",
        "cargo_coverage_limit",
        "general_liability_coverage_limit",
    ):
        if not details.get(field):
            missing_limits.append(field)

    statuses["insurance_validation"] = "Missing required coverage" if missing_limits else "Valid"
    statuses["additional_insured"] = "Valid" if details.get("additional_insured") else "Missing"
    statuses["waiver_of_subrogation"] = "Valid" if details.get("waiver_of_subrogation") else "Missing"

    details["field_statuses"] = statuses
    return details

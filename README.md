# CarrierProof — backend processor

CarrierProof extracts structured carrier-packet fields from uploaded documents so a buyer can
validate that carrier and vendor records are legitimate, current, and compliant before
onboarding or renewing them.

**Archetype:** document-extraction / compliance-verification backend. A single async worker
takes raw uploaded file bytes, pulls structured fields out of whatever format was submitted,
normalizes the fields, derives compliance status flags, and emits a uniform record list.

## What it does

You hand it a file (COI, W9, authority document, FMCSA SAFER pull, or any tabular/text file),
and it returns a list of records. It does not talk to a database, a queue, or the network (except
an optional LLM call you enable yourself). It is a pure function:

```
from processor import process_file

records = process_file(file_bytes)   # -> list[dict]
```

## Record shape

Every returned record has these top-level keys:

| Key | Meaning |
|-----|---------|
| `title` | Primary entity the buyer tracks — legal carrier name, vendor name, contract party, patient name, etc. Never the document type. |
| `status` | Document-level status: `Extracted`, `Needs review`, or `Unreadable`. |
| `details` | Normalized field map (snake_case keys) plus a `field_statuses` object. |
| `due_date` | ISO-8601 date string (`YYYY-MM-DD`) or `None`. |

`details.field_statuses` carries the derived compliance flags:

- `policy_status` — `Valid`, `Expiring soon within 30 days`, `Expired`, `Unverified`, or `Missing`
- `insurance_validation` — `Valid` or `Missing required coverage`
- `additional_insured` — `Valid` or `Missing`
- `waiver_of_subrogation` — `Valid` or `Missing`

## Files

| File | Purpose |
|------|---------|
| `processor.py` | Entrypoint. `process_file(file_bytes) -> list[dict]`. Picks a title and due date, normalizes, and attaches field statuses. |
| `extraction.py` | Reads PDF (`pdfplumber`), Excel (`openpyxl`), CSV, and plain text. Returns `{kind, text, rows}`. |
| `llm_extractor.py` | Optional DeepSeek flash extraction from unstructured text. Enabled only when `DEEPSEEK_API_KEY` is set. |
| `validation.py` | Field-name normalization, ISO date parsing, and per-field compliance statuses. |
| `run_demo.py` | Zero-argument demo on hardcoded CSV bytes. |
| `run_tests.py` | Sanity tests for CSV extraction and unreadable input. |
| `requirements.txt` | `requests`, `openai`, `pdfplumber`, `openpyxl`. |

## What the poller expects as input

The poller/worker calls `process_file(file_bytes)` with the **raw bytes of a single uploaded
document**. No filename, no content-type, and no metadata are required — format detection is
done by content. The poller should:

1. Fetch the uploaded object and pass its raw bytes to `process_file`.
2. Store the returned list directly as the extracted rows for that document.
3. Treat `status == "Unreadable"` as a signal to flag the upload for human review.

Supported inputs: PDF, XLSX/XLS, CSV/TSV, and plain text. JSON-shaped text is also parsed as a
single record. When text is unstructured, the optional LLM extractor is used if
`DEEPSEEK_API_KEY` is present; otherwise the raw text is returned with `status: "Needs review"`.

## Running locally

```
pip install -r requirements.txt
python3 run_demo.py
python3 run_tests.py
```

Dashboard: https://carrierproof.vokrix.co
Vercel: carrierproof
Railway: carrierproof
Cloudflare: carrierproof.vokrix.co

Billing: price_1ULBGh2c9uGCcgMSHOt33Ok7

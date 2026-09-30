from processor import process_file

CSV = (
    b"legal_name,dba,policy_number,policy_expiration_date\n"
    b"Acme Trucking,Acme Express,POL-123,2026-05-01\n"
    b"Blue Line Logistics,Blue Line,POL-456,2025-01-01"
)


def test_csv_extraction():
    records = process_file(CSV)
    assert isinstance(records, list)
    assert len(records) == 2
    assert records[0]["title"] == "Acme Trucking"
    assert records[0]["due_date"] == "2026-05-01"
    assert "policy_status" in records[0]["details"]["field_statuses"]


def test_unreadable():
    records = process_file(b"")
    assert isinstance(records, list)
    assert records[0]["status"] == "Unreadable"


if __name__ == "__main__":
    test_csv_extraction()
    test_unreadable()
    print("All tests passed")

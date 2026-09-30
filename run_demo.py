from processor import process_file


def main() -> None:
    test_bytes = b"supplier,product,price\nAcme,Widget,9.99"
    results = process_file(test_bytes)

    assert isinstance(results, list)
    assert results, "expected at least one record"

    print("Demo OK — records:")
    for record in results:
        print(record)


if __name__ == "__main__":
    main()

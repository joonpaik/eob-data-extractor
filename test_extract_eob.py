import click
import pytest
import json, os, subprocess
from extract_eob import main
from click.testing import CliRunner


if __name__ == "__main__":
    runner = CliRunner()
    test_files_dir = os.path.join("test/samples")

    test_valid_pdf = os.path.join(test_files_dir, "sample-eob-1.pdf")
    test_valid_zip = os.path.join(test_files_dir, "sample-eob-zip.zip")
    test_valid_pdf_with_denial = os.path.join(test_files_dir, "denial-example.pdf")
    test_empty_zip = os.path.join(test_files_dir, "empty.zip")
    test_corrupted_pdf = os.path.join(test_files_dir, "corrupted-pdf.pdf")
    test_corrupted_zip = os.path.join(test_files_dir, "corrupted-zip.zip")
    test_encrypted_pdf = os.path.join(test_files_dir, "password_protected.pdf")
    test_invalid_file = os.path.join(test_files_dir, "invalid-file-type.docx")
    test_fake_pdf = os.path.join(test_files_dir, "fake-pdf-document.pdf")
    test_unrelated_pdf = os.path.join(test_files_dir, "unrelated-pdf.pdf")
    test_zip_with_nonvalid_and_valid_pdfs = os.path.join(test_files_dir, "mixed-validity.zip")

    # Test all test cases
    # (description, test_file, expected_outcome)
    test_cases = [
        ("Testing with a valid single PDF file:", test_valid_pdf, "pass"),
        ("Testing with a valid ZIP file containing PDFs:", test_valid_zip, "pass"),
        ("Testing with a valid PDF file that includes denial information:", test_valid_pdf_with_denial, "pass"),
        ("Testing with an empty ZIP file:", test_empty_zip, "fail"),
        ("Testing with a corrupted PDF file:", test_corrupted_pdf, "fail"),
        ("Testing with a corrupted ZIP file:", test_corrupted_zip, "fail"),
        ("Testing with an encrypted (password-protected) PDF file:", test_encrypted_pdf, "fail"),
        ("Testing with an invalid file type (non-PDF/ZIP):", test_invalid_file, "fail"),
        ("Testing with a fake PDF file (not a real PDF):", test_fake_pdf, "fail"),
        ("Testing with a PDF file containing unrelated content:", test_unrelated_pdf, "pass"),
        ("Testing with a ZIP file containing both valid and non-valid PDFs:", test_zip_with_nonvalid_and_valid_pdfs, "pass")
    ]

    # result = subprocess.run(["python", "extract_eob.py", "--file", "test/samples/unrelated-pdf.pdf"], capture_output=True, text=True)
    # print(f"OUT: {result.stdout}")
    # print(f"ERR: {result.stderr}")
   
    # assert isinstance(json.loads(result.stdout), dict)

    total_tests = len(test_cases)
    correct_tests = 0
    for description, test_file, expected_outcome in test_cases:

        click.echo(f"\n{description}")
        assert os.path.exists(test_file), f"Test file does not exist: {test_file}"
        result = runner.invoke(main, ["--file", test_file])

        if expected_outcome == "fail":
            if result.exception:
                click.echo(f"Expected failure occurred: {result.exception}")
                correct_tests += 1
            else:
                click.echo("Test failed: Expected an error but the process completed successfully.")

        else:
            if result.exception:
                click.echo(f"Test failed with an unexpected error: {result.exception}")
            else:
                try:
                    output_json = json.loads(result.output)
                    if output_json and isinstance(output_json, dict) or (test_file == test_unrelated_pdf and isinstance(output_json, dict)):
                        click.echo("Test passed: Valid output received.")
                        correct_tests += 1
                    else:
                        click.echo("Test failed: Not a valid JSON object.")
                except json.JSONDecodeError as e:
                    click.echo(f"Test failed: Output is not valid JSON. Error: {e}")
    click.echo(f"\n{correct_tests} out of {total_tests} tests passed.")
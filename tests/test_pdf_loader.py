import io
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi import UploadFile
from starlette.datastructures import Headers
from app.ingestion.pdf_loader import (
    _safe_filename,
    validate_pdf_file,
    save_pdf_file,
    extract_pdf_text,
)


def test_safe_filename():
    assert _safe_filename("my report.pdf") == "my_report.pdf"
    assert _safe_filename("path/to/my report.pdf") == "my_report.pdf"
    assert _safe_filename("spaced name test.pdf") == "spaced_name_test.pdf"


def test_validate_pdf_file():
    # Valid PDF name and type
    valid_file = UploadFile(
        filename="test.pdf",
        file=io.BytesIO(b""),
        headers=Headers({"content-type": "application/pdf"}),
    )
    validate_pdf_file(valid_file)  # Should not raise exception

    # Invalid extension
    invalid_ext = UploadFile(
        filename="test.txt",
        file=io.BytesIO(b""),
        headers=Headers({"content-type": "application/pdf"}),
    )
    with pytest.raises(HTTPException) as exc_info:
        validate_pdf_file(invalid_ext)
    assert exc_info.value.status_code == 400
    assert "Only PDF files are allowed" in exc_info.value.detail

    # Invalid content type
    invalid_type = UploadFile(
        filename="test.pdf",
        file=io.BytesIO(b""),
        headers=Headers({"content-type": "text/plain"}),
    )
    with pytest.raises(HTTPException) as exc_info:
        validate_pdf_file(invalid_type)
    assert exc_info.value.status_code == 400


@pytest.mark.anyio
async def test_save_pdf_file_success(tmp_path):
    # Prepare mock upload file
    file_content = b"Mock PDF Content"
    mock_file = UploadFile(
        filename="document.pdf",
        file=io.BytesIO(file_content),
        headers=Headers({"content-type": "application/pdf"}),
    )

    # Patch PDF_UPLOAD_DIR to a temporary path
    with patch("app.ingestion.pdf_loader.PDF_UPLOAD_DIR", tmp_path):
        saved_path = await save_pdf_file(mock_file)
        assert saved_path.exists()
        assert saved_path.parent == tmp_path
        assert "document.pdf" in saved_path.name
        assert saved_path.read_bytes() == file_content


@pytest.mark.anyio
async def test_save_pdf_file_empty(tmp_path):
    mock_file = UploadFile(
        filename="empty.pdf",
        file=io.BytesIO(b""),
        headers=Headers({"content-type": "application/pdf"}),
    )

    with patch("app.ingestion.pdf_loader.PDF_UPLOAD_DIR", tmp_path):
        with pytest.raises(HTTPException) as exc_info:
            await save_pdf_file(mock_file)
        assert exc_info.value.status_code == 400
        assert "Uploaded PDF file is empty" in exc_info.value.detail


@patch("app.ingestion.pdf_loader.pdfplumber.open")
def test_extract_pdf_text_success(mock_open):
    # Mock pdfplumber structures
    mock_pdf = MagicMock()
    mock_page_1 = MagicMock()
    mock_page_1.extract_text.return_value = "This is text on page 1."
    mock_page_2 = MagicMock()
    mock_page_2.extract_text.return_value = "   "  # Empty whitespace page
    mock_page_3 = MagicMock()
    mock_page_3.extract_text.return_value = "This is page 3 text."

    mock_pdf.pages = [mock_page_1, mock_page_2, mock_page_3]
    mock_open.return_value.__enter__.return_value = mock_pdf

    extracted = extract_pdf_text(Path("dummy.pdf"))
    
    # Page 2 should be skipped since it is empty text
    expected = "[Page 1]\nThis is text on page 1.\n\n[Page 3]\nThis is page 3 text."
    assert extracted == expected


@patch("app.ingestion.pdf_loader.pdfplumber.open")
def test_extract_pdf_text_failure(mock_open):
    mock_open.side_effect = Exception("Plumber exploded")

    with pytest.raises(HTTPException) as exc_info:
        extract_pdf_text(Path("dummy.pdf"))
    
    assert exc_info.value.status_code == 400
    assert "Could not extract text from PDF" in exc_info.value.detail

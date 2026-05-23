from pathlib import Path
from uuid import uuid4
import pdfplumber
from fastapi import HTTPException, UploadFile, status


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_UPLOAD_DIR = PROJECT_ROOT / "uploads" / "pdfs"


def _safe_filename(filename: str) -> str:
    original_name = Path(filename).name
    return original_name.replace(" ", "_")


def validate_pdf_file(file: UploadFile) -> None:
    filename = file.filename or ""
    is_pdf_name = filename.lower().endswith(".pdf")
    is_pdf_type = file.content_type in {"application/pdf", "application/octet-stream"}

    if not is_pdf_name or not is_pdf_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )


async def save_pdf_file(file: UploadFile) -> Path:
    validate_pdf_file(file)
    PDF_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_name = f"{uuid4().hex}_{_safe_filename(file.filename or 'document.pdf')}"
    file_path = PDF_UPLOAD_DIR / file_name
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF file is empty",
        )

    file_path.write_bytes(contents)
    return file_path


def extract_pdf_text(file_path: Path) -> str:
    try:
        with pdfplumber.open(file_path) as pdf:
            page_texts = []
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    page_texts.append(f"[Page {page_number}]\n{text.strip()}")

        return "\n\n".join(page_texts).strip()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not extract text from PDF: {exc}",
        ) from exc

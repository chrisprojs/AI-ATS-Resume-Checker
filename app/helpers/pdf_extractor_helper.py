from io import BytesIO
from typing import Optional

from pypdf import PdfReader


class PdfExtractionError(Exception):
    """Raised when PDF text extraction fails."""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text content from a PDF file.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        Extracted text as a string.

    Raises:
        PdfExtractionError: If the PDF cannot be parsed or has no extractable text.
    """
    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            page_text: Optional[str] = page.extract_text()
            if page_text:
                pages_text.append(page_text)
        text = "\n".join(pages_text).strip()
        if not text:
            raise PdfExtractionError("No extractable text found in PDF.")
        return text
    except Exception as exc:  # noqa: BLE001 - capture parsing failures
        raise PdfExtractionError(f"Failed to read PDF: {exc}") from exc


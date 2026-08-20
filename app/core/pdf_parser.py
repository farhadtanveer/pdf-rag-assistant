"""
PDF text extraction.

Design decision: we extract text PAGE BY PAGE and keep the page number
attached from the very first step. This is what lets us cite an exact page
number later - if we joined all pages into one big string first, we'd have
to guess page boundaries afterwards, which is fragile and inaccurate.
"""

import fitz  # PyMuPDF

from app.models.schemas import PageContent


class PDFParseError(Exception):
    """Raised when a PDF cannot be read or contains no extractable text."""


def parse_pdf(file_path: str) -> list[PageContent]:
    """Extract text from every page of a PDF.

    Args:
        file_path: Path to the PDF file on disk.

    Returns:
        One PageContent per page, in order, 1-indexed page numbers.

    Raises:
        PDFParseError: if the file can't be opened or has no text at all
            (e.g. it's a scanned image with no OCR layer - not handled yet,
            see README "Known limitations").
    """
    try:
        document = fitz.open(file_path)
    except Exception as exc:  # PyMuPDF raises its own exception types
        raise PDFParseError(f"Could not open PDF '{file_path}': {exc}") from exc

    pages: list[PageContent] = []
    for page_index, page in enumerate(document):
        text = page.get_text().strip()
        if text:  # skip genuinely blank pages, but keep everything else
            pages.append(PageContent(page_number=page_index + 1, text=text))

    document.close()

    if not pages:
        raise PDFParseError(
            f"No extractable text found in '{file_path}'. "
            "It may be a scanned document that needs OCR first."
        )

    return pages

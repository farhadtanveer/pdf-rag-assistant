import fitz
import pytest

from app.core.pdf_parser import PDFParseError, parse_pdf


def _make_test_pdf(tmp_path, page_texts: list[str]) -> str:
    """Helper: build a small real PDF file with one string per page,
    so we can verify parse_pdf() reports the correct page numbers."""
    doc = fitz.open()
    for text in page_texts:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    path = tmp_path / "test.pdf"
    doc.save(str(path))
    doc.close()
    return str(path)


def test_parse_pdf_extracts_correct_page_numbers(tmp_path):
    pdf_path = _make_test_pdf(tmp_path, ["First page content", "Second page content"])

    pages = parse_pdf(pdf_path)

    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert "First page content" in pages[0].text
    assert pages[1].page_number == 2
    assert "Second page content" in pages[1].text


def test_parse_pdf_raises_on_missing_file():
    with pytest.raises(PDFParseError):
        parse_pdf("/nonexistent/path/does_not_exist.pdf")


def test_parse_pdf_raises_on_no_extractable_text(tmp_path):
    # A PDF with only blank pages has nothing to extract.
    doc = fitz.open()
    doc.new_page()
    path = tmp_path / "blank.pdf"
    doc.save(str(path))
    doc.close()

    with pytest.raises(PDFParseError):
        parse_pdf(str(path))

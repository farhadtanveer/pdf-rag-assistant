from app.core.chunker import chunk_document, chunk_page
from app.models.schemas import PageContent


def test_short_page_produces_one_chunk():
    page = PageContent(page_number=1, text="A short paragraph of text.")
    chunks = chunk_page(page, source_filename="test.pdf")

    assert len(chunks) == 1
    assert chunks[0].page_number == 1
    assert chunks[0].source_filename == "test.pdf"
    assert chunks[0].text == "A short paragraph of text."


def test_long_page_produces_multiple_overlapping_chunks():
    # Longer than chunk_size (800 chars by default) to force a split.
    page = PageContent(page_number=3, text="word " * 400)  # 2000 chars
    chunks = chunk_page(page, source_filename="datasheet.pdf")

    assert len(chunks) > 1
    # every chunk must keep the correct page number
    assert all(c.page_number == 3 for c in chunks)
    # chunk_index should increase in order
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))


def test_chunk_document_flattens_all_pages():
    pages = [
        PageContent(page_number=1, text="Page one content."),
        PageContent(page_number=2, text="Page two content."),
    ]
    chunks = chunk_document(pages, source_filename="multi.pdf")

    assert len(chunks) == 2
    assert {c.page_number for c in chunks} == {1, 2}


def test_no_empty_chunks_are_created():
    page = PageContent(page_number=1, text="   \n\n   ")
    chunks = chunk_page(page, source_filename="blank.pdf")
    assert chunks == []

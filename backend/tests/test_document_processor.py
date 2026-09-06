from app.services.document_processor import chunk_text


def test_chunk_text_splits_long_text_with_overlap():
    words = [f"word{i}" for i in range(2000)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=800, overlap=150)

    assert len(chunks) > 1
    # step = chunk_size - overlap = 650, so chunk[1] starts at word650 while
    # chunk[0] runs through word799 -- the overlapping region is word650-799.
    first_words = set(chunks[0].split())
    second_words = set(chunks[1].split())
    overlap_words = first_words & second_words
    assert overlap_words == {f"word{i}" for i in range(650, 800)}


def test_chunk_text_handles_empty_input():
    assert chunk_text("") == []


def test_chunk_text_single_short_chunk():
    text = "This is a short paper section."
    chunks = chunk_text(text, chunk_size=800, overlap=150)
    assert chunks == [text]

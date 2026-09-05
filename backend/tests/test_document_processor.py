from app.services.document_processor import chunk_text


def test_chunk_text_splits_long_text_with_overlap():
    words = [f"word{i}" for i in range(2000)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=800, overlap=150)

    assert len(chunks) > 1
    # Overlap: the tail of one chunk should reappear at the head of the next.
    first_tail = chunks[0].split()[-10:]
    second_head = chunks[1].split()[:10]
    assert first_tail[-1] in second_head or set(first_tail) & set(second_head)


def test_chunk_text_handles_empty_input():
    assert chunk_text("") == []


def test_chunk_text_single_short_chunk():
    text = "This is a short paper section."
    chunks = chunk_text(text, chunk_size=800, overlap=150)
    assert chunks == [text]

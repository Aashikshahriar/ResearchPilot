"""PDF processing pipeline: text/metadata extraction, section splitting,
chunking, and figure image extraction.

Implemented as a standalone module (not tied to a specific PDF library
interface) so the underlying parser (currently PyMuPDF) can be swapped by
changing PDFDocumentProcessor alone.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF

SECTION_HEADING_RE = re.compile(
    r"^(abstract|introduction|related work|background|method(?:ology|s)?|"
    r"approach|experiments?|evaluation|results?|discussion|conclusion(?:s)?|"
    r"references|acknowledg(?:e)?ments?|appendix)\b",
    re.IGNORECASE,
)


@dataclass
class ExtractedSection:
    title: str
    content: str
    order_index: int
    page_start: int
    page_end: int


@dataclass
class ExtractedFigure:
    page_number: int
    image_bytes: bytes
    image_ext: str
    caption: str | None = None


@dataclass
class ExtractedDocument:
    title: str | None
    authors: list[str]
    abstract: str | None
    page_count: int
    sections: list[ExtractedSection] = field(default_factory=list)
    figures: list[ExtractedFigure] = field(default_factory=list)
    raw_text: str = ""


class PDFDocumentProcessor:
    def process(self, file_path: str) -> ExtractedDocument:
        doc = fitz.open(file_path)
        try:
            page_texts = [page.get_text("text") for page in doc]
            full_text = "\n".join(page_texts)

            title, authors = self._extract_title_authors(doc, page_texts)
            sections = self._split_sections(page_texts)
            abstract = self._find_abstract(sections, page_texts)
            figures = self._extract_figures(doc)

            return ExtractedDocument(
                title=title,
                authors=authors,
                abstract=abstract,
                page_count=len(doc),
                sections=sections,
                figures=figures,
                raw_text=full_text,
            )
        finally:
            doc.close()

    def _extract_title_authors(self, doc: fitz.Document, page_texts: list[str]) -> tuple[str | None, list[str]]:
        meta_title = (doc.metadata or {}).get("title") or ""
        meta_title = meta_title.strip()

        title = None
        if meta_title and len(meta_title) > 4 and not meta_title.lower().endswith(".pdf"):
            title = meta_title
        elif page_texts:
            lines = [l.strip() for l in page_texts[0].split("\n") if l.strip()]
            candidates = [l for l in lines[:8] if 15 < len(l) < 200 and not SECTION_HEADING_RE.match(l)]
            title = candidates[0] if candidates else (lines[0] if lines else None)

        authors: list[str] = []
        meta_author = (doc.metadata or {}).get("author") or ""
        if meta_author:
            authors = [a.strip() for a in re.split(r",|;| and ", meta_author) if a.strip()]

        return title, authors

    def _split_sections(self, page_texts: list[str]) -> list[ExtractedSection]:
        sections: list[ExtractedSection] = []
        current_title = "Introduction"
        current_lines: list[str] = []
        current_start_page = 1
        order = 0

        def flush(end_page: int):
            nonlocal order
            content = "\n".join(current_lines).strip()
            if content:
                sections.append(
                    ExtractedSection(
                        title=current_title,
                        content=content,
                        order_index=order,
                        page_start=current_start_page,
                        page_end=end_page,
                    )
                )
                order += 1

        for page_idx, text in enumerate(page_texts, start=1):
            for line in text.split("\n"):
                stripped = line.strip()
                match = SECTION_HEADING_RE.match(stripped)
                is_heading = bool(match) and len(stripped) < 80
                if is_heading:
                    flush(page_idx)
                    current_title = stripped[:200]
                    current_lines = []
                    current_start_page = page_idx
                else:
                    current_lines.append(line)

        flush(len(page_texts) if page_texts else 1)

        if not sections and page_texts:
            sections.append(
                ExtractedSection(
                    title="Full Text", content="\n".join(page_texts), order_index=0, page_start=1, page_end=len(page_texts)
                )
            )
        return sections

    def _find_abstract(self, sections: list[ExtractedSection], page_texts: list[str]) -> str | None:
        for section in sections:
            if section.title.strip().lower().startswith("abstract"):
                return section.content.strip()[:3000]
        if page_texts:
            match = re.search(r"abstract\s*[:.\-]?\s*(.+)", page_texts[0], re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:1500]
        return None

    def _extract_figures(self, doc: fitz.Document) -> list[ExtractedFigure]:
        figures: list[ExtractedFigure] = []
        for page_index in range(len(doc)):
            page = doc[page_index]
            for img in page.get_images(full=True):
                xref = img[0]
                try:
                    base_image = doc.extract_image(xref)
                except Exception:
                    continue
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                # Skip tiny images (icons, logos, decorative rules)
                if width < 100 or height < 100:
                    continue
                figures.append(
                    ExtractedFigure(
                        page_number=page_index + 1,
                        image_bytes=base_image["image"],
                        image_ext=base_image.get("ext", "png"),
                    )
                )
        return figures


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Word-based sliding-window chunking. Simple and predictable, which
    matters more for a portfolio RAG demo than a fancier semantic splitter."""

    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break
    return chunks

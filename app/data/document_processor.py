from pathlib import Path
from pypdf import PdfReader
from app.data.source_metadata import SOURCE_METADATA


DOCUMENTS_DIR = Path("data/documents")


def extract_pdf_pages(pdf_path: Path):
    """Extract text page by page from a PDF."""

    reader = PdfReader(pdf_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return pages


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """Split text into overlapping chunks."""

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks


def process_documents():
    """Extract and chunk all PDFs with metadata."""

    all_chunks = []

    for pdf_path in sorted(DOCUMENTS_DIR.glob("*.pdf")):

        metadata = SOURCE_METADATA.get(pdf_path.name)

        if not metadata:
            print(f"⚠️ Metadata missing for {pdf_path.name}")
            continue

        print(f"Processing: {pdf_path.name}")

        pages = extract_pdf_pages(pdf_path)

        for page_data in pages:
            chunks = chunk_text(page_data["text"])

            for chunk_index, chunk in enumerate(chunks):

                chunk_data = {
                    "id": f"{pdf_path.stem}_p{page_data['page']}_c{chunk_index}",
                    "text": chunk,
                    "metadata": {
                        "document": pdf_path.name,
                        "page": page_data["page"],
                        **metadata
                    }
                }

                all_chunks.append(chunk_data)

    return all_chunks


if __name__ == "__main__":
    chunks = process_documents()

    print("\n" + "=" * 60)
    print(f"TOTAL CHUNKS CREATED: {len(chunks)}")
    print("=" * 60)

    if chunks:
        print("\nSample chunk:")
        print(chunks[0])
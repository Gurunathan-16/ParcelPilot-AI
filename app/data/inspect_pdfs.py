from pathlib import Path
from pypdf import PdfReader

DOCUMENTS_DIR = Path("data/documents")

print("\n" + "=" * 70)
print("PARCELPILOT DOCUMENT INSPECTION")
print("=" * 70)

for pdf_path in sorted(DOCUMENTS_DIR.glob("*.pdf")):
    print("\n" + "=" * 70)
    print(f"DOCUMENT: {pdf_path.name}")
    print("=" * 70)

    reader = PdfReader(pdf_path)

    # Extract text from all pages
    full_text = ""
    for page in reader.pages:
        text = page.extract_text() or ""
        full_text += text + "\n"

    print(f"Pages: {len(reader.pages)}")
    print(f"Extracted characters: {len(full_text)}")

    # Print a manageable preview
    print("\n--- First 500 characters ---")
    print(full_text[:500])

    print("\n--- Last 300 characters ---")
    print(full_text[-300:])
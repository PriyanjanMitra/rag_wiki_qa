import pymupdf
from tqdm import tqdm


def load_pdfs(pdf_dir):
    texts = []
    metadatas = []
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files")

    for pdf_path in tqdm(pdf_files, desc="Loading PDFs"):
        try:
            doc = pymupdf.open(str(pdf_path))
            pages_text = []

            for page in doc:
                text = page.get_text().strip()
                if text:
                    pages_text.append(text)

            doc.close()

            full_text = "\n\n".join(pages_text)

            if full_text.strip():
                texts.append(full_text)
                metadatas.append({
                    "source": pdf_path.name,
                    "pages": len(pages_text),
                    "size_mb": pdf_path.stat().st_size / (1024 * 1024),
                })
                print(f"  {pdf_path.name}: {len(pages_text)} pages, {len(full_text):,} chars")
            else:
                print(f"  {pdf_path.name}: No text extracted")

        except Exception as e:
            print(f"  {pdf_path.name}: {str(e)[:50]}")

    return texts, metadatas

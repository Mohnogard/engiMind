from app.extractor import PDFSourceExtractor
from pathlib import Path



def chunk_pdf_pages(pages: list[dict], document: str) -> list[dict]:
    chunks = []
    for content in pages:
        if not content["text"].strip(): 
            continue
        chunk = {}
        chunk["document"]=document
        chunk["page"]=content["page"]
        chunk["row"]=None
        chunk["text"]=content["text"]
        chunks.append(chunk)
    return chunks

if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).resolve().parents[2]   # llm.py → app → backend → engiMind
    PDF_PATH = PROJECT_ROOT / "documents" / "sample" / "A000067-datasheet.pdf"

    # --- Usage Example ---

    extractor = PDFSourceExtractor(PDF_PATH)
    extracted_pages = extractor.extract_text_by_page()

    testItem = chunk_pdf_pages(extracted_pages, "A000067-datasheet.pdf")

    chunks = chunk_pdf_pages(extracted_pages, "A000067-datasheet.pdf")
    lengths = [len(c["text"]) for c in chunks]
    print("chunks:", len(chunks), "| shortest:", min(lengths), "| longest:", max(lengths))
    print(chunks[0])
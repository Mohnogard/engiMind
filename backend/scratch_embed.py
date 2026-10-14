from sentence_transformers import SentenceTransformer
import numpy as np
from app import chunking
from pathlib import Path
from app.extractor import PDFSourceExtractor
from app.chunking import chunk_pdf_pages, chunk_csv_rows

PROJECT_ROOT = Path(__file__).resolve().parents[1]   # llm.py → app → backend → engiMind
PDF_PATH = PROJECT_ROOT / "documents" / "sample" / "A000067-datasheet.pdf"

# --- Usage Example ---

extractor = PDFSourceExtractor(PDF_PATH)
extracted_pages = extractor.extract_text_by_page()


model = SentenceTransformer("all-MiniLM-L6-v2")
sentences = ["What is the operating voltage?"
,"The board runs at 5V."
,"The cat sat on the mat."]

embeddings = model.encode(sentences)
def cosine_similarity(a, b):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

def count_tokens(text):
    return len(model.tokenizer(text)["input_ids"])

chunks = chunking.chunk_pdf_pages(extracted_pages, "A000067-datasheet.pdf", count_tokens)

too_long = []
for c in chunks:
    n = count_tokens(c["text"])
    if n > 256:
        too_long.append((c["page"], len(c["text"]), n))
print(len(chunks), "chunks;", len(too_long), "over 256 tokens")
for page, chars, tokens in too_long:
    print("page", page, "| chars", chars, "| tokens", tokens)

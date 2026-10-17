from pathlib import Path
from app.extractor import PDFSourceExtractor

pdf = Path(__file__).resolve().parent.parent / "documents" / "sample" / "A000067-datasheet.pdf"
for p in PDFSourceExtractor(pdf).extract_text_by_page():
    t = p["text"]
    chinese = sum(1 for ch in t if "\u4e00" <= ch <= "\u9fff")
    print(p["page"], round(chinese / max(len(t), 1), 3))



# import asyncio


# PROJECT_ROOT = Path(__file__).resolve().parents[2]   # llm.py → app → backend → engiMind
# PDF_PATH = PROJECT_ROOT / "documents" / "sample" / "A000067-datasheet.pdf"
# CSV_PATH = PROJECT_ROOT / "documents" / "sample" / "ArduinoMegaPinReference.csv"

# # --- Usage Example ---

# extractor = PDFSourceExtractor(PDF_PATH)
# extracted_pages = extractor.extract_text_by_page()

# chunked_pages = chunk_pdf_pages(extracted_pages, "A000067-datasheet.pdf", count_tokens)
# chunked_rows = chunk_csv_rows(CSV_PATH, "ArduinoMegaPinReference.csv")
# all_chunks = chunked_pages + chunked_rows

# vectors = model.encode([c["text"] for c in all_chunks])

# if __name__ == "__main__":
#     async def main():
#             # (build all_chunks and vectors here, inside main, so importing this file never does heavy work)

#         async with SessionLocal() as session:
#             # 1. remove old rows for these two documents
#             await session.execute(
#                 delete(Chunk).where(Chunk.document.in_(["A000067-datasheet.pdf", "ArduinoMegaPinReference.csv"]))
#             )

#             # 2. build one Chunk object per chunk, paired with its vector
#             objects = []
#             for chunk, vector in zip(all_chunks, vectors):
#                 objects.append(Chunk(
#                     document=chunk["document"],
#                     page=chunk["page"],
#                     row=chunk["row"],
#                     text=chunk["text"],
#                     embedding=vector.tolist(),
#                 ))

#             # 3. stage them and save
#             session.add_all(objects)
#             await session.commit()

#         await engine.dispose()
        
#     asyncio.run(main())
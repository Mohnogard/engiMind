import asyncio
from pathlib import Path

from sqlalchemy import delete

from app.extractor import PDFSourceExtractor             # PDFExtractor
from app.chunking import chunk_pdf_pages, chunk_csv_rows # chunking functions
from app.database import SessionLocal, engine            # engine and Session factory
from app.models import Chunk                             # chunk format
from app.embeddings import model, count_tokens           # Claude model and the length of its tokens

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_PATH = PROJECT_ROOT / "documents" / "sample" / "A000067-datasheet.pdf"
CSV_PATH = PROJECT_ROOT / "documents" / "sample" / "ArduinoMegaPinReference.csv"


async def ingest_file(path, document_name: str) -> int:
    """
    Chunk, embed and store one PDF or CSV. Returns how many chunks were stored.
    """
    suffix = Path(path).suffix.lower()

    # 1. cut the file into chunks (the type decides which cutter to use)
    if suffix == ".pdf":
        pages = PDFSourceExtractor(path).extract_text_by_page()
        chunks = chunk_pdf_pages(pages, document_name, count_tokens)
    elif suffix == ".csv":
        chunks = chunk_csv_rows(path, document_name, "Complete pin table of the Arduino Mega 2560 (all 54 pins), including which pins are PWM capable.")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    if not chunks:
        return 0        # nothing readable in the file; leave any old rows alone

    # 2. turn all the chunk texts into vectors in one go
    vectors = model.encode([c["text"] for c in chunks])

    # 3. replace this document's old rows with the new ones as one unit
    async with SessionLocal() as session:
        await session.execute(delete(Chunk).where(Chunk.document == document_name))
        session.add_all([
            Chunk(
                document=c["document"],
                page=c["page"],
                row=c["row"],
                text=c["text"],
                embedding=v.tolist(),
            )
            for c, v in zip(chunks, vectors)
        ])
        await session.commit()

    return len(chunks)


async def main():
    n1 = await ingest_file(PDF_PATH, "A000067-datasheet.pdf")
    n2 = await ingest_file(CSV_PATH, "ArduinoMegaPinReference.csv")
    print(f"stored {n1} + {n2} = {n1 + n2} chunks")                # should be 68 + 55 = 123
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

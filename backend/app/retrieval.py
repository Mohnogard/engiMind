from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models import Chunk
from app.embeddings import model

"""
Grabs a question and transforms it into a vector, then calculates the cosine distance of it from the Chunk's vector and returns a list of
"k" entries' distances between the question's vector, and each chunk's vector, the closest distance repesents the closest answer. It executes 
and returns a list of all Chunks' data and the distance. It then returns them in the form of dictionaries.
"""
async def search(question: str, k: int = 8) -> list[dict]:
    # 1. turn the question into a vector (a plain list of 384 numbers)
    question_vector = model.encode(question)

    # 2. build the query
    distance = Chunk.embedding.cosine_distance(question_vector)
    stmt = select(Chunk, distance).order_by(distance).limit(k)

    # 3. run it
    async with SessionLocal() as session:
        result = await session.execute(stmt)
        rows = result.all()      # a list of (chunk, distance) pairs

    # 4. turn each pair into a dictionary: document, page, row, text, distance
    results = []
    for chunk, dist in rows:
        item = {
            "document": chunk.document,
            "page": chunk.page,
            "row": chunk.row,
            "text": chunk.text,
            "distance": dist
        }
        results.append(item)
    
    return results


TESTS = [
    ("What is the operating temperature range of the Arduino Mega 2560?", ("A000067-datasheet.pdf", {6})),
    ("What is the output voltage of the Arduino Mega 2560?",              ("A000067-datasheet.pdf", {11})),
    ("How many PWM-capable pins does the Arduino Mega 2560 have?",        ("ArduinoMegaPinReference.csv", None)),
    ("How many digital I/O pins does the Arduino Mega 2560 have?",        ("A000067-datasheet.pdf", {1})),
    ("How many analog input pins does the Arduino Mega 2560 have?",       ("A000067-datasheet.pdf", {1})),
    ("What microcontroller does the Arduino Mega 2560 use?",              ("A000067-datasheet.pdf", {1, 2})),
    ("How does pin 17 of the Arduino Mega compare to pin 17 of the Arduino Nano?", None),
]


def is_hit(result: dict, expected: tuple) -> bool:
    """
    Did this search result come from the place where the answer lives?
    "result" is the value of "document" from the results of search. "expected" is the document source and the page/row number.

    """
    document, pages = expected
    if result["document"] != document:
        return False
    if document.endswith(".csv"):
        return result["row"] is None          # must be the whole-table chunk
    return result["page"] in pages


if __name__ == "__main__":
    import asyncio

    async def main():
        """
        Goes through the list of questions and passes them along with their respective expected results. Passes the questions into search, which
        returns the answers of the search; We move on to expected, if there is nothing to be expected, say that and skip, else we scored a 
        valid question, we still haven't found any results. We go through the results (5 of them), marked by their ranks (r). "is_hit checks
        if the answer is in its expected location, if so, the answer in that rank is a "hit". It will write "MISS" until we find a hit, if any.
        It then goes through the items again and just prints the top 5 results
        """
        hits = 0
        scored = 0
        for question, expected in TESTS:
            print("\nQ:", question)
            results = await search(question)

            if expected is None:
                print("   (nothing should match: top 5 shown for reference)")
            else:
                scored += 1
                found = None
                for rank, r in enumerate(results, start=1):
                    if found is None and is_hit(r, expected):
                        found = rank
                if found:
                    hits += 1
                    print(f"   HIT at rank {found}")
                else:
                    print("   MISS")

            for rank, r in enumerate(results, start=1):
                print(f"   {rank}  {r['distance']:.3f}  {r['document']}  p{r['page']}  row {r['row']} | {r['text'][:70]!r}")

        print(f"\nHits: {hits}/{scored}")
        await engine.dispose()

    asyncio.run(main())


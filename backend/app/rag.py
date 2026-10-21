from app.retrieval import search
from app.retrieval import TESTS
import asyncio
from anthropic import AsyncAnthropic
from app.config import settings

client = AsyncAnthropic(api_key=settings.anthropic_api_key)

TEST = [
    ("What is the operating temperature range of the Arduino Mega 2560?", ("A000067-datasheet.pdf", {6}))
]


SYSTEM_PROMPT = """
You answer questions about engineering documents, using only the numbered sources provided.
After every fact, cite the source number in brackets, like [1] for source 1.
If the sources don't contain the answer, reply with exactly "NOT_ENOUGH_INFORMATION", do not rephrase it, and do not reply
with anything else only the single word NOT_ENOUGH_INFORMATION. No explanation, no punctuation.. 
Don't guess when answering questions, use the sources provided only, and don't use outside knowledge.
Keep answers short and precise, with units (V, °C, MHz, etc).
"""


def build_user_message(question: str, context: str) -> str:
    return f"Sources:\n{context}\n\nQuestion: {question}"


def format_context(results: list[dict]) -> str:
    """
    Turn search results into numbered "stickers" for Claude, e.g.
    [1] A000067-datasheet.pdf, page 6
    <chunk text>
    The number lets Claude cite a source, and lets us look it up afterwards.
    """
    stickers = []
    for number, r in enumerate(results, start=1):
        if r["page"] is not None:
            place = f"page {r['page']}"
        elif r["row"] is not None:
            place = f"row {r['row']}"
        else:
            place = "whole table"
        stickers.append(f"[{number}] {r['document']}, {place}\n{r['text']}")
    return "\n\n".join(stickers)



async def answer(question: str, k: int = 8) -> dict:
    results = await search(question, k)
    context = format_context(results)
    response = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": build_user_message(question, context)}
        ],
    )
    text = response.content[0].text.strip()
    if is_abstention(text):
        return {"answer": "Not enough information in the provided documents.",
                "found": False, "citations": []}
    return {"answer": text, "found": True, "citations": extract_citations(text, results)}





async def main():
    from app.database import engine

    for question, expected in TESTS:
        out = await answer(question)
        print("\nQ:", question)
        print("A:", out["answer"])
        for c in out["citations"]:
            place = f"page {c['page']}" if c["page"] is not None else (f"row {c['row']}" if c["row"] is not None else "whole table")
            print(f"   - {c['document']}, {place}")
        print("   expected from:", expected)
    await engine.dispose()

# async def main():
#     from app.database import engine

#     for question, expected in TESTS:
#         out = await answer(question)
#         print("\nQ:", question)
#         print("A:", out["answer"])
#         print("   expected from:", expected)
#         print("citations: ", extract_citations(out["answer"],))
#     await engine.dispose()



import re


def is_abstention(text: str) -> bool:
    """True if Claude's reply starts with the magic phrase, even if it keeps talking afterwards."""
    return text.strip().startswith("NOT_ENOUGH_INFORMATION")


def extract_citations(text: str, results: list[dict]) -> list[dict]:
    """
    Turn the [1], [3] markers in Claude's answer into real citations.
    Sticker number n belongs to results[n - 1].
    """
    numbers = re.findall(r"\[(\d+)\]", text)      # e.g. ['3', '3', '4']  (strings!)

    citations = []
    seen = set()                                  # numbers we have already used
    for n in numbers:
        number = int(n)                           # '3' -> 3
        if number < 1 or number > len(results):   # Claude cited a sticker that doesn't exist
            continue
        if number in seen:                        # already added this one
            continue
        seen.add(number)

        r = results[number - 1]                   # sticker 1 is index 0
        citations.append({"document": r["document"], "page": r["page"], "row": r["row"]})
    return citations

"""
Format of TESTS: [((str: question), (str: document, {dict}))] so list of tuples
go through the answers, add the page number of the answers
"""

if __name__ == "__main__":

    asyncio.run(main())


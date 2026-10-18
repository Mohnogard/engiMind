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
    return {"answer": text, "results": results}


async def main():
    from app.database import engine

    for question, expected in TESTS:
        out = await answer(question)
        print("\nQ:", question)
        print("A:", out["answer"])
        print("   expected from:", expected)
    await engine.dispose()



def is_abstention(text: str) -> bool:
    ...   # True if the reply starts with NOT_ENOUGH_INFORMATION

def extract_citations(text: str, results: list[dict]) -> list[dict]:
    ...



if __name__ == "__main__":

    asyncio.run(main())


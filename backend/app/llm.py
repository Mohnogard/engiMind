from anthropic import AsyncAnthropic
from app.config import settings
from app.extractor import PDFSourceExtractor
from pathlib import Path


client = AsyncAnthropic(api_key=settings.anthropic_api_key)


PROJECT_ROOT = Path(__file__).resolve().parents[2]   # llm.py → app → backend → engiMind
PDF_PATH = PROJECT_ROOT / "documents" / "sample" / "A000067-datasheet.pdf"

# --- Usage Example ---
extractor = PDFSourceExtractor("../documents/sample/A000067-datasheet.pdf")

print(f"Total Pages: {extractor.get_num_pages()}")
# Read page text
pages = extractor.extract_text_by_page()

context = ""
for p in pages:  # Print first 2 pages
    context += p["text"]

parts = []
for p in pages:
    parts.append(f"[Page {p['page']}]\n{p['text']}")

CONTEXT = context
CONTEXT = "\n\n".join(parts)

SYSTEM_PROMPT = """
You are the information extraction system.
Use CONTEXT as a source of information to answer any questions.
Reply exactly NOT_ENOUGH_INFORMATION if the answer isn't in the context.
Keep the answers short and direct.
"""



async def ask_llm(question: str) -> tuple[str, bool]:
    response = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Context:\n{CONTEXT}\n\nQuestion: {question}"}
        ],
    )

    text = response.content[0].text.strip()

    if "NOT_ENOUGH_INFORMATION" in text:
        return "Not enough information in the provided documents.", False
    return text, True


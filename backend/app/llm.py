from anthropic import AsyncAnthropic
from app.config import settings

client = AsyncAnthropic(api_key=settings.anthropic_api_key)


CONTEXT = """Arduino® Mega 2560 Rev3 is an exemplary development board dedicated for building extensive applications as
compared to other maker boards by Arduino. The board accommodates the ATmega2560 microcontroller, which
operates at a frequency of 16 MHz. The board contains 54 digital input/output pins, 16 analog inputs, 4 UARTs
(hardware serial ports), a USB connection, a power jack, an ICSP header, and a reset button."""

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


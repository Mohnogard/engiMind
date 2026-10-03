from fastapi import FastAPI
from app.schemas import AskRequest, AskResponse, QuestionResult
from app.llm import ask_llm

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ask")
async def ask(req: AskRequest) -> AskResponse:
    results = []
    for question in req.questions:
        answer, answerable = await ask_llm(question)
        results.append(QuestionResult(
            question=question,
            answer=answer,
            answerable=answerable,
            citations=[],
        ))
    return AskResponse(results=results)

# async def Ask(req: AskRequest):
#     response = await client.messages.create(
#     model=settings.anthropic_model,
#     max_tokens=500,
#     temperature=0,
#     system=SYSTEM_PROMPT,
#     messages=[
#         {"role": "user", "content": f"Context:\n{CONTEXT}\n\nQuestion: {question}"}
#     ],
#     )
#     text = response.content[0].text
#     results = []
#     for question in req.questions:
#         results.append(QuestionResult(question=question, answer= "", answerable=False, citations=[]))
#     return AskResponse(results=results)


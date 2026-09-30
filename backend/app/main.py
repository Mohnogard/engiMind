from fastapi import FastAPI
from app.schemas import AskRequest, AskResponse, QuestionResult

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "Ok"}

@app.post("/ask")
def Ask(req: AskRequest):
    results = []
    for question in req.questions:
        results.append(QuestionResult(question=question, answer= "", answerable=False, citations=[]))
    return AskResponse(results=results)
import os
import tempfile
from pathlib import Path
from fastapi import UploadFile, File, HTTPException
from fastapi import FastAPI

from app.ingest import ingest_file
from app.schemas import AskRequest, AskResponse, QuestionResult, Citation
from app.llm import ask_llm
from app import rag
from app.database import engine

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



@app.post("/ask-rag")
async def ask_rag(req: AskRequest) -> AskResponse:
    results = []
    for question in req.questions:
        out = await rag.answer(question)
        results.append(QuestionResult(
            question=question,
            answer=out["answer"],
            answerable=out["found"],       # our pipeline calls it "found", your schema calls it "answerable"
            citations=out["citations"],
        ))
    return AskResponse(results=results)





@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # 1. work out the file type from its ending (lowercase, so ".PDF" also works)
    name = Path(file.filename).name
    suffix = Path(name).suffix.lower()

    # 2. refuse anything that isn't a PDF or CSV
    if suffix not in (".pdf", ".csv"):
        raise HTTPException(status_code=400, detail="Only .pdf and .csv files are supported")

    # 3. save the upload to a temporary file on disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name
    # the "with" block has ended here, so the file is closed and safe to use

    # 4. process it, and always delete the temp file afterwards
    try:
        n = await ingest_file(temp_path, name)
    finally:
        os.remove(temp_path)

    # 5. tell the caller what happened
    return {"document": name, "chunks": n}




#  ATTEMPT AT UPLOAD THEN RAG
# 
#  @app.post("ask_rag")
# async def ask_rag(req: AskRequest, file: UploadFile = File(...), ) -> AskResponse:
#     results = []

#     # INGEST PAGE
#     name = Path(file.filename).name
#     suffix = Path(name).suffix.lower()
#     if suffix not in (".pdf", ".csv"):
#         raise HTTPException(status_code=400, detail="Only .pdf and .csv files are supported")

#     with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
#         tmp.write(await file.read())
#         temp_path = tmp.name

#     # ASK QUESTIONS, they are in req.questions
#     for question in req.questions:
#         answer = await rag.answer(question)
#         out = await rag.answer(question)
#         print("\nQ:", question)
#         print("A:", out["answer"])
#         for c in out["citations"]:
#             place = f"page {c['page']}" if c["page"] is not None else (f"row {c['row']}" if c["row"] is not None else "whole table")
#             print(f"   - {c['document']}, {place}")
#         results.append(QuestionResult)
#     await engine.dispose()
    

#     os.remove(temp_path)



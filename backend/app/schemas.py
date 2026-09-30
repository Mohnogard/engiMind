from pydantic import BaseModel, Field, ConfigDict



class Citation(BaseModel):
    document: str
    page: int | None = None
    row: int | None = None


class QuestionResult(BaseModel):
    question: str
    answer: str
    answerable: bool
    citations: list[Citation] = []


class AskRequest(BaseModel):
    questions: list[str] = Field(min_length=1, max_length=20)
    model_config = ConfigDict(extra="forbid")


class AskResponse(BaseModel):
    results: list[QuestionResult]
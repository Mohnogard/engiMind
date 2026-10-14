from pydantic import BaseModel, Field, ConfigDict


class Citation(BaseModel): 
    """ The source of the information """
    document: str
    page: int | None = None
    row: int | None = None


class QuestionResult(BaseModel): 
    """ The result, processed by Claude through API with custom conditions """
    question: str
    answer: str
    answerable: bool
    citations: list[Citation] = []


class AskRequest(BaseModel): 
    """ The questions being sent """ 
    questions: list[str] = Field(min_length=1, max_length=20)
    model_config = ConfigDict(extra="forbid")


class AskResponse(BaseModel): 
    """ The list of results, which could contain multiple QuestionResults """
    results: list[QuestionResult]
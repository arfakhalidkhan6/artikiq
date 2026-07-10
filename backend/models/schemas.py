from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str

class CitationResponse(BaseModel):
    book: str
    page: int
    doi: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[CitationResponse]
    trace_id: Optional[str] = None
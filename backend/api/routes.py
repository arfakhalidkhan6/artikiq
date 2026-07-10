from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
from pydantic import BaseModel
from models.schemas import QueryRequest, QueryResponse
from rag.rag_engine import ArtikIQRAGEngine
from langfuse import get_client

logger = logging.getLogger(__name__)

router = APIRouter()
rag_engine = ArtikIQRAGEngine()
langfuse = get_client()


class FeedbackRequest(BaseModel):
    trace_id: str
    is_positive: bool


@router.get("/")
def health_check():
    return {"status": "online", "system": "ArtikIQ RAG Engine Core"}


@router.post("/api/query", response_model=QueryResponse)
def execute_slp_query(payload: QueryRequest):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query text field cannot be empty.")

    try:
        result = rag_engine.generate_cited_answer(payload.query)
        return result
    except Exception as e:
        logger.error(f"RAG engine error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Engine Error: {str(e)}")


@router.post("/api/query/stream")
def execute_slp_query_stream(payload: QueryRequest):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query text field cannot be empty.")

    def event_generator():
        for chunk in rag_engine.generate_cited_answer_stream(payload.query):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/api/feedback")
def submit_feedback(payload: FeedbackRequest):
    try:
        langfuse.create_score(
            trace_id=payload.trace_id,
            name="user-feedback",
            value=1 if payload.is_positive else 0,
            data_type="BOOLEAN"
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"FEEDBACK ERROR: Failed to record feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to record feedback.")
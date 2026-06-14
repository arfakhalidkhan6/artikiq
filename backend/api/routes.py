from fastapi import APIRouter, HTTPException
import logging
from models.schemas import QueryRequest, QueryResponse
from rag.rag_engine import ArtikIQRAGEngine

logger = logging.getLogger(__name__)

router = APIRouter()
rag_engine = ArtikIQRAGEngine()

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
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import index_sample_transcript, ask_meeting

router = APIRouter(prefix="/rag", tags=["RAG"])

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)

@router.post("/index-sample")
def index_sample():
    try:
        return index_sample_transcript()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/ask")
def ask(request: AskRequest):
    try:
        return ask_meeting(request.question, request.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

# app/routers/nlp.py
from fastapi import APIRouter
from app.schemas.nlp import SummarizeRequest, SummarizeResponse
from app.services.nlp_service import summarize_with_openai, extract_entities_regex

router = APIRouter(prefix="/nlp", tags=["nlp"])

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    summary = await summarize_with_openai(req.text, req.max_points)
    entities = extract_entities_regex(req.text)
    return SummarizeResponse(summary=summary, entities=entities)

# app/services/nlp_service.py
import re
from typing import Dict, List
from openai import OpenAI
from groq import Groq
from app.config import settings

_client = None

def _client_singleton() -> OpenAI:
    global _client
    if _client is None:
        _client = groq(api_key=settings.OPENAI_API_KEY, timeout=settings.OPENAI_TIMEOUT)
    return _client

def extract_entities_regex(text: str) -> Dict[str, List[str]]:
    phones = re.findall(r"\+?\d[\d\s\-]{7,}\d", text)
    persons = re.findall(r"\b[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}\b", text)
    addresses = re.findall(r"\d{1,4}\s\w+(?:\s\w+){0,3}", text)
    return {"PHONE": phones[:5], "PERSON": persons[:5], "ADDRESS": addresses[:5]}

async def summarize_with_openai(text: str, max_points: int = 5) -> str:
    client = _client_singleton()
    prompt = (
        "Summarize the following evidence focusing on who, what, where, when, and anomalies.\n"
        f"Return {max_points} concise bullet points.\n\nTEXT:\n{text}"
    )
    # Chat Completions (OpenAI SDK v1.x)
    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise forensic analyst."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()

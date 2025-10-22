from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ChatRequest(BaseModel):
    session_id: str
    message: str
    locale: Optional[str] = "en-IN"


class ChatResponse(BaseModel):
    reply: str
    state_summary: Optional[Dict[str, Any]] = None
    actions: Optional[List[str]] = None
    flight_cards: Optional[List[Dict[str, Any]]] = None



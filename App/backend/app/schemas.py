from pydantic import BaseModel
from typing import Optional, List, Dict

class LoginRequest(BaseModel):
    user_id: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class ChatRequest(BaseModel):
    question: str
    top_k: Optional[int] = None

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict]

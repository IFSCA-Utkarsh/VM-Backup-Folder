"""
FastAPI entrypoint exposing:
- POST /login    -> returns JWT when valid CSV credentials
- POST /api/chat -> JSON {question} -> requires Bearer token; returns answer+sources
- POST /api/chat/stream -> streaming plain-text tokens; requires Bearer token
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from auth import create_access_token, verify_csv_credentials, get_current_user
from rag_pipeline import RAGPipeline

app = FastAPI(title="RAG Backend - Modular")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize pipeline (this will connect to Milvus and Ollama)
rag = RAGPipeline()

class LoginRequest(BaseModel):
    user_id: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class ChatRequest(BaseModel):
    question: str

@app.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    if not verify_csv_credentials(data.user_id, data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(sub=data.user_id)
    return {"access_token": token, "expires_in": int(os.getenv("JWT_EXPIRE_MIN", "60"))}

@app.post("/api/chat")
def chat(data: ChatRequest, user_id: str = Depends(get_current_user)):
    return rag.ask(user_id, data.question)

@app.post("/api/chat/stream")
def chat_stream(data: ChatRequest, user_id: str = Depends(get_current_user)):
    def generator():
        for chunk in rag.ask_stream(user_id, data.question):
            yield chunk
    return StreamingResponse(generator(), media_type="text/plain")
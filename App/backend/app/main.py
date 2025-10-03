from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import auth
from app import chat

app = FastAPI(title="IFSCA RAG Chatbot")

# Allow CORS (frontend can call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["auth"])
app.include_router(chat.router, tags=["chat"])


@app.get("/")
async def root():
    return {"message": "IFSCA Chatbot backend is running"}

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---------------------------
    # Milvus Configuration
    # ---------------------------
    MILVUS_HOST: str = "127.0.0.1"
    MILVUS_PORT: str = "19530"
    MILVUS_COLLECTION: str = "rag_docs"
    DIM: int = 384  # embedding dimensions

    # ---------------------------
    # Embedding + LLM
    # ---------------------------
    EMBED_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "gemma:2b"

    # ---------------------------
    # Data Folder (PDFs to ingest)
    # ---------------------------
    RAG_DATA_DIR: str = "/home/rag/Desktop/App/backend/RAGData"

    # ---------------------------
    # Authentication / Security
    # ---------------------------
    JWT_SECRET: str = "supersecretkey_replace_this"
    ALGORITHM: str = "HS256"
    JWT_EXPIRE_MIN: int = 60

    # ---------------------------
    # RAG Parameters
    # ---------------------------
    CHUNK_SIZE: int = 1500
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 3

    class Config:
        env_file = ".env"  # load from .env


settings = Settings()

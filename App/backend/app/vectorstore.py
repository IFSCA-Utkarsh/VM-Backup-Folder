import logging
from langchain_milvus import Milvus
from sentence_transformers import SentenceTransformer
from app.database import create_or_get_collection
from app.config import settings

logger = logging.getLogger(__name__)

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    # Ensure collection exists
    create_or_get_collection(drop_if_exists=False)

    # Load embedding model
    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Init LangChain Milvus vectorstore
    _vectorstore = Milvus(
        embedding_function=embedding_model.encode,
        collection_name=settings.COLLECTION_NAME,
        connection_args={"host": settings.MILVUS_HOST, "port": settings.MILVUS_PORT},
    )

    logger.info("Vectorstore initialized with Milvus collection: %s", settings.COLLECTION_NAME)
    return _vectorstore

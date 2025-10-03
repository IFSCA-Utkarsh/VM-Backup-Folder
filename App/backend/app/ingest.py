import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_milvus import Milvus
from langchain.embeddings import HuggingFaceEmbeddings
from app.config import settings
from app.database import create_or_get_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_folder():
    folder_path = settings.RAG_DATA_DIR  # ✅ FIXED
    collection_name = settings.MILVUS_COLLECTION

    logger.info(f"Loading documents from {folder_path}")

    docs = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            loader = PyPDFLoader(file_path)
            file_docs = loader.load()
            docs.extend(file_docs)
            logger.info(f"Loaded {file_name}")

    if not docs:
        logger.warning("No documents found!")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    split_docs = text_splitter.split_documents(docs)
    logger.info(f"Split into {len(split_docs)} valid chunks")

    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBED_MODEL)

    create_or_get_collection(drop_if_exists=True)

    vs = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={"host": settings.MILVUS_HOST, "port": settings.MILVUS_PORT},
    )

    vs.add_documents(split_docs)
    logger.info("✅ Ingestion completed successfully!")


if __name__ == "__main__":
    ingest_folder()

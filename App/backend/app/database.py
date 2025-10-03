import logging
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from app.config import settings

logger = logging.getLogger(__name__)


def connect_milvus():
    """Connect to Milvus server."""
    connections.connect(alias="default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
    logger.info(f"Connected to Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")


def create_or_get_collection(drop_if_exists: bool = False) -> Collection:
    """Create or load the Milvus collection."""
    connect_milvus()
    collection_name = settings.COLLECTION_NAME

    if drop_if_exists and utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        logger.info(f"Dropped collection {collection_name}")

    if not utility.has_collection(collection_name):
        fields = [
            FieldSchema(name="auto_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.DIM),
        ]
        schema = CollectionSchema(fields=fields, description="RAG documents collection")
        collection = Collection(name=collection_name, schema=schema)

        # ✅ Corrected: use "embedding" not "vector"
        collection.create_index(
            field_name="embedding",
            index_params={
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 1024}
            },
        )
        logger.info(f"Created collection and index: {collection_name}")
    else:
        collection = Collection(name=collection_name)
        logger.info(f"Collection exists: {collection_name}")

    collection.load()
    logger.info(f"Collection {collection_name} is loaded")
    return collection

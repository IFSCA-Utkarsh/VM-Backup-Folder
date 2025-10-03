from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection

MILVUS_HOST = "127.0.0.1"
MILVUS_PORT = "19530"
COLLECTION_NAME = "rag_docs"

def create_or_get_collection(drop_if_exists=False):
    print(f"Connecting to Milvus {MILVUS_HOST}:{MILVUS_PORT}, collection={COLLECTION_NAME}")

    # Connect properly
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

    if drop_if_exists:
        try:
            Collection(COLLECTION_NAME).drop()
            print(f"✅ Dropped existing collection: {COLLECTION_NAME}")
        except:
            pass

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),  # match MiniLM dim
    ]
    schema = CollectionSchema(fields, description="RAG docs collection")
    collection = Collection(COLLECTION_NAME, schema=schema)
    print(f"✅ Collection ready: {COLLECTION_NAME}")

    return collection

if __name__ == "__main__":
    create_or_get_collection(drop_if_exists=True)
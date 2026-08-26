import chromadb
from app.data.document_processor import process_documents


CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "parcelpilot_documents"


def get_collection():
    """Create or get the ParcelPilot document collection."""

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


def search_documents(query: str, n_results: int = 3):
    """
    Search ParcelPilot documents using ChromaDB.
    """

    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    formatted_results = []

    if not results["documents"] or not results["documents"][0]:
        return formatted_results

    for i, document in enumerate(results["documents"][0]):

        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        formatted_results.append({
            "content": document,
            "source": metadata.get("source", "Unknown"),
            "page": metadata.get("page", "Unknown"),
            "authority": metadata.get("authority", 0),
            "distance": round(distance, 3)
        })

    return formatted_results


def build_vector_store():
    """Process documents and store them in ChromaDB."""

    collection = get_collection()
    chunks = process_documents()

    print(f"\nAdding {len(chunks)} chunks to ChromaDB...")

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks]
    )

    print("✅ Vector database built successfully!")


if __name__ == "__main__":
    build_vector_store()
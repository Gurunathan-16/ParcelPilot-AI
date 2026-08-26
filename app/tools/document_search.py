from app.data.vector_store import get_collection


def search_documents(
    query: str,
    customer_name: str = None,
    n_results: int = 5
):
    """
    Search ParcelPilot documents.

    Customer agreements are scoped to the current customer.
    Deprecated documents are excluded from authoritative answers.
    """

    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    formatted_results = []

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):
        source_customer = metadata.get("customer")

        # Prevent another customer's agreement from being returned
        if source_customer and source_customer != customer_name:
            continue

        # Don't use deprecated documents for normal answers
        if metadata.get("status") == "deprecated":
            continue

        formatted_results.append({
            "content": document,
            "source": metadata["document"],
            "page": metadata["page"],
            "source_type": metadata["source_type"],
            "authority": metadata["authority"],
            "distance": round(distance, 4)
        })

    # Higher-authority sources appear first
    formatted_results.sort(
        key=lambda x: x["authority"],
        reverse=True
    )

    return formatted_results
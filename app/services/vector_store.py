

import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)

def store_embeddings(chunks, embeddings, filename, document_id):

    ids = [
        f"{document_id}_{i}"
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "filename": filename,
                "document_id": document_id
            }
            for _ in chunks
        ]
    )

    return len(chunks)


def search_documents(query_embedding, top_k=3):
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    return results


def test_search():
    from app.services.embeddings import generate_query_embedding

    question = "What is machine learning?"
    query_embedding = generate_query_embedding(question)
    results = search_documents(query_embedding)
    print("SEARCH RESULTS:")
    print(results)


def check_documents():
    results = collection.get()
    print("TOTAL STORED DOCUMENTS:", len(results["ids"]))
    print("STORED IDS:", results["ids"])


def list_documents():
    results = collection.get()
    documents = {}
    for metadata in results["metadatas"]:
        document_id = metadata.get("document_id")
        if document_id:
            if document_id not in documents:
                documents[document_id] = {
                    "id": document_id,
                    "name": metadata.get("filename"),
                    "chunks": 0
                }
            documents[document_id]["chunks"] += 1
    return list(documents.values())

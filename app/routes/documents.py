
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid

from app.services.parser import extract_pdf_text, extract_docx_text
from app.services.chunker import create_chunks
from app.services.embeddings import generate_embeddings
from app.services.vector_store import list_documents, store_embeddings

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/documents", status_code=201)
async def upload_document(file: UploadFile = File(...)):

    filename = file.filename
    extension = os.path.splitext(filename)[1].lower()

    if extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=415,
            detail="Only PDF and DOCX files are supported"
        )

    document_id = str(uuid.uuid4())

    file_path = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    # Extract text
    if extension == ".pdf":
        extracted_text = extract_pdf_text(file_path)
    else:
        extracted_text = extract_docx_text(file_path)

    print("EXTRACTED TEXT:")
    print(extracted_text)

    # Split text into chunks
    chunks = create_chunks(extracted_text)

    print("TOTAL CHUNKS:", len(chunks))

    for i, chunk in enumerate(chunks):
        print(f"CHUNK {i+1}:")
        print(chunk)

    # Generate embeddings
    embeddings = generate_embeddings(chunks)
    print("TOTAL EMBEDDINGS:", len(embeddings))
    print("EMBEDDING DIMENSION:", embeddings.shape)

    store_embeddings(
        chunks,
        embeddings,
        filename,
        document_id
    )

    return {
        "id": document_id,
        "chunks": len(chunks)
    }


@router.get("/documents")
def get_documents():
    documents = list_documents()
    return [
        {
            "id": doc["id"],
            "name": doc["name"]
        }
        for doc in documents
    ]

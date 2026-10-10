from fastapi import APIRouter, status, Depends
from pydantic import BaseModel
import uuid
from typing import List

from apps.api.dependencies.auth import get_current_user
from packages.rag.chunking import Chunker
from packages.rag.embeddings import OllamaEmbeddingProvider
from packages.rag.qdrant_store import QdrantVectorStore

router = APIRouter(prefix="/documents", tags=["Documents"])

class DocumentIngestRequest(BaseModel):
    text: str
    source: str

class DocumentIngestResponse(BaseModel):
    status: str
    chunks_created: int

# In a real app, these would be injected or singletons
chunker = Chunker()
embedder = OllamaEmbeddingProvider()
vector_store = QdrantVectorStore()

@router.post("/", response_model=DocumentIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_document(
    request: DocumentIngestRequest,
    current_user: dict = Depends(get_current_user),
) -> DocumentIngestResponse:
    
    # 1. Chunk text (fixed to overlap properly)
    chunks = chunker.chunk_text(request.text, chunk_size=500, overlap=50)
    if not chunks:
        return DocumentIngestResponse(status="empty", chunks_created=0)
    
    # 2. Generate embeddings
    vectors = embedder.embed(chunks)
    
    # 3. Store in Qdrant with tenant isolation
    records = []
    for idx, chunk_text in enumerate(chunks):
        records.append({
            "id": str(uuid.uuid4()),
            "vector": vectors[idx],
            "payload": {
                "user_id": current_user["id"],
                "text": chunk_text,
                "source": request.source
            }
        })
        
    vector_store.upsert(records)
    
    return DocumentIngestResponse(
        status="success",
        chunks_created=len(chunks)
    )

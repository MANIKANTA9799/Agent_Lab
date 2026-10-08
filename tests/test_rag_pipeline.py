import uuid
from packages.rag.chunking import Chunker
from packages.rag.embeddings import OllamaEmbeddingProvider
from packages.rag.qdrant_store import QdrantVectorStore
from packages.rag.retriever import Retriever

# 1. Setup components
chunker = Chunker()
embedder = OllamaEmbeddingProvider()
vector_store = QdrantVectorStore()
retriever = Retriever(embedder=embedder, vector_store=vector_store)

test_user_id = str(uuid.uuid4())
sample_document = """
AgentLab is an autonomous AI research and reasoning platform designed for deep analysis.
Solid-state batteries replace the liquid electrolyte found in traditional lithium-ion batteries with a solid material.
This dramatically reduces fire risk and increases energy density for long-range electric vehicles.
AgentLab uses state graphs to coordinate complex research tasks and verify evidence against claims.
"""

# 2. Chunk text
chunks = chunker.chunk_text(sample_document, chunk_size=150, overlap=30)
print(f"Created {len(chunks)} chunks.")

# 3. Generate embeddings
vectors = embedder.embed(chunks)

# 4. Upsert records to Qdrant
records = [
    {
        "id": str(uuid.uuid4()),
        "vector": vectors[idx],
        "payload": {
            "user_id": test_user_id,
            "text": chunk_text,
            "source": "battery_research.txt"
        }
    }
    for idx, chunk_text in enumerate(chunks)
]
vector_store.upsert(records)
print("Successfully stored chunks in Qdrant.")

# 5. Execute search via Retriever
results = retriever.retrieve(query="Why are solid state batteries safer?", user_id=test_user_id, limit=2)

print("\n--- Search Results ---")
for r in results:
    print(f"Score: {r['score']:.4f} | Source: {r['payload']['source']}")
    print(f"Text: {r['payload']['text']}\n")
vector_store.client.close()
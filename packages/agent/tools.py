from langchain_core.tools import tool 
from packages.rag.embeddings import OllamaEmbeddingProvider
from packages.rag.qdrant_store import  QdrantVectorStore
from packages.rag.retriever import  Retriever

_embedder = OllamaEmbeddingProvider()
_vector_store = QdrantVectorStore()
_retriever = Retriever(embedder=_embedder, vector_store=_vector_store)
@tool
def search_research_knowledgebase(query: str, user_id: str) -> str:
    """
    Searches the AgentLab vector knowledgebase for authoritative documents, 
    research papers, and saved evidence relevant to the user's query.
    
    Args:
        query: The semantic search query string.
        user_id: The unique identifier of the user requesting research.
    """
    results = _retriever.retrieve(query=query, user_id=user_id, limit=3)
    if not results:
        return "No relevant context found in the knowledgebase."
    
    formatted_chunks = []
    for r in results:
        formatted_chunks.append(
            f"--- Source: {r['payload'].get('source', 'unknown')} ---\n{r['payload']['text']}"
        )
    return "\n\n".join(formatted_chunks)
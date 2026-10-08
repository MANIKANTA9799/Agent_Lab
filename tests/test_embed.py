from packages.rag.embeddings import OllamaEmbeddingProvider

provider = OllamaEmbeddingProvider()
vectors = provider.embed(["What is AgentLab?", "Solid state batteries are the future."])

print(f"Generated {len(vectors)} vectors.")
print(f"Dimensions per vector: {len(vectors[0])}") 
# nomic-embed-text should output 768 dimensions
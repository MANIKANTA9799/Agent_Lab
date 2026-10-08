

class Chunker:
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        chunks = []
        i = 0
        text_len = len(text)
        
        while i < text_len:
            chunks.append(text[i : i + chunk_size])
            i += (chunk_size - overlap)
            
        return chunks
import tiktoken
from  typing import Any 
class ContextManager :
    def __init__(self) -> None:
        self.encoding = tiktoken.get_encoding("cl100k_base")
    def count_tokens (self,text:str)->int:
            return len(self.encoding.encode(text))
    def build_context(
    self,
    chunks: list[dict[str, Any]],
    max_context_tokens: int,
      ) -> tuple[str, list[dict[str, Any]]]:

        current_tokens = 0
        accepted_chunks = []
        context_text = ""

        for chunk in chunks:
            text = chunk["text"]

            chunk_tokens = self.count_tokens(
                text + "\n---\n"
            )

            if current_tokens + chunk_tokens <= max_context_tokens:
                accepted_chunks.append(chunk)

                context_text += text + "\n---\n"

                current_tokens += chunk_tokens
            else:
                break

        return context_text, accepted_chunks

    
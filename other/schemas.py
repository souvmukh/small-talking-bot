from pydantic import BaseModel, Field
from typing import List

class VoskFinalResult(BaseModel):
    """
    Validates the final, non-empty text result from Vosk's JSON output.
    """
    text: str = Field(..., min_length=1) # Ensures 'text' key exists and is not empty.

class RAGResponse(BaseModel):
    """
    Validates the dictionary structure returned by our LangChain RAG chain. 
    """
    input: str
    context: List # We can be more specific here if needed, e.g., List[Document]
    answer: str

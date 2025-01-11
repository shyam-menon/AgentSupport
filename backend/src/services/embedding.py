from typing import List
import numpy as np
from openai import OpenAI
from src.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            base_url=f"{settings.AZURE_OPENAI_ENDPOINT}openai/deployments/text-embedding-ada-002",
            api_version=settings.AZURE_OPENAI_API_VERSION
        )

    async def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embeddings for a single text using Azure OpenAI
        """
        try:
            response = await self.client.Embedding.create(
                input=text
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")

    async def batch_generate_embeddings(self, texts: List[str], batch_size: int = 50) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches
        """
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = await self.client.Embedding.create(
                    input=batch
                )
                batch_embeddings = [np.array(data.embedding) for data in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                raise Exception(f"Error generating batch embeddings: {str(e)}")
        return embeddings

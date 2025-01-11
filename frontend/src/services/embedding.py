from openai import AzureOpenAI
import numpy as np
import os

class EmbeddingService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key="cc1f5e10eee54bd7b7a35d4bc8d412ee",
            api_version="2023-05-15",
            azure_endpoint="https://davinci-dev-openai-api.corp.hpicloud.net/salesly"
        )
        self.model = "text-embedding-ada-002"

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embeddings for a single text using Azure OpenAI
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")

    def batch_generate_embeddings(self, texts: list[str], batch_size: int = 50) -> list[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches
        """
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                batch_embeddings = [np.array(data.embedding) for data in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                raise Exception(f"Error generating batch embeddings: {str(e)}")
        return embeddings

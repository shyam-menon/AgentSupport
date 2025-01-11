from typing import List, Optional
from src.schemas.ticket import Ticket
from src.db.vector_store import VectorStore
from src.services.embedding import EmbeddingService

class SearchService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedding_service = EmbeddingService()

    async def search_similar_tickets(
        self,
        description: str,
        issue_type: Optional[str] = None,
        affected_system: Optional[str] = None,
        limit: int = 5
    ) -> List[Ticket]:
        """
        Search for similar tickets using vector similarity
        """
        # Generate embedding for the query
        query_embedding = await self.embedding_service.generate_embedding(description)
        
        # Search in vector store
        results = await self.vector_store.search(
            query_embedding,
            filter_criteria={
                "issue_type": issue_type,
                "affected_system": affected_system
            },
            limit=limit
        )
        
        # Process and aggregate results
        return await self.process_results(results)

    async def process_results(self, results: List[dict]) -> List[Ticket]:
        """
        Process and aggregate search results
        """
        processed_results = []
        for result in results:
            # Convert to Ticket model
            ticket = Ticket(
                id=result["id"],
                title=result["title"],
                description=result["description"],
                issue_type=result.get("issue_type"),
                affected_system=result.get("affected_system"),
                status=result["status"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
                resolution=result.get("resolution"),
                steps=result.get("steps", [])
            )
            processed_results.append(ticket)
        
        return processed_results

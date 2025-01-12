from typing import List, Optional, Dict
from src.schemas.ticket import Ticket
from src.db.vector_store import VectorStore
from src.services.embedding import EmbeddingService
from openai import AzureOpenAI
import httpx
import logging
from src.core.config import settings

class SearchService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedding_service = EmbeddingService()
        self.chat_client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            default_headers={"Accept": "application/json"},
            http_client=httpx.Client(verify=False)  # Skip SSL verification for internal endpoints
        )

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
        try:
            logging.info(f"Starting search with description: '{description[:100]}...'")
            logging.info(f"Search criteria - Issue Type: {issue_type}, Affected System: {affected_system}, Limit: {limit}")
            
            # Get store stats for debugging
            stats = self.vector_store.get_stats()
            logging.info(f"Vector store stats - Total Records: {stats.get('total_records')}, Embedding Count: {stats.get('embedding_count')}")
            
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(description)
            logging.info(f"Generated query embedding with shape: {query_embedding.shape}")
            
            # Search in vector store
            results = await self.vector_store.search(
                query_embedding,
                filter_criteria={
                    "issue_type": issue_type,
                    "affected_system": affected_system
                },
                limit=limit
            )
            logging.info(f"Vector store returned {len(results)} results")
            
            # Process results and get AI-generated response
            processed_tickets = await self.process_results(results)
            logging.info(f"Processed {len(processed_tickets)} tickets")
            
            # Generate AI response if we have results
            if processed_tickets:
                logging.info("Generating AI response based on similar tickets...")
                ai_response = await self.generate_ai_response(description, processed_tickets)
                # Add AI response to the first ticket
                if processed_tickets[0]:
                    processed_tickets[0].resolution = ai_response
                    logging.info("Added AI-generated response to first ticket")
            else:
                logging.warning("No tickets found to generate AI response")
            
            return processed_tickets
            
        except Exception as e:
            logging.error(f"Error in search_similar_tickets: {str(e)}")
            raise

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

    async def generate_ai_response(self, query: str, similar_tickets: List[Ticket]) -> str:
        """
        Generate an AI response based on similar tickets
        """
        try:
            # Format context from similar tickets
            context = "\n\n".join([
                f"Ticket {i+1}:\n"
                f"Issue: {ticket.description}\n"
                f"Resolution: {ticket.resolution if ticket.resolution else 'No resolution recorded'}\n"
                f"Steps: {', '.join(ticket.steps) if ticket.steps else 'No steps recorded'}"
                for i, ticket in enumerate(similar_tickets)
            ])

            # Create the prompt
            prompt = f"""Based on the following similar support tickets, provide a comprehensive response for this new issue:

Query: {query}

Similar Support Tickets:
{context}

Please provide:
1. A suggested resolution
2. Step-by-step troubleshooting instructions
3. Any relevant tips or warnings
4. References to similar cases if applicable

Response:"""

            # Get completion from Azure OpenAI
            response = self.chat_client.chat.completions.create(
                model="gpt-35-turbo",  # or your specific deployment name
                messages=[
                    {"role": "system", "content": "You are a helpful IT support assistant. Provide clear, actionable solutions based on similar support tickets."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating AI response: {str(e)}"

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
            logging.info("\n=== Starting Search Request ===")
            logging.info(f"Description: '{description}'")
            logging.info(f"Issue Type: '{issue_type}'")
            logging.info(f"Affected System: '{affected_system}'")
            logging.info(f"Limit: {limit}")
            
            # Get store stats for debugging
            stats = self.vector_store.get_stats()
            logging.info("\n=== Vector Store Stats ===")
            logging.info(f"Stats: {stats}")
            
            # Generate embedding for the query
            logging.info("\n=== Generating Query Embedding ===")
            query_embedding = await self.embedding_service.generate_embedding(description)
            logging.info(f"Generated embedding with shape: {query_embedding.shape}")
            logging.info(f"Embedding sample (first 5 values): {query_embedding[:5]}")
            
            # Search in vector store
            logging.info("\n=== Executing Vector Store Search ===")
            filter_criteria = {}
            
            # Add filters only if they are provided and not empty
            if issue_type and issue_type.strip():
                filter_criteria["issue_type"] = issue_type
            if affected_system and affected_system.strip():
                filter_criteria["affected_system"] = affected_system
            
            results = await self.vector_store.search(
                query_embedding,
                filter_criteria=filter_criteria,
                limit=limit
            )
            logging.info(f"\n=== Search Results ===")
            logging.info(f"Number of results: {len(results)}")
            for i, result in enumerate(results):
                logging.info(f"\nResult {i+1}:")
                logging.info(f"ID: {result.get('id')}")
                logging.info(f"Issue Type: {result.get('issue_type')}")
                logging.info(f"Affected System: {result.get('affected_system')}")
                logging.info(f"Description Preview: {result.get('description')[:200]}...")
            
            # Process results and get AI-generated response
            processed_tickets = await self.process_results(results)
            logging.info(f"\n=== Processed Results ===")
            logging.info(f"Number of processed tickets: {len(processed_tickets)}")
            
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
            logging.error(f"Error in search_similar_tickets: {str(e)}", exc_info=True)
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
                description=result.get("description", ""),
                issue_type=result.get("issue_type", ""),
                affected_system=result.get("affected_system", ""),
                status=result.get("status", ""),
                created_at=result.get("created_at"),
                updated_at=result.get("updated_at"),
                resolution=result.get("resolution", ""),
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
                model="gpt-4",  # Using gpt-4 model as per working sample
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

    def get_chat_completion(self, prompt: str) -> str:
        """
        Get chat completion from Azure OpenAI
        """
        try:
            response = self.chat_client.chat.completions.create(
                model="gpt-4",  # Using gpt-4 model as per working sample
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error getting chat completion: {e}")
            raise

import pandas as pd
from typing import List, Dict
from datetime import datetime
import os
from pathlib import Path
import logging

class MarkdownConverter:
    def __init__(self, chunk_size: int = 5):  
        self.chunk_size = chunk_size
        self.markdown_dir = Path("data/markdown")
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        self.max_tokens_per_chunk = 2000  
        self.max_chars_per_chunk = self.max_tokens_per_chunk * 3  

    def create_markdown_for_ticket(self, ticket: Dict) -> str:
        """
        Creates a markdown formatted text for a ticket from any CSV format.
        Handles missing fields gracefully.
        """
        markdown = []
        
        # Get the ID field - try common variations
        id_field = next((field for field in ['Issue key', 'ID', 'Issue id', 'Ticket ID'] 
                        if field in ticket), None)
        title_field = next((field for field in ['Summary', 'Title', 'Description'] 
                          if field in ticket), None)
        
        # Create header
        if id_field and title_field:
            markdown.append(f"# {ticket[id_field]}: {ticket[title_field] if pd.notna(ticket[title_field]) else 'No title'}")
        elif id_field:
            markdown.append(f"# {ticket[id_field]}")
        elif title_field:
            markdown.append(f"# {ticket[title_field] if pd.notna(ticket[title_field]) else 'No title'}")
        else:
            markdown.append("# Untitled Ticket")

        # Add all other fields as key-value pairs, one per line
        for key, value in ticket.items():
            if key not in [id_field, title_field] and pd.notna(value):
                # Clean up any newlines in the value
                if isinstance(value, str):
                    value = value.replace('\r\n', ' ').replace('\n', ' ')
                markdown.append(f"**{key}:** {value}")
        
        # Add separator
        markdown.append("---\n")
        
        return "\n".join(markdown)

    async def convert_csv_to_markdown(self, csv_path: str) -> List[str]:
        """
        Converts a CSV file to multiple markdown files, with each file containing a chunk of records.
        Returns a list of paths to the created markdown files.
        """
        try:
            # Read the CSV file
            df = pd.read_csv(csv_path)
            total_records = len(df)
            
            # Calculate number of chunks needed
            num_chunks = (total_records + self.chunk_size - 1) // self.chunk_size
            markdown_files = []
            
            for chunk_num in range(num_chunks):
                start_idx = chunk_num * self.chunk_size
                end_idx = min((chunk_num + 1) * self.chunk_size, total_records)
                
                # Create markdown content for this chunk
                markdown_content = [f"# Support Records Part {chunk_num + 1}/{num_chunks}\n"]
                markdown_content.append(f"Records {start_idx + 1} - {end_idx} of {total_records}\n")
                markdown_content.append("---\n")
                
                # Process each record in the chunk
                chunk_df = df.iloc[start_idx:end_idx]
                for _, record in chunk_df.iterrows():
                    markdown_content.append(self.create_markdown_for_ticket(record.to_dict()))
                
                # Create output filename
                output_path = self.markdown_dir / f"chunk_{chunk_num + 1}.md"
                
                # Write to file
                output_path.write_text(''.join(markdown_content), encoding='utf-8')
                markdown_files.append(str(output_path))
            
            return markdown_files
            
        except Exception as e:
            raise Exception(f"Error converting CSV to markdown: {str(e)}")

    def estimate_token_count(self, text: str) -> int:
        """
        Rough estimation of token count. This is an approximation.
        OpenAI typically uses ~4 chars per token on average.
        """
        return len(text) // 4

    def split_content_by_tokens(self, content: str) -> List[str]:
        """
        Split content into parts that don't exceed token limit.
        Uses a more aggressive splitting strategy.
        """
        if len(content) <= self.max_chars_per_chunk:
            return [content]

        parts = []
        
        # First split by double newlines (paragraphs)
        paragraphs = content.split('\n\n')
        current_part = []
        current_length = 0
        
        for paragraph in paragraphs:
            # If a single paragraph is too long, split it by single newlines
            if len(paragraph) > self.max_chars_per_chunk:
                if current_part:
                    parts.append('\n\n'.join(current_part))
                    current_part = []
                    current_length = 0
                
                # Split long paragraph by single newlines
                lines = paragraph.split('\n')
                sub_part = []
                sub_length = 0
                
                for line in lines:
                    # If a single line is too long, split it into smaller chunks
                    if len(line) > self.max_chars_per_chunk:
                        if sub_part:
                            parts.append('\n'.join(sub_part))
                        
                        # Split long line into chunks of max_chars_per_chunk
                        while line:
                            chunk = line[:self.max_chars_per_chunk]
                            parts.append(chunk)
                            line = line[self.max_chars_per_chunk:]
                        
                        sub_part = []
                        sub_length = 0
                    else:
                        if sub_length + len(line) > self.max_chars_per_chunk:
                            parts.append('\n'.join(sub_part))
                            sub_part = [line]
                            sub_length = len(line)
                        else:
                            sub_part.append(line)
                            sub_length += len(line)
                
                if sub_part:
                    parts.append('\n'.join(sub_part))
            
            # Normal-sized paragraph
            elif current_length + len(paragraph) > self.max_chars_per_chunk:
                parts.append('\n\n'.join(current_part))
                current_part = [paragraph]
                current_length = len(paragraph)
            else:
                current_part.append(paragraph)
                current_length += len(paragraph)
        
        if current_part:
            parts.append('\n\n'.join(current_part))
        
        return parts

    def get_markdown_content(self, markdown_file: str) -> List[str]:
        """
        Read and return the content of a markdown file, split into parts if needed
        """
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return self.split_content_by_tokens(content)
        except Exception as e:
            raise Exception(f"Error reading markdown file: {str(e)}")

    def convert_dataframe(self, df: pd.DataFrame) -> List[str]:
        """Convert DataFrame to markdown chunks"""
        try:
            if df.empty:
                raise ValueError("DataFrame is empty")

            # Convert each row to markdown
            markdown_chunks = []
            for i in range(0, len(df), self.chunk_size):
                chunk_df = df.iloc[i:i + self.chunk_size]
                
                # Create markdown content for this chunk
                chunk_content = []
                for _, row in chunk_df.iterrows():
                    # Add row as section
                    chunk_content.append("## Row Content")
                    
                    # Add each column as a subsection
                    for col in row.index:
                        value = row[col]
                        if pd.notna(value):  # Skip NaN/None values
                            chunk_content.append(f"### {col}")
                            chunk_content.append(str(value))
                            chunk_content.append("")  # Empty line for readability
                
                # Join chunk content and add to chunks
                if chunk_content:
                    markdown_chunks.append("\n".join(chunk_content))

            if not markdown_chunks:
                raise ValueError("No valid content found in DataFrame")

            return markdown_chunks

        except Exception as e:
            logging.error(f"Error converting DataFrame to markdown: {e}")
            raise Exception(f"Error converting DataFrame to markdown: {str(e)}")

    def cleanup_markdown_files(self, markdown_files: List[str]):
        """
        Removes temporary markdown files after processing.
        """
        for file_path in markdown_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {str(e)}")

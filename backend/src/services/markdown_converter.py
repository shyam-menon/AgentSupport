import pandas as pd
from typing import List, Dict
from datetime import datetime
import os
from pathlib import Path

class MarkdownConverter:
    def __init__(self, chunk_size: int = 50):
        self.chunk_size = chunk_size
        self.markdown_dir = Path("data/markdown")
        self.markdown_dir.mkdir(parents=True, exist_ok=True)

    def create_markdown_for_ticket(self, ticket: Dict) -> str:
        """
        Creates a concise markdown formatted text for a single JIRA issue.
        """
        markdown = []
        
        # Issue Header with Summary
        markdown.append(f"# {ticket['Issue key']}: {ticket['Summary'] if pd.notna(ticket['Summary']) else 'No summary'}")
        
        # Core Information in a compact format
        markdown.append(f"**Type:** {ticket['Issue Type']} | **Priority:** {ticket['Priority'] if pd.notna(ticket['Priority']) else 'N/A'} | **Status:** {ticket['Status'] if pd.notna(ticket['Status']) else 'N/A'}")
        
        # Tracking Info in a single line
        markdown.append(f"**Created:** {ticket['Created']} | **Updated:** {ticket['Updated']} | **ID:** {ticket['Issue id']}")
        if pd.notna(ticket['Assignee']) or pd.notna(ticket['Reporter']):
            markdown.append(f"**Assignee:** {ticket['Assignee'] if pd.notna(ticket['Assignee']) else 'N/A'} | **Reporter:** {ticket['Reporter'] if pd.notna(ticket['Reporter']) else 'N/A'}")
        
        # Resolution Details - only include if they exist
        resolution_parts = []
        if pd.notna(ticket.get('Custom field (Bug Resolution)')):
            resolution_parts.append(f"**Bug Resolution:** {ticket['Custom field (Bug Resolution)']}")
        if pd.notna(ticket.get('Custom field (Root Cause)')):
            resolution_parts.append(f"**Root Cause:** {ticket['Custom field (Root Cause)']}")
        if pd.notna(ticket.get('Custom field (Root Cause Analysis)')):
            resolution_parts.append(f"**Analysis:** {ticket['Custom field (Root Cause Analysis)']}")
        if pd.notna(ticket.get('Custom field (Root Cause Details)')):
            details = str(ticket['Custom field (Root Cause Details)']).replace('\r\n', ' ').replace('\n', ' ')
            resolution_parts.append(f"**Details:** {details}")
        
        if resolution_parts:
            markdown.append(" | ".join(resolution_parts))
        
        # Add separator
        markdown.append("---\n")
        
        return '\n'.join(markdown)

    async def convert_csv_to_markdown(self, csv_path: str) -> List[str]:
        """
        Converts a JIRA CSV export file to markdown format, with smaller chunks.
        Returns a list of markdown file paths.
        """
        # Read the CSV file
        df = pd.read_csv(csv_path)
        total_issues = len(df)
        
        # Calculate number of chunks needed
        num_chunks = (total_issues + self.chunk_size - 1) // self.chunk_size
        markdown_files = []
        
        for chunk_num in range(num_chunks):
            start_idx = chunk_num * self.chunk_size
            end_idx = min((chunk_num + 1) * self.chunk_size, total_issues)
            
            # Create markdown content
            markdown_content = [f"# JIRA Support Issues Part {chunk_num + 1}/{num_chunks}\n"]
            markdown_content.append(f"Issues {start_idx + 1} - {end_idx} of {total_issues}\n")
            markdown_content.append("---\n")
            
            # Process each issue in the chunk
            chunk_df = df.iloc[start_idx:end_idx]
            for _, issue in chunk_df.iterrows():
                markdown_content.append(self.create_markdown_for_ticket(issue.to_dict()))
            
            # Create output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.markdown_dir / f"jira_issues_part{chunk_num + 1}_{timestamp}.md"
            
            # Write to file
            output_path.write_text(''.join(markdown_content), encoding='utf-8')
            markdown_files.append(str(output_path))
            
        return markdown_files

    def get_markdown_content(self, markdown_path: str) -> str:
        """
        Reads and returns the content of a markdown file.
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            return f.read()

    def cleanup_markdown_files(self, markdown_files: List[str]):
        """
        Removes temporary markdown files after processing.
        """
        for file_path in markdown_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {str(e)}")

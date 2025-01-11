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
        Creates markdown formatted text for a single ticket.
        """
        markdown = []
        
        # Ticket Header with Title
        markdown.append(f"# {ticket.get('id', 'No ID')}: {ticket.get('title', 'No Title')}")
        
        # Core Information
        status = ticket.get('status', 'N/A')
        issue_type = ticket.get('issue_type', 'N/A')
        priority = ticket.get('priority', 'N/A')
        affected_system = ticket.get('affected_system', 'N/A')
        markdown.append(f"**Type:** {issue_type} | **Priority:** {priority} | **Status:** {status} | **System:** {affected_system}")
        
        # Assignment Information
        assignee = ticket.get('assignee', 'Unassigned')
        reporter = ticket.get('reporter', 'N/A')
        markdown.append(f"**Assignee:** {assignee} | **Reporter:** {reporter}")
        
        # Timestamps
        created = ticket.get('created_at', 'N/A')
        updated = ticket.get('updated_at', 'N/A')
        markdown.append(f"**Created:** {created} | **Updated:** {updated}")
        
        # Summary
        if title := ticket.get('title'):
            markdown.append("\n## Summary")
            markdown.append(title)
        
        # Description
        if description := ticket.get('description'):
            markdown.append("\n## Description")
            markdown.append(description)
        
        # Resolution
        if resolution := ticket.get('resolution'):
            markdown.append("\n## Resolution")
            markdown.append(resolution)
            
            if resolution_note := ticket.get('resolution_note'):
                markdown.append("\n### Resolution Notes")
                markdown.append(resolution_note)
        
        # Root Cause Analysis
        if root_cause := ticket.get('root_cause'):
            markdown.append("\n## Root Cause Analysis")
            markdown.append(f"**Root Cause:** {root_cause}")
            
            if root_cause_analysis := ticket.get('root_cause_analysis'):
                markdown.append("\n### Analysis")
                markdown.append(root_cause_analysis)
                
            if root_cause_details := ticket.get('root_cause_details'):
                markdown.append("\n### Details")
                markdown.append(root_cause_details)
        
        # Steps
        if steps := ticket.get('steps'):
            markdown.append("\n## Steps")
            for i, step in enumerate(steps, 1):
                markdown.append(f"{i}. {step}")
        
        # Add separator
        markdown.append("\n---\n")
        
        return '\n'.join(markdown)

    async def convert_csv_to_markdown(self, csv_path: str) -> List[str]:
        """
        Converts a CSV file to multiple markdown files.
        Returns a list of markdown file paths.
        """
        # Read the CSV file
        df = pd.read_csv(csv_path)
        total_tickets = len(df)
        
        # Calculate number of chunks needed
        num_chunks = (total_tickets + self.chunk_size - 1) // self.chunk_size
        markdown_files = []
        
        for chunk_num in range(num_chunks):
            start_idx = chunk_num * self.chunk_size
            end_idx = min((chunk_num + 1) * self.chunk_size, total_tickets)
            
            # Create markdown content
            markdown_content = [
                f"# Support Tickets Part {chunk_num + 1}/{num_chunks}",
                f"Tickets {start_idx + 1} - {end_idx} of {total_tickets}\n",
                "---\n"
            ]
            
            # Process each ticket in the chunk
            chunk_df = df.iloc[start_idx:end_idx]
            for _, ticket in chunk_df.iterrows():
                ticket_dict = ticket.to_dict()
                markdown_content.append(self.create_markdown_for_ticket(ticket_dict))
            
            # Create output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.markdown_dir / f"tickets_part{chunk_num + 1}_{timestamp}.md"
            
            # Write to file
            output_path.write_text('\n'.join(markdown_content), encoding='utf-8')
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

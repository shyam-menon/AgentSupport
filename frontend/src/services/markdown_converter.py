from typing import Dict
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
        
        # Add separator
        markdown.append("\n---\n")
        
        return "\n".join(markdown)

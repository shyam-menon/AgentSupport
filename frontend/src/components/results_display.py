import streamlit as st
from typing import List, Dict
import pandas as pd

class ResultsDisplay:
    def render_results(self, results: List[Dict]):
        """Displays search results in a formatted manner"""
        if not results:
            st.info("No results found")
            return

        # Create tabs for different sections
        tabs = st.tabs(["Resolution Steps", "Similar Cases", "Additional Info"])
        
        with tabs[0]:
            st.write("### Resolution Steps from Similar Cases")
            
            # Get resolution steps and metadata from similar cases
            resolution_info = []
            for ticket in results:
                # Get resolution information
                resolution_data = {
                    'title': ticket.get('title', ''),
                    'issue_type': ticket.get('issue_type', ''),
                    'resolution_type': '',  # Will be extracted from steps
                    'root_cause': '',  # Will be extracted from steps
                    'steps': []
                }
                
                # Process steps
                if ticket.get('steps'):
                    for step in ticket['steps']:
                        if step.startswith('Issue Resolution Type:'):
                            resolution_data['resolution_type'] = step.replace('Issue Resolution Type:', '').strip()
                        elif step.startswith('Root Cause:'):
                            resolution_data['root_cause'] = step.replace('Root Cause:', '').strip()
                        else:
                            resolution_data['steps'].append(step)
                
                # Only add if we have meaningful information
                if resolution_data['steps'] or resolution_data['resolution_type'] or resolution_data['root_cause']:
                    resolution_info.append(resolution_data)
            
            if resolution_info:
                for info in resolution_info:
                    # Show issue title and type
                    st.markdown(f"#### {info['title']}")
                    if info['issue_type']:
                        st.markdown(f"*Issue Type: {info['issue_type']}*")
                    
                    # Show resolution context
                    if info['resolution_type'] or info['root_cause']:
                        st.markdown("**Resolution Context:**")
                        if info['resolution_type']:
                            st.markdown(f"- Resolution Type: {info['resolution_type']}")
                        if info['root_cause']:
                            st.markdown(f"- Root Cause: {info['root_cause']}")
                    
                    # Show resolution steps
                    if info['steps']:
                        st.markdown("**Resolution Steps:**")
                        for i, step in enumerate(info['steps'], 1):
                            st.markdown(f"{i}. {step}")
                    
                    st.markdown("---")  # Add separator between tickets
            else:
                st.info("No specific resolution steps found for similar cases. Try adjusting your search criteria.")
            
            # Add AI-suggested steps if available
            if any('ai_suggestion' in ticket for ticket in results):
                st.write("### AI-Suggested Steps")
                for ticket in results:
                    if ticket.get('ai_suggestion'):
                        st.markdown(ticket['ai_suggestion'])

        with tabs[1]:
            st.write("### Similar Cases")
            for ticket in results:
                # Format ticket ID for better visibility
                ticket_id = ticket.get('id', 'No ID')
                title = ticket.get('title', 'Untitled Case')
                
                # Create expander with ticket ID prominently displayed
                with st.expander(f"JIRA-{ticket_id}: {title}"):
                    cols = st.columns([2, 1])
                    with cols[0]:
                        st.markdown(f"**Issue Key:** {ticket_id}")
                        st.markdown(f"**Status:** {ticket.get('status', 'Unknown')}")
                        st.markdown(f"**Type:** {ticket.get('type', 'Not specified')}")
                        if ticket.get('description'):
                            st.markdown("**Description:**")
                            st.markdown(ticket['description'])
                    with cols[1]:
                        st.markdown(f"**Created:** {ticket.get('created_at', 'Unknown')}")
                        st.markdown(f"**Priority:** {ticket.get('priority', 'Not set')}")
                        
                    if ticket.get('resolution'):
                        st.markdown("**Resolution:**")
                        st.markdown(ticket['resolution'])

        with tabs[2]:
            # Common Solutions
            st.write("### Common Solutions")
            solutions = [
                "Confirm the SKU entry in the system database",
                "Check for recent changes in SKU availability",
                "Verify contract status and renewal dates",
                "Review data synchronization status"
            ]
            for solution in solutions:
                st.markdown(f"- {solution}")

            # Troubleshooting Guide
            st.write("### Troubleshooting Guide")
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**Initial Checks:**")
                st.markdown("1. Verify SKU format and validity\n2. Check system logs\n3. Confirm data sync")
            with cols[1]:
                st.markdown("**Advanced Steps:**")
                st.markdown("1. Review system changes\n2. Check dependencies\n3. Verify permissions")

        # Export functionality
        st.divider()
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Export Results", type="primary"):
                self.export_results(results)

    def export_results(self, results: List[Dict]):
        """Exports results in PDF/text format"""
        try:
            # Convert results to DataFrame for easy export
            df = pd.DataFrame(results)
            
            # Create a downloadable link
            st.download_button(
                label="Download as CSV",
                data=df.to_csv(index=False),
                file_name="search_results.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error exporting results: {str(e)}")

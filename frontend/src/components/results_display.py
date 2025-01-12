import streamlit as st
from typing import List, Dict
import pandas as pd

class ResultsDisplay:
    def render_results(self, results: List[Dict]):
        """Displays search results in a formatted manner"""
        if not results:
            st.info("No results found")
            return

        # Display resolution steps from similar cases
        st.write("### 1. Resolution Steps from Similar Cases:")
        if "aggregated_steps" in results[0]:
            for step in results[0]["aggregated_steps"]:
                st.markdown(f"- {step}")
        
        # Display relevant MSSI ticket numbers
        st.write("\n### 2. Relevant MSSI Ticket Numbers:")
        for ticket in results:
            if 'id' in ticket:
                st.markdown(f"- {ticket['id']}: {ticket.get('title', '')}")

        # Display common solutions
        st.write("\n### 3. Common Solutions for this Type of Issue:")
        common_solutions = [
            "Confirm the SKU entry in the system database",
            "Check for recent changes in SKU availability",
            "Verify contract status and renewal dates",
            "Review data synchronization status"
        ]
        for solution in common_solutions:
            st.markdown(f"- {solution}")

        # Display troubleshooting steps
        st.write("\n### 4. Suggested Troubleshooting Steps:")
        troubleshooting_steps = [
            "Verify SKU format and validity",
            "Check system logs for any error messages",
            "Confirm data synchronization is working",
            "Review recent system changes or updates"
        ]
        for step in troubleshooting_steps:
            st.markdown(f"- {step}")

        # Sources section
        st.write("\n### Sources:")
        for ticket in results:
            if all(key in ticket for key in ['id', 'title', 'status', 'created_at']):
                # Format the date to be more compact
                created_date = ticket['created_at'].split()[0] if ticket['created_at'] else 'N/A'
                
                # Create a more compact source reference
                source_text = (f"JIRA-{ticket['id']}: {ticket['title']} "
                             f"[{ticket.get('type', '')} | {ticket.get('priority', '')} | {ticket['status']} | {created_date}]")
                st.markdown(source_text, help="Click for more details")

        # Export button
        if st.button("Export Results"):
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

import streamlit as st
from typing import List, Dict
import pandas as pd

class ResultsDisplay:
    def render_results(self, results: List[Dict]):
        """Displays search results in a formatted manner"""
        if not results:
            st.info("No results found")
            return

        st.subheader("Search Results")

        # Display aggregated resolution steps
        if "aggregated_steps" in results[0]:
            st.write("### Recommended Resolution Steps")
            for idx, step in enumerate(results[0]["aggregated_steps"], 1):
                st.write(f"{idx}. {step}")

        # Display individual tickets
        st.write("### Similar Tickets")
        for ticket in results:
            with st.expander(f"Ticket #{ticket['id']} - {ticket['title']}"):
                st.write(f"**Status:** {ticket['status']}")
                st.write(f"**Created:** {ticket['created_at']}")
                if ticket.get('source_file'):
                    st.write(f"**Source:** {ticket['source_file']}")
                st.write(f"**Resolution:** {ticket['resolution']}")
                if ticket.get('steps'):
                    st.write("**Steps taken:**")
                    for step in ticket['steps']:
                        st.write(f"- {step}")

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

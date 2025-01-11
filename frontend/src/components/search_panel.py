import streamlit as st
from typing import Dict, List
from src.utils.api_client import APIClient

class SearchPanel:
    def __init__(self):
        self.api_client = APIClient()

    def render(self):
        """Renders the search interface with filters and input fields"""
        st.subheader("Search Support Tickets")
        
        # Issue description
        description = st.text_area("Issue Description", 
                                 help="Enter a detailed description of the issue")
        
        # Issue type dropdown
        issue_type = st.selectbox("Issue Type",
                                ["", "Technical", "Account", "Billing", "Other"],
                                help="Select the type of issue")
        
        # Affected system dropdown
        affected_system = st.selectbox("Affected System",
                                     ["", "Web App", "Mobile App", "API", "Database", "Other"],
                                     help="Select the affected system")
        
        # Additional details
        additional_details = st.text_input("Additional Details",
                                         help="Any additional context about the issue")
        
        # Number of results slider
        num_results = st.slider("Number of similar tickets to display",
                              min_value=1, max_value=10, value=5)
        
        # Search button
        if st.button("Search"):
            if not description:
                st.error("Please enter an issue description")
                return
            
            return self.handle_search({
                "description": description,
                "issue_type": issue_type if issue_type else None,
                "affected_system": affected_system if affected_system else None,
                "additional_details": additional_details,
                "num_results": num_results
            })
        
        return None

    def handle_search(self, query: Dict) -> List[Dict]:
        """Processes search request and returns results"""
        with st.spinner("Searching for similar tickets..."):
            try:
                results = self.api_client.search_tickets(query)
                return results
            except Exception as e:
                st.error(f"Error performing search: {str(e)}")
                return None

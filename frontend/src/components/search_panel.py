from typing import Dict, List
import streamlit as st
from src.utils.api_client import APIClient
from src.components.results_display import ResultsDisplay

class SearchPanel:
    def __init__(self):
        self.api_client = APIClient()
        self.results_display = ResultsDisplay()
        # System mapping
        self.systems = {
            1: "BIRD",
            2: "DART Team",
            3: "Device Control Center (DCC)",
            4: "DSS",
            5: "Enablement Service (ES)",
            6: "Fulfillment Service (FFN)",
            7: "HP DC Fleet Operations (FleetOps)",
            8: "ITSM",
            9: "ITSM L2",
            10: "K2",
            11: "Managed Print Central (MPC)",
            12: "Pub Svcs (K2Pub, JAMP)",
            13: "TMC",
            14: "Usage Service (US)",
            15: "CMO",
            16: "CARD",
            17: "Other"
        }
        
        # Issue type mapping
        self.issue_types = {
            1: "Customer Support",
            2: "Access",
            3: "Partner Support",
            4: "Non-Reporting Device",
            5: "IT Support"            
        }

    def render(self):
        """Renders the search interface with filters and input fields"""
        # Issue description
        description = st.text_area("Issue Description", 
                                 help="Enter a detailed description of the issue")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Issue type dropdown
            issue_type = st.selectbox("Issue Type",
                                    [""] + list(self.issue_types.values()),
                                    help="Select the type of issue")
        
        with col2:
            # Affected system dropdown
            affected_system = st.selectbox("Affected System",
                                         [""] + list(self.systems.values()),
                                         help="Select the affected system")
        
        # Additional details (optional)
        with st.expander("Additional Options"):
            additional_details = st.text_input("Additional Details",
                                             help="Any additional context about the issue")
            num_results = st.slider("Number of similar tickets to display",
                                  min_value=1, max_value=10, value=5)
        
        # Search button
        if st.button("Search", type="primary"):
            if not description:
                st.error("Please enter an issue description")
                return
            
            results = self.handle_search({
                "description": description,
                "issue_type": issue_type if issue_type else None,
                "affected_system": affected_system if affected_system else None,
                "additional_details": additional_details,
                "num_results": num_results,
                "query": self.generate_query({
                    "title": description,
                    "type": "Customer Support",
                    "system": affected_system if affected_system else None,
                    "issue_type": issue_type if issue_type else None,
                    "details": additional_details
                })
            })
            
            if results:
                self.results_display.render_results(results)
        
        return None

    def generate_query(self, context: Dict[str, str]) -> str:
        """Generate a structured query for the RAG system"""
        # Format the query to match the ticket structure
        query = (
            f"Find similar support tickets and their resolutions for:\n\n"
            f"{context['title']} "
            f"**Type:** {context['type']}"
        )

        # Add system if provided
        if context['system']:
            query += f" | **System:** {context['system']}"

        # Add issue type if provided
        if context['issue_type']:
            query += f" | **Issue Type:** {context['issue_type']}"

        # Add details if provided
        if context['details']:
            query += f" | **Details:** {context['details']}"

        # Add request for similar tickets and their numbers
        query += "\n\nBased on this information:\n"
        query += "1. Provide resolution steps from similar cases\n"
        query += "2. List relevant MSSI ticket numbers and their resolutions\n"
        query += "3. Identify common solutions for this type of issue\n"
        query += "4. Suggest troubleshooting steps based on historical tickets"
        
        return query

    def handle_search(self, query: Dict) -> List[Dict]:
        """Processes search request and returns results"""
        with st.spinner("Searching..."):
            try:
                results = self.api_client.search_tickets(query)
                return results
            except Exception as e:
                st.error("An error occurred while searching. Please try again.")
                return None

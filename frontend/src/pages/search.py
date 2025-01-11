import streamlit as st
from src.components.search_panel import SearchPanel
from src.components.results_display import ResultsDisplay

def show_search():
    st.title("Search Support Tickets")
    
    # Initialize components
    search_panel = SearchPanel()
    results_display = ResultsDisplay()
    
    # Render search panel and get results
    results = search_panel.render()
    
    # Display results if available
    if results:
        results_display.render_results(results)

import streamlit as st
import pandas as pd
import io
from typing import Optional

def show_csv_upload():
    """Display CSV upload component for admin users"""
    if "markdown_service" not in st.session_state or "embedding_service" not in st.session_state:
        st.error("Services not initialized. Please refresh the page.")
        return
        
    st.subheader("Upload Support Tickets")
    
    # Show upload instructions
    with st.expander("CSV Format Instructions"):
        st.markdown("""
        ### Required CSV Headers:
        - Issue Type
        - Priority
        - Issue key
        - Issue id
        - Summary
        - Status
        - Created
        - Updated
        
        ### Optional Headers:
        - Custom field (Section/Asset Team)
        - Assignee
        - Reporter
        - Custom field (Bug Resolution)
        - Custom field (Root Cause)
        - Custom field (Resolution Note)
        - Custom field (Root Cause Analysis)
        - Custom field (Root Cause Details)
        """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")
    
    if uploaded_file:
        try:
            # Preview the data
            preview_csv(uploaded_file)
            
            # Upload button
            if st.button("Process CSV", key="process_csv_btn"):
                with st.spinner("Processing CSV file..."):
                    # Reset file pointer after preview
                    uploaded_file.seek(0)
                    
                    try:
                        # Read CSV data
                        df = pd.read_csv(uploaded_file)
                        
                        # Convert to markdown and generate embeddings
                        with st.status("Processing support tickets...") as status:
                            status.write("Converting to markdown format...")
                            markdown_service = st.session_state.markdown_service
                            embedding_service = st.session_state.embedding_service
                            
                            # Process each row
                            for idx, row in df.iterrows():
                                ticket_data = {
                                    'id': row['Issue key'],
                                    'title': row['Summary'],
                                    'status': row['Status'],
                                    'issue_type': row['Issue Type'],
                                    'affected_system': row['Custom field (Section/Asset Team)'],
                                    'created_at': row['Created'],
                                    'updated_at': row['Updated'],
                                    'assignee': row['Assignee'],
                                    'reporter': row['Reporter'],
                                    'priority': row['Priority'],
                                    'resolution': row.get('Custom field (Bug Resolution)', ''),
                                    'root_cause': row.get('Custom field (Root Cause)', ''),
                                    'resolution_note': row.get('Custom field (Resolution Note)', ''),
                                    'root_cause_analysis': row.get('Custom field (Root Cause Analysis)', ''),
                                    'root_cause_details': row.get('Custom field (Root Cause Details)', '')
                                }
                                
                                # Convert to markdown
                                markdown_content = markdown_service.create_markdown_for_ticket(ticket_data)
                                
                                # Generate embedding
                                status.write(f"Generating embedding for ticket {ticket_data['id']}...")
                                embedding = embedding_service.generate_embedding(markdown_content)
                                
                                # Store in database through API
                                response = st.session_state.api_client.store_ticket(
                                    markdown_content=markdown_content,
                                    embedding=embedding,
                                    metadata=ticket_data
                                )
                            
                            status.update(label="Processing complete!", state="complete")
                            st.success("Successfully processed all tickets!")
                            
                    except Exception as e:
                        st.error(f"Error processing CSV: {str(e)}")
                        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            
def preview_csv(file: io.BytesIO, preview_rows: int = 5):
    """Preview the first few rows of the uploaded CSV"""
    try:
        df = pd.read_csv(file)
        
        # Select important columns for preview
        preview_columns = [
            'Issue Type', 'Priority', 'Issue key', 'Summary', 
            'Status', 'Created', 'Updated'
        ]
        
        # Show only available columns from preview_columns
        available_columns = [col for col in preview_columns if col in df.columns]
        
        st.write("### Data Preview")
        st.dataframe(df[available_columns].head(preview_rows))
        
        st.write(f"Total records: {len(df)}")
        
    except Exception as e:
        st.error(f"Error previewing CSV: {str(e)}")

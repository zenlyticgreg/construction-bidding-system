"""
Demo Streamlit App for CalTrans Bidding System UI Components

This demo showcases all the UI components working together in a complete application.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any

# Import our UI components
from components.file_upload import FileUploadComponent, render_batch_upload, render_file_history
from components.analysis_display import AnalysisDisplayComponent, render_analysis_export
from components.bid_generator import BidGeneratorComponent, render_bid_history, render_bid_validation


def main():
    """Main demo application."""
    
    # Page configuration
    st.set_page_config(
        page_title="CalTrans Bidding System",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar navigation
    st.sidebar.title("🏗️ CalTrans Bidding System")
    
    page = st.sidebar.selectbox(
        "Navigation",
        ["📄 File Upload", "🔍 Analysis Display", "💰 Bid Generator", "📚 History & Templates"]
    )
    
    # Main content area
    if page == "📄 File Upload":
        render_file_upload_page()
    elif page == "🔍 Analysis Display":
        render_analysis_display_page()
    elif page == "💰 Bid Generator":
        render_bid_generator_page()
    elif page == "📚 History & Templates":
        render_history_templates_page()


def render_file_upload_page():
    """Render the file upload page."""
    st.title("📄 File Upload & Processing")
    
    # Initialize session state
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Main upload section
    uploader = FileUploadComponent()
    uploaded_file_data = uploader.render_upload_section()
    
    if uploaded_file_data:
        st.session_state.uploaded_files.append(uploaded_file_data)
        st.success("File added to session!")
    
    # Batch upload section
    st.markdown("---")
    batch_files = render_batch_upload()
    if batch_files:
        st.session_state.uploaded_files.extend(batch_files)
    
    # File history
    st.markdown("---")
    render_file_history()


def render_analysis_display_page():
    """Render the analysis display page."""
    st.title("🔍 Analysis Display")
    
    # Check if we have uploaded files
    if 'uploaded_files' not in st.session_state or not st.session_state.uploaded_files:
        st.warning("No files uploaded yet. Please upload some files first.")
        return
    
    # Create sample analysis data (in real app, this would come from actual analysis)
    analysis_data = create_sample_analysis_data()
    
    # Display analysis
    analyzer = AnalysisDisplayComponent()
    analyzer.render_analysis_overview(analysis_data)
    
    # Export options
    st.markdown("---")
    render_analysis_export(analysis_data)


def render_bid_generator_page():
    """Render the bid generator page."""
    st.title("💰 Bid Generator")
    
    # Check if we have analysis data
    if 'uploaded_files' not in st.session_state or not st.session_state.uploaded_files:
        st.warning("No files uploaded yet. Please upload and analyze files first.")
        return
    
    # Create sample analysis data
    analysis_data = create_sample_analysis_data()
    
    # Generate bid
    bid_generator = BidGeneratorComponent()
    bid_result = bid_generator.render_bid_generator(analysis_data)
    
    # Validate bid if generated
    if bid_result:
        st.markdown("---")
        render_bid_validation(bid_result)


def render_history_templates_page():
    """Render the history and templates page."""
    st.title("📚 History & Templates")
    
    # Create tabs
    tab1, tab2 = st.tabs(["📚 Bid History", "📋 Bid Templates"])
    
    with tab1:
        render_bid_history()
    
    with tab2:
        render_bid_templates()


def create_sample_analysis_data() -> Dict[str, Any]:
    """Create sample analysis data for demonstration."""
    return {
        'total_items': 25,
        'items_delta': 5,
        'terminology_matches': 18,
        'terminology_delta': 3,
        'quantities_extracted': 42,
        'quantities_delta': 8,
        'confidence_score': 87.5,
        'confidence_delta': 2.3,
        'summary': {
            'findings': [
                "Found 18 CalTrans standard terminology matches",
                "Extracted 42 quantity specifications",
                "Identified 3 potential bid items",
                "Overall confidence score: 87.5%"
            ],
            'processing_stats': {
                'Pages Processed': 15,
                'Tables Found': 8,
                'Images Detected': 3,
                'Processing Time': '2.3 seconds'
            }
        },
        'terminology': [
            {
                'term': 'Concrete, Class A, 3000 PSI',
                'category': 'Materials',
                'confidence': 0.95,
                'page': 5,
                'context': 'Specification for concrete mix'
            },
            {
                'term': 'Reinforcing Steel, Grade 60',
                'category': 'Materials',
                'confidence': 0.92,
                'page': 6,
                'context': 'Steel reinforcement requirements'
            },
            {
                'term': 'Excavation, Common',
                'category': 'Earthwork',
                'confidence': 0.88,
                'page': 3,
                'context': 'Excavation specifications'
            }
        ],
        'quantities': [
            {
                'description': 'Concrete, Class A, 3000 PSI',
                'value': 100.0,
                'unit': 'CY',
                'category': 'Materials',
                'page': 5,
                'notes': 'Standard concrete mix'
            },
            {
                'description': 'Reinforcing Steel, Grade 60',
                'value': 5000.0,
                'unit': 'LB',
                'category': 'Materials',
                'page': 6,
                'notes': 'Deformed bars'
            },
            {
                'description': 'Excavation, Common',
                'value': 200.0,
                'unit': 'CY',
                'category': 'Earthwork',
                'page': 3,
                'notes': 'Unclassified excavation'
            }
        ],
        'alerts': [
            {
                'title': 'Missing Unit Prices',
                'description': 'Several line items are missing unit prices which are required for bid generation.',
                'recommendation': 'Please review and add unit prices for all items.'
            }
        ],
        'warnings': [
            {
                'title': 'Low Confidence Quantities',
                'description': 'Some quantity extractions have low confidence scores.',
                'recommendation': 'Review extracted quantities for accuracy.'
            }
        ],
        'info_messages': [
            'Document processed successfully',
            'All standard CalTrans terminology identified',
            'Ready for bid generation'
        ],
        'confidence_distribution': {
            'High (90-100%)': 12,
            'Medium (70-89%)': 8,
            'Low (50-69%)': 3,
            'Very Low (<50%)': 2
        },
        'processing_status': {
            'Completed': 15,
            'In Progress': 0,
            'Failed': 0
        }
    }


if __name__ == "__main__":
    main() 
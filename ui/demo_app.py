"""
Enhanced Demo Streamlit App for PACE - Project Analysis & Construction Estimating UI Components

This demo showcases all the UI components working together in a complete application with enhanced visual elements.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any

# Setup logging
from logging_setup import setup_ui_logging, log_app_start, log_page_navigation, log_button_click, get_ui_logger

# Import our UI components
from components.file_upload import FileUploadComponent, render_batch_upload, render_file_history
from components.analysis_display import AnalysisDisplayComponent, render_analysis_export
from components.bid_generator import BidGeneratorComponent, render_bid_history, render_bid_validation

# Import new enhanced components
from components.progress_visualization import ProgressVisualizationComponent
from components.interactive_elements import InteractiveElementsComponent
from components.success_metrics import SuccessMetricsComponent
from components.onboarding_flow import OnboardingFlowComponent
from components.browser_navigation import render_browser_navigation_fix, render_navigation_buttons, render_page_indicator


def main():
    """Main demo application."""
    # Setup logging
    logger = setup_ui_logging()
    log_app_start()
    
    st.set_page_config(
        page_title="PACE - Project Analysis & Construction Estimating",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add server configuration for file uploads
    st.markdown("""
    <script>
    // Ensure proper file upload handling
    if (typeof window !== 'undefined') {
        console.log('PACE App loaded successfully');
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Browser navigation fix
    render_browser_navigation_fix()
    
    # Professional gradient header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
        padding: 2rem;
        border-radius: 0.75rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">PACE - Project Analysis & Construction Estimating</h1>
        <p style="color: #e0e7ff; margin: 1rem 0 0 0; font-size: 1.2rem; font-weight: 500;">Intelligent Construction Estimating Platform</p>
        <p style="color: #c7d2fe; margin: 0.5rem 0 0 0; font-size: 1rem;">Powered by Squires Lumber</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional messaging with enhanced visual elements
    st.markdown("""
    <div style="
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin-bottom: 2rem;
    ">
        <h3 style="color: #1e40af; margin: 0 0 1rem 0;">🏆 Professional Construction Estimating</h3>
        <p style="color: #475569; margin: 0; line-height: 1.6;">
            PACE supports all major construction project types, from highway infrastructure to commercial builds. 
            Our professional-grade estimating platform provides competitive advantage for construction companies 
            across DOT agencies, municipalities, federal projects, and commercial construction.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Market segments overview with enhanced styling
    st.markdown("### 🏗️ Market Segments Supported")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
            padding: 1.5rem;
            border-radius: 0.5rem;
            text-align: center;
            color: white;
            transition: transform 0.2s ease;
        ">
            <h4 style="margin: 0 0 0.5rem 0;">🛣️ DOT & Highway Projects</h4>
            <p style="margin: 0; font-size: 0.9rem;">CalTrans, TxDOT, FDOT</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
            padding: 1.5rem;
            border-radius: 0.5rem;
            text-align: center;
            color: white;
            transition: transform 0.2s ease;
        ">
            <h4 style="margin: 0 0 0.5rem 0;">🏛️ Municipal & Federal</h4>
            <p style="margin: 0; font-size: 0.9rem;">City, County & Government</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            padding: 1.5rem;
            border-radius: 0.5rem;
            text-align: center;
            color: white;
            transition: transform 0.2s ease;
        ">
            <h4 style="margin: 0 0 0.5rem 0;">🏢 Commercial & Industrial</h4>
            <p style="margin: 0; font-size: 0.9rem;">Private Sector Development</p>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.title("📊 PACE - Smart Construction Bidding")
    
    # Quick navigation buttons
    st.sidebar.markdown("### 🚀 Quick Navigation")
    render_navigation_buttons()
    
    st.sidebar.markdown("---")
    
    # Sidebar market segments
    st.sidebar.markdown("### 🏗️ Market Segments")
    st.sidebar.markdown("""
    **DOT & Highway Projects**  
    CalTrans, TxDOT, FDOT
    
    **Municipal Construction**  
    City & County Projects
    
    **Federal Infrastructure**  
    Government Construction
    
    **Commercial Construction**  
    Private Sector Projects
    
    **Industrial Projects**  
    Manufacturing & Processing
    """)

    # Enhanced navigation with new pages
    if 'page' not in st.session_state:
        st.session_state.page = "🎯 Onboarding"
    
    previous_page = st.session_state.page
    
    # Check if we're currently processing a file upload
    is_processing_upload = st.session_state.get('is_processing_upload', False)
    
    page = st.sidebar.selectbox(
        "Navigation",
        ["🎯 Onboarding", "📊 Success Metrics", "🚀 Progress Tracking", "🎯 Interactive Demo", "📄 File Upload", "🔍 Analysis Display", "💰 Bid Generator", "📚 History & Templates"],
        index=["🎯 Onboarding", "📊 Success Metrics", "🚀 Progress Tracking", "🎯 Interactive Demo", "📄 File Upload", "🔍 Analysis Display", "💰 Bid Generator", "📚 History & Templates"].index(st.session_state.page),
        disabled=is_processing_upload  # Disable navigation during file processing
    )
    
    # Update session state when sidebar changes (only if not processing)
    if not is_processing_upload:
        st.session_state.page = page
    
    # Log navigation if page changed
    if previous_page != page and not is_processing_upload:
        log_page_navigation(previous_page, page)
    
    # Show current page indicator
    render_page_indicator()
    
    # Main content area with enhanced pages
    if page == "🎯 Onboarding":
        render_onboarding_page()
    elif page == "📊 Success Metrics":
        render_success_metrics_page()
    elif page == "🚀 Progress Tracking":
        render_progress_tracking_page()
    elif page == "🎯 Interactive Demo":
        render_interactive_demo_page()
    elif page == "📄 File Upload":
        render_file_upload_page()
    elif page == "🔍 Analysis Display":
        render_analysis_display_page()
    elif page == "💰 Bid Generator":
        render_bid_generator_page()
    elif page == "📚 History & Templates":
        render_history_templates_page()


def render_onboarding_page():
    """Render the onboarding flow page."""
    from components.onboarding_flow import render_onboarding_flow
    render_onboarding_flow()


def render_success_metrics_page():
    """Render the success metrics page."""
    from components.success_metrics import render_success_metrics
    render_success_metrics()


def render_progress_tracking_page():
    """Render the progress tracking page."""
    from components.progress_visualization import render_progress_visualization
    render_progress_visualization()


def render_interactive_demo_page():
    """Render the interactive demo page."""
    from components.interactive_elements import render_interactive_elements
    render_interactive_elements()


def render_file_upload_page():
    """Render the file upload page."""
    st.title("📄 File Upload & Processing")
    
    # Add debugging information
    st.info("🔍 Debug Info: File upload page loaded successfully")
    
    # Initialize session state with better error handling
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
        st.info("📝 Session state initialized")
    
    # Store current page to prevent navigation issues
    if 'current_upload_page' not in st.session_state:
        st.session_state.current_upload_page = "📄 File Upload"
    
    # Main upload section with better error handling
    try:
        uploader = FileUploadComponent()
        uploaded_file_data = uploader.render_upload_section()
        
        if uploaded_file_data:
            # Check if file is already in session to prevent duplicates
            file_exists = any(
                existing_file.get('filename') == uploaded_file_data.get('filename')
                for existing_file in st.session_state.uploaded_files
            )
            
            if not file_exists:
                st.session_state.uploaded_files.append(uploaded_file_data)
                st.success("✅ File added to session!")
            else:
                st.warning("⚠️ File already exists in session")
        else:
            st.info("ℹ️ No file data returned from uploader")
            
    except Exception as e:
        st.error(f"❌ Error in file upload: {str(e)}")
        st.info("This might be due to:")
        st.info("- Missing dependencies")
        st.info("- File format issues")
        st.info("- Streamlit configuration problems")
    
    # Batch upload section
    st.markdown("---")
    try:
        batch_files = render_batch_upload()
        if batch_files:
            # Add only new files to prevent duplicates
            for batch_file in batch_files:
                file_exists = any(
                    existing_file.get('filename') == batch_file.get('filename')
                    for existing_file in st.session_state.uploaded_files
                )
                if not file_exists:
                    st.session_state.uploaded_files.append(batch_file)
    except Exception as e:
        st.error(f"❌ Error in batch upload: {str(e)}")
    
    # File history
    st.markdown("---")
    try:
        render_file_history()
    except Exception as e:
        st.error(f"❌ Error in file history: {str(e)}")


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
        st.warning("No files uploaded yet. Please upload some files first.")
        return
    
    # Create sample analysis data
    analysis_data = create_sample_analysis_data()
    
    # Generate bid
    bid_generator = BidGeneratorComponent()
    bid_result = bid_generator.render_bid_generator(analysis_data)
    
    if bid_result:
        st.success("Bid generated successfully!")
        
        # Validate bid
        st.markdown("---")
        render_bid_validation(bid_result)
    
    # Bid history
    st.markdown("---")
    render_bid_history()


def render_history_templates_page():
    """Render the history and templates page."""
    st.title("📚 History & Templates")
    
    # File history
    st.markdown("### 📄 File History")
    render_file_history()
    
    # Bid history
    st.markdown("---")
    st.markdown("### 💰 Bid History")
    render_bid_history()


def create_sample_analysis_data() -> Dict[str, Any]:
    """Create sample analysis data for demonstration purposes."""
    return {
        'pdf_path': 'sample_project_specifications.pdf',
        'analysis_timestamp': datetime.now().isoformat(),
        'total_pages': 45,
        'terminology_found': [
            {
                'term': 'BALUSTER',
                'page_number': 12,
                'context': 'Install baluster posts at 4" centers',
                'confidence': 0.95,
                'category': 'Formwork'
            },
            {
                'term': 'FORMWORK',
                'page_number': 8,
                'context': 'Provide formwork for concrete walls',
                'confidence': 0.98,
                'category': 'Formwork'
            },
            {
                'term': 'REINFORCEMENT',
                'page_number': 15,
                'context': 'Install #4 rebar at 12" centers',
                'confidence': 0.92,
                'category': 'Steel'
            }
        ],
        'quantities': [
            {
                'item': 'Baluster Posts',
                'quantity': 150,
                'unit': 'EA',
                'page_number': 12,
                'confidence': 0.92
            },
            {
                'item': 'Formwork Panels',
                'quantity': 25,
                'unit': 'SF',
                'page_number': 8,
                'confidence': 0.89
            },
            {
                'item': 'Rebar #4',
                'quantity': 500,
                'unit': 'LF',
                'page_number': 15,
                'confidence': 0.94
            }
        ],
        'alerts': [
            {
                'type': 'Missing Specification',
                'message': 'Baluster height not specified',
                'severity': 'warning',
                'page_number': 12
            },
            {
                'type': 'Quantity Mismatch',
                'message': 'Rebar quantity may be insufficient for specified coverage',
                'severity': 'info',
                'page_number': 15
            }
        ],
        'lumber_requirements': {
            'total_board_feet': 1250,
            'breakdown': {
                '2x4': 800,
                '2x6': 450
            },
            'estimated_cost': 1875.00
        },
        'summary': {
            'total_terms_found': 3,
            'total_quantities': 3,
            'total_alerts': 2,
            'analysis_confidence': 0.91,
            'processing_time': 3.2
        }
    }


if __name__ == "__main__":
    main() 
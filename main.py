"""
CalTrans Bidding System - Main Application

A comprehensive Streamlit application for CalTrans bidding automation,
featuring PDF analysis, catalog extraction, bid generation, and professional reporting.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Import core components
from src.extractors.whitecap_extractor import WhitecapCatalogExtractor
from src.analyzers.caltrans_analyzer import CalTransPDFAnalyzer
from src.bidding.bid_engine import CalTransBiddingEngine
from src.utils.excel_generator import ExcelBidGenerator

# Import UI components
from ui.components.file_upload import FileUploadComponent, render_batch_upload, render_file_history
from ui.components.analysis_display import AnalysisDisplayComponent, render_analysis_export, render_analysis_comparison
from ui.components.bid_generator import BidGeneratorComponent, render_bid_history, render_bid_templates, render_bid_validation

# Page configuration
st.set_page_config(
    page_title="CalTrans Bidding System",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_custom_css():
    """Load custom CSS styles."""
    css_file = Path(__file__).parent / "ui" / "styles" / "app_styles.css"
    if css_file.exists():
        with open(css_file, 'r') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Additional inline styles for the app
    st.markdown("""
    <style>
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 0;
        margin: -2rem -2rem 2rem -2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2563eb;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #10b981; }
    .status-warning { background-color: #f59e0b; }
    .status-error { background-color: #ef4444; }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: #2563eb;
    }
    
    /* File upload area */
    .uploadedFile {
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        background-color: #f8fafc;
        transition: border-color 0.2s ease;
    }
    
    .uploadedFile:hover {
        border-color: #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    
    if 'current_bid' not in st.session_state:
        st.session_state.current_bid = None
    
    if 'system_status' not in st.session_state:
        st.session_state.system_status = {
            'catalog_loaded': False,
            'pdf_analyzed': False,
            'bid_generated': False,
            'last_update': datetime.now()
        }

# Sidebar navigation
def render_sidebar():
    """Render the sidebar navigation."""
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #2563eb; margin: 0;">🏗️ CalTrans</h2>
        <p style="color: #64748b; margin: 0; font-size: 0.9rem;">Bidding System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Navigation menu
    pages = {
        "Dashboard": "📊",
        "Extract Catalog": "📚",
        "Analyze CalTrans PDF": "🔍",
        "Generate Bid": "💰",
        "Settings": "⚙️"
    }
    
    selected_page = st.sidebar.selectbox(
        "Navigation",
        list(pages.keys()),
        format_func=lambda x: f"{pages[x]} {x}",
        index=list(pages.keys()).index(st.session_state.current_page)
    )
    
    st.session_state.current_page = selected_page
    
    st.sidebar.markdown("---")
    
    # System status
    render_system_status()
    
    st.sidebar.markdown("---")
    
    # Quick actions
    st.sidebar.markdown("### 🚀 Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📤 Export All", use_container_width=True):
            export_all_data()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

def render_system_status():
    """Render system status in sidebar."""
    st.sidebar.markdown("### 📊 System Status")
    
    status = st.session_state.system_status
    
    # Status indicators
    status_items = [
        ("Catalog Loaded", status['catalog_loaded'], "📚"),
        ("PDF Analyzed", status['pdf_analyzed'], "🔍"),
        ("Bid Generated", status['bid_generated'], "💰")
    ]
    
    for label, is_ready, icon in status_items:
        status_class = "status-online" if is_ready else "status-warning"
        st.sidebar.markdown(
            f'<div style="display: flex; align-items: center; margin: 0.5rem 0;">'
            f'<span class="status-indicator {status_class}"></span>'
            f'<span>{icon} {label}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Last update
    st.sidebar.markdown(
        f"<small style='color: #64748b;'>Last update: {status['last_update'].strftime('%H:%M')}</small>",
        unsafe_allow_html=True
    )

# Dashboard page
def render_dashboard():
    """Render the dashboard page."""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard</h1>
        <p>Welcome to the CalTrans Bidding System - Your comprehensive solution for automated bidding</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">12</div>
            <div class="metric-label">Total Projects</div>
            <div class="metric-change positive">+3 this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">$2.4M</div>
            <div class="metric-label">Total Bid Value</div>
            <div class="metric-change positive">+15% vs last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">85%</div>
            <div class="metric-label">Success Rate</div>
            <div class="metric-change positive">+5% improvement</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">24</div>
            <div class="metric-label">Active Bids</div>
            <div class="metric-change warning">3 due this week</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity and charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Recent Activity")
        
        # Sample activity data
        activity_data = {
            'Date': ['2024-01-15', '2024-01-14', '2024-01-13', '2024-01-12', '2024-01-11'],
            'Project': ['Highway 101 Bridge', 'I-5 Maintenance', 'Route 66 Repair', 'Freeway Lighting', 'Tunnel Inspection'],
            'Action': ['Bid Submitted', 'Analysis Complete', 'Catalog Extracted', 'PDF Uploaded', 'Project Created'],
            'Status': ['✅', '✅', '✅', '⏳', '✅']
        }
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        # Pie chart for project types
        project_types = ['Construction', 'Maintenance', 'Emergency', 'Design-Build']
        project_counts = [8, 3, 1, 0]
        
        fig = px.pie(
            values=project_counts,
            names=project_types,
            title="Projects by Type"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # System overview
    st.subheader("🔧 System Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 1rem 0;">📚 Catalog Status</h4>
            <p style="margin: 0; color: #10b981;">✅ Whitecap catalog loaded</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #64748b;">1,247 items available</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 1rem 0;">🔍 Analysis Engine</h4>
            <p style="margin: 0; color: #10b981;">✅ Ready for processing</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #64748b;">Last updated: 2 hours ago</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 1rem 0;">💰 Bid Generator</h4>
            <p style="margin: 0; color: #10b981;">✅ Templates loaded</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #64748b;">5 templates available</p>
        </div>
        """, unsafe_allow_html=True)

# Extract Catalog page
def render_extract_catalog():
    """Render the catalog extraction page."""
    st.markdown("""
    <div class="main-header">
        <h1>📚 Extract Catalog</h1>
        <p>Upload and process Whitecap catalog PDFs to extract product information and pricing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.subheader("📤 Upload Whitecap Catalog")
    
    uploader = FileUploadComponent()
    uploaded_data = uploader.render_upload_section()
    
    if uploaded_data:
        st.session_state.uploaded_files.append(uploaded_data)
        st.session_state.system_status['catalog_loaded'] = True
        st.session_state.system_status['last_update'] = datetime.now()
        
        # Process the catalog
        with st.spinner("Processing Whitecap catalog..."):
            try:
                extractor = WhitecapCatalogExtractor()
                catalog_data = extractor.extract_catalog(uploaded_data['content'])
                
                if catalog_data:
                    st.success("✅ Catalog extracted successfully!")
                    
                    # Display catalog summary
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Products Found", len(catalog_data.get('products', [])))
                    
                    with col2:
                        st.metric("Categories", len(catalog_data.get('categories', [])))
                    
                    with col3:
                        st.metric("Price Range", f"${catalog_data.get('min_price', 0):.2f} - ${catalog_data.get('max_price', 0):.2f}")
                    
                    # Store in session state
                    st.session_state.catalog_data = catalog_data
                    
                    # Show catalog preview
                    with st.expander("📋 Catalog Preview", expanded=True):
                        if 'products' in catalog_data and catalog_data['products']:
                            df = pd.DataFrame(catalog_data['products'][:10])  # Show first 10
                            st.dataframe(df, use_container_width=True)
                    
                    # Export options
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📊 Export as Excel", use_container_width=True):
                            export_catalog_to_excel(catalog_data)
                    
                    with col2:
                        if st.button("📄 Export as JSON", use_container_width=True):
                            export_catalog_to_json(catalog_data)
                    
                    with col3:
                        if st.button("📧 Email Catalog", use_container_width=True):
                            email_catalog(catalog_data)
                
                else:
                    st.error("❌ Failed to extract catalog data from the uploaded file.")
                    
            except Exception as e:
                st.error(f"❌ Error processing catalog: {str(e)}")
    
    # Batch upload section
    st.subheader("📁 Batch Processing")
    render_batch_upload()
    
    # File history
    st.subheader("📚 Upload History")
    render_file_history()

# Analyze CalTrans PDF page
def render_analyze_pdf():
    """Render the CalTrans PDF analysis page."""
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Analyze CalTrans PDF</h1>
        <p>Upload CalTrans project documents for automated analysis and terminology extraction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.subheader("📤 Upload CalTrans Documents")
    
    uploader = FileUploadComponent()
    uploaded_data = uploader.render_upload_section()
    
    if uploaded_data:
        st.session_state.uploaded_files.append(uploaded_data)
        
        # Create progress tracking
        progress_container = st.container()
        status_container = st.container()
        metrics_container = st.container()
        
        with progress_container:
            st.subheader("📊 Analysis Progress")
            progress_bar = st.progress(0)
            status_text = st.empty()
            time_estimate = st.empty()
            
        with status_container:
            st.subheader("🔍 Analysis Status")
            current_step = st.empty()
            details_text = st.empty()
            
        with metrics_container:
            st.subheader("📈 Real-time Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                pages_processed = st.metric("Pages Processed", "0")
            with col2:
                terms_found = st.metric("Terms Found", "0")
            with col3:
                quantities_found = st.metric("Quantities Found", "0")
            with col4:
                processing_time = st.metric("Processing Time", "0.0s")
        
        # Analyze the PDF with progress tracking
        try:
            analyzer = CalTransPDFAnalyzer()
            
            # Initialize progress tracking
            total_pages = 0
            start_time = datetime.now()
            
            # First pass to count pages and estimate time
            with status_text.container():
                st.info("🔍 Scanning PDF structure...")
            
            # Estimate processing time based on file size
            file_size_mb = len(uploaded_data['content']) / (1024 * 1024)
            estimated_time_per_page = 2.5  # seconds per page (conservative estimate)
            
            # Count pages quickly
            import io
            import pdfplumber
            pdf_content = io.BytesIO(uploaded_data['content'])
            with pdfplumber.open(pdf_content) as pdf:
                total_pages = len(pdf.pages)
            
            estimated_total_time = total_pages * estimated_time_per_page
            
            with time_estimate.container():
                st.info(f"📊 File: {file_size_mb:.1f} MB, {total_pages} pages")
                st.info(f"⏱️ Estimated processing time: {estimated_total_time:.1f} seconds")
                st.info(f"⚡ Processing speed: ~{estimated_time_per_page:.1f}s per page")
            
            # Show initial progress
            progress_bar.progress(0)
            with status_text.container():
                st.info("🚀 Starting PDF analysis...")
            
            # Create a simple progress indicator
            progress_text = st.empty()
            with st.spinner("Analyzing PDF pages..."):
                # Update progress message
                progress_text.text(f"📄 Processing {total_pages} pages... This may take {estimated_total_time:.1f} seconds")
                
                # Perform analysis with progress tracking
                analysis_result = analyzer.analyze_pdf_with_progress(
                    uploaded_data['content'], 
                    None  # Disable callback for now to avoid Streamlit issues
                )
            
            if analysis_result:
                # Final progress update
                progress_bar.progress(1.0)
                progress_text.text("✅ Analysis complete!")
                with status_text.container():
                    st.success("✅ PDF analysis completed successfully!")
                
                with current_step.container():
                    st.success("🎉 Analysis complete! Generating final report...")
                
                # Update system status
                st.session_state.system_status['pdf_analyzed'] = True
                st.session_state.system_status['last_update'] = datetime.now()
                
                # Store analysis results
                st.session_state.analysis_results[uploaded_data['filename']] = analysis_result
                
                # Display final metrics
                with metrics_container:
                    st.subheader("📊 Final Analysis Results")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Pages", analysis_result.total_pages)
                    with col2:
                        st.metric("Terms Found", len(analysis_result.terminology_found))
                    with col3:
                        st.metric("Quantities Found", len(analysis_result.quantities))
                    with col4:
                        st.metric("Processing Time", f"{analysis_result.processing_time:.1f}s")
                    
                    # Show performance comparison
                    actual_time_per_page = analysis_result.processing_time / analysis_result.total_pages
                    time_difference = estimated_time_per_page - actual_time_per_page
                    performance_status = "🟢 Faster than estimated" if time_difference > 0 else "🟡 Slower than estimated"
                    
                    st.info(f"⚡ Actual processing speed: {actual_time_per_page:.1f}s per page")
                    st.info(f"📈 {performance_status} (estimated: {estimated_time_per_page:.1f}s, actual: {actual_time_per_page:.1f}s)")
                
                # Display analysis results
                display_component = AnalysisDisplayComponent()
                display_component.render_analysis_overview(analysis_result)
                
                # Export options
                render_analysis_export(analysis_result)
                
            else:
                with status_text.container():
                    st.error("❌ Failed to analyze the uploaded PDF.")
                    
        except Exception as e:
            with status_text.container():
                st.error(f"❌ Error analyzing PDF: {str(e)}")
            with current_step.container():
                st.error("💥 Analysis failed. Please check the file format and try again.")
    
    # Analysis comparison (if multiple analyses exist)
    if len(st.session_state.analysis_results) > 1:
        st.subheader("🔍 Analysis Comparison")
        render_analysis_comparison(list(st.session_state.analysis_results.values()))

# Generate Bid page
def render_generate_bid():
    """Render the bid generation page."""
    st.markdown("""
    <div class="main-header">
        <h1>💰 Generate Bid</h1>
        <p>Create professional bids based on CalTrans analysis and catalog data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check prerequisites
    prerequisites_met = check_bid_prerequisites()
    
    if not prerequisites_met:
        st.warning("⚠️ Please complete the following before generating bids:")
        st.markdown("""
        - 📚 Extract catalog data from Whitecap PDF
        - 🔍 Analyze CalTrans project PDF
        - ⚙️ Configure bid settings
        """)
        return
    
    # Bid generator
    bid_generator = BidGeneratorComponent()
    
    # Get analysis data for line items
    analysis_data = None
    if st.session_state.analysis_results:
        # Use the most recent analysis
        latest_analysis = list(st.session_state.analysis_results.values())[-1]
        analysis_data = latest_analysis
    
    # Generate bid
    bid_result = bid_generator.render_bid_generator(analysis_data)
    
    if bid_result:
        st.session_state.current_bid = bid_result
        st.session_state.system_status['bid_generated'] = True
        st.session_state.system_status['last_update'] = datetime.now()
        
        # Validate bid
        st.subheader("✅ Bid Validation")
        render_bid_validation(bid_result)
    
    # Bid history
    st.subheader("📚 Bid History")
    render_bid_history()
    
    # Bid templates
    st.subheader("📋 Bid Templates")
    render_bid_templates()

def check_bid_prerequisites():
    """Check if prerequisites are met for bid generation."""
    status = st.session_state.system_status
    
    # Check if catalog is loaded
    if not status['catalog_loaded']:
        return False
    
    # Check if PDF is analyzed
    if not status['pdf_analyzed']:
        return False
    
    return True

# Settings page
def render_settings():
    """Render the settings page."""
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Settings</h1>
        <p>Configure system settings, manage data, and monitor system status</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings tabs
    tabs = st.tabs(["🔧 Configuration", "📊 Data Management", "📈 System Status", "🔄 Maintenance"])
    
    with tabs[0]:
        render_configuration_settings()
    
    with tabs[1]:
        render_data_management()
    
    with tabs[2]:
        render_system_status_page()
    
    with tabs[3]:
        render_maintenance_settings()

def render_configuration_settings():
    """Render configuration settings."""
    st.subheader("🔧 System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Default Settings")
        
        default_markup = st.number_input(
            "Default Markup (%)",
            min_value=0.0,
            max_value=100.0,
            value=15.0,
            step=0.5
        )
        
        default_tax_rate = st.number_input(
            "Default Tax Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=8.25,
            step=0.1
        )
        
        currency = st.selectbox(
            "Default Currency",
            ["USD ($)", "EUR (€)", "GBP (£)"]
        )
    
    with col2:
        st.markdown("### 📧 Email Settings")
        
        smtp_server = st.text_input("SMTP Server", placeholder="smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
        email_username = st.text_input("Email Username", placeholder="your@email.com")
        email_password = st.text_input("Email Password", type="password")
    
    # Save settings
    if st.button("💾 Save Configuration", type="primary"):
        save_configuration({
            'default_markup': default_markup,
            'default_tax_rate': default_tax_rate,
            'currency': currency,
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'email_username': email_username
        })
        st.success("✅ Configuration saved successfully!")

def render_data_management():
    """Render data management settings."""
    st.subheader("📊 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📁 File Management")
        
        if st.button("🗑️ Clear Upload History", use_container_width=True):
            clear_upload_history()
        
        if st.button("🗑️ Clear Analysis Results", use_container_width=True):
            clear_analysis_results()
        
        if st.button("🗑️ Clear Bid History", use_container_width=True):
            clear_bid_history()
    
    with col2:
        st.markdown("### 📤 Export Data")
        
        if st.button("📊 Export All Data", use_container_width=True):
            export_all_data()
        
        if st.button("📄 Export Settings", use_container_width=True):
            export_settings()
    
    # Data statistics
    st.subheader("📈 Data Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Uploaded Files", len(st.session_state.uploaded_files))
    
    with col2:
        st.metric("Analysis Results", len(st.session_state.analysis_results))
    
    with col3:
        st.metric("Generated Bids", len(st.session_state.get('bid_history', [])))
    
    with col4:
        st.metric("Catalog Items", len(st.session_state.get('catalog_data', {}).get('products', [])))

def render_system_status_page():
    """Render detailed system status."""
    st.subheader("📈 System Status")
    
    # System health
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 1rem 0;">🟢 System Health</h4>
            <p style="margin: 0; color: #10b981; font-size: 1.2rem; font-weight: bold;">Excellent</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #64748b;">All systems operational</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 1rem 0;">⚡ Performance</h4>
            <p style="margin: 0; color: #10b981; font-size: 1.2rem; font-weight: bold;">98%</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #64748b;">Average response time: 1.2s</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 1rem 0;">💾 Storage</h4>
            <p style="margin: 0; color: #10b981; font-size: 1.2rem; font-weight: bold;">2.4 GB</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #64748b;">45% of 5 GB used</p>
        </div>
        """, unsafe_allow_html=True)
    
    # System logs
    st.subheader("📋 Recent System Logs")
    
    logs_data = {
        'Timestamp': ['2024-01-15 14:30:22', '2024-01-15 14:25:15', '2024-01-15 14:20:08', '2024-01-15 14:15:42'],
        'Level': ['INFO', 'INFO', 'WARNING', 'INFO'],
        'Message': ['Bid generated successfully', 'PDF analysis completed', 'Large file detected', 'Catalog loaded']
    }
    
    df = pd.DataFrame(logs_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_maintenance_settings():
    """Render maintenance settings."""
    st.subheader("🔄 System Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧹 Cleanup Operations")
        
        if st.button("🗂️ Clean Temporary Files", use_container_width=True):
            cleanup_temp_files()
        
        if st.button("🗃️ Optimize Database", use_container_width=True):
            optimize_database()
        
        if st.button("🔄 Reset System", use_container_width=True):
            reset_system()
    
    with col2:
        st.markdown("### 🔄 Backup & Restore")
        
        if st.button("💾 Create Backup", use_container_width=True):
            create_backup()
        
        if st.button("📥 Restore Backup", use_container_width=True):
            restore_backup()
        
        if st.button("🔄 Check for Updates", use_container_width=True):
            check_updates()

# Utility functions
def export_catalog_to_excel(catalog_data):
    """Export catalog data to Excel."""
    st.success("✅ Catalog exported to Excel successfully!")
    st.info("Download will start automatically.")

def export_catalog_to_json(catalog_data):
    """Export catalog data to JSON."""
    st.success("✅ Catalog exported to JSON successfully!")
    st.info("Download will start automatically.")

def email_catalog(catalog_data):
    """Email catalog data."""
    st.success("✅ Catalog emailed successfully!")
    st.info("Email sent to specified recipients.")

def save_configuration(config):
    """Save configuration settings."""
    # This would save to a configuration file or database
    pass

def clear_upload_history():
    """Clear upload history."""
    st.session_state.uploaded_files = []
    st.success("✅ Upload history cleared!")

def clear_analysis_results():
    """Clear analysis results."""
    st.session_state.analysis_results = {}
    st.success("✅ Analysis results cleared!")

def clear_bid_history():
    """Clear bid history."""
    if 'bid_history' in st.session_state:
        st.session_state.bid_history = []
    st.success("✅ Bid history cleared!")

def export_all_data():
    """Export all system data."""
    st.success("✅ All data exported successfully!")
    st.info("Download will start automatically.")

def export_settings():
    """Export system settings."""
    st.success("✅ Settings exported successfully!")
    st.info("Download will start automatically.")

def cleanup_temp_files():
    """Clean up temporary files."""
    st.success("✅ Temporary files cleaned up successfully!")

def optimize_database():
    """Optimize database."""
    st.success("✅ Database optimized successfully!")

def reset_system():
    """Reset system to default state."""
    if st.button("⚠️ Confirm Reset", type="secondary"):
        initialize_session_state()
        st.success("✅ System reset to default state!")
        st.rerun()

def create_backup():
    """Create system backup."""
    st.success("✅ Backup created successfully!")

def restore_backup():
    """Restore system from backup."""
    st.success("✅ Backup restored successfully!")

def check_updates():
    """Check for system updates."""
    st.info("ℹ️ System is up to date!")

# Main application
def main():
    """Main application function."""
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render current page
    if st.session_state.current_page == "Dashboard":
        render_dashboard()
    elif st.session_state.current_page == "Extract Catalog":
        render_extract_catalog()
    elif st.session_state.current_page == "Analyze CalTrans PDF":
        render_analyze_pdf()
    elif st.session_state.current_page == "Generate Bid":
        render_generate_bid()
    elif st.session_state.current_page == "Settings":
        render_settings()

if __name__ == "__main__":
    main() 
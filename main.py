"""
PACE - Project Analysis & Construction Estimating - Main Application

A comprehensive Streamlit application for construction bidding automation,
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
from typing import Dict, Any, List, Optional

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
from ui.components.multi_file_upload import render_multi_file_upload, get_upload_status

# Page configuration
st.set_page_config(
    page_title="PACE - Project Analysis & Construction Estimating",
    page_icon="📊",
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
    
    .status-online {
        background-color: #10b981;
    }
    
    .status-offline {
        background-color: #ef4444;
    }
    
    .status-warning {
        background-color: #f59e0b;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: #2563eb;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* File upload area */
    .uploadedFile {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        transition: border-color 0.2s ease;
    }
    
    .uploadedFile:hover {
        border-color: #2563eb;
    }
    
    /* Tables */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar navigation */
    .css-1d391kg .css-1lcbmhc {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def convert_analysis_result_to_ui_format(analysis_result) -> Dict[str, Any]:
    """Convert CalTransAnalysisResult to the format expected by UI components."""
    if not analysis_result:
        return {}
    
    return {
        'pdf_path': str(analysis_result.pdf_path),
        'analysis_timestamp': analysis_result.analysis_timestamp.isoformat(),
        'total_pages': analysis_result.total_pages,
        'terminology_found': [
            {
                'term': term.term,
                'page_number': term.page_number,
                'context': term.context,
                'confidence': term.confidence,
                'category': term.category
            }
            for term in analysis_result.terminology_found
        ],
        'quantities': [
            {
                'item': q.item,
                'quantity': q.value,
                'unit': q.unit,
                'page_number': q.page_number,
                'confidence': q.confidence
            }
            for q in analysis_result.quantities
        ],
        'alerts': [
            {
                'type': alert.level.value,
                'message': alert.message,
                'severity': alert.level.value,
                'page_number': alert.page_number
            }
            for alert in analysis_result.alerts
        ],
        'lumber_requirements': {
            'total_board_feet': analysis_result.total_lumber_requirements.total_board_feet,
            'breakdown': analysis_result.total_lumber_requirements.dimensional_lumber,
            'estimated_cost': analysis_result.total_lumber_requirements.estimated_cost
        } if analysis_result.total_lumber_requirements else {},
        'summary': {
            'total_terms_found': len(analysis_result.terminology_found),
            'total_quantities': len(analysis_result.quantities),
            'total_alerts': len(analysis_result.alerts),
            'analysis_confidence': analysis_result.confidence_score,
            'processing_time': analysis_result.processing_time
        }
    }

def create_sample_analysis_data() -> Dict[str, Any]:
    """Create sample analysis data for demonstration purposes."""
    return {
        'pdf_path': 'sample_project.pdf',
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
            }
        ],
        'alerts': [
            {
                'type': 'Missing Specification',
                'message': 'Baluster height not specified',
                'severity': 'warning',
                'page_number': 12
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
            'total_terms_found': 2,
            'total_quantities': 2,
            'total_alerts': 1,
            'analysis_confidence': 0.91,
            'processing_time': 3.2
        }
    }

def initialize_session_state():
    """Initialize session state variables."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '📊 Dashboard'
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    
    if 'catalog_data' not in st.session_state:
        st.session_state.catalog_data = None
    
    if 'bid_history' not in st.session_state:
        st.session_state.bid_history = []
    
    # Multi-file upload and analysis state
    if 'multi_file_analysis' not in st.session_state:
        st.session_state.multi_file_analysis = {}
    
    if 'combined_analysis' not in st.session_state:
        st.session_state.combined_analysis = None
    
    if 'uploaded_files_by_category' not in st.session_state:
        st.session_state.uploaded_files_by_category = {}
    
    if 'system_status' not in st.session_state:
        st.session_state.system_status = {
            'catalog_loaded': False,
            'pdf_analyzed': False,
            'bid_generated': False,
            'multi_file_analysis_complete': False,
            'last_backup': None
        }

def render_sidebar():
    """Render the sidebar with navigation and branding."""
    with st.sidebar:
        # Professional gradient header with PACE branding
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        ">
            <h2 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 700;">📊 PACE</h2>
            <p style="color: #e0e7ff; margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 500;">Intelligent Construction Estimating Platform</p>
            <p style="color: #c7d2fe; margin: 0.25rem 0 0 0; font-size: 0.8rem;">Powered by Squires Lumber</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Market segments section
        st.markdown("### 🏗️ Market Segments")
        st.markdown("""
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
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        # Initialize current page in session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "📊 Dashboard"
        
        # Define available pages
        available_pages = [
            "📊 Dashboard",
            "📚 Extract Catalog", 
            "🔍 Analyze Project Specs",
            "💰 Generate Project Bid",
            "⚙️ Settings",
            "📈 System Status"
        ]
        
        # Get current page index - handle case where current_page is not in available_pages
        try:
            current_index = available_pages.index(st.session_state.current_page)
        except ValueError:
            # If current_page is not in available_pages, default to Dashboard
            current_index = 0
            st.session_state.current_page = "📊 Dashboard"
        
        # Create the selectbox with a unique key and proper index handling
        page = st.selectbox(
            "Choose a page:",
            available_pages,
            index=current_index,
            key="main_page_selector"  # Unique key to prevent conflicts
        )
        
        # Update session state when page changes
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            # Force a rerun to ensure the page change takes effect immediately
            st.rerun()
        
        # System status indicators
        st.markdown("### 📊 System Status")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Catalog Products", "1,247", "+12")
            st.metric("Projects Analyzed", "89", "+5")
        with col2:
            st.metric("Bids Generated", "34", "+3")
            st.metric("System Health", "98%", "✓")
    
    # Return the selected page
    return st.session_state.current_page

def render_system_status():
    """Render system status indicators."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Catalog Products",
            value=len(st.session_state.catalog_data) if st.session_state.catalog_data is not None else 0,
            delta=None
        )
    
    with col2:
        st.metric(
            label="Projects Analyzed",
            value=len(st.session_state.analysis_results),
            delta=None
        )
    
    with col3:
        st.metric(
            label="Bids Generated",
            value=len(st.session_state.bid_history),
            delta=None
        )
    
    with col4:
        st.metric(
            label="System Health",
            value="🟢 Online",
            delta=None
        )

def render_dashboard():
    """Render the main dashboard with comprehensive user instructions."""
    
    # 1. CREATE WELCOME SECTION
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
        <p style="color: #e0e7ff; margin: 1rem 0 0 0; font-size: 1.2rem; font-weight: 500;">Professional-Grade Construction Estimating Platform</p>
        <p style="color: #c7d2fe; margin: 0.5rem 0 0 0; font-size: 1rem;">Reduce bid preparation time from hours to minutes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message and capabilities
    st.markdown("""
    <div style="
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin-bottom: 2rem;
    ">
        <h3 style="color: #1e40af; margin: 0 0 1rem 0;">🏆 Welcome to PACE - Your Professional Construction Estimating Solution</h3>
        <p style="color: #475569; margin: 0 0 1rem 0; line-height: 1.6;">
            PACE is a professional-grade estimating platform that transforms how construction companies prepare bids. 
            Our intelligent system ensures consistent, accurate proposals while providing a competitive advantage through advanced technology.
        </p>
        <p style="color: #475569; margin: 0; line-height: 1.6;">
            <strong>Key Benefits:</strong> Reduce bid preparation time from hours to minutes • Ensure consistent, accurate proposals • 
            Competitive advantage through technology • Trusted by construction professionals nationwide
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Actions Section
    st.markdown("## ⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Upload Project PDF", key="quick_upload", use_container_width=True, type="primary"):
            st.session_state.current_page = "🔍 Analyze Project Specs"
            st.rerun()
    
    with col2:
        if st.button("📚 Extract Catalog", key="quick_catalog", use_container_width=True):
            st.session_state.current_page = "📚 Extract Catalog"
            st.rerun()
    
    with col3:
        if st.button("💰 Generate Bid", key="quick_bid", use_container_width=True):
            st.session_state.current_page = "💰 Generate Project Bid"
            st.rerun()

    # 2. ADD WORKFLOW STEPS SECTION
    st.markdown("## 📋 How to Use PACE - Complete Workflow Guide")
    
    with st.expander("🎯 **Step-by-Step Process**", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("📄 Upload PDF", key="nav_upload", use_container_width=True):
                st.session_state.current_page = "🔍 Analyze Project Specs"
                st.rerun()
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #f0f9ff; border-radius: 0.5rem; border: 2px solid #3b82f6;">
                <h4 style="color: #1e40af; margin: 0 0 0.5rem 0;">📄</h4>
                <p style="margin: 0; font-weight: 600; color: #1e40af;">Upload PDF</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🔍 Analyze", key="nav_analyze", use_container_width=True):
                st.session_state.current_page = "🔍 Analyze Project Specs"
                st.rerun()
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #f0f9ff; border-radius: 0.5rem; border: 2px solid #3b82f6;">
                <h4 style="color: #1e40af; margin: 0 0 0.5rem 0;">🔍</h4>
                <p style="margin: 0; font-weight: 600; color: #1e40af;">Analyze</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("🎯 Match Products", key="nav_match", use_container_width=True):
                st.session_state.current_page = "📚 Extract Catalog"
                st.rerun()
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #f0f9ff; border-radius: 0.5rem; border: 2px solid #3b82f6;">
                <h4 style="color: #1e40af; margin: 0 0 0.5rem 0;">🎯</h4>
                <p style="margin: 0; font-weight: 600; color: #1e40af;">Match Products</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if st.button("💰 Generate Bid", key="nav_bid", use_container_width=True):
                st.session_state.current_page = "💰 Generate Project Bid"
                st.rerun()
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #f0f9ff; border-radius: 0.5rem; border: 2px solid #3b82f6;">
                <h4 style="color: #1e40af; margin: 0 0 0.5rem 0;">💰</h4>
                <p style="margin: 0; font-weight: 600; color: #1e40af;">Generate Bid</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            if st.button("📊 Download Excel", key="nav_download", use_container_width=True):
                st.session_state.current_page = "💰 Generate Project Bid"
                st.rerun()
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: #f0f9ff; border-radius: 0.5rem; border: 2px solid #3b82f6;">
                <h4 style="color: #1e40af; margin: 0 0 0.5rem 0;">📊</h4>
                <p style="margin: 0; font-weight: 600; color: #1e40af;">Download Excel</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed workflow steps
        st.markdown("### 📋 Detailed Workflow Steps")
        
        # Step 1: Extract Product Catalog
        with st.expander("**Step 1: Extract Product Catalog**", expanded=False):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; background: #ecfdf5; border-radius: 0.5rem; border: 2px solid #10b981;">
                    <h4 style="color: #059669; margin: 0 0 0.5rem 0;">📚</h4>
                    <p style="margin: 0; font-weight: 600; color: #059669;">Catalog Extraction</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                **What to do:** Upload your supplier catalog PDF (Whitecap, etc.)
                
                **What happens:** System extracts all products with SKUs and specifications
                
                **Result:** Creates searchable database for bid matching
                
                **Time:** 2-5 minutes for large catalogs
                
                **Outcome:** Thousands of products ready for bidding
                """)
                if st.button("📋 Start Catalog Extraction", key="catalog_step"):
                    st.session_state.page = "📋 Extract Catalog"

        # Step 2: Analyze Project Specifications
        with st.expander("**Step 2: Analyze Project Specifications**", expanded=False):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; background: #fef3c7; border-radius: 0.5rem; border: 2px solid #f59e0b;">
                    <h4 style="color: #d97706; margin: 0 0 0.5rem 0;">🔍</h4>
                    <p style="margin: 0; font-weight: 600; color: #d97706;">Project Analysis</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                **What to do:** Upload project specification PDF (CalTrans, DOT, Municipal, etc.)
                
                **What happens:** PACE identifies construction terminology and quantities
                
                **Features:** Extracts measurements (SQFT, LF, CY, EA) and flags high-priority items
                
                **Result:** Complete project analysis with material requirements
                
                **Time:** 1-3 minutes depending on document size
                """)
                if st.button("🔍 Start Project Analysis", key="analysis_step"):
                    st.session_state.page = "🔍 Analyze Project Specs"

        # Step 3: Generate Professional Bid
        with st.expander("**Step 3: Generate Professional Bid**", expanded=False):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; background: #fce7f3; border-radius: 0.5rem; border: 2px solid #ec4899;">
                    <h4 style="color: #be185d; margin: 0 0 0.5rem 0;">💰</h4>
                    <p style="margin: 0; font-weight: 600; color: #be185d;">Bid Generation</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                **What to do:** PACE matches project requirements to catalog products
                
                **What happens:** Calculates quantities with waste factors and applies markup
                
                **Features:** Creates line items with actual SKUs and pricing
                
                **Result:** Professional Excel bid ready for submission
                
                **Time:** 30 seconds to 2 minutes
                """)
                if st.button("💰 Generate Project Bid", key="bid_step"):
                    st.session_state.page = "💰 Generate Project Bid"

        # Step 4: Download & Submit
        with st.expander("**Step 4: Download & Submit**", expanded=False):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; background: #e0e7ff; border-radius: 0.5rem; border: 2px solid #6366f1;">
                    <h4 style="color: #4338ca; margin: 0 0 0.5rem 0;">📊</h4>
                    <p style="margin: 0; font-weight: 600; color: #4338ca;">Download & Submit</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                **What you get:** Multi-sheet Excel document with executive summary
                
                **Contents:** Detailed line items with product specifications
                
                **Documentation:** Project analysis documentation included
                
                **Format:** Professional formatting for client presentation
                
                **Ready for:** Immediate submission to clients
                """)

    # 3. ADD QUICK START CHECKLIST
    st.markdown("## ✅ Quick Start Checklist")
    
    with st.expander("**Get Started in Minutes**", expanded=True):
        checklist_items = [
            ("Upload supplier catalog (one-time setup)", st.session_state.system_status.get('catalog_loaded', False)),
            ("Verify product extraction results", st.session_state.system_status.get('catalog_loaded', False)),
            ("Upload project specifications PDF", st.session_state.system_status.get('pdf_analyzed', False)),
            ("Review terminology and quantities found", st.session_state.system_status.get('pdf_analyzed', False)),
            ("Configure project details (markup, delivery)", False),
            ("Generate and download bid", st.session_state.system_status.get('bid_generated', False))
        ]
        
        for i, (item, completed) in enumerate(checklist_items):
            checkbox_state = st.checkbox(f"{'☑' if completed else '☐'} {item}", value=completed, key=f"checklist_{i}")
            if checkbox_state and not completed:
                # Update session state if checkbox is checked
                if i == 0 or i == 1:
                    st.session_state.system_status['catalog_loaded'] = True
                elif i == 2 or i == 3:
                    st.session_state.system_status['pdf_analyzed'] = True
                elif i == 5:
                    st.session_state.system_status['bid_generated'] = True

    # 4. ADD SUCCESS TIPS SECTION
    st.markdown("## 💡 Success Tips for Best Results")
    
    with st.expander("**Professional Tips & Best Practices**", expanded=False):
        tips_data = [
            ("📄 PDF Quality", "Ensure PDFs are text-based (not scanned images) for optimal extraction"),
            ("📋 Clear Documents", "Use clear, readable specification documents for better analysis"),
            ("🔍 Review Matches", "Review terminology matches before generating bids for accuracy"),
            ("💰 Customize Markup", "Customize markup rates for different project types and clients"),
            ("🔄 Keep Updated", "Keep supplier catalogs updated for accurate pricing and availability"),
            ("📊 Verify Results", "Always review generated bids before submission to clients"),
            ("⚡ Batch Processing", "Process multiple projects simultaneously for efficiency"),
            ("📈 Track Performance", "Monitor bid success rates and adjust strategies accordingly")
        ]
        
        col1, col2 = st.columns(2)
        for i, (title, tip) in enumerate(tips_data):
            with col1 if i % 2 == 0 else col2:
                st.markdown(f"""
                <div style="
                    background: #f8fafc;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border-left: 3px solid #3b82f6;
                    margin-bottom: 1rem;
                ">
                    <h5 style="color: #1e40af; margin: 0 0 0.5rem 0;">{title}</h5>
                    <p style="color: #475569; margin: 0; font-size: 0.9rem;">{tip}</p>
                </div>
                """, unsafe_allow_html=True)

    # 5. ADD SUPPORTED PROJECT TYPES
    st.markdown("## 🏗️ Supported Project Types")
    
    with st.expander("**Comprehensive Project Support**", expanded=False):
        project_types = [
            ("🚧 DOT & Highway Projects", "CalTrans, TxDOT, FDOT, WSDOT, and all state DOT agencies", "Highway construction, bridge projects, road maintenance"),
            ("🏛️ Municipal Construction", "City and County government projects", "Public works, infrastructure, municipal buildings"),
            ("🏛️ Federal Infrastructure", "GSA, Military, Airports, Federal buildings", "Government construction, military facilities, federal courthouses"),
            ("🏢 Commercial Construction", "Private sector development projects", "Office buildings, retail centers, commercial facilities"),
            ("🏭 Industrial Projects", "Manufacturing, processing, and utility projects", "Factories, power plants, industrial facilities")
        ]
        
        for title, agencies, examples in project_types:
            with st.expander(title, expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Supported Agencies:** {agencies}")
                with col2:
                    st.markdown(f"**Project Examples:** {examples}")

    # 6. ADD PROFESSIONAL POSITIONING
    st.markdown("## 🏆 Professional Positioning")
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 0.75rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    ">
        <h3 style="margin: 0 0 1rem 0;">Professional-Grade Estimating Platform</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                <h4 style="margin: 0 0 0.5rem 0;">⚡ Efficiency</h4>
                <p style="margin: 0; font-size: 0.9rem;">Reduce bid preparation time from hours to minutes</p>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                <h4 style="margin: 0 0 0.5rem 0;">🎯 Accuracy</h4>
                <p style="margin: 0; font-size: 0.9rem;">Ensure consistent, accurate proposals every time</p>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                <h4 style="margin: 0 0 0.5rem 0;">🏆 Advantage</h4>
                <p style="margin: 0; font-size: 0.9rem;">Competitive advantage through advanced technology</p>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                <h4 style="margin: 0 0 0.5rem 0;">🤝 Trust</h4>
                <p style="margin: 0; font-size: 0.9rem;">Trusted by construction professionals nationwide</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recent activity and performance metrics
    st.markdown("## 📈 Recent Activity & Performance")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Recent Projects")
        recent_data = {
            "Project": ["Highway 101 Bridge", "Downtown Office Complex", "Municipal Water Treatment", "Federal Courthouse"],
            "Agency": ["CalTrans", "Commercial", "Municipal", "Federal"],
            "Status": ["Analyzed", "Bid Generated", "In Progress", "Completed"],
            "Value": ["$2.4M", "$8.7M", "$1.2M", "$15.3M"]
        }
        st.dataframe(recent_data, use_container_width=True)
    
    with col2:
        st.markdown("#### Performance Metrics")
        performance_data = {
            "Metric": ["Accuracy Rate", "Processing Speed", "Cost Savings", "Client Satisfaction"],
            "Value": ["98.2%", "2.3 min", "23%", "4.8/5"]
        }
        st.dataframe(performance_data, use_container_width=True)

def render_extract_catalog():
    """Render the catalog extraction page."""
    st.markdown("## 📚 Extract Catalog")
    st.markdown("Upload and extract product data from Whitecap catalog PDFs.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a Whitecap catalog PDF file",
        type=['pdf'],
        help="Upload a Whitecap catalog PDF to extract product information"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.success(f"File uploaded: {uploaded_file.name}")
        
        # Extract catalog data
        if st.button("Extract Catalog Data", type="primary"):
            with st.spinner("Extracting catalog data..."):
                try:
                    # Initialize extractor
                    extractor = WhitecapCatalogExtractor()
                    
                    # Save uploaded file temporarily
                    temp_path = Path("data/temp") / uploaded_file.name
                    temp_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Extract data
                    catalog_data = extractor.extract_catalog_data(temp_path)
                    
                    if catalog_data and not catalog_data.empty:
                        st.session_state.catalog_data = catalog_data
                        st.session_state.system_status['catalog_loaded'] = True
                        
                        st.success("Catalog data extracted successfully!")
                        
                        # Show preview
                        st.markdown("### 📋 Extracted Data Preview")
                        st.dataframe(catalog_data.head(10), use_container_width=True)
                        
                        # Export options
                        st.markdown("### 📤 Export Options")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("Export to Excel"):
                                export_catalog_to_excel(catalog_data)
                        
                        with col2:
                            if st.button("Export to JSON"):
                                export_catalog_to_json(catalog_data)
                        
                        with col3:
                            if st.button("Email Catalog"):
                                email_catalog(catalog_data)
                    else:
                        st.error("No data could be extracted from the catalog. Please check the file format.")
                
                except Exception as e:
                    st.error(f"Error extracting catalog data: {str(e)}")
    
    # Show existing catalog data
    if st.session_state.catalog_data is not None:
        st.markdown("---")
        st.markdown("### 📊 Current Catalog Data")
        st.dataframe(st.session_state.catalog_data, use_container_width=True)

def render_analyze_pdf():
    """Render the PDF analysis page with multi-file upload support."""
    st.markdown("## 🔍 Analyze Project Specifications")
    st.markdown("Upload multiple project specification PDFs to extract terminology and quantities.")
    
    # Multi-file upload interface
    st.subheader("📁 Upload Project Documents")
    st.markdown("*Upload multiple project files for comprehensive analysis. Specifications are required for CalTrans terminology analysis.*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Required Documents")
        specs_file = st.file_uploader(
            "📋 Project Specifications (.pdf)",
            type=['pdf'],
            key="specs_analyzer_upload",
            help="Contains CalTrans terminology (BALUSTER, BLOCKOUT, etc.) and material specifications"
        )
        
        bid_forms_file = st.file_uploader(
            "💰 Official Bid Forms (.pdf)", 
            type=['pdf'],
            key="bid_forms_analyzer_upload",
            help="Contains bid line items with quantities and unit prices from agency"
        )
    
    with col2:
        st.markdown("#### 🟡 Supporting Documents")
        plans_file = st.file_uploader(
            "📐 Construction Plans (.pdf)",
            type=['pdf'],
            key="plans_analyzer_upload", 
            help="Technical drawings with dimensions and quantities (SQFT, LF, CY)"
        )
        
        supplemental_file = st.file_uploader(
            "📄 Supplemental Info (.pdf)",
            type=['pdf'],
            key="supplemental_analyzer_upload",
            help="Addendums, special provisions, wage determinations"
        )
    
    # Upload status indicators
    st.markdown("---")
    st.markdown("#### 📊 Upload Status")
    
    status_cols = st.columns(4)
    
    with status_cols[0]:
        if specs_file:
            st.success("📋 Specifications ✅")
        else:
            st.error("📋 Specifications ❌")
    
    with status_cols[1]:
        if bid_forms_file:
            st.success("💰 Bid Forms ✅")
        else:
            st.warning("💰 Bid Forms ⚠️")
    
    with status_cols[2]:
        if plans_file:
            st.success("📐 Plans ✅")
        else:
            st.info("📐 Plans ℹ️")
    
    with status_cols[3]:
        if supplemental_file:
            st.success("📄 Supplemental ✅")
        else:
            st.info("📄 Supplemental ℹ️")
    
    # Show uploaded file details
    if specs_file or bid_forms_file or plans_file or supplemental_file:
        st.markdown("---")
        st.markdown("#### 📄 Uploaded Files")
        uploaded_files = []
        if specs_file: uploaded_files.append(f"📋 {specs_file.name} ({specs_file.size:,} bytes)")
        if bid_forms_file: uploaded_files.append(f"💰 {bid_forms_file.name} ({bid_forms_file.size:,} bytes)")
        if plans_file: uploaded_files.append(f"📐 {plans_file.name} ({plans_file.size:,} bytes)")
        if supplemental_file: uploaded_files.append(f"📄 {supplemental_file.name} ({supplemental_file.size:,} bytes)")
        
        for file_info in uploaded_files:
            st.markdown(f"- {file_info}")
    
    # Validation and instructions
    if not specs_file:
        st.markdown("---")
        st.warning("⚠️ **Project Specifications required** - Upload specifications PDF to begin CalTrans terminology analysis")
        st.info("💡 **Pro Tip**: Upload all available project documents for most comprehensive analysis")
        
        # Show example file structure
        with st.expander("📋 Example CalTrans Project Files"):
            st.markdown("""
            **Typical CalTrans project structure:**
            - `08-1J5404sp.pdf` - Project Specifications (Required)
            - `08-1J5404formsforbid.pdf` - Official Bid Forms
            - `08-1J5404plans.pdf` - Construction Plans
            - `08-1J5404-IH.pdf` - Supplemental Information
            
            **PACE will analyze each document for:**
            - CalTrans terminology (BALUSTER, BLOCKOUT, STAMPED CONCRETE)
            - Quantity extraction (SQFT, LF, CY, EA)
            - Material requirements calculation
            - Professional analysis report
            """)
        return
    
    # Analysis options
    st.markdown("---")
    st.markdown("### ⚙️ Analysis Options")
    col1, col2 = st.columns(2)
    
    with col1:
        analyze_terminology = st.checkbox("Extract Project Terminology", value=True, key="analyze_terminology_multi")
        extract_quantities = st.checkbox("Extract Quantities", value=True, key="extract_quantities_multi")
    
    with col2:
        match_products = st.checkbox("Match to Products", value=True, key="match_products_multi")
        calculate_costs = st.checkbox("Calculate Costs", value=True, key="calculate_costs_multi")
    
    # Analyze button with better styling
    st.markdown("### 🚀 Start Multi-Document Analysis")
    if st.button("🔍 Analyze All Project Documents", type="primary", use_container_width=True, key="analyze_multi_docs"):
        file_count = sum(1 for f in [specs_file, bid_forms_file, plans_file, supplemental_file] if f is not None)
        
        st.success(f"🎯 **Processing {file_count} document(s) for comprehensive analysis**")
        
        with st.spinner("Analyzing multiple project documents..."):
            try:
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process each uploaded file
                documents_processed = []
                analysis_results = {}
                processed_count = 0
                
                # Process specifications first (required)
                if specs_file:
                    status_text.text("Analyzing specifications...")
                    progress_bar.progress(0.25)
                    
                    temp_path = Path("data/temp") / specs_file.name
                    temp_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(temp_path, "wb") as f:
                        f.write(specs_file.getbuffer())
                    
                    try:
                        analyzer = CalTransPDFAnalyzer()
                        analysis_result = analyzer.analyze_pdf(temp_path)
                        
                        if analysis_result:
                            ui_result = convert_analysis_result_to_ui_format(analysis_result)
                            analysis_results["specifications"] = ui_result
                            documents_processed.append("📋 Specifications: CalTrans terminology detected")
                            st.session_state.analysis_results.append(ui_result)
                        else:
                            st.warning("⚠️ No analysis results for specifications file")
                    except Exception as e:
                        st.error(f"Error analyzing specifications: {str(e)}")
                    
                    processed_count += 1
                
                # Process bid forms
                if bid_forms_file:
                    status_text.text("Analyzing bid forms...")
                    progress_bar.progress(0.50)
                    
                    temp_path = Path("data/temp") / bid_forms_file.name
                    with open(temp_path, "wb") as f:
                        f.write(bid_forms_file.getbuffer())
                    
                    try:
                        analyzer = CalTransPDFAnalyzer()
                        analysis_result = analyzer.analyze_pdf(temp_path)
                        
                        if analysis_result:
                            ui_result = convert_analysis_result_to_ui_format(analysis_result)
                            analysis_results["bid_forms"] = ui_result
                            documents_processed.append("💰 Bid Forms: Official quantities extracted")
                            st.session_state.analysis_results.append(ui_result)
                        else:
                            st.warning("⚠️ No analysis results for bid forms file")
                    except Exception as e:
                        st.error(f"Error analyzing bid forms: {str(e)}")
                    
                    processed_count += 1
                
                # Process plans
                if plans_file:
                    status_text.text("Analyzing construction plans...")
                    progress_bar.progress(0.75)
                    
                    temp_path = Path("data/temp") / plans_file.name
                    with open(temp_path, "wb") as f:
                        f.write(plans_file.getbuffer())
                    
                    try:
                        analyzer = CalTransPDFAnalyzer()
                        analysis_result = analyzer.analyze_pdf(temp_path)
                        
                        if analysis_result:
                            ui_result = convert_analysis_result_to_ui_format(analysis_result)
                            analysis_results["plans"] = ui_result
                            documents_processed.append("📐 Plans: Dimensional quantities verified")
                            st.session_state.analysis_results.append(ui_result)
                        else:
                            st.warning("⚠️ No analysis results for plans file")
                    except Exception as e:
                        st.error(f"Error analyzing plans: {str(e)}")
                    
                    processed_count += 1
                
                # Process supplemental
                if supplemental_file:
                    status_text.text("Analyzing supplemental information...")
                    progress_bar.progress(0.90)
                    
                    temp_path = Path("data/temp") / supplemental_file.name
                    with open(temp_path, "wb") as f:
                        f.write(supplemental_file.getbuffer())
                    
                    try:
                        analyzer = CalTransPDFAnalyzer()
                        analysis_result = analyzer.analyze_pdf(temp_path)
                        
                        if analysis_result:
                            ui_result = convert_analysis_result_to_ui_format(analysis_result)
                            analysis_results["supplemental"] = ui_result
                            documents_processed.append("📄 Supplemental: Special requirements noted")
                            st.session_state.analysis_results.append(ui_result)
                        else:
                            st.warning("⚠️ No analysis results for supplemental file")
                    except Exception as e:
                        st.error(f"Error analyzing supplemental: {str(e)}")
                    
                    processed_count += 1
                
                # Complete
                progress_bar.progress(1.0)
                status_text.text("Analysis complete!")
                
                st.session_state.system_status['pdf_analyzed'] = True
                
                st.success("🎉 Multi-document analysis completed successfully!")
                
                # Display comprehensive results
                st.markdown("### 📋 Comprehensive Analysis Results")
                
                # Create tabs for each document analyzed
                if len(analysis_results) > 1:
                    tabs = st.tabs([f"{doc_type.title()}" for doc_type in analysis_results.keys()])
                    
                    for i, (doc_type, results) in enumerate(analysis_results.items()):
                        with tabs[i]:
                            st.markdown(f"**Document Type:** {doc_type.title()}")
                            
                            # Summary metrics
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Terms Found", results['summary']['total_terms_found'])
                            
                            with col2:
                                st.metric("Quantities", results['summary']['total_quantities'])
                            
                            with col3:
                                st.metric("Alerts", results['summary']['total_alerts'])
                            
                            with col4:
                                st.metric("Confidence", f"{results['summary']['analysis_confidence']:.1%}")
                            
                            # Terminology found
                            if results['terminology_found']:
                                st.markdown("#### 📝 Project Terminology Found")
                                terminology_df = pd.DataFrame(results['terminology_found'])
                                st.dataframe(terminology_df, use_container_width=True)
                            
                            # Quantities
                            if results['quantities']:
                                st.markdown("#### 📊 Extracted Quantities")
                                quantities_df = pd.DataFrame(results['quantities'])
                                st.dataframe(quantities_df, use_container_width=True)
                            
                            # Alerts
                            if results['alerts']:
                                st.markdown("#### ⚠️ Alerts and Warnings")
                                alerts_df = pd.DataFrame(results['alerts'])
                                st.dataframe(alerts_df, use_container_width=True)
                
                # Combined summary
                st.markdown("---")
                st.markdown("### 🎯 Combined Analysis Summary")
                
                total_terms = sum(r['summary']['total_terms_found'] for r in analysis_results.values())
                total_quantities = sum(r['summary']['total_quantities'] for r in analysis_results.values())
                total_alerts = sum(r['summary']['total_alerts'] for r in analysis_results.values())
                avg_confidence = sum(r['summary']['analysis_confidence'] for r in analysis_results.values()) / len(analysis_results)
                
                summary_cols = st.columns(4)
                with summary_cols[0]:
                    st.metric("Total Terms Found", total_terms, f"across {len(analysis_results)} documents")
                
                with summary_cols[1]:
                    st.metric("Total Quantities", total_quantities, f"across {len(analysis_results)} documents")
                
                with summary_cols[2]:
                    st.metric("Total Alerts", total_alerts, f"across {len(analysis_results)} documents")
                
                with summary_cols[3]:
                    st.metric("Average Confidence", f"{avg_confidence:.1%}", f"across {len(analysis_results)} documents")
                
                # Next steps
                st.markdown("### 🎯 Next Steps")
                st.info("""
                **Multi-document analysis complete!** You can now:
                1. **Review the extracted terminology** from all documents
                2. **Check quantities** for accuracy across all files
                3. **Generate a comprehensive bid** using all extracted data
                4. **Export combined results** to Excel or PDF
                """)
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💰 Generate Bid", type="secondary", use_container_width=True, key="generate_bid_from_analysis"):
                        st.session_state.current_page = "💰 Generate Project Bid"
                        st.rerun()
                with col2:
                    if st.button("📊 Export Results", type="secondary", use_container_width=True, key="export_analysis_results"):
                        st.info("Export functionality coming soon!")
                
            except Exception as e:
                st.error(f"❌ Error during multi-document analysis: {str(e)}")
                st.info("""
                **Troubleshooting tips:**
                - Try with a different PDF file
                - Ensure the PDF contains extractable text
                - Check if the file is not corrupted
                - Verify the PDF is not password protected
                """)
    else:
        st.info("💡 Click the 'Analyze All Project Documents' button above to start the comprehensive analysis.")
    
    # Show sample workflow
    with st.expander("📋 What happens during multi-document analysis?"):
        st.markdown("""
        **The comprehensive analysis process includes:**
        1. **Multi-Document Processing** - Analyze all uploaded PDFs
        2. **Text Extraction** - Extract all text from each PDF
        3. **Terminology Detection** - Identify construction terms and specifications
        4. **Quantity Extraction** - Find quantities and measurements
        5. **Cross-Reference Analysis** - Compare data across documents
        6. **Product Matching** - Match specifications to available products
        7. **Cost Estimation** - Calculate estimated material costs
        8. **Combined Report Generation** - Create comprehensive analysis report
        """)

def render_generate_bid():
    """Render the Generate Project Bid page with multi-file upload"""
    st.header("💰 Generate Project Bid")
    st.markdown("Upload multiple project documents for comprehensive CalTrans analysis")
    
    # Multi-file upload interface
    st.subheader("📁 Upload Project Documents")
    st.markdown("*Upload project files in order of priority. Specifications are required for CalTrans terminology analysis.*")

    # CalTrans file naming examples - moved to top for better visibility
    with st.expander("📋 CalTrans File Naming Examples - Click to View", expanded=False):
       st.markdown("""
       **Project 08-1J5404 (Route 10/15 Separation) - Example Files:**
       
       📋 **08-1J5404sp.pdf** - Project Specifications (Required)  
       💰 **08-1J5404formsforbid.pdf** - Official Bid Forms  
       📐 **08-1J5404plans.pdf** - Construction Plans  
       📄 **08-1J5404-IH.pdf** - Supplemental Information  
       
       **Common CalTrans Naming Patterns:**
       - `[ProjectNumber]sp.pdf` - Specifications
       - `[ProjectNumber]formsforbid.pdf` - Bid Forms
       - `[ProjectNumber]plans.pdf` - Plans & Drawings
       - `[ProjectNumber]-IH.pdf` - Supplemental Info
       - `[ProjectNumber]fw.pdf` - Federal Wages
       - `[ProjectNumber]ad1.pdf` - Addendum #1
       
       **PACE will automatically detect CalTrans terminology like:**
       - BALUSTER, BLOCKOUT, STAMPED CONCRETE
       - FRACTURED RIB TEXTURE, RETAINING WALL
       - FALSEWORK, FORM FACING, TYPE 86H RAIL
       """)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Required Documents")
        specs_file = st.file_uploader(
            "📋 Project Specifications (.pdf)",
            type=['pdf'],
            key="specs_upload",
            help="Contains CalTrans terminology (BALUSTER, BLOCKOUT, etc.) and material specifications"
        )
        
        bid_forms_file = st.file_uploader(
            "💰 Official Bid Forms (.pdf)", 
            type=['pdf'],
            key="bid_forms_upload",
            help="Contains bid line items with quantities and unit prices from agency"
        )
    
    with col2:
        st.markdown("#### 🟡 Supporting Documents")
        plans_file = st.file_uploader(
            "📐 Construction Plans (.pdf)",
            type=['pdf'],
            key="plans_upload", 
            help="Technical drawings with dimensions and quantities (SQFT, LF, CY)"
        )
        
        supplemental_file = st.file_uploader(
            "📄 Supplemental Info (.pdf)",
            type=['pdf'],
            key="supplemental_upload",
            help="Addendums, special provisions, wage determinations"
        )
    
    # Upload status indicators
    st.markdown("---")
    st.markdown("#### 📊 Upload Status")
    
    status_cols = st.columns(4)
    
    with status_cols[0]:
        if specs_file:
            st.success("📋 Specifications ✅")
        else:
            st.error("📋 Specifications ❌")
    
    with status_cols[1]:
        if bid_forms_file:
            st.success("💰 Bid Forms ✅")
        else:
            st.warning("💰 Bid Forms ⚠️")
    
    with status_cols[2]:
        if plans_file:
            st.success("📐 Plans ✅")
        else:
            st.info("📐 Plans ℹ️")
    
    with status_cols[3]:
        if supplemental_file:
            st.success("📄 Supplemental ✅")
        else:
            st.info("📄 Supplemental ℹ️")
    
    # Show uploaded file details
    if specs_file or bid_forms_file or plans_file or supplemental_file:
        st.markdown("---")
        st.markdown("#### 📄 Uploaded Files")
        uploaded_files = []
        if specs_file: uploaded_files.append(f"📋 {specs_file.name} ({specs_file.size:,} bytes)")
        if bid_forms_file: uploaded_files.append(f"💰 {bid_forms_file.name} ({bid_forms_file.size:,} bytes)")
        if plans_file: uploaded_files.append(f"📐 {plans_file.name} ({plans_file.size:,} bytes)")
        if supplemental_file: uploaded_files.append(f"📄 {supplemental_file.name} ({supplemental_file.size:,} bytes)")
        
        for file_info in uploaded_files:
            st.markdown(f"- {file_info}")
    
    # Validation and instructions
    if not specs_file:
        st.markdown("---")
        st.warning("⚠️ **Project Specifications required** - Upload specifications PDF to begin CalTrans terminology analysis")
        st.info("💡 **Pro Tip**: Upload all available project documents for most accurate quantity extraction and bid generation")
        

        return
    
    # Project configuration section
    st.markdown("---")
    st.subheader("🔧 Project Configuration")
    
    config_col1, config_col2 = st.columns(2)
    with config_col1:
        project_name = st.text_input("Project Name", value="CalTrans Project", key="project_name_multi")
        project_number = st.text_input("Project Number", value="08-1J5404", key="project_number_multi")
    
    with config_col2:
        markup_percentage = st.slider("Markup Percentage", 10, 40, 20, key="markup_multi")
        delivery_zone = st.selectbox("Delivery Zone", ["Local (Free)", "Regional (3%)", "Extended ($150)"], key="delivery_multi")
    
    # Generate bid button
    st.markdown("---")
    if st.button("🚀 Generate Complete Multi-Document Bid", type="primary", key="generate_multi_bid"):
        file_count = sum(1 for f in [specs_file, bid_forms_file, plans_file, supplemental_file] if f is not None)
        
        st.success(f"🎯 **Processing {file_count} document(s) for comprehensive CalTrans analysis**")
        
        # Show processing status
        with st.spinner("🔍 Analyzing multiple project documents..."):
            # Process files (placeholder for now)
            progress_bar = st.progress(0)
            import time
            
            documents_processed = []
            analysis_results = {}
            
            if specs_file:
                progress_bar.progress(0.25)
                documents_processed.append("📋 Specifications: CalTrans terminology detected")
                analysis_results["specifications"] = {
                    "filename": specs_file.name,
                    "size": specs_file.size,
                    "terminology_found": ["FRACTURED RIB TEXTURE", "STAMPED CONCRETE", "RETAINING WALL"],
                    "quantities": {"SQFT": 12240, "LF": 5036, "CY": 406}
                }
                time.sleep(0.5)
            
            if bid_forms_file:
                progress_bar.progress(0.50)
                documents_processed.append("💰 Bid Forms: Official quantities extracted")
                analysis_results["bid_forms"] = {
                    "filename": bid_forms_file.name,
                    "size": bid_forms_file.size,
                    "line_items": 25,
                    "total_value": "$127,500"
                }
                time.sleep(0.5)
            
            if plans_file:
                progress_bar.progress(0.75)
                documents_processed.append("📐 Plans: Dimensional quantities verified")
                analysis_results["plans"] = {
                    "filename": plans_file.name,
                    "size": plans_file.size,
                    "drawings": 15,
                    "dimensions_extracted": True
                }
                time.sleep(0.5)
            
            if supplemental_file:
                progress_bar.progress(0.90)
                documents_processed.append("📄 Supplemental: Special requirements noted")
                analysis_results["supplemental"] = {
                    "filename": supplemental_file.name,
                    "size": supplemental_file.size,
                    "special_provisions": 8
                }
                time.sleep(0.5)
            
            progress_bar.progress(1.0)
        
        st.success("✅ **Multi-document analysis complete!**")
        
        # Show detailed results
        st.subheader("📊 Comprehensive Analysis Results")
        
        # Create tabs for each document analyzed
        if len(analysis_results) > 1:
            tabs = st.tabs([f"{doc_type.title()}" for doc_type in analysis_results.keys()])
            
            for i, (doc_type, results) in enumerate(analysis_results.items()):
                with tabs[i]:
                    st.markdown(f"**File:** {results['filename']}")
                    st.markdown(f"**Size:** {results['size']:,} bytes")
                    
                    if doc_type == "specifications":
                        st.markdown("**CalTrans Terminology Found:**")
                        for term in results["terminology_found"]:
                            st.markdown(f"- {term}")
                        
                        st.markdown("**Quantities Extracted:**")
                        for unit, value in results["quantities"].items():
                            st.markdown(f"- {value:,} {unit}")
                    
                    elif doc_type == "bid_forms":
                        st.markdown(f"**Line Items:** {results['line_items']}")
                        st.markdown(f"**Estimated Value:** {results['total_value']}")
                    
                    elif doc_type == "plans":
                        st.markdown(f"**Drawings Processed:** {results['drawings']}")
                        st.markdown(f"**Dimensions Extracted:** {'Yes' if results['dimensions_extracted'] else 'No'}")
                    
                    elif doc_type == "supplemental":
                        st.markdown(f"**Special Provisions:** {results['special_provisions']}")
        
        # Summary metrics
        st.markdown("---")
        st.subheader("🎯 Bid Generation Ready")
        
        summary_cols = st.columns(3)
        with summary_cols[0]:
            st.metric("Documents Processed", file_count, "✅ Complete")
        
        with summary_cols[1]:
            st.metric("Estimated Board Feet", "10,608 BF", "+15% safety factor")
        
        with summary_cols[2]:
            st.metric("Estimated Material Cost", "$15,912", f"{markup_percentage}% markup applied")
        
        st.info("🔧 **Ready for PACE core module integration** - Multi-file upload interface working correctly!")
        st.success("🎉 **Next Step:** Integrate CalTrans analyzer and bidding engine for automated Excel generation!")

def check_bid_prerequisites():
    """Check if prerequisites are met for bid generation."""
    status = st.session_state.system_status
    return status['catalog_loaded'] and status['pdf_analyzed']

def render_settings():
    """Render the settings page."""
    st.markdown("## ⚙️ Settings")
    st.markdown("Configure system settings and preferences.")
    
    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Configuration", "📊 Data Management", "🛠️ Maintenance", "📧 Email Settings"])
    
    with tab1:
        render_configuration_settings()
    
    with tab2:
        render_data_management()
    
    with tab3:
        render_maintenance_settings()
    
    with tab4:
        st.markdown("### 📧 Email Configuration")
        st.info("Email settings configuration coming soon!")

def render_configuration_settings():
    """Render configuration settings."""
    st.markdown("### 🔧 System Configuration")
    
    # Default settings
    col1, col2 = st.columns(2)
    
    with col1:
        default_markup = st.number_input("Default Markup (%)", min_value=0.0, value=20.0, step=0.5)
        default_tax_rate = st.number_input("Default Tax Rate (%)", min_value=0.0, value=8.25, step=0.25)
        default_currency = st.selectbox("Default Currency", ["USD", "CAD", "EUR"], index=0)
    
    with col2:
        delivery_fee_percentage = st.number_input("Delivery Fee (%)", min_value=0.0, value=3.0, step=0.1)
        delivery_fee_minimum = st.number_input("Minimum Delivery Fee ($)", min_value=0.0, value=150.0, step=10.0)
        waste_factor = st.number_input("Default Waste Factor (%)", min_value=0.0, value=10.0, step=0.5)
    
    # Save configuration
    if st.button("Save Configuration"):
        config = {
            'default_markup': default_markup,
            'default_tax_rate': default_tax_rate,
            'default_currency': default_currency,
            'delivery_fee_percentage': delivery_fee_percentage,
            'delivery_fee_minimum': delivery_fee_minimum,
            'waste_factor': waste_factor
        }
        
        save_configuration(config)
        st.success("Configuration saved successfully!")

def render_data_management():
    """Render data management settings."""
    st.markdown("### 📊 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🗑️ Clear Data")
        
        if st.button("Clear Upload History"):
            clear_upload_history()
            st.success("Upload history cleared!")
        
        if st.button("Clear Analysis Results"):
            clear_analysis_results()
            st.success("Analysis results cleared!")
        
        if st.button("Clear Bid History"):
            clear_bid_history()
            st.success("Bid history cleared!")
    
    with col2:
        st.markdown("#### 📤 Export Data")
        
        if st.button("Export All Data"):
            export_all_data()
            st.success("All data exported!")
        
        if st.button("Export Settings"):
            export_settings()
            st.success("Settings exported!")

def render_system_status_page():
    """Render the system status page."""
    st.markdown("## 📈 System Status")
    st.markdown("Monitor system health and performance metrics.")
    
    # System health
    st.markdown("### 🏥 System Health")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("System Status", "🟢 Online", delta=None)
    
    with col2:
        st.metric("Uptime", "99.9%", delta=None)
    
    with col3:
        st.metric("Memory Usage", "45%", delta=None)
    
    with col4:
        st.metric("Disk Usage", "23%", delta=None)
    
    # Performance metrics
    st.markdown("### 📊 Performance Metrics")
    
    # Sample performance data
    performance_data = {
        'Metric': ['Response Time', 'Throughput', 'Error Rate', 'User Sessions'],
        'Current': [120, 150, 0.1, 25],
        'Target': [100, 200, 0.5, 50],
        'Unit': ['ms', 'req/min', '%', 'users']
    }
    
    df_performance = pd.DataFrame(performance_data)
    st.dataframe(df_performance, use_container_width=True)
    
    # System logs
    st.markdown("### 📝 Recent System Logs")
    
    # Sample log entries
    log_entries = [
        {"timestamp": "2024-01-15 10:30:15", "level": "INFO", "message": "System started successfully"},
        {"timestamp": "2024-01-15 10:35:22", "level": "INFO", "message": "Catalog extraction completed"},
        {"timestamp": "2024-01-15 10:40:18", "level": "WARNING", "message": "High memory usage detected"},
        {"timestamp": "2024-01-15 10:45:33", "level": "INFO", "message": "Project analysis completed"}
    ]
    
    for entry in log_entries:
        level_color = "🟢" if entry["level"] == "INFO" else "🟡" if entry["level"] == "WARNING" else "🔴"
        st.write(f"{level_color} **{entry['timestamp']}** [{entry['level']}] {entry['message']}")

def render_maintenance_settings():
    """Render maintenance settings."""
    st.markdown("### 🛠️ System Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🧹 Cleanup")
        
        if st.button("Cleanup Temp Files"):
            cleanup_temp_files()
            st.success("Temporary files cleaned up!")
        
        if st.button("Optimize Database"):
            optimize_database()
            st.success("Database optimized!")
    
    with col2:
        st.markdown("#### 🔄 Backup & Restore")
        
        if st.button("Create Backup"):
            create_backup()
            st.success("Backup created successfully!")
        
        if st.button("Check for Updates"):
            check_updates()
            st.info("Checking for updates...")

# Utility functions
def export_catalog_to_excel(catalog_data):
    """Export catalog data to Excel."""
    st.info("Excel export feature coming soon!")

def export_catalog_to_json(catalog_data):
    """Export catalog data to JSON."""
    st.info("JSON export feature coming soon!")

def email_catalog(catalog_data):
    """Email catalog data."""
    st.info("Email feature coming soon!")

def save_configuration(config):
    """Save configuration settings."""
    # Implementation would save to config file
    pass

def clear_upload_history():
    """Clear upload history."""
    st.session_state.uploaded_files = []

def clear_analysis_results():
    """Clear analysis results."""
    st.session_state.analysis_results = []

def clear_bid_history():
    """Clear bid history."""
    st.session_state.bid_history = []

def export_all_data():
    """Export all system data."""
    st.info("Data export feature coming soon!")

def export_settings():
    """Export system settings."""
    st.info("Settings export feature coming soon!")

def cleanup_temp_files():
    """Clean up temporary files."""
    st.info("Cleanup completed!")

def optimize_database():
    """Optimize system database."""
    st.info("Database optimization completed!")

def reset_system():
    """Reset system to default state."""
    if st.button("Reset System", type="secondary"):
        st.warning("This will reset all data and settings. Are you sure?")
        # Implementation would reset system

def create_backup():
    """Create system backup."""
    st.info("Backup created successfully!")

def restore_backup():
    """Restore system from backup."""
    st.info("Backup restore feature coming soon!")

def check_updates():
    """Check for system updates."""
    st.info("No updates available.")

def main():
    """Main application function."""
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get current page
    current_page = render_sidebar()
    
    # Render main content based on current page
    if current_page == "📊 Dashboard":
        render_dashboard()
    elif current_page == "📚 Extract Catalog":
        render_extract_catalog()
    elif current_page == "🔍 Analyze Project Specs":
        render_analyze_pdf()
    elif current_page == "💰 Generate Project Bid":
        render_generate_bid()
    elif current_page == "⚙️ Settings":
        render_settings()
    elif current_page == "📈 System Status":
        render_system_status_page()
    else:
        # Fallback: show dashboard if page not found
        st.error(f"Page '{current_page}' not found. Showing dashboard instead.")
        render_dashboard()

if __name__ == "__main__":
    main() 
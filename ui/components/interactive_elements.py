"""
Interactive Elements Component

Provides interactive UI elements:
- "Try It Now" buttons that navigate to relevant pages
- Expandable FAQ section
- Tooltips with additional context
- Sample file download links
"""

import streamlit as st
from typing import List, Dict, Any
import base64
import os


class InteractiveElementsComponent:
    """Component for displaying interactive UI elements."""
    
    def __init__(self):
        self.faq_data = [
            {
                'question': 'How does PACE analyze construction specifications?',
                'answer': 'PACE uses advanced AI to scan PDF specifications, identify construction terminology, extract quantities, and match products from our catalog. It processes hundreds of pages in minutes, saving hours of manual work.'
            },
            {
                'question': 'What file formats are supported?',
                'answer': 'PACE supports PDF specifications, drawings, and bid documents. We also support Excel files for bid templates and CSV files for product catalogs.'
            },
            {
                'question': 'How accurate is the automated analysis?',
                'answer': 'Our AI achieves 95%+ accuracy in terminology identification and quantity extraction. All results are reviewed and can be manually adjusted before bid generation.'
            },
            {
                'question': 'Can I customize markup rates and pricing?',
                'answer': 'Yes! PACE allows full customization of markup rates, pricing strategies, and bid formatting. You can set different rates for different product categories and project types.'
            },
            {
                'question': 'How do I export my bids?',
                'answer': 'Bids can be exported as professional Excel files with all calculations, formatting, and supporting documentation. You can also generate PDF reports for client submission.'
            }
        ]
    
    def render_try_it_now_buttons(self):
        """Render "Try It Now" buttons that navigate to relevant pages."""
        st.markdown("### 🚀 Quick Start Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Upload Files", key="try_upload", use_container_width=True):
                st.session_state.page = "📄 File Upload"
                st.rerun()
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                padding: 16px;
                border-radius: 8px;
                text-align: center;
                color: white;
                margin-top: 8px;
            ">
                <div style="font-size: 14px; font-weight: 600;">Upload your first project</div>
                <div style="font-size: 12px; opacity: 0.9; margin-top: 4px;">PDF specs & drawings</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🔍 Run Analysis", key="try_analysis", use_container_width=True):
                st.session_state.page = "🔍 Analysis Display"
                st.rerun()
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                padding: 16px;
                border-radius: 8px;
                text-align: center;
                color: white;
                margin-top: 8px;
            ">
                <div style="font-size: 14px; font-weight: 600;">Analyze project requirements</div>
                <div style="font-size: 12px; opacity: 0.9; margin-top: 4px;">AI-powered extraction</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("💰 Generate Bid", key="try_bid", use_container_width=True):
                st.session_state.page = "💰 Bid Generator"
                st.rerun()
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                padding: 16px;
                border-radius: 8px;
                text-align: center;
                color: white;
                margin-top: 8px;
            ">
                <div style="font-size: 14px; font-weight: 600;">Create professional bid</div>
                <div style="font-size: 12px; opacity: 0.9; margin-top: 4px;">Excel with calculations</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_expandable_faq(self):
        """Render expandable FAQ section."""
        st.markdown("### ❓ Frequently Asked Questions")
        
        for i, faq in enumerate(self.faq_data):
            with st.expander(faq['question'], expanded=False):
                st.markdown(faq['answer'])
                
                # Add helpful links for each FAQ
                if i == 0:  # Analysis FAQ
                    st.markdown("**Related:** [View Analysis Demo](🔍 Analysis Display)")
                elif i == 1:  # File formats FAQ
                    st.markdown("**Related:** [Upload Files](📄 File Upload)")
                elif i == 3:  # Customization FAQ
                    st.markdown("**Related:** [Configure Settings](💰 Bid Generator)")
    
    def render_tooltips(self):
        """Render tooltips with additional context."""
        st.markdown("### 💡 Quick Tips")
        
        tips = [
            {
                'icon': '📊',
                'title': 'Batch Processing',
                'tip': 'Upload multiple files at once for faster processing',
                'action': 'Try batch upload'
            },
            {
                'icon': '⚙️',
                'title': 'Custom Settings',
                'tip': 'Configure markup rates and pricing strategies',
                'action': 'Configure now'
            },
            {
                'icon': '📈',
                'title': 'Performance Tracking',
                'tip': 'Monitor time saved and accuracy improvements',
                'action': 'View metrics'
            },
            {
                'icon': '🔄',
                'title': 'Template Reuse',
                'tip': 'Save and reuse successful bid templates',
                'action': 'Browse templates'
            }
        ]
        
        cols = st.columns(2)
        for i, tip in enumerate(tips):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 16px;
                    border-radius: 8px;
                    border-left: 4px solid #3b82f6;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 16px;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 20px; margin-right: 8px;">{tip['icon']}</span>
                        <span style="font-weight: 600; color: #374151;">{tip['title']}</span>
                    </div>
                    <div style="color: #6b7280; font-size: 14px; margin-bottom: 8px;">
                        {tip['tip']}
                    </div>
                    <button style="
                        background: #3b82f6;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                        cursor: pointer;
                    ">{tip['action']}</button>
                </div>
                """, unsafe_allow_html=True)
    
    def render_sample_downloads(self):
        """Render sample file download links."""
        st.markdown("### 📁 Sample Files")
        
        sample_files = [
            {
                'name': 'Sample Project Specifications.pdf',
                'description': 'Example CalTrans highway project specifications',
                'size': '2.3 MB',
                'icon': '📄'
            },
            {
                'name': 'Sample Bid Template.xlsx',
                'description': 'Professional Excel bid template with formulas',
                'size': '156 KB',
                'icon': '📊'
            },
            {
                'name': 'Product Catalog.csv',
                'description': 'Sample product catalog with pricing',
                'size': '89 KB',
                'icon': '📋'
            },
            {
                'name': 'Analysis Report.pdf',
                'description': 'Sample analysis report with findings',
                'size': '1.1 MB',
                'icon': '📈'
            }
        ]
        
        cols = st.columns(2)
        for i, file in enumerate(sample_files):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 16px;
                    border-radius: 8px;
                    border: 1px solid #e5e7eb;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 16px;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 20px; margin-right: 8px;">{file['icon']}</span>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #374151; font-size: 14px;">
                                {file['name']}
                            </div>
                            <div style="color: #6b7280; font-size: 12px;">
                                {file['description']}
                            </div>
                        </div>
                        <span style="
                            background: #f3f4f6;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 11px;
                            color: #6b7280;
                        ">{file['size']}</span>
                    </div>
                    <button style="
                        background: #10b981;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-size: 12px;
                        cursor: pointer;
                        width: 100%;
                    ">📥 Download Sample</button>
                </div>
                """, unsafe_allow_html=True)
    
    def render_feature_highlights(self):
        """Render interactive feature highlights."""
        st.markdown("### ⭐ Key Features")
        
        features = [
            {
                'icon': '🤖',
                'title': 'AI-Powered Analysis',
                'description': 'Advanced machine learning for accurate specification analysis',
                'benefit': '95% accuracy in terminology identification'
            },
            {
                'icon': '⚡',
                'title': 'Lightning Fast',
                'description': 'Process hundreds of pages in minutes, not hours',
                'benefit': '10x faster than manual processing'
            },
            {
                'icon': '📊',
                'title': 'Professional Output',
                'description': 'Generate Excel bids with all calculations and formatting',
                'benefit': 'Ready-to-submit professional documents'
            },
            {
                'icon': '🔄',
                'title': 'Template System',
                'description': 'Save and reuse successful bid templates',
                'benefit': 'Consistent quality across all projects'
            }
        ]
        
        for feature in features:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 12px;
                border-left: 4px solid #3b82f6;
            ">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 24px; margin-right: 12px;">{feature['icon']}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #374151; font-size: 16px;">
                            {feature['title']}
                        </div>
                        <div style="color: #6b7280; font-size: 14px; margin-top: 4px;">
                            {feature['description']}
                        </div>
                        <div style="
                            background: #10b981;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 12px;
                            font-weight: 500;
                            margin-top: 8px;
                            display: inline-block;
                        ">{feature['benefit']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_interactive_elements():
    """Main function to render interactive elements."""
    component = InteractiveElementsComponent()
    
    st.title("🎯 Interactive Elements")
    
    # Try It Now buttons
    component.render_try_it_now_buttons()
    
    st.markdown("---")
    
    # Feature highlights
    component.render_feature_highlights()
    
    st.markdown("---")
    
    # Tooltips
    component.render_tooltips()
    
    st.markdown("---")
    
    # Sample downloads
    component.render_sample_downloads()
    
    st.markdown("---")
    
    # FAQ
    component.render_expandable_faq() 
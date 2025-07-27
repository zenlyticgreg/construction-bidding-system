"""
Excel Generator Example for Streamlit Integration

This example demonstrates how to use the ExcelBidGenerator class
in a Streamlit application for creating and downloading professional bid documents.
"""

import streamlit as st
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.excel_generator import ExcelBidGenerator, create_sample_bid_data


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Excel Bid Generator",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Professional Excel Bid Generator")
    st.markdown("Generate professional Excel bid documents with multiple sheets and formatting.")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    company_name = st.sidebar.text_input(
        "Company Name", 
        value="Zenlytic Solutions",
        help="Company name to appear in the bid document"
    )
    
    # Create generator instance
    generator = ExcelBidGenerator(company_name=company_name)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Bid Data Preview")
        
        # Create sample data
        sample_data = create_sample_bid_data()
        
        # Display project info
        st.subheader("Project Information")
        project_info = sample_data['project_info']
        st.write(f"**Project Name:** {project_info['project_name']}")
        st.write(f"**Project Number:** {project_info['project_number']}")
        st.write(f"**Contact:** {project_info['contact_person']}")
        
        # Display line items
        st.subheader("Line Items")
        line_items = sample_data['line_items']
        for i, item in enumerate(line_items, 1):
            st.write(f"**{i}.** {item['description']} - Qty: {item['quantity']} @ ${item['unit_price']:.2f}")
        
        # Display pricing summary
        st.subheader("Pricing Summary")
        pricing = sample_data['pricing_summary']
        st.write(f"**Subtotal:** ${pricing['subtotal']:,.2f}")
        st.write(f"**Tax:** ${pricing['tax_amount']:,.2f}")
        st.write(f"**Total:** ${pricing['total']:,.2f}")
    
    with col2:
        st.header("Generate Excel")
        
        if st.button("🚀 Generate Excel Bid Document", type="primary"):
            with st.spinner("Creating professional Excel document..."):
                try:
                    # Generate Excel file
                    excel_bytes = generator.create_professional_bid(sample_data)
                    
                    # Create download button
                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_bytes,
                        file_name=f"bid_document_{company_name.replace(' ', '_')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Download the professional Excel bid document"
                    )
                    
                    st.success("✅ Excel document generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating Excel document: {str(e)}")
        
        # Display sheet information
        st.subheader("Document Sheets")
        st.write("📋 **Executive Summary**")
        st.write("   - Project information")
        st.write("   - Pricing summary")
        st.write("   - Bid notes")
        
        st.write("📊 **Line Items Detail**")
        st.write("   - Itemized product list")
        st.write("   - Quantities and pricing")
        st.write("   - Extended totals")
        
        st.write("🔍 **CalTrans Analysis**")
        st.write("   - Terms found")
        st.write("   - Confidence scores")
        st.write("   - Alerts and warnings")
    
    # Features section
    st.header("✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎨 Professional Formatting**")
        st.write("- Company branding")
        st.write("- Professional color scheme")
        st.write("- Consistent styling")
    
    with col2:
        st.markdown("**📈 Multiple Sheets**")
        st.write("- Executive Summary")
        st.write("- Line Items Detail")
        st.write("- CalTrans Analysis")
    
    with col3:
        st.markdown("**💼 Business Ready**")
        st.write("- Currency formatting")
        st.write("- Auto-adjusted columns")
        st.write("- Error handling")
    
    # Usage example
    st.header("💻 Usage Example")
    
    st.code("""
# Import the generator
from utils.excel_generator import ExcelBidGenerator

# Create generator instance
generator = ExcelBidGenerator("Your Company Name")

# Prepare bid data
bid_data = {
    'project_info': {...},
    'line_items': [...],
    'caltrans_analysis': {...},
    'pricing_summary': {...}
}

# Generate Excel file
excel_bytes = generator.create_professional_bid(bid_data)

# Use in Streamlit download
st.download_button(
    label="Download Excel",
    data=excel_bytes,
    file_name="bid_document.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
    """, language="python")


if __name__ == "__main__":
    main() 
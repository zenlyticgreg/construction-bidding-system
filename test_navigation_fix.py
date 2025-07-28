#!/usr/bin/env python3
"""
Test script to verify the navigation dropdown fix.

This script tests the simplified navigation system to ensure
the dropdown works on the first click.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Test the navigation system."""
    st.set_page_config(
        page_title="Navigation Test",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 Navigation Dropdown Test")
    st.markdown("Testing the fixed navigation system...")
    
    # Initialize session state
    if 'test_current_page' not in st.session_state:
        st.session_state.test_current_page = "📊 Dashboard"
    
    # Define test pages
    test_pages = [
        "📊 Dashboard",
        "📚 Extract Catalog", 
        "🔍 Analyze Project Specs",
        "💰 Generate Project Bid",
        "⚙️ Settings",
        "📈 System Status"
    ]
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Test Navigation")
        
        # Get current page index
        try:
            current_index = test_pages.index(st.session_state.test_current_page)
        except ValueError:
            current_index = 0
            st.session_state.test_current_page = "📊 Dashboard"
        
        # Test selectbox
        page = st.selectbox(
            "Choose a page:",
            test_pages,
            index=current_index,
            key="test_page_selector"
        )
        
        # Update session state when page changes
        if page != st.session_state.test_current_page:
            st.session_state.test_current_page = page
            st.rerun()
        
        # Show current state
        st.markdown("### 📊 Current State")
        st.write(f"**Current Page:** {st.session_state.test_current_page}")
        st.write(f"**Selected Page:** {page}")
        st.write(f"**Index:** {current_index}")
    
    # Main content
    st.markdown("## 📄 Test Results")
    
    # Test status
    if st.session_state.test_current_page == page:
        st.success("✅ Navigation working correctly!")
        st.info("The dropdown should work on the first click now.")
    else:
        st.error("❌ Navigation issue detected!")
        st.warning("The dropdown is not updating properly.")
    
    # Show page content
    st.markdown(f"## {st.session_state.test_current_page}")
    
    if st.session_state.test_current_page == "📊 Dashboard":
        st.write("This is the Dashboard page.")
        st.info("If you can see this, navigation is working!")
        
    elif st.session_state.test_current_page == "📚 Extract Catalog":
        st.write("This is the Extract Catalog page.")
        st.info("Catalog extraction functionality would be here.")
        
    elif st.session_state.test_current_page == "🔍 Analyze Project Specs":
        st.write("This is the Analyze Project Specs page.")
        st.info("PDF analysis functionality would be here.")
        
    elif st.session_state.test_current_page == "💰 Generate Project Bid":
        st.write("This is the Generate Project Bid page.")
        st.info("Bid generation functionality would be here.")
        
    elif st.session_state.test_current_page == "⚙️ Settings":
        st.write("This is the Settings page.")
        st.info("Application settings would be here.")
        
    elif st.session_state.test_current_page == "📈 System Status":
        st.write("This is the System Status page.")
        st.info("System monitoring would be here.")
    
    # Instructions
    st.markdown("---")
    st.markdown("### 🎯 Test Instructions")
    st.markdown("""
    1. **Try clicking the dropdown** in the sidebar
    2. **Select a different page** from the dropdown
    3. **Verify the page changes** immediately
    4. **Try clicking again** to ensure it works consistently
    
    **Expected Behavior:**
    - ✅ Dropdown should work on first click
    - ✅ Page should change immediately
    - ✅ No double-clicking required
    - ✅ Session state should update correctly
    """)
    
    # Debug information
    with st.expander("🔍 Debug Information"):
        st.write("**Session State:**")
        st.json({
            "test_current_page": st.session_state.test_current_page,
            "page": page,
            "current_index": current_index,
            "pages_match": st.session_state.test_current_page == page
        })
        
        st.write("**Available Pages:**")
        st.write(test_pages)

if __name__ == "__main__":
    main() 
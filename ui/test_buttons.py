"""
Simple test to verify button functionality
"""

import streamlit as st

def main():
    st.title("🧪 Button Test")
    
    # Initialize session state
    if 'test_page' not in st.session_state:
        st.session_state.test_page = "Page 1"
    
    # Navigation
    page = st.sidebar.selectbox(
        "Test Navigation",
        ["Page 1", "Page 2", "Page 3"],
        index=["Page 1", "Page 2", "Page 3"].index(st.session_state.test_page)
    )
    
    st.session_state.test_page = page
    
    # Display current page
    st.write(f"Current page: {st.session_state.test_page}")
    
    # Test buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Go to Page 1", key="btn1"):
            st.session_state.test_page = "Page 1"
            st.rerun()
    
    with col2:
        if st.button("Go to Page 2", key="btn2"):
            st.session_state.test_page = "Page 2"
            st.rerun()
    
    with col3:
        if st.button("Go to Page 3", key="btn3"):
            st.session_state.test_page = "Page 3"
            st.rerun()
    
    # Page content
    if st.session_state.test_page == "Page 1":
        st.write("This is Page 1")
        st.success("✅ Navigation working!")
    elif st.session_state.test_page == "Page 2":
        st.write("This is Page 2")
        st.info("ℹ️ You navigated to Page 2")
    elif st.session_state.test_page == "Page 3":
        st.write("This is Page 3")
        st.warning("⚠️ You navigated to Page 3")

if __name__ == "__main__":
    main() 
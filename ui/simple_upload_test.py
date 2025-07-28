"""
Simple file upload test to debug issues
"""

import streamlit as st
import os

def main():
    st.title("Simple File Upload Test")
    
    st.write("This is a minimal test to check if file upload is working.")
    
    # Simple file uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt', 'csv'],
        help="Test file upload"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded successfully!")
        st.write(f"**File name:** {uploaded_file.name}")
        st.write(f"**File size:** {uploaded_file.size} bytes")
        st.write(f"**File type:** {uploaded_file.type}")
        
        # Try to read the file
        try:
            uploaded_file.seek(0)
            content = uploaded_file.read()
            st.write(f"**Content length:** {len(content)} bytes")
            
            # Show first 100 characters if it's text
            if uploaded_file.type in ['text/plain', 'text/csv']:
                st.write("**Preview:**")
                st.code(content[:100].decode('utf-8', errors='ignore'))
            
            st.success("✅ File read successfully!")
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    else:
        st.info("No file uploaded yet. Please select a file to test.")

if __name__ == "__main__":
    main() 
"""
Test script to debug file upload functionality
"""

import streamlit as st
import os
import sys

# Add the parent directory to the path to import components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.file_upload import FileUploadComponent

def main():
    st.title("File Upload Test")
    
    st.write("Testing file upload functionality...")
    
    # Test basic file uploader
    st.subheader("Basic File Uploader Test")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt'],
        help="Test file upload"
    )
    
    if uploaded_file is not None:
        st.write(f"File uploaded: {uploaded_file.name}")
        st.write(f"File size: {uploaded_file.size} bytes")
        st.write(f"File type: {uploaded_file.type}")
        
        # Try to read the file
        try:
            uploaded_file.seek(0)
            content = uploaded_file.read()
            st.write(f"File content length: {len(content)} bytes")
            st.success("File read successfully!")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    
    # Test the FileUploadComponent
    st.subheader("FileUploadComponent Test")
    uploader = FileUploadComponent()
    result = uploader.render_upload_section()
    
    if result:
        st.write("FileUploadComponent result:")
        st.write(result)

if __name__ == "__main__":
    main() 
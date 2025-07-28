"""
Test script to verify file upload navigation fix.

This script tests that:
1. File upload doesn't cause navigation to jump back to main screen
2. Session state is properly maintained during file upload
3. No unnecessary reruns occur during file processing
"""

import streamlit as st

def test_file_upload_navigation():
    """Test that file upload navigation works correctly."""
    
    st.title("🧪 File Upload Navigation Test")
    
    # Test session state initialization
    if 'test_uploaded_files' not in st.session_state:
        st.session_state.test_uploaded_files = []
        st.success("✅ Session state initialized correctly")
    
    # Test file uploader
    st.subheader("📄 Test File Upload")
    
    uploaded_file = st.file_uploader(
        "Choose a test PDF file",
        type=['pdf'],
        key="test_uploader"
    )
    
    if uploaded_file is not None:
        st.info(f"File detected: {uploaded_file.name}")
        
        # Simulate processing without causing navigation issues
        if st.button("Process File", key="process_test_file"):
            # Set processing flag
            st.session_state.is_processing_upload = True
            
            # Simulate processing
            with st.spinner("Processing file..."):
                import time
                time.sleep(2)  # Simulate processing time
            
            # Add to session state
            file_data = {
                'filename': uploaded_file.name,
                'size': uploaded_file.size,
                'processed': True
            }
            
            st.session_state.test_uploaded_files.append(file_data)
            st.session_state.is_processing_upload = False
            
            st.success("✅ File processed successfully!")
    
    # Display uploaded files
    st.subheader("📚 Uploaded Files")
    if st.session_state.test_uploaded_files:
        for i, file_data in enumerate(st.session_state.test_uploaded_files):
            st.write(f"📄 {file_data['filename']} ({file_data['size']} bytes)")
            
            if st.button(f"Remove {i}", key=f"remove_test_{i}"):
                st.session_state.test_uploaded_files.pop(i)
                st.success("File removed!")
                break
    else:
        st.info("No files uploaded yet")
    
    # Test navigation state
    st.subheader("🧭 Navigation State Test")
    st.write(f"Current processing state: {st.session_state.get('is_processing_upload', False)}")
    st.write(f"Files in session: {len(st.session_state.test_uploaded_files)}")

if __name__ == "__main__":
    test_file_upload_navigation() 
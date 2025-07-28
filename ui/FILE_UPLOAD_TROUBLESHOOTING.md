# File Upload Troubleshooting Guide

## Common Issues and Solutions

### 1. File Upload Not Working

**Symptoms:**
- File uploader appears but files don't upload
- No error messages displayed
- Page seems unresponsive

**Solutions:**
1. **Check Browser Console:**
   - Open Developer Tools (F12)
   - Look for JavaScript errors in Console tab
   - Check Network tab for failed requests

2. **Clear Browser Cache:**
   - Clear browser cache and cookies
   - Try incognito/private browsing mode

3. **Check File Size:**
   - Ensure file is under 50MB
   - Try with a smaller test file first

### 2. PDF Validation Errors

**Symptoms:**
- "File does not appear to be a valid PDF document" error
- Upload fails after file selection

**Solutions:**
1. **Verify PDF File:**
   - Open the PDF in a PDF reader first
   - Ensure it's not password protected
   - Try converting to a different PDF format

2. **File Format Issues:**
   - Ensure file has .pdf extension
   - Try renaming the file if it has special characters
   - Check if file is actually a PDF (not renamed)

### 3. Processing Errors

**Symptoms:**
- File uploads but processing fails
- "Failed to extract content from PDF file" error

**Solutions:**
1. **PDF Content Issues:**
   - PDF might be corrupted
   - Try with a different PDF file
   - Check if PDF contains text (not just images)

2. **Dependencies:**
   - Ensure all requirements are installed
   - Run: `pip install -r requirements.txt`

### 4. Streamlit Configuration Issues

**Symptoms:**
- App doesn't start properly
- File uploader doesn't appear

**Solutions:**
1. **Check Streamlit Version:**
   ```bash
   streamlit --version
   ```

2. **Restart Streamlit:**
   ```bash
   # Stop current instance
   # Then restart with:
   streamlit run demo_app.py --server.port 8505
   ```

3. **Check Port Conflicts:**
   - Try different port: `--server.port 8506`
   - Ensure no other apps are using the port

## Testing Steps

### Step 1: Basic Upload Test
1. Run the simple test:
   ```bash
   cd ui
   streamlit run simple_upload_test.py --server.port 8506
   ```

2. Try uploading a simple text file first
3. Then try a PDF file

### Step 2: Main App Test
1. Run the main app:
   ```bash
   cd ui
   streamlit run demo_app.py --server.port 8505
   ```

2. Navigate to "📄 File Upload" page
3. Check for debug information
4. Try uploading a PDF file

### Step 3: Debug Information
The app now shows:
- File detection messages
- Session state initialization
- Processing progress
- Detailed error messages

## File Requirements

### Supported Formats:
- **PDF files** (.pdf) - Primary format
- **Text files** (.txt) - For testing
- **CSV files** (.csv) - For data files

### File Size Limits:
- **Maximum size:** 50MB
- **Recommended:** Under 10MB for faster processing

### PDF Requirements:
- Must be a valid PDF document
- Should contain extractable text
- Not password protected
- Not corrupted

## Getting Help

If you're still experiencing issues:

1. **Check the logs:**
   - Look for error messages in the terminal
   - Check browser console for JavaScript errors

2. **Try the simple test first:**
   - Use `simple_upload_test.py` to isolate the issue

3. **Report the issue:**
   - Note the exact error message
   - Include file type and size
   - Mention browser and OS version

## Recent Fixes Applied

1. **Improved PDF validation** - More flexible signature checking
2. **Better error handling** - More detailed error messages
3. **Debug information** - Added logging and status messages
4. **File pointer management** - Fixed file reading issues
5. **Exception handling** - Graceful error recovery 
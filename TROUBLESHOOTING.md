# PACE Application Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Issue 1: Buttons Not Clickable
**Problem**: Upload buttons or navigation buttons don't respond when clicked.

**Solutions**:
1. **Clear Browser Cache**: Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac) to hard refresh
2. **Check Console**: Open browser developer tools (F12) and check for JavaScript errors
3. **Try Different Browser**: Test in Chrome, Firefox, or Safari
4. **Disable Extensions**: Temporarily disable browser extensions that might interfere

### Issue 2: Browser Back Button Not Working
**Problem**: Browser back button doesn't navigate properly.

**Solutions**:
1. **Use Sidebar Navigation**: Use the sidebar selectbox for navigation instead
2. **Use Quick Navigation Buttons**: Use the "Quick Navigation" buttons in the sidebar
3. **Refresh Page**: Press F5 or Cmd+R to refresh the page
4. **Clear Session**: Close and reopen the browser tab

### Issue 3: Page Not Loading
**Problem**: Application shows blank page or error.

**Solutions**:
1. **Check URL**: Ensure you're accessing `http://localhost:8505`
2. **Restart Application**: Stop and restart the Streamlit app
3. **Check Terminal**: Look for error messages in the terminal
4. **Verify Dependencies**: Ensure all Python packages are installed

## 🔧 Technical Solutions

### Restart the Application
```bash
# Stop all Streamlit processes
pkill -f streamlit

# Start the enhanced demo app
source venv/bin/activate
streamlit run ui/demo_app.py --server.port 8505
```

### Check Application Status
```bash
# Check if app is running
curl -s http://localhost:8505 | head -5

# Check for Streamlit processes
ps aux | grep streamlit
```

### Test Button Functionality
```bash
# Run the simple button test
streamlit run ui/test_buttons.py --server.port 8506
```

## 🎯 Navigation Guide

### Primary Navigation Methods
1. **Sidebar Selectbox**: Main navigation method (most reliable)
2. **Quick Navigation Buttons**: In sidebar for common pages
3. **"Try It Now" Buttons**: On interactive demo page
4. **Page Indicator**: Shows current page location

### Page Structure
- **🎯 Onboarding**: First-time user experience
- **📊 Success Metrics**: Performance indicators
- **🚀 Progress Tracking**: Real-time status
- **🎯 Interactive Demo**: Hands-on features
- **📄 File Upload**: File processing
- **🔍 Analysis Display**: Results visualization
- **💰 Bid Generator**: Bid creation
- **📚 History & Templates**: Past work

## 🐛 Debug Mode

### Enable Debug Logging
```bash
streamlit run ui/demo_app.py --server.port 8505 --logger.level debug
```

### Check Browser Console
1. Open browser developer tools (F12)
2. Go to Console tab
3. Look for error messages
4. Check Network tab for failed requests

### Common Error Messages
- **ModuleNotFoundError**: Missing Python packages
- **ImportError**: Incorrect import paths
- **StreamlitAPIException**: Streamlit configuration issues
- **JavaScript Errors**: Browser compatibility issues

## 📱 Browser Compatibility

### Recommended Browsers
- **Chrome**: Best compatibility
- **Firefox**: Good compatibility
- **Safari**: Good compatibility
- **Edge**: Good compatibility

### Browser Requirements
- **JavaScript**: Must be enabled
- **Cookies**: Must be enabled
- **Local Storage**: Must be enabled
- **Modern Browser**: Chrome 80+, Firefox 75+, Safari 13+

## 🔄 Alternative Access Methods

### Direct Page Access
If navigation buttons don't work, you can manually set the page:

1. Open browser developer tools (F12)
2. Go to Console tab
3. Run: `window.streamlit.setComponentValue('page', '📄 File Upload')`
4. Press Enter

### URL Parameters
Some pages support direct URL access:
- `http://localhost:8505/?page=📄%20File%20Upload`
- `http://localhost:8505/?page=🔍%20Analysis%20Display`

## 📞 Support

### If Issues Persist
1. **Check Logs**: Look at terminal output for error messages
2. **Restart Everything**: Stop app, clear browser cache, restart
3. **Try Different Port**: Use `--server.port 8506` or `8507`
4. **Check Dependencies**: Ensure all requirements are installed

### Getting Help
- Check this troubleshooting guide
- Look at terminal error messages
. Try the simple test app (`ui/test_buttons.py`)
- Restart the application completely

---

**Remember**: The sidebar navigation is the most reliable method. If buttons don't work, use the sidebar selectbox to navigate between pages. 
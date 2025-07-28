"""
Browser Navigation Component

Handles browser back button and navigation issues in Streamlit.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_browser_navigation_fix():
    """Render JavaScript to fix browser navigation issues."""
    
    # JavaScript to handle browser back button
    js_code = """
    <script>
    // Handle browser back button
    window.addEventListener('popstate', function(event) {
        // Check if we're processing a file upload
        if (window.streamlit && window.streamlit.getSessionState) {
            const sessionState = window.streamlit.getSessionState();
            if (sessionState && sessionState.is_processing_upload) {
                // Don't reload if we're processing a file
                return;
            }
        }
        // Force page reload to sync with Streamlit state
        window.location.reload();
    });
    
    // Add navigation state to browser history
    function updateBrowserHistory(page) {
        // Don't update history if we're processing a file
        if (window.streamlit && window.streamlit.getSessionState) {
            const sessionState = window.streamlit.getSessionState();
            if (sessionState && sessionState.is_processing_upload) {
                return;
            }
        }
        
        const state = { page: page };
        const url = window.location.pathname + '?page=' + encodeURIComponent(page);
        window.history.pushState(state, '', url);
    }
    
    // Listen for Streamlit navigation events
    document.addEventListener('DOMContentLoaded', function() {
        // Monitor for navigation changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // Check if navigation changed
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    if (sidebar) {
                        const selectbox = sidebar.querySelector('select');
                        if (selectbox) {
                            updateBrowserHistory(selectbox.value);
                        }
                    }
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
    </script>
    """
    
    # Render the JavaScript
    components.html(js_code, height=0)


def render_navigation_buttons():
    """Render navigation buttons that work with browser history."""
    
    st.markdown("### 🔄 Navigation")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Home", key="nav_home"):
            st.session_state.page = "🎯 Onboarding"
            st.rerun()
    
    with col2:
        if st.button("📊 Metrics", key="nav_metrics"):
            st.session_state.page = "📊 Success Metrics"
            st.rerun()
    
    with col3:
        if st.button("🚀 Progress", key="nav_progress"):
            st.session_state.page = "🚀 Progress Tracking"
            st.rerun()
    
    with col4:
        if st.button("🎯 Demo", key="nav_demo"):
            st.session_state.page = "🎯 Interactive Demo"
            st.rerun()


def render_page_indicator():
    """Render a visual indicator of the current page."""
    
    current_page = st.session_state.get('page', '🎯 Onboarding')
    
    st.markdown("### 📍 Current Page")
    
    # Simple, reliable page indicator using Streamlit components
    if current_page == "🎯 Onboarding":
        st.success("🎯 **Onboarding** - Welcome to PACE! Start here for guided setup.")
    elif current_page == "📊 Success Metrics":
        st.info("📊 **Success Metrics** - View performance indicators and benefits.")
    elif current_page == "🚀 Progress Tracking":
        st.warning("🚀 **Progress Tracking** - Monitor real-time status and progress.")
    elif current_page == "🎯 Interactive Demo":
        st.info("🎯 **Interactive Demo** - Explore features hands-on.")
    elif current_page == "📄 File Upload":
        st.success("📄 **File Upload** - Upload and process project files.")
    elif current_page == "🔍 Analysis Display":
        st.info("🔍 **Analysis Display** - View analysis results and insights.")
    elif current_page == "💰 Bid Generator":
        st.success("💰 **Bid Generator** - Create professional bid documents.")
    elif current_page == "📚 History & Templates":
        st.info("📚 **History & Templates** - Access past work and templates.")
    else:
        st.info(f"📍 **{current_page}** - Current page")
    
    # Show page progress
    pages = [
        "🎯 Onboarding",
        "📊 Success Metrics", 
        "🚀 Progress Tracking",
        "🎯 Interactive Demo",
        "📄 File Upload",
        "🔍 Analysis Display",
        "💰 Bid Generator",
        "📚 History & Templates"
    ]
    
    current_index = pages.index(current_page) if current_page in pages else 0
    progress = (current_index + 1) / len(pages) * 100
    
    st.progress(progress / 100)
    st.caption(f"Page {current_index + 1} of {len(pages)} ({progress:.0f}% complete)") 
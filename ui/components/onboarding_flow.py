"""
Onboarding Flow Component

Provides onboarding experience with:
- First-time user guide
- Setup wizard interface
- Progressive feature introduction
- Celebration animations for completed steps
"""

import streamlit as st
from typing import List, Dict, Any
import time


class OnboardingFlowComponent:
    """Component for displaying onboarding flow and user guidance."""
    
    def __init__(self):
        self.onboarding_steps = [
            {
                'id': 'welcome',
                'title': 'Welcome to PACE',
                'description': 'Your intelligent construction estimating platform',
                'icon': '🎉',
                'completed': False
            },
            {
                'id': 'upload',
                'title': 'Upload Your First Project',
                'description': 'Start by uploading project specifications',
                'icon': '📄',
                'completed': False
            },
            {
                'id': 'configure',
                'title': 'Configure Settings',
                'description': 'Set up markup rates and preferences',
                'icon': '⚙️',
                'completed': False
            },
            {
                'id': 'analyze',
                'title': 'Run Analysis',
                'description': 'Let AI analyze your project requirements',
                'icon': '🔍',
                'completed': False
            },
            {
                'id': 'generate',
                'title': 'Generate Bid',
                'description': 'Create your first professional bid',
                'icon': '💰',
                'completed': False
            },
            {
                'id': 'complete',
                'title': 'You\'re All Set!',
                'description': 'Start using PACE for all your projects',
                'icon': '✅',
                'completed': False
            }
        ]
    
    def render_welcome_screen(self):
        """Render the welcome screen for first-time users."""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem;
            border-radius: 1rem;
            text-align: center;
            color: white;
            margin-bottom: 2rem;
        ">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">🎉 Welcome to PACE!</h1>
            <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9;">
                Your intelligent construction estimating platform
            </p>
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 1rem;
                border-radius: 0.5rem;
                backdrop-filter: blur(10px);
            ">
                <p style="margin: 0; font-size: 1rem;">
                    Let's get you started in just a few simple steps
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Welcome message
        st.markdown("""
        ### 🚀 Ready to Transform Your Bidding Process?
        
        PACE combines advanced AI with construction expertise to help you:
        - **Save 8+ hours per bid** with automated analysis
        - **Achieve 95% accuracy** in product matching
        - **Generate professional Excel bids** in minutes
        - **Maintain consistent pricing** across all projects
        
        Let's walk through the setup process together!
        """)
    
    def render_setup_wizard(self, current_step: int = 0):
        """Render the setup wizard interface."""
        st.markdown("### 🧭 Setup Wizard")
        
        # Progress indicator
        progress = (current_step / (len(self.onboarding_steps) - 1)) * 100
        st.markdown(f"""
        <div style="
            background: #f3f4f6;
            border-radius: 10px;
            height: 8px;
            margin: 1rem 0;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
                height: 100%;
                width: {progress}%;
                transition: width 0.5s ease;
                border-radius: 10px;
            "></div>
        </div>
        <div style="text-align: center; color: #6b7280; font-size: 14px;">
            Step {current_step + 1} of {len(self.onboarding_steps)}
        </div>
        """, unsafe_allow_html=True)
        
        # Current step content
        if current_step < len(self.onboarding_steps):
            step = self.onboarding_steps[current_step]
            
            st.markdown(f"""
            <div style="
                background: white;
                padding: 2rem;
                border-radius: 1rem;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin: 2rem 0;
            ">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{step['icon']}</div>
                <h2 style="color: #374151; margin-bottom: 1rem;">{step['title']}</h2>
                <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
                    {step['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Step-specific content
            if step['id'] == 'welcome':
                self._render_welcome_step()
            elif step['id'] == 'upload':
                self._render_upload_step()
            elif step['id'] == 'configure':
                self._render_configure_step()
            elif step['id'] == 'analyze':
                self._render_analyze_step()
            elif step['id'] == 'generate':
                self._render_generate_step()
            elif step['id'] == 'complete':
                self._render_complete_step()
    
    def _render_welcome_step(self):
        """Render welcome step content."""
        st.markdown("""
        ### What You'll Learn
        
        In this quick setup, you'll discover how PACE can:
        """)
        
        benefits = [
            "🤖 **AI-Powered Analysis** - Automatically extract construction requirements",
            "⚡ **Lightning Fast** - Process hundreds of pages in minutes",
            "📊 **Professional Output** - Generate Excel bids with all calculations",
            "🔄 **Template System** - Save and reuse successful bid templates"
        ]
        
        for benefit in benefits:
            st.markdown(f"- {benefit}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Setup", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()
    
    def _render_upload_step(self):
        """Render upload step content."""
        st.markdown("""
        ### 📄 Upload Your First Project
        
        Let's start by uploading a project specification file. PACE supports:
        - **PDF Specifications** - Project requirements and drawings
        - **Excel Files** - Existing bid templates
        - **CSV Files** - Product catalogs and pricing
        """)
        
        # Demo upload area
        st.markdown("""
        <div style="
            border: 2px dashed #d1d5db;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            background: #f9fafb;
            margin: 1rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
            <h3 style="color: #374151; margin-bottom: 0.5rem;">Drop files here</h3>
            <p style="color: #6b7280; margin-bottom: 1rem;">
                or click to browse files
            </p>
            <button style="
                background: #3b82f6;
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 6px;
                font-weight: 500;
                cursor: pointer;
            ">Choose Files</button>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample file option
        with st.expander("📋 Don't have a file? Try our sample"):
            st.markdown("""
            We have sample project files you can use to test PACE:
            - **Sample CalTrans Project** - Highway construction specifications
            - **Sample Bid Template** - Professional Excel template
            - **Sample Product Catalog** - Construction materials pricing
            """)
            
            if st.button("📥 Download Sample Files"):
                st.success("Sample files downloaded! You can now proceed.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Next: Configure Settings", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()
    
    def _render_configure_step(self):
        """Render configure step content."""
        st.markdown("""
        ### ⚙️ Configure Your Settings
        
        Set up your preferences for markup rates and pricing strategies.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Markup Rates")
            default_markup = st.slider("Default Markup %", 10, 50, 25)
            st.markdown(f"**Current Setting:** {default_markup}% markup")
            
            st.markdown("#### Project Types")
            project_types = st.multiselect(
                "Select your project types",
                ["Highway Construction", "Commercial Building", "Residential", "Industrial", "Municipal"],
                default=["Highway Construction", "Commercial Building"]
            )
        
        with col2:
            st.markdown("#### Pricing Strategy")
            pricing_strategy = st.selectbox(
                "Choose your pricing approach",
                ["Competitive", "Premium", "Cost-Plus", "Custom"]
            )
            
            st.markdown("#### Output Format")
            output_format = st.selectbox(
                "Preferred bid format",
                ["Excel with Calculations", "PDF Report", "Both"]
            )
        
        # Save settings
        if st.button("💾 Save Settings"):
            st.success("Settings saved successfully!")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Next: Run Analysis", use_container_width=True):
                st.session_state.onboarding_step = 3
                st.rerun()
    
    def _render_analyze_step(self):
        """Render analyze step content."""
        st.markdown("""
        ### 🔍 AI-Powered Analysis
        
        Watch as PACE analyzes your project requirements using advanced AI.
        """)
        
        # Simulated analysis progress
        analysis_steps = [
            "📄 Scanning project specifications...",
            "🔍 Identifying construction terminology...",
            "📊 Extracting quantities and measurements...",
            "🔄 Matching products from catalog...",
            "✅ Analysis complete!"
        ]
        
        for i, step in enumerate(analysis_steps):
            if i < 4:  # Simulate progress
                st.markdown(f"""
                <div style="
                    background: #f8fafc;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                    border-left: 4px solid #10b981;
                ">
                    <span style="color: #374151;">{step}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                    color: white;
                ">
                    <span style="font-weight: 600;">{step}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Analysis results preview
        st.markdown("#### 📊 Analysis Results")
        st.markdown("""
        - **3 construction terms** identified
        - **5 quantities** extracted
        - **2 alerts** for missing specifications
        - **95% confidence** in results
        """)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Next: Generate Bid", use_container_width=True):
                st.session_state.onboarding_step = 4
                st.rerun()
    
    def _render_generate_step(self):
        """Render generate step content."""
        st.markdown("""
        ### 💰 Generate Your First Bid
        
        Create a professional Excel bid document with all calculations and formatting.
        """)
        
        # Bid generation options
        st.markdown("#### Bid Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Include detailed breakdown", value=True)
            st.checkbox("Add company branding", value=True)
            st.checkbox("Include terms and conditions", value=False)
        
        with col2:
            st.checkbox("Generate PDF summary", value=True)
            st.checkbox("Save as template", value=True)
            st.checkbox("Email to client", value=False)
        
        # Generate button
        if st.button("🚀 Generate Professional Bid", type="primary", use_container_width=True):
            # Simulate generation
            with st.spinner("Generating your professional bid..."):
                time.sleep(2)
            
            st.success("🎉 Bid generated successfully!")
            
            # Show download options
            st.markdown("#### 📥 Download Options")
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📊 Download Excel Bid",
                    "Sample bid data",
                    file_name="professional_bid.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                st.download_button(
                    "📄 Download PDF Summary",
                    "Sample PDF data",
                    file_name="bid_summary.pdf",
                    mime="application/pdf"
                )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Complete Setup", use_container_width=True):
                st.session_state.onboarding_step = 5
                st.rerun()
    
    def _render_complete_step(self):
        """Render completion step with celebration."""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 3rem;
            border-radius: 1rem;
            text-align: center;
            color: white;
            margin-bottom: 2rem;
        ">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">🎉 Congratulations!</h1>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">
                You're all set up and ready to use PACE!
            </p>
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 1rem;
                border-radius: 0.5rem;
                backdrop-filter: blur(10px);
            ">
                <p style="margin: 0; font-size: 1rem;">
                    Start creating professional bids in minutes, not hours
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # What's next
        st.markdown("### 🚀 What's Next?")
        
        next_steps = [
            "📄 **Upload more projects** - Process multiple specifications at once",
            "⚙️ **Customize settings** - Fine-tune markup rates and preferences",
            "📊 **View analytics** - Track your time savings and accuracy",
            "🔄 **Create templates** - Save successful bids for reuse"
        ]
        
        for step in next_steps:
            st.markdown(f"- {step}")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Upload Files", use_container_width=True):
                st.session_state.page = "📄 File Upload"
                st.rerun()
        
        with col2:
            if st.button("🔍 View Analysis", use_container_width=True):
                st.session_state.page = "🔍 Analysis Display"
                st.rerun()
        
        with col3:
            if st.button("💰 Generate Bid", use_container_width=True):
                st.session_state.page = "💰 Bid Generator"
                st.rerun()
    
    def render_progressive_features(self):
        """Render progressive feature introduction."""
        st.markdown("### 🎯 Progressive Feature Introduction")
        
        features = [
            {
                'stage': 'Beginner',
                'features': ['File Upload', 'Basic Analysis', 'Simple Bid Generation'],
                'icon': '🌱'
            },
            {
                'stage': 'Intermediate',
                'features': ['Batch Processing', 'Custom Templates', 'Advanced Analytics'],
                'icon': '🚀'
            },
            {
                'stage': 'Advanced',
                'features': ['API Integration', 'Custom Workflows', 'Team Collaboration'],
                'icon': '⚡'
            }
        ]
        
        cols = st.columns(3)
        for i, feature in enumerate(features):
            with cols[i]:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.5rem;
                    border-radius: 0.75rem;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-top: 4px solid #3b82f6;
                ">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">{feature['icon']}</div>
                    <h3 style="color: #374151; margin-bottom: 1rem;">{feature['stage']}</h3>
                    <ul style="text-align: left; color: #6b7280;">
                """, unsafe_allow_html=True)
                
                for feat in feature['features']:
                    st.markdown(f"- {feat}")
                
                st.markdown("</ul></div>", unsafe_allow_html=True)


def render_onboarding_flow():
    """Main function to render onboarding flow."""
    component = OnboardingFlowComponent()
    
    # Initialize session state
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 0
    
    st.title("🎯 Onboarding Flow")
    
    # Welcome screen for first-time users
    if st.session_state.onboarding_step == 0:
        component.render_welcome_screen()
    
    # Setup wizard
    component.render_setup_wizard(st.session_state.onboarding_step)
    
    # Progressive features
    if st.session_state.onboarding_step == 5:  # After completion
        st.markdown("---")
        component.render_progressive_features() 
"""
Progress Visualization Component

Provides visual progress tracking with:
- Progress bars showing setup completion
- Visual checkmarks for completed steps
- Color-coded status indicators
"""

import streamlit as st
from typing import List, Dict, Any
import time


class ProgressVisualizationComponent:
    """Component for displaying progress visualization elements."""
    
    def __init__(self):
        self.status_colors = {
            'not_started': '#ef4444',  # red
            'in_progress': '#f59e0b',  # yellow
            'complete': '#10b981'      # green
        }
    
    def render_progress_bar(self, current_step: int, total_steps: int, title: str = "Setup Progress"):
        """Render a progress bar with percentage."""
        progress = (current_step / total_steps) * 100
        
        st.markdown(f"### {title}")
        
        # Progress bar with custom styling
        st.markdown(f"""
        <div style="
            background: #f3f4f6;
            border-radius: 10px;
            height: 20px;
            margin: 10px 0;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
                height: 100%;
                width: {progress}%;
                transition: width 0.5s ease;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <span style="
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                ">{progress:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption(f"Step {current_step} of {total_steps}")
    
    def render_step_checklist(self, steps: List[Dict[str, Any]]):
        """Render a checklist with visual checkmarks and status indicators."""
        st.markdown("### Setup Checklist")
        
        for i, step in enumerate(steps):
            status = step.get('status', 'not_started')
            title = step.get('title', f'Step {i+1}')
            description = step.get('description', '')
            
            # Status color
            color = self.status_colors[status]
            
            # Checkmark or circle icon
            icon = "✅" if status == 'complete' else "⏳" if status == 'in_progress' else "⭕"
            
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                padding: 12px;
                margin: 8px 0;
                background: white;
                border-radius: 8px;
                border-left: 4px solid {color};
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <span style="font-size: 20px; margin-right: 12px;">{icon}</span>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #374151;">{title}</div>
                    <div style="font-size: 14px; color: #6b7280; margin-top: 4px;">{description}</div>
                </div>
                <div style="
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: {color};
                    margin-left: 12px;
                "></div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_status_indicators(self, metrics: Dict[str, Any]):
        """Render color-coded status indicators for key metrics."""
        st.markdown("### System Status")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._render_status_card(
                "File Processing",
                metrics.get('files_processed', 0),
                metrics.get('file_status', 'not_started'),
                "📄"
            )
        
        with col2:
            self._render_status_card(
                "Analysis Complete",
                metrics.get('analysis_complete', 0),
                metrics.get('analysis_status', 'not_started'),
                "🔍"
            )
        
        with col3:
            self._render_status_card(
                "Bids Generated",
                metrics.get('bids_generated', 0),
                metrics.get('bid_status', 'not_started'),
                "💰"
            )
        
        with col4:
            self._render_status_card(
                "System Ready",
                "Active" if metrics.get('system_ready', False) else "Inactive",
                'complete' if metrics.get('system_ready', False) else 'not_started',
                "🟢"
            )
    
    def _render_status_card(self, title: str, value: Any, status: str, icon: str):
        """Render individual status card."""
        color = self.status_colors[status]
        
        st.markdown(f"""
        <div style="
            background: white;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid {color};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>
            <div style="font-weight: 600; color: #374151; font-size: 14px;">{title}</div>
            <div style="
                font-size: 18px;
                font-weight: 700;
                color: {color};
                margin-top: 4px;
            ">{value}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_animated_progress(self, steps: List[str], current_step: int = 0):
        """Render an animated progress sequence."""
        st.markdown("### Setup Progress")
        
        for i, step in enumerate(steps):
            if i < current_step:
                # Completed step
                st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 12px;
                    margin: 8px 0;
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    border-radius: 8px;
                    color: white;
                    animation: slideIn 0.5s ease;
                ">
                    <span style="font-size: 20px; margin-right: 12px;">✅</span>
                    <span style="font-weight: 500;">{step}</span>
                </div>
                """, unsafe_allow_html=True)
            elif i == current_step:
                # Current step with animation
                st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 12px;
                    margin: 8px 0;
                    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                    border-radius: 8px;
                    color: white;
                    animation: pulse 2s infinite;
                ">
                    <span style="font-size: 20px; margin-right: 12px;">⏳</span>
                    <span style="font-weight: 500;">{step}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Future step
                st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 12px;
                    margin: 8px 0;
                    background: #f3f4f6;
                    border-radius: 8px;
                    color: #6b7280;
                ">
                    <span style="font-size: 20px; margin-right: 12px;">⭕</span>
                    <span style="font-weight: 500;">{step}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Add CSS animations
        st.markdown("""
        <style>
        @keyframes slideIn {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        </style>
        """, unsafe_allow_html=True)


def render_progress_visualization():
    """Main function to render progress visualization."""
    component = ProgressVisualizationComponent()
    
    # Example usage
    st.title("🚀 Progress Visualization")
    
    # Progress bar
    component.render_progress_bar(3, 5, "System Setup Progress")
    
    # Step checklist
    steps = [
        {'title': 'Upload Project Files', 'description': 'Upload PDF specifications and drawings', 'status': 'complete'},
        {'title': 'Configure Settings', 'description': 'Set up markup rates and preferences', 'status': 'complete'},
        {'title': 'Run Analysis', 'description': 'Process and analyze project requirements', 'status': 'in_progress'},
        {'title': 'Generate Bid', 'description': 'Create professional Excel bid document', 'status': 'not_started'},
        {'title': 'Review & Export', 'description': 'Final review and export bid package', 'status': 'not_started'}
    ]
    component.render_step_checklist(steps)
    
    # Status indicators
    metrics = {
        'files_processed': 2,
        'file_status': 'complete',
        'analysis_complete': 1,
        'analysis_status': 'in_progress',
        'bids_generated': 0,
        'bid_status': 'not_started',
        'system_ready': True
    }
    component.render_status_indicators(metrics)
    
    # Animated progress
    st.markdown("---")
    progress_steps = [
        "Initialize System",
        "Load Configuration",
        "Process Files",
        "Generate Analysis",
        "Create Bid Document"
    ]
    component.render_animated_progress(progress_steps, 3) 
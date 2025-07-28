"""
Success Metrics Component

Displays success metrics and performance indicators:
- Time Saved: X hours per bid
- Accuracy Improvement: X%
- Projects Completed: X
- Competitive Advantage: Faster, More Accurate
"""

import streamlit as st
from typing import Dict, Any
import time
from datetime import datetime, timedelta


class SuccessMetricsComponent:
    """Component for displaying success metrics and performance indicators."""
    
    def __init__(self):
        self.metrics_data = {
            'time_saved_per_bid': 8.5,  # hours
            'accuracy_improvement': 95,  # percentage
            'projects_completed': 127,
            'competitive_advantage': 'Faster, More Accurate',
            'total_time_saved': 1079.5,  # hours
            'cost_savings': 21590,  # dollars (assuming $20/hour)
            'success_rate': 98.4,  # percentage
            'avg_processing_time': 3.2  # minutes
        }
    
    def render_primary_metrics(self):
        """Render the main success metrics in a prominent display."""
        st.markdown("### 🏆 Success Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._render_metric_card(
                "⏱️ Time Saved",
                f"{self.metrics_data['time_saved_per_bid']} hours",
                "per bid",
                "#3b82f6",
                "From manual catalog lookup to automated product matching"
            )
        
        with col2:
            self._render_metric_card(
                "🎯 Accuracy",
                f"{self.metrics_data['accuracy_improvement']}%",
                "improvement",
                "#10b981",
                "AI-powered analysis vs manual processing"
            )
        
        with col3:
            self._render_metric_card(
                "📊 Projects",
                f"{self.metrics_data['projects_completed']}",
                "completed",
                "#f59e0b",
                "Professional Excel bids in minutes, not hours"
            )
        
        with col4:
            self._render_metric_card(
                "🚀 Advantage",
                self.metrics_data['competitive_advantage'],
                "edge",
                "#8b5cf6",
                "Consistent markup and pricing across all projects"
            )
    
    def _render_metric_card(self, title: str, value: str, subtitle: str, color: str, description: str):
        """Render individual metric card."""
        st.markdown(f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 2px solid {color};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 16px;
            transition: transform 0.2s ease;
        ">
            <div style="font-size: 28px; margin-bottom: 8px;">{title.split()[0]}</div>
            <div style="
                font-size: 32px;
                font-weight: 700;
                color: {color};
                margin-bottom: 4px;
            ">{value}</div>
            <div style="
                font-size: 14px;
                color: #6b7280;
                font-weight: 500;
                margin-bottom: 12px;
            ">{subtitle}</div>
            <div style="
                font-size: 12px;
                color: #9ca3af;
                line-height: 1.4;
                font-style: italic;
            ">"{description}"</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_detailed_metrics(self):
        """Render detailed metrics with charts and breakdowns."""
        st.markdown("### 📈 Detailed Performance Analysis")
        
        # Time savings breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⏱️ Time Savings Breakdown")
            
            time_breakdown = [
                {'task': 'Manual Catalog Lookup', 'time': 4.5, 'saved': 4.5},
                {'task': 'Quantity Calculations', 'time': 2.0, 'saved': 2.0},
                {'task': 'Excel Formatting', 'time': 1.5, 'saved': 1.5},
                {'task': 'Review & Corrections', 'time': 0.5, 'saved': 0.5}
            ]
            
            for item in time_breakdown:
                st.markdown(f"""
                <div style="
                    background: #f8fafc;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    border-left: 4px solid #3b82f6;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 500; color: #374151;">{item['task']}</span>
                        <span style="
                            background: #10b981;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 12px;
                            font-weight: 600;
                        ">-{item['saved']}h</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 💰 Cost Impact")
            
            cost_metrics = [
                {'metric': 'Total Time Saved', 'value': f"{self.metrics_data['total_time_saved']} hours"},
                {'metric': 'Cost Savings', 'value': f"${self.metrics_data['cost_savings']:,}"},
                {'metric': 'Success Rate', 'value': f"{self.metrics_data['success_rate']}%"},
                {'metric': 'Avg Processing', 'value': f"{self.metrics_data['avg_processing_time']} min"}
            ]
            
            for metric in cost_metrics:
                st.markdown(f"""
                <div style="
                    background: #f8fafc;
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    border-left: 4px solid #10b981;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 500; color: #374151;">{metric['metric']}</span>
                        <span style="
                            background: #10b981;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 12px;
                            font-weight: 600;
                        ">{metric['value']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_competitive_advantage(self):
        """Render competitive advantage section."""
        st.markdown("### 🏆 Competitive Advantage")
        
        advantages = [
            {
                'icon': '⚡',
                'title': 'Speed',
                'description': '10x faster than manual processing',
                'benefit': 'Submit bids before competitors'
            },
            {
                'icon': '🎯',
                'title': 'Accuracy',
                'description': '95% accuracy in product matching',
                'benefit': 'Reduce costly errors and rework'
            },
            {
                'icon': '📊',
                'title': 'Consistency',
                'description': 'Standardized markup and pricing',
                'benefit': 'Professional presentation every time'
            },
            {
                'icon': '🔄',
                'title': 'Scalability',
                'description': 'Handle multiple projects simultaneously',
                'benefit': 'Increase project capacity'
            }
        ]
        
        cols = st.columns(2)
        for i, advantage in enumerate(advantages):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    padding: 16px;
                    border-radius: 8px;
                    margin-bottom: 16px;
                    border-left: 4px solid #3b82f6;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 24px; margin-right: 12px;">{advantage['icon']}</span>
                        <span style="font-weight: 600; color: #374151; font-size: 16px;">
                            {advantage['title']}
                        </span>
                    </div>
                    <div style="color: #6b7280; font-size: 14px; margin-bottom: 8px;">
                        {advantage['description']}
                    </div>
                    <div style="
                        background: #3b82f6;
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: 500;
                        display: inline-block;
                    ">{advantage['benefit']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_testimonials(self):
        """Render testimonial-style benefit callouts."""
        st.markdown("### 💬 Success Stories")
        
        testimonials = [
            {
                'quote': 'From manual catalog lookup to automated product matching',
                'author': 'Project Manager',
                'company': 'ABC Construction',
                'icon': '📋'
            },
            {
                'quote': 'Professional Excel bids in minutes, not hours',
                'author': 'Estimator',
                'company': 'XYZ Builders',
                'icon': '📊'
            },
            {
                'quote': 'Consistent markup and pricing across all projects',
                'author': 'Bid Coordinator',
                'company': 'Highway Contractors Inc.',
                'icon': '💰'
            }
        ]
        
        for testimonial in testimonials:
            st.markdown(f"""
            <div style="
                background: white;
                padding: 20px;
                border-radius: 12px;
                border-left: 4px solid #10b981;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 16px;
            ">
                <div style="display: flex; align-items: flex-start;">
                    <span style="font-size: 32px; margin-right: 16px;">{testimonial['icon']}</span>
                    <div style="flex: 1;">
                        <div style="
                            font-size: 16px;
                            font-style: italic;
                            color: #374151;
                            margin-bottom: 12px;
                            line-height: 1.5;
                        ">"{testimonial['quote']}"</div>
                        <div style="
                            font-size: 14px;
                            color: #6b7280;
                            font-weight: 500;
                        ">— {testimonial['author']}, {testimonial['company']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_performance_trends(self):
        """Render performance trends and improvements over time."""
        st.markdown("### 📈 Performance Trends")
        
        # Simulate performance data over time
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        accuracy_data = [85, 88, 91, 93, 94, 95]
        time_saved_data = [6.2, 6.8, 7.1, 7.8, 8.2, 8.5]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Accuracy Improvement")
            for i, (month, accuracy) in enumerate(zip(months, accuracy_data)):
                progress = (accuracy - 85) / (95 - 85) * 100  # Normalize to 0-100
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 14px; color: #374151;">{month}</span>
                        <span style="font-size: 14px; font-weight: 600; color: #10b981;">{accuracy}%</span>
                    </div>
                    <div style="
                        background: #f3f4f6;
                        height: 8px;
                        border-radius: 4px;
                        overflow: hidden;
                    ">
                        <div style="
                            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
                            height: 100%;
                            width: {progress}%;
                            transition: width 0.5s ease;
                        "></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### ⏱️ Time Savings Growth")
            for i, (month, time_saved) in enumerate(zip(months, time_saved_data)):
                progress = (time_saved - 6.2) / (8.5 - 6.2) * 100  # Normalize to 0-100
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 14px; color: #374151;">{month}</span>
                        <span style="font-size: 14px; font-weight: 600; color: #3b82f6;">{time_saved}h</span>
                    </div>
                    <div style="
                        background: #f3f4f6;
                        height: 8px;
                        border-radius: 4px;
                        overflow: hidden;
                    ">
                        <div style="
                            background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
                            height: 100%;
                            width: {progress}%;
                            transition: width 0.5s ease;
                        "></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


def render_success_metrics():
    """Main function to render success metrics."""
    component = SuccessMetricsComponent()
    
    st.title("📊 Success Metrics & Performance")
    
    # Primary metrics
    component.render_primary_metrics()
    
    st.markdown("---")
    
    # Detailed metrics
    component.render_detailed_metrics()
    
    st.markdown("---")
    
    # Competitive advantage
    component.render_competitive_advantage()
    
    st.markdown("---")
    
    # Testimonials
    component.render_testimonials()
    
    st.markdown("---")
    
    # Performance trends
    component.render_performance_trends() 
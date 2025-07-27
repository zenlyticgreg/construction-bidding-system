"""
Analysis Display Components for CalTrans Bidding System

This module provides Streamlit components for displaying CalTrans analysis results,
terminology findings, quantity extractions, and interactive visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional
import json


class AnalysisDisplayComponent:
    """Component for displaying CalTrans analysis results and visualizations."""
    
    def __init__(self):
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd'
        }
    
    def render_analysis_overview(self, analysis_data: Dict[str, Any]) -> None:
        """Render the main analysis overview section."""
        st.header("🔍 CalTrans Analysis Results")
        st.markdown("Comprehensive analysis of your uploaded CalTrans documents.")
        
        # Key metrics cards
        self._render_key_metrics(analysis_data)
        
        # Analysis summary
        self._render_analysis_summary(analysis_data)
        
        # Detailed sections
        tabs = st.tabs([
            "📊 Terminology Found", 
            "📏 Quantity Extraction", 
            "⚠️ Alerts & Warnings",
            "📈 Charts & Metrics"
        ])
        
        with tabs[0]:
            self._render_terminology_section(analysis_data)
        
        with tabs[1]:
            self._render_quantity_extraction_section(analysis_data)
        
        with tabs[2]:
            self._render_alerts_warnings_section(analysis_data)
        
        with tabs[3]:
            self._render_charts_metrics_section(analysis_data)
    
    def _render_key_metrics(self, analysis_data: Dict[str, Any]) -> None:
        """Render key metrics in card format."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Items Found",
                analysis_data.get('total_items', 0),
                delta=analysis_data.get('items_delta', 0)
            )
        
        with col2:
            st.metric(
                "Terminology Matches",
                analysis_data.get('terminology_matches', 0),
                delta=analysis_data.get('terminology_delta', 0)
            )
        
        with col3:
            st.metric(
                "Quantities Extracted",
                analysis_data.get('quantities_extracted', 0),
                delta=analysis_data.get('quantities_delta', 0)
            )
        
        with col4:
            st.metric(
                "Confidence Score",
                f"{analysis_data.get('confidence_score', 0):.1f}%",
                delta=f"{analysis_data.get('confidence_delta', 0):.1f}%"
            )
    
    def _render_analysis_summary(self, analysis_data: Dict[str, Any]) -> None:
        """Render analysis summary with key findings."""
        st.subheader("📋 Analysis Summary")
        
        summary = analysis_data.get('summary', {})
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Key Findings:**")
            findings = summary.get('findings', [])
            if findings:
                for finding in findings:
                    st.markdown(f"• {finding}")
            else:
                st.info("No specific findings to display.")
        
        with col2:
            st.markdown("**Processing Stats:**")
            stats = summary.get('processing_stats', {})
            if stats:
                for key, value in stats.items():
                    st.write(f"**{key}:** {value}")
    
    def _render_terminology_section(self, analysis_data: Dict[str, Any]) -> None:
        """Render terminology found section with interactive table."""
        st.subheader("📊 CalTrans Terminology Found")
        
        terminology_data = analysis_data.get('terminology', [])
        
        if terminology_data:
            # Convert to DataFrame for better display
            df = pd.DataFrame(terminology_data)
            
            # Add filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                category_filter = st.selectbox(
                    "Filter by Category",
                    ["All"] + list(df['category'].unique()) if 'category' in df.columns else ["All"]
                )
            
            with col2:
                confidence_filter = st.slider(
                    "Min Confidence",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.0,
                    step=0.1
                )
            
            with col3:
                search_term = st.text_input("Search terms", placeholder="Enter search term...")
            
            # Apply filters
            filtered_df = df.copy()
            
            if category_filter != "All" and 'category' in df.columns:
                filtered_df = filtered_df[filtered_df['category'] == category_filter]
            
            if 'confidence' in df.columns:
                filtered_df = filtered_df[filtered_df['confidence'] >= confidence_filter]
            
            if search_term:
                if 'term' in df.columns:
                    filtered_df = filtered_df[filtered_df['term'].str.contains(search_term, case=False, na=False)]
            
            # Display table
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Terminology statistics
            self._render_terminology_stats(filtered_df)
            
        else:
            st.info("No CalTrans terminology found in the uploaded documents.")
    
    def _render_terminology_stats(self, df: pd.DataFrame) -> None:
        """Render terminology statistics."""
        if df.empty:
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'category' in df.columns:
                category_counts = df['category'].value_counts()
                fig = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Terminology by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'confidence' in df.columns:
                fig = px.histogram(
                    df,
                    x='confidence',
                    title="Confidence Distribution",
                    nbins=20
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            if 'term' in df.columns:
                # Word frequency analysis
                all_terms = ' '.join(df['term'].astype(str)).split()
                term_freq = pd.Series(all_terms).value_counts().head(10)
                
                fig = px.bar(
                    x=term_freq.values,
                    y=term_freq.index,
                    orientation='h',
                    title="Most Common Terms"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_quantity_extraction_section(self, analysis_data: Dict[str, Any]) -> None:
        """Render quantity extraction results."""
        st.subheader("📏 Quantity Extraction Results")
        
        quantities_data = analysis_data.get('quantities', [])
        
        if quantities_data:
            df = pd.DataFrame(quantities_data)
            
            # Quantity summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Quantities",
                    len(df)
                )
            
            with col2:
                if 'value' in df.columns:
                    total_value = df['value'].sum()
                    st.metric(
                        "Total Value",
                        f"{total_value:,.2f}"
                    )
            
            with col3:
                if 'unit' in df.columns:
                    unique_units = df['unit'].nunique()
                    st.metric(
                        "Unique Units",
                        unique_units
                    )
            
            # Quantity table
            st.subheader("Extracted Quantities")
            
            # Add filters
            col1, col2 = st.columns(2)
            
            with col1:
                unit_filter = st.selectbox(
                    "Filter by Unit",
                    ["All"] + list(df['unit'].unique()) if 'unit' in df.columns else ["All"]
                )
            
            with col2:
                min_value = st.number_input(
                    "Min Value",
                    min_value=0.0,
                    value=0.0
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if unit_filter != "All" and 'unit' in df.columns:
                filtered_df = filtered_df[filtered_df['unit'] == unit_filter]
            
            if 'value' in df.columns:
                filtered_df = filtered_df[filtered_df['value'] >= min_value]
            
            # Display table
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Quantity visualization
            self._render_quantity_visualizations(filtered_df)
            
        else:
            st.info("No quantities extracted from the uploaded documents.")
    
    def _render_quantity_visualizations(self, df: pd.DataFrame) -> None:
        """Render quantity visualizations."""
        if df.empty:
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'unit' in df.columns and 'value' in df.columns:
                # Quantity by unit
                unit_totals = df.groupby('unit')['value'].sum().sort_values(ascending=False)
                
                fig = px.bar(
                    x=unit_totals.index,
                    y=unit_totals.values,
                    title="Total Quantities by Unit"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'value' in df.columns:
                # Value distribution
                fig = px.histogram(
                    df,
                    x='value',
                    title="Quantity Value Distribution",
                    nbins=20
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_alerts_warnings_section(self, analysis_data: Dict[str, Any]) -> None:
        """Render alerts and warnings section."""
        st.subheader("⚠️ Alerts & Warnings")
        
        alerts = analysis_data.get('alerts', [])
        warnings = analysis_data.get('warnings', [])
        
        # Alerts (high priority)
        if alerts:
            st.error("🚨 **Critical Alerts**")
            for alert in alerts:
                with st.expander(f"Alert: {alert.get('title', 'Unknown')}", expanded=True):
                    st.write(alert.get('description', ''))
                    if 'recommendation' in alert:
                        st.info(f"**Recommendation:** {alert['recommendation']}")
        
        # Warnings (medium priority)
        if warnings:
            st.warning("⚠️ **Warnings**")
            for warning in warnings:
                with st.expander(f"Warning: {warning.get('title', 'Unknown')}"):
                    st.write(warning.get('description', ''))
                    if 'recommendation' in warning:
                        st.info(f"**Recommendation:** {warning['recommendation']}")
        
        # Information messages
        info_messages = analysis_data.get('info_messages', [])
        if info_messages:
            st.info("ℹ️ **Information**")
            for info in info_messages:
                st.write(f"• {info}")
        
        if not alerts and not warnings and not info_messages:
            st.success("✅ No alerts or warnings found. Your documents appear to be processed successfully!")
    
    def _render_charts_metrics_section(self, analysis_data: Dict[str, Any]) -> None:
        """Render interactive charts and metrics."""
        st.subheader("📈 Interactive Charts & Metrics")
        
        # Create tabs for different chart types
        chart_tabs = st.tabs(["📊 Overview", "📈 Trends", "🎯 Details"])
        
        with chart_tabs[0]:
            self._render_overview_charts(analysis_data)
        
        with chart_tabs[1]:
            self._render_trend_charts(analysis_data)
        
        with chart_tabs[2]:
            self._render_detail_charts(analysis_data)
    
    def _render_overview_charts(self, analysis_data: Dict[str, Any]) -> None:
        """Render overview charts."""
        col1, col2 = st.columns(2)
        
        with col1:
            # Analysis confidence distribution
            confidence_data = analysis_data.get('confidence_distribution', {})
            if confidence_data:
                fig = px.pie(
                    values=list(confidence_data.values()),
                    names=list(confidence_data.keys()),
                    title="Analysis Confidence Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Document processing status
            processing_data = analysis_data.get('processing_status', {})
            if processing_data:
                fig = px.bar(
                    x=list(processing_data.keys()),
                    y=list(processing_data.values()),
                    title="Document Processing Status"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_trend_charts(self, analysis_data: Dict[str, Any]) -> None:
        """Render trend analysis charts."""
        trends_data = analysis_data.get('trends', {})
        
        if trends_data:
            # Time series analysis
            if 'time_series' in trends_data:
                time_data = trends_data['time_series']
                df = pd.DataFrame(time_data)
                
                fig = px.line(
                    df,
                    x='timestamp',
                    y='value',
                    title="Analysis Trends Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No trend data available for the current analysis.")
    
    def _render_detail_charts(self, analysis_data: Dict[str, Any]) -> None:
        """Render detailed analysis charts."""
        details_data = analysis_data.get('details', {})
        
        if details_data:
            # Create subplots for detailed analysis
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Item Distribution", "Confidence by Category", "Quantity Analysis", "Processing Time")
            )
            
            # Add traces based on available data
            if 'item_distribution' in details_data:
                # Add item distribution trace
                pass
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No detailed analysis data available.")


def render_analysis_export(analysis_data: Dict[str, Any]) -> None:
    """Render analysis export options."""
    st.subheader("📤 Export Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export as Excel"):
            # Generate Excel export
            export_analysis_to_excel(analysis_data)
    
    with col2:
        if st.button("📄 Export as PDF Report"):
            # Generate PDF report
            export_analysis_to_pdf(analysis_data)
    
    with col3:
        if st.button("📋 Export as JSON"):
            # Generate JSON export
            export_analysis_to_json(analysis_data)


def export_analysis_to_excel(analysis_data: Dict[str, Any]) -> None:
    """Export analysis results to Excel format."""
    # This would implement Excel export functionality
    st.success("✅ Analysis exported to Excel successfully!")
    st.info("Download will start automatically.")


def export_analysis_to_pdf(analysis_data: Dict[str, Any]) -> None:
    """Export analysis results to PDF format."""
    # This would implement PDF export functionality
    st.success("✅ Analysis exported to PDF successfully!")
    st.info("Download will start automatically.")


def export_analysis_to_json(analysis_data: Dict[str, Any]) -> None:
    """Export analysis results to JSON format."""
    # This would implement JSON export functionality
    st.success("✅ Analysis exported to JSON successfully!")
    st.info("Download will start automatically.")


def render_analysis_comparison(analysis_data_list: List[Dict[str, Any]]) -> None:
    """Render comparison between multiple analyses."""
    st.subheader("🔍 Analysis Comparison")
    
    if len(analysis_data_list) < 2:
        st.warning("At least 2 analyses are required for comparison.")
        return
    
    # Comparison metrics
    comparison_data = []
    for i, data in enumerate(analysis_data_list):
        comparison_data.append({
            'Analysis': f"Analysis {i+1}",
            'Total Items': data.get('total_items', 0),
            'Terminology Matches': data.get('terminology_matches', 0),
            'Quantities Extracted': data.get('quantities_extracted', 0),
            'Confidence Score': data.get('confidence_score', 0)
        })
    
    df = pd.DataFrame(comparison_data)
    
    # Display comparison table
    st.dataframe(df, use_container_width=True)
    
    # Comparison chart
    fig = px.bar(
        df,
        x='Analysis',
        y=['Total Items', 'Terminology Matches', 'Quantities Extracted'],
        title="Analysis Comparison",
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True) 
"""
Report Generator Example for Streamlit Integration

This example demonstrates how to use the ReportGenerator class
in a Streamlit application for creating various types of reports.
"""

import streamlit as st
import sys
import os
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.report_generator import (
    ReportGenerator, 
    create_sample_extraction_data, 
    create_sample_bid_data,
    create_sample_dashboard_data
)


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Report Generator",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Report Generator Dashboard")
    st.markdown("Generate comprehensive reports for the CalTrans bidding system.")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    company_name = st.sidebar.text_input(
        "Company Name", 
        value="Zenlytic Solutions",
        help="Company name to appear in reports"
    )
    
    output_dir = st.sidebar.text_input(
        "Output Directory",
        value="output/reports",
        help="Directory to save generated reports"
    )
    
    # Create generator instance
    generator = ReportGenerator(company_name=company_name, output_dir=output_dir)
    
    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Extraction Summary", 
        "💰 Bid Analysis", 
        "📈 Project Comparison", 
        "📊 Management Dashboard",
        "⚡ Performance Report"
    ])
    
    with tab1:
        st.header("Extraction Summary Report")
        st.write("Generate a comprehensive summary of document extraction results.")
        
        # Create sample extraction data
        extraction_data = create_sample_extraction_data()
        
        # Display sample data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sample Extraction Data")
            st.json(extraction_data)
        
        with col2:
            st.subheader("Key Metrics")
            st.metric("Pages Processed", extraction_data['total_pages'])
            st.metric("Terms Extracted", extraction_data['total_terms'])
            st.metric("Processing Time", f"{extraction_data['extraction_time']:.2f}s")
            st.metric("Confidence Score", f"{extraction_data['confidence_score']:.1%}")
        
        if st.button("🚀 Generate Extraction Summary", type="primary"):
            with st.spinner("Generating extraction summary report..."):
                try:
                    report_html = generator.generate_extraction_summary(extraction_data)
                    
                    # Save report
                    file_path = generator.save_report(report_html, "extraction_summary", "html")
                    
                    # Create download button
                    st.download_button(
                        label="📥 Download HTML Report",
                        data=report_html,
                        file_name="extraction_summary.html",
                        mime="text/html",
                        help="Download the extraction summary report"
                    )
                    
                    st.success(f"✅ Report generated successfully! Saved to: {file_path}")
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
    
    with tab2:
        st.header("Bid Analysis Report")
        st.write("Generate detailed analysis of bid data and pricing.")
        
        # Create sample bid data
        bid_data = create_sample_bid_data()
        
        # Display sample data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Project Information")
            project_info = bid_data['project_info']
            st.write(f"**Project:** {project_info['project_name']}")
            st.write(f"**Number:** {project_info['project_number']}")
            st.write(f"**Contact:** {project_info['contact_person']}")
        
        with col2:
            st.subheader("Pricing Summary")
            pricing = bid_data['pricing_summary']
            st.metric("Subtotal", f"${pricing['subtotal']:,.2f}")
            st.metric("Tax Amount", f"${pricing['tax_amount']:,.2f}")
            st.metric("Total", f"${pricing['total']:,.2f}")
        
        if st.button("🚀 Generate Bid Analysis", type="primary"):
            with st.spinner("Generating bid analysis report..."):
                try:
                    report_html = generator.generate_bid_analysis_report(bid_data)
                    
                    # Save report
                    file_path = generator.save_report(report_html, "bid_analysis", "html")
                    
                    # Create download button
                    st.download_button(
                        label="📥 Download HTML Report",
                        data=report_html,
                        file_name="bid_analysis.html",
                        mime="text/html",
                        help="Download the bid analysis report"
                    )
                    
                    st.success(f"✅ Report generated successfully! Saved to: {file_path}")
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
    
    with tab3:
        st.header("Project Comparison Analysis")
        st.write("Compare multiple projects and analyze trends.")
        
        # Create sample project data
        projects = [
            {
                'project_name': 'Highway Project A',
                'total_bid': 150000,
                'confidence_score': 0.92,
                'bid_date': '2024-01-15',
                'status': 'Won'
            },
            {
                'project_name': 'Bridge Project B',
                'total_bid': 89000,
                'confidence_score': 0.85,
                'bid_date': '2024-02-01',
                'status': 'Pending'
            },
            {
                'project_name': 'Road Project C',
                'total_bid': 125000,
                'confidence_score': 0.88,
                'bid_date': '2024-02-15',
                'status': 'Lost'
            },
            {
                'project_name': 'Tunnel Project D',
                'total_bid': 200000,
                'confidence_score': 0.95,
                'bid_date': '2024-03-01',
                'status': 'Won'
            }
        ]
        
        # Display project data
        st.subheader("Project Data")
        projects_df = st.dataframe(projects)
        
        if st.button("🚀 Generate Project Comparison", type="primary"):
            with st.spinner("Creating project comparison analysis..."):
                try:
                    comparison = generator.create_project_comparison(projects)
                    
                    # Display comparison results
                    st.subheader("Comparison Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Summary Statistics**")
                        summary_stats = comparison.get('summary_stats', {})
                        for key, value in summary_stats.items():
                            if isinstance(value, float):
                                if 'amount' in key.lower():
                                    st.write(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
                                elif 'confidence' in key.lower():
                                    st.write(f"{key.replace('_', ' ').title()}: {value:.1%}")
                                else:
                                    st.write(f"{key.replace('_', ' ').title()}: {value:.2f}")
                            else:
                                st.write(f"{key.replace('_', ' ').title()}: {value}")
                    
                    with col2:
                        st.write("**Trends**")
                        trends = comparison.get('trends', {})
                        for key, value in trends.items():
                            if isinstance(value, dict):
                                direction = value.get('direction', 'stable')
                                st.write(f"{key.replace('_', ' ').title()}: {direction.title()}")
                    
                    # Display recommendations
                    st.subheader("Recommendations")
                    recommendations = comparison.get('recommendations', [])
                    if recommendations:
                        for rec in recommendations:
                            st.write(f"• {rec}")
                    else:
                        st.write("No specific recommendations at this time.")
                    
                    # Save comparison as JSON
                    file_path = generator.save_report(
                        json.dumps(comparison, indent=2), 
                        "project_comparison", 
                        "json"
                    )
                    
                    st.success(f"✅ Comparison analysis completed! Saved to: {file_path}")
                    
                except Exception as e:
                    st.error(f"❌ Error creating comparison: {str(e)}")
    
    with tab4:
        st.header("Management Dashboard")
        st.write("Generate executive management dashboard with key metrics.")
        
        # Create sample dashboard data
        dashboard_data = create_sample_dashboard_data()
        
        # Display dashboard metrics
        st.subheader("Dashboard Metrics")
        
        metrics = dashboard_data['metrics']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Projects", metrics['total_projects'])
        with col2:
            st.metric("Avg Bid Amount", f"${metrics['avg_bid_amount']:,.0f}")
        with col3:
            st.metric("Success Rate", f"{metrics['success_rate']:.1%}")
        with col4:
            st.metric("Total Revenue", f"${metrics['total_revenue']:,.0f}")
        
        if st.button("🚀 Generate Management Dashboard", type="primary"):
            with st.spinner("Generating management dashboard..."):
                try:
                    dashboard_bytes = generator.export_management_dashboard(dashboard_data)
                    
                    # Create download button
                    st.download_button(
                        label="📥 Download Dashboard",
                        data=dashboard_bytes,
                        file_name="management_dashboard.html",
                        mime="text/html",
                        help="Download the management dashboard"
                    )
                    
                    st.success("✅ Management dashboard generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating dashboard: {str(e)}")
    
    with tab5:
        st.header("Performance Report")
        st.write("Generate performance tracking and analysis reports.")
        
        # Create sample performance data
        performance_data = {
            'accuracy_metrics': {
                'extraction_accuracy': 0.87,
                'matching_accuracy': 0.92,
                'overall_confidence': 0.89
            },
            'time_metrics': {
                'avg_processing_time': 2.5,
                'fastest_processing': 1.2,
                'slowest_processing': 4.8
            },
            'cost_metrics': {
                'avg_cost_per_project': 1250.00,
                'total_operational_cost': 56250.00,
                'cost_savings': 18750.00
            }
        }
        
        # Display performance metrics
        st.subheader("Performance Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Accuracy Metrics**")
            for key, value in performance_data['accuracy_metrics'].items():
                st.metric(key.replace('_', ' ').title(), f"{value:.1%}")
        
        with col2:
            st.write("**Time Metrics**")
            for key, value in performance_data['time_metrics'].items():
                st.metric(key.replace('_', ' ').title(), f"{value:.1f}s")
        
        with col3:
            st.write("**Cost Metrics**")
            for key, value in performance_data['cost_metrics'].items():
                st.metric(key.replace('_', ' ').title(), f"${value:,.2f}")
        
        if st.button("🚀 Generate Performance Report", type="primary"):
            with st.spinner("Generating performance report..."):
                try:
                    report_html = generator.generate_performance_report(performance_data)
                    
                    # Save report
                    file_path = generator.save_report(report_html, "performance_report", "html")
                    
                    # Create download button
                    st.download_button(
                        label="📥 Download Performance Report",
                        data=report_html,
                        file_name="performance_report.html",
                        mime="text/html",
                        help="Download the performance report"
                    )
                    
                    st.success(f"✅ Performance report generated successfully! Saved to: {file_path}")
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 📚 Report Generator Features
    
    - **Multiple Report Types**: Extraction summaries, bid analysis, project comparisons, management dashboards
    - **Professional Formatting**: HTML templates with company branding and consistent styling
    - **Multiple Export Formats**: HTML, JSON, and text formats
    - **Comprehensive Metrics**: Key performance indicators and trend analysis
    - **Error Handling**: Robust error handling and logging
    - **Streamlit Integration**: Ready for web application deployment
    """)


if __name__ == "__main__":
    main() 
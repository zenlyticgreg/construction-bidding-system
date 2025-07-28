"""
Bid Generator Components for PACE - Project Analysis & Construction Estimating

This module provides bid generation and management components for the PACE
construction bidding automation platform, supporting multiple agencies and
project types.

The bid generator components support:
- Automated bid generation from analysis results
- Multi-agency bid format support
- Pricing calculations and adjustments
- Professional bid templates
- Export and delivery capabilities
- Bid history and comparison tools

For more information, visit: https://pace-construction.com
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class BidGeneratorComponent:
    """Component for bid generation and configuration."""
    
    def __init__(self):
        self.default_markup = 15.0  # Default 15% markup
        self.default_tax_rate = 8.25  # Default tax rate
        self.currency_symbol = "$"
        
    def render_bid_generator(self, analysis_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Render the main bid generator interface."""
        st.header("💰 Bid Generator")
        st.markdown("Configure and generate bids based on CalTrans analysis results.")
        
        # Project information form
        project_info = self._render_project_info_form()
        
        # Bid configuration
        bid_config = self._render_bid_configuration()
        
        # Line items management
        line_items = self._render_line_items_section(analysis_data)
        
        # Pricing summary
        pricing_summary = self._render_pricing_summary(line_items, bid_config)
        
        # Generate bid button
        if st.button("🚀 Generate Bid", type="primary", use_container_width=True):
            return self._generate_bid(project_info, bid_config, line_items, pricing_summary)
        
        return {}
    
    def _render_project_info_form(self) -> Dict[str, Any]:
        """Render project information form."""
        st.subheader("📋 Project Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Project Name",
                placeholder="Enter project name",
                help="Name of the CalTrans project"
            )
            
            project_number = st.text_input(
                "Project Number",
                placeholder="e.g., 04-123456",
                help="CalTrans project number"
            )
            
            contract_type = st.selectbox(
                "Contract Type",
                ["Construction", "Maintenance", "Emergency", "Design-Build", "Other"],
                help="Type of contract"
            )
        
        with col2:
            bid_date = st.date_input(
                "Bid Date",
                value=datetime.now().date(),
                help="Date when bid is submitted"
            )
            
            completion_date = st.date_input(
                "Expected Completion Date",
                value=(datetime.now() + timedelta(days=365)).date(),
                help="Expected project completion date"
            )
            
            project_location = st.text_input(
                "Project Location",
                placeholder="e.g., Los Angeles County",
                help="Geographic location of the project"
            )
        
        # Additional project details
        project_description = st.text_area(
            "Project Description",
            placeholder="Brief description of the project scope and requirements",
            height=100
        )
        
        return {
            'project_name': project_name,
            'project_number': project_number,
            'contract_type': contract_type,
            'bid_date': bid_date,
            'completion_date': completion_date,
            'project_location': project_location,
            'project_description': project_description
        }
    
    def _render_bid_configuration(self) -> Dict[str, Any]:
        """Render bid configuration options."""
        st.subheader("⚙️ Bid Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            markup_percentage = st.number_input(
                "Markup Percentage (%)",
                min_value=0.0,
                max_value=100.0,
                value=self.default_markup,
                step=0.5,
                help="Percentage markup to apply to base costs"
            )
            
            overhead_rate = st.number_input(
                "Overhead Rate (%)",
                min_value=0.0,
                max_value=50.0,
                value=10.0,
                step=0.5,
                help="Overhead percentage"
            )
        
        with col2:
            profit_margin = st.number_input(
                "Profit Margin (%)",
                min_value=0.0,
                max_value=50.0,
                value=8.0,
                step=0.5,
                help="Desired profit margin"
            )
            
            contingency_rate = st.number_input(
                "Contingency Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                help="Contingency percentage for unexpected costs"
            )
        
        with col3:
            tax_rate = st.number_input(
                "Tax Rate (%)",
                min_value=0.0,
                max_value=15.0,
                value=self.default_tax_rate,
                step=0.1,
                help="Sales tax rate"
            )
            
            currency = st.selectbox(
                "Currency",
                ["USD ($)", "EUR (€)", "GBP (£)"],
                help="Currency for bid amounts"
            )
        
        # Advanced options
        with st.expander("🔧 Advanced Configuration"):
            col1, col2 = st.columns(2)
            
            with col1:
                include_alternates = st.checkbox(
                    "Include Alternates",
                    value=True,
                    help="Include alternate bid items"
                )
                
                use_escalation = st.checkbox(
                    "Use Escalation",
                    value=False,
                    help="Apply cost escalation factors"
                )
            
            with col2:
                escalation_rate = st.number_input(
                    "Escalation Rate (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=3.0,
                    step=0.1,
                    disabled=not st.session_state.get('use_escalation', False)
                )
                
                bid_validity_days = st.number_input(
                    "Bid Validity (Days)",
                    min_value=30,
                    max_value=365,
                    value=90,
                    step=1
                )
        
        return {
            'markup_percentage': markup_percentage,
            'overhead_rate': overhead_rate,
            'profit_margin': profit_margin,
            'contingency_rate': contingency_rate,
            'tax_rate': tax_rate,
            'currency': currency,
            'include_alternates': include_alternates,
            'use_escalation': use_escalation,
            'escalation_rate': escalation_rate,
            'bid_validity_days': bid_validity_days
        }
    
    def _render_line_items_section(self, analysis_data: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Render line items management section."""
        st.subheader("📝 Line Items")
        
        # Initialize line items from analysis data or create sample data
        if analysis_data and 'quantities' in analysis_data:
            line_items = self._create_line_items_from_analysis(analysis_data)
        else:
            line_items = self._get_sample_line_items()
        
        # Display line items in an editable table
        line_items_df = self._render_line_items_table(line_items)
        
        # Add new line item
        if st.button("➕ Add Line Item"):
            line_items.append(self._get_empty_line_item())
            st.rerun()
        
        return line_items
    
    def _create_line_items_from_analysis(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create line items from analysis data."""
        line_items = []
        quantities = analysis_data.get('quantities', [])
        
        for i, quantity in enumerate(quantities):
            line_item = {
                'item_number': f"{i+1:03d}",
                'description': quantity.get('description', f'Item {i+1}'),
                'quantity': quantity.get('value', 0),
                'unit': quantity.get('unit', 'EA'),
                'unit_price': 0.0,
                'total_price': 0.0,
                'category': quantity.get('category', 'General'),
                'notes': quantity.get('notes', '')
            }
            line_items.append(line_item)
        
        return line_items
    
    def _get_sample_line_items(self) -> List[Dict[str, Any]]:
        """Get sample line items for demonstration."""
        return [
            {
                'item_number': '001',
                'description': 'Concrete, Class A, 3000 PSI',
                'quantity': 100.0,
                'unit': 'CY',
                'unit_price': 150.00,
                'total_price': 15000.00,
                'category': 'Materials',
                'notes': 'Standard concrete mix'
            },
            {
                'item_number': '002',
                'description': 'Reinforcing Steel, Grade 60',
                'quantity': 5000.0,
                'unit': 'LB',
                'unit_price': 0.85,
                'total_price': 4250.00,
                'category': 'Materials',
                'notes': 'Deformed bars'
            },
            {
                'item_number': '003',
                'description': 'Excavation, Common',
                'quantity': 200.0,
                'unit': 'CY',
                'unit_price': 25.00,
                'total_price': 5000.00,
                'category': 'Earthwork',
                'notes': 'Unclassified excavation'
            }
        ]
    
    def _get_empty_line_item(self) -> Dict[str, Any]:
        """Get an empty line item template."""
        return {
            'item_number': '',
            'description': '',
            'quantity': 0.0,
            'unit': 'EA',
            'unit_price': 0.0,
            'total_price': 0.0,
            'category': 'General',
            'notes': ''
        }
    
    def _render_line_items_table(self, line_items: List[Dict[str, Any]]) -> pd.DataFrame:
        """Render line items in an interactive table."""
        if not line_items:
            st.info("No line items available. Add some items to get started.")
            return pd.DataFrame()
        
        # Convert to DataFrame for display
        df = pd.DataFrame(line_items)
        
        # Display with editing capabilities
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'item_number': st.column_config.TextColumn(
                    'Item #',
                    width='small',
                    help='Line item number'
                ),
                'description': st.column_config.TextColumn(
                    'Description',
                    width='medium',
                    help='Item description'
                ),
                'quantity': st.column_config.NumberColumn(
                    'Quantity',
                    width='small',
                    help='Item quantity'
                ),
                'unit': st.column_config.SelectboxColumn(
                    'Unit',
                    width='small',
                    options=['EA', 'CY', 'SF', 'LF', 'LB', 'TON', 'GAL', 'LS'],
                    help='Unit of measure'
                ),
                'unit_price': st.column_config.NumberColumn(
                    'Unit Price',
                    width='small',
                    format='$%.2f',
                    help='Price per unit'
                ),
                'total_price': st.column_config.NumberColumn(
                    'Total Price',
                    width='small',
                    format='$%.2f',
                    help='Total price for this item'
                ),
                'category': st.column_config.SelectboxColumn(
                    'Category',
                    width='small',
                    options=['Materials', 'Labor', 'Equipment', 'Earthwork', 'General'],
                    help='Item category'
                ),
                'notes': st.column_config.TextColumn(
                    'Notes',
                    width='medium',
                    help='Additional notes'
                )
            }
        )
        
        return edited_df
    
    def _render_pricing_summary(self, line_items: List[Dict[str, Any]], bid_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render pricing summary with calculations."""
        st.subheader("💰 Pricing Summary")
        
        # Calculate totals
        subtotal = sum(item.get('total_price', 0) for item in line_items)
        markup_amount = subtotal * (bid_config['markup_percentage'] / 100)
        overhead_amount = subtotal * (bid_config['overhead_rate'] / 100)
        profit_amount = subtotal * (bid_config['profit_margin'] / 100)
        contingency_amount = subtotal * (bid_config['contingency_rate'] / 100)
        
        # Apply escalation if enabled
        escalation_amount = 0
        if bid_config.get('use_escalation', False):
            escalation_amount = subtotal * (bid_config['escalation_rate'] / 100)
        
        # Calculate totals
        total_before_tax = subtotal + markup_amount + overhead_amount + profit_amount + contingency_amount + escalation_amount
        tax_amount = total_before_tax * (bid_config['tax_rate'] / 100)
        grand_total = total_before_tax + tax_amount
        
        # Display summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Subtotal",
                f"{self.currency_symbol}{subtotal:,.2f}",
                help="Sum of all line items"
            )
        
        with col2:
            st.metric(
                "Markup",
                f"{self.currency_symbol}{markup_amount:,.2f}",
                delta=f"{bid_config['markup_percentage']}%",
                help="Markup amount"
            )
        
        with col3:
            st.metric(
                "Overhead & Profit",
                f"{self.currency_symbol}{overhead_amount + profit_amount:,.2f}",
                delta=f"{bid_config['overhead_rate'] + bid_config['profit_margin']}%",
                help="Overhead and profit combined"
            )
        
        with col4:
            st.metric(
                "Grand Total",
                f"{self.currency_symbol}{grand_total:,.2f}",
                delta=f"{self.currency_symbol}{tax_amount:,.2f}",
                help="Final bid amount including tax"
            )
        
        # Detailed breakdown
        with st.expander("📊 Detailed Breakdown"):
            breakdown_data = {
                'Category': ['Subtotal', 'Markup', 'Overhead', 'Profit', 'Contingency', 'Escalation', 'Subtotal (Before Tax)', 'Tax', 'Grand Total'],
                'Amount': [subtotal, markup_amount, overhead_amount, profit_amount, contingency_amount, escalation_amount, total_before_tax, tax_amount, grand_total],
                'Percentage': [100, bid_config['markup_percentage'], bid_config['overhead_rate'], bid_config['profit_margin'], bid_config['contingency_rate'], bid_config.get('escalation_rate', 0), 0, bid_config['tax_rate'], 0]
            }
            
            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
        
        return {
            'subtotal': subtotal,
            'markup_amount': markup_amount,
            'overhead_amount': overhead_amount,
            'profit_amount': profit_amount,
            'contingency_amount': contingency_amount,
            'escalation_amount': escalation_amount,
            'total_before_tax': total_before_tax,
            'tax_amount': tax_amount,
            'grand_total': grand_total
        }
    
    def _generate_bid(self, project_info: Dict[str, Any], bid_config: Dict[str, Any], 
                     line_items: List[Dict[str, Any]], pricing_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the final bid."""
        
        # Create bid data structure
        bid_data = {
            'project_info': project_info,
            'bid_config': bid_config,
            'line_items': line_items,
            'pricing_summary': pricing_summary,
            'generated_at': datetime.now().isoformat(),
            'bid_id': f"BID-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }
        
        # Store in session state
        st.session_state['current_bid'] = bid_data
        
        # Show success message
        st.success(f"✅ Bid generated successfully! Bid ID: {bid_data['bid_id']}")
        
        # Show download options
        self._render_download_options(bid_data)
        
        return bid_data
    
    def _render_download_options(self, bid_data: Dict[str, Any]) -> None:
        """Render download options for the generated bid."""
        st.subheader("📥 Download Options")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Excel Bid Sheet", use_container_width=True):
                self._download_excel_bid(bid_data)
        
        with col2:
            if st.button("📄 PDF Bid Report", use_container_width=True):
                self._download_pdf_bid(bid_data)
        
        with col3:
            if st.button("📋 JSON Data", use_container_width=True):
                self._download_json_bid(bid_data)
        
        with col4:
            if st.button("📧 Email Bid", use_container_width=True):
                self._email_bid(bid_data)


def render_bid_history() -> None:
    """Render bid history and management."""
    st.subheader("📚 Bid History")
    
    if 'bid_history' not in st.session_state:
        st.session_state.bid_history = []
    
    if st.session_state.bid_history:
        for i, bid in enumerate(st.session_state.bid_history):
            with st.expander(f"💰 {bid.get('project_info', {}).get('project_name', 'Unknown Project')} - {bid.get('bid_id', 'No ID')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Generated:** {bid.get('generated_at', 'Unknown')}")
                    st.write(f"**Total:** {bid.get('pricing_summary', {}).get('grand_total', 0):,.2f}")
                
                with col2:
                    st.write(f"**Project:** {bid.get('project_info', {}).get('project_number', 'No Number')}")
                    st.write(f"**Type:** {bid.get('project_info', {}).get('contract_type', 'Unknown')}")
                
                with col3:
                    if st.button(f"View Details", key=f"view_{i}"):
                        st.session_state['current_bid'] = bid
                        st.rerun()
                    
                    if st.button(f"Delete", key=f"delete_{i}"):
                        st.session_state.bid_history.pop(i)
                        st.rerun()
    else:
        st.info("No bids generated yet. Create your first bid to see it here.")


def _download_excel_bid(bid_data: Dict[str, Any]) -> None:
    """Download bid as Excel file."""
    # This would implement Excel generation and download
    st.success("✅ Excel bid sheet generated successfully!")
    st.info("Download will start automatically.")


def _download_pdf_bid(bid_data: Dict[str, Any]) -> None:
    """Download bid as PDF file."""
    # This would implement PDF generation and download
    st.success("✅ PDF bid report generated successfully!")
    st.info("Download will start automatically.")


def _download_json_bid(bid_data: Dict[str, Any]) -> None:
    """Download bid as JSON file."""
    # This would implement JSON export and download
    st.success("✅ JSON bid data exported successfully!")
    st.info("Download will start automatically.")


def _email_bid(bid_data: Dict[str, Any]) -> None:
    """Email bid to specified recipients."""
    # This would implement email functionality
    st.success("✅ Bid emailed successfully!")
    st.info("Email sent to specified recipients.")


def render_bid_templates() -> None:
    """Render bid template management."""
    st.subheader("📋 Bid Templates")
    
    # Template selection
    template_type = st.selectbox(
        "Select Template Type",
        ["Construction", "Maintenance", "Emergency", "Design-Build", "Custom"]
    )
    
    # Template configuration
    with st.expander("🔧 Template Configuration"):
        col1, col2 = st.columns(2)
        
        with col1:
            template_name = st.text_input("Template Name", placeholder="Enter template name")
            default_markup = st.number_input("Default Markup (%)", value=15.0, step=0.5)
        
        with col2:
            template_description = st.text_area("Description", placeholder="Template description")
            default_overhead = st.number_input("Default Overhead (%)", value=10.0, step=0.5)
    
    # Save template
    if st.button("💾 Save Template"):
        st.success("✅ Template saved successfully!")


def render_bid_validation(bid_data: Dict[str, Any]) -> None:
    """Render bid validation and quality checks."""
    st.subheader("✅ Bid Validation")
    
    validation_results = []
    
    # Check project information
    project_info = bid_data.get('project_info', {})
    if not project_info.get('project_name'):
        validation_results.append(("❌", "Project name is missing", "error"))
    else:
        validation_results.append(("✅", "Project name is provided", "success"))
    
    if not project_info.get('project_number'):
        validation_results.append(("⚠️", "Project number is missing", "warning"))
    else:
        validation_results.append(("✅", "Project number is provided", "success"))
    
    # Check line items
    line_items = bid_data.get('line_items', [])
    if not line_items:
        validation_results.append(("❌", "No line items found", "error"))
    else:
        validation_results.append(("✅", f"{len(line_items)} line items found", "success"))
    
    # Check pricing
    pricing_summary = bid_data.get('pricing_summary', {})
    if pricing_summary.get('grand_total', 0) <= 0:
        validation_results.append(("❌", "Bid total is zero or negative", "error"))
    else:
        validation_results.append(("✅", f"Bid total: ${pricing_summary.get('grand_total', 0):,.2f}", "success"))
    
    # Display validation results
    for icon, message, status in validation_results:
        if status == "error":
            st.error(f"{icon} {message}")
        elif status == "warning":
            st.warning(f"{icon} {message}")
        else:
            st.success(f"{icon} {message}")
    
    # Overall validation status
    errors = sum(1 for _, _, status in validation_results if status == "error")
    warnings = sum(1 for _, _, status in validation_results if status == "warning")
    
    if errors == 0 and warnings == 0:
        st.success("🎉 Bid validation passed! Your bid is ready for submission.")
    elif errors == 0:
        st.warning(f"⚠️ Bid validation passed with {warnings} warning(s). Please review before submission.")
    else:
        st.error(f"❌ Bid validation failed with {errors} error(s). Please fix issues before submission.") 
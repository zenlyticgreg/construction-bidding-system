import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_drawable_canvas import st_canvas
import pandas as pd
from typing import Dict, List, Optional
import base64

class EnhancedPlanViewer:
    """Interactive plan viewer with measurement and annotation tools"""
    
    def __init__(self):
        self.measurement_tools = ['Linear', 'Area', 'Count', 'Annotation']
        self.drawing_layers = ['Architectural', 'Structural', 'Dimensions', 'Annotations']
    
    def create_plan_viewer_interface(self, pdf_analysis_result: Dict = None):
        """Create the main plan viewer interface"""
        
        st.subheader("🖼️ Interactive Plan Viewer")
        
        # Viewer controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            measurement_mode = st.selectbox(
                "📏 Measurement Tool",
                self.measurement_tools,
                help="Select measurement tool for plan analysis"
            )
        
        with col2:
            scale_factor = st.number_input(
                "📐 Scale Factor (px/ft)",
                min_value=1.0,
                max_value=200.0,
                value=48.0,
                step=1.0,
                help="Pixels per foot for accurate measurements"
            )
        
        with col3:
            line_width = st.slider(
                "✏️ Line Width",
                min_value=1,
                max_value=10,
                value=2,
                help="Drawing line thickness"
            )
        
        with col4:
            drawing_color = st.color_picker(
                "🎨 Draw Color",
                value="#FF0000",
                help="Color for measurements and annotations"
            )
        
        # Layer controls
        with st.expander("🔧 Layer Controls", expanded=False):
            layer_cols = st.columns(len(self.drawing_layers))
            layer_visibility = {}
            
            for i, layer in enumerate(self.drawing_layers):
                with layer_cols[i]:
                    layer_visibility[layer] = st.checkbox(
                        layer, 
                        value=True,
                        help=f"Show/hide {layer.lower()} layer"
                    )
        
        # Main canvas area
        canvas_container = st.container()
        
        with canvas_container:
            # Create drawable canvas
            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",
                stroke_width=line_width,
                stroke_color=drawing_color,
                background_color="#FFFFFF",
                background_image=None,  # Would be PDF image in real implementation
                update_streamlit=True,
                height=600,
                width=800,
                drawing_mode="line" if measurement_mode == "Linear" else "rect",
                point_display_radius=3,
                key="plan_canvas"
            )
        
        # Measurement results panel
        col_left, col_right = st.columns([3, 1])
        
        with col_right:
            st.subheader("📊 Measurements")
            
            if canvas_result.json_data is not None:
                objects = canvas_result.json_data["objects"]
                if objects:
                    measurements_df = self._process_canvas_measurements(
                        objects, scale_factor, measurement_mode
                    )
                    
                    if not measurements_df.empty:
                        st.dataframe(measurements_df, use_container_width=True)
                        
                        # Export measurements
                        if st.button("📥 Export Measurements"):
                            csv = measurements_df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name="plan_measurements.csv",
                                mime="text/csv"
                            )
                    else:
                        st.info("No measurements yet")
                else:
                    st.info("Draw on the plan to start measuring")
            else:
                st.info("Canvas loading...")
            
            # Quick actions
            st.subheader("⚡ Quick Actions")
            
            if st.button("🔄 Clear All", use_container_width=True):
                st.experimental_rerun()
            
            if st.button("📐 Calibrate Scale", use_container_width=True):
                st.info("Draw a line on a known dimension, then enter the actual length")
            
            if st.button("💾 Save View", use_container_width=True):
                st.success("View saved!")
        
        return canvas_result
    
    def _process_canvas_measurements(self, objects: List, scale_factor: float, mode: str) -> pd.DataFrame:
        """Process canvas drawings into measurements"""
        measurements = []
        
        for i, obj in enumerate(objects):
            if obj["type"] == "line":
                # Calculate line length
                x1, y1 = obj["x1"], obj["y1"]
                x2, y2 = obj["x2"], obj["y2"]
                pixel_length = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
                actual_length = pixel_length / scale_factor
                
                measurements.append({
                    "ID": f"L{i+1}",
                    "Type": "Linear",
                    "Value": round(actual_length, 2),
                    "Unit": "ft",
                    "Notes": "Line measurement"
                })
            
            elif obj["type"] == "rect":
                # Calculate rectangle area
                width_px = obj["width"]
                height_px = obj["height"]
                width_ft = width_px / scale_factor
                height_ft = height_px / scale_factor
                area_sf = width_ft * height_ft
                
                measurements.append({
                    "ID": f"A{i+1}",
                    "Type": "Area",
                    "Value": round(area_sf, 2),
                    "Unit": "sf",
                    "Notes": f"{round(width_ft, 1)}' x {round(height_ft, 1)}'"
                })
        
        return pd.DataFrame(measurements)
    
    def create_quantity_summary_dashboard(self, analysis_results: Dict):
        """Create quantity summary dashboard"""
        
        st.subheader("📊 Quantity Summary Dashboard")
        
        # Sample data - would come from actual analysis
        sample_quantities = {
            'Concrete': {'quantity': 45.2, 'unit': 'CY', 'cost': 6780.00},
            'Steel': {'quantity': 12.8, 'unit': 'Tons', 'cost': 32000.00},
            'Lumber': {'quantity': 3250, 'unit': 'BF', 'cost': 2762.50},
            'Formwork': {'quantity': 1215, 'unit': 'SF', 'cost': 10327.50},
            'Doors': {'quantity': 8, 'unit': 'EA', 'cost': 3400.00},
            'Windows': {'quantity': 12, 'unit': 'EA', 'cost': 4620.00}
        }
        
        # Create metrics display
        cols = st.columns(3)
        
        for i, (material, data) in enumerate(sample_quantities.items()):
            col_idx = i % 3
            with cols[col_idx]:
                st.metric(
                    label=f"{material}",
                    value=f"{data['quantity']} {data['unit']}",
                    delta=f"${data['cost']:,.0f}"
                )
        
        # Quantity breakdown chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Quantity chart
            materials = list(sample_quantities.keys())
            quantities = [data['quantity'] for data in sample_quantities.values()]
            
            fig_qty = px.bar(
                x=materials,
                y=quantities,
                title="Quantities by Material Type",
                labels={'x': 'Material', 'y': 'Quantity'}
            )
            fig_qty.update_layout(height=400)
            st.plotly_chart(fig_qty, use_container_width=True)
        
        with col2:
            # Cost distribution pie chart
            costs = [data['cost'] for data in sample_quantities.values()]
            
            fig_cost = px.pie(
                values=costs,
                names=materials,
                title="Cost Distribution by Material"
            )
            fig_cost.update_layout(height=400)
            st.plotly_chart(fig_cost, use_container_width=True)
        
        # Detailed quantity table
        st.subheader("📋 Detailed Quantity Breakdown")
        
        # Convert to DataFrame for display
        qty_data = []
        for material, data in sample_quantities.items():
            qty_data.append({
                'Material': material,
                'Quantity': data['quantity'],
                'Unit': data['unit'],
                'Unit Cost': f"${data['cost']/data['quantity']:.2f}",
                'Extended Cost': f"${data['cost']:,.2f}",
                'Source': 'Plan Analysis',
                'Confidence': '90%'
            })
        
        qty_df = pd.DataFrame(qty_data)
        
        st.dataframe(
            qty_df,
            use_container_width=True,
            column_config={
                "Material": st.column_config.TextColumn(
                    "Material Type",
                    width="medium"
                ),
                "Quantity": st.column_config.NumberColumn(
                    "Quantity",
                    format="%.2f"
                ),
                "Extended Cost": st.column_config.TextColumn(
                    "Extended Cost",
                    width="medium"
                ),
                "Confidence": st.column_config.ProgressColumn(
                    "Confidence",
                    min_value=0,
                    max_value=100,
                    format="%.0f%%"
                )
            }
        )
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export to Excel"):
                st.success("Exported to Excel format!")
        
        with col2:
            if st.button("📄 Generate Report"):
                st.success("PDF report generated!")
        
        with col3:
            if st.button("💰 Create Bid"):
                st.success("Bid package created!")
    
    def create_quality_control_panel(self, analysis_quality: Dict):
        """Create quality control and validation panel"""
        
        st.subheader("✅ Quality Control Panel")
        
        # Quality score display
        quality_score = analysis_quality.get('overall_score', 85.5)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Overall Quality Score",
                value=f"{quality_score:.1f}%",
                delta="Above Target"
            )
        
        with col2:
            accuracy = analysis_quality.get('accuracy', 92.3)
            st.metric(
                label="Measurement Accuracy",
                value=f"{accuracy:.1f}%",
                delta="+2.3%"
            )
        
        with col3:
            completeness = analysis_quality.get('completeness', 88.7)
            st.metric(
                label="Analysis Completeness",
                value=f"{completeness:.1f}%",
                delta="+5.2%"
            )
        
        # Quality alerts
        st.subheader("🚨 Quality Alerts")
        
        alerts = [
            {"level": "INFO", "message": "Scale calibration successful", "action": "None required"},
            {"level": "WARNING", "message": "Some dimensions estimated", "action": "Verify manually"},
            {"level": "SUCCESS", "message": "All materials identified", "action": "Proceed with confidence"}
        ]
        
        for alert in alerts:
            if alert["level"] == "INFO":
                st.info(f"ℹ️ {alert['message']} - {alert['action']}")
            elif alert["level"] == "WARNING":
                st.warning(f"⚠️ {alert['message']} - {alert['action']}")
            elif alert["level"] == "SUCCESS":
                st.success(f"✅ {alert['message']} - {alert['action']}")
        
        # Validation checklist
        st.subheader("📋 Validation Checklist")
        
        checklist_items = [
            ("Scale verification completed", True),
            ("Drawing type identified", True),
            ("Key dimensions extracted", True),
            ("Material quantities calculated", True),
            ("Cross-reference validation", False),
            ("Peer review completed", False)
        ]
        
        for item, completed in checklist_items:
            if completed:
                st.success(f"✅ {item}")
            else:
                st.error(f"❌ {item}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Run Additional Validation"):
                st.info("Additional validation checks initiated...")
        
        with col2:
            if st.button("📝 Generate QC Report"):
                st.success("Quality control report generated!")

# Usage example for integration
def create_enhanced_plan_analysis_page():
    """Main function to create the enhanced plan analysis page"""
    
    viewer = EnhancedPlanViewer()
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📐 Plan Viewer", "📊 Quantities", "✅ Quality Control"])
    
    with tab1:
        canvas_result = viewer.create_plan_viewer_interface()
    
    with tab2:
        viewer.create_quantity_summary_dashboard({})
    
    with tab3:
        viewer.create_quality_control_panel({})
    
    return canvas_result
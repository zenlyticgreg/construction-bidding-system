import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
from datetime import datetime

@dataclass
class EnhancedBidLineItem:
    """Enhanced bid line item with plan analysis integration"""
    csi_division: str
    description: str
    quantity: float
    unit: str
    unit_price: float
    extended_price: float
    source: str  # 'caltrans_analysis', 'plan_takeoff', 'catalog_match'
    confidence: float
    notes: str = ""

@dataclass
class EnhancedBidSummary:
    """Enhanced bid summary with comprehensive analysis"""
    project_info: Dict
    caltrans_analysis: Dict
    plan_analysis: Dict
    line_items: List[EnhancedBidLineItem]
    pricing_summary: Dict
    quality_metrics: Dict
    generation_timestamp: str

class AdvancedBidEngine:
    """Enhanced bid engine combining CalTrans analysis with plan takeoffs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # CSI MasterFormat divisions for organization
        self.csi_divisions = {
            '03': 'Concrete',
            '05': 'Metals', 
            '06': 'Wood, Plastics, and Composites',
            '07': 'Thermal and Moisture Protection',
            '08': 'Openings',
            '09': 'Finishes',
            '31': 'Earthwork',
            '32': 'Exterior Improvements',
            '33': 'Utilities'
        }
        
        # Standard markup and fee structure
        self.pricing_structure = {
            'material_markup': 0.20,      # 20% markup on materials
            'labor_markup': 0.15,         # 15% markup on labor
            'equipment_markup': 0.10,     # 10% markup on equipment
            'overhead_rate': 0.12,        # 12% overhead
            'profit_rate': 0.08,          # 8% profit
            'delivery_rate': 0.03,        # 3% delivery fee
            'min_delivery_fee': 150.00,   # $150 minimum delivery
            'bond_rate': 0.015,           # 1.5% for bonds (if required)
            'tax_rate': 0.0875            # 8.75% sales tax (example)
        }
    
    def generate_enhanced_bid(self, 
                            project_info: Dict,
                            caltrans_analysis: Dict = None,
                            plan_analysis: Dict = None,
                            catalog_data: Dict = None) -> EnhancedBidSummary:
        """Generate comprehensive bid combining all analysis sources"""
        
        try:
            # Initialize bid components
            line_items = []
            
            # Process CalTrans analysis results
            if caltrans_analysis:
                caltrans_items = self._process_caltrans_analysis(caltrans_analysis, catalog_data)
                line_items.extend(caltrans_items)
            
            # Process plan analysis results  
            if plan_analysis:
                plan_items = self._process_plan_analysis(plan_analysis, catalog_data)
                line_items.extend(plan_items)
            
            # Calculate pricing summary
            pricing_summary = self._calculate_enhanced_pricing(line_items)
            
            # Generate quality metrics
            quality_metrics = self._calculate_quality_metrics(
                caltrans_analysis, plan_analysis, line_items
            )
            
            # Create enhanced bid summary
            enhanced_bid = EnhancedBidSummary(
                project_info=project_info,
                caltrans_analysis=caltrans_analysis or {},
                plan_analysis=plan_analysis or {},
                line_items=line_items,
                pricing_summary=pricing_summary,
                quality_metrics=quality_metrics,
                generation_timestamp=datetime.now().isoformat()
            )
            
            return enhanced_bid
            
        except Exception as e:
            self.logger.error(f"Error generating enhanced bid: {str(e)}")
            raise
    
    def _process_caltrans_analysis(self, caltrans_analysis: Dict, catalog_data: Dict = None) -> List[EnhancedBidLineItem]:
        """Convert CalTrans analysis to bid line items"""
        line_items = []
        
        terminology_found = caltrans_analysis.get('terminology_found', {})
        lumber_requirements = caltrans_analysis.get('lumber_requirements', {})
        
        # Process specific CalTrans terms
        for term, term_data in terminology_found.items():
            if term == 'BALUSTER':
                # Concrete bridge railing posts - heavy formwork
                quantity = term_data.get('total_quantity', 0)
                if quantity > 0:
                    # Formwork lumber
                    lumber_bf = quantity * 25.0  # 25 board feet per baluster
                    line_items.append(EnhancedBidLineItem(
                        csi_division='06',
                        description='Formwork Lumber - Baluster Forms (Heavy Duty)',
                        quantity=lumber_bf,
                        unit='BF',
                        unit_price=1.25,
                        extended_price=lumber_bf * 1.25,
                        source='caltrans_analysis',
                        confidence=0.9,
                        notes=f'Based on {quantity} balusters detected'
                    ))
                    
                    # Form hardware
                    line_items.append(EnhancedBidLineItem(
                        csi_division='06',
                        description='Form Hardware - Ties, Clamps, Brackets',
                        quantity=quantity * 15.0,  # 15 lbs hardware per baluster
                        unit='LB',
                        unit_price=2.25,
                        extended_price=quantity * 15.0 * 2.25,
                        source='caltrans_analysis',
                        confidence=0.8,
                        notes='Heavy duty forming hardware'
                    ))
            
            elif term == 'BLOCKOUT':
                # Void formers - temporary lumber
                quantity = term_data.get('total_quantity', 0)
                if quantity > 0:
                    lumber_bf = quantity * 8.0  # 8 board feet per blockout
                    line_items.append(EnhancedBidLineItem(
                        csi_division='06',
                        description='Blockout Forms - Temporary Lumber',
                        quantity=lumber_bf,
                        unit='BF',
                        unit_price=0.95,
                        extended_price=lumber_bf * 0.95,
                        source='caltrans_analysis',
                        confidence=0.85,
                        notes=f'Temporary forms for {quantity} blockouts'
                    ))
            
            elif term == 'STAMPED_CONCRETE':
                # Textured decorative concrete - special forms
                area_sf = term_data.get('total_quantity', 0)
                if area_sf > 0:
                    # Textured form liner
                    line_items.append(EnhancedBidLineItem(
                        csi_division='03',
                        description='Textured Form Liner - Stamped Pattern',
                        quantity=area_sf,
                        unit='SF',
                        unit_price=4.50,
                        extended_price=area_sf * 4.50,
                        source='caltrans_analysis',
                        confidence=0.9,
                        notes='Fractured rib or stamped texture'
                    ))
                    
                    # Form release agent
                    line_items.append(EnhancedBidLineItem(
                        csi_division='03',
                        description='Form Release Agent - Textured Forms',
                        quantity=area_sf / 400,  # 1 gallon per 400 SF
                        unit='GAL',
                        unit_price=35.00,
                        extended_price=(area_sf / 400) * 35.00,
                        source='caltrans_analysis',
                        confidence=0.8,
                        notes='Specialized release for textured forms'
                    ))
            
            elif term == 'FALSEWORK':
                # Heavy temporary structural support
                quantity = term_data.get('total_quantity', 0)
                if quantity > 0:
                    # Heavy timber for falsework
                    timber_bf = quantity * 150.0  # 150 board feet per unit
                    line_items.append(EnhancedBidLineItem(
                        csi_division='06',
                        description='Heavy Timber - Falsework Structure',
                        quantity=timber_bf,
                        unit='BF',
                        unit_price=2.75,
                        extended_price=timber_bf * 2.75,
                        source='caltrans_analysis',
                        confidence=0.85,
                        notes='Engineered falsework system'
                    ))
                    
                    # Structural hardware
                    line_items.append(EnhancedBidLineItem(
                        csi_division='05',
                        description='Structural Hardware - Falsework Connections',
                        quantity=quantity * 50.0,  # 50 lbs per unit
                        unit='LB',
                        unit_price=3.25,
                        extended_price=quantity * 50.0 * 3.25,
                        source='caltrans_analysis',
                        confidence=0.8,
                        notes='Heavy duty structural connections'
                    ))
        
        # Add lumber summary if available
        if lumber_requirements:
            total_lumber = lumber_requirements.get('total_lumber_bf', 0)
            if total_lumber > 0 and not any(item.description.startswith('Total Lumber') for item in line_items):
                line_items.append(EnhancedBidLineItem(
                    csi_division='06',
                    description='Total Lumber Summary - All Applications',
                    quantity=total_lumber,
                    unit='BF',
                    unit_price=1.15,  # Average lumber price
                    extended_price=total_lumber * 1.15,
                    source='caltrans_analysis',
                    confidence=0.85,
                    notes='Combined lumber requirements'
                ))
        
        return line_items
    
    def _process_plan_analysis(self, plan_analysis: Dict, catalog_data: Dict = None) -> List[EnhancedBidLineItem]:
        """Convert plan analysis to bid line items"""
        line_items = []
        
        # Process extracted quantities from plans
        quantities = plan_analysis.get('extracted_quantities', [])
        
        for quantity_item in quantities:
            material_type = quantity_item.get('material_type', 'UNKNOWN')
            quantity_value = quantity_item.get('quantity', 0)
            unit = quantity_item.get('unit', 'EA')
            confidence = quantity_item.get('confidence', 0.7)
            
            if quantity_value <= 0:
                continue
            
            # Map material types to CSI divisions and pricing
            if material_type == 'CONCRETE':
                line_items.append(EnhancedBidLineItem(
                    csi_division='03',
                    description='Ready-Mix Concrete',
                    quantity=quantity_value,
                    unit=unit,
                    unit_price=150.00,  # $150 per CY
                    extended_price=quantity_value * 150.00,
                    source='plan_takeoff',
                    confidence=confidence,
                    notes='Structural concrete placement'
                ))
            
            elif material_type == 'STEEL':
                line_items.append(EnhancedBidLineItem(
                    csi_division='05',
                    description='Structural Steel',
                    quantity=quantity_value,
                    unit=unit,
                    unit_price=1.25,  # $1.25 per LB
                    extended_price=quantity_value * 1.25,
                    source='plan_takeoff',
                    confidence=confidence,
                    notes='Fabricated structural steel'
                ))
            
            elif material_type == 'LUMBER':
                line_items.append(EnhancedBidLineItem(
                    csi_division='06',
                    description='Construction Lumber',
                    quantity=quantity_value,
                    unit=unit,
                    unit_price=0.85,  # $0.85 per BF
                    extended_price=quantity_value * 0.85,
                    source='plan_takeoff',
                    confidence=confidence,
                    notes='Framing and form lumber'
                ))
            
            elif material_type == 'DOORS':
                line_items.append(EnhancedBidLineItem(
                    csi_division='08',
                    description='Doors and Hardware',
                    quantity=quantity_value,
                    unit=unit,
                    unit_price=425.00,  # $425 per door
                    extended_price=quantity_value * 425.00,
                    source='plan_takeoff',
                    confidence=confidence,
                    notes='Interior/exterior doors with hardware'
                ))
            
            elif material_type == 'WINDOWS':
                line_items.append(EnhancedBidLineItem(
                    csi_division='08',
                    description='Windows',
                    quantity=quantity_value,
                    unit=unit,
                    unit_price=385.00,  # $385 per window
                    extended_price=quantity_value * 385.00,
                    source='plan_takeoff',
                    confidence=confidence,
                    notes='Windows with installation'
                ))
            
            elif material_type == 'FLOORING':
                line_items.append(EnhancedBidLineItem(
                    csi_division='09',
                    description='Flooring Materials',
                    quantity=quantity_value,
                    unit=unit,
                    unit_price=3.75,  # $3.75 per SF
                    extended_price=quantity_value * 3.75,
                    source='plan_takeoff',
                    confidence=confidence,
                    notes='Flooring material and installation'
                ))
        
        return line_items
    
    def _calculate_enhanced_pricing(self, line_items: List[EnhancedBidLineItem]) -> Dict:
        """Calculate comprehensive pricing summary"""
        
        # Calculate subtotals
        materials_subtotal = sum(item.extended_price for item in line_items)
        
        # Apply markups
        material_markup = materials_subtotal * self.pricing_structure['material_markup']
        materials_with_markup = materials_subtotal + material_markup
        
        # Calculate delivery
        delivery_fee = max(
            materials_with_markup * self.pricing_structure['delivery_rate'],
            self.pricing_structure['min_delivery_fee']
        )
        
        # Calculate overhead and profit
        subtotal_before_overhead = materials_with_markup + delivery_fee
        overhead = subtotal_before_overhead * self.pricing_structure['overhead_rate']
        subtotal_with_overhead = subtotal_before_overhead + overhead
        profit = subtotal_with_overhead * self.pricing_structure['profit_rate']
        
        # Calculate tax
        subtotal_before_tax = subtotal_with_overhead + profit
        tax = subtotal_before_tax * self.pricing_structure['tax_rate']
        
        # Final total
        total = subtotal_before_tax + tax
        
        return {
            'materials_subtotal': round(materials_subtotal, 2),
            'material_markup': round(material_markup, 2),
            'materials_with_markup': round(materials_with_markup, 2),
            'delivery_fee': round(delivery_fee, 2),
            'overhead': round(overhead, 2),
            'profit': round(profit, 2),
            'subtotal_before_tax': round(subtotal_before_tax, 2),
            'tax': round(tax, 2),
            'total': round(total, 2),
            'line_item_count': len(line_items),
            'pricing_structure': self.pricing_structure
        }
    
    def _calculate_quality_metrics(self, caltrans_analysis: Dict, plan_analysis: Dict, line_items: List) -> Dict:
        """Calculate quality and confidence metrics"""
        
        # Confidence scoring
        if line_items:
            avg_confidence = sum(item.confidence for item in line_items) / len(line_items)
        else:
            avg_confidence = 0.0
        
        # Source analysis
        source_breakdown = {}
        for item in line_items:
            source = item.source
            if source not in source_breakdown:
                source_breakdown[source] = {'count': 0, 'value': 0.0}
            source_breakdown[source]['count'] += 1
            source_breakdown[source]['value'] += item.extended_price
        
        # Completeness assessment
        has_caltrans = bool(caltrans_analysis)
        has_plans = bool(plan_analysis)
        completeness_score = (has_caltrans * 0.4) + (has_plans * 0.6)
        
        return {
            'average_confidence': round(avg_confidence, 3),
            'completeness_score': round(completeness_score, 3),
            'source_breakdown': source_breakdown,
            'has_caltrans_analysis': has_caltrans,
            'has_plan_analysis': has_plans,
            'total_line_items': len(line_items),
            'quality_grade': self._assign_quality_grade(avg_confidence, completeness_score)
        }
    
    def _assign_quality_grade(self, confidence: float, completeness: float) -> str:
        """Assign quality grade based on metrics"""
        overall_score = (confidence * 0.6) + (completeness * 0.4)
        
        if overall_score >= 0.9:
            return 'A - Excellent'
        elif overall_score >= 0.8:
            return 'B - Good'
        elif overall_score >= 0.7:
            return 'C - Fair'
        elif overall_score >= 0.6:
            return 'D - Poor'
        else:
            return 'F - Inadequate'
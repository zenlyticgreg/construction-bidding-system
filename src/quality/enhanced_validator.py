import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class ValidationAlert:
    """Quality validation alert"""
    level: str  # 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    category: str
    message: str
    recommendation: str
    confidence: float

@dataclass
class QualityMetrics:
    """Overall quality assessment metrics"""
    overall_score: float
    accuracy_score: float
    completeness_score: float
    consistency_score: float
    confidence_score: float
    alerts: List[ValidationAlert]
    validation_summary: str

class EnhancedQualityValidator:
    """Comprehensive quality validation for construction takeoffs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Industry standard ratios for validation
        self.industry_ratios = {
            'sf_per_door': {'min': 100, 'max': 500, 'typical': 250},
            'sf_per_window': {'min': 50, 'max': 200, 'typical': 100},
            'sf_per_bathroom': {'min': 20, 'max': 100, 'typical': 50},
            'lf_electrical_per_sf': {'min': 2, 'max': 12, 'typical': 6},
            'cy_concrete_per_sf': {'min': 0.05, 'max': 0.5, 'typical': 0.2},
            'lbs_rebar_per_cy': {'min': 25, 'max': 300, 'typical': 100},
            'bf_lumber_per_sf': {'min': 3, 'max': 15, 'typical': 8}
        }
        
        # Cost validation ranges (per unit)
        self.cost_ranges = {
            'CONCRETE_CY': {'min': 100, 'max': 250, 'typical': 150},
            'STEEL_LB': {'min': 0.80, 'max': 2.00, 'typical': 1.25},
            'LUMBER_BF': {'min': 0.50, 'max': 2.00, 'typical': 0.85},
            'FORMWORK_SF': {'min': 4.00, 'max': 15.00, 'typical': 8.50},
            'DOOR_EA': {'min': 200, 'max': 800, 'typical': 425},
            'WINDOW_EA': {'min': 150, 'max': 600, 'typical': 385}
        }
    
    def validate_comprehensive_analysis(self, 
                                      caltrans_analysis: Dict,
                                      plan_analysis: Dict,
                                      extracted_quantities: List,
                                      pricing_data: Dict) -> QualityMetrics:
        """Perform comprehensive quality validation"""
        
        alerts = []
        
        try:
            # 1. Validate quantity ratios
            ratio_alerts = self._validate_quantity_ratios(extracted_quantities)
            alerts.extend(ratio_alerts)
            
            # 2. Validate cross-references between CalTrans and plans
            consistency_alerts = self._validate_cross_references(caltrans_analysis, plan_analysis)
            alerts.extend(consistency_alerts)
            
            # 3. Validate pricing reasonableness
            pricing_alerts = self._validate_pricing(extracted_quantities, pricing_data)
            alerts.extend(pricing_alerts)
            
            # 4. Validate completeness
            completeness_alerts = self._validate_completeness(caltrans_analysis, plan_analysis)
            alerts.extend(completeness_alerts)
            
            # 5. Calculate overall quality scores
            quality_scores = self._calculate_quality_scores(alerts, extracted_quantities)
            
            # Generate validation summary
            summary = self._generate_validation_summary(alerts, quality_scores)
            
            return QualityMetrics(
                overall_score=quality_scores['overall'],
                accuracy_score=quality_scores['accuracy'],
                completeness_score=quality_scores['completeness'],
                consistency_score=quality_scores['consistency'],
                confidence_score=quality_scores['confidence'],
                alerts=alerts,
                validation_summary=summary
            )
            
        except Exception as e:
            self.logger.error(f"Error in quality validation: {str(e)}")
            return QualityMetrics(
                overall_score=0.0,
                accuracy_score=0.0,
                completeness_score=0.0,
                consistency_score=0.0,
                confidence_score=0.0,
                alerts=[ValidationAlert('ERROR', 'SYSTEM', f'Validation failed: {str(e)}', 
                                       'Check system logs and retry', 0.0)],
                validation_summary="Validation could not be completed due to system error"
            )
    
    def _validate_quantity_ratios(self, extracted_quantities: List) -> List[ValidationAlert]:
        """Validate quantities against industry standard ratios"""
        alerts = []
        
        # Organize quantities by type
        qty_by_type = {}
        for item in extracted_quantities:
            material_type = item.get('material_type', 'UNKNOWN')
            quantity = item.get('quantity', 0)
            unit = item.get('unit', '')
            
            if material_type not in qty_by_type:
                qty_by_type[material_type] = []
            qty_by_type[material_type].append({'quantity': quantity, 'unit': unit})
        
        # Get building area for ratio calculations
        floor_area = self._get_total_floor_area(qty_by_type)
        
        if floor_area > 0:
            # Check door ratios
            door_count = self._get_count_by_type(qty_by_type, 'DOORS')
            if door_count > 0:
                sf_per_door = floor_area / door_count
                ratio_check = self.industry_ratios['sf_per_door']
                
                if sf_per_door < ratio_check['min'] or sf_per_door > ratio_check['max']:
                    alerts.append(ValidationAlert(
                        level='WARNING',
                        category='RATIO_CHECK',
                        message=f'Unusual door ratio: {sf_per_door:.0f} SF per door',
                        recommendation=f'Typical range: {ratio_check["min"]}-{ratio_check["max"]} SF per door',
                        confidence=0.8
                    ))
            
            # Check window ratios
            window_count = self._get_count_by_type(qty_by_type, 'WINDOWS')
            if window_count > 0:
                sf_per_window = floor_area / window_count
                ratio_check = self.industry_ratios['sf_per_window']
                
                if sf_per_window < ratio_check['min'] or sf_per_window > ratio_check['max']:
                    alerts.append(ValidationAlert(
                        level='WARNING',
                        category='RATIO_CHECK',
                        message=f'Unusual window ratio: {sf_per_window:.0f} SF per window',
                        recommendation=f'Typical range: {ratio_check["min"]}-{ratio_check["max"]} SF per window',
                        confidence=0.8
                    ))
        
        # Check concrete and reinforcement ratios
        concrete_cy = self._get_quantity_by_type(qty_by_type, 'CONCRETE', 'CY')
        rebar_lbs = self._get_quantity_by_type(qty_by_type, 'REINFORCEMENT', 'LB')
        
        if concrete_cy > 0 and rebar_lbs > 0:
            lbs_per_cy = rebar_lbs / concrete_cy
            ratio_check = self.industry_ratios['lbs_rebar_per_cy']
            
            if lbs_per_cy < ratio_check['min'] or lbs_per_cy > ratio_check['max']:
                alerts.append(ValidationAlert(
                    level='WARNING',
                    category='RATIO_CHECK',
                    message=f'Unusual rebar ratio: {lbs_per_cy:.0f} lbs per CY concrete',
                    recommendation=f'Typical range: {ratio_check["min"]}-{ratio_check["max"]} lbs per CY',
                    confidence=0.9
                ))
        
        return alerts
    
    def _validate_cross_references(self, caltrans_analysis: Dict, plan_analysis: Dict) -> List[ValidationAlert]:
        """Validate consistency between CalTrans and plan analysis"""
        alerts = []
        
        if not caltrans_analysis or not plan_analysis:
            alerts.append(ValidationAlert(
                level='INFO',
                category='CROSS_REFERENCE',
                message='Limited cross-reference validation - missing analysis data',
                recommendation='Ensure both CalTrans and plan analysis are completed',
                confidence=0.7
            ))
            return alerts
        
        # Check for conflicting information
        caltrans_terms = caltrans_analysis.get('terminology_found', {})
        plan_quantities = plan_analysis.get('extracted_quantities', [])
        
        # Look for major discrepancies
        has_concrete_terms = any('CONCRETE' in term.upper() for term in caltrans_terms.keys())
        has_concrete_quantities = any(item.get('material_type') == 'CONCRETE' for item in plan_quantities)
        
        if has_concrete_terms and not has_concrete_quantities:
            alerts.append(ValidationAlert(
                level='WARNING',
                category='CROSS_REFERENCE',
                message='Concrete work indicated in specifications but not found in plan quantities',
                recommendation='Verify concrete quantities in plan analysis',
                confidence=0.8
            ))
        
        if not has_concrete_terms and has_concrete_quantities:
            alerts.append(ValidationAlert(
                level='INFO',
                category='CROSS_REFERENCE',
                message='Concrete quantities found in plans but not in CalTrans terminology',
                recommendation='Verify specification requirements for concrete work',
                confidence=0.7
            ))
        
        return alerts
    
    def _validate_pricing(self, extracted_quantities: List, pricing_data: Dict) -> List[ValidationAlert]:
        """Validate pricing reasonableness"""
        alerts = []
        
        for item in extracted_quantities:
            material_type = item.get('material_type', 'UNKNOWN')
            unit = item.get('unit', '')
            unit_price = item.get('unit_price', 0)
            
            # Create pricing key
            price_key = f"{material_type}_{unit}"
            
            if price_key in self.cost_ranges:
                cost_range = self.cost_ranges[price_key]
                
                if unit_price < cost_range['min']:
                    alerts.append(ValidationAlert(
                        level='WARNING',
                        category='PRICING',
                        message=f'{material_type} unit price ${unit_price:.2f} seems low',
                        recommendation=f'Typical range: ${cost_range["min"]:.2f}-${cost_range["max"]:.2f}',
                        confidence=0.8
                    ))
                
                elif unit_price > cost_range['max']:
                    alerts.append(ValidationAlert(
                        level='WARNING',
                        category='PRICING',
                        message=f'{material_type} unit price ${unit_price:.2f} seems high',
                        recommendation=f'Typical range: ${cost_range["min"]:.2f}-${cost_range["max"]:.2f}',
                        confidence=0.8
                    ))
        
        return alerts
    
    def _validate_completeness(self, caltrans_analysis: Dict, plan_analysis: Dict) -> List[ValidationAlert]:
        """Validate completeness of analysis"""
        alerts = []
        
        # Check CalTrans analysis completeness
        if caltrans_analysis:
            terms_found = len(caltrans_analysis.get('terminology_found', {}))
            if terms_found == 0:
                alerts.append(ValidationAlert(
                    level='ERROR',
                    category='COMPLETENESS',
                    message='No CalTrans terminology detected',
                    recommendation='Verify document is a CalTrans specification',
                    confidence=0.9
                ))
            elif terms_found < 3:
                alerts.append(ValidationAlert(
                    level='WARNING',
                    category='COMPLETENESS',
                    message=f'Only {terms_found} CalTrans terms found',
                    recommendation='Consider reviewing additional specification sections',
                    confidence=0.7
                ))
        
        # Check plan analysis completeness
        if plan_analysis:
            quantities = plan_analysis.get('extracted_quantities', [])
            if len(quantities) == 0:
                alerts.append(ValidationAlert(
                    level='ERROR',
                    category='COMPLETENESS',
                    message='No quantities extracted from plans',
                    recommendation='Verify plan quality and scale detection',
                    confidence=0.9
                ))
            elif len(quantities) < 5:
                alerts.append(ValidationAlert(
                    level='WARNING',
                    category='COMPLETENESS',
                    message=f'Only {len(quantities)} quantities extracted',
                    recommendation='Consider analyzing additional plan sheets',
                    confidence=0.7
                ))
        
        return alerts
    
    def _calculate_quality_scores(self, alerts: List[ValidationAlert], quantities: List) -> Dict:
        """Calculate overall quality scores"""
        
        # Base scores
        accuracy_score = 100.0
        completeness_score = 100.0
        consistency_score = 100.0
        confidence_score = 100.0
        
        # Deduct points based on alerts
        for alert in alerts:
            deduction = 0
            if alert.level == 'ERROR':
                deduction = 15
            elif alert.level == 'WARNING':
                deduction = 8
            elif alert.level == 'INFO':
                deduction = 2
            
            if alert.category == 'RATIO_CHECK':
                accuracy_score -= deduction
            elif alert.category == 'COMPLETENESS':
                completeness_score -= deduction
            elif alert.category == 'CROSS_REFERENCE':
                consistency_score -= deduction
            elif alert.category == 'PRICING':
                accuracy_score -= deduction * 0.5
        
        # Calculate confidence based on quantity confidence
        if quantities:
            avg_confidence = sum(item.get('confidence', 0.5) for item in quantities) / len(quantities)
            confidence_score = avg_confidence * 100
        
        # Ensure scores don't go below 0
        accuracy_score = max(0, accuracy_score)
        completeness_score = max(0, completeness_score)
        consistency_score = max(0, consistency_score)
        confidence_score = max(0, confidence_score)
        
        # Calculate overall score
        overall_score = (accuracy_score + completeness_score + consistency_score + confidence_score) / 4
        
        return {
            'overall': round(overall_score, 1),
            'accuracy': round(accuracy_score, 1),
            'completeness': round(completeness_score, 1),
            'consistency': round(consistency_score, 1),
            'confidence': round(confidence_score, 1)
        }
    
    def _generate_validation_summary(self, alerts: List[ValidationAlert], scores: Dict) -> str:
        """Generate human-readable validation summary"""
        
        critical_count = sum(1 for alert in alerts if alert.level == 'CRITICAL')
        error_count = sum(1 for alert in alerts if alert.level == 'ERROR')
        warning_count = sum(1 for alert in alerts if alert.level == 'WARNING')
        
        overall_score = scores['overall']
        
        if overall_score >= 95:
            grade = "Excellent"
        elif overall_score >= 85:
            grade = "Good"
        elif overall_score >= 75:
            grade = "Fair"
        elif overall_score >= 60:
            grade = "Poor"
        else:
            grade = "Inadequate"
        
        summary = f"Quality Assessment: {grade} ({overall_score:.1f}%)\n"
        summary += f"Issues Found: {critical_count} Critical, {error_count} Errors, {warning_count} Warnings\n"
        
        if overall_score >= 85:
            summary += "Analysis quality is sufficient for bidding. Minor issues may need attention."
        elif overall_score >= 70:
            summary += "Analysis quality is acceptable but requires review of flagged issues."
        else:
            summary += "Analysis quality requires significant improvement before use in bidding."
        
        return summary
    
    # Helper methods
    def _get_total_floor_area(self, qty_by_type: Dict) -> float:
        """Get total floor area from quantities"""
        flooring_items = qty_by_type.get('FLOORING', [])
        return sum(item['quantity'] for item in flooring_items if item['unit'] == 'SF')
    
    def _get_count_by_type(self, qty_by_type: Dict, material_type: str) -> int:
        """Get count of items by material type"""
        items = qty_by_type.get(material_type, [])
        return sum(int(item['quantity']) for item in items if item['unit'] == 'EA')
    
    def _get_quantity_by_type(self, qty_by_type: Dict, material_type: str, unit: str) -> float:
        """Get total quantity by material type and unit"""
        items = qty_by_type.get(material_type, [])
        return sum(item['quantity'] for item in items if item['unit'] == unit)
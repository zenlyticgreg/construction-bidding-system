import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class QuantityResult:
    """Result of quantity extraction"""
    material_type: str
    quantity: float
    unit: str
    confidence: float
    calculation_method: str
    waste_factor: float
    final_quantity: float

class MaterialQuantityExtractor:
    """Extracts material quantities from construction plans"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Waste factors by material type
        self.waste_factors = {
            'CONCRETE': 0.05,      # 5% waste
            'LUMBER': 0.10,        # 10% waste
            'STEEL': 0.05,         # 5% waste
            'DRYWALL': 0.10,       # 10% waste
            'ROOFING': 0.08,       # 8% waste
            'FLOORING': 0.07,      # 7% waste
            'MASONRY': 0.05,       # 5% waste
            'INSULATION': 0.10,    # 10% waste
            'DEFAULT': 0.10        # 10% default waste
        }
        
        # Unit conversion factors
        self.unit_conversions = {
            'SQ_FT_TO_SQ_YD': 1/9,
            'CU_FT_TO_CU_YD': 1/27,
            'LIN_FT_TO_BOARD_FT': {
                '2x4': 2/3,    # 2x4 = 0.67 board feet per linear foot
                '2x6': 1.0,    # 2x6 = 1.0 board feet per linear foot
                '2x8': 4/3,    # 2x8 = 1.33 board feet per linear foot
                '2x10': 5/3,   # 2x10 = 1.67 board feet per linear foot
                '2x12': 2.0,   # 2x12 = 2.0 board feet per linear foot
            }
        }
    
    def extract_quantities_from_text(self, text: str, drawing_type: str, scale_ratio: float = 48.0) -> List[QuantityResult]:
        """Main method to extract quantities from drawing text"""
        quantities = []
        
        try:
            # Extract different types of quantities based on drawing type
            if drawing_type == "ARCHITECTURAL_PLAN":
                quantities.extend(self._extract_floor_areas(text))
                quantities.extend(self._extract_door_window_counts(text))
                quantities.extend(self._extract_wall_lengths(text))
                
            elif drawing_type == "STRUCTURAL_PLAN":
                quantities.extend(self._extract_concrete_volumes(text))
                quantities.extend(self._extract_steel_quantities(text))
                quantities.extend(self._extract_formwork_areas(text))
                
            elif drawing_type == "SITE_PLAN":
                quantities.extend(self._extract_earthwork_volumes(text))
                quantities.extend(self._extract_paving_areas(text))
                
            # Apply waste factors
            for quantity in quantities:
                waste_factor = self.waste_factors.get(quantity.material_type, self.waste_factors['DEFAULT'])
                quantity.waste_factor = waste_factor
                quantity.final_quantity = quantity.quantity * (1 + waste_factor)
        
        except Exception as e:
            self.logger.error(f"Error extracting quantities: {str(e)}")
        
        return quantities
    
    def _extract_floor_areas(self, text: str) -> List[QuantityResult]:
        """Extract floor areas from architectural plans"""
        areas = []
        
        # Pattern for area callouts like "ROOM 245 SF", "LIVING 324 SQ FT"
        area_patterns = [
            r'(\w+)\s+(\d+)\s*SF',           # ROOM 245 SF
            r'(\w+)\s+(\d+)\s*SQ\.?\s*FT',   # LIVING 324 SQ FT
            r'AREA[:\s=]+(\d+)\s*SF',        # AREA: 245 SF
            r'(\d+)\s*SF\s+(\w+)',           # 245 SF BEDROOM
        ]
        
        for pattern in area_patterns:
            matches = re.finditer(pattern, text.upper())
            for match in matches:
                try:
                    if len(match.groups()) >= 2:
                        if match.group(2).isdigit():
                            area_value = float(match.group(2))
                        else:
                            area_value = float(match.group(1))
                        
                        areas.append(QuantityResult(
                            material_type='FLOORING',
                            quantity=area_value,
                            unit='SF',
                            confidence=0.8,
                            calculation_method='text_extraction',
                            waste_factor=0.0,  # Will be set later
                            final_quantity=0.0  # Will be calculated later
                        ))
                except (ValueError, IndexError):
                    continue
        
        return areas
    
    def _extract_door_window_counts(self, text: str) -> List[QuantityResult]:
        """Extract door and window counts"""
        items = []
        
        # Count door references
        door_matches = re.findall(r'\bD\d+|\bDOOR\s*\d+|\bDR\s*\d+', text.upper())
        if door_matches:
            items.append(QuantityResult(
                material_type='DOORS',
                quantity=len(door_matches),
                unit='EA',
                confidence=0.9,
                calculation_method='symbol_count',
                waste_factor=0.0,
                final_quantity=len(door_matches)
            ))
        
        # Count window references
        window_matches = re.findall(r'\bW\d+|\bWINDOW\s*\d+|\bWIN\s*\d+', text.upper())
        if window_matches:
            items.append(QuantityResult(
                material_type='WINDOWS',
                quantity=len(window_matches),
                unit='EA',
                confidence=0.9,
                calculation_method='symbol_count',
                waste_factor=0.0,
                final_quantity=len(window_matches)
            ))
        
        return items
    
    def _extract_wall_lengths(self, text: str) -> List[QuantityResult]:
        """Extract wall lengths from dimensions"""
        lengths = []
        total_length = 0.0
        
        # Extract dimension callouts
        dimension_patterns = [
            r"(\d+)'-(\d+)\"",  # 12'-6"
            r"(\d+)'-0\"",      # 12'-0"
            r"(\d+)'",          # 12'
        ]
        
        for pattern in dimension_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    feet = int(match.group(1))
                    inches = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                    total_length += feet + (inches / 12.0)
                except (ValueError, IndexError):
                    continue
        
        if total_length > 0:
            lengths.append(QuantityResult(
                material_type='LUMBER',
                quantity=total_length,
                unit='LF',
                confidence=0.7,
                calculation_method='dimension_sum',
                waste_factor=0.0,
                final_quantity=0.0
            ))
        
        return lengths
    
    def _extract_concrete_volumes(self, text: str) -> List[QuantityResult]:
        """Extract concrete volumes from structural plans"""
        volumes = []
        
        # Pattern for concrete callouts like "15 CY", "CONC 8.5 CY"
        concrete_patterns = [
            r'(\d+\.?\d*)\s*CY\s+CONC',     # 15.5 CY CONC
            r'CONC\s+(\d+\.?\d*)\s*CY',     # CONC 15.5 CY
            r'(\d+\.?\d*)\s*CUBIC YARDS',   # 15.5 CUBIC YARDS
            r'CONCRETE\s+(\d+\.?\d*)\s*CY', # CONCRETE 15.5 CY
        ]
        
        for pattern in concrete_patterns:
            matches = re.finditer(pattern, text.upper())
            for match in matches:
                try:
                    volume = float(match.group(1))
                    volumes.append(QuantityResult(
                        material_type='CONCRETE',
                        quantity=volume,
                        unit='CY',
                        confidence=0.9,
                        calculation_method='text_extraction',
                        waste_factor=0.0,
                        final_quantity=0.0
                    ))
                except (ValueError, IndexError):
                    continue
        
        return volumes
    
    def _extract_steel_quantities(self, text: str) -> List[QuantityResult]:
        """Extract steel quantities from structural plans"""
        steel_items = []
        
        # Pattern for steel callouts like "W12x26", "W18x40"
        steel_patterns = [
            r'W(\d+)[xX](\d+)',     # W12x26
            r'HSS(\d+)[xX](\d+)',   # HSS8x6
            r'L(\d+)[xX](\d+)',     # L4x4
        ]
        
        for pattern in steel_patterns:
            matches = re.finditer(pattern, text.upper())
            for match in matches:
                steel_items.append(QuantityResult(
                    material_type='STEEL',
                    quantity=1.0,  # Count of members
                    unit='EA',
                    confidence=0.8,
                    calculation_method='symbol_count',
                    waste_factor=0.0,
                    final_quantity=0.0
                ))
        
        return steel_items
    
    def _extract_formwork_areas(self, text: str) -> List[QuantityResult]:
        """Extract formwork contact areas"""
        formwork = []
        
        # Pattern for formwork callouts
        formwork_patterns = [
            r'FORMWORK\s+(\d+\.?\d*)\s*SF',     # FORMWORK 245 SF
            r'FORM\s+(\d+\.?\d*)\s*SF',         # FORM 245 SF
            r'(\d+\.?\d*)\s*SF\s+FORM',         # 245 SF FORM
        ]
        
        for pattern in formwork_patterns:
            matches = re.finditer(pattern, text.upper())
            for match in matches:
                try:
                    area = float(match.group(1))
                    formwork.append(QuantityResult(
                        material_type='FORMWORK',
                        quantity=area,
                        unit='SF',
                        confidence=0.8,
                        calculation_method='text_extraction',
                        waste_factor=0.15,  # 15% waste for formwork
                        final_quantity=0.0
                    ))
                except (ValueError, IndexError):
                    continue
        
        return formwork
    
    def _extract_earthwork_volumes(self, text: str) -> List[QuantityResult]:
        """Extract earthwork volumes from site plans"""
        earthwork = []
        
        # Pattern for earthwork callouts
        earthwork_patterns = [
            r'CUT\s+(\d+\.?\d*)\s*CY',          # CUT 150 CY
            r'FILL\s+(\d+\.?\d*)\s*CY',         # FILL 75 CY
            r'EXCAVATION\s+(\d+\.?\d*)\s*CY',   # EXCAVATION 200 CY
        ]
        
        for pattern in earthwork_patterns:
            matches = re.finditer(pattern, text.upper())
            for match in matches:
                try:
                    volume = float(match.group(1))
                    earthwork.append(QuantityResult(
                        material_type='EARTHWORK',
                        quantity=volume,
                        unit='CY',
                        confidence=0.8,
                        calculation_method='text_extraction',
                        waste_factor=0.0,  # No waste for earthwork
                        final_quantity=volume
                    ))
                except (ValueError, IndexError):
                    continue
        
        return earthwork
    
    def _extract_paving_areas(self, text: str) -> List[QuantityResult]:
        """Extract paving areas from site plans"""
        paving = []
        
        # Pattern for paving callouts
        paving_patterns = [
            r'PAVING\s+(\d+\.?\d*)\s*SF',       # PAVING 1250 SF
            r'ASPHALT\s+(\d+\.?\d*)\s*SF',      # ASPHALT 1250 SF
            r'PAVEMENT\s+(\d+\.?\d*)\s*SF',     # PAVEMENT 1250 SF
        ]
        
        for pattern in paving_patterns:
            matches = re.finditer(pattern, text.upper())
            for match in matches:
                try:
                    area = float(match.group(1))
                    paving.append(QuantityResult(
                        material_type='PAVING',
                        quantity=area,
                        unit='SF',
                        confidence=0.8,
                        calculation_method='text_extraction',
                        waste_factor=0.02,  # 2% waste for paving
                        final_quantity=0.0
                    ))
                except (ValueError, IndexError):
                    continue
        
        return paving
    
    def convert_units(self, quantity: float, from_unit: str, to_unit: str, material_size: str = None) -> float:
        """Convert between different units"""
        
        if from_unit == to_unit:
            return quantity
        
        # Square feet to square yards
        if from_unit == 'SF' and to_unit == 'SY':
            return quantity * self.unit_conversions['SQ_FT_TO_SQ_YD']
        
        # Cubic feet to cubic yards
        if from_unit == 'CF' and to_unit == 'CY':
            return quantity * self.unit_conversions['CU_FT_TO_CU_YD']
        
        # Linear feet to board feet (requires material size)
        if from_unit == 'LF' and to_unit == 'BF' and material_size:
            multiplier = self.unit_conversions['LIN_FT_TO_BOARD_FT'].get(material_size, 1.0)
            return quantity * multiplier
        
        return quantity  # No conversion available
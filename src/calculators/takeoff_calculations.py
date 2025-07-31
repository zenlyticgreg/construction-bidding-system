import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class MaterialCalculation:
    """Result of material calculation"""
    material_type: str
    base_quantity: float
    unit: str
    unit_price: float
    extended_cost: float
    waste_factor: float
    final_quantity: float
    final_cost: float

class ConcreteCalculator:
    """Calculate concrete quantities and related materials"""
    
    def __init__(self):
        # Concrete calculation factors
        self.formwork_factors = {
            'SLAB_ON_GRADE': 0.0,      # No formwork contact
            'ELEVATED_SLAB': 27.0,     # 27 SF contact per CY
            'WALL': 30.0,              # 30 SF contact per CY average
            'COLUMN': 50.0,            # 50 SF contact per CY
            'BEAM': 40.0,              # 40 SF contact per CY
        }
        
        self.reinforcement_ratios = {
            'LIGHT': 50.0,    # 50 lbs per CY
            'MEDIUM': 100.0,  # 100 lbs per CY
            'HEAVY': 150.0,   # 150 lbs per CY
        }
    
    def calculate_slab_volume(self, length_ft: float, width_ft: float, thickness_in: float) -> float:
        """Calculate slab concrete volume in cubic yards"""
        volume_cf = length_ft * width_ft * (thickness_in / 12.0)
        volume_cy = volume_cf / 27.0
        return round(volume_cy, 2)
    
    def calculate_wall_volume(self, height_ft: float, length_ft: float, thickness_in: float) -> float:
        """Calculate wall concrete volume in cubic yards"""
        volume_cf = height_ft * length_ft * (thickness_in / 12.0)
        volume_cy = volume_cf / 27.0
        return round(volume_cy, 2)
    
    def calculate_formwork_area(self, concrete_volume_cy: float, element_type: str) -> float:
        """Calculate formwork contact area in square feet"""
        factor = self.formwork_factors.get(element_type, 30.0)
        formwork_sf = concrete_volume_cy * factor
        return round(formwork_sf, 1)
    
    def calculate_reinforcement(self, concrete_volume_cy: float, reinforcement_level: str = 'MEDIUM') -> float:
        """Calculate reinforcement weight in pounds"""
        ratio = self.reinforcement_ratios.get(reinforcement_level, 100.0)
        rebar_lbs = concrete_volume_cy * ratio
        return round(rebar_lbs, 0)

class SteelCalculator:
    """Calculate structural steel quantities"""
    
    def __init__(self):
        # AISC weight tables (lbs per linear foot)
        self.steel_weights = {
            # W-Shapes (Wide Flange)
            'W12X26': 26.0,   'W12X30': 30.0,   'W12X35': 35.0,
            'W14X22': 22.0,   'W14X26': 26.0,   'W14X30': 30.0,
            'W16X26': 26.0,   'W16X31': 31.0,   'W16X36': 36.0,
            'W18X35': 35.0,   'W18X40': 40.0,   'W18X46': 46.0,
            'W21X44': 44.0,   'W21X50': 50.0,   'W21X57': 57.0,
            
            # HSS (Hollow Structural Sections)
            'HSS8X8X1/2': 40.7,   'HSS8X6X1/2': 32.6,
            'HSS6X6X1/2': 31.8,   'HSS6X4X1/2': 25.8,
            
            # Angles
            'L4X4X1/2': 12.8,   'L6X6X1/2': 19.6,   'L8X8X1/2': 26.4,
            
            # Channels
            'C12X20.7': 20.7,   'C15X33.9': 33.9,   'C18X42.7': 42.7,
        }
        
        # Connection material factors (percentage of steel weight)
        self.connection_factors = {
            'SIMPLE': 0.05,    # 5% for simple connections
            'MOMENT': 0.12,    # 12% for moment connections
            'COMPLEX': 0.20,   # 20% for complex connections
        }
    
    def calculate_beam_weight(self, size: str, length_ft: float) -> float:
        """Calculate beam weight in pounds"""
        size_clean = size.upper().replace('X', 'X').replace(' ', '')
        weight_per_ft = self.steel_weights.get(size_clean, 0.0)
        total_weight = weight_per_ft * length_ft
        return round(total_weight, 1)
    
    def calculate_column_weight(self, size: str, height_ft: float) -> float:
        """Calculate column weight in pounds"""
        return self.calculate_beam_weight(size, height_ft)
    
    def estimate_connection_material(self, steel_weight_lbs: float, connection_type: str = 'SIMPLE') -> float:
        """Estimate connection material weight"""
        factor = self.connection_factors.get(connection_type, 0.05)
        connection_weight = steel_weight_lbs * factor
        return round(connection_weight, 1)

class LumberCalculator:
    """Calculate lumber quantities"""
    
    def __init__(self):
        # Board foot conversion factors
        self.board_foot_factors = {
            '2X4': 2/3,      # 0.67 BF per LF
            '2X6': 1.0,      # 1.0 BF per LF
            '2X8': 4/3,      # 1.33 BF per LF
            '2X10': 5/3,     # 1.67 BF per LF
            '2X12': 2.0,     # 2.0 BF per LF
            '4X4': 4/3,      # 1.33 BF per LF
            '6X6': 3.0,      # 3.0 BF per LF
            '6X8': 4.0,      # 4.0 BF per LF
            '6X12': 6.0,     # 6.0 BF per LF
        }
        
        # Plywood sheet coverage (SF per sheet)
        self.plywood_coverage = {
            '4X8': 32.0,     # 32 SF per sheet
            '4X10': 40.0,    # 40 SF per sheet
            '5X8': 40.0,     # 40 SF per sheet
        }
    
    def calculate_board_feet(self, thickness_in: float, width_in: float, length_ft: float) -> float:
        """Calculate board feet using the standard formula"""
        board_feet = (thickness_in * width_in * length_ft) / 12.0
        return round(board_feet, 2)
    
    def convert_linear_to_board_feet(self, linear_ft: float, nominal_size: str) -> float:
        """Convert linear feet to board feet for standard lumber sizes"""
        size_key = nominal_size.upper().replace(' ', '').replace('X', 'X')
        factor = self.board_foot_factors.get(size_key, 1.0)
        board_feet = linear_ft * factor
        return round(board_feet, 2)
    
    def calculate_plywood_sheets(self, area_sf: float, sheet_size: str = '4X8') -> int:
        """Calculate number of plywood sheets needed"""
        coverage = self.plywood_coverage.get(sheet_size, 32.0)
        sheets_needed = math.ceil(area_sf / coverage)
        return sheets_needed

class TakeoffCalculationEngine:
    """Main calculation engine that combines all calculators"""
    
    def __init__(self):
        self.concrete_calc = ConcreteCalculator()
        self.steel_calc = SteelCalculator()
        self.lumber_calc = LumberCalculator()
        
        # Standard waste factors
        self.waste_factors = {
            'CONCRETE': 0.05,      # 5%
            'STEEL': 0.05,         # 5%
            'LUMBER': 0.10,        # 10%
            'FORMWORK': 0.15,      # 15%
            'REINFORCEMENT': 0.05, # 5%
            'DRYWALL': 0.10,       # 10%
            'ROOFING': 0.08,       # 8%
            'DEFAULT': 0.10        # 10%
        }
        
        # Estimated unit prices (for demonstration)
        self.unit_prices = {
            'CONCRETE_CY': 150.00,
            'FORMWORK_SF': 8.50,
            'REINFORCEMENT_LB': 0.75,
            'STEEL_LB': 1.25,
            'LUMBER_BF': 0.85,
            'PLYWOOD_SHEET': 45.00,
            'DRYWALL_SF': 1.20,
        }
    
    def calculate_material_costs(self, quantities: List, material_type: str) -> List[MaterialCalculation]:
        """Calculate costs for material quantities"""
        calculations = []
        
        for quantity_item in quantities:
            try:
                # Get base parameters
                base_quantity = quantity_item.quantity
                unit = quantity_item.unit
                
                # Determine unit price
                price_key = f"{material_type}_{unit}"
                unit_price = self.unit_prices.get(price_key, 1.00)
                
                # Calculate base cost
                extended_cost = base_quantity * unit_price
                
                # Apply waste factor
                waste_factor = self.waste_factors.get(material_type, self.waste_factors['DEFAULT'])
                final_quantity = base_quantity * (1.0 + waste_factor)
                final_cost = final_quantity * unit_price
                
                calculation = MaterialCalculation(
                    material_type=material_type,
                    base_quantity=base_quantity,
                    unit=unit,
                    unit_price=unit_price,
                    extended_cost=extended_cost,
                    waste_factor=waste_factor,
                    final_quantity=final_quantity,
                    final_cost=final_cost
                )
                
                calculations.append(calculation)
                
            except Exception as e:
                continue
        
        return calculations
    
    def calculate_lumber_requirements_from_caltrans(self, caltrans_quantities: Dict) -> Dict:
        """Calculate lumber requirements from CalTrans terminology"""
        lumber_requirements = {
            'formwork_lumber_bf': 0.0,
            'structural_lumber_bf': 0.0,
            'blocking_lumber_bf': 0.0,
            'total_lumber_bf': 0.0,
            'plywood_sheets': 0,
            'estimated_cost': 0.0
        }
        
        # Process CalTrans terms
        for term, data in caltrans_quantities.items():
            quantity = data.get('quantity', 0)
            
            if term == 'BALUSTER':
                # Heavy formwork for concrete posts
                lumber_requirements['formwork_lumber_bf'] += quantity * 25.0  # 25 BF per baluster
                lumber_requirements['plywood_sheets'] += math.ceil(quantity * 0.5)  # 0.5 sheets per baluster
                
            elif term == 'BLOCKOUT':
                # Temporary formwork
                lumber_requirements['formwork_lumber_bf'] += quantity * 8.0   # 8 BF per blockout
                
            elif term == 'FALSEWORK':
                # Heavy structural lumber
                lumber_requirements['structural_lumber_bf'] += quantity * 150.0  # 150 BF per unit
                
            elif term == 'STAMPED_CONCRETE':
                # Textured form lumber
                area_sf = quantity
                lumber_requirements['formwork_lumber_bf'] += area_sf * 0.25   # 0.25 BF per SF
                lumber_requirements['plywood_sheets'] += math.ceil(area_sf / 32)  # 32 SF per sheet
                
            elif term == 'RETAINING_WALL':
                # Wall formwork
                volume_cy = quantity
                formwork_sf = volume_cy * 30.0  # 30 SF formwork per CY
                lumber_requirements['formwork_lumber_bf'] += formwork_sf * 0.3  # 0.3 BF per SF
                lumber_requirements['plywood_sheets'] += math.ceil(formwork_sf / 32)
        
        # Calculate totals
        lumber_requirements['total_lumber_bf'] = (
            lumber_requirements['formwork_lumber_bf'] + 
            lumber_requirements['structural_lumber_bf'] + 
            lumber_requirements['blocking_lumber_bf']
        )
        
        # Estimate costs
        lumber_cost = lumber_requirements['total_lumber_bf'] * self.unit_prices['LUMBER_BF']
        plywood_cost = lumber_requirements['plywood_sheets'] * self.unit_prices['PLYWOOD_SHEET']
        lumber_requirements['estimated_cost'] = lumber_cost + plywood_cost
        
        return lumber_requirements
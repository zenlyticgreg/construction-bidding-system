import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pdfplumber
import time

@dataclass
class DrawingAnalysisResult:
    """Result of advanced plan analysis"""
    drawing_type: str
    scale_info: Dict
    dimensions_found: List[Dict]
    symbols_detected: List[Dict]
    material_specifications: List[str]
    quality_score: float
    processing_time: float
    
@dataclass
class ScaleInfo:
    """Drawing scale information"""
    scale_notation: str
    scale_ratio: float  # pixels per foot
    confidence: float
    detection_method: str

class AdvancedPlanAnalyzer:
    """Advanced construction plan analysis with drawing type detection and symbol recognition"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Drawing type detection patterns
        self.drawing_type_patterns = {
            'ARCHITECTURAL_PLAN': [
                r'FLOOR PLAN', r'PLAN VIEW', r'LEVEL \d+', r'FIRST FLOOR', r'SECOND FLOOR',
                r'ROOM SCHEDULE', r'DOOR SCHEDULE', r'WINDOW SCHEDULE', r'ARCHITECTURAL'
            ],
            'STRUCTURAL_PLAN': [
                r'FOUNDATION PLAN', r'FRAMING PLAN', r'STRUCTURAL PLAN', 
                r'W\d+[xX]\d+', r'HSS\d+', r'BEAM SCHEDULE', r'COLUMN SCHEDULE',
                r'STRUCTURAL', r'FOUNDATION', r'FRAMING'
            ],
            'ELEVATION': [
                r'ELEVATION', r'ELEV\.', r'NORTH ELEVATION', r'SOUTH ELEVATION',
                r'EAST ELEVATION', r'WEST ELEVATION', r'EXTERIOR ELEVATION'
            ],
            'SECTION': [
                r'SECTION', r'SECT\.', r'BUILDING SECTION', r'WALL SECTION',
                r'DETAIL SECTION'
            ],
            'MEP_PLAN': [
                r'ELECTRICAL PLAN', r'PLUMBING PLAN', r'MECHANICAL PLAN',
                r'HVAC PLAN', r'LIGHTING PLAN', r'POWER PLAN', r'MEP'
            ],
            'SITE_PLAN': [
                r'SITE PLAN', r'PLOT PLAN', r'SURVEY', r'TOPOGRAPHIC',
                r'UTILITY PLAN', r'GRADING PLAN', r'CIVIL'
            ]
        }
        
        # Scale detection patterns
        self.scale_patterns = [
            r'SCALE[:\s=]+(\d+/\d+)\"?\s*=\s*(\d+)[\'-]?(\d+)?\"?',  # 1/4"=1'-0"
            r'(\d+)\"?\s*=\s*(\d+)[\'-]?(\d+)?\"?',  # 1"=10'
            r'SCALE[:\s=]+(\d+:\d+)',  # Scale: 1:48
            r'1:(\d+)',  # 1:48
        ]
        
        # Material specification keywords
        self.material_keywords = {
            'CONCRETE': ['CONCRETE', 'CONC', 'CIP', 'CAST IN PLACE', 'f\'c'],
            'STEEL': ['STEEL', 'W\d+X\d+', 'HSS', 'L\d+X\d+', 'AISC'],
            'LUMBER': ['LUMBER', 'WOOD', 'TIMBER', '\d+X\d+', 'DOUGLAS FIR', 'SOUTHERN PINE'],
            'MASONRY': ['MASONRY', 'BRICK', 'BLOCK', 'CMU', 'CONCRETE MASONRY'],
            'DRYWALL': ['DRYWALL', 'GWB', 'GYPSUM', 'SHEETROCK'],
            'ROOFING': ['ROOFING', 'ROOF', 'SHINGLE', 'MEMBRANE', 'TPO', 'EPDM']
        }
    
    def analyze_pdf(self, pdf_path: str) -> DrawingAnalysisResult:
        """Main method to analyze a construction drawing PDF"""
        start_time = time.time()
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract text from all pages
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""
                
                # Analyze drawing type
                drawing_type = self.analyze_drawing_type(full_text)
                
                # Extract scale information
                scale_info = self.extract_scale_information(full_text)
                
                # Detect dimensions (placeholder)
                dimensions_found = self.detect_dimensions(full_text)
                
                # Identify symbols (placeholder)
                symbols_detected = self.identify_symbols(full_text)
                
                # Extract material specifications
                material_specs = self.extract_material_specifications(full_text)
                
                # Calculate quality score
                quality_score = self.calculate_quality_score(
                    drawing_type, scale_info, dimensions_found, symbols_detected
                )
                
                processing_time = time.time() - start_time
                
                return DrawingAnalysisResult(
                    drawing_type=drawing_type,
                    scale_info=scale_info,
                    dimensions_found=dimensions_found,
                    symbols_detected=symbols_detected,
                    material_specifications=material_specs,
                    quality_score=quality_score,
                    processing_time=processing_time
                )
                
        except Exception as e:
            self.logger.error(f"Error analyzing PDF: {str(e)}")
            return DrawingAnalysisResult(
                drawing_type="UNKNOWN",
                scale_info={},
                dimensions_found=[],
                symbols_detected=[],
                material_specifications=[],
                quality_score=0.0,
                processing_time=time.time() - start_time
            )
    
    def analyze_drawing_type(self, text: str) -> str:
        """Detect the type of construction drawing"""
        text_upper = text.upper()
        
        # Score each drawing type
        type_scores = {}
        for drawing_type, patterns in self.drawing_type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_upper))
                score += matches
            type_scores[drawing_type] = score
        
        # Return the type with highest score
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        return "GENERAL_CONSTRUCTION"
    
    def extract_scale_information(self, text: str) -> Dict:
        """Extract scale information from drawing"""
        text_upper = text.upper()
        
        for pattern in self.scale_patterns:
            match = re.search(pattern, text_upper)
            if match:
                try:
                    # Parse different scale formats
                    if '/' in match.group(1):  # 1/4"=1'-0"
                        numerator, denominator = match.group(1).split('/')
                        scale_ratio = float(denominator) / float(numerator)
                        scale_notation = match.group(0)
                    else:  # 1:48
                        scale_ratio = float(match.group(1))
                        scale_notation = f"1:{match.group(1)}"
                    
                    return {
                        'scale_notation': scale_notation,
                        'scale_ratio': scale_ratio,
                        'confidence': 0.9,
                        'detection_method': 'regex_pattern'
                    }
                except (ValueError, IndexError):
                    continue
        
        # Default scale if none detected
        return {
            'scale_notation': 'UNKNOWN',
            'scale_ratio': 48.0,  # Assume 1/4"=1'
            'confidence': 0.3,
            'detection_method': 'default_assumption'
        }
    
    def detect_dimensions(self, text: str) -> List[Dict]:
        """Detect dimension callouts in the drawing text"""
        dimensions = []
        
        # Pattern for dimension callouts like 12'-6", 8'-0", 24'-6"
        dimension_patterns = [
            r"(\d+)'-(\d+)\"",  # 12'-6"
            r"(\d+)'-(\d+)",    # 12'-6
            r"(\d+)'",          # 12'
            r"(\d+)\"",         # 24"
        ]
        
        for pattern in dimension_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                dimensions.append({
                    'text': match.group(0),
                    'position': match.span(),
                    'feet': int(match.group(1)) if match.group(1) else 0,
                    'inches': int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                })
        
        return dimensions
    
    def identify_symbols(self, text: str) -> List[Dict]:
        """Identify construction symbols mentioned in text"""
        symbols = []
        
        # Door symbols
        door_matches = re.finditer(r'DOOR|DR\.|\bD\d+', text.upper())
        for match in door_matches:
            symbols.append({
                'type': 'DOOR',
                'text': match.group(0),
                'position': match.span()
            })
        
        # Window symbols
        window_matches = re.finditer(r'WINDOW|WIN\.|\bW\d+', text.upper())
        for match in window_matches:
            symbols.append({
                'type': 'WINDOW',
                'text': match.group(0),
                'position': match.span()
            })
        
        return symbols
    
    def extract_material_specifications(self, text: str) -> List[str]:
        """Extract material specifications from drawing notes"""
        materials_found = []
        text_upper = text.upper()
        
        for material_type, keywords in self.material_keywords.items():
            for keyword in keywords:
                if re.search(keyword, text_upper):
                    if material_type not in materials_found:
                        materials_found.append(material_type)
                    break
        
        return materials_found
    
    def calculate_quality_score(self, drawing_type: str, scale_info: Dict, 
                              dimensions: List, symbols: List) -> float:
        """Calculate overall quality score for the analysis"""
        score = 0.0
        
        # Drawing type detection (25 points)
        if drawing_type != "UNKNOWN":
            score += 25.0
        
        # Scale detection (25 points)
        if scale_info.get('confidence', 0) > 0.5:
            score += 25.0 * scale_info['confidence']
        
        # Dimensions found (25 points)
        if dimensions:
            score += min(25.0, len(dimensions) * 2.5)
        
        # Symbols detected (25 points)
        if symbols:
            score += min(25.0, len(symbols) * 5.0)
        
        return min(100.0, score)
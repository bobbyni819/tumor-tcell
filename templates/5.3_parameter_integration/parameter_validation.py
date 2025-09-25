"""
Parameter Validation Template
============================

Template for parameter validation and conversion utilities based on tumor-tcell patterns.

This template provides:
- Unit conversion and validation
- Biological range checking  
- Parameter consistency validation
- Error handling and reporting

Usage:
    from parameter_validation import ParameterValidator, validate_parameter_set
    
    validator = ParameterValidator()
    validated_params = validator.validate_tumor_parameters(raw_params)
"""

import math
import warnings
from typing import Dict, Any, Optional, Tuple, List
from scipy import constants
from vivarium.library.units import units, Quantity

# Standard units and constants from tumor-tcell patterns
LENGTH_UNIT = units.um
MASS_UNIT = units.ng
TIME_UNIT = units.s
CONCENTRATION_UNIT = units.ng / units.mL
VELOCITY_UNIT = units.um / units.min
AVOGADRO = constants.N_A
PI = math.pi


class ParameterValidationError(Exception):
    """Custom exception for parameter validation errors"""
    pass


class ParameterWarning(UserWarning):
    """Custom warning for parameter validation concerns"""
    pass


class ParameterValidator:
    """
    Parameter validation utility based on biological constraints and unit requirements.
    
    Provides validation for:
    - Unit consistency and conversion
    - Biological feasibility ranges
    - Parameter interdependencies
    - Literature-based bounds checking
    """
    
    def __init__(self):
        self.validation_rules = self._define_validation_rules()
        self.unit_conversions = self._define_unit_conversions()
        self.biological_ranges = self._define_biological_ranges()
    
    def _define_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Define validation rules for different parameter types"""
        return {
            'physical': {
                'diameter': {
                    'min_value': 1.0,
                    'max_value': 50.0,
                    'units': LENGTH_UNIT,
                    'biological_context': 'Cell diameter must be within observed biological range'
                },
                'mass': {
                    'min_value': 0.1,
                    'max_value': 100.0,
                    'units': MASS_UNIT,
                    'biological_context': 'Cell mass must be physiologically reasonable'
                }
            },
            'rates': {
                'growth_rate': {
                    'min_value': 0.0,
                    'max_value': 2.0,
                    'units': None,
                    'biological_context': 'Growth rate probability must be between 0 and 1 (or up to 2 for very aggressive tumors)'
                },
                'death_rate': {
                    'min_value': 0.0,
                    'max_value': 1.0,
                    'units': None,
                    'biological_context': 'Death rate probability must be between 0 and 1'
                }
            },
            'molecular': {
                'concentration': {
                    'min_value': 1e-6,
                    'max_value': 1e6,
                    'units': CONCENTRATION_UNIT,
                    'biological_context': 'Molecular concentrations must be within physiological range'
                },
                'molecular_weight': {
                    'min_value': 100.0,
                    'max_value': 1e6,
                    'units': units.g / units.mol,
                    'biological_context': 'Molecular weight must be reasonable for biological molecules'
                }
            },
            'temporal': {
                'time_constant': {
                    'min_value': 1.0,
                    'max_value': 864000.0,  # 10 days in seconds
                    'units': TIME_UNIT,
                    'biological_context': 'Time constants must be within relevant biological timescales'
                }
            }
        }
    
    def _define_unit_conversions(self) -> Dict[str, Any]:
        """Define standard unit conversions for biological parameters"""
        return {
            'length': {
                'standard': LENGTH_UNIT,
                'conversions': {
                    'nm': units.nm,
                    'um': units.um,
                    'mm': units.mm,
                    'cm': units.cm
                }
            },
            'mass': {
                'standard': MASS_UNIT,
                'conversions': {
                    'pg': units.pg,
                    'ng': units.ng,
                    'ug': units.ug,
                    'mg': units.mg
                }
            },
            'time': {
                'standard': TIME_UNIT,
                'conversions': {
                    'ms': units.ms,
                    's': units.s,
                    'min': units.min,
                    'hour': units.hour,
                    'day': units.day
                }
            },
            'concentration': {
                'standard': CONCENTRATION_UNIT,
                'conversions': {
                    'ng_mL': units.ng / units.mL,
                    'ug_mL': units.ug / units.mL,
                    'mg_mL': units.mg / units.mL,
                    'M': units.mol / units.L,
                    'mM': units.mmol / units.L
                }
            }
        }
    
    def _define_biological_ranges(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Define biologically feasible ranges for different cell types"""
        return {
            'tumor_cell': {
                'diameter_um': (5.0, 30.0),
                'mass_ng': (1.0, 50.0),
                'growth_rate_per_day': (0.1, 1.5),
                'death_rate_per_day': (0.0, 0.8)
            },
            't_cell': {
                'diameter_um': (4.0, 12.0),
                'mass_ng': (0.5, 10.0),
                'migration_um_per_min': (1.0, 20.0),
                'activation_time_hours': (1.0, 24.0)
            },
            'dendritic_cell': {
                'diameter_um': (6.0, 15.0),
                'mass_ng': (0.8, 15.0),
                'migration_um_per_min': (1.0, 25.0),
                'activation_threshold': (1e5, 1e8)
            }
        }
    
    def validate_parameter(self, name: str, value: Any, expected_type: str = None) -> Tuple[Any, List[str]]:
        """
        Validate a single parameter value.
        
        Args:
            name: Parameter name
            value: Parameter value (may include units)
            expected_type: Expected parameter type (physical, rates, molecular, temporal)
        
        Returns:
            Tuple of (validated_value, list_of_warnings)
        """
        warnings_list = []
        
        # Handle None values
        if value is None:
            raise ParameterValidationError(f"Parameter '{name}' cannot be None")
        
        # Convert to standard units if applicable
        if isinstance(value, Quantity):
            converted_value = self._convert_to_standard_units(name, value)
        else:
            converted_value = value
        
        # Apply biological range checking
        if expected_type and expected_type in self.validation_rules:
            rules = self.validation_rules[expected_type]
            if name in rules:
                rule = rules[name]
                validated_value, rule_warnings = self._apply_validation_rule(name, converted_value, rule)
                warnings_list.extend(rule_warnings)
                converted_value = validated_value
        
        return converted_value, warnings_list
    
    def _convert_to_standard_units(self, name: str, value: Quantity) -> Quantity:
        """Convert parameter to standard units"""
        # Determine parameter category based on name patterns
        if any(keyword in name.lower() for keyword in ['diameter', 'length', 'distance', 'radius']):
            return value.to(LENGTH_UNIT)
        elif any(keyword in name.lower() for keyword in ['mass', 'weight']):
            return value.to(MASS_UNIT)
        elif any(keyword in name.lower() for keyword in ['time', 'duration', 'period']):
            return value.to(TIME_UNIT)
        elif any(keyword in name.lower() for keyword in ['concentration', 'conc']):
            return value.to(CONCENTRATION_UNIT)
        elif any(keyword in name.lower() for keyword in ['velocity', 'speed', 'migration']):
            return value.to(VELOCITY_UNIT)
        else:
            return value
    
    def _apply_validation_rule(self, name: str, value: Any, rule: Dict[str, Any]) -> Tuple[Any, List[str]]:
        """Apply validation rule to parameter value"""
        warnings_list = []
        
        # Extract numeric value for range checking
        if isinstance(value, Quantity):
            numeric_value = value.magnitude
        else:
            numeric_value = value
        
        # Check minimum value
        if 'min_value' in rule and numeric_value < rule['min_value']:
            warnings_list.append(
                f"Parameter '{name}' value {numeric_value} is below biological minimum {rule['min_value']}. "
                f"Context: {rule.get('biological_context', 'No context provided')}"
            )
        
        # Check maximum value
        if 'max_value' in rule and numeric_value > rule['max_value']:
            warnings_list.append(
                f"Parameter '{name}' value {numeric_value} exceeds biological maximum {rule['max_value']}. "
                f"Context: {rule.get('biological_context', 'No context provided')}"
            )
        
        return value, warnings_list
    
    def validate_tumor_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tumor cell parameters based on biological constraints"""
        validated_params = {}
        all_warnings = []
        
        # Validate physical parameters
        physical_params = ['diameter', 'mass']
        for param in physical_params:
            if param in parameters:
                validated_value, warnings = self.validate_parameter(param, parameters[param], 'physical')
                validated_params[param] = validated_value
                all_warnings.extend(warnings)
        
        # Validate rate parameters
        rate_params = ['PDL1n_growth', 'death_apoptosis']
        for param in rate_params:
            if param in parameters:
                validated_value, warnings = self.validate_parameter(param, parameters[param], 'rates')
                validated_params[param] = validated_value
                all_warnings.extend(warnings)
        
        # Validate molecular parameters
        molecular_params = ['IFNg_MW', 'tumor_debris_amount']
        for param in molecular_params:
            if param in parameters:
                validated_value, warnings = self.validate_parameter(param, parameters[param], 'molecular')
                validated_params[param] = validated_value
                all_warnings.extend(warnings)
        
        # Apply tumor-specific consistency checks
        consistency_warnings = self._check_tumor_parameter_consistency(validated_params)
        all_warnings.extend(consistency_warnings)
        
        # Report warnings
        for warning in all_warnings:
            warnings.warn(warning, ParameterWarning)
        
        return validated_params
    
    def validate_tcell_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate T cell parameters based on biological constraints"""
        validated_params = {}
        all_warnings = []
        
        # Validate physical parameters
        physical_params = ['diameter', 'mass']
        for param in physical_params:
            if param in parameters:
                validated_value, warnings = self.validate_parameter(param, parameters[param], 'physical')
                validated_params[param] = validated_value
                all_warnings.extend(warnings)
        
        # Validate temporal parameters
        temporal_params = ['activation_time', 'activation_refractory_time']
        for param in temporal_params:
            if param in parameters:
                validated_value, warnings = self.validate_parameter(param, parameters[param], 'temporal')
                validated_params[param] = validated_value
                all_warnings.extend(warnings)
        
        # Apply T cell-specific consistency checks
        consistency_warnings = self._check_tcell_parameter_consistency(validated_params)
        all_warnings.extend(consistency_warnings)
        
        # Report warnings
        for warning in all_warnings:
            warnings.warn(warning, ParameterWarning)
        
        return validated_params
    
    def _check_tumor_parameter_consistency(self, parameters: Dict[str, Any]) -> List[str]:
        """Check consistency between tumor cell parameters"""
        warnings_list = []
        
        # Check if growth rate is consistent with cell size
        if 'PDL1n_growth' in parameters and 'diameter' in parameters:
            growth_rate = parameters['PDL1n_growth']
            diameter = parameters['diameter']
            
            # Large cells typically grow slower
            if isinstance(diameter, Quantity):
                diameter_magnitude = diameter.magnitude
            else:
                diameter_magnitude = diameter
            
            if diameter_magnitude > 20.0 and growth_rate > 0.8:
                warnings_list.append(
                    "Large tumor cells (>20 μm) with high growth rate (>0.8) may be biologically unrealistic"
                )
        
        # Check if death rate and growth rate are balanced
        if 'PDL1n_growth' in parameters and 'death_apoptosis' in parameters:
            growth_rate = parameters['PDL1n_growth']
            death_rate = parameters['death_apoptosis']
            
            if death_rate > growth_rate:
                warnings_list.append(
                    "Death rate exceeds growth rate, may lead to population decline"
                )
        
        return warnings_list
    
    def _check_tcell_parameter_consistency(self, parameters: Dict[str, Any]) -> List[str]:
        """Check consistency between T cell parameters"""
        warnings_list = []
        
        # Check activation timing consistency
        if 'activation_time' in parameters and 'activation_refractory_time' in parameters:
            activation_time = parameters['activation_time']
            refractory_time = parameters['activation_refractory_time']
            
            if isinstance(activation_time, Quantity):
                activation_magnitude = activation_time.magnitude
            else:
                activation_magnitude = activation_time
            
            if isinstance(refractory_time, Quantity):
                refractory_magnitude = refractory_time.magnitude
            else:
                refractory_magnitude = refractory_time
            
            if refractory_magnitude < activation_magnitude:
                warnings_list.append(
                    "Refractory time should typically be longer than activation time"
                )
        
        return warnings_list


def validate_parameter_set(parameters: Dict[str, Any], cell_type: str) -> Dict[str, Any]:
    """
    Convenience function to validate a complete parameter set for a specific cell type.
    
    Args:
        parameters: Dictionary of parameters to validate
        cell_type: Type of cell ('tumor', 'tcell', 'dendritic')
    
    Returns:
        Dictionary of validated parameters
    """
    validator = ParameterValidator()
    
    if cell_type == 'tumor':
        return validator.validate_tumor_parameters(parameters)
    elif cell_type == 'tcell':
        return validator.validate_tcell_parameters(parameters)
    else:
        raise ValueError(f"Validation not implemented for cell type: {cell_type}")


def check_parameter_units(parameters: Dict[str, Any]) -> Dict[str, str]:
    """
    Check and report the units of all parameters.
    
    Args:
        parameters: Dictionary of parameters
    
    Returns:
        Dictionary mapping parameter names to their units (as strings)
    """
    parameter_units = {}
    
    for name, value in parameters.items():
        if isinstance(value, Quantity):
            parameter_units[name] = str(value.units)
        else:
            parameter_units[name] = 'dimensionless'
    
    return parameter_units


def convert_parameter_units(parameters: Dict[str, Any], target_units: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert parameters to target units.
    
    Args:
        parameters: Dictionary of parameters to convert
        target_units: Dictionary mapping parameter names to target units
    
    Returns:
        Dictionary of parameters with converted units
    """
    converted_params = {}
    
    for name, value in parameters.items():
        if name in target_units and isinstance(value, Quantity):
            converted_params[name] = value.to(target_units[name])
        else:
            converted_params[name] = value
    
    return converted_params


# Example usage and testing
if __name__ == '__main__':
    # Example tumor cell parameters for validation
    tumor_params = {
        'diameter': 15.0 * LENGTH_UNIT,
        'mass': 8.0 * MASS_UNIT,
        'PDL1n_growth': 0.6,
        'death_apoptosis': 0.5,
        'IFNg_MW': 17000 * units.g / units.mol
    }
    
    # Validate parameters
    try:
        validated_params = validate_parameter_set(tumor_params, 'tumor')
        print("Tumor parameters validated successfully")
        
        # Check units
        units_info = check_parameter_units(validated_params)
        print(f"Parameter units: {units_info}")
        
    except ParameterValidationError as e:
        print(f"Validation error: {e}")
    
    # Example T cell parameters
    tcell_params = {
        'diameter': 7.5 * LENGTH_UNIT,
        'mass': 2.0 * MASS_UNIT,
        'activation_time': 6 * units.hour,
        'activation_refractory_time': 18 * units.hour
    }
    
    # Validate T cell parameters
    try:
        validated_tcell_params = validate_parameter_set(tcell_params, 'tcell')
        print("T cell parameters validated successfully")
        
    except ParameterValidationError as e:
        print(f"T cell validation error: {e}")
    
    print("Parameter validation template created successfully!")
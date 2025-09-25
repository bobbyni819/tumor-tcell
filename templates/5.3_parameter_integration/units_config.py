"""
Units Configuration Template
===========================

Standard units configuration for biological modeling based on tumor-tcell patterns.

This template provides:
- Standard unit definitions for biological systems
- Unit conversion utilities
- Dimension analysis helpers
- Common biological unit combinations

Usage:
    from units_config import BioUnits, convert_units, validate_dimensions
    
    bio_units = BioUnits()
    cellular_length = 10 * bio_units.CELLULAR_LENGTH
    converted_value = convert_units(cellular_length, bio_units.TISSUE_LENGTH)
"""

import math
from typing import Dict, Any, Optional, Union
from scipy import constants
from vivarium.library.units import units, Quantity

# Physical constants frequently used in biological modeling
AVOGADRO = constants.N_A  # Avogadro's number
BOLTZMANN = constants.k   # Boltzmann constant
PI = math.pi             # Pi constant
GAS_CONSTANT = constants.R  # Universal gas constant


class BioUnits:
    """
    Standardized biological units based on tumor-tcell repository patterns.
    
    Organizes units by biological scale and application:
    - Cellular scale (micrometers, nanograms, seconds)
    - Tissue scale (millimeters, micrograms, minutes)
    - Molecular scale (nanometers, picograms, milliseconds)
    - Concentration units for different contexts
    """
    
    def __init__(self):
        self._define_length_units()
        self._define_mass_units()
        self._define_time_units()
        self._define_concentration_units()
        self._define_velocity_units()
        self._define_area_volume_units()
        self._define_rate_units()
        self._define_molecular_units()
    
    def _define_length_units(self):
        """Define length units for different biological scales"""
        # Molecular scale
        self.MOLECULAR_LENGTH = units.nm      # nanometers - for molecular distances
        self.MEMBRANE_THICKNESS = units.nm    # nanometers - for membrane properties
        
        # Cellular scale (primary scale for tumor-tcell modeling)
        self.CELLULAR_LENGTH = units.um       # micrometers - primary cellular length
        self.CELL_DIAMETER = units.um         # micrometers - cell diameter measurements
        self.ORGANELLE_SIZE = units.um        # micrometers - organelle dimensions
        
        # Tissue scale
        self.TISSUE_LENGTH = units.mm         # millimeters - tissue dimensions
        self.ORGAN_LENGTH = units.cm          # centimeters - organ scale
        
        # Default length unit (matches tumor-tcell patterns)
        self.LENGTH = self.CELLULAR_LENGTH
    
    def _define_mass_units(self):
        """Define mass units for different biological contexts"""
        # Molecular scale
        self.MOLECULAR_MASS = units.pg        # picograms - for small molecules
        self.PROTEIN_MASS = units.ng          # nanograms - for proteins
        
        # Cellular scale (primary scale for tumor-tcell modeling)
        self.CELLULAR_MASS = units.ng         # nanograms - primary cellular mass
        self.CELL_MASS = units.ng             # nanograms - total cell mass
        
        # Tissue scale
        self.TISSUE_MASS = units.ug           # micrograms - tissue samples
        self.ORGAN_MASS = units.mg            # milligrams - small organs
        
        # Default mass unit (matches tumor-tcell patterns)
        self.MASS = self.CELLULAR_MASS
    
    def _define_time_units(self):
        """Define time units for different biological processes"""
        # Fast molecular processes
        self.MOLECULAR_TIME = units.ms        # milliseconds - fast reactions
        self.BINDING_TIME = units.s           # seconds - binding kinetics
        
        # Cellular processes (primary scale for tumor-tcell modeling)
        self.CELLULAR_TIME = units.s          # seconds - primary time unit
        self.PROCESS_TIME = units.min         # minutes - cellular processes
        
        # Long-term processes
        self.CELL_CYCLE_TIME = units.hour     # hours - cell cycle, activation
        self.EXPERIMENT_TIME = units.day      # days - experimental timescales
        
        # Default time unit (matches tumor-tcell patterns)
        self.TIME = self.CELLULAR_TIME
    
    def _define_concentration_units(self):
        """Define concentration units for different contexts"""
        # Mass-based concentrations (primary for tumor-tcell)
        self.MASS_CONCENTRATION = units.ng / units.mL     # ng/mL - primary concentration
        self.PROTEIN_CONC = units.ug / units.mL           # μg/mL - protein concentrations
        self.DRUG_CONC = units.mg / units.mL              # mg/mL - drug concentrations
        
        # Molar concentrations
        self.MOLAR_CONC = units.mol / units.L             # M - molar concentration
        self.MILLIMOLAR_CONC = units.mmol / units.L       # mM - millimolar
        self.MICROMOLAR_CONC = units.umol / units.L       # μM - micromolar
        self.NANOMOLAR_CONC = units.nmol / units.L        # nM - nanomolar
        
        # Cell-based concentrations
        self.MOLECULES_PER_CELL = 1 / units.cell          # molecules per cell
        self.CELLS_PER_VOLUME = units.cell / units.mL     # cells per volume
        
        # Default concentration unit (matches tumor-tcell patterns)
        self.CONCENTRATION = self.MASS_CONCENTRATION
    
    def _define_velocity_units(self):
        """Define velocity units for cellular migration"""
        # Cellular migration (primary for tumor-tcell)
        self.CELL_VELOCITY = units.um / units.min         # μm/min - cell migration
        self.DIFFUSION_RATE = units.um**2 / units.s       # μm²/s - molecular diffusion
        
        # Alternative velocity units
        self.FAST_VELOCITY = units.um / units.s           # μm/s - fast processes
        self.SLOW_VELOCITY = units.um / units.hour        # μm/h - slow migration
        
        # Default velocity unit (matches tumor-tcell patterns)
        self.VELOCITY = self.CELL_VELOCITY
    
    def _define_area_volume_units(self):
        """Define area and volume units for cellular contexts"""
        # Areas
        self.CELL_AREA = units.um**2                      # μm² - cell surface area
        self.MEMBRANE_AREA = units.nm**2                  # nm² - membrane patches
        self.TISSUE_AREA = units.mm**2                    # mm² - tissue sections
        
        # Volumes
        self.CELL_VOLUME = units.um**3                    # μm³ - cell volume
        self.ORGANELLE_VOLUME = units.um**3               # μm³ - organelle volume
        self.CULTURE_VOLUME = units.mL                    # mL - culture medium
        
        # Default volume unit
        self.VOLUME = self.CELL_VOLUME
    
    def _define_rate_units(self):
        """Define rate units for biological processes"""
        # Process rates
        self.GROWTH_RATE = 1 / units.day                  # per day - growth rates
        self.BINDING_RATE = 1 / (units.M * units.s)       # M⁻¹s⁻¹ - binding kinetics
        self.CATALYTIC_RATE = 1 / units.s                 # s⁻¹ - enzyme kinetics
        
        # Production rates
        self.PRODUCTION_RATE = 1 / units.s                # per second - molecule production
        self.SECRETION_RATE = units.ng / (units.cell * units.s)  # ng/cell/s - secretion
        
        # Death rates
        self.DEATH_RATE = 1 / units.hour                  # per hour - cell death
        self.APOPTOSIS_RATE = 1 / units.day               # per day - apoptosis
    
    def _define_molecular_units(self):
        """Define molecular-specific units"""
        # Molecular weights
        self.MOLECULAR_WEIGHT = units.g / units.mol       # g/mol - molecular weight
        self.DALTON = units.Da                            # Daltons - alternative MW
        
        # Molecular amounts
        self.MOLES = units.mol                            # moles - amount of substance
        self.MOLECULES = 1                                # molecule count (dimensionless)
        
        # Energy units
        self.ENERGY = units.J                             # Joules - energy
        self.THERMAL_ENERGY = units.k * units.K           # kT - thermal energy
    
    def get_standard_units(self) -> Dict[str, Any]:
        """Return dictionary of standard units for each dimension"""
        return {
            'length': self.LENGTH,
            'mass': self.MASS,
            'time': self.TIME,
            'concentration': self.CONCENTRATION,
            'velocity': self.VELOCITY,
            'volume': self.VOLUME,
            'area': self.CELL_AREA,
            'molecular_weight': self.MOLECULAR_WEIGHT
        }
    
    def get_cellular_units(self) -> Dict[str, Any]:
        """Return units optimized for cellular-scale modeling"""
        return {
            'length': self.CELLULAR_LENGTH,
            'mass': self.CELLULAR_MASS,
            'time': self.CELLULAR_TIME,
            'concentration': self.MASS_CONCENTRATION,
            'velocity': self.CELL_VELOCITY,
            'volume': self.CELL_VOLUME
        }
    
    def get_molecular_units(self) -> Dict[str, Any]:
        """Return units optimized for molecular-scale modeling"""
        return {
            'length': self.MOLECULAR_LENGTH,
            'mass': self.MOLECULAR_MASS,
            'time': self.MOLECULAR_TIME,
            'concentration': self.MOLAR_CONC,
            'molecular_weight': self.MOLECULAR_WEIGHT
        }


class UnitConverter:
    """Utility class for unit conversions and validations"""
    
    def __init__(self, bio_units: BioUnits = None):
        self.bio_units = bio_units or BioUnits()
    
    def convert_to_standard(self, value: Quantity, dimension: str) -> Quantity:
        """
        Convert a quantity to the standard unit for its dimension.
        
        Args:
            value: Quantity with units
            dimension: Dimension type ('length', 'mass', 'time', etc.)
        
        Returns:
            Quantity converted to standard units
        """
        standard_units = self.bio_units.get_standard_units()
        
        if dimension not in standard_units:
            raise ValueError(f"Unknown dimension: {dimension}")
        
        return value.to(standard_units[dimension])
    
    def convert_concentration(self, value: Quantity, molecular_weight: Quantity, 
                            target_type: str = 'mass') -> Quantity:
        """
        Convert between mass-based and molar concentrations.
        
        Args:
            value: Concentration value with units
            molecular_weight: Molecular weight of the substance
            target_type: Target concentration type ('mass' or 'molar')
        
        Returns:
            Converted concentration
        """
        if target_type == 'mass':
            # Convert from molar to mass concentration
            if 'mol' in str(value.units):
                return (value * molecular_weight).to(self.bio_units.MASS_CONCENTRATION)
            else:
                return value  # Already mass concentration
        
        elif target_type == 'molar':
            # Convert from mass to molar concentration
            if 'mol' not in str(value.units):
                return (value / molecular_weight).to(self.bio_units.MOLAR_CONC)
            else:
                return value  # Already molar concentration
        
        else:
            raise ValueError(f"Unknown concentration type: {target_type}")
    
    def validate_dimensions(self, value: Quantity, expected_dimension: str) -> bool:
        """
        Validate that a quantity has the expected dimensions.
        
        Args:
            value: Quantity to validate
            expected_dimension: Expected dimension string
        
        Returns:
            True if dimensions match, False otherwise
        """
        # Get expected units for the dimension
        standard_units = self.bio_units.get_standard_units()
        
        if expected_dimension not in standard_units:
            return False
        
        expected_units = standard_units[expected_dimension]
        
        try:
            # Try to convert to expected units
            value.to(expected_units)
            return True
        except:
            return False
    
    def get_magnitude_in_standard_units(self, value: Quantity, dimension: str) -> float:
        """
        Get the magnitude of a quantity in standard units.
        
        Args:
            value: Quantity with units
            dimension: Dimension type
        
        Returns:
            Magnitude in standard units
        """
        standard_value = self.convert_to_standard(value, dimension)
        return standard_value.magnitude


def convert_units(value: Quantity, target_units: Any) -> Quantity:
    """
    Convenience function for unit conversion.
    
    Args:
        value: Quantity to convert
        target_units: Target units
    
    Returns:
        Converted quantity
    """
    return value.to(target_units)


def validate_dimensions(value: Quantity, expected_dimension: str, 
                       bio_units: BioUnits = None) -> bool:
    """
    Convenience function for dimension validation.
    
    Args:
        value: Quantity to validate
        expected_dimension: Expected dimension
        bio_units: BioUnits instance (optional)
    
    Returns:
        True if dimensions are valid
    """
    converter = UnitConverter(bio_units)
    return converter.validate_dimensions(value, expected_dimension)


def create_quantity(magnitude: float, unit_string: str, bio_units: BioUnits = None) -> Quantity:
    """
    Create a quantity from magnitude and unit string.
    
    Args:
        magnitude: Numeric value
        unit_string: String representation of units
        bio_units: BioUnits instance for standard units
    
    Returns:
        Quantity with appropriate units
    """
    if bio_units is None:
        bio_units = BioUnits()
    
    # Map common unit strings to actual units
    unit_mapping = {
        'um': bio_units.CELLULAR_LENGTH,
        'ng': bio_units.CELLULAR_MASS,
        's': bio_units.CELLULAR_TIME,
        'ng/mL': bio_units.MASS_CONCENTRATION,
        'um/min': bio_units.CELL_VELOCITY,
        'um^2': bio_units.CELL_AREA,
        'um^3': bio_units.CELL_VOLUME,
        'g/mol': bio_units.MOLECULAR_WEIGHT
    }
    
    if unit_string in unit_mapping:
        return magnitude * unit_mapping[unit_string]
    else:
        # Try to parse using pint directly
        try:
            return magnitude * units(unit_string)
        except:
            raise ValueError(f"Cannot parse unit string: {unit_string}")


# Predefined unit sets for common use cases
class CommonUnitSets:
    """Predefined unit sets for common biological modeling scenarios"""
    
    @staticmethod
    def tumor_cell_units() -> Dict[str, Any]:
        """Units optimized for tumor cell modeling"""
        bio_units = BioUnits()
        return {
            'diameter': bio_units.CELLULAR_LENGTH,
            'mass': bio_units.CELLULAR_MASS,
            'time_step': bio_units.CELLULAR_TIME,
            'concentration': bio_units.MASS_CONCENTRATION,
            'velocity': bio_units.CELL_VELOCITY,
            'molecular_weight': bio_units.MOLECULAR_WEIGHT
        }
    
    @staticmethod
    def tcell_units() -> Dict[str, Any]:
        """Units optimized for T cell modeling"""
        bio_units = BioUnits()
        return {
            'diameter': bio_units.CELLULAR_LENGTH,
            'mass': bio_units.CELLULAR_MASS,
            'migration_velocity': bio_units.CELL_VELOCITY,
            'activation_time': bio_units.CELL_CYCLE_TIME,
            'concentration': bio_units.MASS_CONCENTRATION
        }
    
    @staticmethod
    def molecular_interaction_units() -> Dict[str, Any]:
        """Units optimized for molecular interaction modeling"""
        bio_units = BioUnits()
        return {
            'binding_rate': bio_units.BINDING_RATE,
            'concentration': bio_units.MOLAR_CONC,
            'molecular_weight': bio_units.MOLECULAR_WEIGHT,
            'diffusion_rate': bio_units.DIFFUSION_RATE,
            'time': bio_units.MOLECULAR_TIME
        }


# Example usage and testing
if __name__ == '__main__':
    # Create BioUnits instance
    bio_units = BioUnits()
    converter = UnitConverter(bio_units)
    
    # Example 1: Create quantities with biological units
    cell_diameter = 15.0 * bio_units.CELLULAR_LENGTH
    cell_mass = 8.0 * bio_units.CELLULAR_MASS
    ifng_concentration = 1.5 * bio_units.MASS_CONCENTRATION
    
    print(f"Cell diameter: {cell_diameter}")
    print(f"Cell mass: {cell_mass}")
    print(f"IFN-gamma concentration: {ifng_concentration}")
    
    # Example 2: Unit conversion
    diameter_in_nm = convert_units(cell_diameter, bio_units.MOLECULAR_LENGTH)
    print(f"Cell diameter in nm: {diameter_in_nm}")
    
    # Example 3: Concentration conversion
    ifng_mw = 17000 * bio_units.MOLECULAR_WEIGHT
    ifng_molar = converter.convert_concentration(ifng_concentration, ifng_mw, 'molar')
    print(f"IFN-gamma in molar: {ifng_molar}")
    
    # Example 4: Dimension validation
    is_valid_length = validate_dimensions(cell_diameter, 'length', bio_units)
    print(f"Cell diameter has valid length dimension: {is_valid_length}")
    
    # Example 5: Standard unit sets
    tumor_units = CommonUnitSets.tumor_cell_units()
    tcell_units = CommonUnitSets.tcell_units()
    
    print(f"Tumor cell units: {tumor_units}")
    print(f"T cell units: {tcell_units}")
    
    # Example 6: Create quantity from string
    velocity = create_quantity(10.0, 'um/min', bio_units)
    print(f"Cell velocity: {velocity}")
    
    print("Units configuration template created successfully!")
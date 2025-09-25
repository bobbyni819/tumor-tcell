"""
Biological Parameter Template
============================

Template for defining biological parameters with proper units, citations, and biological context.
Based on patterns extracted from tumor-tcell repository.

This template provides standardized patterns for:
- Parameter definitions with units and biological context
- Literature citations and references
- Parameter groupings by biological function
- Unit conversion utilities

Usage:
    from biological_parameters import TumorCellParameters, TCellParameters
    
    # Use predefined parameter sets
    tumor_params = TumorCellParameters()
    tcell_params = TCellParameters()
    
    # Customize for specific tissue systems
    custom_params = TumorCellParameters()
    custom_params.update_growth_parameters(growth_rate=0.8)
"""

import math
from scipy import constants
from vivarium.library.units import units

# Standard units for biological modeling
LENGTH_UNIT = units.um  # micrometers for cellular scale
MASS_UNIT = units.ng    # nanograms for cellular mass
TIME_UNIT = units.s     # seconds for molecular processes
CONCENTRATION_UNIT = units.ng / units.mL  # concentration units

# Physical constants
PI = math.pi
AVOGADRO = constants.N_A


class BiologicalParameterBase:
    """Base class for biological parameter definitions"""
    
    def __init__(self):
        self.parameters = {}
        self.citations = {}
        self.biological_context = {}
    
    def add_parameter(self, name, value, units, citation, context):
        """Add a parameter with full documentation"""
        self.parameters[name] = value * units if units else value
        self.citations[name] = citation
        self.biological_context[name] = context
    
    def get_parameter(self, name):
        """Get parameter value with metadata"""
        return {
            'value': self.parameters.get(name),
            'citation': self.citations.get(name),
            'context': self.biological_context.get(name)
        }


class TumorCellParameters(BiologicalParameterBase):
    """
    Tumor cell parameters template based on tumor-tcell repository patterns.
    
    Covers:
    - Physical properties (size, mass)
    - Growth and division rates
    - Death mechanisms and thresholds
    - Molecular production and internalization
    - State transition parameters
    """
    
    def __init__(self):
        super().__init__()
        self._define_physical_parameters()
        self._define_growth_parameters()
        self._define_death_parameters()
        self._define_molecular_parameters()
        self._define_state_parameters()
    
    def _define_physical_parameters(self):
        """Define physical properties of tumor cells"""
        self.add_parameter(
            'diameter', 15, LENGTH_UNIT,
            'Typical tumor cell diameter from microscopy studies',
            'Cell size affects surface area for molecular interactions and spatial constraints'
        )
        
        self.add_parameter(
            'mass', 8, MASS_UNIT,
            'Estimated from cell volume and density measurements',
            'Cell mass affects division mechanics and metabolic requirements'
        )
    
    def _define_growth_parameters(self):
        """Define growth and division parameters"""
        self.add_parameter(
            'PDL1n_growth', 0.6, None,
            'Eden, 2011 - Probability of division in 24 hr',
            'PDL1-negative cells maintain proliferative capacity'
        )
        
        self.add_parameter(
            'initial_PDL1n', 0.9, None,
            'Typical proportion of PDL1-negative cells in tumor',
            'Initial heterogeneity in PDL1 expression affects immune evasion'
        )
    
    def _define_death_parameters(self):
        """Define death mechanisms and thresholds"""
        self.add_parameter(
            'death_apoptosis', 0.5, None,
            'Gong, 2017 - Baseline apoptosis rate negligible compared to growth/killing (0.95 by 5 day)',
            'Background cell death from metabolic stress and DNA damage'
        )
        
        self.add_parameter(
            'cytotoxic_packet_threshold', 128 * 100, None,
            'Betts, 2004; Zhang, 2006 - Need at least 128 packets for death (multiply by 100 for T cell time adjustment)',
            'Threshold for T cell-mediated cytotoxic killing'
        )
    
    def _define_molecular_parameters(self):
        """Define molecular production and internalization"""
        self.add_parameter(
            'Max_IFNg_internalization', 31 / 60, None,
            'A. Celada, 1987 - 1860 molecules/cell/hr degraded, converted to seconds',
            'Rate of IFN-gamma internalization and degradation'
        )
        
        self.add_parameter(
            'IFNg_MW', 17000, units.g / units.mol,
            'Standard molecular weight of IFN-gamma',
            'Molecular weight for concentration conversions'
        )
        
        self.add_parameter(
            'tumor_debris_amount', 1.4e15, None,
            'Apetoh, 2007 - Molecules per cell',
            'Amount of damage-associated molecular patterns (DAMPs) released upon cell death'
        )
    
    def _define_state_parameters(self):
        """Define state transition parameters"""
        self.add_parameter(
            'IFNg_threshold', 15000, None,
            'Calculated from data of incubating 1 ng/mL for 20 mL and 20x10^6 cells and half-life',
            'IFN-gamma threshold for PDL1n to PDL1p transition'
        )
        
        self.add_parameter(
            'PDL1p_PDL1_equilibrium', 5e4, None,
            'Estimated equilibrium amount of PDL1 on cell surface',
            'PDL1 expression level in immune-suppressive state'
        )


class TCellParameters(BiologicalParameterBase):
    """
    T cell parameters template based on tumor-tcell repository patterns.
    
    Covers:
    - Physical properties and migration
    - Activation and exhaustion dynamics
    - Cytokine production
    - Death mechanisms
    - TCR regulation
    """
    
    def __init__(self):
        super().__init__()
        self._define_physical_parameters()
        self._define_activation_parameters()
        self._define_migration_parameters()
        self._define_death_parameters()
        self._define_molecular_parameters()
    
    def _define_physical_parameters(self):
        """Define physical properties of T cells"""
        self.add_parameter(
            'diameter', 7.5, LENGTH_UNIT,
            'Typical T cell diameter from flow cytometry measurements',
            'Smaller than tumor cells, affects migration through tissue'
        )
        
        self.add_parameter(
            'mass', 2, MASS_UNIT,
            'Estimated from cell volume and density',
            'Lower mass than tumor cells, affects migration dynamics'
        )
    
    def _define_activation_parameters(self):
        """Define activation and exhaustion parameters"""
        self.add_parameter(
            'initial_PD1n', 0.8, None,
            'Typical proportion of PD1-negative (non-exhausted) T cells',
            'Initial activation state affects cytotoxic capacity'
        )
        
        self.add_parameter(
            'activation_time', 21600, TIME_UNIT,
            'Salerno, 2017; Gallegos, 2016 - 6 hours of activation and cytokine production',
            'Duration of active cytokine production after stimulation'
        )
        
        self.add_parameter(
            'activation_refractory_time', 43200, TIME_UNIT,
            'Salerno, 2017; Gallegos, 2016 - 18 hour refractory period plus 6 h activation',
            'Recovery time with limited cytokine production after activation'
        )
    
    def _define_migration_parameters(self):
        """Define migration and movement parameters"""
        self.add_parameter(
            'PD1n_migration', 10.0, LENGTH_UNIT / units.min,
            'Boissonnas 2007 - Migration velocity of activated T cells',
            'Non-exhausted T cells migrate faster for tumor surveillance'
        )
        
        self.add_parameter(
            'PD1p_migration', 5.0, LENGTH_UNIT / units.min,
            'Boissonnas 2007 - Reduced migration of exhausted T cells',
            'Exhausted T cells have impaired migration capacity'
        )
    
    def _define_death_parameters(self):
        """Define death mechanisms"""
        self.add_parameter(
            'death_PD1p_14hr', 0.35, None,
            'Petrovas 2007 - 0.7 / 14 hrs death rate for exhausted T cells',
            'Increased death rate in exhausted (PD1-positive) state'
        )
        
        self.add_parameter(
            'PDL1_critical_number', 1e4, None,
            'Threshold number of PDL1 molecules/cell to induce T cell dysfunction',
            'PDL1-PD1 interaction threshold for T cell exhaustion'
        )
    
    def _define_molecular_parameters(self):
        """Define molecular production parameters"""
        self.add_parameter(
            'IFNg_production_PD1n', 2.78e-4, None,
            'Chen, 2009 - IFN-gamma production rate per second for activated T cells',
            'Cytokine production rate in non-exhausted state'
        )
        
        self.add_parameter(
            'cytotoxic_packet_production', 0.5, None,
            'Rate of cytotoxic granule production and release',
            'Perforin/granzyme production for tumor cell killing'
        )


class DendriticCellParameters(BiologicalParameterBase):
    """
    Dendritic cell parameters template based on tumor-tcell repository patterns.
    
    Covers:
    - Physical properties
    - Activation states  
    - Antigen presentation
    - Migration dynamics
    - Molecular interactions
    """
    
    def __init__(self):
        super().__init__()
        self._define_physical_parameters()
        self._define_activation_parameters()
        self._define_migration_parameters()
        self._define_molecular_parameters()
    
    def _define_physical_parameters(self):
        """Define physical properties of dendritic cells"""
        self.add_parameter(
            'diameter', 10.0, LENGTH_UNIT,
            'Morefield, 2005 - Typical dendritic cell diameter',
            'Intermediate size between T cells and tumor cells'
        )
        
        self.add_parameter(
            'mass', 2.0, MASS_UNIT,
            'Estimated from cell volume and density',
            'Similar mass to T cells but with extended dendrites'
        )
    
    def _define_activation_parameters(self):
        """Define activation state parameters"""
        self.add_parameter(
            'activation_threshold', 1e7, None,
            'Tumor debris threshold for dendritic cell activation',
            'DAMP recognition threshold for maturation and activation'
        )
        
        self.add_parameter(
            'death_apoptosis', 0.5, None,
            'Naik, 2008 - Background apoptosis rate',
            'Baseline death rate in tissue environment'
        )
    
    def _define_migration_parameters(self):
        """Define migration parameters"""
        self.add_parameter(
            'velocity_inactive', 3.0, LENGTH_UNIT / units.min,
            'Lammermann, 2008 - 2-5 um/min when inactive',
            'Surveillance migration in inactive state'
        )
        
        self.add_parameter(
            'velocity_active', 12.5, LENGTH_UNIT / units.min,
            'Lammermann, 2008 - 10-15 um/min when active',
            'Rapid migration to lymph nodes after activation'
        )
    
    def _define_molecular_parameters(self):
        """Define molecular interaction parameters"""
        self.add_parameter(
            'tumor_debris_MW', 29000, units.g / units.mol,
            'Apetoh, 2007 - Assumed HMGB1 molecular weight for DAMP recognition',
            'Molecular weight for DAMP concentration calculations'
        )


# Utility functions for parameter management
def create_parameter_set(cell_type, tissue_system=None, custom_params=None):
    """
    Create a parameter set for a specific cell type and tissue system.
    
    Args:
        cell_type (str): Type of cell ('tumor', 'tcell', 'dendritic')
        tissue_system (str): Specific tissue context (e.g., 'breast', 'lung', 'colon')
        custom_params (dict): Custom parameter overrides
    
    Returns:
        BiologicalParameterBase: Configured parameter set
    """
    parameter_classes = {
        'tumor': TumorCellParameters,
        'tcell': TCellParameters,
        'dendritic': DendriticCellParameters
    }
    
    if cell_type not in parameter_classes:
        raise ValueError(f"Unknown cell type: {cell_type}")
    
    param_set = parameter_classes[cell_type]()
    
    # Apply tissue-specific modifications
    if tissue_system:
        param_set = apply_tissue_modifications(param_set, tissue_system)
    
    # Apply custom parameters
    if custom_params:
        for name, value in custom_params.items():
            if name in param_set.parameters:
                param_set.parameters[name] = value
    
    return param_set


def apply_tissue_modifications(param_set, tissue_system):
    """Apply tissue-specific parameter modifications"""
    # Example tissue-specific modifications
    tissue_modifications = {
        'breast': {
            'growth_rate_modifier': 1.2,  # Faster growth in breast tissue
            'vascularization_factor': 0.8  # Lower vascularization
        },
        'lung': {
            'growth_rate_modifier': 0.9,   # Slower growth in lung tissue
            'oxygen_availability': 1.1     # Higher oxygen availability
        },
        'colon': {
            'growth_rate_modifier': 1.1,   # Moderate growth rate
            'immune_infiltration': 1.3     # Higher immune cell presence
        }
    }
    
    if tissue_system in tissue_modifications:
        modifications = tissue_modifications[tissue_system]
        # Apply modifications to relevant parameters
        # This would be implemented based on specific parameter relationships
    
    return param_set


# Example usage and testing
if __name__ == '__main__':
    # Create parameter sets for different cell types
    tumor_params = TumorCellParameters()
    tcell_params = TCellParameters()
    dc_params = DendriticCellParameters()
    
    # Example parameter access
    growth_param = tumor_params.get_parameter('PDL1n_growth')
    print(f"Growth parameter: {growth_param}")
    
    # Create custom parameter set
    custom_tumor = create_parameter_set(
        'tumor', 
        tissue_system='breast',
        custom_params={'PDL1n_growth': 0.8}
    )
    
    print("Parameter templates created successfully!")
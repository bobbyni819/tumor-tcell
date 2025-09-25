"""
Parameter Schema Template
========================

Schema templates for different biological systems based on tumor-tcell patterns.

This template provides:
- Standardized parameter schemas for different cell types
- Tissue-specific parameter variations
- Schema validation and inheritance
- Extensible parameter hierarchies

Usage:
    from parameter_schema import CellParameterSchema, create_schema
    
    schema = CellParameterSchema.tumor_cell_schema()
    tissue_schema = create_schema('tumor_cell', 'breast_tissue')
"""

from typing import Dict, Any, List, Optional, Union, Type
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import copy
from vivarium.library.units import units

from .units_config import BioUnits
from .citation_format import Citation


@dataclass
class ParameterDefinition:
    """Definition of a single parameter with metadata"""
    name: str
    default_value: Any
    units: Optional[Any] = None
    description: str = ""
    biological_context: str = ""
    citation: Optional[Citation] = None
    valid_range: Optional[tuple] = None
    parameter_type: str = "numeric"  # numeric, categorical, boolean
    required: bool = True
    tissue_variations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParameterGroup:
    """Group of related parameters"""
    name: str
    description: str
    parameters: Dict[str, ParameterDefinition] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


class ParameterSchema(ABC):
    """Abstract base class for parameter schemas"""
    
    def __init__(self):
        self.bio_units = BioUnits()
        self.parameter_groups: Dict[str, ParameterGroup] = {}
        self._define_schema()
    
    @abstractmethod
    def _define_schema(self):
        """Define the parameter schema structure"""
        pass
    
    def add_parameter_group(self, group: ParameterGroup):
        """Add a parameter group to the schema"""
        self.parameter_groups[group.name] = group
    
    def get_parameter(self, group_name: str, param_name: str) -> Optional[ParameterDefinition]:
        """Get a specific parameter definition"""
        if group_name in self.parameter_groups:
            return self.parameter_groups[group_name].parameters.get(param_name)
        return None
    
    def get_all_parameters(self) -> Dict[str, Dict[str, ParameterDefinition]]:
        """Get all parameters organized by group"""
        return {
            group_name: group.parameters
            for group_name, group in self.parameter_groups.items()
        }
    
    def get_default_values(self) -> Dict[str, Any]:
        """Get dictionary of all default parameter values"""
        defaults = {}
        for group in self.parameter_groups.values():
            for param_name, param_def in group.parameters.items():
                if param_def.units:
                    defaults[param_name] = param_def.default_value * param_def.units
                else:
                    defaults[param_name] = param_def.default_value
        return defaults
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """Validate parameters against the schema"""
        errors = []
        
        # Check required parameters
        for group in self.parameter_groups.values():
            for param_name, param_def in group.parameters.items():
                if param_def.required and param_name not in parameters:
                    errors.append(f"Required parameter '{param_name}' is missing")
        
        # Check parameter values
        for param_name, value in parameters.items():
            param_def = self._find_parameter(param_name)
            if param_def:
                validation_errors = self._validate_parameter(param_def, value)
                errors.extend(validation_errors)
        
        return errors
    
    def _find_parameter(self, param_name: str) -> Optional[ParameterDefinition]:
        """Find parameter definition by name"""
        for group in self.parameter_groups.values():
            if param_name in group.parameters:
                return group.parameters[param_name]
        return None
    
    def _validate_parameter(self, param_def: ParameterDefinition, value: Any) -> List[str]:
        """Validate a single parameter value"""
        errors = []
        
        # Check valid range
        if param_def.valid_range and param_def.parameter_type == "numeric":
            min_val, max_val = param_def.valid_range
            if hasattr(value, 'magnitude'):
                check_value = value.magnitude
            else:
                check_value = value
            
            if check_value < min_val or check_value > max_val:
                errors.append(
                    f"Parameter '{param_def.name}' value {check_value} "
                    f"outside valid range [{min_val}, {max_val}]"
                )
        
        return errors


class TumorCellSchema(ParameterSchema):
    """Parameter schema for tumor cells based on tumor-tcell patterns"""
    
    def _define_schema(self):
        """Define tumor cell parameter schema"""
        
        # Physical properties group
        physical_group = ParameterGroup(
            name="physical_properties",
            description="Physical characteristics of tumor cells"
        )
        
        physical_group.parameters['diameter'] = ParameterDefinition(
            name='diameter',
            default_value=15.0,
            units=self.bio_units.CELLULAR_LENGTH,
            description='Cell diameter',
            biological_context='Tumor cell size affects surface area for molecular interactions',
            valid_range=(5.0, 30.0),
            tissue_variations={
                'breast': 18.0,
                'lung': 12.0,
                'colon': 16.0,
                'prostate': 14.0
            }
        )
        
        physical_group.parameters['mass'] = ParameterDefinition(
            name='mass',
            default_value=8.0,
            units=self.bio_units.CELLULAR_MASS,
            description='Cell mass',
            biological_context='Cell mass affects division mechanics and metabolic requirements',
            valid_range=(1.0, 50.0),
            tissue_variations={
                'breast': 10.0,
                'lung': 6.0,
                'colon': 9.0,
                'prostate': 7.5
            }
        )
        
        self.add_parameter_group(physical_group)
        
        # Growth and division group
        growth_group = ParameterGroup(
            name="growth_division",
            description="Parameters controlling tumor cell growth and division"
        )
        
        growth_group.parameters['PDL1n_growth'] = ParameterDefinition(
            name='PDL1n_growth',
            default_value=0.6,
            description='Probability of division in 24 hours for PDL1-negative cells',
            biological_context='PDL1-negative cells maintain proliferative capacity',
            valid_range=(0.0, 2.0),
            tissue_variations={
                'breast': 0.8,
                'lung': 0.4,
                'colon': 0.7,
                'prostate': 0.3
            }
        )
        
        growth_group.parameters['initial_PDL1n'] = ParameterDefinition(
            name='initial_PDL1n',
            default_value=0.9,
            description='Initial proportion of PDL1-negative cells',
            biological_context='Initial heterogeneity in PDL1 expression affects immune evasion',
            valid_range=(0.0, 1.0),
            tissue_variations={
                'breast': 0.7,
                'lung': 0.8,
                'colon': 0.6,
                'prostate': 0.9
            }
        )
        
        self.add_parameter_group(growth_group)
        
        # Death mechanisms group
        death_group = ParameterGroup(
            name="death_mechanisms",
            description="Parameters controlling tumor cell death"
        )
        
        death_group.parameters['death_apoptosis'] = ParameterDefinition(
            name='death_apoptosis',
            default_value=0.5,
            description='Background apoptosis rate',
            biological_context='Background cell death from metabolic stress and DNA damage',
            valid_range=(0.0, 1.0)
        )
        
        death_group.parameters['cytotoxic_packet_threshold'] = ParameterDefinition(
            name='cytotoxic_packet_threshold',
            default_value=12800,  # 128 * 100
            description='Threshold for T cell-mediated cytotoxic killing',
            biological_context='Number of cytotoxic packets needed for tumor cell death',
            valid_range=(1000, 50000)
        )
        
        self.add_parameter_group(death_group)
        
        # Molecular interactions group
        molecular_group = ParameterGroup(
            name="molecular_interactions",
            description="Parameters for molecular production and interactions"
        )
        
        molecular_group.parameters['IFNg_threshold'] = ParameterDefinition(
            name='IFNg_threshold',
            default_value=15000,
            description='IFN-gamma threshold for PDL1n to PDL1p transition',
            biological_context='Threshold for immune-mediated state transition',
            valid_range=(1000, 100000)
        )
        
        molecular_group.parameters['tumor_debris_amount'] = ParameterDefinition(
            name='tumor_debris_amount',
            default_value=1.4e15,
            description='Amount of DAMPs released upon cell death',
            biological_context='Damage-associated molecular patterns for immune activation',
            valid_range=(1e14, 1e16)
        )
        
        molecular_group.parameters['IFNg_MW'] = ParameterDefinition(
            name='IFNg_MW',
            default_value=17000,
            units=self.bio_units.MOLECULAR_WEIGHT,
            description='IFN-gamma molecular weight',
            biological_context='Molecular weight for concentration conversions',
            valid_range=(15000, 20000)
        )
        
        self.add_parameter_group(molecular_group)


class TCellSchema(ParameterSchema):
    """Parameter schema for T cells based on tumor-tcell patterns"""
    
    def _define_schema(self):
        """Define T cell parameter schema"""
        
        # Physical properties group
        physical_group = ParameterGroup(
            name="physical_properties",
            description="Physical characteristics of T cells"
        )
        
        physical_group.parameters['diameter'] = ParameterDefinition(
            name='diameter',
            default_value=7.5,
            units=self.bio_units.CELLULAR_LENGTH,
            description='T cell diameter',
            biological_context='Smaller than tumor cells, affects migration through tissue',
            valid_range=(4.0, 12.0)
        )
        
        physical_group.parameters['mass'] = ParameterDefinition(
            name='mass',
            default_value=2.0,
            units=self.bio_units.CELLULAR_MASS,
            description='T cell mass',
            biological_context='Lower mass than tumor cells, affects migration dynamics',
            valid_range=(0.5, 10.0)
        )
        
        self.add_parameter_group(physical_group)
        
        # Activation and exhaustion group
        activation_group = ParameterGroup(
            name="activation_exhaustion",
            description="Parameters controlling T cell activation and exhaustion"
        )
        
        activation_group.parameters['initial_PD1n'] = ParameterDefinition(
            name='initial_PD1n',
            default_value=0.8,
            description='Initial proportion of PD1-negative (non-exhausted) T cells',
            biological_context='Initial activation state affects cytotoxic capacity',
            valid_range=(0.0, 1.0)
        )
        
        activation_group.parameters['activation_time'] = ParameterDefinition(
            name='activation_time',
            default_value=21600,  # 6 hours
            units=self.bio_units.CELLULAR_TIME,
            description='Duration of active cytokine production after stimulation',
            biological_context='Time window for maximum T cell activity',
            valid_range=(3600, 86400)  # 1-24 hours
        )
        
        activation_group.parameters['activation_refractory_time'] = ParameterDefinition(
            name='activation_refractory_time',
            default_value=43200,  # 12 hours
            units=self.bio_units.CELLULAR_TIME,
            description='Recovery time with limited cytokine production',
            biological_context='Refractory period after activation',
            valid_range=(3600, 172800)  # 1-48 hours
        )
        
        self.add_parameter_group(activation_group)
        
        # Migration group
        migration_group = ParameterGroup(
            name="migration",
            description="Parameters controlling T cell migration"
        )
        
        migration_group.parameters['PD1n_migration'] = ParameterDefinition(
            name='PD1n_migration',
            default_value=10.0,
            units=self.bio_units.CELL_VELOCITY,
            description='Migration velocity of non-exhausted T cells',
            biological_context='Active T cells migrate faster for tumor surveillance',
            valid_range=(1.0, 20.0)
        )
        
        migration_group.parameters['PD1p_migration'] = ParameterDefinition(
            name='PD1p_migration',
            default_value=5.0,
            units=self.bio_units.CELL_VELOCITY,
            description='Migration velocity of exhausted T cells',
            biological_context='Exhausted T cells have impaired migration',
            valid_range=(0.5, 15.0)
        )
        
        self.add_parameter_group(migration_group)
        
        # Cytotoxic function group
        cytotoxic_group = ParameterGroup(
            name="cytotoxic_function",
            description="Parameters controlling T cell cytotoxic function"
        )
        
        cytotoxic_group.parameters['IFNg_production_PD1n'] = ParameterDefinition(
            name='IFNg_production_PD1n',
            default_value=2.78e-4,
            description='IFN-gamma production rate for non-exhausted T cells',
            biological_context='Cytokine production in active state',
            valid_range=(1e-5, 1e-2)
        )
        
        cytotoxic_group.parameters['cytotoxic_packet_production'] = ParameterDefinition(
            name='cytotoxic_packet_production',
            default_value=0.5,
            description='Rate of cytotoxic granule production',
            biological_context='Perforin/granzyme production for tumor killing',
            valid_range=(0.0, 2.0)
        )
        
        self.add_parameter_group(cytotoxic_group)


class DendriticCellSchema(ParameterSchema):
    """Parameter schema for dendritic cells based on tumor-tcell patterns"""
    
    def _define_schema(self):
        """Define dendritic cell parameter schema"""
        
        # Physical properties group
        physical_group = ParameterGroup(
            name="physical_properties",
            description="Physical characteristics of dendritic cells"
        )
        
        physical_group.parameters['diameter'] = ParameterDefinition(
            name='diameter',
            default_value=10.0,
            units=self.bio_units.CELLULAR_LENGTH,
            description='Dendritic cell diameter',
            biological_context='Intermediate size between T cells and tumor cells',
            valid_range=(6.0, 15.0)
        )
        
        physical_group.parameters['mass'] = ParameterDefinition(
            name='mass',
            default_value=2.0,
            units=self.bio_units.CELLULAR_MASS,
            description='Dendritic cell mass',
            biological_context='Similar mass to T cells but with extended dendrites',
            valid_range=(0.8, 15.0)
        )
        
        self.add_parameter_group(physical_group)
        
        # Activation group
        activation_group = ParameterGroup(
            name="activation",
            description="Parameters controlling dendritic cell activation"
        )
        
        activation_group.parameters['activation_threshold'] = ParameterDefinition(
            name='activation_threshold',
            default_value=1e7,
            description='Tumor debris threshold for activation',
            biological_context='DAMP recognition threshold for maturation',
            valid_range=(1e5, 1e9)
        )
        
        activation_group.parameters['death_apoptosis'] = ParameterDefinition(
            name='death_apoptosis',
            default_value=0.5,
            description='Background apoptosis rate',
            biological_context='Baseline death rate in tissue environment',
            valid_range=(0.0, 1.0)
        )
        
        self.add_parameter_group(activation_group)
        
        # Migration group
        migration_group = ParameterGroup(
            name="migration",
            description="Parameters controlling dendritic cell migration"
        )
        
        migration_group.parameters['velocity_inactive'] = ParameterDefinition(
            name='velocity_inactive',
            default_value=3.0,
            units=self.bio_units.CELL_VELOCITY,
            description='Migration velocity in inactive state',
            biological_context='Surveillance migration for antigen capture',
            valid_range=(1.0, 10.0)
        )
        
        migration_group.parameters['velocity_active'] = ParameterDefinition(
            name='velocity_active',
            default_value=12.5,
            units=self.bio_units.CELL_VELOCITY,
            description='Migration velocity in active state',
            biological_context='Rapid migration to lymph nodes after activation',
            valid_range=(5.0, 25.0)
        )
        
        self.add_parameter_group(migration_group)


class TissueSpecificSchema:
    """Utility class for applying tissue-specific parameter modifications"""
    
    @staticmethod
    def get_tissue_modifications(tissue_type: str) -> Dict[str, Dict[str, Any]]:
        """Get tissue-specific parameter modifications"""
        
        tissue_modifications = {
            'breast': {
                'tumor_cell': {
                    'diameter': 18.0,
                    'mass': 10.0,
                    'PDL1n_growth': 0.8,
                    'initial_PDL1n': 0.7
                },
                'environment': {
                    'vascularization': 0.8,
                    'stiffness': 1.2,
                    'immune_infiltration': 0.9
                }
            },
            'lung': {
                'tumor_cell': {
                    'diameter': 12.0,
                    'mass': 6.0,
                    'PDL1n_growth': 0.4,
                    'initial_PDL1n': 0.8
                },
                'environment': {
                    'oxygen_availability': 1.1,
                    'immune_infiltration': 1.2
                }
            },
            'colon': {
                'tumor_cell': {
                    'diameter': 16.0,
                    'mass': 9.0,
                    'PDL1n_growth': 0.7,
                    'initial_PDL1n': 0.6
                },
                'environment': {
                    'immune_infiltration': 1.3,
                    'microbiome_influence': 1.0
                }
            },
            'prostate': {
                'tumor_cell': {
                    'diameter': 14.0,
                    'mass': 7.5,
                    'PDL1n_growth': 0.3,
                    'initial_PDL1n': 0.9
                },
                'environment': {
                    'hormone_influence': 1.2,
                    'immune_infiltration': 0.7
                }
            }
        }
        
        return tissue_modifications.get(tissue_type, {})
    
    @staticmethod
    def apply_tissue_modifications(schema: ParameterSchema, tissue_type: str) -> ParameterSchema:
        """Apply tissue-specific modifications to a parameter schema"""
        
        modifications = TissueSpecificSchema.get_tissue_modifications(tissue_type)
        modified_schema = copy.deepcopy(schema)
        
        # Apply modifications to relevant parameters
        for group_name, group in modified_schema.parameter_groups.items():
            for param_name, param_def in group.parameters.items():
                if param_name in param_def.tissue_variations:
                    # Use tissue-specific value if available
                    if tissue_type in param_def.tissue_variations:
                        param_def.default_value = param_def.tissue_variations[tissue_type]
        
        return modified_schema


def create_schema(cell_type: str, tissue_type: str = None) -> ParameterSchema:
    """
    Create a parameter schema for a specific cell type and tissue.
    
    Args:
        cell_type: Type of cell ('tumor_cell', 'tcell', 'dendritic_cell')
        tissue_type: Specific tissue context (optional)
    
    Returns:
        ParameterSchema configured for the specified cell type and tissue
    """
    
    schema_classes = {
        'tumor_cell': TumorCellSchema,
        'tcell': TCellSchema,
        'dendritic_cell': DendriticCellSchema
    }
    
    if cell_type not in schema_classes:
        raise ValueError(f"Unknown cell type: {cell_type}")
    
    # Create base schema
    schema = schema_classes[cell_type]()
    
    # Apply tissue-specific modifications if specified
    if tissue_type:
        schema = TissueSpecificSchema.apply_tissue_modifications(schema, tissue_type)
    
    return schema


def compare_schemas(schema1: ParameterSchema, schema2: ParameterSchema) -> Dict[str, Any]:
    """Compare two parameter schemas and return differences"""
    
    differences = {
        'added_parameters': [],
        'removed_parameters': [],
        'modified_parameters': []
    }
    
    params1 = schema1.get_all_parameters()
    params2 = schema2.get_all_parameters()
    
    # Find all parameter names
    all_params1 = set()
    all_params2 = set()
    
    for group_params in params1.values():
        all_params1.update(group_params.keys())
    
    for group_params in params2.values():
        all_params2.update(group_params.keys())
    
    # Find differences
    differences['added_parameters'] = list(all_params2 - all_params1)
    differences['removed_parameters'] = list(all_params1 - all_params2)
    
    # Find modified parameters
    common_params = all_params1 & all_params2
    for param_name in common_params:
        param1 = schema1._find_parameter(param_name)
        param2 = schema2._find_parameter(param_name)
        
        if param1 and param2 and param1.default_value != param2.default_value:
            differences['modified_parameters'].append({
                'parameter': param_name,
                'old_value': param1.default_value,
                'new_value': param2.default_value
            })
    
    return differences


# Example usage and testing
if __name__ == '__main__':
    # Create different cell type schemas
    tumor_schema = TumorCellSchema()
    tcell_schema = TCellSchema()
    dc_schema = DendriticCellSchema()
    
    # Get default parameters
    tumor_defaults = tumor_schema.get_default_values()
    print(f"Tumor cell default parameters: {list(tumor_defaults.keys())}")
    
    # Create tissue-specific schema
    breast_tumor_schema = create_schema('tumor_cell', 'breast')
    breast_defaults = breast_tumor_schema.get_default_values()
    
    # Compare schemas
    differences = compare_schemas(tumor_schema, breast_tumor_schema)
    print(f"Differences for breast tissue: {differences}")
    
    # Validate parameters
    test_params = {
        'diameter': 15.0,
        'mass': 8.0,
        'PDL1n_growth': 0.6
    }
    
    validation_errors = tumor_schema.validate_parameters(test_params)
    if validation_errors:
        print(f"Validation errors: {validation_errors}")
    else:
        print("Parameters validated successfully")
    
    print("Parameter schema template created successfully!")
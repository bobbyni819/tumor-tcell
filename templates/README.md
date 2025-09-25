# Template Engine Architecture Components 5.3-5.10

This directory contains comprehensive templates for automatic vivarium repository generation based on patterns extracted from the tumor-tcell repository. These templates serve as blueprints for creating new agent-based models for different tissue systems while maintaining biological accuracy and vivarium best practices.

## Directory Structure

### 5.3 Parameter Integration Templates
**Location**: `5.3_parameter_integration/`
- `biological_parameters.py` - Biological parameter definitions with units and citations
- `parameter_validation.py` - Parameter validation and conversion utilities  
- `units_config.py` - Standard units configuration for biological modeling
- `citation_format.py` - Citation formatting and reference management
- `parameter_schema.py` - Schema templates for different biological systems

**Key Features**:
- Standardized units for cellular, molecular, and tissue scales
- Literature citation tracking and formatting
- Parameter validation with biological range checking  
- Tissue-specific parameter variations
- Extensible schema system for different cell types

### 5.4 State Machine Generation Templates
**Location**: `5.4_state_machine_generation/`
- `state_machine_base.py` - Abstract state machine framework
- `cell_state_transitions.py` - Specific cell state transition patterns
- `probability_transitions.py` - Probability-based transition logic
- `state_behaviors.py` - State-dependent behavior templates
- `transition_validation.py` - State transition validation and testing

**Key Features**:
- Abstract state machine framework with biological constraints
- Cell-specific state machines (tumor, T-cell, dendritic) with biologically accurate transitions
- Probability-based transition functions (exponential, threshold, molecular, composite)
- State-dependent behaviors (molecular production, migration, division, death, timers)
- Comprehensive validation and testing framework with statistical analysis

### 5.5 Molecular Interaction Generation Templates
**Location**: `5.5_molecular_interaction_generation/`
- `neighbor_interactions.py` - Core neighbor interaction framework
- `molecular_exchange.py` - Molecular transfer and signaling patterns

**Key Features**:
- Cell-to-cell molecular interactions (present/accept, transfer/receive)
- Distance-dependent interaction strength
- Receptor-ligand binding patterns
- Immune checkpoint molecule interactions

### 5.6 Composite Architecture Generation Templates
**Location**: `5.6_composite_architecture_generation/`
- `agent_composer.py` - Abstract composer framework
- Process composition and topology wiring patterns

**Key Features**:
- Agent composition patterns from tumor-tcell *_agent.py files
- Process topology wiring templates
- Parameter inheritance and schema definitions

### 5.7 File Structure Generation Templates
**Location**: `5.7_file_structure_generation/`
- `repository_structure.py` - Complete repository scaffolding

**Key Features**:
- Complete vivarium repository structure based on tumor-tcell organization
- Standard directory layout (processes/, composites/, experiments/, library/)
- Python package organization with proper __init__.py files

### 5.8 Validation Testing Templates
**Location**: `5.8_validation_testing/`
- `process_tests.py` - Process testing patterns

**Key Features**:
- Process validation frameworks
- Testing patterns from tumor-tcell repository
- Integration and performance testing templates

### 5.9 Customization Extension Templates
**Location**: `5.9_customization_extension/`
- `parameter_customization.py` - Parameter override patterns

**Key Features**:
- Tissue-specific parameter customization
- Process extension and inheritance patterns
- Plugin architecture for modularity

### 5.10 Code Quality Standards Templates
**Location**: `5.10_code_quality_standards/`
- `documentation_standards.py` - Docstring and documentation patterns

**Key Features**:
- Comprehensive documentation standards with biological context
- Type annotation templates
- Code organization and style guidelines

## Biological Context

These templates are based on specific patterns extracted from the tumor-tcell repository:

### Cell Types Supported
- **Tumor Cells**: PDL1n/PDL1p state transitions, growth and death mechanisms
- **T Cells**: PD1n/PD1p exhaustion, activation cycles, cytotoxic function
- **Dendritic Cells**: inactive/active maturation, antigen presentation

### Key Molecular Interactions
- **PDL1-PD1**: Immune checkpoint suppression
- **MHCI-TCR**: Antigen recognition and T cell activation
- **IFN-γ signaling**: Cytokine-mediated state transitions
- **Cytotoxic killing**: T cell-mediated tumor destruction
- **DAMP signaling**: Damage signals for immune activation

### Biological Processes
- Cell state transitions with biological triggers
- Molecular production and degradation
- Cell migration and contact-dependent interactions
- Division and death mechanisms
- Timer-based activation and refractory cycles

## Usage Examples

### Creating a New Tissue Model

```python
from templates.repository_structure import RepositoryGenerator
from templates.parameter_integration import create_parameter_set
from templates.state_machine_generation import create_cell_state_machine

# Generate repository structure
generator = RepositoryGenerator('breast_cancer_model')
generator.create_repository('/path/to/new/model')

# Create tissue-specific parameters
tumor_params = create_parameter_set('tumor', 'breast_tissue')

# Create state machines
tumor_sm = create_cell_state_machine('tumor', tumor_params)
```

### Customizing Parameters for Different Tissues

```python
from templates.parameter_customization import ParameterCustomizer

customizer = ParameterCustomizer()
breast_params = customizer.customize_for_tissue('breast', base_parameters)
lung_params = customizer.customize_for_tissue('lung', base_parameters)
```

### Validating Model Components

```python
from templates.transition_validation import StateMachineValidator
from templates.process_tests import ProcessTestFramework

# Validate state machine
validator = StateMachineValidator()
result = validator.validate_state_machine(tumor_sm, 'tumor')

# Test processes
tester = ProcessTestFramework()
test_data = tester.test_process(tumor_process)
```

## Template Design Principles

1. **Biological Accuracy**: All templates are based on literature-supported biological mechanisms
2. **Modularity**: Templates can be mixed and matched for different tissue systems
3. **Extensibility**: Easy to customize and extend for new biological contexts
4. **Documentation**: Comprehensive biological context and citations throughout
5. **Validation**: Built-in testing and validation frameworks
6. **Vivarium Integration**: Full compatibility with vivarium-core patterns and conventions

## Integration with LLM Systems

These templates are designed to facilitate LLM-assisted model generation by providing:
- Clear biological context and explanations
- Standardized patterns and conventions
- Comprehensive documentation and examples
- Modular components that can be combined programmatically
- Validation frameworks to ensure model correctness

## Future Extensions

The template system is designed to be extended for additional:
- Cell types (fibroblasts, endothelial cells, immune cells)
- Tissue types (liver, brain, skin, etc.)
- Disease contexts (inflammation, infection, autoimmunity)
- Therapeutic interventions (drug treatments, immunotherapies)
- Multi-scale modeling (molecular to tissue level)

## References

These templates are based on patterns and biological mechanisms from:
- The tumor-tcell vivarium repository
- Published literature on tumor-immune interactions
- Established vivarium modeling conventions
- Best practices in agent-based modeling

For specific citations and biological context, see the individual template files which include detailed references and biological explanations.
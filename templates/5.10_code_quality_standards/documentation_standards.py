"""
Documentation Standards Template
===============================

Docstring and documentation patterns based on tumor-tcell repository.

This module provides templates and standards for:
- Process documentation
- Parameter documentation with biological context
- Function and class docstrings
- Biological system explanations

Usage:
    from documentation_standards import ProcessDocTemplate
    
    # Use templates for consistent documentation
"""

from typing import Dict, Any, List


class ProcessDocTemplate:
    """
    Template for process documentation following tumor-tcell standards.
    
    Provides consistent documentation patterns for biological processes
    including parameter descriptions, biological context, and citations.
    """
    
    @staticmethod
    def get_process_docstring_template() -> str:
        """
        Get standard docstring template for biological processes.
        
        Returns:
            Formatted docstring template following tumor-tcell patterns
        """
        return '''"""
{process_name}
{process_name_underline}

{biological_description}

This process models {biological_system} and includes:
- {key_feature_1}
- {key_feature_2}  
- {key_feature_3}

References:
    * {reference_1}
    * {reference_2}

Parameters:
    parameters (dict): Configuration with the following keys:
        * **{param_1}** ({type_1}): {description_1} (default: {default_1})
        * **{param_2}** ({type_2}): {description_2} (default: {default_2})

Ports:
    * **{port_1}**: {port_description_1}
    * **{port_2}**: {port_description_2}

Example:
    >>> from {module_name} import {process_name}
    >>> process = {process_name}({{'{param_1}': {example_value}}})
    >>> result = process.next_update(60, states)
"""'''
    
    @staticmethod
    def get_parameter_doc_template() -> str:
        """Get template for parameter documentation with biological context"""
        return '''
        '{parameter_name}': {{
            'value': {default_value},
            'units': {units},
            'description': '{biological_description}',
            'citation': '{literature_reference}',
            'biological_context': '{biological_explanation}',
            'valid_range': {valid_range},
            'tissue_variations': {{
                'breast': {breast_value},
                'lung': {lung_value},
                'colon': {colon_value}
            }}
        }}'''
    
    @classmethod
    def generate_process_documentation(cls, process_info: Dict[str, Any]) -> str:
        """
        Generate complete process documentation.
        
        Args:
            process_info: Dictionary containing process information
                - name: Process name
                - description: Biological description
                - parameters: List of parameter dictionaries
                - ports: List of port descriptions
                - references: List of literature references
        
        Returns:
            Formatted documentation string
        """
        template = cls.get_process_docstring_template()
        
        # Fill in template values
        formatted_doc = template.format(
            process_name=process_info.get('name', 'ProcessName'),
            process_name_underline='=' * len(process_info.get('name', 'ProcessName')),
            biological_description=process_info.get('description', 'Biological process description'),
            biological_system=process_info.get('system', 'biological system'),
            key_feature_1=process_info.get('features', ['Feature 1'])[0],
            key_feature_2=process_info.get('features', ['Feature 1', 'Feature 2'])[1],
            key_feature_3=process_info.get('features', ['Feature 1', 'Feature 2', 'Feature 3'])[2],
            reference_1=process_info.get('references', ['Reference 1'])[0],
            reference_2=process_info.get('references', ['Reference 1', 'Reference 2'])[1],
            module_name=process_info.get('module', 'module_name'),
        )
        
        return formatted_doc


class BioContextDocumentation:
    """Biological context documentation standards"""
    
    @staticmethod
    def get_cell_state_docs() -> Dict[str, str]:
        """Get documentation for cell states"""
        return {
            'PDL1n': 'Proliferative tumor cell state with growth capability and immune vulnerability',
            'PDL1p': 'Immune-suppressive tumor cell state expressing PDL1 checkpoint molecules',
            'PD1n': 'Active T cell state with full cytotoxic and cytokine production capability',
            'PD1p': 'Exhausted T cell state with reduced effector functions',
            'inactive': 'Surveillance dendritic cell state with antigen capture capability',
            'active': 'Mature dendritic cell state with antigen presentation and migration'
        }
    
    @staticmethod
    def get_molecular_docs() -> Dict[str, str]:
        """Get documentation for key molecules"""
        return {
            'IFNg': 'Interferon-gamma: Pro-inflammatory cytokine produced by T cells that induces tumor cell PDL1 expression',
            'PDL1': 'Programmed death-ligand 1: Immune checkpoint molecule that suppresses T cell function',
            'PD1': 'Programmed death receptor 1: T cell checkpoint receptor that mediates exhaustion',
            'MHCI': 'Major histocompatibility complex class I: Antigen presentation molecule recognized by TCR',
            'TCR': 'T cell receptor: Recognizes antigen presented by MHCI molecules',
            'cytotoxic_packets': 'Perforin/granzyme granules: Cytotoxic molecules released by T cells to kill tumor cells',
            'tumor_debris': 'Damage-associated molecular patterns (DAMPs): Released by dying tumor cells to activate immune cells'
        }


# Example usage for generating documentation
def generate_tumor_process_docs():
    """Generate documentation for tumor process"""
    
    process_info = {
        'name': 'TumorCellProcess',
        'description': 'Models tumor cell behavior including growth, death, and immune interactions',
        'system': 'tumor microenvironment',
        'features': [
            'PDL1 expression regulation',
            'IFN-gamma response',
            'Cell division and death'
        ],
        'references': [
            'Eden et al. (2011) - Tumor growth rates',
            'Gong et al. (2017) - Apoptosis mechanisms'
        ],
        'module': 'tumor_tcell.processes.tumor'
    }
    
    return ProcessDocTemplate.generate_process_documentation(process_info)


if __name__ == '__main__':
    # Example documentation generation
    docs = generate_tumor_process_docs()
    print(docs)
    
    # Example biological context
    bio_docs = BioContextDocumentation()
    cell_states = bio_docs.get_cell_state_docs()
    print("\nCell State Documentation:")
    for state, description in cell_states.items():
        print(f"  {state}: {description}")
    
    print("Documentation standards templates created successfully!")
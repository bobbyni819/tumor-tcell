"""
Repository Structure Template
============================

Complete repository scaffolding based on tumor-tcell organization.

Usage:
    from repository_structure import RepositoryGenerator
    
    generator = RepositoryGenerator('my_tissue_model')
    generator.create_repository('/path/to/output')
"""

import os
from typing import Dict, List, Any
from pathlib import Path


class RepositoryGenerator:
    """
    Generator for vivarium repository structure based on tumor-tcell patterns.
    """
    
    def __init__(self, package_name: str):
        self.package_name = package_name
        self.directory_structure = self._define_structure()
        self.file_templates = self._define_file_templates()
    
    def _define_structure(self) -> Dict[str, List[str]]:
        """Define directory structure based on tumor-tcell"""
        return {
            '': ['setup.py', 'requirements.txt', 'README.md', 'pytest.ini'],
            self.package_name: ['__init__.py'],
            f'{self.package_name}/processes': ['__init__.py'],
            f'{self.package_name}/composites': ['__init__.py'],
            f'{self.package_name}/experiments': ['__init__.py', 'main.py'],
            f'{self.package_name}/library': ['__init__.py'],
            f'{self.package_name}/plots': ['__init__.py'],
            f'{self.package_name}/data': [],
            'out': [],
            'out/processes': [],
            'out/composites': [],
            'out/experiments': []
        }
    
    def _define_file_templates(self) -> Dict[str, str]:
        """Define file templates"""
        return {
            '__init__.py': self._get_init_template(),
            'setup.py': self._get_setup_template(),
            'README.md': self._get_readme_template(),
            'main.py': self._get_main_template(),
            'requirements.txt': self._get_requirements_template()
        }
    
    def create_repository(self, output_path: str):
        """Create complete repository structure"""
        base_path = Path(output_path)
        
        # Create directories
        for directory, files in self.directory_structure.items():
            dir_path = base_path / directory if directory else base_path
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create files
            for filename in files:
                file_path = dir_path / filename
                if filename in self.file_templates:
                    content = self.file_templates[filename]
                    file_path.write_text(content)
    
    def _get_init_template(self) -> str:
        """Get __init__.py template"""
        return f'''import os
package_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PROCESS_OUT_DIR = os.path.join(package_path, 'out', 'processes')
COMPOSITE_OUT_DIR = os.path.join(package_path, 'out', 'composites')
EXPERIMENT_OUT_DIR = os.path.join(package_path, 'out', 'experiments')
REFERENCE_DATA_DIR = os.path.join(package_path, 'reference_data')
'''
    
    def _get_setup_template(self) -> str:
        """Get setup.py template"""
        return f'''from setuptools import setup, find_packages

setup(
    name="{self.package_name}",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "vivarium-core",
        "vivarium-multibody",
        "numpy",
        "scipy",
        "matplotlib",
        "pandas"
    ],
    python_requires=">=3.8",
    author="Your Name",
    description="Agent-based model for {self.package_name.replace('_', ' ')} system",
)
'''
    
    def _get_readme_template(self) -> str:
        """Get README.md template"""
        return f'''# {self.package_name.replace('_', ' ').title()}

Agent-based model for {self.package_name.replace('_', ' ')} system using Vivarium.

## Installation

```bash
pip install -e .
```

## Usage

```python
from {self.package_name}.experiments.main import run_simulation
run_simulation()
```
'''
    
    def _get_main_template(self) -> str:
        """Get main.py template"""
        return f'''"""
Main experiment file for {self.package_name} simulations.
"""

from vivarium.core.engine import Engine
from vivarium.core.control import Control


def run_simulation():
    \"\"\"Run the main simulation\"\"\"
    pass


if __name__ == '__main__':
    run_simulation()
'''
    
    def _get_requirements_template(self) -> str:
        """Get requirements.txt template"""
        return '''vivarium-core
vivarium-multibody
numpy
scipy
matplotlib
pandas
'''
"""
Agent Composer Template
======================

Abstract composer framework based on tumor-tcell repository patterns.

Usage:
    from agent_composer import CellAgentComposer
    
    class MyAgentComposer(CellAgentComposer):
        def _define_processes(self):
            # Define agent processes
            pass
"""

from typing import Dict, Any, List
from abc import ABC, abstractmethod
from vivarium.core.composer import Composer


class CellAgentComposer(Composer, ABC):
    """
    Abstract base class for cell agent composers based on tumor-tcell patterns.
    
    Provides framework for:
    - Process initialization and reuse
    - Topology generation
    - Parameter management
    - Schema definitions
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.processes_initialized = False
        self.core_processes = {}
    
    @abstractmethod
    def _define_processes(self) -> Dict[str, Any]:
        """Define the processes that make up this agent"""
        pass
    
    @abstractmethod
    def _define_topology(self) -> Dict[str, Any]:
        """Define how processes are wired together"""
        pass
    
    def initialize_processes(self, config: Dict[str, Any]):
        """Initialize core processes with reuse capability"""
        if not self.processes_initialized or not config.get('reuse_processes', True):
            self.core_processes = self._define_processes()
            self.processes_initialized = True
    
    def generate_processes(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate processes for this agent instance"""
        if not self.processes_initialized:
            self.initialize_processes(config)
        
        return self.core_processes
    
    def generate_topology(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate topology for this agent instance"""
        return self._define_topology()


class TumorAgentTemplate(CellAgentComposer):
    """Template for tumor agent based on tumor_agent.py patterns"""
    
    defaults = {
        'time_step': 60,
        'reuse_processes': False,
        'boundary_path': ('boundary',),
        'agents_path': ('..', '..', 'agents',),
        'field_path': ('..', '..', 'fields',),
        'dimensions_path': ('..', '..', 'dimensions',),
    }
    
    def _define_processes(self) -> Dict[str, Any]:
        """Define tumor agent processes"""
        from tumor_tcell.processes.tumor import TumorCellProcess
        from tumor_tcell.processes.local_field import LocalField
        from vivarium.processes.meta_division import MetaDivision
        from vivarium.processes.remove import Remove
        
        return {
            'tumor': TumorCellProcess(self.config.get('tumor', {})),
            'local_field': LocalField({}),
            'division': MetaDivision({}),
            'death': Remove({})
        }
    
    def _define_topology(self) -> Dict[str, Any]:
        """Define tumor agent topology"""
        boundary_path = self.config['boundary_path']
        agents_path = self.config['agents_path']
        field_path = self.config['field_path']
        dimensions_path = self.config['dimensions_path']
        
        return {
            'tumor': {
                'internal': ('internal',),
                'boundary': boundary_path,
                'globals': boundary_path,
                'neighbors': ('neighbors',),
            },
            'local_field': {
                'exchanges': boundary_path + ('exchange',),
                'location': boundary_path + ('location',),
                'fields': field_path,
                'dimensions': dimensions_path,
            },
            'division': {
                'global': boundary_path,
                'agents': agents_path,
            },
            'death': {
                'trigger': boundary_path + ('death',),
                'agents': agents_path,
            },
        }
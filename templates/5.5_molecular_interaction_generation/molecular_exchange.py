"""
Molecular Exchange Template
==========================

Molecular transfer and signaling patterns based on tumor-tcell repository.

Usage:
    from molecular_exchange import MolecularExchangeManager, ExchangePattern
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from .neighbor_interactions import InteractionMechanism, InteractionResult, InteractionType


@dataclass
class ExchangePattern:
    """Pattern for molecular exchange between cells"""
    source_molecule: str
    target_molecule: str
    conversion_rate: float
    exchange_type: str  # 'direct', 'catalytic', 'competitive'
    biological_context: str = ""


class MolecularExchangeManager:
    """Manages molecular exchange patterns from tumor-tcell repository"""
    
    def __init__(self):
        self.exchange_patterns = []
        self.exchange_history = {}
    
    def add_exchange_pattern(self, pattern: ExchangePattern):
        """Add molecular exchange pattern"""
        self.exchange_patterns.append(pattern)
    
    def process_exchange(self, cell_state: Dict[str, Any], 
                        neighbors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process molecular exchanges between cells"""
        
        updates = {
            'boundary': {'exchange': {}},
            'neighbors': {'transfer': {}, 'receive': {}}
        }
        
        # Process each exchange pattern
        for pattern in self.exchange_patterns:
            if pattern.exchange_type == 'direct':
                self._process_direct_exchange(pattern, cell_state, neighbors, updates)
            elif pattern.exchange_type == 'catalytic':
                self._process_catalytic_exchange(pattern, cell_state, neighbors, updates)
        
        return updates
    
    def _process_direct_exchange(self, pattern: ExchangePattern, 
                               cell_state: Dict[str, Any], neighbors: List[Dict[str, Any]], 
                               updates: Dict[str, Any]):
        """Process direct molecular exchange"""
        source_amount = cell_state.get('internal', {}).get(pattern.source_molecule, 0)
        
        if source_amount > 0:
            exchange_amount = source_amount * pattern.conversion_rate
            updates['neighbors']['transfer'][pattern.target_molecule] = exchange_amount


# Example exchange patterns from tumor-tcell
def create_tumor_tcell_exchanges() -> MolecularExchangeManager:
    """Create tumor-tcell molecular exchange patterns"""
    manager = MolecularExchangeManager()
    
    # IFN-gamma cytokine exchange
    ifng_pattern = ExchangePattern(
        source_molecule='IFNg_internal',
        target_molecule='IFNg',
        conversion_rate=0.1,
        exchange_type='direct',
        biological_context='T cell IFN-gamma secretion'
    )
    manager.add_exchange_pattern(ifng_pattern)
    
    return manager
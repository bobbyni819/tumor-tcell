"""
Neighbor Interactions Template
=============================

Core neighbor interaction framework based on tumor-tcell repository patterns.

This template provides:
- Neighbor detection and management
- Molecular interaction mechanics
- Distance-dependent interaction strength
- Contact time tracking

Usage:
    from neighbor_interactions import NeighborInteractionManager, InteractionType
    
    manager = NeighborInteractionManager()
    interactions = manager.process_interactions(cell_state, neighbors)
"""

from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
import math
import random


class InteractionType(Enum):
    """Types of neighbor interactions based on tumor-tcell patterns"""
    PRESENT_ACCEPT = "present_accept"  # Membrane-bound signaling (PDL1-PD1, MHCI-TCR)
    TRANSFER_RECEIVE = "transfer_receive"  # Soluble molecule exchange
    CONTACT_DEPENDENT = "contact_dependent"  # Direct cell contact effects
    DISTANCE_DEPENDENT = "distance_dependent"  # Distance-modulated interactions


@dataclass
class InteractionResult:
    """Result of a molecular interaction"""
    interaction_type: InteractionType
    molecules: Dict[str, float]
    target_cell: str
    interaction_strength: float
    biological_context: str = ""


@dataclass
class NeighborState:
    """State information for a neighboring cell"""
    cell_id: str
    cell_type: str
    distance: float
    contact_time: float
    present_molecules: Dict[str, float]
    accept_molecules: Dict[str, float]
    transfer_molecules: Dict[str, float]
    receive_molecules: Dict[str, float]


class InteractionMechanism(ABC):
    """Abstract base class for molecular interaction mechanisms"""
    
    def __init__(self, name: str, biological_context: str = ""):
        self.name = name
        self.biological_context = biological_context
        self.parameters = {}
    
    @abstractmethod
    def calculate_interaction(self, source_state: Dict[str, Any], 
                            target_state: NeighborState) -> Optional[InteractionResult]:
        """Calculate interaction between source and target cells"""
        pass
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set mechanism parameters"""
        self.parameters.update(parameters)
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get mechanism parameter"""
        return self.parameters.get(name, default)


class PresentAcceptMechanism(InteractionMechanism):
    """
    Present-accept interaction mechanism for membrane-bound signaling.
    
    Based on tumor-tcell patterns:
    - PDL1 (present) + PD1 (accept) → T cell suppression
    - MHCI (present) + TCR (accept) → T cell activation
    """
    
    def __init__(self, molecule_pair: Tuple[str, str], biological_context: str = ""):
        super().__init__(f"present_accept_{molecule_pair[0]}_{molecule_pair[1]}", biological_context)
        self.ligand = molecule_pair[0]  # Present molecule
        self.receptor = molecule_pair[1]  # Accept molecule
    
    def calculate_interaction(self, source_state: Dict[str, Any], 
                            target_state: NeighborState) -> Optional[InteractionResult]:
        """Calculate present-accept interaction"""
        
        # Get ligand concentration from source (present)
        ligand_amount = source_state.get('neighbors', {}).get('present', {}).get(self.ligand, 0)
        
        # Get receptor concentration from target (accept)
        receptor_amount = target_state.accept_molecules.get(self.receptor, 0)
        
        if ligand_amount <= 0 or receptor_amount <= 0:
            return None
        
        # Calculate binding based on distance and concentrations
        distance_factor = self._calculate_distance_factor(target_state.distance)
        binding_strength = self._calculate_binding_strength(ligand_amount, receptor_amount)
        
        interaction_strength = binding_strength * distance_factor
        
        if interaction_strength > self.get_parameter('threshold', 0.1):
            return InteractionResult(
                interaction_type=InteractionType.PRESENT_ACCEPT,
                molecules={self.ligand: ligand_amount, self.receptor: receptor_amount},
                target_cell=target_state.cell_id,
                interaction_strength=interaction_strength,
                biological_context=f"{self.ligand}-{self.receptor} binding interaction"
            )
        
        return None
    
    def _calculate_distance_factor(self, distance: float) -> float:
        """Calculate distance-dependent interaction factor"""
        max_distance = self.get_parameter('max_interaction_distance', 2.0)  # μm
        
        if distance > max_distance:
            return 0.0
        
        # Exponential decay with distance
        decay_constant = self.get_parameter('distance_decay', 1.0)
        return math.exp(-decay_constant * distance / max_distance)
    
    def _calculate_binding_strength(self, ligand: float, receptor: float) -> float:
        """Calculate binding strength using simplified kinetics"""
        kd = self.get_parameter('binding_affinity', 1e4)  # Kd value
        
        # Simplified binding equation: strength = ([L] * [R]) / (Kd + [L])
        return (ligand * receptor) / (kd + ligand)


class TransferReceiveMechanism(InteractionMechanism):
    """
    Transfer-receive mechanism for soluble molecule exchange.
    
    Based on tumor-tcell patterns:
    - Cytotoxic packets (transfer) → tumor cell damage (receive)
    - Cytokines transferred to environment
    """
    
    def __init__(self, molecule: str, biological_context: str = ""):
        super().__init__(f"transfer_receive_{molecule}", biological_context)
        self.molecule = molecule
    
    def calculate_interaction(self, source_state: Dict[str, Any], 
                            target_state: NeighborState) -> Optional[InteractionResult]:
        """Calculate transfer-receive interaction"""
        
        # Get transfer amount from source
        transfer_amount = source_state.get('neighbors', {}).get('transfer', {}).get(self.molecule, 0)
        
        if transfer_amount <= 0:
            return None
        
        # Calculate transfer efficiency based on distance and contact time
        distance_factor = self._calculate_transfer_efficiency(target_state.distance)
        contact_factor = self._calculate_contact_factor(target_state.contact_time)
        
        # Total amount transferred
        effective_transfer = transfer_amount * distance_factor * contact_factor
        
        if effective_transfer > self.get_parameter('min_transfer', 0.01):
            return InteractionResult(
                interaction_type=InteractionType.TRANSFER_RECEIVE,
                molecules={self.molecule: effective_transfer},
                target_cell=target_state.cell_id,
                interaction_strength=effective_transfer,
                biological_context=f"{self.molecule} transfer interaction"
            )
        
        return None
    
    def _calculate_transfer_efficiency(self, distance: float) -> float:
        """Calculate transfer efficiency based on distance"""
        max_distance = self.get_parameter('max_transfer_distance', 1.0)  # μm
        
        if distance > max_distance:
            return 0.0
        
        # Linear decay with distance
        return 1.0 - (distance / max_distance)
    
    def _calculate_contact_factor(self, contact_time: float) -> float:
        """Calculate contact time-dependent factor"""
        min_contact_time = self.get_parameter('min_contact_time', 60)  # seconds
        
        if contact_time < min_contact_time:
            return contact_time / min_contact_time
        
        return 1.0


class ContactDependentMechanism(InteractionMechanism):
    """
    Contact-dependent interaction mechanism.
    
    Handles interactions that require direct cell-cell contact,
    such as mechanical forces or contact-dependent signaling.
    """
    
    def __init__(self, interaction_name: str, biological_context: str = ""):
        super().__init__(f"contact_dependent_{interaction_name}", biological_context)
        self.interaction_name = interaction_name
    
    def calculate_interaction(self, source_state: Dict[str, Any], 
                            target_state: NeighborState) -> Optional[InteractionResult]:
        """Calculate contact-dependent interaction"""
        
        # Check if cells are in direct contact
        max_contact_distance = self.get_parameter('contact_distance', 0.1)  # μm
        
        if target_state.distance > max_contact_distance:
            return None
        
        # Check minimum contact time
        min_contact_time = self.get_parameter('min_contact_time', 30)  # seconds
        
        if target_state.contact_time < min_contact_time:
            return None
        
        # Calculate interaction strength based on contact area (simplified)
        source_diameter = source_state.get('boundary', {}).get('diameter', 10.0)
        interaction_strength = self._calculate_contact_strength(
            source_diameter, target_state.distance, target_state.contact_time
        )
        
        return InteractionResult(
            interaction_type=InteractionType.CONTACT_DEPENDENT,
            molecules={},  # No specific molecules, just contact effect
            target_cell=target_state.cell_id,
            interaction_strength=interaction_strength,
            biological_context=f"Direct cell contact: {self.interaction_name}"
        )
    
    def _calculate_contact_strength(self, cell_diameter: float, distance: float, 
                                  contact_time: float) -> float:
        """Calculate contact interaction strength"""
        # Simplified contact area calculation
        contact_radius = (cell_diameter / 2) - distance
        contact_area = math.pi * contact_radius * contact_radius
        
        # Time-dependent strengthening
        time_factor = min(1.0, contact_time / self.get_parameter('saturation_time', 300))
        
        return contact_area * time_factor


class NeighborInteractionManager:
    """
    Manager for processing neighbor interactions based on tumor-tcell patterns.
    
    Coordinates multiple interaction mechanisms and manages neighbor states.
    """
    
    def __init__(self):
        self.mechanisms: List[InteractionMechanism] = []
        self.neighbor_history: Dict[Tuple[str, str], float] = {}  # (source, target) -> contact_time
        self.interaction_history: List[InteractionResult] = []
    
    def add_mechanism(self, mechanism: InteractionMechanism):
        """Add an interaction mechanism"""
        self.mechanisms.append(mechanism)
    
    def process_interactions(self, cell_state: Dict[str, Any], 
                           neighbors_data: Dict[str, Any]) -> List[InteractionResult]:
        """
        Process all interactions between the cell and its neighbors.
        
        Args:
            cell_state: Current state of the cell
            neighbors_data: Neighbor information from the simulation
        
        Returns:
            List of interaction results
        """
        interactions = []
        
        # Extract cell information
        cell_id = cell_state.get('cell_id', 'unknown')
        
        # Process each neighbor
        neighbors = self._extract_neighbor_states(cell_state, neighbors_data)
        
        for neighbor in neighbors:
            # Update contact time
            self._update_contact_time(cell_id, neighbor.cell_id)
            
            # Process each interaction mechanism
            for mechanism in self.mechanisms:
                interaction = mechanism.calculate_interaction(cell_state, neighbor)
                
                if interaction:
                    interactions.append(interaction)
                    self.interaction_history.append(interaction)
        
        return interactions
    
    def _extract_neighbor_states(self, cell_state: Dict[str, Any], 
                                neighbors_data: Dict[str, Any]) -> List[NeighborState]:
        """Extract neighbor states from simulation data"""
        neighbors = []
        
        # Get neighbor information (simplified extraction)
        present_data = neighbors_data.get('present', {})
        accept_data = neighbors_data.get('accept', {})
        transfer_data = neighbors_data.get('transfer', {})
        receive_data = neighbors_data.get('receive', {})
        
        # In tumor-tcell, neighbors are managed by the neighbors process
        # This is a simplified version for template purposes
        neighbor_positions = cell_state.get('neighbor_positions', {})
        
        for neighbor_id, position in neighbor_positions.items():
            # Calculate distance (simplified)
            cell_position = cell_state.get('boundary', {}).get('location', [0, 0])
            distance = math.sqrt(
                (position[0] - cell_position[0])**2 + 
                (position[1] - cell_position[1])**2
            )
            
            # Get contact time
            contact_key = (cell_state.get('cell_id', ''), neighbor_id)
            contact_time = self.neighbor_history.get(contact_key, 0)
            
            neighbor = NeighborState(
                cell_id=neighbor_id,
                cell_type="unknown",  # Would need to be provided
                distance=distance,
                contact_time=contact_time,
                present_molecules=present_data.get(neighbor_id, {}),
                accept_molecules=accept_data.get(neighbor_id, {}),
                transfer_molecules=transfer_data.get(neighbor_id, {}),
                receive_molecules=receive_data.get(neighbor_id, {})
            )
            
            neighbors.append(neighbor)
        
        return neighbors
    
    def _update_contact_time(self, cell_id: str, neighbor_id: str, timestep: float = 1.0):
        """Update contact time between cells"""
        contact_key = (cell_id, neighbor_id)
        current_time = self.neighbor_history.get(contact_key, 0)
        self.neighbor_history[contact_key] = current_time + timestep
    
    def get_interaction_summary(self) -> Dict[str, Any]:
        """Get summary of recent interactions"""
        if not self.interaction_history:
            return {'total_interactions': 0}
        
        # Analyze recent interactions
        recent_interactions = self.interaction_history[-100:]  # Last 100 interactions
        
        interaction_types = {}
        molecule_counts = {}
        
        for interaction in recent_interactions:
            # Count interaction types
            interaction_type = interaction.interaction_type.value
            interaction_types[interaction_type] = interaction_types.get(interaction_type, 0) + 1
            
            # Count molecules
            for molecule in interaction.molecules:
                molecule_counts[molecule] = molecule_counts.get(molecule, 0) + 1
        
        return {
            'total_interactions': len(recent_interactions),
            'interaction_types': interaction_types,
            'molecule_counts': molecule_counts,
            'average_strength': sum(i.interaction_strength for i in recent_interactions) / len(recent_interactions)
        }
    
    def clear_history(self):
        """Clear interaction and contact history"""
        self.neighbor_history.clear()
        self.interaction_history.clear()


class TumorTCellInteractionLibrary:
    """Library of common interaction mechanisms from tumor-tcell repository"""
    
    @staticmethod
    def create_pdl1_pd1_interaction() -> PresentAcceptMechanism:
        """Create PDL1-PD1 immune checkpoint interaction"""
        mechanism = PresentAcceptMechanism(
            ('PDL1', 'PD1'),
            "PDL1-PD1 immune checkpoint suppression interaction"
        )
        mechanism.set_parameters({
            'binding_affinity': 1e4,  # Kd for PDL1-PD1 binding
            'max_interaction_distance': 1.0,  # μm
            'distance_decay': 2.0,
            'threshold': 0.1
        })
        return mechanism
    
    @staticmethod
    def create_mhci_tcr_interaction() -> PresentAcceptMechanism:
        """Create MHCI-TCR antigen recognition interaction"""
        mechanism = PresentAcceptMechanism(
            ('MHCI', 'TCR'),
            "MHCI-TCR antigen recognition interaction"
        )
        mechanism.set_parameters({
            'binding_affinity': 5e3,  # Kd for MHCI-TCR binding
            'max_interaction_distance': 0.5,  # μm (closer contact required)
            'distance_decay': 3.0,
            'threshold': 0.2
        })
        return mechanism
    
    @staticmethod
    def create_cytotoxic_transfer() -> TransferReceiveMechanism:
        """Create cytotoxic packet transfer mechanism"""
        mechanism = TransferReceiveMechanism(
            'cytotoxic_packets',
            "T cell cytotoxic packet delivery to tumor cells"
        )
        mechanism.set_parameters({
            'max_transfer_distance': 1.0,  # μm
            'min_contact_time': 30,  # seconds
            'min_transfer': 1.0
        })
        return mechanism
    
    @staticmethod
    def create_immunological_synapse() -> ContactDependentMechanism:
        """Create immunological synapse formation"""
        mechanism = ContactDependentMechanism(
            'immunological_synapse',
            "Formation of immunological synapse between T cell and APC"
        )
        mechanism.set_parameters({
            'contact_distance': 0.1,  # μm
            'min_contact_time': 60,  # seconds
            'saturation_time': 300  # seconds
        })
        return mechanism
    
    @staticmethod
    def create_tumor_tcell_manager() -> NeighborInteractionManager:
        """Create interaction manager for tumor-T cell interactions"""
        manager = NeighborInteractionManager()
        
        # Add tumor-tcell specific mechanisms
        manager.add_mechanism(TumorTCellInteractionLibrary.create_pdl1_pd1_interaction())
        manager.add_mechanism(TumorTCellInteractionLibrary.create_mhci_tcr_interaction())
        manager.add_mechanism(TumorTCellInteractionLibrary.create_cytotoxic_transfer())
        manager.add_mechanism(TumorTCellInteractionLibrary.create_immunological_synapse())
        
        return manager


def create_interaction_manager(interaction_types: List[str]) -> NeighborInteractionManager:
    """
    Factory function to create interaction manager with specified interaction types.
    
    Args:
        interaction_types: List of interaction types to include
    
    Returns:
        Configured NeighborInteractionManager
    """
    manager = NeighborInteractionManager()
    
    interaction_factories = {
        'pdl1_pd1': TumorTCellInteractionLibrary.create_pdl1_pd1_interaction,
        'mhci_tcr': TumorTCellInteractionLibrary.create_mhci_tcr_interaction,
        'cytotoxic_transfer': TumorTCellInteractionLibrary.create_cytotoxic_transfer,
        'immunological_synapse': TumorTCellInteractionLibrary.create_immunological_synapse
    }
    
    for interaction_type in interaction_types:
        if interaction_type in interaction_factories:
            mechanism = interaction_factories[interaction_type]()
            manager.add_mechanism(mechanism)
    
    return manager


# Example usage and testing
if __name__ == '__main__':
    # Create interaction manager with tumor-tcell interactions
    manager = TumorTCellInteractionLibrary.create_tumor_tcell_manager()
    
    # Example cell state
    cell_state = {
        'cell_id': 'tcell_001',
        'boundary': {
            'location': [10.0, 15.0],
            'diameter': 7.5
        },
        'neighbors': {
            'present': {'TCR': 50000},
            'accept': {'PDL1': 0, 'MHCI': 0},
            'transfer': {'cytotoxic_packets': 100},
            'receive': {}
        },
        'neighbor_positions': {
            'tumor_001': [10.5, 15.2],  # Close neighbor
            'tumor_002': [12.0, 16.0]   # Farther neighbor
        }
    }
    
    # Example neighbors data (simplified)
    neighbors_data = {
        'present': {
            'tumor_001': {'PDL1': 5e4, 'MHCI': 5e4},
            'tumor_002': {'PDL1': 2e4, 'MHCI': 3e4}
        },
        'accept': {},
        'transfer': {},
        'receive': {}
    }
    
    # Process interactions
    interactions = manager.process_interactions(cell_state, neighbors_data)
    
    print(f"Found {len(interactions)} interactions:")
    for interaction in interactions:
        print(f"  {interaction.interaction_type.value}: {interaction.biological_context}")
        print(f"    Strength: {interaction.interaction_strength:.3f}")
        print(f"    Target: {interaction.target_cell}")
        print(f"    Molecules: {interaction.molecules}")
    
    # Get interaction summary
    summary = manager.get_interaction_summary()
    print(f"\nInteraction summary: {summary}")
    
    print("Neighbor interactions template created successfully!")
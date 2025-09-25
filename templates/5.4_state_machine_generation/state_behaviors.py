"""
State Behaviors Template
=======================

State-dependent behavior templates based on tumor-tcell repository patterns.

This template provides:
- State-specific behavior implementations
- Molecular production and consumption patterns
- Migration and interaction behaviors
- Death and division behaviors

Usage:
    from state_behaviors import BehaviorLibrary, StateBehavior
    
    behavior = BehaviorLibrary.get_tumor_growth_behavior()
    result = behavior.execute(context)
"""

from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import random
import math

from .probability_transitions import ProbabilityCalculator, get_probability_timestep


@dataclass
class BehaviorResult:
    """Result of executing a state behavior"""
    internal_update: Dict[str, Any]
    boundary_update: Dict[str, Any]
    neighbors_update: Dict[str, Any]
    globals_update: Dict[str, Any]
    biological_context: str = ""


class StateBehavior(ABC):
    """Abstract base class for state-dependent behaviors"""
    
    def __init__(self, name: str, biological_context: str = ""):
        self.name = name
        self.biological_context = biological_context
        self.parameters = {}
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> BehaviorResult:
        """Execute the behavior and return updates"""
        pass
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set behavior parameters"""
        self.parameters.update(parameters)
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get a behavior parameter"""
        return self.parameters.get(name, default)


class MolecularProductionBehavior(StateBehavior):
    """
    Behavior for molecular production based on tumor-tcell patterns.
    
    Handles:
    - Cytokine production (IFN-γ, IL-2, etc.)
    - Checkpoint molecule expression (PDL1, PD1, etc.)
    - Cytotoxic packet release
    - Molecular internalization and degradation
    """
    
    def __init__(self, molecules: Dict[str, float], biological_context: str = ""):
        super().__init__("molecular_production", biological_context)
        self.molecules = molecules  # molecule_name -> production_rate
    
    def execute(self, context: Dict[str, Any]) -> BehaviorResult:
        """Execute molecular production"""
        timestep = context.get('timestep', 1.0)
        
        boundary_update = {'exchange': {}}
        neighbors_update = {'present': {}}
        
        for molecule, rate in self.molecules.items():
            if rate > 0:
                amount = rate * timestep
                
                # Determine where molecule goes based on type
                if molecule in ['IFNg', 'IL2', 'TNFa']:
                    # Secreted cytokines go to boundary exchange
                    boundary_update['exchange'][molecule] = amount
                
                elif molecule in ['PDL1', 'MHCI', 'TCR', 'PD1']:
                    # Surface molecules go to neighbors present
                    neighbors_update['present'][molecule] = amount
                
                elif molecule in ['cytotoxic_packets']:
                    # Cytotoxic molecules go to neighbors transfer
                    if 'transfer' not in neighbors_update:
                        neighbors_update['transfer'] = {}
                    neighbors_update['transfer'][molecule] = amount
        
        return BehaviorResult(
            internal_update={},
            boundary_update=boundary_update,
            neighbors_update=neighbors_update,
            globals_update={},
            biological_context=f"Molecular production: {list(self.molecules.keys())}"
        )


class MolecularInternalizationBehavior(StateBehavior):
    """
    Behavior for molecular internalization and degradation.
    Based on tumor-tcell patterns for IFN-γ uptake.
    """
    
    def __init__(self, molecules: Dict[str, Dict[str, float]], biological_context: str = ""):
        super().__init__("molecular_internalization", biological_context)
        self.molecules = molecules  # molecule_name -> {'rate': rate, 'threshold': threshold}
    
    def execute(self, context: Dict[str, Any]) -> BehaviorResult:
        """Execute molecular internalization"""
        timestep = context.get('timestep', 1.0)
        
        internal_update = {}
        boundary_update = {'exchange': {}}
        
        for molecule, params in self.molecules.items():
            internalization_rate = params.get('rate', 0)
            available_external = context.get('boundary', {}).get('external', {}).get(molecule, 0)
            
            if internalization_rate > 0 and available_external > 0:
                # Calculate internalization amount
                max_internalization = internalization_rate * timestep
                actual_internalization = min(max_internalization, available_external)
                
                # Update internal amount (accumulate)
                current_internal = context.get('internal', {}).get(molecule, 0)
                internal_update[molecule] = actual_internalization
                
                # Remove from external (negative exchange)
                boundary_update['exchange'][molecule] = -actual_internalization
        
        return BehaviorResult(
            internal_update=internal_update,
            boundary_update=boundary_update,
            neighbors_update={},
            globals_update={},
            biological_context=f"Molecular internalization: {list(self.molecules.keys())}"
        )


class MigrationBehavior(StateBehavior):
    """
    Migration behavior based on tumor-tcell patterns.
    
    Handles:
    - Velocity changes based on cell state
    - Directional migration (chemotaxis)
    - Contact-dependent migration changes
    """
    
    def __init__(self, base_velocity: float, biological_context: str = ""):
        super().__init__("migration", biological_context)
        self.base_velocity = base_velocity
    
    def execute(self, context: Dict[str, Any]) -> BehaviorResult:
        """Execute migration behavior"""
        # Get migration modifiers from context
        velocity_modifier = self.get_velocity_modifier(context)
        final_velocity = self.base_velocity * velocity_modifier
        
        boundary_update = {}
        if final_velocity != context.get('boundary', {}).get('velocity', 0):
            boundary_update['velocity'] = final_velocity
        
        return BehaviorResult(
            internal_update={},
            boundary_update=boundary_update,
            neighbors_update={},
            globals_update={},
            biological_context=f"Migration with velocity {final_velocity}"
        )
    
    def get_velocity_modifier(self, context: Dict[str, Any]) -> float:
        """Calculate velocity modifier based on context"""
        modifier = 1.0
        
        # Example: reduce velocity when in contact with other cells
        neighbors_present = context.get('neighbors', {}).get('present', {})
        if neighbors_present:
            # Slow down when in contact
            modifier *= 0.7
        
        # Example: increase velocity when detecting chemokines
        external = context.get('boundary', {}).get('external', {})
        if external.get('chemokine', 0) > 100:
            modifier *= 1.5
        
        return modifier


class DivisionBehavior(StateBehavior):
    """
    Cell division behavior based on tumor-tcell patterns.
    
    Handles:
    - Probability-based division
    - State-dependent division rates
    - Division counters and tracking
    """
    
    def __init__(self, division_rate: float, timescale: float, biological_context: str = ""):
        super().__init__("division", biological_context)
        self.division_rate = division_rate
        self.timescale = timescale
        self.probability_calc = ProbabilityCalculator()
    
    def execute(self, context: Dict[str, Any]) -> BehaviorResult:
        """Execute division behavior"""
        timestep = context.get('timestep', 1.0)
        
        # Calculate division probability
        prob_divide = self.probability_calc.calculate_timestep_probability(
            self.division_rate, self.timescale, timestep
        )
        
        # Check division conditions
        can_divide = self.check_division_conditions(context)
        
        if can_divide and random.random() < prob_divide:
            # Division occurs
            division_count = self.get_parameter('division_count_key', 'divide_count')
            
            globals_update = {
                'divide': True,
                division_count: 1
            }
            
            return BehaviorResult(
                internal_update={},
                boundary_update={},
                neighbors_update={},
                globals_update=globals_update,
                biological_context=f"Cell division with rate {self.division_rate}"
            )
        
        return BehaviorResult({}, {}, {}, {}, "No division")
    
    def check_division_conditions(self, context: Dict[str, Any]) -> bool:
        """Check if cell can divide based on current conditions"""
        # Example conditions from tumor-tcell patterns
        
        # Check cell state allows division
        cell_state = context.get('internal', {}).get('cell_state', '')
        if cell_state in self.get_parameter('non_dividing_states', ['PDL1p', 'PD1p_exhausted']):
            return False
        
        # Check for space constraints (simplified)
        neighbor_count = len(context.get('neighbors', {}).get('present', {}))
        if neighbor_count > self.get_parameter('max_neighbors_for_division', 8):
            return False
        
        # Check for resource availability (simplified)
        internal_energy = context.get('internal', {}).get('energy', 100)
        if internal_energy < self.get_parameter('min_energy_for_division', 50):
            return False
        
        return True


class DeathBehavior(StateBehavior):
    """
    Cell death behavior based on tumor-tcell patterns.
    
    Handles:
    - Apoptotic death
    - Cytotoxic death
    - Death-associated molecular release
    """
    
    def __init__(self, death_rates: Dict[str, float], biological_context: str = ""):
        super().__init__("death", biological_context)
        self.death_rates = death_rates  # death_type -> rate
        self.probability_calc = ProbabilityCalculator()
    
    def execute(self, context: Dict[str, Any]) -> BehaviorResult:
        """Execute death behavior"""
        timestep = context.get('timestep', 1.0)
        
        # Check each death mechanism
        for death_type, params in self.death_rates.items():
            if self.check_death_condition(death_type, context):
                # Execute death
                death_result = self.execute_death(death_type, context)
                if death_result:
                    return death_result
        
        return BehaviorResult({}, {}, {}, {}, "No death")
    
    def check_death_condition(self, death_type: str, context: Dict[str, Any]) -> bool:
        """Check if death condition is met"""
        timestep = context.get('timestep', 1.0)
        
        if death_type == 'apoptosis':
            death_rate = self.death_rates[death_type]
            timescale = self.get_parameter('apoptosis_timescale', 432000)  # 5 days
            prob_death = self.probability_calc.calculate_timestep_probability(
                death_rate, timescale, timestep
            )
            return random.random() < prob_death
        
        elif death_type == 'cytotoxic':
            cytotoxic_packets = context.get('neighbors', {}).get('receive', {}).get('cytotoxic_packets', 0)
            threshold = self.get_parameter('cytotoxic_threshold', 12800)
            return cytotoxic_packets >= threshold
        
        elif death_type == 'necrosis':
            # Example: necrosis from lack of nutrients
            nutrients = context.get('boundary', {}).get('external', {}).get('glucose', 100)
            return nutrients < self.get_parameter('necrosis_threshold', 10)
        
        return False
    
    def execute_death(self, death_type: str, context: Dict[str, Any]) -> Optional[BehaviorResult]:
        """Execute specific death mechanism"""
        # Release death-associated molecules
        boundary_update = {'exchange': {}}
        
        if death_type in ['apoptosis', 'cytotoxic']:
            # Release tumor debris/DAMPs
            debris_amount = self.get_parameter('debris_amount', 1.4e15)
            boundary_update['exchange']['tumor_debris'] = int(debris_amount)
        
        # Set death flag
        globals_update = {'death': death_type}
        
        return BehaviorResult(
            internal_update={},
            boundary_update=boundary_update,
            neighbors_update={},
            globals_update=globals_update,
            biological_context=f"Cell death by {death_type}"
        )


class TimerBehavior(StateBehavior):
    """
    Timer-based behavior for tracking activation, refractory periods, etc.
    Based on tumor-tcell T cell activation patterns.
    """
    
    def __init__(self, timer_configs: Dict[str, Dict[str, Any]], biological_context: str = ""):
        super().__init__("timer", biological_context)
        self.timer_configs = timer_configs
    
    def execute(self, context: Dict[str, Any]) -> BehaviorResult:
        """Execute timer behavior"""
        timestep = context.get('timestep', 1.0)
        internal_update = {}
        neighbors_update = {'present': {}}
        
        for timer_name, config in self.timer_configs.items():
            current_timer = context.get('internal', {}).get(timer_name, 0)
            threshold = config.get('threshold', 0)
            reset_value = config.get('reset_value', 0)
            increment_condition = config.get('increment_condition', lambda ctx: True)
            
            # Check if timer should increment
            if increment_condition(context):
                new_timer = current_timer + timestep
                internal_update[timer_name] = timestep  # Increment by timestep
                
                # Check for threshold crossing
                if new_timer > threshold and current_timer <= threshold:
                    # Threshold crossed - execute threshold action
                    threshold_action = config.get('threshold_action')
                    if threshold_action:
                        action_result = threshold_action(context, new_timer)
                        if action_result:
                            # Merge action result
                            internal_update.update(action_result.get('internal', {}))
                            neighbors_update['present'].update(
                                action_result.get('neighbors', {}).get('present', {})
                            )
                
                # Check for reset condition
                reset_threshold = config.get('reset_threshold')
                if reset_threshold and new_timer > reset_threshold:
                    internal_update[timer_name] = reset_value - current_timer  # Reset timer
                    
                    # Execute reset action
                    reset_action = config.get('reset_action')
                    if reset_action:
                        reset_result = reset_action(context, new_timer)
                        if reset_result:
                            internal_update.update(reset_result.get('internal', {}))
                            neighbors_update['present'].update(
                                reset_result.get('neighbors', {}).get('present', {})
                            )
        
        return BehaviorResult(
            internal_update=internal_update,
            boundary_update={},
            neighbors_update=neighbors_update,
            globals_update={},
            biological_context="Timer management"
        )


class BehaviorLibrary:
    """
    Library of common state behaviors based on tumor-tcell patterns.
    """
    
    @staticmethod
    def get_tumor_growth_behavior(growth_rate: float = 0.6) -> DivisionBehavior:
        """Get tumor cell growth behavior"""
        behavior = DivisionBehavior(
            division_rate=growth_rate,
            timescale=86400,  # 24 hours
            biological_context="Tumor cell proliferation"
        )
        behavior.set_parameters({
            'non_dividing_states': ['PDL1p'],
            'division_count_key': 'PDL1n_divide_count'
        })
        return behavior
    
    @staticmethod
    def get_tumor_death_behavior() -> DeathBehavior:
        """Get tumor cell death behavior"""
        behavior = DeathBehavior(
            death_rates={'apoptosis': 0.5, 'cytotoxic': 1.0},
            biological_context="Tumor cell death mechanisms"
        )
        behavior.set_parameters({
            'apoptosis_timescale': 432000,  # 5 days
            'cytotoxic_threshold': 12800,
            'debris_amount': 1.4e15
        })
        return behavior
    
    @staticmethod
    def get_tumor_ifng_internalization_behavior() -> MolecularInternalizationBehavior:
        """Get tumor cell IFN-γ internalization behavior"""
        return MolecularInternalizationBehavior(
            molecules={
                'IFNg': {'rate': 31/60, 'reduction_factor': 2}  # From tumor-tcell patterns
            },
            biological_context="IFN-gamma internalization and degradation"
        )
    
    @staticmethod
    def get_tumor_pdl1_expression_behavior() -> MolecularProductionBehavior:
        """Get tumor cell PDL1 expression behavior (PDL1p state)"""
        return MolecularProductionBehavior(
            molecules={
                'PDL1': 5e4,  # PDL1p_PDL1_equilibrium
                'MHCI': 5e4   # PDL1p_MHCI_equilibrium
            },
            biological_context="Immune checkpoint molecule expression"
        )
    
    @staticmethod
    def get_tcell_cytotoxic_behavior() -> MolecularProductionBehavior:
        """Get T cell cytotoxic function behavior (PD1n state)"""
        return MolecularProductionBehavior(
            molecules={
                'cytotoxic_packets': 0.5,
                'IFNg': 2.78e-4
            },
            biological_context="T cell cytotoxic and cytokine function"
        )
    
    @staticmethod
    def get_tcell_migration_behavior(state: str = 'PD1n') -> MigrationBehavior:
        """Get T cell migration behavior"""
        velocity = 10.0 if state == 'PD1n' else 5.0  # PD1n vs PD1p
        
        behavior = MigrationBehavior(
            base_velocity=velocity,
            biological_context=f"T cell migration in {state} state"
        )
        return behavior
    
    @staticmethod
    def get_tcell_activation_timer_behavior() -> TimerBehavior:
        """Get T cell activation timer behavior"""
        def tcr_downregulation_action(context, timer_value):
            """Action when TCR downregulation occurs"""
            return {'neighbors': {'present': {'TCR': 0}}}
        
        def tcr_upregulation_action(context, timer_value):
            """Action when TCR upregulation occurs"""
            return {
                'neighbors': {'present': {'TCR': 50000}},
                'internal': {'refractory_count': 1}
            }
        
        timer_configs = {
            'TCR_timer': {
                'threshold': 21600,  # 6 hours activation
                'reset_threshold': 43200,  # 12 hours refractory
                'reset_value': -43200,
                'threshold_action': tcr_downregulation_action,
                'reset_action': tcr_upregulation_action,
                'increment_condition': lambda ctx: (
                    ctx.get('neighbors', {}).get('accept', {}).get('MHCI', 0) > 1000 or
                    ctx.get('internal', {}).get('TCR_timer', 0) > 21600
                )
            }
        }
        
        return TimerBehavior(
            timer_configs=timer_configs,
            biological_context="T cell activation and refractory cycles"
        )
    
    @staticmethod
    def get_dendritic_activation_behavior() -> MolecularProductionBehavior:
        """Get dendritic cell activation behavior (active state)"""
        return MolecularProductionBehavior(
            molecules={
                'PDL1': 5e4,
                'MHCI': 5e4
            },
            biological_context="Dendritic cell antigen presentation"
        )
    
    @staticmethod
    def get_dendritic_migration_behavior(state: str = 'inactive') -> MigrationBehavior:
        """Get dendritic cell migration behavior"""
        velocity = 3.0 if state == 'inactive' else 12.5  # inactive vs active
        
        return MigrationBehavior(
            base_velocity=velocity,
            biological_context=f"Dendritic cell migration in {state} state"
        )


class BehaviorManager:
    """
    Manager for organizing and executing multiple behaviors for a cell state.
    """
    
    def __init__(self):
        self.behaviors: Dict[str, StateBehavior] = {}
        self.execution_order: List[str] = []
    
    def add_behavior(self, behavior: StateBehavior, execution_priority: int = 0):
        """Add a behavior to the manager"""
        self.behaviors[behavior.name] = behavior
        
        # Insert in execution order based on priority
        inserted = False
        for i, existing_name in enumerate(self.execution_order):
            if execution_priority < getattr(self.behaviors[existing_name], 'priority', 0):
                self.execution_order.insert(i, behavior.name)
                inserted = True
                break
        
        if not inserted:
            self.execution_order.append(behavior.name)
        
        # Set priority on behavior
        behavior.priority = execution_priority
    
    def remove_behavior(self, behavior_name: str):
        """Remove a behavior from the manager"""
        if behavior_name in self.behaviors:
            del self.behaviors[behavior_name]
            self.execution_order.remove(behavior_name)
    
    def execute_all_behaviors(self, context: Dict[str, Any]) -> BehaviorResult:
        """Execute all behaviors in order and merge results"""
        merged_result = BehaviorResult({}, {}, {}, {})
        
        for behavior_name in self.execution_order:
            if behavior_name in self.behaviors:
                behavior = self.behaviors[behavior_name]
                result = behavior.execute(context)
                
                # Merge results
                merged_result.internal_update.update(result.internal_update)
                merged_result.boundary_update.update(result.boundary_update)
                merged_result.neighbors_update.update(result.neighbors_update)
                merged_result.globals_update.update(result.globals_update)
                
                # Update context with internal changes for next behavior
                context.setdefault('internal', {}).update(result.internal_update)
        
        return merged_result
    
    def get_behavior_summary(self) -> Dict[str, Any]:
        """Get summary of managed behaviors"""
        return {
            'total_behaviors': len(self.behaviors),
            'execution_order': self.execution_order,
            'behavior_types': [
                type(behavior).__name__ for behavior in self.behaviors.values()
            ]
        }


# Example usage and testing
if __name__ == '__main__':
    # Test molecular production behavior
    ifng_production = MolecularProductionBehavior(
        molecules={'IFNg': 2.78e-4, 'cytotoxic_packets': 0.5},
        biological_context="T cell cytotoxic function"
    )
    
    context = {'timestep': 60}
    result = ifng_production.execute(context)
    print(f"IFN-γ production result: {result.boundary_update}")
    
    # Test behavior manager
    manager = BehaviorManager()
    
    # Add tumor behaviors
    manager.add_behavior(BehaviorLibrary.get_tumor_growth_behavior(), priority=1)
    manager.add_behavior(BehaviorLibrary.get_tumor_death_behavior(), priority=0)  # Check death first
    
    tumor_context = {
        'timestep': 3600,
        'internal': {'cell_state': 'PDL1n', 'energy': 80},
        'neighbors': {'receive': {'cytotoxic_packets': 5000}}
    }
    
    combined_result = manager.execute_all_behaviors(tumor_context)
    print(f"Combined tumor behaviors result: {combined_result.globals_update}")
    
    print("State behaviors template created successfully!")
"""
State Machine Base Template
==========================

Abstract base classes for state machine implementation based on tumor-tcell patterns.

This template provides:
- Abstract state machine framework
- State definition and validation
- Transition logic infrastructure
- Event-driven state changes

Usage:
    from state_machine_base import StateMachine, State, Transition
    
    class CellStateMachine(StateMachine):
        def _define_states(self):
            # Define cell-specific states
            pass
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import math
import logging

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class StateMetadata:
    """Metadata for a state including biological context"""
    name: str
    description: str
    biological_context: str
    behaviors: Dict[str, Any]
    molecular_production: Dict[str, float]
    migration_properties: Dict[str, float]
    death_rates: Dict[str, float]
    division_rates: Dict[str, float]


@dataclass  
class TransitionCondition:
    """Condition that must be met for a state transition"""
    condition_type: str  # 'threshold', 'probability', 'timer', 'molecular'
    parameter: str
    operator: str  # '>', '<', '>=', '<=', '=='
    threshold: float
    biological_context: str


@dataclass
class TransitionMetadata:
    """Metadata for a state transition"""
    from_state: str
    to_state: str
    conditions: List[TransitionCondition]
    probability_function: Optional[Callable] = None
    biological_context: str = ""
    reversible: bool = False


class State:
    """
    Represents a cell state with associated behaviors and properties.
    
    Based on patterns from tumor-tcell repository where states like PDL1n/PDL1p,
    PD1n/PD1p, and active/inactive have distinct behaviors.
    """
    
    def __init__(self, name: str, metadata: StateMetadata):
        self.name = name
        self.metadata = metadata
        self.entry_actions: List[Callable] = []
        self.exit_actions: List[Callable] = []
        self.behaviors: Dict[str, Callable] = {}
    
    def add_entry_action(self, action: Callable):
        """Add action to perform when entering this state"""
        self.entry_actions.append(action)
    
    def add_exit_action(self, action: Callable):
        """Add action to perform when exiting this state"""
        self.exit_actions.append(action)
    
    def add_behavior(self, behavior_name: str, behavior_func: Callable):
        """Add state-specific behavior"""
        self.behaviors[behavior_name] = behavior_func
    
    def execute_entry_actions(self, context: Dict[str, Any]):
        """Execute all entry actions for this state"""
        for action in self.entry_actions:
            action(context)
    
    def execute_exit_actions(self, context: Dict[str, Any]):
        """Execute all exit actions for this state"""
        for action in self.exit_actions:
            action(context)
    
    def execute_behavior(self, behavior_name: str, context: Dict[str, Any]) -> Any:
        """Execute a specific behavior for this state"""
        if behavior_name in self.behaviors:
            return self.behaviors[behavior_name](context)
        return None
    
    def get_molecular_production(self, molecule: str) -> float:
        """Get production rate for a specific molecule in this state"""
        return self.metadata.molecular_production.get(molecule, 0.0)
    
    def get_migration_velocity(self) -> float:
        """Get migration velocity for this state"""
        return self.metadata.migration_properties.get('velocity', 0.0)
    
    def get_death_rate(self, death_type: str = 'apoptosis') -> float:
        """Get death rate for this state"""
        return self.metadata.death_rates.get(death_type, 0.0)
    
    def get_division_rate(self) -> float:
        """Get division rate for this state"""
        return self.metadata.division_rates.get('growth', 0.0)


class Transition:
    """
    Represents a transition between two states.
    
    Based on tumor-tcell patterns like IFN-γ triggering PDL1n→PDL1p transition
    or repeated activation leading to PD1n→PD1p exhaustion.
    """
    
    def __init__(self, metadata: TransitionMetadata):
        self.metadata = metadata
        self.from_state = metadata.from_state
        self.to_state = metadata.to_state
        self.conditions = metadata.conditions
        self.probability_function = metadata.probability_function
    
    def can_transition(self, context: Dict[str, Any]) -> bool:
        """Check if transition conditions are met"""
        for condition in self.conditions:
            if not self._evaluate_condition(condition, context):
                return False
        return True
    
    def _evaluate_condition(self, condition: TransitionCondition, context: Dict[str, Any]) -> bool:
        """Evaluate a single transition condition"""
        if condition.parameter not in context:
            logger.warning(f"Parameter {condition.parameter} not found in context")
            return False
        
        value = context[condition.parameter]
        threshold = condition.threshold
        
        # Handle different condition types
        if condition.condition_type == 'threshold':
            return self._evaluate_operator(value, condition.operator, threshold)
        
        elif condition.condition_type == 'probability':
            probability = threshold
            return random.random() < probability
        
        elif condition.condition_type == 'timer':
            timer_value = context.get('timer', 0)
            return self._evaluate_operator(timer_value, condition.operator, threshold)
        
        elif condition.condition_type == 'molecular':
            return self._evaluate_operator(value, condition.operator, threshold)
        
        return False
    
    def _evaluate_operator(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate comparison operators"""
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return abs(value - threshold) < 1e-9
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def get_transition_probability(self, context: Dict[str, Any]) -> float:
        """Get probability of transition occurring"""
        if self.probability_function:
            return self.probability_function(context)
        return 1.0 if self.can_transition(context) else 0.0


class StateMachine(ABC):
    """
    Abstract base class for cell state machines.
    
    Implements the core state machine logic based on patterns from
    tumor-tcell repository processes.
    """
    
    def __init__(self, initial_state: str):
        self.states: Dict[str, State] = {}
        self.transitions: Dict[str, List[Transition]] = {}
        self.current_state = initial_state
        self.state_history: List[Tuple[str, float]] = []  # (state, timestamp)
        self.transition_count: Dict[str, int] = {}
        
        # Initialize the state machine
        self._define_states()
        self._define_transitions()
        self._validate_state_machine()
    
    @abstractmethod
    def _define_states(self):
        """Define all possible states for this state machine"""
        pass
    
    @abstractmethod
    def _define_transitions(self):
        """Define all possible transitions between states"""
        pass
    
    def add_state(self, state: State):
        """Add a state to the state machine"""
        self.states[state.name] = state
        if state.name not in self.transitions:
            self.transitions[state.name] = []
    
    def add_transition(self, transition: Transition):
        """Add a transition to the state machine"""
        from_state = transition.from_state
        
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        
        self.transitions[from_state].append(transition)
    
    def get_current_state(self) -> State:
        """Get the current state object"""
        return self.states[self.current_state]
    
    def get_possible_transitions(self) -> List[Transition]:
        """Get all possible transitions from current state"""
        return self.transitions.get(self.current_state, [])
    
    def update(self, timestep: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the state machine for one timestep.
        
        Args:
            timestep: Time step size
            context: Current state of the system
        
        Returns:
            Dictionary of updates to apply
        """
        # Check for possible transitions
        possible_transitions = self.get_possible_transitions()
        
        # Evaluate transitions in order of priority
        for transition in possible_transitions:
            if transition.can_transition(context):
                probability = transition.get_transition_probability(context)
                
                if random.random() < probability:
                    # Execute the transition
                    self._execute_transition(transition, context)
                    break
        
        # Execute current state behaviors
        current_state_obj = self.get_current_state()
        return self._execute_state_behaviors(current_state_obj, timestep, context)
    
    def _execute_transition(self, transition: Transition, context: Dict[str, Any]):
        """Execute a state transition"""
        old_state = self.current_state
        new_state = transition.to_state
        
        logger.info(f"Transitioning from {old_state} to {new_state}")
        
        # Execute exit actions for old state
        if old_state in self.states:
            self.states[old_state].execute_exit_actions(context)
        
        # Update current state
        self.current_state = new_state
        
        # Record transition
        self.state_history.append((new_state, context.get('time', 0)))
        transition_key = f"{old_state}->{new_state}"
        self.transition_count[transition_key] = self.transition_count.get(transition_key, 0) + 1
        
        # Execute entry actions for new state
        if new_state in self.states:
            self.states[new_state].execute_entry_actions(context)
    
    def _execute_state_behaviors(self, state: State, timestep: float, 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute behaviors for the current state"""
        update = {
            'internal': {},
            'boundary': {},
            'neighbors': {'present': {}, 'accept': {}, 'transfer': {}}
        }
        
        # Execute molecular production
        molecular_update = self._calculate_molecular_production(state, timestep, context)
        if molecular_update:
            update['boundary'].update(molecular_update)
        
        # Execute migration behavior
        migration_update = self._calculate_migration(state, context)
        if migration_update:
            update['boundary'].update(migration_update)
        
        # Execute neighbor interactions
        neighbor_update = self._calculate_neighbor_interactions(state, context)
        if neighbor_update:
            update['neighbors'].update(neighbor_update)
        
        return update
    
    def _calculate_molecular_production(self, state: State, timestep: float,
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate molecular production for current state"""
        production = {}
        
        for molecule, rate in state.metadata.molecular_production.items():
            if rate > 0:
                amount = rate * timestep
                production[molecule] = amount
        
        return {'exchange': production} if production else {}
    
    def _calculate_migration(self, state: State, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate migration properties for current state"""
        velocity = state.get_migration_velocity()
        
        if velocity > 0:
            return {'velocity': velocity}
        
        return {}
    
    def _calculate_neighbor_interactions(self, state: State, 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate neighbor interactions for current state"""
        interactions = {'present': {}}
        
        # Add state-specific molecular presentations
        for molecule, amount in state.metadata.molecular_production.items():
            if amount > 0 and molecule in ['PDL1', 'MHCI', 'TCR']:
                interactions['present'][molecule] = amount
        
        return interactions
    
    def _validate_state_machine(self):
        """Validate the state machine configuration"""
        # Check that initial state exists
        if self.current_state not in self.states:
            raise ValueError(f"Initial state '{self.current_state}' not defined")
        
        # Check that all transitions reference valid states
        for from_state, transitions in self.transitions.items():
            if from_state not in self.states:
                raise ValueError(f"Transition from undefined state: {from_state}")
            
            for transition in transitions:
                if transition.to_state not in self.states:
                    raise ValueError(f"Transition to undefined state: {transition.to_state}")
        
        logger.info(f"State machine validated with {len(self.states)} states")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state machine status"""
        return {
            'current_state': self.current_state,
            'total_states': len(self.states),
            'state_history': self.state_history[-10:],  # Last 10 transitions
            'transition_counts': self.transition_count,
            'possible_transitions': [
                t.to_state for t in self.get_possible_transitions()
            ]
        }
    
    def reset(self, initial_state: str = None):
        """Reset state machine to initial state"""
        if initial_state:
            self.current_state = initial_state
        
        self.state_history.clear()
        self.transition_count.clear()


# Utility functions for common transition logic
def get_probability_timestep(probability_parameter: float, timescale: float, 
                           timestep: float) -> float:
    """
    Calculate transition probability as function of time.
    Based on tumor-tcell repository pattern.
    """
    rate = -math.log(1 - probability_parameter)
    timestep_fraction = timestep / timescale
    return 1 - math.exp(-rate * timestep_fraction)


def probability_of_occurrence_within_interval(interval_duration: float, 
                                            expected_time: float) -> float:
    """
    Compute probability of event occurring within time interval.
    Assumes Poisson process from tumor-tcell repository pattern.
    """
    lambda_ = interval_duration / expected_time
    P_0 = math.exp(-lambda_)
    P_at_least_one = 1 - P_0
    return P_at_least_one


def create_threshold_condition(parameter: str, operator: str, threshold: float,
                             biological_context: str = "") -> TransitionCondition:
    """Create a threshold-based transition condition"""
    return TransitionCondition(
        condition_type='threshold',
        parameter=parameter,
        operator=operator,
        threshold=threshold,
        biological_context=biological_context
    )


def create_probability_condition(probability: float, 
                               biological_context: str = "") -> TransitionCondition:
    """Create a probability-based transition condition"""
    return TransitionCondition(
        condition_type='probability',
        parameter='random',
        operator='<',
        threshold=probability,
        biological_context=biological_context
    )


def create_timer_condition(parameter: str, operator: str, threshold: float,
                         biological_context: str = "") -> TransitionCondition:
    """Create a timer-based transition condition"""
    return TransitionCondition(
        condition_type='timer',
        parameter=parameter,
        operator=operator,
        threshold=threshold,
        biological_context=biological_context
    )


# Example usage and testing
if __name__ == '__main__':
    # This would be implemented by specific cell type state machines
    # See cell_state_transitions.py for concrete implementations
    
    print("State machine base template created successfully!")
    
    # Example of creating conditions
    ifng_condition = create_threshold_condition(
        'IFNg_internal', '>=', 15000,
        'IFN-gamma threshold for PDL1n to PDL1p transition'
    )
    
    growth_condition = create_probability_condition(
        0.6, 'Probability of cell division in 24 hours'
    )
    
    print(f"Created threshold condition: {ifng_condition}")
    print(f"Created probability condition: {growth_condition}")
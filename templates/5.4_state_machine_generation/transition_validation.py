"""
Transition Validation Template
=============================

State transition validation and testing based on tumor-tcell repository patterns.

This template provides:
- State machine validation utilities
- Transition logic testing
- Behavior verification
- Statistical analysis of transitions

Usage:
    from transition_validation import StateMachineValidator, TransitionTester
    
    validator = StateMachineValidator()
    results = validator.validate_state_machine(state_machine)
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import json

from .state_machine_base import StateMachine, State, Transition
from .cell_state_transitions import create_cell_state_machine
from .probability_transitions import ProbabilityCalculator


@dataclass
class ValidationResult:
    """Result of state machine validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    summary: Dict[str, Any]


@dataclass
class TransitionTestResult:
    """Result of transition testing"""
    transition_name: str
    success_rate: float
    expected_probability: float
    actual_probability: float
    statistical_significance: float
    biological_plausibility: bool
    context_variations: List[Dict[str, Any]]


class StateMachineValidator:
    """
    Validator for state machine configurations and logic.
    
    Provides comprehensive validation including:
    - Structural validation (states, transitions)
    - Biological plausibility checks
    - Consistency validation
    - Performance analysis
    """
    
    def __init__(self):
        self.validation_rules = self._define_validation_rules()
    
    def _define_validation_rules(self) -> Dict[str, Any]:
        """Define validation rules for state machines"""
        return {
            'required_states': {
                'tumor': ['PDL1n', 'PDL1p'],
                'tcell': ['PD1n', 'PD1p'],
                'dendritic': ['inactive', 'active']
            },
            'required_transitions': {
                'tumor': ['PDL1n->PDL1p'],
                'tcell': ['PD1n->PD1p'],
                'dendritic': ['inactive->active']
            },
            'biological_constraints': {
                'max_states': 10,
                'max_transitions_per_state': 5,
                'probability_range': (0.0, 1.0),
                'required_behaviors': ['molecular_production', 'death']
            },
            'performance_limits': {
                'max_update_time_ms': 10.0,
                'max_memory_usage_mb': 100.0
            }
        }
    
    def validate_state_machine(self, state_machine: StateMachine, 
                             cell_type: str = None) -> ValidationResult:
        """
        Comprehensive validation of a state machine.
        
        Args:
            state_machine: State machine to validate
            cell_type: Type of cell for specific validation rules
        
        Returns:
            ValidationResult with validation outcome
        """
        errors = []
        warnings = []
        
        # Structural validation
        struct_errors, struct_warnings = self._validate_structure(state_machine)
        errors.extend(struct_errors)
        warnings.extend(struct_warnings)
        
        # State validation
        state_errors, state_warnings = self._validate_states(state_machine)
        errors.extend(state_errors)
        warnings.extend(state_warnings)
        
        # Transition validation
        trans_errors, trans_warnings = self._validate_transitions(state_machine)
        errors.extend(trans_errors)
        warnings.extend(trans_warnings)
        
        # Cell type specific validation
        if cell_type:
            type_errors, type_warnings = self._validate_cell_type_specific(
                state_machine, cell_type
            )
            errors.extend(type_errors)
            warnings.extend(type_warnings)
        
        # Biological plausibility
        bio_errors, bio_warnings = self._validate_biological_plausibility(state_machine)
        errors.extend(bio_errors)
        warnings.extend(bio_warnings)
        
        # Generate summary
        summary = self._generate_validation_summary(state_machine)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            summary=summary
        )
    
    def _validate_structure(self, state_machine: StateMachine) -> Tuple[List[str], List[str]]:
        """Validate basic structural integrity"""
        errors = []
        warnings = []
        
        # Check for states
        if not state_machine.states:
            errors.append("State machine has no states defined")
        
        # Check for initial state
        if state_machine.current_state not in state_machine.states:
            errors.append(f"Initial state '{state_machine.current_state}' is not defined")
        
        # Check for unreachable states
        reachable_states = self._find_reachable_states(state_machine)
        unreachable = set(state_machine.states.keys()) - reachable_states
        if unreachable:
            warnings.append(f"Unreachable states found: {unreachable}")
        
        # Check for dead-end states (states with no outgoing transitions except death)
        dead_ends = self._find_dead_end_states(state_machine)
        if dead_ends:
            warnings.append(f"Dead-end states found: {dead_ends}")
        
        return errors, warnings
    
    def _validate_states(self, state_machine: StateMachine) -> Tuple[List[str], List[str]]:
        """Validate individual states"""
        errors = []
        warnings = []
        
        for state_name, state in state_machine.states.items():
            # Check state metadata
            if not state.metadata:
                warnings.append(f"State '{state_name}' has no metadata")
            
            # Check biological context
            if not state.metadata.biological_context:
                warnings.append(f"State '{state_name}' has no biological context")
            
            # Check for required behaviors
            required_behaviors = self.validation_rules['biological_constraints']['required_behaviors']
            state_behaviors = set(state.behaviors.keys())
            missing_behaviors = set(required_behaviors) - state_behaviors
            if missing_behaviors:
                warnings.append(
                    f"State '{state_name}' missing behaviors: {missing_behaviors}"
                )
            
            # Validate molecular production rates
            for molecule, rate in state.metadata.molecular_production.items():
                if rate < 0:
                    errors.append(
                        f"State '{state_name}' has negative production rate for {molecule}: {rate}"
                    )
                
                if rate > 1e6:  # Arbitrary large number check
                    warnings.append(
                        f"State '{state_name}' has very high production rate for {molecule}: {rate}"
                    )
        
        return errors, warnings
    
    def _validate_transitions(self, state_machine: StateMachine) -> Tuple[List[str], List[str]]:
        """Validate state transitions"""
        errors = []
        warnings = []
        
        for from_state, transitions in state_machine.transitions.items():
            if from_state not in state_machine.states:
                errors.append(f"Transition from undefined state: {from_state}")
                continue
            
            # Check transition count
            max_transitions = self.validation_rules['biological_constraints']['max_transitions_per_state']
            if len(transitions) > max_transitions:
                warnings.append(
                    f"State '{from_state}' has {len(transitions)} transitions "
                    f"(max recommended: {max_transitions})"
                )
            
            for transition in transitions:
                # Check target state exists
                if transition.to_state not in state_machine.states:
                    errors.append(f"Transition to undefined state: {transition.to_state}")
                
                # Validate transition conditions
                for condition in transition.conditions:
                    if not condition.parameter:
                        errors.append(f"Transition condition has no parameter specified")
                    
                    if condition.threshold < 0 and condition.condition_type != 'timer':
                        warnings.append(
                            f"Negative threshold in transition {from_state}->{transition.to_state}"
                        )
                
                # Check biological context
                if not transition.metadata.biological_context:
                    warnings.append(
                        f"Transition {from_state}->{transition.to_state} has no biological context"
                    )
        
        return errors, warnings
    
    def _validate_cell_type_specific(self, state_machine: StateMachine, 
                                   cell_type: str) -> Tuple[List[str], List[str]]:
        """Validate cell type specific requirements"""
        errors = []
        warnings = []
        
        if cell_type not in self.validation_rules['required_states']:
            warnings.append(f"No specific validation rules for cell type: {cell_type}")
            return errors, warnings
        
        # Check required states
        required_states = set(self.validation_rules['required_states'][cell_type])
        actual_states = set(state_machine.states.keys())
        missing_states = required_states - actual_states
        
        if missing_states:
            errors.append(f"Missing required states for {cell_type}: {missing_states}")
        
        # Check required transitions
        required_transitions = self.validation_rules['required_transitions'][cell_type]
        actual_transitions = []
        
        for from_state, transitions in state_machine.transitions.items():
            for transition in transitions:
                actual_transitions.append(f"{from_state}->{transition.to_state}")
        
        for required_transition in required_transitions:
            if required_transition not in actual_transitions:
                errors.append(f"Missing required transition for {cell_type}: {required_transition}")
        
        return errors, warnings
    
    def _validate_biological_plausibility(self, state_machine: StateMachine) -> Tuple[List[str], List[str]]:
        """Validate biological plausibility of state machine"""
        errors = []
        warnings = []
        
        # Check for biologically implausible transitions
        for from_state, transitions in state_machine.transitions.items():
            for transition in transitions:
                # Example: Check if exhausted cells can become active (usually not possible)
                if ('exhausted' in from_state.lower() or 'p' in from_state and 
                    'active' in transition.to_state.lower() or 'n' in transition.to_state):
                    warnings.append(
                        f"Potentially implausible transition: {from_state}->{transition.to_state}"
                    )
        
        # Check molecular production consistency
        for state_name, state in state_machine.states.items():
            production = state.metadata.molecular_production
            
            # Check for contradictory molecular production
            if 'PDL1' in production and production['PDL1'] > 0:
                if 'immune_suppression' not in state.metadata.behaviors:
                    warnings.append(
                        f"State '{state_name}' produces PDL1 but doesn't have immune suppression behavior"
                    )
            
            # Check migration velocities
            migration = state.metadata.migration_properties
            velocity = migration.get('velocity', 0)
            
            if velocity > 50:  # Very fast for cellular scale
                warnings.append(
                    f"State '{state_name}' has very high migration velocity: {velocity}"
                )
        
        return errors, warnings
    
    def _find_reachable_states(self, state_machine: StateMachine) -> Set[str]:
        """Find all states reachable from initial state"""
        reachable = {state_machine.current_state}
        to_visit = [state_machine.current_state]
        
        while to_visit:
            current = to_visit.pop()
            if current in state_machine.transitions:
                for transition in state_machine.transitions[current]:
                    if transition.to_state not in reachable:
                        reachable.add(transition.to_state)
                        to_visit.append(transition.to_state)
        
        return reachable
    
    def _find_dead_end_states(self, state_machine: StateMachine) -> Set[str]:
        """Find states with no outgoing transitions"""
        dead_ends = set()
        
        for state_name in state_machine.states:
            if state_name not in state_machine.transitions or not state_machine.transitions[state_name]:
                dead_ends.add(state_name)
        
        return dead_ends
    
    def _generate_validation_summary(self, state_machine: StateMachine) -> Dict[str, Any]:
        """Generate validation summary statistics"""
        total_states = len(state_machine.states)
        total_transitions = sum(len(transitions) for transitions in state_machine.transitions.values())
        
        return {
            'total_states': total_states,
            'total_transitions': total_transitions,
            'initial_state': state_machine.current_state,
            'reachable_states': len(self._find_reachable_states(state_machine)),
            'dead_end_states': len(self._find_dead_end_states(state_machine)),
            'avg_transitions_per_state': total_transitions / max(total_states, 1)
        }


class TransitionTester:
    """
    Tester for validating transition probabilities and behaviors.
    
    Provides statistical testing of:
    - Transition probability accuracy
    - Behavior consistency
    - Performance characteristics
    """
    
    def __init__(self, num_samples: int = 1000):
        self.num_samples = num_samples
        self.probability_calc = ProbabilityCalculator()
    
    def test_transition_probability(self, state_machine: StateMachine,
                                  from_state: str, to_state: str,
                                  context_variations: List[Dict[str, Any]]) -> TransitionTestResult:
        """
        Test transition probability accuracy across different contexts.
        
        Args:
            state_machine: State machine to test
            from_state: Source state
            to_state: Target state  
            context_variations: List of context variations to test
        
        Returns:
            TransitionTestResult with testing results
        """
        # Find the transition
        transition = None
        if from_state in state_machine.transitions:
            for trans in state_machine.transitions[from_state]:
                if trans.to_state == to_state:
                    transition = trans
                    break
        
        if not transition:
            return TransitionTestResult(
                transition_name=f"{from_state}->{to_state}",
                success_rate=0.0,
                expected_probability=0.0,
                actual_probability=0.0,
                statistical_significance=0.0,
                biological_plausibility=False,
                context_variations=context_variations
            )
        
        # Test across context variations
        total_successes = 0
        total_tests = 0
        probabilities = []
        
        for context in context_variations:
            # Set initial state
            state_machine.current_state = from_state
            
            # Test transition multiple times
            successes = 0
            for _ in range(self.num_samples):
                # Reset state machine
                state_machine.current_state = from_state
                
                # Check if transition can occur
                if transition.can_transition(context):
                    probability = transition.get_transition_probability(context)
                    if random.random() < probability:
                        successes += 1
                
                total_tests += 1
            
            actual_prob = successes / self.num_samples
            probabilities.append(actual_prob)
            total_successes += successes
        
        # Calculate overall statistics
        overall_success_rate = total_successes / max(total_tests, 1)
        mean_probability = np.mean(probabilities) if probabilities else 0.0
        
        # Calculate expected probability (simplified)
        expected_prob = self._calculate_expected_probability(transition, context_variations[0])
        
        # Statistical significance (simplified chi-square test)
        significance = self._calculate_statistical_significance(
            probabilities, expected_prob
        )
        
        # Biological plausibility
        plausibility = self._assess_biological_plausibility(from_state, to_state, transition)
        
        return TransitionTestResult(
            transition_name=f"{from_state}->{to_state}",
            success_rate=overall_success_rate,
            expected_probability=expected_prob,
            actual_probability=mean_probability,
            statistical_significance=significance,
            biological_plausibility=plausibility,
            context_variations=context_variations
        )
    
    def test_all_transitions(self, state_machine: StateMachine,
                           context_generator: callable = None) -> List[TransitionTestResult]:
        """Test all transitions in a state machine"""
        if not context_generator:
            context_generator = self._default_context_generator
        
        results = []
        context_variations = context_generator()
        
        for from_state, transitions in state_machine.transitions.items():
            for transition in transitions:
                result = self.test_transition_probability(
                    state_machine, from_state, transition.to_state, context_variations
                )
                results.append(result)
        
        return results
    
    def _calculate_expected_probability(self, transition: Transition, 
                                      context: Dict[str, Any]) -> float:
        """Calculate expected probability for transition"""
        if transition.probability_function:
            return transition.probability_function(context)
        
        # Simplified calculation based on conditions
        if transition.can_transition(context):
            return 0.5  # Default expected probability
        return 0.0
    
    def _calculate_statistical_significance(self, probabilities: List[float], 
                                          expected: float) -> float:
        """Calculate statistical significance of probability differences"""
        if not probabilities:
            return 0.0
        
        # Simplified t-test
        mean_prob = np.mean(probabilities)
        std_prob = np.std(probabilities)
        
        if std_prob == 0:
            return 1.0 if abs(mean_prob - expected) < 0.01 else 0.0
        
        t_statistic = abs(mean_prob - expected) / (std_prob / np.sqrt(len(probabilities)))
        
        # Simplified p-value calculation
        return max(0.0, 1.0 - t_statistic / 10.0)
    
    def _assess_biological_plausibility(self, from_state: str, to_state: str,
                                      transition: Transition) -> bool:
        """Assess biological plausibility of transition"""
        # Basic heuristics for biological plausibility
        
        # Check if transition makes biological sense
        if 'exhausted' in from_state.lower() and 'active' in to_state.lower():
            return False  # Exhausted cells typically don't become active
        
        if 'dead' in from_state.lower() or 'death' in from_state.lower():
            return False  # Dead cells don't transition to other states
        
        # Check if conditions are biologically reasonable
        for condition in transition.conditions:
            if condition.threshold < 0 and condition.condition_type != 'timer':
                return False
            
            if condition.threshold > 1e10:  # Extremely high threshold
                return False
        
        return True
    
    def _default_context_generator(self) -> List[Dict[str, Any]]:
        """Generate default context variations for testing"""
        return [
            # Low molecular context
            {
                'timestep': 60,
                'IFNg_internal': 5000,
                'cytotoxic_packets': 1000,
                'refractory_count': 1,
                'internal_tumor_debris': 1e5
            },
            # Medium molecular context
            {
                'timestep': 60,
                'IFNg_internal': 15000,
                'cytotoxic_packets': 8000,
                'refractory_count': 3,
                'internal_tumor_debris': 1e7
            },
            # High molecular context
            {
                'timestep': 60,
                'IFNg_internal': 30000,
                'cytotoxic_packets': 20000,
                'refractory_count': 5,
                'internal_tumor_debris': 1e8
            }
        ]


class StateMachineProfiler:
    """
    Profiler for analyzing state machine performance and behavior patterns.
    """
    
    def __init__(self):
        self.transition_counts = defaultdict(int)
        self.state_durations = defaultdict(list)
        self.behavior_statistics = defaultdict(list)
    
    def profile_simulation(self, state_machine: StateMachine,
                          simulation_contexts: List[Dict[str, Any]],
                          num_steps: int = 1000) -> Dict[str, Any]:
        """
        Profile state machine behavior over a simulation.
        
        Args:
            state_machine: State machine to profile
            simulation_contexts: List of contexts for each simulation step
            num_steps: Number of simulation steps
        
        Returns:
            Profiling results dictionary
        """
        # Reset profiling data
        self.transition_counts.clear()
        self.state_durations.clear()
        self.behavior_statistics.clear()
        
        # Track state machine execution
        current_state = state_machine.current_state
        state_entry_time = 0
        
        for step in range(num_steps):
            context = simulation_contexts[step % len(simulation_contexts)]
            context['time'] = step
            
            # Record current state
            previous_state = state_machine.current_state
            
            # Update state machine
            update_result = state_machine.update(1.0, context)
            
            # Check for state transition
            if state_machine.current_state != previous_state:
                # Record transition
                transition_key = f"{previous_state}->{state_machine.current_state}"
                self.transition_counts[transition_key] += 1
                
                # Record state duration
                duration = step - state_entry_time
                self.state_durations[previous_state].append(duration)
                state_entry_time = step
            
            # Record behavior statistics
            if update_result:
                self._record_behavior_statistics(previous_state, update_result)
        
        # Record final state duration
        final_duration = num_steps - state_entry_time
        self.state_durations[state_machine.current_state].append(final_duration)
        
        return self._generate_profiling_report(num_steps)
    
    def _record_behavior_statistics(self, state: str, update_result: Dict[str, Any]):
        """Record statistics about behavior execution"""
        # Count molecular production
        if 'boundary' in update_result and 'exchange' in update_result['boundary']:
            for molecule, amount in update_result['boundary']['exchange'].items():
                self.behavior_statistics[f"{state}_production_{molecule}"].append(amount)
        
        # Count neighbor interactions
        if 'neighbors' in update_result:
            neighbor_data = update_result['neighbors']
            if 'present' in neighbor_data:
                present_count = len(neighbor_data['present'])
                self.behavior_statistics[f"{state}_neighbors_present"].append(present_count)
        
        # Count division/death events
        if 'globals' in update_result:
            globals_data = update_result['globals']
            if 'divide' in globals_data:
                self.behavior_statistics[f"{state}_divisions"].append(1)
            if 'death' in globals_data:
                self.behavior_statistics[f"{state}_deaths"].append(1)
    
    def _generate_profiling_report(self, num_steps: int) -> Dict[str, Any]:
        """Generate comprehensive profiling report"""
        report = {
            'simulation_steps': num_steps,
            'transition_frequencies': dict(self.transition_counts),
            'state_statistics': {},
            'behavior_statistics': {}
        }
        
        # Calculate state statistics
        for state, durations in self.state_durations.items():
            if durations:
                report['state_statistics'][state] = {
                    'total_time': sum(durations),
                    'average_duration': np.mean(durations),
                    'max_duration': max(durations),
                    'min_duration': min(durations),
                    'visit_count': len(durations)
                }
        
        # Calculate behavior statistics
        for behavior, values in self.behavior_statistics.items():
            if values:
                report['behavior_statistics'][behavior] = {
                    'total_events': len(values),
                    'total_amount': sum(values),
                    'average_amount': np.mean(values),
                    'max_amount': max(values),
                    'min_amount': min(values)
                }
        
        return report
    
    def visualize_results(self, profiling_report: Dict[str, Any], output_file: str = None):
        """Create visualizations of profiling results"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # State duration histogram
        if profiling_report['state_statistics']:
            states = list(profiling_report['state_statistics'].keys())
            durations = [profiling_report['state_statistics'][state]['average_duration'] 
                        for state in states]
            
            axes[0, 0].bar(states, durations)
            axes[0, 0].set_title('Average State Durations')
            axes[0, 0].set_ylabel('Duration (steps)')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Transition frequency plot
        if profiling_report['transition_frequencies']:
            transitions = list(profiling_report['transition_frequencies'].keys())
            counts = list(profiling_report['transition_frequencies'].values())
            
            axes[0, 1].bar(range(len(transitions)), counts)
            axes[0, 1].set_title('Transition Frequencies')
            axes[0, 1].set_ylabel('Count')
            axes[0, 1].set_xticks(range(len(transitions)))
            axes[0, 1].set_xticklabels(transitions, rotation=45)
        
        # State visit counts
        if profiling_report['state_statistics']:
            states = list(profiling_report['state_statistics'].keys())
            visits = [profiling_report['state_statistics'][state]['visit_count'] 
                     for state in states]
            
            axes[1, 0].pie(visits, labels=states, autopct='%1.1f%%')
            axes[1, 0].set_title('State Visit Distribution')
        
        # Behavior statistics (example: divisions)
        division_behaviors = {k: v for k, v in profiling_report['behavior_statistics'].items() 
                            if 'divisions' in k}
        
        if division_behaviors:
            behaviors = list(division_behaviors.keys())
            events = [division_behaviors[behavior]['total_events'] for behavior in behaviors]
            
            axes[1, 1].bar(behaviors, events)
            axes[1, 1].set_title('Division Events by State')
            axes[1, 1].set_ylabel('Total Events')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()


# Example usage and testing
if __name__ == '__main__':
    # Test state machine validation
    print("Testing state machine validation...")
    
    # Create test state machine
    tumor_sm = create_cell_state_machine('tumor')
    
    # Validate state machine
    validator = StateMachineValidator()
    validation_result = validator.validate_state_machine(tumor_sm, 'tumor')
    
    print(f"Validation result: {'PASS' if validation_result.is_valid else 'FAIL'}")
    print(f"Errors: {len(validation_result.errors)}")
    print(f"Warnings: {len(validation_result.warnings)}")
    print(f"Summary: {validation_result.summary}")
    
    if validation_result.errors:
        print("Errors found:")
        for error in validation_result.errors:
            print(f"  - {error}")
    
    if validation_result.warnings:
        print("Warnings found:")
        for warning in validation_result.warnings[:3]:  # Show first 3
            print(f"  - {warning}")
    
    # Test transition probabilities
    print("\nTesting transition probabilities...")
    
    tester = TransitionTester(num_samples=100)  # Reduced for example
    transition_results = tester.test_all_transitions(tumor_sm)
    
    for result in transition_results:
        print(f"Transition {result.transition_name}:")
        print(f"  Success rate: {result.success_rate:.3f}")
        print(f"  Expected prob: {result.expected_probability:.3f}")
        print(f"  Actual prob: {result.actual_probability:.3f}")
        print(f"  Biologically plausible: {result.biological_plausibility}")
    
    print("Transition validation template created successfully!")
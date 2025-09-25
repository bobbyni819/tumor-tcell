"""
Probability Transitions Template
===============================

Probability-based transition logic based on tumor-tcell repository patterns.

This template provides:
- Stochastic transition functions
- Time-dependent probability calculations
- Biological parameter-driven transitions
- Statistical distribution utilities

Usage:
    from probability_transitions import ProbabilityCalculator, create_transition_function
    
    calc = ProbabilityCalculator()
    prob = calc.calculate_timestep_probability(rate, timescale, timestep)
"""

import math
import random
from typing import Dict, Any, Callable, Optional, List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from scipy import stats


@dataclass
class ProbabilityParameters:
    """Parameters for probability calculations"""
    base_rate: float
    timescale: float
    temperature_factor: float = 1.0
    noise_level: float = 0.0
    saturation_threshold: Optional[float] = None
    biological_context: str = ""


class ProbabilityCalculator:
    """
    Utility class for calculating transition probabilities based on biological parameters.
    
    Implements patterns from tumor-tcell repository including:
    - Time-dependent exponential decay probabilities
    - Poisson process event probabilities
    - Threshold-based sigmoid transitions
    - Stochastic noise addition
    """
    
    def __init__(self):
        self.random_state = random.Random()
    
    def set_seed(self, seed: int):
        """Set random seed for reproducible results"""
        self.random_state.seed(seed)
        np.random.seed(seed)
    
    def calculate_timestep_probability(self, probability_parameter: float, 
                                     timescale: float, timestep: float) -> float:
        """
        Calculate transition probability as function of time.
        Based on tumor-tcell repository pattern: get_probability_timestep()
        
        Args:
            probability_parameter: Base probability over timescale
            timescale: Reference time period (seconds)
            timestep: Current timestep (seconds)
        
        Returns:
            Probability for current timestep
        """
        if probability_parameter <= 0:
            return 0.0
        
        if probability_parameter >= 1.0:
            probability_parameter = 0.999  # Avoid log(0)
        
        rate = -math.log(1 - probability_parameter)
        timestep_fraction = timestep / timescale
        return 1 - math.exp(-rate * timestep_fraction)
    
    def calculate_poisson_probability(self, interval_duration: float, 
                                    expected_time: float) -> float:
        """
        Calculate probability of event occurring within time interval.
        Based on tumor-tcell repository pattern: probability_of_occurrence_within_interval()
        
        Assumes Poisson process where event is expected once every expected_time.
        
        Args:
            interval_duration: Duration of time interval
            expected_time: Expected time between occurrences
        
        Returns:
            Probability of at least one occurrence
        """
        if expected_time <= 0:
            return 1.0
        
        lambda_rate = interval_duration / expected_time
        P_0 = math.exp(-lambda_rate)  # Probability of zero occurrences
        return 1 - P_0  # Probability of at least one occurrence
    
    def calculate_threshold_probability(self, current_value: float, threshold: float,
                                      steepness: float = 1.0, 
                                      baseline: float = 0.0) -> float:
        """
        Calculate sigmoid probability based on threshold crossing.
        
        Args:
            current_value: Current value to compare
            threshold: Threshold value
            steepness: Steepness of sigmoid transition
            baseline: Baseline probability
        
        Returns:
            Sigmoid probability between baseline and 1.0
        """
        if threshold <= 0:
            return 1.0 if current_value > 0 else baseline
        
        # Sigmoid function: P = baseline + (1-baseline) / (1 + exp(-steepness * (x - threshold)))
        x_normalized = (current_value - threshold) / threshold
        sigmoid_value = 1.0 / (1.0 + math.exp(-steepness * x_normalized))
        return baseline + (1.0 - baseline) * sigmoid_value
    
    def calculate_concentration_dependent_probability(self, concentration: float,
                                                    kd: float, hill_coefficient: float = 1.0,
                                                    max_probability: float = 1.0) -> float:
        """
        Calculate probability based on molecular concentration using Hill equation.
        
        Args:
            concentration: Current molecular concentration
            kd: Dissociation constant (half-maximum concentration)
            hill_coefficient: Hill coefficient for cooperativity
            max_probability: Maximum probability at saturation
        
        Returns:
            Concentration-dependent probability
        """
        if concentration <= 0:
            return 0.0
        
        if kd <= 0:
            return max_probability
        
        # Hill equation: P = P_max * [C]^n / (Kd^n + [C]^n)
        conc_power = math.pow(concentration, hill_coefficient)
        kd_power = math.pow(kd, hill_coefficient)
        
        return max_probability * conc_power / (kd_power + conc_power)
    
    def add_stochastic_noise(self, base_probability: float, 
                           noise_level: float = 0.1) -> float:
        """
        Add stochastic noise to probability calculation.
        
        Args:
            base_probability: Base probability without noise
            noise_level: Standard deviation of Gaussian noise
        
        Returns:
            Probability with added noise, clamped to [0, 1]
        """
        if noise_level <= 0:
            return base_probability
        
        noise = self.random_state.gauss(0, noise_level)
        noisy_probability = base_probability + noise
        
        # Clamp to valid probability range
        return max(0.0, min(1.0, noisy_probability))
    
    def calculate_temperature_dependent_probability(self, base_probability: float,
                                                  temperature_factor: float,
                                                  activation_energy: float = 1.0) -> float:
        """
        Calculate temperature-dependent probability using Arrhenius-like equation.
        
        Args:
            base_probability: Base probability at reference temperature
            temperature_factor: Relative temperature (1.0 = reference)
            activation_energy: Activation energy parameter
        
        Returns:
            Temperature-adjusted probability
        """
        if temperature_factor <= 0:
            return 0.0
        
        # Arrhenius-like: P = P_base * exp(-E_a * (1/T - 1/T_ref))
        temperature_adjustment = math.exp(-activation_energy * (1.0/temperature_factor - 1.0))
        adjusted_probability = base_probability * temperature_adjustment
        
        return max(0.0, min(1.0, adjusted_probability))


class TransitionFunction(ABC):
    """Abstract base class for transition probability functions"""
    
    @abstractmethod
    def calculate_probability(self, context: Dict[str, Any]) -> float:
        """Calculate transition probability given current context"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get function parameters"""
        pass


class ExponentialTransition(TransitionFunction):
    """
    Exponential decay transition function.
    Based on tumor-tcell patterns for growth, division, and death rates.
    """
    
    def __init__(self, rate: float, timescale: float, 
                 biological_context: str = ""):
        self.rate = rate
        self.timescale = timescale
        self.biological_context = biological_context
        self.calculator = ProbabilityCalculator()
    
    def calculate_probability(self, context: Dict[str, Any]) -> float:
        """Calculate exponential transition probability"""
        timestep = context.get('timestep', 1.0)
        return self.calculator.calculate_timestep_probability(
            self.rate, self.timescale, timestep
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'type': 'exponential',
            'rate': self.rate,
            'timescale': self.timescale,
            'biological_context': self.biological_context
        }


class ThresholdTransition(TransitionFunction):
    """
    Threshold-based transition function.
    Based on tumor-tcell patterns for IFN-γ and molecular thresholds.
    """
    
    def __init__(self, parameter_name: str, threshold: float,
                 steepness: float = 1.0, baseline: float = 0.0,
                 biological_context: str = ""):
        self.parameter_name = parameter_name
        self.threshold = threshold
        self.steepness = steepness
        self.baseline = baseline
        self.biological_context = biological_context
        self.calculator = ProbabilityCalculator()
    
    def calculate_probability(self, context: Dict[str, Any]) -> float:
        """Calculate threshold-based transition probability"""
        current_value = context.get(self.parameter_name, 0)
        return self.calculator.calculate_threshold_probability(
            current_value, self.threshold, self.steepness, self.baseline
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'type': 'threshold',
            'parameter': self.parameter_name,
            'threshold': self.threshold,
            'steepness': self.steepness,
            'baseline': self.baseline,
            'biological_context': self.biological_context
        }


class MolecularTransition(TransitionFunction):
    """
    Molecular concentration-dependent transition function.
    Based on tumor-tcell patterns for ligand-receptor interactions.
    """
    
    def __init__(self, molecule_name: str, kd: float, 
                 hill_coefficient: float = 1.0, max_probability: float = 1.0,
                 biological_context: str = ""):
        self.molecule_name = molecule_name
        self.kd = kd
        self.hill_coefficient = hill_coefficient
        self.max_probability = max_probability
        self.biological_context = biological_context
        self.calculator = ProbabilityCalculator()
    
    def calculate_probability(self, context: Dict[str, Any]) -> float:
        """Calculate molecular concentration-dependent probability"""
        concentration = context.get(self.molecule_name, 0)
        return self.calculator.calculate_concentration_dependent_probability(
            concentration, self.kd, self.hill_coefficient, self.max_probability
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'type': 'molecular',
            'molecule': self.molecule_name,
            'kd': self.kd,
            'hill_coefficient': self.hill_coefficient,
            'max_probability': self.max_probability,
            'biological_context': self.biological_context
        }


class CompositeTransition(TransitionFunction):
    """
    Composite transition combining multiple transition functions.
    Allows complex biological logic like AND/OR conditions.
    """
    
    def __init__(self, transitions: List[TransitionFunction], 
                 combination_type: str = "AND",
                 biological_context: str = ""):
        self.transitions = transitions
        self.combination_type = combination_type.upper()
        self.biological_context = biological_context
        
        if self.combination_type not in ["AND", "OR", "PRODUCT", "MAX", "MIN"]:
            raise ValueError(f"Unknown combination type: {combination_type}")
    
    def calculate_probability(self, context: Dict[str, Any]) -> float:
        """Calculate composite transition probability"""
        if not self.transitions:
            return 0.0
        
        probabilities = [t.calculate_probability(context) for t in self.transitions]
        
        if self.combination_type == "AND":
            # All conditions must be met
            return min(probabilities)
        
        elif self.combination_type == "OR":
            # At least one condition must be met
            return max(probabilities)
        
        elif self.combination_type == "PRODUCT":
            # Independent probabilities multiplied
            result = 1.0
            for p in probabilities:
                result *= p
            return result
        
        elif self.combination_type == "MAX":
            return max(probabilities)
        
        elif self.combination_type == "MIN":
            return min(probabilities)
        
        return 0.0
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            'type': 'composite',
            'combination_type': self.combination_type,
            'transitions': [t.get_parameters() for t in self.transitions],
            'biological_context': self.biological_context
        }


class BiologicalTransitionLibrary:
    """
    Library of common biological transition functions based on tumor-tcell patterns.
    """
    
    @staticmethod
    def tumor_growth_transition(growth_rate: float = 0.6) -> ExponentialTransition:
        """Tumor cell growth/division transition"""
        return ExponentialTransition(
            rate=growth_rate,
            timescale=86400,  # 24 hours
            biological_context="Tumor cell division probability over 24 hours"
        )
    
    @staticmethod
    def tumor_death_transition(death_rate: float = 0.5) -> ExponentialTransition:
        """Tumor cell apoptotic death transition"""
        return ExponentialTransition(
            rate=death_rate,
            timescale=432000,  # 5 days
            biological_context="Background apoptosis rate over 5 days"
        )
    
    @staticmethod
    def ifng_state_transition(threshold: float = 15000) -> ThresholdTransition:
        """IFN-γ induced PDL1n to PDL1p transition"""
        return ThresholdTransition(
            parameter_name='IFNg_internal',
            threshold=threshold,
            steepness=2.0,
            baseline=0.01,
            biological_context="IFN-gamma threshold for PDL1 expression induction"
        )
    
    @staticmethod
    def tcell_exhaustion_transition(refractory_threshold: int = 3) -> ThresholdTransition:
        """T cell exhaustion transition based on refractory count"""
        return ThresholdTransition(
            parameter_name='refractory_count',
            threshold=refractory_threshold,
            steepness=3.0,
            baseline=0.0,
            biological_context="T cell exhaustion from repeated activation cycles"
        )
    
    @staticmethod
    def tcell_activation_transition(activation_time: float = 21600) -> ExponentialTransition:
        """T cell activation transition"""
        return ExponentialTransition(
            rate=0.8,
            timescale=activation_time,
            biological_context="T cell activation probability over 6 hours"
        )
    
    @staticmethod
    def dendritic_activation_transition(debris_threshold: float = 1e7) -> ThresholdTransition:
        """Dendritic cell activation by tumor debris"""
        return ThresholdTransition(
            parameter_name='internal_tumor_debris',
            threshold=debris_threshold,
            steepness=1.5,
            baseline=0.0,
            biological_context="DAMP recognition threshold for dendritic cell maturation"
        )
    
    @staticmethod
    def cytotoxic_killing_transition(packet_threshold: float = 12800) -> ThresholdTransition:
        """Cytotoxic T cell killing transition"""
        return ThresholdTransition(
            parameter_name='cytotoxic_packets',
            threshold=packet_threshold,
            steepness=2.0,
            baseline=0.0,
            biological_context="Cytotoxic packet threshold for tumor cell death"
        )
    
    @staticmethod
    def pdl1_immune_suppression_transition(pdl1_threshold: float = 1e4) -> MolecularTransition:
        """PDL1-mediated immune suppression transition"""
        return MolecularTransition(
            molecule_name='PDL1',
            kd=pdl1_threshold,
            hill_coefficient=2.0,
            max_probability=0.95,
            biological_context="PDL1-PD1 interaction for T cell suppression"
        )


def create_transition_function(transition_type: str, **kwargs) -> TransitionFunction:
    """
    Factory function to create transition functions.
    
    Args:
        transition_type: Type of transition ('exponential', 'threshold', 'molecular', 'composite')
        **kwargs: Parameters specific to transition type
    
    Returns:
        Appropriate TransitionFunction instance
    """
    if transition_type == 'exponential':
        return ExponentialTransition(
            rate=kwargs.get('rate', 0.5),
            timescale=kwargs.get('timescale', 86400),
            biological_context=kwargs.get('biological_context', '')
        )
    
    elif transition_type == 'threshold':
        return ThresholdTransition(
            parameter_name=kwargs.get('parameter_name', 'value'),
            threshold=kwargs.get('threshold', 1.0),
            steepness=kwargs.get('steepness', 1.0),
            baseline=kwargs.get('baseline', 0.0),
            biological_context=kwargs.get('biological_context', '')
        )
    
    elif transition_type == 'molecular':
        return MolecularTransition(
            molecule_name=kwargs.get('molecule_name', 'molecule'),
            kd=kwargs.get('kd', 1.0),
            hill_coefficient=kwargs.get('hill_coefficient', 1.0),
            max_probability=kwargs.get('max_probability', 1.0),
            biological_context=kwargs.get('biological_context', '')
        )
    
    elif transition_type == 'composite':
        return CompositeTransition(
            transitions=kwargs.get('transitions', []),
            combination_type=kwargs.get('combination_type', 'AND'),
            biological_context=kwargs.get('biological_context', '')
        )
    
    else:
        raise ValueError(f"Unknown transition type: {transition_type}")


def analyze_transition_statistics(transition_func: TransitionFunction,
                                context_variations: List[Dict[str, Any]],
                                num_samples: int = 1000) -> Dict[str, Any]:
    """
    Analyze statistical properties of a transition function.
    
    Args:
        transition_func: Transition function to analyze
        context_variations: List of context variations to test
        num_samples: Number of samples for statistical analysis
    
    Returns:
        Dictionary containing statistical analysis results
    """
    results = {
        'mean_probability': [],
        'std_probability': [],
        'min_probability': [],
        'max_probability': [],
        'context_variations': context_variations
    }
    
    for context in context_variations:
        probabilities = []
        
        for _ in range(num_samples):
            prob = transition_func.calculate_probability(context)
            probabilities.append(prob)
        
        results['mean_probability'].append(np.mean(probabilities))
        results['std_probability'].append(np.std(probabilities))
        results['min_probability'].append(np.min(probabilities))
        results['max_probability'].append(np.max(probabilities))
    
    return results


# Example usage and testing
if __name__ == '__main__':
    # Test probability calculator
    calc = ProbabilityCalculator()
    
    # Test exponential probability (tumor growth)
    growth_prob = calc.calculate_timestep_probability(0.6, 86400, 3600)  # 1 hour timestep
    print(f"Tumor growth probability (1h): {growth_prob:.6f}")
    
    # Test Poisson probability (random events)
    poisson_prob = calc.calculate_poisson_probability(3600, 86400)  # 1 hour interval, 1 day expected
    print(f"Poisson event probability: {poisson_prob:.6f}")
    
    # Test threshold probability (IFN-gamma response)
    threshold_prob = calc.calculate_threshold_probability(20000, 15000, 2.0)
    print(f"IFN-gamma threshold probability: {threshold_prob:.6f}")
    
    # Test biological transition library
    tumor_growth = BiologicalTransitionLibrary.tumor_growth_transition()
    ifng_transition = BiologicalTransitionLibrary.ifng_state_transition()
    
    context = {
        'timestep': 3600,
        'IFNg_internal': 20000
    }
    
    growth_prob = tumor_growth.calculate_probability(context)
    ifng_prob = ifng_transition.calculate_probability(context)
    
    print(f"Tumor growth transition probability: {growth_prob:.6f}")
    print(f"IFN-gamma state transition probability: {ifng_prob:.6f}")
    
    # Test composite transition
    composite = CompositeTransition(
        [tumor_growth, ifng_transition],
        combination_type="PRODUCT",
        biological_context="Combined growth and state transition"
    )
    
    composite_prob = composite.calculate_probability(context)
    print(f"Composite transition probability: {composite_prob:.6f}")
    
    print("Probability transitions template created successfully!")
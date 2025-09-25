# 5.4 State Machine Generation Templates

This directory contains templates for state transition logic based on tumor-tcell repository patterns.

## Templates Overview

### 1. `state_machine_base.py` - Abstract base classes for state machine implementation
### 2. `cell_state_transitions.py` - Specific cell state transition patterns  
### 3. `probability_transitions.py` - Probability-based transition logic
### 4. `state_behaviors.py` - State-dependent behavior templates
### 5. `transition_validation.py` - State transition validation and testing

## Usage

These templates provide standardized patterns for:
- Defining cell states and valid transitions
- Implementing probability-based state changes
- Managing state-dependent behaviors and molecular interactions
- Validating state transition logic

## Biological Context

Based on state machine patterns from tumor-tcell repository:
- **Tumor cells**: PDL1n (proliferative) ↔ PDL1p (immune-suppressive)
- **T cells**: PD1n (active) → PD1p (exhausted), activation/refractory cycles
- **Dendritic cells**: inactive (surveillance) → active (antigen presenting)
- **State-dependent behaviors**: molecular production, migration, death rates

## State Transition Patterns

### Tumor Cell States
- **PDL1n**: Proliferative state with growth capability
- **PDL1p**: Immune-suppressive state with PDL1 expression
- **Transitions**: IFN-γ threshold triggers PDL1n → PDL1p

### T Cell States  
- **PD1n**: Active, non-exhausted state
- **PD1p**: Exhausted state with reduced function
- **Activation cycles**: TCR engagement → activation → refractory → recovery
- **Transitions**: Repeated activation → exhaustion

### Dendritic Cell States
- **inactive**: Surveillance state with low migration
- **active**: Matured state with high migration and antigen presentation
- **Transitions**: Tumor debris threshold triggers activation
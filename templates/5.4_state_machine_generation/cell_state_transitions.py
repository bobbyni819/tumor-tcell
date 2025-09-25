"""
Cell State Transitions Template
==============================

Specific cell state transition patterns based on tumor-tcell repository.

This template provides:
- Concrete state machine implementations for different cell types
- Biologically accurate state definitions and transitions
- Parameter-driven transition logic

Usage:
    from cell_state_transitions import TumorCellStateMachine, TCellStateMachine
    
    tumor_sm = TumorCellStateMachine()
    update = tumor_sm.update(timestep, context)
"""

from typing import Dict, Any, List
import random
import math

from .state_machine_base import (
    StateMachine, State, Transition, StateMetadata, TransitionMetadata,
    TransitionCondition, get_probability_timestep, probability_of_occurrence_within_interval,
    create_threshold_condition, create_probability_condition, create_timer_condition
)


class TumorCellStateMachine(StateMachine):
    """
    State machine for tumor cells based on tumor-tcell repository patterns.
    
    States:
    - PDL1n: Proliferative state with growth capability
    - PDL1p: Immune-suppressive state with PDL1 expression
    
    Key transitions:
    - PDL1n → PDL1p: Triggered by IFN-γ threshold
    - Death transitions: Apoptosis or T cell-mediated killing
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        self.parameters = parameters or self._get_default_parameters()
        super().__init__(initial_state='PDL1n')
    
    def _get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for tumor cell state machine"""
        return {
            'initial_PDL1n': 0.9,
            'PDL1n_growth': 0.6,
            'death_apoptosis': 0.5,
            'IFNg_threshold': 15000,
            'cytotoxic_packet_threshold': 12800,
            'PDL1p_PDL1_equilibrium': 5e4,
            'PDL1p_MHCI_equilibrium': 5e4,
            'tumor_debris_amount': 1.4e15,
            'Max_IFNg_internalization': 31/60,
            'reduction_IFNg_internalization': 2
        }
    
    def _define_states(self):
        """Define tumor cell states"""
        
        # PDL1n state - proliferative
        pdl1n_metadata = StateMetadata(
            name='PDL1n',
            description='Proliferative tumor cell state',
            biological_context='PDL1-negative cells maintain growth capability and are susceptible to immune attack',
            behaviors={
                'growth': True,
                'immune_suppression': False,
                'ifng_response': True
            },
            molecular_production={
                'PDL1': 0.0,
                'MHCI': 1e4  # Baseline MHCI expression
            },
            migration_properties={
                'velocity': 0.0  # Tumor cells are typically non-motile
            },
            death_rates={
                'apoptosis': self.parameters['death_apoptosis'],
                'cytotoxic': 1.0  # Susceptible to T cell killing
            },
            division_rates={
                'growth': self.parameters['PDL1n_growth']
            }
        )
        
        pdl1n_state = State('PDL1n', pdl1n_metadata)
        
        # Add PDL1n-specific behaviors
        def pdl1n_entry_action(context):
            context['growth_capable'] = True
            context['immune_vulnerable'] = True
        
        def pdl1n_growth_behavior(context):
            """Handle growth/division for PDL1n cells"""
            timestep = context.get('timestep', 1.0)
            prob_divide = get_probability_timestep(
                self.parameters['PDL1n_growth'],
                86400,  # 24 hours
                timestep
            )
            
            if random.random() < prob_divide:
                return {'globals': {'divide': True, 'PDL1n_divide_count': 1}}
            return {}
        
        pdl1n_state.add_entry_action(pdl1n_entry_action)
        pdl1n_state.add_behavior('growth', pdl1n_growth_behavior)
        
        self.add_state(pdl1n_state)
        
        # PDL1p state - immune-suppressive
        pdl1p_metadata = StateMetadata(
            name='PDL1p',
            description='Immune-suppressive tumor cell state',
            biological_context='PDL1-positive cells express immune checkpoint molecules to evade T cell attack',
            behaviors={
                'growth': False,
                'immune_suppression': True,
                'ifng_response': False
            },
            molecular_production={
                'PDL1': self.parameters['PDL1p_PDL1_equilibrium'],
                'MHCI': self.parameters['PDL1p_MHCI_equilibrium'],
                'IFNg_internalization': self.parameters['Max_IFNg_internalization'] / 
                                       self.parameters['reduction_IFNg_internalization']
            },
            migration_properties={
                'velocity': 0.0
            },
            death_rates={
                'apoptosis': self.parameters['death_apoptosis'],
                'cytotoxic': 0.3  # Reduced susceptibility to T cell killing
            },
            division_rates={
                'growth': 0.0  # No growth in PDL1p state
            }
        )
        
        pdl1p_state = State('PDL1p', pdl1p_metadata)
        
        # Add PDL1p-specific behaviors
        def pdl1p_entry_action(context):
            context['growth_capable'] = False
            context['immune_vulnerable'] = False
            context['PDL1_expressing'] = True
        
        def pdl1p_immune_suppression_behavior(context):
            """Handle immune suppression for PDL1p cells"""
            return {
                'neighbors': {
                    'present': {
                        'PDL1': self.parameters['PDL1p_PDL1_equilibrium'],
                        'MHCI': self.parameters['PDL1p_MHCI_equilibrium']
                    }
                }
            }
        
        pdl1p_state.add_entry_action(pdl1p_entry_action)
        pdl1p_state.add_behavior('immune_suppression', pdl1p_immune_suppression_behavior)
        
        self.add_state(pdl1p_state)
    
    def _define_transitions(self):
        """Define tumor cell state transitions"""
        
        # PDL1n → PDL1p transition (IFN-γ induced)
        ifng_condition = create_threshold_condition(
            'IFNg_internal', '>=', self.parameters['IFNg_threshold'],
            'IFN-gamma threshold for immune-mediated state transition'
        )
        
        pdl1n_to_pdl1p = TransitionMetadata(
            from_state='PDL1n',
            to_state='PDL1p',
            conditions=[ifng_condition],
            biological_context='IFN-γ stimulation induces PDL1 expression for immune evasion'
        )
        
        self.add_transition(Transition(pdl1n_to_pdl1p))
        
        # Death transitions for both states
        for state in ['PDL1n', 'PDL1p']:
            # Apoptotic death
            apoptosis_condition = TransitionCondition(
                condition_type='probability',
                parameter='death_probability',
                operator='<',
                threshold=lambda ctx: get_probability_timestep(
                    self.parameters['death_apoptosis'],
                    432000,  # 5 days
                    ctx.get('timestep', 1.0)
                ),
                biological_context='Background apoptosis from metabolic stress'
            )
            
            # Cytotoxic death (more likely for PDL1n)
            cytotoxic_threshold = self.parameters['cytotoxic_packet_threshold']
            if state == 'PDL1p':
                cytotoxic_threshold *= 2  # PDL1p cells are more resistant
            
            cytotoxic_condition = create_threshold_condition(
                'cytotoxic_packets', '>=', cytotoxic_threshold,
                'T cell-mediated cytotoxic killing threshold'
            )
            
            # Note: Death transitions would lead to cell removal, not another state
            # This is typically handled by the removal process in vivarium
    
    def update(self, timestep: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update tumor cell state machine.
        
        Args:
            timestep: Time step size
            context: Current cell state including internal and boundary variables
        
        Returns:
            Dictionary of updates to apply
        """
        # Add timestep to context
        context['timestep'] = timestep
        
        # Extract relevant state variables
        internal_ifng = context.get('internal', {}).get('IFNg', 0)
        cytotoxic_packets = context.get('neighbors', {}).get('receive', {}).get('cytotoxic_packets', 0)
        
        # Add to context for transition evaluation
        context['IFNg_internal'] = internal_ifng
        context['cytotoxic_packets'] = cytotoxic_packets
        
        # Check for death conditions first
        death_update = self._check_death_conditions(context)
        if death_update:
            return death_update
        
        # Run state machine update
        update = super().update(timestep, context)
        
        # Add state-specific behaviors
        current_state = self.get_current_state()
        
        if current_state.name == 'PDL1n':
            growth_update = current_state.execute_behavior('growth', context)
            if growth_update:
                update.update(growth_update)
        
        elif current_state.name == 'PDL1p':
            immune_update = current_state.execute_behavior('immune_suppression', context)
            if immune_update:
                if 'neighbors' not in update:
                    update['neighbors'] = {}
                update['neighbors'].update(immune_update['neighbors'])
        
        return update
    
    def _check_death_conditions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for death conditions and return death update if triggered"""
        timestep = context.get('timestep', 1.0)
        
        # Check apoptotic death
        prob_death = get_probability_timestep(
            self.parameters['death_apoptosis'],
            432000,  # 5 days
            timestep
        )
        
        if random.random() < prob_death:
            return {
                'boundary': {
                    'exchange': {'tumor_debris': int(self.parameters['tumor_debris_amount'])}
                },
                'globals': {'death': 'apoptosis'}
            }
        
        # Check cytotoxic death
        cytotoxic_packets = context.get('cytotoxic_packets', 0)
        threshold = self.parameters['cytotoxic_packet_threshold']
        
        # PDL1p cells are more resistant
        if self.current_state == 'PDL1p':
            threshold *= 2
        
        if cytotoxic_packets >= threshold:
            return {
                'boundary': {
                    'exchange': {'tumor_debris': int(self.parameters['tumor_debris_amount'])}
                },
                'globals': {'death': 'Tcell_death'}
            }
        
        return {}


class TCellStateMachine(StateMachine):
    """
    State machine for T cells based on tumor-tcell repository patterns.
    
    States:
    - PD1n: Active, non-exhausted state with full cytotoxic function
    - PD1p: Exhausted state with reduced function
    - delay: Temporary delay state (for lymph node T cells)
    
    Key transitions:
    - PD1n → PD1p: Triggered by repeated activation or high division count
    - Activation cycles: TCR engagement → activation → refractory → recovery
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        self.parameters = parameters or self._get_default_parameters()
        super().__init__(initial_state='PD1n')
    
    def _get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for T cell state machine"""
        return {
            'initial_PD1n': 0.8,
            'activation_time': 21600,  # 6 hours
            'activation_refractory_time': 43200,  # 12 hours
            'refractory_count_threshold': 3,
            'PD1n_divide_threshold': 5,
            'PD1n_growth_28hr': 0.3,
            'PD1p_growth_28hr': 0.1,
            'death_PD1p_14hr': 0.35,
            'death_PD1p_next_to_PDL1p_14hr': 0.5,
            'PDL1_critical_number': 1e4,
            'IFNg_production_PD1n': 2.78e-4,
            'cytotoxic_packet_production': 0.5,
            'PD1n_migration': 10.0,
            'PD1p_migration': 5.0,
            'TCR_downregulated': 0,
            'TCR_upregulated': 50000,
            'ligand_threshold': 1000
        }
    
    def _define_states(self):
        """Define T cell states"""
        
        # PD1n state - active, non-exhausted
        pd1n_metadata = StateMetadata(
            name='PD1n',
            description='Active, non-exhausted T cell state',
            biological_context='Functional T cells with full cytotoxic and cytokine production capability',
            behaviors={
                'cytotoxic_function': True,
                'cytokine_production': True,
                'proliferation': True,
                'migration': True
            },
            molecular_production={
                'IFNg': self.parameters['IFNg_production_PD1n'],
                'cytotoxic_packets': self.parameters['cytotoxic_packet_production'],
                'TCR': self.parameters['TCR_upregulated']
            },
            migration_properties={
                'velocity': self.parameters['PD1n_migration']
            },
            death_rates={
                'apoptosis': 0.1  # Low death rate for active T cells
            },
            division_rates={
                'growth': self.parameters['PD1n_growth_28hr']
            }
        )
        
        pd1n_state = State('PD1n', pd1n_metadata)
        
        # PD1n behaviors
        def pd1n_cytotoxic_behavior(context):
            """Handle cytotoxic function for PD1n T cells"""
            if context.get('MHCI', 0) > self.parameters['ligand_threshold']:
                return {
                    'neighbors': {
                        'transfer': {
                            'cytotoxic_packets': self.parameters['cytotoxic_packet_production']
                        }
                    }
                }
            return {}
        
        def pd1n_cytokine_behavior(context):
            """Handle cytokine production for PD1n T cells"""
            timestep = context.get('timestep', 1.0)
            ifng_amount = self.parameters['IFNg_production_PD1n'] * timestep
            
            return {
                'boundary': {
                    'exchange': {'IFNg': ifng_amount}
                }
            }
        
        pd1n_state.add_behavior('cytotoxic', pd1n_cytotoxic_behavior)
        pd1n_state.add_behavior('cytokine', pd1n_cytokine_behavior)
        
        self.add_state(pd1n_state)
        
        # PD1p state - exhausted
        pd1p_metadata = StateMetadata(
            name='PD1p',
            description='Exhausted T cell state',
            biological_context='Dysfunctional T cells with reduced cytotoxic and cytokine production',
            behaviors={
                'cytotoxic_function': False,
                'cytokine_production': False,
                'proliferation': True,  # Can still divide but at reduced rate
                'migration': True
            },
            molecular_production={
                'IFNg': self.parameters['IFNg_production_PD1n'] * 0.1,  # Reduced production
                'cytotoxic_packets': 0,  # No cytotoxic function
                'TCR': self.parameters['TCR_upregulated'] * 0.5  # Reduced TCR expression
            },
            migration_properties={
                'velocity': self.parameters['PD1p_migration']
            },
            death_rates={
                'apoptosis': self.parameters['death_PD1p_14hr']
            },
            division_rates={
                'growth': self.parameters['PD1p_growth_28hr']
            }
        )
        
        pd1p_state = State('PD1p', pd1p_metadata)
        self.add_state(pd1p_state)
        
        # Delay state (for lymph node T cells)
        delay_metadata = StateMetadata(
            name='delay',
            description='Temporary delay state',
            biological_context='T cells in lymph nodes with delayed activation',
            behaviors={
                'cytotoxic_function': False,
                'cytokine_production': False,
                'proliferation': True,
                'migration': False
            },
            molecular_production={},
            migration_properties={'velocity': 0.0},
            death_rates={'apoptosis': 0.05},
            division_rates={'growth': 0.2}
        )
        
        delay_state = State('delay', delay_metadata)
        self.add_state(delay_state)
    
    def _define_transitions(self):
        """Define T cell state transitions"""
        
        # PD1n → PD1p transition (exhaustion)
        exhaustion_conditions = [
            create_threshold_condition(
                'refractory_count', '>', self.parameters['refractory_count_threshold'],
                'T cell exhaustion from repeated activation cycles'
            )
        ]
        
        # Alternative exhaustion trigger: too many divisions
        division_condition = create_threshold_condition(
            'PD1n_divide_counts', '>', self.parameters['PD1n_divide_threshold'],
            'T cell exhaustion from excessive proliferation'
        )
        
        exhaustion_transition = TransitionMetadata(
            from_state='PD1n',
            to_state='PD1p',
            conditions=exhaustion_conditions,  # Could also check division_condition
            biological_context='Transition to exhausted state due to chronic stimulation'
        )
        
        self.add_transition(Transition(exhaustion_transition))
        
        # delay → PD1n transition (lymph node activation)
        delay_to_active = TransitionMetadata(
            from_state='delay',
            to_state='PD1n',
            conditions=[
                create_probability_condition(0.1, 'Probability of lymph node T cell activation')
            ],
            biological_context='Lymph node T cells become activated and migrate to tumor'
        )
        
        self.add_transition(Transition(delay_to_active))
    
    def update(self, timestep: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update T cell state machine"""
        context['timestep'] = timestep
        
        # Extract relevant variables
        refractory_count = context.get('internal', {}).get('refractory_count', 0)
        divide_counts = context.get('internal', {}).get('PD1n_divide_counts', 0)
        tcr_timer = context.get('internal', {}).get('TCR_timer', 0)
        mhci = context.get('neighbors', {}).get('accept', {}).get('MHCI', 0)
        pdl1 = context.get('neighbors', {}).get('accept', {}).get('PDL1', 0)
        
        # Add to context for transitions
        context['refractory_count'] = refractory_count
        context['PD1n_divide_counts'] = divide_counts
        context['MHCI'] = mhci
        context['PDL1'] = pdl1
        
        # Check for death conditions
        death_update = self._check_death_conditions(context)
        if death_update:
            return death_update
        
        # Handle TCR regulation
        tcr_update = self._handle_tcr_regulation(context)
        
        # Run state machine update
        update = super().update(timestep, context)
        
        # Merge TCR regulation update
        if tcr_update:
            if 'internal' not in update:
                update['internal'] = {}
            if 'neighbors' not in update:
                update['neighbors'] = {'present': {}}
            
            update['internal'].update(tcr_update.get('internal', {}))
            update['neighbors']['present'].update(tcr_update.get('neighbors', {}).get('present', {}))
        
        # Add state-specific behaviors
        current_state = self.get_current_state()
        
        if current_state.name == 'PD1n':
            cytotoxic_update = current_state.execute_behavior('cytotoxic', context)
            cytokine_update = current_state.execute_behavior('cytokine', context)
            
            if cytotoxic_update:
                if 'neighbors' not in update:
                    update['neighbors'] = {}
                update['neighbors'].update(cytotoxic_update['neighbors'])
            
            if cytokine_update:
                if 'boundary' not in update:
                    update['boundary'] = {}
                update['boundary'].update(cytokine_update['boundary'])
        
        return update
    
    def _handle_tcr_regulation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TCR down-regulation and up-regulation cycles"""
        tcr_timer = context.get('internal', {}).get('TCR_timer', 0)
        mhci = context.get('MHCI', 0)
        timestep = context.get('timestep', 1.0)
        
        update = {'internal': {}, 'neighbors': {'present': {}}}
        
        # TCR down-regulation after activation
        if tcr_timer > self.parameters['activation_time']:
            update['neighbors']['present']['TCR'] = self.parameters['TCR_downregulated']
        
        # Update TCR timer
        if mhci > self.parameters['ligand_threshold'] or tcr_timer > self.parameters['activation_time']:
            update['internal']['TCR_timer'] = timestep
        
        # TCR up-regulation after refractory period
        if tcr_timer > self.parameters['activation_refractory_time']:
            update['neighbors']['present']['TCR'] = self.parameters['TCR_upregulated']
            update['internal']['TCR_timer'] = -self.parameters['activation_refractory_time']
            update['internal']['refractory_count'] = 1
        
        return update
    
    def _check_death_conditions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check T cell death conditions"""
        if self.current_state == 'PD1p':
            timestep = context.get('timestep', 1.0)
            pdl1 = context.get('PDL1', 0)
            
            # Higher death rate when next to PDL1+ cells
            death_rate = (self.parameters['death_PD1p_next_to_PDL1p_14hr'] 
                         if pdl1 >= self.parameters['PDL1_critical_number']
                         else self.parameters['death_PD1p_14hr'])
            
            prob_death = get_probability_timestep(death_rate, 50400, timestep)  # 14 hours
            
            if random.random() < prob_death:
                death_type = 'PD1p_PDL1_death' if pdl1 >= self.parameters['PDL1_critical_number'] else 'PD1p_apoptosis'
                return {'globals': {'death': death_type}}
        
        return {}


class DendriticCellStateMachine(StateMachine):
    """
    State machine for dendritic cells based on tumor-tcell repository patterns.
    
    States:
    - inactive: Surveillance state with low migration
    - active: Matured state with high migration and antigen presentation
    
    Key transitions:
    - inactive → active: Triggered by tumor debris threshold (DAMP recognition)
    """
    
    def __init__(self, parameters: Dict[str, Any] = None):
        self.parameters = parameters or self._get_default_parameters()
        super().__init__(initial_state='inactive')
    
    def _get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for dendritic cell state machine"""
        return {
            'internal_tumor_debris_threshold': 1e7,
            'death_apoptosis': 0.5,
            'divide_prob': 0.2,
            'velocity_inactive': 3.0,
            'velocity_active': 12.5,
            'tumor_debris_uptake': 1000,
            'PDL1p_PDL1_equilibrium': 5e4,
            'PDL1p_MHCI_equilibrium': 5e4
        }
    
    def _define_states(self):
        """Define dendritic cell states"""
        
        # Inactive state - surveillance
        inactive_metadata = StateMetadata(
            name='inactive',
            description='Surveillance dendritic cell state',
            biological_context='Immature DCs patrol tissue for antigen capture',
            behaviors={
                'antigen_capture': True,
                'antigen_presentation': False,
                'migration_lymph_node': False
            },
            molecular_production={},
            migration_properties={
                'velocity': self.parameters['velocity_inactive']
            },
            death_rates={
                'apoptosis': self.parameters['death_apoptosis']
            },
            division_rates={
                'growth': 0.0  # No division in inactive state
            }
        )
        
        inactive_state = State('inactive', inactive_metadata)
        self.add_state(inactive_state)
        
        # Active state - mature/activated
        active_metadata = StateMetadata(
            name='active',
            description='Mature dendritic cell state',
            biological_context='Mature DCs present antigens and migrate to lymph nodes',
            behaviors={
                'antigen_capture': False,
                'antigen_presentation': True,
                'migration_lymph_node': True
            },
            molecular_production={
                'PDL1': self.parameters['PDL1p_PDL1_equilibrium'],
                'MHCI': self.parameters['PDL1p_MHCI_equilibrium']
            },
            migration_properties={
                'velocity': self.parameters['velocity_active']
            },
            death_rates={
                'apoptosis': self.parameters['death_apoptosis']
            },
            division_rates={
                'growth': self.parameters['divide_prob']
            }
        )
        
        active_state = State('active', active_metadata)
        self.add_state(active_state)
    
    def _define_transitions(self):
        """Define dendritic cell state transitions"""
        
        # inactive → active transition (maturation)
        maturation_condition = create_threshold_condition(
            'internal_tumor_debris', '>=', self.parameters['internal_tumor_debris_threshold'],
            'DAMP recognition threshold for dendritic cell maturation'
        )
        
        maturation_transition = TransitionMetadata(
            from_state='inactive',
            to_state='active',
            conditions=[maturation_condition],
            biological_context='Tumor debris (DAMPs) trigger dendritic cell maturation and activation'
        )
        
        self.add_transition(Transition(maturation_transition))
    
    def update(self, timestep: float, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update dendritic cell state machine"""
        context['timestep'] = timestep
        
        # Extract relevant variables
        internal_debris = context.get('internal', {}).get('tumor_debris', 0)
        external_debris = context.get('boundary', {}).get('external', {}).get('tumor_debris', 0)
        
        context['internal_tumor_debris'] = internal_debris
        
        # Handle tumor debris uptake
        uptake_update = self._handle_tumor_debris_uptake(context, external_debris)
        
        # Run state machine update
        update = super().update(timestep, context)
        
        # Merge uptake update
        if uptake_update:
            if 'boundary' not in update:
                update['boundary'] = {}
            if 'internal' not in update:
                update['internal'] = {}
            
            update['boundary'].update(uptake_update.get('boundary', {}))
            update['internal'].update(uptake_update.get('internal', {}))
        
        return update
    
    def _handle_tumor_debris_uptake(self, context: Dict[str, Any], 
                                   external_debris: float) -> Dict[str, Any]:
        """Handle tumor debris uptake by dendritic cells"""
        timestep = context.get('timestep', 1.0)
        
        # Calculate available debris for uptake
        available_debris = external_debris * 1e6  # Convert concentration to counts
        
        # Calculate uptake amount
        uptake_amount = min(
            int(self.parameters['tumor_debris_uptake'] * timestep),
            int(available_debris)
        )
        
        if uptake_amount > 0:
            return {
                'boundary': {'exchange': {'tumor_debris': -uptake_amount}},
                'internal': {'tumor_debris': uptake_amount}
            }
        
        return {}


# Factory function for creating state machines
def create_cell_state_machine(cell_type: str, parameters: Dict[str, Any] = None) -> StateMachine:
    """
    Factory function to create appropriate state machine for cell type.
    
    Args:
        cell_type: Type of cell ('tumor', 'tcell', 'dendritic')
        parameters: Optional parameters for the state machine
    
    Returns:
        Appropriate StateMachine instance
    """
    state_machine_classes = {
        'tumor': TumorCellStateMachine,
        'tcell': TCellStateMachine,
        'dendritic': DendriticCellStateMachine
    }
    
    if cell_type not in state_machine_classes:
        raise ValueError(f"Unknown cell type: {cell_type}")
    
    return state_machine_classes[cell_type](parameters)


# Example usage and testing
if __name__ == '__main__':
    # Test tumor cell state machine
    tumor_sm = TumorCellStateMachine()
    
    context = {
        'internal': {'IFNg': 20000},
        'neighbors': {'receive': {'cytotoxic_packets': 5000}},
        'timestep': 60
    }
    
    print(f"Initial tumor state: {tumor_sm.current_state}")
    
    update = tumor_sm.update(60, context)
    print(f"Tumor update: {update}")
    print(f"New tumor state: {tumor_sm.current_state}")
    
    # Test T cell state machine
    tcell_sm = TCellStateMachine()
    
    tcell_context = {
        'internal': {'refractory_count': 5, 'TCR_timer': 0},
        'neighbors': {'accept': {'MHCI': 2000, 'PDL1': 1000}},
        'timestep': 60
    }
    
    print(f"\nInitial T cell state: {tcell_sm.current_state}")
    
    tcell_update = tcell_sm.update(60, tcell_context)
    print(f"T cell update: {tcell_update}")
    print(f"New T cell state: {tcell_sm.current_state}")
    
    print("Cell state transitions template created successfully!")
# 5.5 Molecular Interaction Generation Templates

This directory contains templates for neighbor interaction patterns based on tumor-tcell repository.

## Templates Overview

### 1. `neighbor_interactions.py` - Core neighbor interaction framework
### 2. `molecular_exchange.py` - Molecular transfer and signaling patterns
### 3. `receptor_ligand.py` - Receptor-ligand interaction templates  
### 4. `immune_checkpoints.py` - Immune checkpoint interaction patterns
### 5. `interaction_validation.py` - Validation and testing of molecular interactions

## Usage

These templates provide standardized patterns for:
- Cell-to-cell molecular interactions (present/accept, transfer/receive)
- Receptor-ligand binding and signaling
- Immune checkpoint molecule interactions
- Distance-dependent interaction strength
- Molecular exchange kinetics

## Biological Context

Based on neighbor interaction patterns from tumor-tcell repository:

### Interaction Types
- **present/accept**: Membrane-bound signaling molecules (PDL1-PD1, MHCI-TCR)
- **transfer/receive**: Soluble molecule exchange (cytotoxic packets, cytokines)
- **Distance-dependent**: Interaction strength based on cell proximity
- **Threshold-based**: Binary interactions above molecular thresholds

### Key Molecular Interactions
- **PDL1-PD1**: Immune checkpoint suppression (tumor → T cell)
- **MHCI-TCR**: Antigen recognition (tumor/DC → T cell) 
- **Cytotoxic packets**: T cell killing mechanism (T cell → tumor)
- **IFN-γ**: Cytokine signaling (T cell → environment → tumor)
- **Tumor debris/DAMPs**: Death signals (tumor → DC)

### Interaction Mechanics
- Neighbor detection within specified distance thresholds
- Molecular concentration-dependent binding
- Contact time-dependent signal integration
- Competitive binding between multiple ligands
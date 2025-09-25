# 5.6 Composite Architecture Generation Templates

Agent composer templates based on tumor-tcell repository patterns.

## Templates Overview

### 1. `agent_composer.py` - Abstract composer framework
### 2. `cell_agent_templates.py` - Specific cell agent patterns
### 3. `topology_generation.py` - Process topology wiring templates
### 4. `environment_composers.py` - Environment and field composers

## Key Patterns

Based on composer patterns from *_agent.py files:
- **Process composition**: Combining multiple processes (cell, local_field, division, death)
- **Topology wiring**: Connecting process ports and data flow
- **Parameter inheritance**: Sharing parameters across processes
- **Schema definitions**: Defining data structures and emissions
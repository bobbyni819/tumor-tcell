"""
Process Tests Template
=====================

Process testing patterns based on tumor-tcell repository.

Usage:
    from process_tests import ProcessTestFramework
    
    tester = ProcessTestFramework()
    results = tester.test_process(my_process)
"""

from typing import Dict, Any, List
from vivarium.core.process import Process
from vivarium.core.composition import simulate_process


class ProcessTestFramework:
    """Framework for testing vivarium processes"""
    
    def test_process(self, process: Process, config: Dict[str, Any] = None,
                    total_time: float = 100) -> Dict[str, Any]:
        """Test a process with default configuration"""
        
        config = config or {}
        initial_state = process.initial_state(config)
        
        settings = {
            'return_raw_data': True,
            'initial_state': initial_state,
            'total_time': total_time,
        }
        
        return simulate_process(process, settings)
    
    def validate_process_schema(self, process: Process) -> List[str]:
        """Validate process ports schema"""
        errors = []
        
        try:
            schema = process.ports_schema()
            if not isinstance(schema, dict):
                errors.append("Schema must be a dictionary")
        except Exception as e:
            errors.append(f"Schema generation failed: {e}")
        
        return errors
    
    def test_tumor_process(self):
        """Test tumor process following tumor-tcell patterns"""
        from tumor_tcell.processes.tumor import TumorCellProcess
        
        tumor_process = TumorCellProcess()
        
        # Test basic functionality
        data = self.test_process(tumor_process, total_time=1000)
        
        # Validate results
        assert len(data) > 0, "Process should produce output"
        
        return data
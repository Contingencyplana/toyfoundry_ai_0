# Assembly Line Reception Tests

```python
import unittest
from system import AssemblyLineReception, ValidationError, ReceptionError

class TestAssemblyLineReception(unittest.TestCase):
    def setUp(self):
        self.reception = AssemblyLineReception()

    def test_valid_enhancement(self):
        """Test reception of valid enhancement"""
        enhancement = {
            'type': 'workflow_optimization',
            'target': 'assembly_line_1',
            'parameters': {
                'optimization_type': 'throughput',
                'constraints': {
                    'max_resources': 100,
                    'min_quality': 0.95
                }
            }
        }
        
        result = self.reception.receive_enhancement(enhancement)
        self.assertEqual(result['status'], 'received')
        self.assertEqual(result['validation'], 'passed')

    def test_invalid_schema(self):
        """Test rejection of invalid schema"""
        enhancement = {
            'type': 'invalid_type',
            'target': 'assembly_line_1'
        }
        
        with self.assertRaises(ValidationError):
            self.reception.receive_enhancement(enhancement)

    def test_order036_compliance(self):
        """Test Order-036 compliance validation"""
        enhancement = {
            'type': 'workflow_optimization',
            'target': 'assembly_line_1',
            'parameters': {},
            'protocol_version': 'Order-036',
            'headers': {
                'source': 'ai_labscape',
                'timestamp': '2025-10-18T12:00:00Z'
            }
        }
        
        result = self.reception.receive_enhancement(enhancement)
        self.assertEqual(result['status'], 'received')
        self.assertEqual(result['validation'], 'passed')

    def test_security_validation(self):
        """Test security validation"""
        enhancement = {
            'type': 'workflow_optimization',
            'target': 'assembly_line_1',
            'parameters': {},
            'security': {
                'signature': 'valid_signature',
                'certificate': 'valid_cert'
            }
        }
        
        result = self.reception.receive_enhancement(enhancement)
        self.assertEqual(result['status'], 'received')
        self.assertEqual(result['validation'], 'passed')

if __name__ == '__main__':
    unittest.main()
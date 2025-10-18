"""
Tests for Quality Control Reception System
"""

import unittest
from datetime import datetime
from system import QualityControlReception, ValidationError

class TestQualityControlReception(unittest.TestCase):
    def setUp(self):
        self.reception = QualityControlReception()
        self.base_enhancement = {
            'type': 'quality_insight',
            'target': 'production_line_1',
            'parameters': {
                'threshold': 0.95,
                'inspection_points': [
                    {
                        'location': 'assembly_stage_1',
                        'type': 'visual_inspection',
                        'parameters': {'sensitivity': 0.9}
                    }
                ]
            },
            'protocol_version': 'Order-036',
            'headers': {
                'timestamp': datetime.now().isoformat(),
                'source': 'ai_labscape',
                'sequence': 1
            },
            'security': {
                'signature': 'valid_signature'
            }
        }

    def test_valid_enhancement(self):
        """Test reception of valid enhancement"""
        result = self.reception.receive_enhancement(self.base_enhancement)
        self.assertEqual(result['status'], 'received')
        self.assertTrue(all(result['validation'].values()))

    def test_schema_validation(self):
        """Test schema validation"""
        # Test missing required field
        invalid_enhancement = self.base_enhancement.copy()
        del invalid_enhancement['type']
        with self.assertRaises(ValidationError):
            self.reception.receive_enhancement(invalid_enhancement)

        # Test invalid type
        invalid_enhancement = self.base_enhancement.copy()
        invalid_enhancement['type'] = 'invalid_type'
        with self.assertRaises(ValidationError):
            self.reception.receive_enhancement(invalid_enhancement)

    def test_order036_compliance(self):
        """Test Order-036 compliance validation"""
        # Test missing protocol version
        invalid_enhancement = self.base_enhancement.copy()
        del invalid_enhancement['protocol_version']
        with self.assertRaises(ValidationError):
            self.reception.receive_enhancement(invalid_enhancement)

        # Test missing headers
        invalid_enhancement = self.base_enhancement.copy()
        del invalid_enhancement['headers']
        with self.assertRaises(ValidationError):
            self.reception.receive_enhancement(invalid_enhancement)

    def test_security_validation(self):
        """Test security validation"""
        # Test missing security info
        invalid_enhancement = self.base_enhancement.copy()
        del invalid_enhancement['security']
        with self.assertRaises(ValidationError):
            self.reception.receive_enhancement(invalid_enhancement)

        # Test invalid signature
        invalid_enhancement = self.base_enhancement.copy()
        invalid_enhancement['security']['signature'] = 'invalid_signature'
        with self.assertRaises(ValidationError):
            self.reception.receive_enhancement(invalid_enhancement)

    def test_domain_rules(self):
        """Test domain-specific validation rules"""
        # Test invalid threshold
        invalid_enhancement = self.base_enhancement.copy()
        invalid_enhancement['parameters']['threshold'] = 1.5
        with self.assertRaises(ValidationError):
            self.reception.receive_enhancement(invalid_enhancement)

        # Test invalid inspection point
        invalid_enhancement = self.base_enhancement.copy()
        invalid_enhancement['parameters']['inspection_points'] = [{'invalid': 'point'}]
        with self.assertRaises(ValidationError):
            self.reception.receive_enhancement(invalid_enhancement)

    def test_enhancement_queuing(self):
        """Test enhancement queuing"""
        # Test queue operation
        initial_queue_size = len(self.reception.enhancement_queue)
        self.reception.receive_enhancement(self.base_enhancement)
        self.assertEqual(len(self.reception.enhancement_queue), initial_queue_size + 1)

        # Test queue data
        queued_enhancement = self.reception.enhancement_queue[-1]
        self.assertEqual(queued_enhancement['enhancement'].type, 'quality_insight')
        self.assertEqual(queued_enhancement['status'], 'queued')

if __name__ == '__main__':
    unittest.main()
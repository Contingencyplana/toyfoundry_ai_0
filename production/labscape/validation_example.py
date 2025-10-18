"""
Validation example for single labscape reception
"""

from single_reception import SingleLabscapeReception
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def main():
    # Initialize reception for a single labscape
    labscape_id = "LABSCAPE_001"
    reception = SingleLabscapeReception(labscape_id)
    
    # Create test artifact
    test_artifact = {
        'headers': {
            'timestamp': datetime.now().isoformat(),
            'source': 'ai_unit_001',
            'sequence': 1,
            'labscape_id': 'LABSCAPE_001',
            'artifact_type': 'concept_model',
            'artifact_id': 'ART001'
        },
        'version': '1.0',
        'payload': {
            'model_type': 'component',
            'parameters': {
                'complexity': 0.7,
                'innovation_factor': 0.85
            }
        }
    }
    
    # Test reception
    print("\n=== Testing Single Artifact Reception ===")
    result = reception.receive_artifact(test_artifact)
    print(f"Reception result: {result}")
    
    # Test queue processing
    print("\n=== Processing Artifact Queue ===")
    processed = reception.process_queue(batch_size=1)
    for item in processed:
        print(f"Processed artifact: {item['metadata'].artifact_id}")
        print(f"Status: {item['status']}")
    
    # Check labscape status
    print("\n=== Labscape Status ===")
    status = reception.get_status()
    print(f"Current status: {status}")

if __name__ == "__main__":
    main()
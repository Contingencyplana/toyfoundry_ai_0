"""
Manufacturing Pipeline Validation Example
Tests artifact generation and validation for a single labscape
"""

from pipeline import (
    LabscapeManufacturing,
    ArtifactSpec,
    ArtifactType
)
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def main():
    # Initialize manufacturing pipeline for a single labscape
    labscape_id = "LABSCAPE_001"
    manufacturing = LabscapeManufacturing(labscape_id)
    
    # Create test specifications
    test_specs = [
        ArtifactSpec(
            type=ArtifactType.COMPONENT,
            parameters={
                'component_type': 'processor',
                'attributes': {
                    'capacity': 100,
                    'efficiency': 0.95
                },
                'interfaces': ['input', 'output']
            },
            requirements={
                'performance': {
                    'min_throughput': 50,
                    'max_latency': 100
                },
                'reliability': {
                    'uptime': 0.999,
                    'mtbf': 1000
                }
            }
        ),
        ArtifactSpec(
            type=ArtifactType.ASSEMBLY,
            parameters={
                'assembly_type': 'pipeline',
                'components': ['processor', 'validator'],
                'connections': [
                    {'from': 'processor', 'to': 'validator'}
                ]
            },
            requirements={
                'integration': {
                    'max_coupling': 0.7,
                    'min_cohesion': 0.8
                }
            }
        )
    ]
    
    # Test artifact generation
    print("\n=== Testing Artifact Generation ===")
    for spec in test_specs:
        print(f"\nGenerating {spec.type.value} artifact...")
        artifact = manufacturing.generate_artifact(spec)
        
        print(f"Artifact ID: {artifact.artifact_id}")
        print(f"Type: {artifact.type.value}")
        print(f"Validation Results:")
        for gate, result in artifact.validation_results.items():
            print(f"  {gate}: {'PASS' if result else 'FAIL'}")
            
        print("\nOrder-036 Headers:")
        for key, value in artifact.headers.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
"""
Phase 1 Validation - Single AI Lab/Alfa Unit
Validation example specifically for AI lab/Alfa artifact generation
"""

from pipeline import (
    LabscapeManufacturing,
    ArtifactSpec,
    ArtifactType
)
import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_phase1_artifacts():
    """Run Phase 1 validation for single AI lab/Alfa unit"""
    
    # Initialize manufacturing pipeline
    labscape_id = "LABSCAPE_001"
    manufacturing = LabscapeManufacturing(labscape_id)
    
    # 1. AI Lab/Alfa Unit Component
    alfa_component_spec = ArtifactSpec(
        type=ArtifactType.COMPONENT,
        parameters={
            'component_type': 'ai_lab_unit',
            'attributes': {
                'unit_id': 'ALFA_0001',
                'capacity': 1,  # 1/4,096 of labscape
                'processing_cores': 16,
                'memory_allocation': '64GB',
                'training_capability': 'standard'
            },
            'interfaces': [
                'command_reception',
                'artifact_generation',
                'telemetry_output'
            ]
        },
        requirements={
            'performance': {
                'processing_rate': 100,  # ops/second
                'response_latency': 50,   # milliseconds
                'reliability': 0.9999     # uptime requirement
            },
            'compliance': {
                'schema_version': 'field-report@1.0',
                'protocol': 'Order-036',
                'security_level': 'baseline'
            }
        }
    )
    
    # 2. Assembly Template
    assembly_spec = ArtifactSpec(
        type=ArtifactType.TEMPLATE,
        parameters={
            'template_type': 'ai_lab_assembly',
            'structure': {
                'unit_type': 'alfa',
                'capacity_scale': '1/4096',
                'components': ['processor', 'memory', 'training_unit'],
                'interfaces': ['command', 'artifact', 'telemetry']
            },
            'parameters': {
                'scaling_factor': 0.00024414,  # 1/4096
                'redundancy_level': 'minimal',
                'integration_points': ['labscape_bus', 'command_channel']
            }
        },
        requirements={
            'template_compliance': {
                'schema_version': 'field-report@1.0',
                'validation_level': 'strict'
            }
        }
    )
    
    # 3. Schema Validation Template
    schema_spec = ArtifactSpec(
        type=ArtifactType.SCHEMA,
        parameters={
            'schema_type': 'field_report',
            'version': '1.0',
            'fields': {
                'unit_id': {'type': 'string', 'required': True},
                'timestamp': {'type': 'datetime', 'required': True},
                'metrics': {'type': 'object', 'required': True},
                'status': {'type': 'string', 'required': True}
            },
            'validations': [
                'header_compliance',
                'content_integrity',
                'field_requirements'
            ]
        },
        requirements={
            'schema_compliance': {
                'format': 'field-report@1.0',
                'validation_rules': 'strict'
            }
        }
    )

    artifacts = []
    validation_results = {}
    
    # Generate and validate each artifact in sequence
    specs = [
        ("AI Lab/Alfa Unit Component", alfa_component_spec),
        ("Assembly Template", assembly_spec),
        ("Schema Validation", schema_spec)
    ]
    
    print("\n=== Phase 1 Validation - Single AI Lab/Alfa Unit ===")
    
    for name, spec in specs:
        print(f"\nGenerating {name}...")
        try:
            artifact = manufacturing.generate_artifact(spec)
            artifacts.append(artifact)
            validation_results[name] = artifact.validation_results
            
            print(f"Artifact ID: {artifact.artifact_id}")
            print("Order-036 Headers:")
            for key, value in artifact.headers.items():
                print(f"  {key}: {value}")
                
            print("Validation Results:")
            for gate, result in artifact.validation_results.items():
                status = "PASS" if result else "FAIL"
                print(f"  {gate}: {status}")
                
            print(f"Checksum: {artifact.checksum}")
            
        except Exception as e:
            logger.error(f"Error generating {name}: {str(e)}")
            print(f"ERROR: Failed to generate {name}")
            raise

    # Generate production report
    report = {
        'timestamp': datetime.now().isoformat(),
        'labscape_id': labscape_id,
        'artifacts_generated': len(artifacts),
        'validation_summary': {
            name: all(results.values())
            for name, results in validation_results.items()
        },
        'production_log': manufacturing.production_log
    }
    
    # Save production report
    report_path = 'phase1_validation_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"\nProduction Report saved to: {report_path}")
    
    return artifacts, validation_results, report

if __name__ == "__main__":
    validate_phase1_artifacts()
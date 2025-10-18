"""
Validation example for labscape monitoring system
"""

from monitor import LabscapeMonitor, MetricType
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def main():
    # Initialize monitoring for a single labscape
    labscape_id = "LABSCAPE_001"
    monitor = LabscapeMonitor(labscape_id)
    
    # Create test telemetry points
    test_points = [
        {
            'headers': {
                'timestamp': datetime.now().isoformat(),
                'source': 'ai_unit_001',
                'sequence': 1,
                'labscape_id': 'LABSCAPE_001'
            },
            'metric_type': 'PERFORMANCE',
            'value': 150.0,
            'unit': 'ms',
            'context': {
                'operation': 'artifact_generation',
                'batch_size': 1
            }
        },
        {
            'headers': {
                'timestamp': datetime.now().isoformat(),
                'source': 'ai_unit_001',
                'sequence': 2,
                'labscape_id': 'LABSCAPE_001'
            },
            'metric_type': 'RESOURCE',
            'value': 75.5,
            'unit': 'percent',
            'context': {
                'resource_type': 'cpu',
                'operation_type': 'processing'
            }
        }
    ]
    
    # Test telemetry collection
    print("\n=== Testing Telemetry Collection ===")
    for point in test_points:
        result = monitor.collect_telemetry(point)
        print(f"Collection result: {result}")
    
    # Update and check performance metrics
    print("\n=== Performance Metrics ===")
    metrics = monitor.update_performance_metrics()
    print(f"Current metrics: {metrics}")
    
    # Generate monitoring report
    print("\n=== Monitoring Report ===")
    report = monitor.get_monitoring_report()
    print(f"Report summary: {report}")

if __name__ == "__main__":
    main()
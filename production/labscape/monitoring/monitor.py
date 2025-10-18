"""
Labscape Monitoring System
Handles telemetry collection and performance monitoring for a single AI Labscape
Part of Phase 1 Foundation (1/256 scale implementation)
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics collected from labscape operations"""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    SAFETY = "safety"
    ARTIFACT = "artifact"
    INTERACTION = "interaction"

@dataclass
class TelemetryPoint:
    """Individual telemetry data point"""
    timestamp: str
    metric_type: MetricType
    value: float
    unit: str
    source: str
    context: Dict[str, Any]

@dataclass
class PerformanceMetrics:
    """Core performance metrics for labscape operations"""
    artifact_generation_rate: float  # artifacts per minute
    processing_latency: float       # milliseconds
    queue_depth: int               # current queue size
    error_rate: float             # errors per 1000 operations
    resource_utilization: float   # percentage

class LabscapeMonitor:
    """
    Monitoring and telemetry system for a single AI Labscape
    Focuses on comprehensive data collection and analysis
    """
    
    def __init__(self, labscape_id: str):
        self.labscape_id = labscape_id
        self.telemetry_data: List[TelemetryPoint] = []
        self.performance_history: List[PerformanceMetrics] = []
        self.alert_thresholds: Dict[str, float] = {
            'error_rate': 5.0,        # errors per 1000 ops
            'latency': 1000.0,        # ms
            'utilization': 90.0       # percent
        }
        
    def collect_telemetry(self, data_point: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect and store a single telemetry data point
        Returns validation result
        """
        try:
            # Validate Order-036 headers
            if not self._validate_telemetry_headers(data_point):
                raise ValueError("Invalid telemetry headers")

            # Create telemetry point
            point = TelemetryPoint(
                timestamp=data_point['headers']['timestamp'],
                metric_type=MetricType(data_point['metric_type']),
                value=data_point['value'],
                unit=data_point['unit'],
                source=data_point['headers']['source'],
                context=data_point.get('context', {})
            )
            
            # Store telemetry
            self.telemetry_data.append(point)
            
            # Check for alerts
            alerts = self._check_alerts(point)
            
            return {
                'status': 'collected',
                'timestamp': datetime.now().isoformat(),
                'alerts': alerts
            }

        except Exception as e:
            logger.error(f"Error collecting telemetry: {str(e)}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'message': str(e)
            }

    def update_performance_metrics(self) -> PerformanceMetrics:
        """
        Calculate and store current performance metrics
        Returns latest metrics
        """
        # Calculate metrics from recent telemetry
        recent_metrics = self._calculate_recent_metrics()
        
        # Store in history
        self.performance_history.append(recent_metrics)
        
        # Trim history if needed
        if len(self.performance_history) > 1000:  # Keep last 1000 metric points
            self.performance_history = self.performance_history[-1000:]
            
        return recent_metrics

    def get_monitoring_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive monitoring report
        """
        current_metrics = self.update_performance_metrics()
        
        return {
            'labscape_id': self.labscape_id,
            'timestamp': datetime.now().isoformat(),
            'current_metrics': {
                'artifact_generation_rate': current_metrics.artifact_generation_rate,
                'processing_latency': current_metrics.processing_latency,
                'queue_depth': current_metrics.queue_depth,
                'error_rate': current_metrics.error_rate,
                'resource_utilization': current_metrics.resource_utilization
            },
            'telemetry_points_collected': len(self.telemetry_data),
            'performance_history_length': len(self.performance_history),
            'alert_status': self._get_alert_status()
        }

    def _validate_telemetry_headers(self, data_point: Dict[str, Any]) -> bool:
        """Validate Order-036 compliant headers for telemetry"""
        required_fields = {
            'timestamp',
            'source',
            'sequence',
            'labscape_id'
        }
        
        if 'headers' not in data_point:
            return False
            
        headers = data_point['headers']
        if not all(field in headers for field in required_fields):
            return False
            
        if headers['labscape_id'] != self.labscape_id:
            return False
            
        return True

    def _calculate_recent_metrics(self) -> PerformanceMetrics:
        """Calculate metrics from recent telemetry data"""
        # In real implementation, this would analyze recent telemetry
        # For now, return placeholder metrics
        return PerformanceMetrics(
            artifact_generation_rate=0.0,
            processing_latency=0.0,
            queue_depth=0,
            error_rate=0.0,
            resource_utilization=0.0
        )

    def _check_alerts(self, point: TelemetryPoint) -> List[Dict[str, Any]]:
        """Check telemetry point against alert thresholds"""
        alerts = []
        
        # Example alert checks
        if point.metric_type == MetricType.PERFORMANCE:
            if point.value > self.alert_thresholds['latency']:
                alerts.append({
                    'type': 'latency_alert',
                    'threshold': self.alert_thresholds['latency'],
                    'value': point.value,
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts

    def _get_alert_status(self) -> Dict[str, Any]:
        """Get current alert status"""
        return {
            'active_alerts': len([p for p in self.telemetry_data[-100:] 
                                if self._check_alerts(p)]),
            'thresholds': self.alert_thresholds
        }
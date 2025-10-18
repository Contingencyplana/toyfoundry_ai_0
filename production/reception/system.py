"""
Basic Reception System for ToyFoundry AI
Implements minimal Order-036 compliant reception point
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReceptionPoint:
    """Basic reception point for incoming enhancements"""
    name: str
    type: str
    status: str = "active"

class BasicReception:
    """
    Minimal implementation of a reception system
    Handles basic Order-036 compliance and command exchange
    """
    
    def __init__(self):
        self.reception_points = {}
        self.incoming_queue = []
        
    def register_reception_point(self, name: str, point_type: str) -> ReceptionPoint:
        """Register a new reception point"""
        point = ReceptionPoint(name=name, type=point_type)
        self.reception_points[name] = point
        logger.info(f"Registered reception point: {name} of type {point_type}")
        return point

    def validate_order036_headers(self, headers: Dict[str, Any]) -> bool:
        """Basic Order-036 header validation"""
        required_fields = {'timestamp', 'source', 'sequence'}
        return all(field in headers for field in required_fields)

    def receive_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive and process an incoming command
        Implements minimal Order-036 compliance
        """
        try:
            # Basic validation
            if 'headers' not in command:
                raise ValueError("Missing Order-036 headers")
            
            if not self.validate_order036_headers(command['headers']):
                raise ValueError("Invalid Order-036 headers")

            # Queue the command
            self.incoming_queue.append({
                'command': command,
                'received_at': datetime.now().isoformat(),
                'status': 'queued'
            })

            return {
                'status': 'received',
                'timestamp': datetime.now().isoformat(),
                'message': 'Command queued for processing'
            }

        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'message': str(e)
            }

    def process_queue(self) -> None:
        """Basic queue processing"""
        while self.incoming_queue:
            item = self.incoming_queue.pop(0)
            logger.info(f"Processing queued command: {item['command'].get('type', 'unknown')}")
            # Basic processing - will be expanded later
            item['status'] = 'processed'
"""
Single Labscape Reception System
Handles artifact reception and validation for a single AI Labscape
Part of Phase 1 Foundation (1/256 scale implementation)
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ArtifactMetadata:
    """Metadata for a single AI-generated artifact"""
    artifact_id: str
    labscape_id: str
    generation_timestamp: str
    type: str
    version: str
    checksum: str

@dataclass
class LabscapeStatus:
    """Status tracking for a single labscape"""
    labscape_id: str
    artifact_count: int = 0
    last_artifact_timestamp: Optional[str] = None
    status: str = "active"

class SingleLabscapeReception:
    """
    Reception system for a single AI Labscape (1/256 scale)
    Focuses on artifact reception and Order-036 compliance
    """
    
    def __init__(self, labscape_id: str):
        self.labscape_id = labscape_id
        self.status = LabscapeStatus(labscape_id=labscape_id)
        self.artifact_queue = []
        self.processed_artifacts: List[str] = []  # Store processed artifact IDs
        
    def validate_artifact_headers(self, headers: Dict[str, Any]) -> bool:
        """
        Validate Order-036 headers for artifact reception
        Minimal implementation for single labscape validation
        """
        required_fields = {
            'timestamp',
            'source',
            'sequence',
            'labscape_id',
            'artifact_type'
        }
        
        if not all(field in headers for field in required_fields):
            return False
            
        # Verify labscape ID matches
        if headers['labscape_id'] != self.labscape_id:
            logger.error(f"Labscape ID mismatch: {headers['labscape_id']} != {self.labscape_id}")
            return False
            
        return True

    def receive_artifact(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive and validate a single artifact from the labscape
        """
        try:
            # Header validation
            if 'headers' not in artifact:
                raise ValueError("Missing Order-036 headers")
            
            if not self.validate_artifact_headers(artifact['headers']):
                raise ValueError("Invalid Order-036 headers")

            # Create artifact metadata
            metadata = ArtifactMetadata(
                artifact_id=artifact['headers'].get('artifact_id', f"ART-{datetime.now().timestamp()}"),
                labscape_id=self.labscape_id,
                generation_timestamp=artifact['headers']['timestamp'],
                type=artifact['headers']['artifact_type'],
                version=artifact.get('version', '1.0'),
                checksum=self._generate_checksum(artifact)
            )

            # Queue artifact with metadata
            queued_item = {
                'artifact': artifact,
                'metadata': metadata,
                'received_at': datetime.now().isoformat(),
                'status': 'queued'
            }
            self.artifact_queue.append(queued_item)
            
            # Update labscape status
            self.status.artifact_count += 1
            self.status.last_artifact_timestamp = datetime.now().isoformat()

            return {
                'status': 'received',
                'artifact_id': metadata.artifact_id,
                'timestamp': datetime.now().isoformat(),
                'queue_position': len(self.artifact_queue)
            }

        except Exception as e:
            logger.error(f"Error receiving artifact: {str(e)}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'message': str(e)
            }

    def _generate_checksum(self, artifact: Dict[str, Any]) -> str:
        """Generate a simple checksum for artifact validation"""
        # Basic implementation - would be replaced with proper cryptographic hash
        return str(hash(json.dumps(artifact, sort_keys=True)))

    def process_queue(self, batch_size: int = 1) -> List[Dict[str, Any]]:
        """
        Process queued artifacts
        Returns list of processed artifacts
        """
        processed = []
        for _ in range(min(batch_size, len(self.artifact_queue))):
            if not self.artifact_queue:
                break
                
            item = self.artifact_queue.pop(0)
            
            # Basic processing - verify checksum and store artifact ID
            current_checksum = self._generate_checksum(item['artifact'])
            if current_checksum != item['metadata'].checksum:
                logger.error(f"Checksum mismatch for artifact {item['metadata'].artifact_id}")
                item['status'] = 'error'
            else:
                item['status'] = 'processed'
                self.processed_artifacts.append(item['metadata'].artifact_id)
            
            processed.append(item)
            
        return processed

    def get_status(self) -> Dict[str, Any]:
        """Get current labscape status"""
        return {
            'labscape_id': self.labscape_id,
            'artifacts_received': self.status.artifact_count,
            'artifacts_processed': len(self.processed_artifacts),
            'queue_size': len(self.artifact_queue),
            'last_activity': self.status.last_artifact_timestamp,
            'status': self.status.status
        }
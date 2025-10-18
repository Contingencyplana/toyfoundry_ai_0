"""
Example usage of the basic reception system
"""

from system import BasicReception
from datetime import datetime

def main():
    # Create reception system
    reception = BasicReception()
    
    # Register a reception point
    reception.register_reception_point(
        name="test_point",
        point_type="command"
    )
    
    # Create a test command
    test_command = {
        'type': 'test_command',
        'headers': {
            'timestamp': datetime.now().isoformat(),
            'source': 'test_system',
            'sequence': 1
        },
        'payload': {
            'action': 'test'
        }
    }
    
    # Send command
    result = reception.receive_command(test_command)
    print(f"Reception result: {result}")
    
    # Process queue
    reception.process_queue()

if __name__ == "__main__":
    main()
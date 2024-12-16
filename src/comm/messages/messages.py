import asyncio
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from comm.comm_service import CommunicationService
from comm.messages.message_base import MessageBase

# Existing Vector3 and MessageBase classes from previous implementation

class MessageTypes:
    # ... previous message types ...
    LOAD_PLANNING_DATA_REQUEST = "LoadPlanningDataRequest"
    LOAD_PLANNING_DATA_RESPONSE = "LoadPlanningDataResponse"
    START_REGISTRATION_REQUEST = "StartRegistrationRequest"
    START_REGISTRATION_RESPONSE = "StartRegistrationResponse"
    STOP_REGISTRATION_REQUEST = "StopRegistrationRequest"
    STOP_REGISTRATION_RESPONSE = "StopRegistrationResponse"
    UPDATE_ANTENNA_SAMPLE_REQUEST = "UpdateAntennaSampleRequest"
    UPDATE_ANTENNA_SAMPLE_RESPONSE = "UpdateAntennaSampleResponse"

@dataclass
class TranslationVector:
    """Represents a translation vector with x, y, z coordinates"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_dict(self):
        return {"x": self.x, "y": self.y, "z": self.z}

@dataclass
class Lumen:
    """Represents a lumen with position and radius"""
    x: int = 0
    y: int = 0
    radius: int = 0
    fid: int = 0

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "fid": self.fid
        }

@dataclass
class CGSClock:
    """Represents a clock with timestamp"""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {"timestamp": self.timestamp.isoformat()}

@dataclass
class CGSSample:
    """Represents a CGS sample"""
    # Add specific attributes as needed
    data: dict = field(default_factory=dict)

    def to_dict(self):
        return self.data
    
@dataclass 
class Vector3:
    def __init__(self, x=0.0, y=0.0 , z=0.0):
        self.X = x
        self.Y = y
        self.Z = z


@dataclass
class LoadPlanningDataRequest(MessageBase):
    """Request for loading planning data"""
    def __init__(self, 
                 skeleton_dir_path: str = '',
                 data_dir_file_path: str = '',
                 target_position: Vector3 = None):
        super().__init__(MessageTypes.LOAD_PLANNING_DATA_REQUEST)
        self.skeleton_dir_path = skeleton_dir_path
        self.data_dir_file_path = data_dir_file_path
        self.target_position = target_position or Vector3()

@dataclass
class LoadPlanningDataResponse(MessageBase):
    """Response for loading planning data"""
    def __init__(self, 
                 success: bool = False, 
                 error_message: str = ''):
        super().__init__(MessageTypes.LOAD_PLANNING_DATA_RESPONSE)
        self.success = success
        self.error_message = error_message

@dataclass
class StartRegistrationRequest(MessageBase):
    """Request to start registration"""
    def __init__(self, 
                 pst1_position: TranslationVector = None,
                 pst2_position: TranslationVector = None,
                 pst3_position: TranslationVector = None):
        super().__init__(MessageTypes.START_REGISTRATION_REQUEST)
        self.pst1_position = pst1_position or TranslationVector()
        self.pst2_position = pst2_position or TranslationVector()
        self.pst3_position = pst3_position or TranslationVector()

@dataclass
class StartRegistrationResponse(MessageBase):
    """Response for start registration"""
    def __init__(self, 
                 success: bool = False, 
                 error_message: str = ''):
        super().__init__(MessageTypes.START_REGISTRATION_RESPONSE)
        self.success = success
        self.error_message = error_message

@dataclass
class StopRegistrationRequest(MessageBase):
    """Request to stop registration"""
    def __init__(self):
        super().__init__(MessageTypes.STOP_REGISTRATION_REQUEST)

@dataclass
class StopRegistrationResponse(MessageBase):
    """Response for stop registration"""
    def __init__(self, 
                 success: bool = False, 
                 error_message: str = ''):
        super().__init__(MessageTypes.STOP_REGISTRATION_RESPONSE)
        self.success = success
        self.error_message = error_message

@dataclass
class UpdateAntennaSampleRequest(MessageBase):
    """Request to update antenna sample"""
    def __init__(self, 
                 pc_time: int = 0,
                 cgs_time: CGSClock = None,
                 cgs_sample: CGSSample = None):
        super().__init__(MessageTypes.UPDATE_ANTENNA_SAMPLE_REQUEST)
        self.pc_time = pc_time
        self.cgs_time = cgs_time or CGSClock()
        self.cgs_sample = cgs_sample or CGSSample()

@dataclass
class UpdateAntennaSampleResponse(MessageBase):
    """Response for updating antenna sample"""
    def __init__(self, 
                 pc_time: str = '',
                 cgs_time: CGSClock = None,
                 process_time: float = 0.0,
                 lg_ct_position: List[List[float]] = None,
                 node_id: int = 0,
                 lumens: List[Lumen] = None,
                 selections: List[Lumen] = None):
        super().__init__(MessageTypes.UPDATE_ANTENNA_SAMPLE_RESPONSE)
        self.pc_time = pc_time
        self.cgs_time = cgs_time or CGSClock()
        self.process_time = process_time
        self.lg_ct_position = lg_ct_position or []
        self.node_id = node_id
        self.lumens = lumens or []
        self.selections = selections or []

# Example usage in the communication service
async def example_message_handlers(comm_service: CommunicationService):
    """Example of registering handlers for different message types"""
    
    # Handler for Load Planning Data Request
    async def handle_load_planning_data(message):
        # Process the request and return a response
        request = LoadPlanningDataRequest(**message)
        response = LoadPlanningDataResponse(
            success=True, 
            error_message=""
        )
        return response.to_dict()
    
    # Handler for Start Registration Request
    async def handle_start_registration(message):
        request = StartRegistrationRequest(**message)
        response = StartRegistrationResponse(
            success=True, 
            error_message=""
        )
        return response.to_dict()
    
    # Register handlers
    comm_service.register_handler(
        MessageTypes.LOAD_PLANNING_DATA_REQUEST, 
        handle_load_planning_data
    )
    comm_service.register_handler(
        MessageTypes.START_REGISTRATION_REQUEST, 
        handle_start_registration
    )

# Demonstration of sending and receiving messages
async def demonstration():
    # Create communication service
    comm_service = CommunicationService(host='localhost', port=8000)
    
    # Register message handlers
    await example_message_handlers(comm_service)
    
    # As a client: send a load planning data request
    request = LoadPlanningDataRequest(
        skeleton_dir_path='/path/to/skeleton',
        data_dir_file_path='/path/to/data',
        target_position=Vector3(1.0, 2.0, 3.0)
    )
    
    # Send the request and await response
    response = await comm_service.send_message(request)
    print("Received response:", response)

# Run the demonstration
if __name__ == '__main__':
    asyncio.run(demonstration())
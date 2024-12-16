
class MessageBase:
    """Base class for all messages"""
    def __init__(self, message_type: str):
        self.id = str(uuid.uuid4())
        self.type = message_type

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str: str):
        return cls(**json.loads(json_str))


class MessageTypes:
    """Defines message type constants"""
    INIT_CONTINUES_REGISTRATION_REQUEST = "InitContinuesRegistrationRequest"
    INIT_CONTINUES_REGISTRATION_RESPONSE = "InitContinuesRegistrationResponse"
    LOAD_PLANNING_DATA_REQUEST = "LoadPlanningDataRequest"
    LOAD_PLANNING_DATA_RESPONSE = "LoadPlanningDataResponse"
    START_REGISTRATION_REQUEST = "StartRegistrationRequest"
    STOP_REGISTRATION_REQUEST = "StopRegistrationRequest"
    UPDATE_ANTENNA_SAMPLE_REQUEST = "UpdateAntennaSampleRequest"
    UPDATE_ANTENNA_SAMPLE_RESPONSE = "UpdateAntennaSampleResponse"

class InitContinuesRegistrationRequest(MessageBase):
    """Request for continuous registration initialization"""
    def __init__(self, 
                 configuration_dir_path: str = '',
                 catheter_calibration_path: str = '',
                 log_file_path: str = '',
                 shared_memory_name: str = '',
                 frame_width: int = 0,
                 frame_height: int = 0,
                 color_bytes: int = 0):
        super().__init__(MessageTypes.INIT_CONTINUES_REGISTRATION_REQUEST)
        self.configuration_dir_path = configuration_dir_path
        self.catheter_calibration_path = catheter_calibration_path
        self.log_file_path = log_file_path
        self.shared_memory_name = shared_memory_name
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.color_bytes = color_bytes
        

class InitContinuesRegistrationResponse(MessageBase):
    """Response for continuous registration initialization"""
    def __init__(self, 
                 success: bool = False, 
                 error_message: str = ''):
        super().__init__(MessageTypes.INIT_CONTINUES_REGISTRATION_RESPONSE)
        self.success = success
        self.error_message = error_message
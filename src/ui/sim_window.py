from datetime import datetime
import sys
import os

print("PYTHONPATH:", os.getenv('PYTHONPATH'))
print("sys.path:", sys.path)

from comm.messages.vector3 import Vector3
from comm.messages.message_base import InitContinuesRegistrationRequest
from comm.messages.messages import CGSClock, CGSSample, LoadPlanningDataRequest, StartRegistrationRequest, StopRegistrationRequest, TranslationVector, UpdateAntennaSampleRequest
# from algoSimEnv.Lib import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from comm.comm_service import CommunicationService, MessageTypes

class VideoRegistrationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Registration Application")
        self.setGeometry(100, 100, 1000, 800)

        # Main central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Video feed layout
        video_layout = QVBoxLayout()
        main_layout.addLayout(video_layout)

        # Video display
        self.video_label = QLabel()
        self.video_label.setFixedSize(720, 720)
        video_layout.addWidget(self.video_label)

        # Buttons layout
        buttons_layout = QVBoxLayout()
        main_layout.addLayout(buttons_layout)

        # Create 6 buttons
        button_texts = [
            "Init Continuous Registration",
            "Load Planning Data",
            "Start Registration",
            "Stop Registration",
            "Update Antenna Sample",
            "Exit"
        ]

        self.buttons = []
        for text in button_texts:
            button = QPushButton(text)
            button.setFixedSize(250, 50)
            buttons_layout.addWidget(button)
            self.buttons.append(button)

        # Connect button clicks
        self.buttons[0].clicked.connect(self.on_init_continuous_registration)
        self.buttons[1].clicked.connect(self.on_load_planning_data)
        self.buttons[2].clicked.connect(self.on_start_registration)
        self.buttons[3].clicked.connect(self.on_stop_registration)
        self.buttons[4].clicked.connect(self.on_update_antenna_sample)
        self.buttons[5].clicked.connect(self.close)

        # Video capture setup
        self.capture = cv2.VideoCapture(0)  # Use default camera
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 FPS

        # Communication service
        self.comm_service = self.setup_communication_service()

    def setup_communication_service(self):
        """Setup communication service"""
        comm_service = CommunicationService()
        
        # Register message handlers
        comm_service.register_handler(
            MessageTypes.INIT_CONTINUES_REGISTRATION_REQUEST, 
            self.handle_init_continuous_registration
        )
        # Add other message handlers similarly
        
        return comm_service

    async def handle_init_continuous_registration(self, message):
        """Handle init continuous registration request"""
        # Implement your logic here
        response = {
            'success': True,
            'error_message': ''
        }
        return response

    def update_frame(self):
        """Update video frame"""
        ret, frame = self.capture.read()
        if ret:
            # Resize frame to 720x720
            frame = cv2.resize(frame, (720, 720))
            
            # Convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to QImage
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Set pixmap
            pixmap = QPixmap.fromImage(qt_image)
            self.video_label.setPixmap(pixmap)

    async def on_init_continuous_registration(self):
        """Initialize continuous registration"""
        try:
            request = InitContinuesRegistrationRequest(
                configuration_dir_path='/path/to/config',
                shared_memory_name='video_frame_shm',
                frame_width=720,
                frame_height=720
            )
            response = await self.comm_service.send_message(request)
            print("Init Continuous Registration Response:", response)
        except Exception as e:
            print(f"Error in init continuous registration: {e}")

    async def on_load_planning_data(self):
        """Load planning data"""
        try:
            request = LoadPlanningDataRequest(
                skeleton_dir_path='/path/to/skeleton',
                data_dir_file_path='/path/to/data',
                target_position=Vector3(1.0, 2.0, 3.0)
            )
            response = await self.comm_service.send_message(request)
            print("Load Planning Data Response:", response)
        except Exception as e:
            print(f"Error in load planning data: {e}")

    async def on_start_registration(self):
        """Start registration"""
        try:
            request = StartRegistrationRequest(
                pst1_position=TranslationVector(1.0, 0.0, 0.0),
                pst2_position=TranslationVector(0.0, 1.0, 0.0),
                pst3_position=TranslationVector(0.0, 0.0, 1.0)
            )
            response = await self.comm_service.send_message(request)
            print("Start Registration Response:", response)
        except Exception as e:
            print(f"Error in start registration: {e}")

    async def on_stop_registration(self):
        """Stop registration"""
        try:
            request = StopRegistrationRequest()
            response = await self.comm_service.send_message(request)
            print("Stop Registration Response:", response)
        except Exception as e:
            print(f"Error in stop registration: {e}")

    async def on_update_antenna_sample(self):
        """Update antenna sample"""
        try:
            request = UpdateAntennaSampleRequest(
                pc_time=int(datetime.now().timestamp()),
                cgs_time=CGSClock(),
                cgs_sample=CGSSample()
            )
            response = await self.comm_service.send_message(request)
            print("Update Antenna Sample Response:", response)
        except Exception as e:
            print(f"Error in update antenna sample: {e}")

    def closeEvent(self, event):
        """Handle application close"""
        self.capture.release()
        self.timer.stop()
        event.accept()

def run_app():
    """Run the application"""
    import asyncio
    
    # Create event loop
    loop = asyncio.get_event_loop()
    
    # Create application
    app = QApplication(sys.argv)
    window = VideoRegistrationApp()
    window.show()
    
    # Run the event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()
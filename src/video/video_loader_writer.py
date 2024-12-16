import cv2
import numpy as np
from multiprocessing import shared_memory
import multiprocessing as mp
import time

def video_loader_writer(video_path, shared_memory_name):
    # Open the video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create shared memory for metadata
    metadata_shm = shared_memory.SharedMemory(name='video_metadata', create=True, size=16)
    metadata_array = np.ndarray((4,), dtype=np.int32, buffer=metadata_shm.buf)
    
    # Create shared memory for frame
    frame_shm = shared_memory.SharedMemory(name=shared_memory_name, create=True, size=frame_width * frame_height * 3)
    frame_array = np.ndarray((frame_height, frame_width, 3), dtype=np.uint8, buffer=frame_shm.buf)

    frame_id = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                # Signal end of video
                metadata_array[0] = -1
                break

            # Update metadata
            metadata_array[0] = frame_id  # Frame ID
            metadata_array[1] = frame_height  # Frame Height
            metadata_array[2] = frame_width   # Frame Width
            metadata_array[3] = 1  # Frame available flag

            # Copy frame to shared memory
            frame_array[:] = frame

            frame_id += 1
            time.sleep(1/30)  # Control frame rate

    finally:
        cap.release()
        metadata_shm.close()
        metadata_shm.unlink()
        frame_shm.close()
        frame_shm.unlink()

def main():
    video_path = 'your_video.mp4'  # Replace with your video path
    shared_memory_name = 'video_frame_shm'
    
    video_loader_writer(video_path, shared_memory_name)

if __name__ == '__main__':
    main()
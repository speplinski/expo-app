import argparse
import signal
import sys
import time
import os

from oak_camera_system import CameraManager

def signal_handler(sig, frame):
    print('\nShutting down cameras...')
    if 'manager' in globals():
        manager.stop_all()
    sys.exit(0)

def parse_arguments():
    parser = argparse.ArgumentParser(description='OAK-D Camera System')
    parser.add_argument('--config', help='Path to camera configuration file')
    parser.add_argument('--cameras', nargs='+', help='Specific cameras to start (left, center, right)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    config_path = args.config
    if config_path and not os.path.isabs(config_path):
        config_path = os.path.abspath(config_path)
    
    print(f"Initializing cameras{' from config: ' + config_path if config_path else ' with default settings'}")
    manager = CameraManager(config_path)
    manager.initialize_cameras()
    
    if args.cameras:
        for camera_name in args.cameras:
            if manager.start_camera(camera_name):
                print(f"Started camera: {camera_name}")
            else:
                print(f"Camera not found: {camera_name}")
    else:
        manager.start_all()
    
    print("\nCamera system running. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(10)
            statuses = manager.get_camera_status()
            for name, status in statuses.items():
                print(status)
    except KeyboardInterrupt:
        signal_handler(None, None)
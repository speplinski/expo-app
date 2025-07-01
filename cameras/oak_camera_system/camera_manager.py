import json
import threading
from .oak_camera import OakCamera
from .camera_config import DEFAULT_CAMERAS

class CameraManager:
    def __init__(self, config_file=None):
        self.configs = self._load_configs(config_file)
        self.cameras = {}
        self._lock = threading.Lock()
    
    def _load_configs(self, config_file):
        if not config_file:
            return DEFAULT_CAMERAS
            
        with open(config_file, 'r') as f:
            data = json.load(f)

            if isinstance(data, list):
                return data
            elif 'cameras' in data:
                return data['cameras']
            else:
                raise ValueError("Invalid configuration format")
    
    def initialize_cameras(self):
        with self._lock:
            for config in self.configs:
                name = config['name']
                self.cameras[name] = OakCamera(config)
                print(f"Initialized camera: {name} ({config['ip_address']})")
            
            return self.cameras
    
    def start_all(self):
        with self._lock:
            for name, camera in self.cameras.items():
                camera.start()
                print(f"Started camera: {name}")
    
    def stop_all(self):
        with self._lock:
            for name, camera in self.cameras.items():
                camera.stop()
            print("All cameras stopped")
    
    def get_camera(self, name):
        with self._lock:
            return self.cameras.get(name)
    
    def get_camera_status(self):
        with self._lock:
            return {name: camera.get_status() for name, camera in self.cameras.items()}
    
    def start_camera(self, name):
        with self._lock:
            camera = self.cameras.get(name)
            if camera:
                camera.start()
                print(f"Started camera: {name}")
                return True
            return False
    
    def stop_camera(self, name):
        with self._lock:
            camera = self.cameras.get(name)
            if camera:
                camera.stop()
                print(f"Stopped camera: {name}")
                return True
            return False
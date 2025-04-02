import socket
import re
import logging
import numpy as np
from typing import List, Dict, Any

from config.modules_configs.depth_config import DepthConfig, OakCameraConfig


class OakSocketAdapter:
    def __init__(self, config: DepthConfig):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.nH = config.depth_grid_segments_count.horizontal
        self.nV = config.depth_grid_segments_count.vertical
        self.header_length = config.header_length

        self.logger.info(f"Initialized OakSocketAdapter with {len(config.cameras)} cameras")

    def read_frame_from_camera(self, camera_config: OakCameraConfig) -> np.ndarray:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(camera_config.timeout)
                sock.connect((camera_config.ip_address, camera_config.port))

                chunks = []
                bytes_recd = 0
                while bytes_recd < self.header_length:
                    chunk = sock.recv(min(self.header_length - bytes_recd, 2048))
                    if chunk == b'':
                        raise RuntimeError(f"Socket connection broken to {camera_config.ip_address}")
                    chunks.append(chunk)
                    bytes_recd = bytes_recd + len(chunk)
                header = str(b''.join(chunks), encoding="ascii")

                header_s = re.split(' +', header)
                if header_s[0] == "HEAD":
                    message_length = int(header_s[1])

                    chunks = []
                    bytes_recd = 0
                    while bytes_recd < message_length:
                        chunk = sock.recv(min(message_length - bytes_recd, 2048))
                        if chunk == b'':
                            raise RuntimeError(f"Socket connection broken to {camera_config.ip_address}")
                        chunks.append(chunk)
                        bytes_recd = bytes_recd + len(chunk)
                    msg = str(b''.join(chunks), encoding="ascii")

                    distances = []
                    dets = msg.split("|")
                    for det in dets:
                        if det.strip():  # Skip empty strings
                            try:
                                distances.append(float(det))
                            except ValueError:
                                self.logger.warning(f"Invalid distance value: '{det}'")

                    expected_length = self.nH * self.nV
                    if len(distances) != expected_length:
                        self.logger.warning(
                            f"Unexpected number of distance values from {camera_config.ip_address}: "
                            f"got {len(distances)}, expected {expected_length}"
                        )
                        if len(distances) < expected_length:
                            distances.extend([0.0] * (expected_length - len(distances)))
                        else:
                            distances = distances[:expected_length]
                    
                    return np.array(distances)
                else:
                    raise ValueError(f"Invalid header format from camera {camera_config.ip_address}: {header}")
        except Exception as e:
            self.logger.error(f"Error reading from camera {camera_config.ip_address}: {str(e)}")
            return np.zeros(self.nH * self.nV)

    def get_distances(self) -> List[np.ndarray]:
        camera_distances = []

        for camera_key, camera_config in self.config.cameras.items():
            try:
                self.logger.debug(f"Reading from camera {camera_key} at {camera_config.ip_address}")
                distances = self.read_frame_from_camera(camera_config)
                camera_distances.append(distances)
            except Exception as e:
                self.logger.error(f"Failed to get distances from camera {camera_key}: {str(e)}")
                # Add empty array as fallback
                camera_distances.append(np.zeros(self.nH * self.nV))

        return camera_distances

    def close(self):
        self.logger.info("OakSocketAdapter closed")

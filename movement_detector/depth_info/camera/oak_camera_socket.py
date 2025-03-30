import socket
import re
import logging
import time
from typing import List, Optional


class OakCameraSocket:
    def __init__(self, ip_address: str, port: int = 65432, timeout: float = 5.0):
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.logger = logging.getLogger()
        self.sock: Optional[socket.socket] = None
        self.connected = False

    def get_distances(self, header_length: int) -> List[float]:
        try:
            return self.read_frame(header_length)
        except Exception as e:
            self.logger.error(f"Error getting distances from {self.ip_address}: {e}")
            time.sleep(0.5)
            try:
                return self.read_frame(header_length)
            except Exception as e2:
                self.logger.error(f"Error getting distances after retry: {e2}")
                return []


    def read_frame(self, header_length: int) -> List[float]:
        if not self.connect():
            raise ConnectionError(f"Failed to connect to OAK camera at {self.ip_address}")

        try:
            header_data = self._receive_data(header_length)
            header = str(header_data, encoding="ascii")
            header_s = re.split(' +', header)

            if header_s[0] != "HEAD":
                self.close()
                raise ValueError(f"Invalid header format: {header}")

            message_length = int(header_s[1])
            message_data = self._receive_data(message_length)
            msg = str(message_data, encoding="ascii")

            distances = []
            dets = msg.split("|")
            for det in dets:
                if det.strip():  # Check if not empty
                    distances.append(float(det))

            self.close()
            return distances

        except (socket.timeout, socket.error) as e:
            self.logger.error(f"Socket error while reading frame from {self.ip_address}: {e}")
            self.connected = False
            self.close()
            raise

    def connect(self) -> bool:
        try:
            if self.sock:
                self.close()

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.ip_address, self.port))
            self.connected = True
            self.logger.info(f"Connected to OAK camera at {self.ip_address}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to OAK camera at {self.ip_address}: {e}")
            self.connected = False
            return False

    def _receive_data(self, length: int) -> bytes:
        chunks = []
        bytes_recd = 0
        while bytes_recd < length:
            chunk = self.sock.recv(min(length - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd += len(chunk)
        return b''.join(chunks)

    def close(self):
        if self.sock:
            try:
                self.sock.close()
                self.logger.debug(f"Connection to {self.ip_address} closed")
            except Exception as e:
                self.logger.error(f"Error closing socket: {e}")
            finally:
                self.sock = None
                self.connected = False
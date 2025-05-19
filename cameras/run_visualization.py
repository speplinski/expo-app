import socket
import re
import numpy as np
import cv2
import time
import argparse
import json
import os

DEFAULT_CONFIG = {
    "grid_size": {
        "nH": 22,
        "nV": 14
    },
    "camera_ips": {
        "left": "192.168.70.64",
        "center": "192.168.70.62",
        "right": "192.168.70.65"
    },
    "thresholds": {
        "left": {"min": 1.7, "max": 3.2},
        "center": {"min": 1.7, "max": 2.8},
        "right": {"min": 1.7, "max": 2.8}
    },
    "segments": {
        "horizontal": 3
    },
    "display": {
        "scale_factor": 30
    }
}

class CameraVisualizer:
    def __init__(self, config=None):
        if config is None:
            self.config = DEFAULT_CONFIG
        elif isinstance(config, str):
            with open(config, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = config
        
        self.nH = self.config["grid_size"]["nH"]
        self.nV = self.config["grid_size"]["nV"]
        
        self.cameras = {
            "left": {"ip": self.config["camera_ips"]["left"], "thresholds": self.config["thresholds"]["left"]},
            "center": {"ip": self.config["camera_ips"]["center"], "thresholds": self.config["thresholds"]["center"]},
            "right": {"ip": self.config["camera_ips"]["right"], "thresholds": self.config["thresholds"]["right"]}
        }
        
        self.segments_h = self.config["segments"]["horizontal"]
        self.scale_factor = self.config["display"]["scale_factor"]
        
        self.active_camera = "left"
    
    def read_frame(self, camera_ip, port=65432):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((camera_ip, port))
                
            HLEN = 32
            
            chunks = []
            bytes_recd = 0
            while bytes_recd < HLEN:
                chunk = sock.recv(min(HLEN - bytes_recd, 2048))
                if chunk == b'':
                    raise RuntimeError("socket connection broken")
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            header = str(b''.join(chunks), encoding="ascii")

            header_s = re.split(' +', header)
            if header_s[0] == "HEAD":
                MESLEN = int(header_s[1])
                
                chunks = []
                bytes_recd = 0
                while bytes_recd < MESLEN:
                    chunk = sock.recv(min(MESLEN - bytes_recd, 2048))
                    if chunk == b'':
                        raise RuntimeError("socket connection broken")
                    chunks.append(chunk)
                    bytes_recd = bytes_recd + len(chunk)
                msg = str(b''.join(chunks), encoding="ascii")
            
                distances = []
                dets = msg.split("|")
                for det in dets:
                    distances.append(float(det))
        
        return distances
    
    def check_segments_presence(self, heatmap1, heatmap2, heatmap3, mask1, mask2, mask3):
        result = [0] * (self.segments_h * 3)
        
        segment_width = self.nH // self.segments_h
        
        for ip_idx, mask in enumerate([mask1, mask2, mask3]):
            for seg_idx in range(self.segments_h):
                
                start_col = seg_idx * segment_width
                end_col = start_col + segment_width if seg_idx < self.segments_h-1 else self.nH
                
                segment_mask = mask[:, start_col:end_col]
                
                result_idx = ip_idx * self.segments_h + seg_idx
                
                if np.any(segment_mask):
                    result[result_idx] = 1
        
        return result

    def create_heatmap(self, distances1, distances2, distances3):
        heatmap1 = np.array(distances1).reshape(self.nV, self.nH)
        heatmap2 = np.array(distances2).reshape(self.nV, self.nH)
        heatmap3 = np.array(distances3).reshape(self.nV, self.nH)
        
        min_threshold1 = self.cameras["left"]["thresholds"]["min"]
        max_threshold1 = self.cameras["left"]["thresholds"]["max"]
        min_threshold2 = self.cameras["center"]["thresholds"]["min"]
        max_threshold2 = self.cameras["center"]["thresholds"]["max"]
        min_threshold3 = self.cameras["right"]["thresholds"]["min"]
        max_threshold3 = self.cameras["right"]["thresholds"]["max"]
        
        mask1 = (heatmap1 >= min_threshold1) & (heatmap1 <= max_threshold1)
        mask2 = (heatmap2 >= min_threshold2) & (heatmap2 <= max_threshold2)
        mask3 = (heatmap3 >= min_threshold3) & (heatmap3 <= max_threshold3)
        
        presence = self.check_segments_presence(heatmap1, heatmap2, heatmap3, mask1, mask2, mask3)
        
        heatmap = np.hstack((heatmap1, heatmap2, heatmap3))
        mask = np.hstack((mask1, mask2, mask3))
        
        min_dist = np.min(heatmap)
        max_dist = np.max(heatmap)
        normalized = ((heatmap - min_dist) / (max_dist - min_dist) * 255).astype(np.uint8)
        
        heatmap_colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        
        filtered_heatmap = heatmap_colored.copy()
        filtered_heatmap[~mask] = [0, 0, 0]
        
        heatmap_scaled = cv2.resize(filtered_heatmap,
                                 (3*self.nH * self.scale_factor, self.nV * self.scale_factor), 
                                 interpolation=cv2.INTER_NEAREST)
        
        segment_width = self.nH * self.scale_factor // self.segments_h
        
        for oak_idx in range(3):
            oak_x_start = oak_idx * self.nH * self.scale_factor
            
            for h_idx in range(1, self.segments_h):
                x = oak_x_start + h_idx * segment_width
                cv2.line(heatmap_scaled, (x, 0), (x, self.nV*self.scale_factor), (255, 255, 255), 1)
        
        for i in range(1, 3):
            x = i * self.nH * self.scale_factor
            cv2.line(heatmap_scaled, (x, 0), (x, self.nV*self.scale_factor), (255, 255, 255), 2)
        
        for y in range(self.nV):
            for x in range(3*self.nH):
                text_x = x * self.scale_factor + 5
                text_y = y * self.scale_factor + self.scale_factor//2
                distance = heatmap[y, x]
                
                text_color = (255, 255, 255)
                
                if x < self.nH:  # Left camera
                    if not mask1[y, x % self.nH]:
                        text_color = (128, 128, 128)
                elif x < 2*self.nH:  # Center camera
                    if not mask2[y, x % self.nH]:
                        text_color = (128, 128, 128)
                else:  # Right camera
                    if not mask3[y, x % self.nH]:
                        text_color = (128, 128, 128)
                
                cv2.putText(heatmap_scaled, f"{distance:.1f}", (text_x, text_y),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.3, text_color, 1)
        
        for segment_idx in range(9):
            oak_idx = segment_idx // self.segments_h
            segment_in_oak = segment_idx % self.segments_h
            
            segment_x = oak_idx * self.nH * self.scale_factor + segment_in_oak * segment_width + segment_width // 2
            segment_y = self.nV * self.scale_factor - 10
            
            color = (0, 255, 0) if presence[segment_idx] else (0, 0, 255)
            
            cv2.putText(heatmap_scaled, f"S{segment_idx+1}:{presence[segment_idx]}", 
                       (segment_x - 25, segment_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return heatmap_scaled, presence
    
    def save_config(self, filename):
        try:
            for cam_name in self.cameras:
                self.config["thresholds"][cam_name]["min"] = self.cameras[cam_name]["thresholds"]["min"]
                self.config["thresholds"][cam_name]["max"] = self.cameras[cam_name]["thresholds"]["max"]
                
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {filename}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def adjust_threshold(self, camera, direction, amount=0.1):
        if direction == 'up':
            self.cameras[camera]["thresholds"]["max"] += amount
            print(f"Increased maximum threshold for {camera} camera: {self.cameras[camera]['thresholds']['max']:.1f}")
        elif direction == 'down':
            min_threshold = self.cameras[camera]["thresholds"]["min"]
            max_threshold = self.cameras[camera]["thresholds"]["max"]
            new_max = max(min_threshold, max_threshold - amount)
            self.cameras[camera]["thresholds"]["max"] = new_max
            print(f"Decreased maximum threshold for {camera} camera: {new_max:.1f}")
    
    def run(self):
        print("Keyboard Controls:")
        print("  1 - select left camera for threshold adjustment")
        print("  2 - select center camera for threshold adjustment")
        print("  3 - select right camera for threshold adjustment")
        print("  z - decrease maximum threshold for active camera by 0.1")
        print("  x - increase maximum threshold for active camera by 0.1")
        print("  s - save current configuration")
        print("  q - quit program")
        
        while True:
            try:
                start_time = time.time()
                
                distances1 = self.read_frame(self.cameras["left"]["ip"])
                distances2 = self.read_frame(self.cameras["center"]["ip"])
                distances3 = self.read_frame(self.cameras["right"]["ip"])
                
                all_distances = distances1 + distances2 + distances3
                print(f"Frame read time: {time.time()-start_time:.3f}s")
                
                thresh_info = (
                    f"Left: min={self.cameras['left']['thresholds']['min']:.1f} "
                    f"max={self.cameras['left']['thresholds']['max']:.1f} | "
                    f"Center: min={self.cameras['center']['thresholds']['min']:.1f} "
                    f"max={self.cameras['center']['thresholds']['max']:.1f} | "
                    f"Right: min={self.cameras['right']['thresholds']['min']:.1f} "
                    f"max={self.cameras['right']['thresholds']['max']:.1f} | "
                    f"Active: {self.active_camera}"
                )
                print(thresh_info)
                
                heatmap, presence = self.create_heatmap(distances1, distances2, distances3)
                
                presence_text = f"Presence in segments: {presence}"
                print(presence_text)
                
                y_offset = 20
                for cam_name in ["left", "center", "right"]:
                    min_val = self.cameras[cam_name]["thresholds"]["min"]
                    max_val = self.cameras[cam_name]["thresholds"]["max"]
                    color = (0, 255, 255) if cam_name == self.active_camera else (255, 255, 255)
                    
                    cv2.putText(heatmap, f"{cam_name.capitalize()}: min={min_val:.1f} max={max_val:.1f}", 
                                (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                    y_offset += 20
                
                cv2.putText(heatmap, f"Active: {self.active_camera}", 
                            (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
                cv2.imshow("Depth Heatmap", heatmap)
                
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
                elif key == ord('1'):
                    self.active_camera = "left"
                    print(f"Selected left camera for threshold adjustment")
                elif key == ord('2'):
                    self.active_camera = "center"
                    print(f"Selected center camera for threshold adjustment")
                elif key == ord('3'):
                    self.active_camera = "right"
                    print(f"Selected right camera for threshold adjustment")
                elif key == ord('z'):
                    self.adjust_threshold(self.active_camera, 'down')
                elif key == ord('x'):
                    self.adjust_threshold(self.active_camera, 'up')
                elif key == ord('s'):
                    self.save_config("camera_visualization_config.json")
                    
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
        
        cv2.destroyAllWindows()

def parse_arguments():
    parser = argparse.ArgumentParser(description='OAK-D Camera Visualization')
    parser.add_argument('--config', help='Path to visualization configuration file')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    config_path = args.config
    if config_path and not os.path.isabs(config_path):
        config_path = os.path.abspath(config_path)
    
    visualizer = CameraVisualizer(config_path)
    visualizer.run()
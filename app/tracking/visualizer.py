import sys
import numpy as np
import cv2

from app.terminal_utils import TerminalUtils


class Visualizer:
    def __init__(self, config):
        self.config = config
        
    def create_buffer(self) -> list[list[str]]:
        """Create a buffer for storing previous state of the heatmap."""
        return [[" " for _ in range(self.config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT)] for _ in range(self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT)]

    def create_heatmap(self, distances, mirror=True):
        """Create a CV2 heatmap visualization of the depth data."""
        heatmap = np.array(distances).reshape(self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT, self.config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT)
        
        if mirror:
            heatmap = np.fliplr(heatmap)
        
        mask = (heatmap >= self.config.MIN_DISTANCE_THRESHOLD_IN_M) & (heatmap <= self.config.MAX_DISTANCE_THRESHOLD_IN_M)
        
        normalized = np.zeros_like(heatmap)
        normalized[mask] = ((heatmap[mask] - self.config.MIN_DISTANCE_THRESHOLD_IN_M) / 
                        (self.config.MAX_DISTANCE_THRESHOLD_IN_M - self.config.MIN_DISTANCE_THRESHOLD_IN_M) * 255)
        normalized = normalized.astype(np.uint8)
        
        heatmap_colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        heatmap_colored[~mask] = [0, 0, 0]
        
        scale_factor = 80
        heatmap_scaled = cv2.resize(heatmap_colored, 
                                (self.config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT * scale_factor, self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT * scale_factor), 
                                interpolation=cv2.INTER_NEAREST)
        
        return heatmap_scaled

    def create_console_heatmap(self, distances, prev_buffer, mirror=True):
        """Create and update console-based heatmap visualization."""
        heatmap = np.array(distances).reshape(self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT, self.config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT)
        
        if mirror:
            heatmap = np.fliplr(heatmap)
        
        mask = (heatmap >= self.config.MIN_DISTANCE_THRESHOLD_IN_M) & (heatmap <= self.config.MAX_DISTANCE_THRESHOLD_IN_M)
        normalized = np.zeros_like(heatmap, dtype=float)
        normalized[mask] = ((heatmap[mask] - self.config.MIN_DISTANCE_THRESHOLD_IN_M) /
                        (self.config.MAX_DISTANCE_THRESHOLD_IN_M - self.config.MIN_DISTANCE_THRESHOLD_IN_M))
        
        chars = ' ░▒▓█'
        current_buffer = [[" " for _ in range(self.config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT)] for _ in range(self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT)]
        
        if all(all(cell == " " for cell in row) for row in prev_buffer):
            print("\033[2J")  # Clear screen
            print("\033[?25l")  # Hide cursor
            
            # Draw frame
            TerminalUtils.move_cursor(1, 1)
            print("┏" + "━" * (self.config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT * 2) + "┓")
            for i in range(self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT):
                TerminalUtils.move_cursor(1, i + 2)
                print("┃" + " " * (self.config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT * 2) + "┃")
            TerminalUtils.move_cursor(1, self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT + 2)
            print("┗" + "━" * (self.config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT * 2) + "┛")
            
            # Print legend and controls
            TerminalUtils.move_cursor(1, self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT + 4)
            print(f"Range: {self.config.MIN_DISTANCE_THRESHOLD_IN_M:.1f}m to {self.config.MAX_DISTANCE_THRESHOLD_IN_M:.1f}m")
            TerminalUtils.move_cursor(1, self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT + 5)
            print("Controls:")
            TerminalUtils.move_cursor(1, self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT + 6)
            print("  'q' - Exit")
            TerminalUtils.move_cursor(1, self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT + 7)
            print("  'w' - Toggle window")
            TerminalUtils.move_cursor(1, self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT + 8)
            print("  's' - Toggle stats")
            TerminalUtils.move_cursor(1, self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT + 9)
            print("  'm' - Toggle mirror mode")

        for i in range(self.config.DEPTH_GRID_VERTICAL_SEGMENTS_COUNT):
            for j in range(self.config.DEPTH_GRID_HORIZONTAL_SEGMENTS_COUNT):
                if mask[i, j]:
                    char_idx = int(normalized[i, j] * (len(chars) - 1))
                    current_char = chars[char_idx]
                else:
                    current_char = " "
                
                current_buffer[i][j] = current_char
                
                if current_char != prev_buffer[i][j]:
                    TerminalUtils.move_cursor(j * 2 + 2, i + 2)
                    sys.stdout.write(f"\033[94m{current_char}\033[0m ")
                    sys.stdout.flush()
        
        return current_buffer
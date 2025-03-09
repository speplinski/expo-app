import numpy as np

class VisitorSimulation:
    def __init__(self, y: float, x: float, height: float, angle: float):
        self.y = y
        self.x = x
        self.height = height
        self.dy = np.sin(angle)
        self.dx = np.cos(angle)
        self.is_moving = True
        self.is_leaving = False

    def move(self, step_distance: float):
        if self.is_moving:
            self.y += self.dy * step_distance
            self.x += self.dx * step_distance

    def change_direction(self):
        angle = np.random.uniform(0, 2*np.pi)
        self.dy = np.sin(angle)
        self.dx = np.cos(angle)

    def start_leaving(self, grid_shape: tuple[int, int]):
        self.is_leaving = True
        self.is_moving = True

        dist_to_left = self.x
        dist_to_right = grid_shape[1] - 1 - self.x
        dist_to_top = self.y
        dist_to_bottom = grid_shape[0] - 1 - self.y
        min_dist = min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom)

        if min_dist == dist_to_left:
            self.dx, self.dy = -1, 0
        elif min_dist == dist_to_right:
            self.dx, self.dy = 1, 0
        elif min_dist == dist_to_top:
            self.dx, self.dy = 0, -1
        else:
            self.dx, self.dy = 0, 1

    def is_out_of_bounds(self, grid_shape: tuple[int, int]) -> bool:
        return (self.y < 0 or self.y >= grid_shape[0] or
                self.x < 0 or self.x >= grid_shape[1])
import numpy as np

class OakDSimulation:
    def __init__(self, horizontal_segments_count, vertical_segments_count):
        self.distances = np.zeros((vertical_segments_count, horizontal_segments_count))

    def get_distances(self):
        return self.distances.flatten()

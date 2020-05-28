# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------

import numpy as np
from typing import Tuple


class GridTopology:
    def __init__(self, bounding_box: np.array, threshold: int, max_crime_count: int,
                 grid_resolution: Tuple[float, float], bin_dimensions: Tuple[int, int]):

        self.bounding_box = bounding_box
        self.grid_resolution = grid_resolution
        self.threshold = threshold
        self.max_crime_count = max_crime_count
        self.bin_dimensions = bin_dimensions

    def calculate_extents(self) -> np.array:
        return [self.bounding_box[0], self.bounding_box[2], self.bounding_box[1], self.bounding_box[3]]
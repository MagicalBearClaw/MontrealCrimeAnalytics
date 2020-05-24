# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------

import numpy as np
import pandas as pd
import shapefile

from src.CrimeGridInfo import CrimeGridInfo
from typing import Tuple


class CrimeRateInfoGenerator:

    def __init__(self):
        self._data_frame = None
        self._bounding_box = None

    def initialize(self, file_name: str) -> None:
        crime_dt_shape_file = shapefile.Reader(file_name, encoding='latin-1')
        self._bounding_box = crime_dt_shape_file.bbox
        crime_data_shape = [s.points[0] for s in crime_dt_shape_file.shapes()]
        crime_data_array = np.array(crime_data_shape)
        self._data_frame = pd.DataFrame({'longitude': crime_data_array[:, 0], 'latitude': crime_data_array[:, 1]})

    def create_crime_grid_info(self, grid_resolution: Tuple[float, float]) -> CrimeGridInfo:
        return CrimeGridInfo(grid_resolution, self._bounding_box, self._data_frame.copy(deep=True))

# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------

import numpy as np
import pandas as pd

from src.GridTopology import GridTopology
from typing import Tuple, List, Iterable


class CrimeGridInfo:
    def __init__(self, grid_resolution: Tuple[float, float], bonding_box: np.array, data_frame: pd.DataFrame):
        self.grid_resolution = grid_resolution
        self.bounding_box = bonding_box
        self._epsilon = float(0.0000759)
        self._data_frame = data_frame
        self.bin_dimensions = self.__calculate_bin_shape()
        self.__partition_grid()

    def __calculate_bin_shape(self) -> Tuple[int, int]:
        delta_x, delta_y = self.__get_bbox_dimensions()
        x_resolution, y_resolution = self.grid_resolution
        columns = np.ceil(delta_x / x_resolution)
        rows = np.ceil(delta_y / y_resolution)
        return int(rows), int(columns)

    def __get_bbox_dimensions(self) -> Tuple[float, float]:
        delta_x = np.abs(self.bounding_box[2] - self.bounding_box[0])
        delta_y = np.abs(self.bounding_box[3] - self.bounding_box[1])
        return delta_x, delta_y

    def __partition_grid(self) -> None:
        self._data_frame['cell'] = self.__get_cell_for_point()

    # vectorized implementation of calculating the cell from a point using interpolation
    def __get_cell_for_point(self) -> List[Tuple[int, int]]:
        rows, columns = self.bin_dimensions
        delta_x, delta_y = self.__get_bbox_dimensions()
        cells_x = np.abs(np.floor((self._data_frame['longitude'].values - self.bounding_box[0] - self._epsilon)
                                  / delta_x * columns))
        cells_y = np.abs(np.floor((self._data_frame['latitude'].values - self.bounding_box[1] - self._epsilon)
                                  / delta_y * rows))
        return list(zip(cells_x, cells_y))

    def get_cell_from_point(self, point: Tuple[float, float]):
        rows, columns = self.bin_dimensions
        delta_x, delta_y = self.__get_bbox_dimensions()
        x, y = point
        cells_x = np.abs(np.floor((x - self.bounding_box[0] - self._epsilon) / delta_x * columns))
        cells_y = np.abs(np.floor((y - self.bounding_box[1] - self._epsilon) / delta_y * rows))
        return int(cells_x), int(cells_y)

    def __get_crime_count_per_cell(self) -> pd.DataFrame:
        df = self._data_frame.groupby(['cell']).count().rename(columns={"longitude": "count"}) \
            .drop(columns={"latitude"})
        df['cell'] = df.index
        return df

    def generate_grid_dict(self, grid: np.array, threshold):
        grid_dict = dict(((j, i), grid[i][j]) for i in range(len(grid)) for j in range(len(grid[0])))
        for key in grid_dict:
            grid_dict[key] = grid_dict[key] >= threshold
        return grid_dict

    def generate_grid(self, threshold_percentage: int) -> Tuple[np.array, GridTopology]:
        # returns the modified data frame where the index is the cell coordinates(x, y) with the crime count as a column
        self._data_frame = self.__get_crime_count_per_cell()
        rows, columns = self.bin_dimensions

        # creates the grid of N x N cells
        grid = self.__create_grid_data(rows, columns, self._data_frame)
        # get the index to find the crime count threshold to determine high crime cells
        index = int(np.floor((rows * columns) * (1 - (threshold_percentage / 100)))) - 1

        crime_count_threshold = np.NAN
        max_crime_count = np.NaN

        # when a threshold percentage is at a 100% we get an index of -1 since there is no low crime rates
        # so we do not need to find our crime rate threshold to determine if a cell is low or high crime.
        if index != -1:
            sorted_flatten = np.sort(grid.flatten())[::-1]
            max_crime_count = sorted_flatten[0]
            crime_count_threshold = sorted_flatten[index]

        # create the topology information of the grid
        grid_topology = GridTopology(self.bounding_box, crime_count_threshold,
                                     max_crime_count, self.grid_resolution, self.bin_dimensions)

        return grid, grid_topology

    def __create_grid_data(self, rows: int, columns: int, df: pd.DataFrame) -> np.array:
        grid = np.zeros((rows, columns))

        # function used to insert crime counts into the appropriate cell in the grid
        def insert_cell_data_into_grid(cell: Tuple[int, int], count: int, g: np.array) -> None:
            r, c = cell
            g[int(c), int(r)] = count

        df.apply(lambda r: insert_cell_data_into_grid(r['cell'], r['count'], grid), axis=1)
        return grid

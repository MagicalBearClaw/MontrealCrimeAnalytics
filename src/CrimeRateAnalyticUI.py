# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------
from typing import Tuple

import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.image import AxesImage
from matplotlib.widgets import Slider, Button, TextBox, Cursor
import numpy as np
from src.CrimeGridInfo import CrimeGridInfo
from src.CrimeRateGridGenerator import CrimeRateInfoGenerator
from matplotlib.lines import Line2D
import matplotlib.patches as patches

from src.CrimeStatisticCalculator import CrimeStatisticCalculator
from src.DisconnectedGraph import DisconnectedGraph


class CrimeRateAnalyticUI:

    def __init__(self):
        self._crime_rate_info_generator = CrimeRateInfoGenerator()
        self._crime_rate_info_generator.initialize('../data/crime_dt.shp')
        self._default_threshold_percentage = 50
        self._default_grid_resolution = (0.002, 0.002)
        self._start_node_id: int = -1
        self._end_node_id: int = -1
        self.crime_grid_info = None
        self._grid_topology = None
        self._grid = None
        self._start_path_circle = None
        self._end_path_circle = None
        self._grid_dict = None
        self._console_text = None
        self._console_text_data = ""
        self._disconnected_graph = None

    def start_application(self) -> None:
        self.crime_grid_info = self._crime_rate_info_generator.create_crime_grid_info(self._default_grid_resolution)
        self._grid, self._grid_topology = self.crime_grid_info.generate_grid(self._default_threshold_percentage)
        self._disconnected_graph = DisconnectedGraph(self._grid, self._grid_topology)
        self._disconnected_graph.build_graph_from_grid()
        self.__display(self._grid, self._grid_topology.calculate_extents(), self._grid_topology.threshold,
                       self._grid_topology.max_crime_count, 0)

    def __display(self, grid: np.array, extents: np.array, threshold: int, max_count: int, xticks) -> None:

        self._fig: plt.Figure = plt.figure(figsize=(11, 11))
        self._plot: plt.Axes = self._fig.add_subplot(111)
        plt.subplots_adjust(bottom=0.35)

        self._plot.set_title('Montreal Crime Analytics A*', pad=10)
        self._im: AxesImage = self._plot.imshow(grid, interpolation='none', aspect='equal', origin='lower')
        self.__load(grid, threshold, max_count, extents)
        self.__create_widgets()
        self._fig.canvas.mpl_connect('button_press_event', self.__on_grid_click)
        self.__display_statistics(grid.flatten())
        plt.show()

    def __load(self, grid: np.array, threshold: int, max_count: int, extents: np.array) -> None:
        cmap = colors.ListedColormap(['purple', 'yellow'])
        bounds = [0, threshold, max_count]
        norm = colors.BoundaryNorm(bounds, cmap.N)
        self._im.set_data(grid)
        self._im.set_extent(extents)
        self._im.set_cmap(cmap)
        self._im.set_norm(norm)
        self._grid_dict = self.crime_grid_info.generate_grid_dict(grid, threshold)

    def __create_widgets(self) -> None:
        self.__create_slider_widget()
        self.__create_grid_resolution_input()
        self.__create_console()
        reset_btn_axes = plt.axes([0.68, 0.020, 0.1, 0.045])
        self._reset_btn = Button(reset_btn_axes, 'Reset')
        self._reset_btn.on_clicked(self.__reset)
        update_btn_axes = plt.axes([0.57, 0.020, 0.1, 0.045])
        self._update_btn = Button(update_btn_axes, 'Update Grid')
        self._update_btn.on_clicked(self.__update)
        path_btn_axes = plt.axes([0.46, 0.020, 0.1, 0.045])
        self._path_btn = Button(path_btn_axes, 'Find Path')
        self._path_btn.on_clicked(self.__find_path)

    def __create_slider_widget(self) -> None:
        self.threshold_axes = plt.axes([0.80, 0.35, 0.03, 0.53], facecolor='purple')
        self._threshold_slider: plt.Slider = Slider(self.threshold_axes, 'Threshold:', 0.0, 100.0,
                                                    valinit=self._default_threshold_percentage,
                                                    valstep=1.0, orientation='vertical', color='yellow')

    def __display_statistics(self, data: np.ndarray) -> None:
        statistic_calculator = CrimeStatisticCalculator(data)
        self._console_text_data = f'The mean is {statistic_calculator.calculate_mean()} \n' \
                                  f'The median is {statistic_calculator.calculate_median()} \n' \
                                  f'The standard deviation is {statistic_calculator.calculate_std()} \n'

        self._console_text.set_text(self._console_text_data)

    def __create_grid_resolution_input(self) -> None:
        res_x, res_y = self._default_grid_resolution
        self._grid_x_axes_text_Box = plt.axes([0.35, 0.295, 0.15, 0.020])
        self._grid_x_text_box: TextBox = TextBox(self._grid_x_axes_text_Box, "Res X:  ", str(res_x))
        self._grid_y_axes_text_Box = plt.axes([0.57, 0.295, 0.15, 0.020])
        self._grid_y_text_box: TextBox = TextBox(self._grid_y_axes_text_Box, "Res Y:  ", str(res_y))

    def __create_console(self) -> None:
        text_axes: plt.Axes = plt.axes([0.250, 0.08, 0.53, 0.2], frameon=False)
        text_axes.set_axis_off()
        r = patches.Rectangle((0, 0), 1, 1, facecolor='black')
        text_axes.add_artist(r)
        self._console_text = text_axes.annotate(self._console_text_data, (0.02, 0.70), color='white')

    def __reset(self, event) -> None:
        self._threshold_slider.set_val(self._default_threshold_percentage)
        res_x, res_y = self._default_grid_resolution
        self._grid_x_text_box.set_val(str(res_x))
        self._grid_y_text_box.set_val(str(res_y))
        self._console_text.set_text('')
        self.__update_grid(self._default_grid_resolution, self._default_threshold_percentage)
        if self._start_path_circle is not None:
            self._start_path_circle.remove()
        if self._end_path_circle is not None:
            self._end_path_circle.remove()
        self.__display_statistics(self._grid.flatten())
        self._fig.canvas.draw()

    def __update(self, event) -> None:
        try:
            res_x = float(self._grid_x_text_box.text)
            res_y = float(self._grid_y_text_box.text)
            grid_resolution = (res_x, res_y)
        except ValueError:
            grid_resolution = self._default_grid_resolution
            res_x, res_y = grid_resolution
            self._grid_x_text_box.set_val(str(res_x))
            self._grid_y_text_box.set_val(str(res_y))

        self.__update_grid(grid_resolution, int(self._threshold_slider.val))
        self.__display_statistics(self._grid.flatten())
        self._fig.canvas.draw()

    def __update_grid(self, grid_resolution: Tuple[float, float], threshold: int) -> None:
        self.crime_grid_info = self._crime_rate_info_generator.create_crime_grid_info(grid_resolution)
        self._grid, self._grid_topology = self.crime_grid_info.generate_grid(threshold)
        self._disconnected_graph = DisconnectedGraph(self._grid, self._grid_topology)
        self._disconnected_graph.build_graph_from_grid()
        self.__load(self._grid, self._grid_topology.threshold, self._grid_topology.max_crime_count,
                    self._grid_topology.calculate_extents())

    def __find_path(self, event) -> None:
        pass

    def __calculate_distance_between_points(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        x1, y1 = p1
        x2, y2 = p2
        return ((x2 - x1) ** 2) + ((y2 - y1) ** 2)

    def __calculate_coordinates_from_cell(self, cell: Tuple[int, int], raw_point: Tuple[float, float]) \
            -> Tuple[float, float]:
        x, y = cell
        res_x, res_y = self._grid_topology.grid_resolution
        x_min, y_min = self._grid_topology.bounding_box[0], self._grid_topology.bounding_box[1]

        left_bottom_corner_x = x_min + (x * res_x)
        left_bottom_corner_y = y_min + (y * res_y)

        right_bottom_corner_x = x_min + ((x + 1) * res_x)
        right_bottom_corner_y = y_min + (y * res_y)

        left_top_corner_x = x_min + (x * res_x)
        left_top_corner_y = y_min + ((y + 1) * res_y)

        right_top_corner_x = x_min + ((x + 1) * res_x)
        right_top_corner_y = y_min + ((y + 1) * res_y)

        coordinates_dict = dict()
        coordinates_dict[0] = (left_bottom_corner_x, left_bottom_corner_y)
        coordinates_dict[1] = (right_bottom_corner_x, right_bottom_corner_y)
        coordinates_dict[2] = (left_top_corner_x, left_top_corner_y)
        coordinates_dict[3] = (right_top_corner_x, right_top_corner_y)

        left_bottom_distance = self.__calculate_distance_between_points(coordinates_dict[0],
                                                                        raw_point)
        right_bottom_distance = self.__calculate_distance_between_points(coordinates_dict[1],
                                                                         raw_point)
        left_top_distance = self.__calculate_distance_between_points(coordinates_dict[2],
                                                                     raw_point)
        right_top_distance = self.__calculate_distance_between_points(coordinates_dict[3],
                                                                      raw_point)

        shortest_distance_index = np.argmin([left_bottom_distance, right_bottom_distance, left_top_distance,
                                             right_top_distance])

        return coordinates_dict[shortest_distance_index]



    def __on_grid_click(self, event) -> None:
        axes = event.inaxes
        if self._plot != axes:
            return None

        x_cord, y_cord = event.xdata, event.ydata
        cell = self.crime_grid_info.get_cell_from_point((x_cord, y_cord))
        is_blocked = self._grid_dict.get(cell)
        if not is_blocked:
            # calculate the nearest corner to place our start or end point
            cord = self.__calculate_coordinates_from_cell(cell, (x_cord, y_cord))

            if self._start_node_id != -1 and self._end_node_id != -1:
                self._start_path_circle.remove()
                self._end_path_circle.remove()
                self._start_path_circle: plt.Circle = plt.Circle(cord, 0.00025, color='green', clip_on=False)
                self._plot.add_artist(self._start_path_circle)
                self._end_node_id = -1
                self._start_node_id = 1
            elif self._start_node_id != -1:
                self._end_path_circle: plt.Circle = plt.Circle(cord, 0.00025, color='red', clip_on=False)
                end_center = self._end_path_circle.get_center()
                start_center = self._start_path_circle.get_center()
                if end_center == start_center:
                    return None
                self._plot.add_artist(self._end_path_circle)
                self._end_node_id = 1
            else:
                self._start_path_circle: plt.Circle = plt.Circle(cord, 0.00025, color='green', clip_on=False)
                self._plot.add_artist(self._start_path_circle)
                self._start_node_id = 1
            self._fig.canvas.draw()

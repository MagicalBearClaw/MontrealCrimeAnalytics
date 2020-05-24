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

    def start_application(self) -> None:
        self.crime_grid_info = self._crime_rate_info_generator.create_crime_grid_info(self._default_grid_resolution)
        self._grid, self._grid_topology = self.crime_grid_info.generate_grid(self._default_threshold_percentage)
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
        self._fig.canvas.mpl_connect('button_press_event', self.__on_click)
        plt.show()

    def __load(self, grid: np.array, threshold: int, max_count: int, extents: np.array) -> None:
        cmap = colors.ListedColormap(['purple', 'yellow'])
        bounds = [0, threshold, max_count]
        norm = colors.BoundaryNorm(bounds, cmap.N)
        self._im.set_data(grid)
        self._im.set_extent(extents)
        self._im.set_cmap(cmap)
        self._im.set_norm(norm)

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
        self.threshold_axes = plt.axes([0.80, 0.35, 0.03, 0.53], facecolor='yellow')
        self._threshold_slider: plt.Slider = Slider(self.threshold_axes, 'Threshold:', 0.0, 100.0, valinit=50,
                                                    valstep=1.0, orientation='vertical', color='purple')

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
        self._console_text = text_axes.annotate('', (0.02, 0.85), color='white')

    def __reset(self, event) -> None:
        self._threshold_slider.set_val(self._default_threshold_percentage)
        res_x, res_y = self._default_grid_resolution
        self._grid_x_text_box.set_val(str(res_x))
        self._grid_y_text_box.set_val(str(res_y))
        self._console_text.set_text('')
        self.__update_grid(self._default_grid_resolution, self._default_threshold_percentage)
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
        self._fig.canvas.draw()

    def __update_grid(self, grid_resolution: Tuple[float, float], threshold: int) -> None:
        self.crime_grid_info = self._crime_rate_info_generator.create_crime_grid_info(grid_resolution)
        self._grid, self._grid_topology = self.crime_grid_info.generate_grid(threshold)
        self.__load(self._grid, self._grid_topology.threshold, self._grid_topology.max_crime_count,
                    self._grid_topology.calculate_extents())

    def __find_path(self, event) -> None:
        pass

    def __on_click(self, event) -> None:
        print(event)
        x_cord, y_cord = event.xdata, event.ydata
        cell_x, cell_y = cell = self.crime_grid_info.get_cell_from_point((x_cord, y_cord))
        print(f'cell_x: {cell_x}, cell_y: {cell_y}')
        is_blocked = self.crime_grid_info.is_cell_blocked(cell, self._grid_topology.threshold)
        if not is_blocked:
            if self._start_node_id != -1:
                pass
            else:
                pass
# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------

from src.Node import Node
from typing import Dict, Tuple
import numpy as np

from src.GridTopology import GridTopology


class DisconnectedGraph:
    def __init__(self, grid: np.ndarray, grid_topology: GridTopology):
        self._node_dict: Dict[int, Node] = dict()
        self._grid_topology = grid_topology
        self._epsilon = float(0.0000759)
        self._diagonal_weight = 1.5
        self._shared_edge_weight = 1.3
        self._edge_weight = 1
        self._grid = grid

    def build_graph_from_grid(self) -> Dict[int, Node]:
        # build the graph by using a dictionary as the backing data structure.
        # used handles(ids) as a keys to associate to a node.
        rows, columns = self._grid_topology.bin_dimensions
        boundaries = self._grid_topology.bounding_box[0], \
                                                  self._grid_topology.bounding_box[1], \
                                                  self._grid_topology.bounding_box[2], \
                                                  self._grid_topology.bounding_box[3]
        for c in range(columns):
            for r in range(rows):
                # the node is blocked, so we skip it
                if self._grid[c, r] >= self._grid_topology.threshold:
                    continue

                self.create_node_connections_for_cell(c, r, boundaries)

        return self._node_dict

    def create_node_connections_for_cell(self, x: int, y: int,
                                         grid_boundaries: Tuple[float, float, float, float]) -> None:

        # each cell has up to 4 nodes. we must create them if they are not already created. We also do bi-directional
        # connections. We respect that we cannot two nodes that are on a boundary edge.

        x_min, y_min, x_max, y_max = grid_boundaries
        rows, columns = self._grid_topology.bin_dimensions
        res_x, res_y = self._grid_topology.grid_resolution
        # whenever we are ina  new cell we process nodes in a counter clockwise fashion starting at the bottom left
        # node

        # we need to do + 1 for rows since we are processing the vertices of the cells.
        vertex_rows = rows + 1

        # left bottom node
        current_lb_node_index = (x * vertex_rows) + y
        current_lb_node = self._node_dict.get(current_lb_node_index)
        # the node does not exist so we need toc create it.

        # when calculating the coordinates of the nodes when need to flip
        # x and y because y represent the current column and x represent the row
        # in order to get the correct position we need to do this flip

        # left bottom node
        if current_lb_node is None:
            current_lb_node = Node(current_lb_node_index)
            # create the current node
            # calculate the nodes real coordinates
            left_bottom_corner_x = x_min + (y * res_x)
            left_bottom_corner_y = y_min + (x * res_y)
            current_lb_node.cod_x = left_bottom_corner_x
            current_lb_node.cod_y = left_bottom_corner_y
            self._node_dict[current_lb_node_index] = current_lb_node

        # left top node
        current_lt_node_index = ((x+1) * vertex_rows) + y
        current_lt_node = self._node_dict.get(current_lt_node_index)
        # the node does not exist so we need toc create it.
        if current_lt_node is None:
            current_lt_node = Node(current_lt_node_index)
            # create the current node
            # calculate the nodes real coordinates
            left_bottom_corner_x = x_min + (y * res_x)
            left_bottom_corner_y = y_min + ((x + 1) * res_y)
            current_lt_node.cod_x = left_bottom_corner_x
            current_lt_node.cod_y = left_bottom_corner_y
            self._node_dict[current_lt_node_index] = current_lt_node

        # right top node
        current_rt_node_index = ((x+1) * vertex_rows) + y + 1
        current_rt_node = self._node_dict.get(current_rt_node_index)
        # the node does not exist so we need toc create it.
        if current_rt_node is None:
            current_rt_node = Node(current_rt_node_index)
            # create the current node
            # calculate the nodes real coordinates
            left_bottom_corner_x = x_min + ((y + 1) * res_x)
            left_bottom_corner_y = y_min + ((x + 1) * res_y)
            current_rt_node.cod_x = left_bottom_corner_x
            current_rt_node.cod_y = left_bottom_corner_y
            self._node_dict[current_rt_node_index] = current_rt_node

        # right bottom node
        current_rb_node_index = (x * vertex_rows) + y + 1
        current_rb_node = self._node_dict.get(current_rb_node_index)
        # the node does not exist so we need toc create it.
        if current_rb_node is None:
            current_rb_node = Node(current_rb_node_index)
            # create the current node
            left_bottom_corner_x = x_min + ((y + 1) * res_x)
            left_bottom_corner_y = y_min + (x * res_y)
            current_rb_node.cod_x = left_bottom_corner_x
            current_rb_node.cod_y = left_bottom_corner_y
            self._node_dict[current_rb_node_index] = current_rb_node

        # create bi-directional diagonal connection from left bottom to right top node
        if not current_lb_node.is_connected_to(current_rt_node_index):
            current_lb_node.connect_to_node(self._diagonal_weight, current_rt_node_index)
            if not current_rt_node.is_connected_to(current_lb_node_index):
                current_rt_node.connect_to_node(self._diagonal_weight, current_lb_node_index)

        # create bi-directional diagonal connection from right bottom to left top node
        if not current_lt_node.is_connected_to(current_rb_node_index):
            current_lt_node.connect_to_node(self._diagonal_weight, current_rb_node_index)
            if not current_rb_node.is_connected_to(current_lt_node_index):
                current_rb_node.connect_to_node(self._diagonal_weight, current_lt_node_index)

        # left -> right and we are not at the left edge of the grid
        # if we are at column 0 we can not process the left edge of the grid.
        # we cannot connect the bottom left node to the top left node together.
        if y != 0:
            weight = self._edge_weight
            if self._grid[x, y - 1] >= self._grid_topology.threshold:
                weight = self._shared_edge_weight
            if not current_lb_node.is_connected_to(current_lt_node_index):
                current_lb_node.connect_to_node(weight, current_lt_node_index)
            if not current_lt_node.is_connected_to(current_lb_node_index):
                current_lt_node.connect_to_node(weight, current_lb_node_index)

        # bottom -> up and we are not at the bottom edge of the grid
        # if we are at row 0 we can not process the bottom edge of the grid.
        # we cannot connect the bottom left node to the bottom right node together.
        if x != 0:
            weight = self._edge_weight
            if self._grid[x - 1, y] >= self._grid_topology.threshold:
                weight = self._shared_edge_weight
            if not current_lb_node.is_connected_to(current_rb_node_index):
                current_lb_node.connect_to_node(weight, current_rb_node_index)
            if not current_rb_node.is_connected_to(current_lb_node_index):
                current_rb_node.connect_to_node(weight, current_lb_node_index)

        # right -> left and we are not at the right edge of the grid
        # if we are at len(columns) - 1 we can not process the right edge of the grid.
        # we cannot connect the bottom right node to the top right node together.
        if y != (columns-1):
            weight = self._edge_weight
            if self._grid[x, y + 1] >= self._grid_topology.threshold:
                weight = self._shared_edge_weight
            if not current_rb_node.is_connected_to(current_rt_node_index):
                current_rb_node.connect_to_node(weight, current_rt_node_index)
            if not current_rt_node.is_connected_to(current_rb_node_index):
                current_rt_node.connect_to_node(weight, current_rb_node_index)

        # top -> bottom and we are not at the top edge of the grid
        # if we are at len(rows) - 1 we can not process the top edge of the grid.
        # we cannot connect the top left node to the top right node together.
        if x != (rows - 1):
            weight = self._edge_weight
            if self._grid[x + 1, y] >= self._grid_topology.threshold:
                weight = self._shared_edge_weight
            if not current_lt_node.is_connected_to(current_rt_node_index):
                current_lt_node.connect_to_node(weight, current_rt_node_index)
            if not current_rt_node.is_connected_to(current_lt_node_index):
                current_rt_node.connect_to_node(weight, current_lt_node_index)

    def get_node(self, node_id: int):
        return self._node_dict.get(node_id)

    def __get_cell_from_point(self, grid_dimensions: Tuple[int, int], point: Tuple[float, float]):
        # given a point get the current cell of that grid that it exists in.
        rows, columns = grid_dimensions
        delta_x, delta_y = self.__get_bbox_dimensions()
        bbox = self._grid_topology.bounding_box
        x, y = point
        cells_x = np.abs(np.floor((x - bbox[0] - self._epsilon) / delta_x * columns))
        cells_y = np.abs(np.floor((y - bbox[1] - self._epsilon) / delta_y * rows))
        return int(cells_x), int(cells_y)

    def __get_bbox_dimensions(self) -> Tuple[float, float]:
        bbox = self._grid_topology.bounding_box
        delta_x = np.abs(bbox[2] - bbox[0])
        delta_y = np.abs(bbox[3] - bbox[1])
        return delta_x, delta_y

# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------
from src.Graph import Node, Edge
from typing import Dict
import numpy as np


class DisconnectedGraph:
    def __init__(self):
        self._node_dict: Dict[int, Node] = dict()
        self._edge_dict: Dict[int, Edge] = dict()

    def build_graph_from_grid(self, grid: np.array):
        pass

    def get_node(self, node_id: int):
        pass

    def get_edge(self, start_node_id: int, end_node_id: int):
        pass

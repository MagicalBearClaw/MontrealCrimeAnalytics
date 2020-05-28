# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------

# Node class used by the DisconnectedGraph class

class Node:
    def __init__(self, node_id: int = -1):
        self.id: int = node_id
        self.cod_x = -1
        self.cod_y = -1
        self.cord = lambda: self.cod_x, self.cod_y
        self._connected_nodes = dict()
        self.parent = None
        self.g_score = 0
        self.h_score = 0
        self.f_score = 0

    def connect_to_node(self, weight: float, node_id: int) -> None:
        self._connected_nodes[node_id] = weight

    def is_connected_to(self, node_id: int) -> bool:
        return self._connected_nodes.get(node_id) is not None

    def get_neighbours(self):
        return self._connected_nodes

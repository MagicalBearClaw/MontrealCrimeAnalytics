# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------


class Node:
    def __init__(self):
        # our id, whether or not we are a block, and the weight of the node
        self.id: int = -1
        self._is_block: bool = False
        self.weight = 0
        # handles to other nodes
        self.bottom_ref: int = -1
        self.top_ref: int = -1
        self.left_ref: int = -1
        self.right_ref: int = -1
        self.top_right_ref: int = -1
        self.bottom_right_ref: int = -1
        self.bottom_left_ref: int = -1
        self.top_left_ref: int = -1

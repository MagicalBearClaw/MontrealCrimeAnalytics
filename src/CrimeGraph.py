# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------
from src.Node import Node
from typing import Dict


class CrimeGraph:
    def __init__(self):
        self._node_dict: Dict[int, Node] = dict()

# -------------------------------------------------------
# Assignment #1 Montreal Crime Analytics
# Written by Michael McMahon - 26250912
# For COMP 472 Section ABJX – Summer 2020
# --------------------------------------------------------
import time
from queue import PriorityQueue
from threading import Event, Thread
from typing import Dict, List

from src.Node import Node


class AStar:
    def __init__(self, timeout_seconds: int):
        self._graph = None
        self._open_list = PriorityQueue()
        self._open_set = set()
        self._closed_list = set()
        self._timeout_seconds = timeout_seconds
        self._stop_event = Event()
        self._path = list()
        self._start_node_id = -1
        self._end_node_id = -1

    def find_path(self, start_node_id: int, end_node_id: int):
        # reset a* state
        self.__reset_node_in_graph()
        self._path = list()
        self._open_list = PriorityQueue()
        self._open_set = set()
        self._closed_list = set()
        self._start_node_id = start_node_id
        self._end_node_id = end_node_id

        # launch the a* algorithm in a separate thread
        action_thread = Thread(target=self.__find_path_worker)

        # star the execution timer
        start_time = time.time()
        # start the thread, there is a cost in launching an starting a thread
        action_thread.start()
        # if the thread takes longer than the timeout to find a path than we suspend the thread.
        action_thread.join(timeout=self._timeout_seconds)
        elapsed_time_ms = (time.time() - start_time) * 1000
        if action_thread.is_alive():
            # We send a signal that the other thread should stop.
            self._stop_event.set()

        # return how long it took to execute the a* and the path it found.
        return elapsed_time_ms, self._path

    def __find_path_worker(self):
        # get the nodes bu id in the graph.
        start_node: Node = self._graph[self._start_node_id]
        end_node: Node = self._graph[self._end_node_id]

        # add the start node to the open_list/set.
        self._open_list.put((start_node.h_score, start_node.id))
        self._open_set.add(start_node.id)
        # if our open list is not empty or we did not get a timeout event from the main thread
        # continue
        while not self._open_list.empty() and not self._stop_event.is_set():
            _, current_node_id = self._open_list.get()
            self._open_set.remove(current_node_id)
            self._closed_list.add(current_node_id)

            # if we have found our goal build the path and break out of the loop
            if current_node_id == end_node.id:
                end_node = self._graph[current_node_id]
                self._path = self.__build_path(end_node)
                break

            current_node = self._graph[current_node_id]
            current_neighbours = current_node.get_neighbours()
            # process the neighbours of the current node
            for neighbour_id in current_neighbours:
                neighbour_node: Node = self._graph[neighbour_id]

                if neighbour_id in self._closed_list:
                    continue

                # current g_score + the cost(edge weight) to move to the neighbour.
                current_weight = current_neighbours[neighbour_id]
                g_score = current_node.g_score + current_weight

                if neighbour_id not in self._open_set:
                    neighbour_node.parent = current_node
                    neighbour_node.g_score = g_score
                    neighbour_node.h_score = self.__calculate_h_score(neighbour_node, end_node, current_weight)
                    neighbour_node.f_score = neighbour_node.g_score + neighbour_node.h_score
                    self._open_list.put((neighbour_node.f_score, neighbour_id))
                    self._open_set.add(neighbour_id)
                # perform edge relaxation
                elif g_score < neighbour_node.g_score:
                    neighbour_node.parent = current_node
                    neighbour_node.g_score = g_score
                    neighbour_node.f_score = neighbour_node.g_score + neighbour_node.h_score

    def __reset_node_in_graph(self) -> None:
        for node_id in self._graph:
            node = self._graph[node_id]
            node.parent = None
            node.h_score = 0
            node.f_score = 0
            node.g_score = 0

    def __build_path(self, node: Node) -> List[Node]:
        path = list()
        current_node = node
        while current_node is not None:
            path.append(current_node)
            current_node = current_node.parent

        path.reverse()
        return path

    def set_graph(self, graph: Dict[int, Node]) -> None:
        self._graph = graph

    def __calculate_h_score(self, current: Node, goal: Node, current_weight) -> float:
        # perform a diagonal heuristic
        abs_delta_x = abs(current.cod_x - goal.cod_x)
        abs_delta_y = abs(current.cod_x - goal.cod_x)
        d_min = min(abs_delta_x, abs_delta_y)
        d_max = max(abs_delta_x, abs_delta_y)
        h_score = 1.5 * d_min + (current_weight * (d_max - d_min))
        return h_score

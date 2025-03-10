import json
import logging
import random
from collections import deque

from config.modules_configs.sequence_config import SequenceConfig
from sequences_manager.sequence_generator.random_paths_generator.sceneries_tags_manager import SceneriesTagsManager


class SceneriesGraph:
    def __init__(self, config: SequenceConfig):
        self._logger = logging.getLogger()

        with open(config.sequence_transitions_graph, 'r') as file:
            graph_info = json.load(file)

            self._starting_node: str = graph_info['starting_node']
            self._transitions_graph: dict[str, list[str]] = {}
            for node, neighbors in graph_info['transitions'].items():
                self._transitions_graph[node] = neighbors

    def find_path_with_tags(self, tag_groups: list[list[str]], tags_manager: SceneriesTagsManager) -> list[str]:
        tags_groups_with_matching_nodes = [
            (tags, tags_manager.find_sceneries_with_tags(tags)) for tags in tag_groups
        ]

        start_node = self._starting_node
        result_path = [start_node]
        current_node = start_node
        visited_nodes = { current_node }

        for i, (tag_group, matching_nodes) in enumerate(tags_groups_with_matching_nodes):
            if current_node in matching_nodes:
                continue

            unvisited_matches = [node for node in matching_nodes if node not in visited_nodes]
            target_nodes = unvisited_matches if len(unvisited_matches) > 0 else matching_nodes
            random.shuffle(target_nodes)

            best_path = None

            for target_node in target_nodes:
                path = self._find_path_avoiding_nodes(current_node, target_node, visited_nodes)

                if not path:
                    path = self._find_shortest_path(current_node, target_node, self._transitions_graph)

                if path and (best_path is None or len(path) < len(best_path)):
                    best_path = path

            if not best_path:
                self._logger.warning(f"Cannot reach any node matching {tag_group} from {current_node}")
                continue

            for target_node in best_path[1:]:
                result_path.append(target_node)
                visited_nodes.add(target_node)

            current_node = best_path[-1]

        if current_node != start_node:
            return_path = self._find_path_avoiding_nodes(current_node, start_node, visited_nodes - {start_node})

            if not return_path:
                return_path = self._find_shortest_path(current_node, start_node, self._transitions_graph)

            if not return_path:
                raise f"Sequence transitions graph is not allowing for proper cycles, {result_path} -> (no path) -> {start_node}"

            result_path.extend(return_path[1:])

        return result_path

    def _find_path_avoiding_nodes(self, start, end, nodes_to_avoid):
        if start == end:
            return [start]

        modified_graph = {}
        for node, neighbors in self._transitions_graph.items():
            if node not in nodes_to_avoid or node == start or node == end:
                modified_graph[node] = [n for n in neighbors if n not in nodes_to_avoid or n == end]

        return self._find_shortest_path(start, end, modified_graph)

    @staticmethod
    def _find_shortest_path(start, end, graph):
        if start == end:
            return [start]

        visited = {start}
        queue = deque([(start, [start])])

        while queue:
            current, path = queue.popleft()

            neighbors = graph[current]
            random.shuffle(neighbors)

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    if neighbor == end:
                        return path + [neighbor]
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None
import logging
import random
from collections import deque

from sequences_manager.sequence_generator.next_sequence_generator import NextSequenceGenerator
from sequences_manager.sequence_generator.random_paths_generator.config import SEQUENCE_CONFIG

TAG_SEQUENCE_LENGTH = 5
MAX_WINDOW_SIZE = 3

class RandomSequenceGenerator(NextSequenceGenerator):
    def __init__(self):
        super().__init__(True)

        self._logger = logging.getLogger()

        self._sceneries_tags = SEQUENCE_CONFIG['sceneries_tags']

        self._tags = list(SEQUENCE_CONFIG['tags_weights'].keys())
        self._tags_weights = list(SEQUENCE_CONFIG['tags_weights'].values())

        self._starting_node = SEQUENCE_CONFIG['starting_node']
        self._transitions_graph = {}
        for node, neighbors in SEQUENCE_CONFIG['transitions'].items():
            self._transitions_graph[node] = neighbors

        self.current_path_data = {
            'tags_sequence': [],
            'combined_tags_sequence': [],
            'path': []
        }

    def _get_next_sequence_path(self) -> list[int]:
        tags_sequence = self._combine_identical_neighboring_tags(
            random.choices(self._tags, weights=self._tags_weights, k=TAG_SEQUENCE_LENGTH)
        )
        combined_tags = self._combine_tags_sliding_window(tags_sequence, MAX_WINDOW_SIZE)

        path = self._find_path_with_tags(self._starting_node, combined_tags)

        self.current_path_data = {
            'tags_sequence': tags_sequence,
            'combined_tags_sequence': combined_tags,
            'path': path
        }

        return path

    @staticmethod
    def _combine_identical_neighboring_tags(tag_sequence):
        result = [tag_sequence[0]]

        for tag in tag_sequence[1:]:
            if tag != result[-1]:
                result.append(tag)

        return result

    def _combine_tags_sliding_window(self, tags_sequence: list[str], max_window_size) -> list[list[str]]:
        max_window_size = min(max_window_size, len(tags_sequence))

        combined = [False] * len(tags_sequence)
        result = []

        for window_size in range(max_window_size, 0, -1):
            i = 0
            while i <= len(tags_sequence) - window_size:
                window_positions = list(range(i, i + window_size))

                if any(combined[j] for j in window_positions):
                    i += 1
                    continue

                window_tags = tags_sequence[i:i + window_size]

                if self._has_matching_node(window_tags):
                    for j in window_positions:
                        combined[j] = True

                    result.append(window_tags)

                    i += window_size
                else:
                    i += 1

        return result

    def _has_matching_node(self, tags: list[str]) -> bool:
        for node_tags in self._sceneries_tags.values():
            if all(tag in node_tags for tag in tags):
                return True
        return False

    def _find_path_with_tags(self, start_node, tag_groups):
        tags_groups_with_matching_nodes = [
            (tags, self._find_nodes_with_tags(tags)) for tags in tag_groups
        ]

        result_path = [start_node]
        current_node = start_node
        visited_nodes = { current_node }

        for i, (tag_group, matching_nodes) in enumerate(tags_groups_with_matching_nodes):
            if current_node in matching_nodes:
                continue

            unvisited_matches = [node for node in matching_nodes if node not in visited_nodes]

            target_nodes = unvisited_matches if len(unvisited_matches) > 0 else matching_nodes

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

        return [int(i) for i in result_path]

    def _find_nodes_with_tags(self, tags):
        matching_nodes = []

        for node_id, node_tags in self._sceneries_tags.items():
            if all(tag in node_tags for tag in tags):
                matching_nodes.append(node_id)

        return matching_nodes

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

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    if neighbor == end:
                        return path + [neighbor]
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None






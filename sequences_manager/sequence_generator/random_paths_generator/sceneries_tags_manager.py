import json
import random

from config.modules_configs.sequence_config import SequenceConfig


class SceneriesTagsManager:
    def __init__(self, config: SequenceConfig):
        with open(config.sequence_nodes_tags, 'r') as file:
            self._sceneries_tags: dict[str, list[str]] = json.load(file)

        with open(config.tags_weights, 'r') as file:
            tags_weights = json.load(file)
            self._tags: list[str] = list(tags_weights.keys())
            self._tags_weights: list[int] = list(tags_weights.values())


    def get_scenery_tags(self, scenery: str) -> list[str]:
        return self._sceneries_tags[scenery]


    def find_sceneries_with_tags(self, tags):
        matching_sceneries = []

        for scenery_id, scenery_tags in self._sceneries_tags.items():
            if all(tag in scenery_tags for tag in tags):
                matching_sceneries.append(scenery_id)

        return matching_sceneries


    def generate_tags_list(self, tag_sequence_length: int, max_window_size: int) -> tuple[list[str], list[list[str]]]:
        tags_sequence = random.choices(self._tags, weights=self._tags_weights, k=tag_sequence_length)
        tags_sequence = self._combine_identical_neighboring_tags(tags_sequence)
        combined_tags = self._combine_tags_sliding_window(tags_sequence, max_window_size)

        return tags_sequence, combined_tags

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

                if self._has_matching_scenery(window_tags):
                    for j in window_positions:
                        combined[j] = True

                    result.append(window_tags)

                    i += window_size
                else:
                    i += 1

        return result

    def _has_matching_scenery(self, tags: list[str]) -> bool:
        for scenery_tags in self._sceneries_tags.values():
            if all(tag in scenery_tags for tag in tags):
                return True
        return False

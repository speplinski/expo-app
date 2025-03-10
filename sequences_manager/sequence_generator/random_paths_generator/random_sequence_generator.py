from config.modules_configs.sequence_config import SequenceConfig
from sequences_manager.sequence_generator.next_sequence_generator import NextSequenceGenerator
from sequences_manager.sequence_generator.random_paths_generator.sceneries_graph import SceneriesGraph
from sequences_manager.sequence_generator.random_paths_generator.sceneries_tags_manager import SceneriesTagsManager

TAG_SEQUENCE_LENGTH = 5
MAX_TAGS_COMBINATION_WINDOW_SIZE = 3

MINIMUM_LOOP_SIZE = 5
MAX_GENERATION_RETRIES = 5

class RandomSequenceGenerator(NextSequenceGenerator):
    def __init__(self, config: SequenceConfig):
        super().__init__(config)

        self._tags_manager = SceneriesTagsManager(config)

        self._sceneries_graph = SceneriesGraph(config)

        self.current_path_data = {
            'tags_sequence': [],
            'combined_tags_sequence': [],
            'path': []
        }

    def get_scenery_tags(self, scenery: str) -> list[str]:
        return self._tags_manager.get_scenery_tags(scenery)

    def _get_next_sequence_path(self) -> list[str]:
        path = []

        current_generation_attempt = 0
        while current_generation_attempt < MAX_GENERATION_RETRIES:
            tags_sequence, combined_tags = self._tags_manager.generate_tags_list(TAG_SEQUENCE_LENGTH, MAX_TAGS_COMBINATION_WINDOW_SIZE)
            path = self._sceneries_graph.find_path_with_tags(combined_tags, self._tags_manager)

            self.current_path_data = {
                'tags_sequence': tags_sequence,
                'combined_tags_sequence': combined_tags,
                'path': path,
                'attempts': current_generation_attempt + 1
            }

            if not self._has_repeats_in_window(path, MINIMUM_LOOP_SIZE):
                break

            current_generation_attempt += 1

        return path

    @staticmethod
    def _has_repeats_in_window(string_list, window_size):
        for i in range(len(string_list) - window_size + 1):
            window = string_list[i:i+window_size]

            if len(set(window)) < len(window):
                return True

        return False








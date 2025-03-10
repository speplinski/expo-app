import json
import random

from config.modules_configs.sequence_config import SequenceConfig
from sequences_manager.sequence_generator.next_sequence_generator import NextSequenceGenerator


class StaticPathsNextSequenceGenerator(NextSequenceGenerator):
    def __init__(self, config: SequenceConfig):
        super().__init__(config)

        with open(config.static_paths_path, 'r') as file:
            self._allowed_sequences: list[list[str]] = json.load(file)

        self._current_index = 0
        self._shuffle_sequences()

    def _shuffle_sequences(self):
        random.shuffle(self._allowed_sequences)
        self._current_index = 0

    def _get_next_sequence_path(self) -> list[str]:
        if self._current_index >= len(self._allowed_sequences):
            self._shuffle_sequences()

        sequence = self._allowed_sequences[self._current_index]
        self._current_index += 1

        return sequence

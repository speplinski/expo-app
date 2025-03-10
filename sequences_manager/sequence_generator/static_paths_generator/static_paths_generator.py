import json
import random

from config.modules_configs.sequence_config import SequenceConfig
from sequences_manager.sequence_generator.next_sequence_generator import NextSequenceGenerator


class StaticPathsNextSequenceGenerator(NextSequenceGenerator):
    def __init__(self, config: SequenceConfig):
        super().__init__(config)

        with open(config.static_paths_path, 'r') as file:
            self._allowed_sequences: list[list[str]] = json.load(file)

    def _get_next_sequence_path(self) -> list[str]:
        return random.choice(self._allowed_sequences)

import random

from sequences_manager.sequence_generator.next_sequence_generator import NextSequenceGenerator
from sequences_manager.sequence_generator.static_paths_generator.config import ALLOWED_PATHS


class StaticPathsNextSequenceGenerator(NextSequenceGenerator):
    def __init__(self):
        super().__init__(True)

        self._allowed_sequences: list[list[int]] = ALLOWED_PATHS

    def _get_next_sequence_path(self) -> list[int]:
        return random.choice(self._allowed_sequences)

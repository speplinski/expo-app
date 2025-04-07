import json
from abc import abstractmethod, ABC

from config.modules_configs.sequence_config import SequenceConfig


class NextSequenceGenerator(ABC):
    def __init__(self, config: SequenceConfig) -> None:
        self._current_path_item = -1
        self._current_path = []

        with open(config.sequence_mapping_path, 'r') as file:
            self._sequence_mapping = json.load(file)

    def next_sequence(self) -> str:
        self._current_path_item += 1

        if self._current_path_item >= len(self._current_path):
            self._current_path_item = 0
            self._current_path = self._get_next_sequence_path()

        current_item = self._current_path[self._current_path_item]
        return self._sequence_mapping[current_item]

    @abstractmethod
    def _get_next_sequence_path(self) -> list[str]:
        pass

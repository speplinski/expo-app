from abc import abstractmethod, ABC


class NextSequenceGenerator(ABC):
    def __init__(self, subtract_one_from_result: bool) -> None:
        self._current_path_item = -1
        self._current_path = []

        self._subtract_value = 1 if subtract_one_from_result else 0

    def next_sequence(self) -> int:
        self._current_path_item += 1

        if self._current_path_item >= len(self._current_path):
            self._current_path_item = 0
            self._current_path = self._get_next_sequence_path()

        return self._current_path[self._current_path_item] - self._subtract_value

    @abstractmethod
    def _get_next_sequence_path(self) -> list[int]:
        pass

import numpy as np
import numpy.typing as npt

from sequences_manager.sequence_layer import SequenceLayer


class Sequence:
    def __init__(self, name: str, config: dict,  target_size: (int, int)) -> None:
        self.name = name
        self._config = config
        self._target_size = target_size
        self._layers = []

    def load_data(self, files_path: str):
        data_path_root = f'{files_path}/{self.name}'

        layers_dict = {}

        for static_mask_id, static_mask_gray_shade in self._config['static_masks'].items():
            layers_dict[int(static_mask_id)] = SequenceLayer(
                static_mask_gray_shade,
                self._target_size,
                static_file_path=f'{data_path_root}/{self.name}_{static_mask_id}.png'
            )

        for dynamic_mask_id, dynamic_mask_gray_shade in self._config['sequence_masks'].items():
            layers_dict[int(dynamic_mask_id)] = SequenceLayer(
                dynamic_mask_gray_shade,
                self._target_size,
                dynamic_files_path=f'{data_path_root}/{self.name}_{dynamic_mask_id}'
            )

        self._layers = [layers_dict[key] for key in sorted(layers_dict.keys(), reverse=True)]

    def build_image(self, counters: npt.NDArray[np.uint8])-> npt.NDArray[np.uint8]:
        width, height = self._target_size
        result = np.zeros((height, width), dtype=np.uint8)

        for layer in self._layers:
            layer_image = layer.build_layer_image(counters)
            result = np.where(layer_image > 0, layer_image, result)

        return result

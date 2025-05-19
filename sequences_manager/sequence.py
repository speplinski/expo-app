import numpy as np
import numpy.typing as npt

from sequences_manager.sequence_layer import SequenceLayer
from sequences_manager.sequence_overlay import SequenceOverlay


class Sequence:
    def __init__(
            self, name: str, config: dict,
            content_size: (int, int), output_size: (int, int),
            max_counter_value: int
    ) -> None:
        self.name = name
        self._config = config
        self._content_size = content_size
        self._output_size = output_size
        self._layers = []
        self._overlay: SequenceOverlay | None = None
        self._max_counter_value = max_counter_value

    def load_data(self, files_path: str, overlay_files_path: str):
        data_path_root = f'{files_path}/{self.name}'

        layers_dict = {}

        for static_mask_id, static_mask_gray_shade in self._config['static_masks'].items():
            layers_dict[int(static_mask_id)] = SequenceLayer(
                static_mask_gray_shade,
                self._content_size,
                static_file_path=f'{data_path_root}/{self.name}_{static_mask_id}.png'
            )

        for dynamic_mask_id, dynamic_mask_gray_shade in self._config['sequence_masks'].items():
            layers_dict[int(dynamic_mask_id)] = SequenceLayer(
                dynamic_mask_gray_shade,
                self._content_size,
                dynamic_files_path=f'{data_path_root}/{self.name}_{dynamic_mask_id}',
                max_counter_value=self._max_counter_value
            )

        self._layers = [layers_dict[key] for key in sorted(layers_dict.keys(), reverse=True)]

        if 'overlay' in self._config:
            self._overlay = SequenceOverlay(
                self._output_size,
                f'{overlay_files_path}/{self._config["overlay"]["path"]}',
                self._config["overlay"]["max_overlay_height_percent"],
                self._config["overlay"]["min_images_per_column_update"],
                self._config["overlay"]["max_images_per_column_update"]
            )
        else:
            self._overlay = SequenceOverlay(self._output_size)

    def build_image(self, counters: npt.NDArray[np.uint8])-> npt.NDArray[np.uint8]:
        width, height = self._content_size
        result = np.zeros((height, width), dtype=np.uint8)

        for layer in self._layers:
            layer_image = layer.build_layer_image(counters)
            result = np.where(layer_image > 0, layer_image, result)

        return result

    def update_overlay(self, counters: npt.NDArray[np.uint8])-> npt.NDArray[np.uint8]:
        return self._overlay.update_overlay_image(counters)

    def reset_overlay(self):
        self._overlay.reset_overlay()

import logging
from typing import Tuple

import cv2
import torch

import numpy as np
import numpy.typing as npt

from config.modules_configs.spade_config import SpadeConfig
from spade.pix2pix_model import Pix2PixModel


class SpadeAdapter:
    def __init__(self, config: SpadeConfig, resolution: Tuple[int, int]):
        self.config = config
        self.logger = logging.getLogger()

        self.device = self._setup_device(config.device_type)
        self.logger.info(f"Spade using device: {self.device}")

        self.resolution = resolution

        if not config.bypass_spade:
            self.model = Pix2PixModel(config, self.device)
            self.model.eval()
            self.model.to(self.device)
        else:
            self.model = None

    @staticmethod
    def _setup_device(device_type: str) -> torch.device:
        if device_type == 'auto':
            if torch.cuda.is_available():
                return torch.device('cuda')
            elif torch.backends.mps.is_available():
                return torch.device('mps')

            return torch.device('cpu')

        return torch.device(device_type)

    def process_mask(self, mask: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        if self.config.bypass_spade:
            normalized_mask = cv2.normalize(mask, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            return cv2.applyColorMap(normalized_mask, self.config.colormap)

        data = {
            'label': torch.from_numpy(np.stack([mask])).unsqueeze(1).float(),
            'instance': torch.zeros(1).to(self.device),
            'image': torch.zeros(1, 3, mask.shape[0], mask.shape[1]).to(self.device)
        }

        with torch.no_grad():
            if self.device.type == 'cuda':
                with torch.cuda.amp.autocast():
                    generated = self.model(data, mode='inference')
            else:
                generated = self.model(data, mode='inference')

        image = ((generated[0].cpu().numpy() * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
        if image.shape[0] == 3:
            image = image[[2, 1, 0]].transpose(1, 2, 0)

        del generated, data
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
        elif self.device.type == 'mps':
            torch.mps.empty_cache()

        return image

    def get_empty_frame(self):
        width, height = self.resolution
        return np.zeros((height, width, 3), dtype=np.uint8)

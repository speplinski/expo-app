from dataclasses import dataclass, field

import cv2


@dataclass
class SpadeConfig:
    bypass_spade: bool = False

    colormap: str = cv2.COLORMAP_VIRIDIS

    device_type: str = 'auto'

    weights_path: str = './data/checkpoints/980_net_G.pth'

    gpu_ids: list[int] = field(default_factory=lambda: [0])

    crop_size: int = 1920
    aspect_ratio: float = 3.0

    norm_G: str = 'spectralspadesyncbatch3x3'
    num_upsampling_layers: str = 'most'

    label_nc: int = 51 # v8
    semantic_nc: int = 52
    ngf: int = 96

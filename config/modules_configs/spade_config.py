from dataclasses import dataclass, field

import cv2


MODELS = {
    'debug_small': {
        'weights_path': './data/checkpoints/20_net_G.pth',

        'content_resolution': (960, 320),
        'aspect_ratio': 3.0,

        'norm_G': 'spectralspadesyncbatch3x3',
        'num_upsampling_layers': 'normal',

        'label_nc': 56,
        'semantic_nc': 57,
        'ngf': 64
    },
    'full': {
        'weights_path': './data/checkpoints/1160_net_G.pth',

        'content_resolution': (1920, 640),
        'aspect_ratio': 3.0,

        'norm_G': 'spectralspadesyncbatch3x3',
        'num_upsampling_layers': 'most',

        'label_nc': 56, # v10
        'semantic_nc': 57,
        'ngf': 96
    }
}

@dataclass
class SpadeConfig:
    bypass_spade: bool = False
    model_name: str = 'debug_small'

    colormap: str = cv2.COLORMAP_VIRIDIS

    device_type: str = 'auto'
    gpu_ids: list[int] = field(default_factory=lambda: [0])

    weights_path: str = ''

    upscaler_model: str = 'weights/RealESRGAN_x2plus.pth'
    upscale_scale: int = 2

    content_resolution: tuple[int, int] = (0, 0)
    output_resolution: tuple[int, int] = (0, 0)
    crop_size: int = -1
    aspect_ratio: float = -1

    norm_G: str = ''
    num_upsampling_layers: str = ''

    label_nc: int = -1
    semantic_nc: int = -1
    ngf: int = -1

    def __post_init__(self):
        if hasattr(self, 'model_name') and self.model_name in MODELS:
            model_config = MODELS[self.model_name]
            for key, value in model_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            output_scale = 1 if self.bypass_spade else self.upscale_scale
            self.output_resolution = tuple(dimension * output_scale for dimension in self.content_resolution)

        self.crop_size = self.content_resolution[0]

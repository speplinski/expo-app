import cv2
import numpy as np
import torch
from PIL import Image
from RealESRGAN import RealESRGAN
from torch import autocast


class ImageUpscaler:
    def __init__(self, weights_path, scale):
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            self.precision = "fp16"
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
            self.precision = "fp32"
        else:
            self.device = torch.device("cpu")
            self.precision = "fp32"

        self.model = RealESRGAN(self.device, scale=scale)
        self.model.load_weights(weights_path, download=True)

        print(f'Upscaler initialized: {self.device} | {self.precision}')

    def upscale(self, cv_image):
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

        pil_image = Image.fromarray(rgb_image)

        if self.precision == "fp16":
            with torch.no_grad():
                with autocast():
                    sr_pil_image = self.model.predict(pil_image)
        else:
            with torch.no_grad():
                sr_pil_image = self.model.predict(pil_image)

        sr_rgb = np.array(sr_pil_image)
        sr_bgr = cv2.cvtColor(sr_rgb, cv2.COLOR_RGB2BGR)

        return sr_bgr
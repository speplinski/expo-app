import torch

from config.modules_configs.spade_config import SpadeConfig
from spade.networks.generator import SPADEGenerator


class Pix2PixModel(torch.nn.Module):
    def __init__(self, config: SpadeConfig, device):
        super().__init__()
        self.opt = config
        self.device = device

        self.FloatTensor = lambda *args: torch.FloatTensor(*args).to(self.device)
        self.ByteTensor = lambda *args: torch.ByteTensor(*args).to(self.device)

        self.netG = SPADEGenerator(config)
        weights = torch.load(config.weights_path, weights_only=True)
        self.netG.load_state_dict(weights)


    def forward(self, data, mode):
        input_semantics, real_image = self.preprocess_input(data)

        if mode == 'inference':
            with torch.no_grad():
                fake_image = self.netG(input_semantics, z=None)
            return fake_image
        else:
            raise ValueError("|mode| is invalid")

    def preprocess_input(self, data):
        data['label'] = data['label'].to(self.device)
        data['instance'] = data['instance'].to(self.device)
        if 'image' in data:
            data['image'] = data['image'].to(self.device)

        label_map = data['label']
        bs, _, h, w = label_map.size()
        nc = self.opt.label_nc + 1
        
        input_label = torch.zeros(bs, nc, h, w, device=self.device)
        input_semantics = input_label.scatter_(1, label_map.long(), 1.0)

        return input_semantics, data['image']

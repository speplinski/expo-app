from dataclasses import dataclass


@dataclass
class SequenceConfig:
    config_path: str = "data/mask_mapping.json"
    images_path: str = "data/landscapes"

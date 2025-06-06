import logging
from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    log_file = 'application.log'
    log_level = logging.INFO

    test_animation_mode: bool = False

import argparse

from config.integrated_config import IntegratedConfig


def parse_arguments_and_init_config():
    config = IntegratedConfig()

    args = _parse_arguments(config)

    config.display.monitor_index = args.monitor
    config.depth.mirror_mode = args.mirror
    config.spade.device_type = args.spade_device

    return config


def _parse_arguments(config: IntegratedConfig):
    parser = argparse.ArgumentParser(description='Integrated TMPL Application')

    parser.add_argument('--monitor', type=int, default=config.display.monitor_index,
                        help='Monitor index (0 is usually the main display)')
    parser.add_argument('--mirror', action='store_true', default=config.depth.mirror_mode,
                        help='Enable mirror mode')
    parser.add_argument('--disable-spade', action='store_true', default=config.spade.bypass_spade,
                        help='Disable SPADE processing')
    parser.add_argument('--spade-device', type=str, default=config.spade.device_type,
                        help='Device for SPADE (cuda/mps/cpu/auto)')

    return parser.parse_args()
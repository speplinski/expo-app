DEFAULT_CAMERAS = [
    {
        'name': 'left',
        'ip_address': '192.168.70.64',
        'grid_size': (22, 14),
        'margins': (0.2, 0.05, 0.3, 0.1),  # top, bottom, left, right
        'port': 65432,
        'script_config': {
            'debug_mode': False,
            'custom_distance_processing': '# Left camera distance processing',
            'custom_data_preparation': '# Left camera custom data preparation'
        }
    },
    {
        'name': 'center',
        'ip_address': '192.168.70.62',
        'grid_size': (22, 14),
        'margins': (0.2, 0.1, 0.25, 0.25),
        'port': 65432,
        'script_config': {
            'debug_mode': False,
            'custom_distance_processing': '# Center camera distance processing',
            'custom_data_preparation': '# Center camera custom data preparation'
        }
    },
    {
        'name': 'right',
        'ip_address': '192.168.70.65',
        'grid_size': (22, 14),
        'margins': (0.2, 0.1, 0.1, 0.3),
        'port': 65432,
        'script_config': {
            'debug_mode': False,
            'custom_distance_processing': '# Right camera distance processing',
            'custom_data_preparation': '# Right camera custom data preparation'
        }
    }
]

def load_camera_configs(config_file=None):
    if config_file:
        import json
        with open(config_file, 'r') as f:
            return json.load(f)
    return DEFAULT_CAMERAS
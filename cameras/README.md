# OAK-D Camera System

A modular system for managing multiple OAK-D depth cameras for spatial awareness in an exhibition environment.

## Overview

This system provides a structured approach to manage multiple OAK-D depth cameras. It replaces the previous individual camera scripts with a unified, configurable system that reduces code duplication and improves maintainability.

## Features

- Template-based script generation for each camera
- Configurable camera settings via JSON configuration files
- Automatic reconnection handling
- Parallel camera management
- Modular design with separation of concerns
- Visualization tool for monitoring camera data

## Components

- `oak_camera_system/` - Core camera management system
  - `oak_camera.py` - Base OAK-D camera class
  - `camera_manager.py` - Manager for multiple cameras
  - `camera_config.py` - Configuration management
  - `camera_script_template.py` - Templating system for camera scripts
- `run_cameras.py` - Script to run the camera system
- `run_visualization.py` - Visualization tool for camera data
- `example_camera_config.json` - Example camera configuration

## Usage

### Running the Camera System

```bash
# Run with default configuration
python run_cameras.py

# Run with custom configuration
python run_cameras.py --config example_camera_config.json

# Run only specific cameras
python run_cameras.py --cameras left center
```

### Running the Visualization

```bash
# Run with default configuration
python run_visualization.py

# Run with custom configuration
python run_visualization.py --config camera_visualization_config.json
```

## Configuration

The system can be configured through JSON files. Example configuration:

```json
{
  "cameras": [
    {
      "name": "left",
      "ip_address": "192.168.70.64",
      "grid_size": [22, 14],
      "margins": [0.2, 0.05, 0.3, 0.1],
      "port": 65432,
      "script_config": {
        "debug_mode": false,
        "custom_distance_processing": "# Custom processing code here"
      }
    },
    // Additional cameras...
  ]
}
```

### Camera-Specific Configurations

Each camera can have its own configuration, including:
- IP address
- Grid size and margins
- Socket port
- Custom script behavior via the script_config section

## Visualization Controls

- `1`, `2`, `3` - Select left, center, or right camera for threshold adjustment
- `z` - Decrease maximum threshold for active camera
- `x` - Increase maximum threshold for active camera
- `s` - Save current configuration
- `q` - Quit program
# The Most Polish Landscape — Expo 2025 Osaka

Real-time generative AI system for an interactive art installation at the Poland Pavilion, Expo 2025 Osaka. Part of the exhibition awarded Gold in Exhibition Design (BIE Official Awards).

Visitors stand in front of a panoramic 4K display. Three depth cameras detect their spatial positions. A SPADE neural network transforms semantic landscape masks into photorealistic imagery — driven by how long people remain in each zone. The landscape evolves through presence, not movement.

## Architecture

The entire pipeline runs as a single process, orchestrated by RxPY (ReactiveX for Python) with six dedicated schedulers:

```
  OAK-D Cameras (3×)          Movement Detector          Reactive Pipeline (RxPY)
 ┌───────────────────┐      ┌─────────────────────┐      ┌──────────────────────────┐
 │ 192.168.70.62     │─────▶│ 22×14 depth grid    │─────▶│ 6 schedulers:            │
 │ 192.168.70.64     │      │ per camera           │      │  · detections            │
 │ 192.168.70.65     │      │ threshold: 1.7–2.8m │      │  · counters_processing   │
 │                   │      │ → 9 binary counters  │      │  · image_generation      │
 │ socket :65432     │      │   (3 per camera)     │      │  · spade_processing      │
 └───────────────────┘      └─────────────────────┘      │  · overlay_processing    │
                                                          │  · transition            │
                                                          └────────────┬─────────────┘
                                                                       │
                            ┌──────────────────────────────────────────┘
                            │
                            ▼
  Sequences Manager                SPADE + RealESRGAN              Display
 ┌─────────────────────┐      ┌─────────────────────────┐      ┌──────────────────┐
 │ mask_mapping.json   │─────▶│ Pix2PixModel             │─────▶│ OpenCV fullscreen│
 │ static + dynamic    │      │ label_nc=84, ngf=96     │      │ 3840×2160        │
 │ layers per sequence │      │ content: 1920×640       │      │ 60 fps interp.   │
 │ overlay blending    │      │ output:  3840×1280 (×2) │      │ linear blend     │
 └─────────────────────┘      │ + saturation boost 1.25 │      └──────────────────┘
                              └─────────────────────────┘
```

### Data Flow

1. **Depth sensing** — Three OAK-D cameras stream depth frames over network sockets (port 65432). Each camera captures a 22×14 grid of distance values at 200ms intervals.

2. **Presence detection** — Distances are thresholded (1.7–2.8m valid range) and reduced to 9 binary detection columns (3 per camera). The display grid (9×5) provides a real-time heatmap visualization.

3. **Counter accumulation** — Each detection column accumulates a counter (sampled every 1.0s). Counters are clamped at a maximum of 30. Three aggregate counters (left/center/right camera max) and one global counter are derived, giving 13 values total.

4. **Mask composition** — `SequencesManager` loads landscape datasets and builds semantic masks from static layers and dynamic frame sequences. Counter values select which frames to composite. Each sequence has configurable grayscale-indexed regions that the SPADE model interprets.

5. **Neural inference** — `SpadeAdapter` feeds the composed mask to a Pix2PixModel (SPADE architecture, 84 semantic classes). Inference runs with `torch.cuda.amp.autocast()` on CUDA. Output (1920×640) is upscaled 2× by RealESRGAN to 3840×1280, with a 1.25× saturation boost in HSV.

6. **Display** — OpenCV fullscreen window renders on the target monitor at 3840×2160. `ImagesInterpolator` linearly blends between generated keyframes over 1 second, targeting 60 fps refresh.

7. **Sequence rotation** — After 45 epochs without max counters, the pipeline switches to the next landscape. Sequence paths are either static (predefined order) or generated via a weighted tag-based graph walk.

## Modules

| Module | What it does |
|--------|-------------|
| `main.py` | Entry point: config → pipeline → Textual app |
| `config/` | Dataclass-based configuration: depth, display, SPADE, timing, sequences, runtime |
| `scheduler/` | `MainPipeline` — RxPY orchestration with 6 schedulers, counter logic, frame sampling |
| `movement_detector/` | Depth stream from OAK-D cameras (or simulation), 22×14 grid → 9 binary counters |
| `movement_detector/depth_info/camera/` | `OakCameraSocket` / `OakSocketAdapter` — TCP socket protocol for depth frames |
| `movement_detector/depth_info/simulation/` | `OakDSimulation` — simulated visitors (speed 0.3 m/s, height 0.8–2.0m) |
| `sequences_manager/` | Loads landscape datasets, builds semantic masks from static + dynamic layers, overlay blending |
| `sequences_manager/sequence_generator/` | Static path cycling or random graph-based path generation with tag weighting |
| `spade/` | `SpadeAdapter` + `Pix2PixModel` — SPADE inference (auto device: CUDA/MPS/CPU) |
| `spade/networks/` | Generator, normalization (SPADE blocks), sync batch norm, architecture utils |
| `image_upscaler/` | RealESRGAN (RRDBNet, scale=2, tile=1024) + saturation boost |
| `ui/` | `ExpoApp` (Textual TUI): detection heatmap, sparkline counters, sequence tree, log panel |
| `ui/display/` | `CVApp` (OpenCV window), `WindowDisplay` (scaling/refresh), `ImagesInterpolator` (60fps blend) |
| `cameras/` | OAK-D camera scripts — stereo depth pipeline, ROI config, socket streaming |

## Configuration

All configuration lives in `config/modules_configs/` as Python dataclasses.

### Key Defaults

| Parameter | Value | Source |
|-----------|-------|--------|
| Depth grid per camera | 22 × 14 | `DepthConfig.depth_grid_segments_count` |
| Display heatmap grid | 9 × 5 | `DepthConfig.depth_grid_display_segments_count` |
| Detection range | 1.7 – 2.8 m | `DistanceThresholdInM` |
| Counters per camera | 3 | `DepthConfig.horizontal_segment_count_per_camera` |
| Total counters | 9 base + 3 sides + 1 global = 13 | `MainPipeline` |
| Max counter value | 30 | `TimingConfig.max_counter_value` |
| Sampling interval | 1.0 s | `TimingConfig.counters_sampling_interval` |
| Depth refresh | 200 ms | `TimingConfig.depth_data_refresh_interval` |
| Sequence switch epoch | 45 | `TimingConfig.sequence_switch_epoch` |
| Target interpolation FPS | 60 | `TimingConfig.target_interpolation_frames` |
| SPADE model | `full_new` (v11, label_nc=84) | `SpadeConfig.model_name` |
| Content resolution | 1920 × 640 | `MODELS['full_new']` |
| Upscale factor | 2× (→ 3840 × 1280) | `SpadeConfig.upscale_scale` |
| Display resolution | 3840 × 2160 | `DisplayConfig.available_monitors` |
| Full screen | enabled | `DisplayConfig.full_screen_mode` |
| Cameras | 3 OAK-D at .62, .64, .65 | `DepthConfig.cameras` |
| Simulation mode | disabled | `DepthConfig.run_cameras_in_simulation_mode` |

### SPADE Models

| Name | Weights | Resolution | label_nc | ngf |
|------|---------|-----------|----------|-----|
| `debug_small` | `20_net_G.pth` | 960×320 | 56 | 64 |
| `full` | `1160_net_G.pth` | 1920×640 | 56 | 96 |
| `full_new` (default) | `v11_660_net_G.pth` | 1920×640 | 84 | 96 |

## Installation

```bash
git clone https://github.com/speplinski/expo-app.git
cd expo-app
pip install -r requirements.txt
```

### Requirements

Python 3.13, plus (from `requirements.txt`):

```
torch~=2.6.0            # Neural network inference
torchvision~=0.21.0
depthai~=2.29.0.0        # OAK-D camera SDK
reactivex~=4.0.4         # Reactive pipeline
opencv-python~=4.11.0    # Display and image processing
numpy~=2.2.2
textual~=2.1.1           # Terminal UI
pillow~=11.1.0
scipy~=1.15.1
```

RealESRGAN and model weights installed separately (see `Pipfile` for git source).

## Usage

```bash
# Production (cameras connected)
python main.py

# Specify monitor
python main.py --monitor 1

# Mirror mode (front-facing cameras)
python main.py --mirror

# Without SPADE inference (colormap visualization only)
python main.py --disable-spade

# Force CPU inference
python main.py --spade-device cpu
```

### TUI Controls

The application launches a Textual terminal dashboard alongside the OpenCV display window ("The Most Polish Landscape"):

- **Detection heatmap** — 9×5 color-coded grid (blue = valid range, red = too far, light = too close)
- **Counters** — sparkline graphs for 9 base counters + aggregate (left/center/right/global)
- **Sequence tree** — loading status and current sequence selection
- **Playback stats** — elapsed time, frame count, FPS
- **`L` key** — toggle full log panel

### Simulation Mode

When `run_cameras_in_simulation_mode = True` in `DepthConfig`, the system generates synthetic visitors instead of reading from cameras. Simulated visitors move at 0.3 m/s with configurable arrival and departure probabilities.

## Data Layout

```
data/
├── checkpoints/
│   ├── v11_660_net_G.pth     # SPADE model (full_new, default)
│   ├── 1160_net_G.pth        # SPADE model (full)
│   └── 20_net_G.pth          # SPADE model (debug_small)
├── landscapes/               # Semantic mask datasets per sequence
├── overlays/                 # PNG overlay images with alpha
└── sequence_config/
    ├── mask_mapping.json     # Sequence → layer definitions
    ├── sequence_mapping.json # Node ID → sequence name
    ├── static_paths.json     # Predefined sequence order
    ├── sequence_transitions_graph.json
    ├── sequence_nodes_tags.json
    └── tags_weights.json

weights/
└── net_g_18000.pth           # RealESRGAN upscaler model
```

## Related Repositories

| Repository | Role |
|-----------|------|
| [tmpl-viewer-position-tracking](https://github.com/speplinski/tmpl-viewer-position-tracking) | Standalone OAK-D depth tracking |
| [tmpl-generator](https://github.com/speplinski/tmpl-generator) | Standalone mask composition |
| [tmpl-benchmark-app](https://github.com/speplinski/tmpl-benchmark-app) | Multi-GPU SPADE renderer |
| [tmpl-app](https://github.com/speplinski/tmpl-app) | SDL2-based display manager |

## License

SPADE model architecture based on [NVlabs/SPADE](https://github.com/NVlabs/SPADE). RealESRGAN based on [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN).

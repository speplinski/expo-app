# The Most Polish Landscape — Expo 2025 Osaka

A real-time generative AI installation for the Poland Pavilion at Expo 2025 Osaka. Visitor presence transforms Polish landscapes — not through movement, but through being. The system won **Gold in Exhibition Design** (BIE Official Awards).

## How It Works

Three OAK-D depth cameras detect visitors standing in front of a panoramic display (3840×1280). Their spatial presence is mapped to semantic regions of a landscape. A SPADE neural network (Spatially-Adaptive Normalization) generates photorealistic imagery from semantic masks in real time. The longer a visitor stands in a zone, the more that part of the landscape evolves.

The result is a continuously generated landscape that responds to presence — not gestures, not touch, not buttons. Just people being there.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  OAK-D Cameras  │────▶│ Movement Detector │────▶│    Scheduler    │
│  (3× depth)     │     │ (depth → presence)│     │  (RxPY pipeline)│
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                         ┌────────────────┐               │
                         │   Sequences    │◀──────────────┘
                         │    Manager     │
                         │ (mask composer)│
                         └───────┬────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     SPADE + RealESRGAN  │
                    │  (inference + upscale)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Display Pipeline     │
                    │ (interpolation + render)│
                    └─────────────────────────┘
```

## Modules

| Module | Purpose |
|--------|---------|
| `cameras/` | Multi-camera OAK-D depth capture over network sockets (3 cameras, 9 detection zones) |
| `movement_detector/` | Depth stream → presence detection using configurable distance thresholds and spatial segmentation |
| `scheduler/` | Reactive pipeline (RxPY) orchestrating the full data flow — from depth detections through mask generation to display. Manages concurrency across 6 dedicated schedulers |
| `sequences_manager/` | Loads landscape datasets, composes semantic masks from static and animated layers based on visitor counters, manages sequence rotation |
| `spade/` | SPADE (Pix2PixHD) adapter — converts semantic masks to photorealistic landscape images via neural inference (CUDA/MPS/CPU) |
| `image_upscaler/` | RealESRGAN super-resolution for production output quality |
| `ui/` | Textual-based terminal dashboard for real-time monitoring: depth heatmaps, detection counters, sequence status, playback statistics. Separate OpenCV window for the rendered output |
| `config/` | Pydantic-based configuration system covering depth, display, SPADE, timing, sequences, and runtime settings |
| `data/` | Landscape datasets (semantic masks, overlays), SPADE model checkpoints |

## Key Design Decisions

**Reactive pipeline.** The entire data flow — from raw depth frames to rendered output — is built on RxPY (ReactiveX for Python). This handles the concurrency problem of running depth detection, mask composition, neural inference, and display rendering on parallel schedulers without shared mutable state.

**Presence, not movement.** The system accumulates presence over time through a counter mechanism. Each detection zone has a counter that increments while a visitor stands in it, up to a configurable maximum. Counters drive mask evolution — the landscape changes gradually, not abruptly.

**Multi-model pipeline.** Semantic masks are generated from landscape datasets, then passed through SPADE for photorealistic synthesis, then through RealESRGAN for upscaling. Each stage runs on a dedicated thread with its own scheduler.

**Sequence rotation.** The installation cycles through multiple Polish landscape datasets (Baltic coast dunes, Biebrza marshes, mountain peaks). Each landscape runs until visitor counters reach maximum, then transitions to the next.

**Frame interpolation.** Because neural inference takes hundreds of milliseconds per frame, the display pipeline interpolates between generated frames to maintain smooth visual output.

## Landscape Datasets

All training data comes exclusively from photographs taken in Poland — no generic models, no stock imagery. Landscapes include:

- Baltic Sea coastal dunes
- Biebrza marshland meadows
- Tatra mountain ridgelines
- Forest and agricultural lowlands

Each dataset contains semantic masks with labeled regions (sky, water, vegetation, terrain, etc.) that the SPADE model uses to generate photorealistic output.

## Requirements

- Python 3.8+
- OAK-D camera(s) with DepthAI SDK
- CUDA-capable GPU (recommended) or Apple Silicon (MPS) or CPU
- PyTorch, OpenCV, RealESRGAN, RxPY, Textual

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Default (main display, auto device detection)
python main.py

# Specify display and device
python main.py --monitor 1 --spade-device cuda

# Mirror mode (for front-facing camera setups)
python main.py --mirror

# Disable SPADE (debug/visualization only)
python main.py --disable-spade
```

## Production Setup

The installation at Expo 2025 runs on a dedicated machine with:
- 3× OAK-D cameras connected over Ethernet
- NVIDIA GPU for SPADE inference + RealESRGAN upscaling
- Panoramic display at 3840×1280 resolution
- Continuous operation with automatic sequence rotation

## Related Repositories

| Repository | Description |
|-----------|-------------|
| [tmpl-app](https://github.com/speplinski/tmpl-app) | Standalone SDL2 renderer for pre-generated sequences |
| [tmpl-generator](https://github.com/speplinski/tmpl-generator) | Mask processing and composition pipeline |
| [tmpl-viewer-position-tracking](https://github.com/speplinski/tmpl-viewer-position-tracking) | OAK-D viewer tracking subsystem |
| [tmpl-simulation](https://github.com/speplinski/tmpl-simulation) | Simulation environment for testing without hardware |
| [tmpl-visualizer](https://github.com/speplinski/tmpl-visualizer) | Visualization tools |
| [tmpl-benchmark-app](https://github.com/speplinski/tmpl-benchmark-app) | Performance benchmarking |

## Credits

Created for the Poland Pavilion at Expo 2025 Osaka by a team including Szymon Peplinski, Paweł Gołąb, and collaborators. The installation is part of "The Most Polish Landscape" — a generative environment shaped by people's presence, rendered live in 4K, and entirely created through AI.

## License

See individual module licenses. SPADE model architecture based on [NVlabs/SPADE](https://github.com/NVlabs/SPADE).

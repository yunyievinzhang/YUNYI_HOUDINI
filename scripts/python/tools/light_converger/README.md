# Light Converger

A Houdini procedural lighting workflow combining Houdini Digital Assets and Python automation for light generation, placement, targeting, variation, and finalization.

## Overview

Light Converger was developed to simplify the creation and management of larger lighting formations while preserving direct artistic control.

The system combines reusable HDAs with supporting Python tools.

## Features

- Procedural light formation setup
- Configurable light positioning
- Artist-controlled light targets and offsets
- Randomized positional variation
- Automated Houdini control creation
- Procedural light-path projection
- Light baking and finalization
- Automated node-network creation and organization
- Artist-facing workflow controls

## Implementation

The main supporting implementation includes:

- `spot_light_converge.py`
- `spot_light_converge_ui.py`
- `convergeable_light.json`

These files contain Houdini automation for:

- procedural light generation
- node and parameter creation
- target and transform calculations
- light variation controls
- light-path projection
- procedural network management
- light baking and output
- artist-facing UI controls

## Houdini Digital Assets

Related HDAs include tools for:

- light placement
- light path projection
- light painting
- light culling
- light editing
- proxy generation
- light workflow management

These assets package different parts of the procedural lighting workflow into reusable artist-facing Houdini tools.

See [`otls/`](../../../../otls/) for the packaged assets.

## Technologies

- Houdini
- Houdini Digital Assets
- Python
- Houdini HOM
- VEX
- Arnold
- PySide / Qt

## Demo

For visual examples and workflow demonstrations:

[View Technical Art Showcase →](https://www.yunyizhangtechart.com/houdini-tools)

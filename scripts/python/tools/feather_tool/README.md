# Procedural Feather Tool

A Houdini procedural feather workflow combining Houdini Digital Assets and Python automation for feather generation, simulation setup, clustering, caching, and data management.

## Overview

The Feather Tool was developed to simplify procedural feather workflows and automate repetitive setup tasks involved in managing feather geometry and simulation data.

The system combines reusable HDAs with supporting Python tools.

## Features

- Procedural feather workflow setup
- Geometry and UV validation
- Automated Vellum workflow setup
- Feather grouping and clustering
- Procedural Houdini node creation
- Static and dynamic feather workflows
- Cache generation and loading
- Distributed feather-data loading
- Artist-facing workflow controls

## Implementation

The main supporting Python implementation is:

- `prac_func.py`

It contains Houdini automation for:

- geometry validation
- parameter management
- procedural node creation
- Vellum setup
- feather clustering
- cache management
- data loading

## Houdini Digital Assets

Related HDAs include:

- `feather_tool.hda`
- `vellum_feather.hda`

These assets package the feather setup and Vellum workflow into reusable artist-facing Houdini tools.

See [`otls/`](../../../../otls/) for the packaged assets.

## Technologies

- Houdini
- Houdini Digital Assets
- Python
- Houdini HOM
- VEX
- Vellum
- Procedural Geometry

## Demo

For visual examples and workflow demonstrations:

[View Technical Art Showcase →](https://www.yunyizhangtechart.com/)

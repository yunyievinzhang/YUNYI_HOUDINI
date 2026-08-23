# Yunyi Zhang — Houdini Technical Art & Pipeline Tools

A collection of Houdini tools and procedural systems developed using Python, VEX, Houdini HOM, and Houdini Digital Assets.

This repository focuses on artist-facing procedural workflows, lighting automation, Houdini tool development, and procedural geometry systems.

## Demo & Visual Showcase

For screenshots, tool demonstrations, and workflow examples, visit:

[Technical Art Showcase →](https://www.yunyizhangtechart.com/houdini-tools)

## Featured Tools

### Light Procedural Factory

Procedural Arnold light-instancing tool that automatically builds and organizes light generation, instancing, and artist controls.

[View Tool →](scripts/python/tools/light_procedural_factory)

### Light Converger

Procedural lighting system designed to generate and control large light formations while allowing artists to manipulate targets, offsets, variation, and baked output.

[View Tool →](scripts/python/tools/light_converger)

### Procedural Feather Tool

Feather pipeline workflow containing Houdini automation for Vellum setup, geometry validation, clustering, caching, and distributed data loading.

[View Tool →](scripts/python/tools/feather_tool)

### Wing Feather Tool

Procedural Houdini system for generating, organizing, and deforming structured wing-feather arrangements.

[View Tool →](scripts/python/tools/wing_feather)

## Houdini Digital Assets

The repository includes reusable artist-facing HDAs for lighting and procedural feather workflows.

Examples include:

- Light Camera Cull
- Light Chaser
- Light Painter
- Light Palette
- Light Path Projector
- Light Proxy Maker
- Feather Tool
- Vellum Feather
- Wing Feather
- Wing Feather Deformed

See [`otls/`](otls/) for the full collection.

## Repository Structure

- `otls/` — packaged Houdini Digital Assets
- `scripts/python/tools/` — Python implementation and supporting tool logic
- `viewer_states/` — custom Houdini viewer-state implementations
- `toolbar/` — shelf and toolbar integrations
- `config/icons/` — custom tool icons

## Technologies

Python · VEX · Houdini HOM · HDAs · PySide · Arnold · Vellum

## About

These tools are examples of personal and portfolio development.

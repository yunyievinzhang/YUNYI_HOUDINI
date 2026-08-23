# Light Procedural Factory

A Houdini procedural lighting workflow combining Python automation and Arnold light-instancing for faster, more consistent lighting setup.

## Overview

Light Procedural Factory was developed to reduce repetitive lighting setup by automatically creating and organizing the Houdini nodes required for Arnold light-instancing workflows.

The system combines Python/HOM automation with procedural Houdini workflows while keeping the generated setup accessible to artists.

## Features

- Automated Arnold light creation
- Support for multiple light types
- Procedural light-instancing setup
- Automated Houdini instance-node configuration
- Structured node-network generation
- Automatic node connection and organization
- Artist-facing procedural controls
- Reduced repetitive manual lighting setup

## Implementation

The main supporting implementation includes:

- `create_light_inst_set.py`
- `create_light_inst_set_ui.py`

These files contain Houdini automation for:

- Arnold light creation
- procedural node generation
- instance setup and configuration
- node connection and organization
- light-type-specific setup
- artist-facing UI controls

Python and Houdini HOM are used to construct and configure the lighting network programmatically.

## Houdini Digital Assets

Related lighting HDAs can be found in the repository's [`otls/`](../../../../otls/) directory.

These assets package supporting parts of the lighting workflow into reusable artist-facing Houdini tools.

## Technologies

- Houdini
- Houdini Digital Assets
- Python
- Houdini HOM
- Arnold
- Procedural Instancing
- PySide / Qt

## Demo

For visual examples and workflow demonstrations:

[View Technical Art Showcase →](https://www.yunyizhangtechart.com/houdini-tools)

# Eye Catchlight Rig

A procedural Houdini/Arnold lighting tool that preserves artist-defined eye catchlights throughout character animation.

## Overview

Eye Catchlight Rig was developed to maintain consistent and artist-controlled eye highlights on animated characters.

Artists first establish the desired catchlight appearance on a reference frame using standard Arnold lights. The tool then analyzes the relationship between the reference lights and each eyeball and generates procedural eye lights that follow the animated eyes while preserving the intended catchlight placement.

The workflow is designed to keep the initial lighting decision artist-driven while automating the repetitive task of maintaining the catchlight across animation.

## Features

- Reference-frame-based catchlight matching
- Independent left- and right-eye setup
- Procedural tracking of animated eyeballs
- Automatic calculation of eye focus and light-placement points
- Preservation of artist-defined catchlight placement
- Automatic transfer of Arnold light parameters from reference lights
- Support for Solaris / LOP eyeball geometry
- Artist-facing Houdini Digital Asset workflow
- Reduced manual eye-light adjustment across animation

## Implementation

The main supporting Python implementation is:

- `eyelight_match.py`

The matching process uses artist-placed reference lights to calculate two pieces of information for each eye:

1. A focus point on the original eyeball surface based on the reference light direction.
2. A light-placement point on a procedurally scaled representation of the eyeball based on the reference light position.

The reference light is evaluated in world space and transformed into the eyeball's local geometry space. A ray intersection against the eyeball determines the corresponding focus location.

The distance between the reference light and the eyeball center is then used to scale the tracking sphere and determine the procedural light-placement point.

The resulting locations are stored by the HDA and used to drive the generated catchlights as the eyeballs move.

Arnold-specific parameters from the artist's reference lights are also transferred automatically to the generated eye lights, preserving the original lighting setup.

## Houdini Digital Assets

The tool is packaged as:

- `hlgt.eye_light_rig.1.0.hda`

The HDA provides separate controls for the left and right eyes, including:

- Solaris / LOP geometry paths
- eyeball primitive selection
- reference light assignment
- procedural matching controls
- generated catchlight tracking

See [`otls/`](../../../../otls/) for the packaged asset.

## Technologies

- Houdini
- Houdini Digital Assets
- Python
- Houdini HOM
- Solaris / USD
- Arnold
- Procedural Lighting

## Demo

Typical workflow:

Reference Frame  
→ Place and adjust Arnold catchlights  
→ Match the desired eye highlights  
→ Generate procedural catchlights  
→ Play character animation  
→ Catchlights remain consistently positioned on the animated eyes

For visual examples and workflow demonstrations:

[View Technical Art Showcase →](https://www.yunyizhangtechart.com/houdini-tools)

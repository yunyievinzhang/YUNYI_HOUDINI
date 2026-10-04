'''
Helpers for matching eyelight positions.
'''
import hou

REQUIRED_PARM_KEYWORD=["loppath", "primpattern", "sample_lgt"]
LOCAL_LIGHT_FORWARD = hou.Vector3(0, 0, -1)

def calculate_parm(node):
    '''
    Calculate all parameters required for positioning.
    '''
    # Unlock the HDA once all required parameters are filled.
    if node.isLockedHDA() and _all_required_parms_filled(node):
        node.allowEditingOfContents()

    # Run once for each eye.
    for side in ("l", "r"):
        # Get the sample light path.
        lgt_path= node.parm(f"sample_lgt_{side}").eval()

        if not lgt_path:
            continue

        # Get the focus and location points used by the matching light.
        inner_focus_pt, outer_loc_pt=_compute_eye_points(node, lgt_path, side)

        # Set the matching point numbers.
        node.parm(f"inner_focus_group_{side}").set(str(inner_focus_pt))
        node.parm(f"outer_point_group_{side}").set(str(outer_loc_pt))

        # Also copy all Arnold-related light parameters.
        _copy_light_parameters(node, lgt_path, side)

def _all_required_parms_filled(node):
    '''
    Check whether all required parameters are filled.
    '''
    for parm in node.parms():
        if any(k in parm.name() for k in REQUIRED_PARM_KEYWORD):
            if not parm.eval():
                return False
    return True

def _copy_light_parameters(node, lgt_path, side):
    '''
    Copy all Arnold-related light parameters.
    '''
    eyelight=node.node(f"{side.upper()}_eyelight")
    sample_light=hou.node(lgt_path)

    if not eyelight or not sample_light:
        return

    for parm in sample_light.parms():
        # Copy only Arnold parameters, which use the ar_ prefix.
        if parm.name().startswith("ar_"):
            target=eyelight.parm(parm.name())
            if target:
                target.set(parm.eval())

def _compute_eye_points(node, lgt_path, side):
    '''
    Calculate the eye focus point and location point for the matching light.
    '''
    sample_lgt=hou.node(lgt_path)

    # Return early if no valid sample light is provided.
    if not sample_lgt:
        return -1, -1

    lgt_xform=sample_lgt.worldTransform()

    # Get the light position in world space.
    light_pos_w=lgt_xform.extractTranslates("srt")

    # Get the light rotation so the final pointing direction can be derived.
    rot = lgt_xform.extractRotationMatrix3()
    rot4 = hou.Matrix4(rot)

    # Rotate the default forward direction to get the final light direction.
    dir4 = hou.Vector4(
        LOCAL_LIGHT_FORWARD[0],
        LOCAL_LIGHT_FORWARD[1],
        LOCAL_LIGHT_FORWARD[2],
        0
    )
    world_dir4 = dir4 * rot4
    world_dir = hou.Vector3(world_dir4[0], world_dir4[1], world_dir4[2]).normalized()

    # Get the original eyeball geometry.
    eyeball_node=node.node(f"{side.upper()}_track").node("eyeball")
    if not eyeball_node:
        return -1, -1
    obj=eyeball_node.parent()
    geo=eyeball_node.geometry()

    # Get the light position in SOP space.
    obj_xform=obj.worldTransform()
    world_to_obj= obj_xform.inverted()
    origin_o=light_pos_w * world_to_obj

    # Get the light direction in SOP space.
    rot = world_to_obj.extractRotationMatrix3()
    rot4 = hou.Matrix4(rot)
    dir4 = hou.Vector4(world_dir[0], world_dir[1], world_dir[2], 0)
    dir_o4 = dir4 * rot4
    dir_o = hou.Vector3(dir_o4[0], dir_o4[1], dir_o4[2]).normalized()

    # Intersect the light direction with the front of the eye to find the focus point.
    hit_pos=hou.Vector3()
    hit_nrm=hou.Vector3()
    hit_uvw=hou.Vector3()
    prim=geo.intersect(origin_o, dir_o, hit_pos,hit_nrm, hit_uvw) 

    inner_focus_ptnum=-1
    if prim !=-1:
        inner_focus_ptnum=geo.nearestPoint(hit_pos).number()

    # Find the location point on the rescaled eyeball sphere for the matching light.
    outer_loc_ptnum=_compute_scaled_projection(
        node, side, geo, obj_xform, world_to_obj, light_pos_w
    )

    return inner_focus_ptnum, outer_loc_ptnum

def _compute_scaled_projection(node, side, geo, obj_xform, world_to_obj, light_pos_w):
    '''
    Calculate the matching light location point, usually on the rescaled eyeball sphere.
    '''
    # Get the original eyeball sphere radius in world space.
    bbox=geo.boundingBox()
    center_obj= bbox.center()
    radius_obj=max(bbox.sizevec())*0.5
    radius_w = (hou.Vector3(radius_obj, 0, 0) * obj_xform).length()

    # Get the sphere center in world space.
    center_w =  center_obj * obj_xform

    # Use the light-to-center distance as the rescaled radius and derive the scale value.
    distance= (light_pos_w - center_w).length()
    scale= distance/radius_w if radius_w !=0 else 1.0

    # Set the scale value.
    node.parm(f"scale_{side}").set(scale)
    # Get the scaled eyeball sphere geometry.
    scaled_geo=node.node(f"{side.upper()}_track").node("scale_eyeball").geometry()

    # Get the light intersection point on the rescaled sphere.
    direction= (light_pos_w - center_w).normalized()
    scaled_pos_w= center_w + direction * (radius_w * scale)
    scaled_pos_o = scaled_pos_w * world_to_obj
    outer_loc_ptnum=scaled_geo.nearestPoint(scaled_pos_o).number()

    return outer_loc_ptnum

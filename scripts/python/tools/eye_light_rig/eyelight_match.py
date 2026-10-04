'''
眼神光位置匹配需要的模块
'''
import hou

REQUIRED_PARM_KEYWORD=["loppath", "primpattern", "sample_lgt"]
LOCAL_LIGHT_FORWARD = hou.Vector3(0, 0, -1)

def calculate_parm(node):
    '''
    计算定位需要的所有参数
    '''
    # 如果参数齐全了就解锁HDA
    if node.isLockedHDA() and _all_required_parms_filled(node):
        node.allowEditingOfContents()

    # 左右眼都要执行一遍
    for side in ("l", "r"):
        # 获取样例灯光的路径
        lgt_path= node.parm(f"sample_lgt_{side}").eval()

        if not lgt_path:
            continue

        # 获取聚焦点和定位点作为匹配灯光的位置
        inner_focus_pt, outer_loc_pt=_compute_eye_points(node, lgt_path, side)

        # 设置匹配点号
        node.parm(f"inner_focus_group_{side}").set(str(inner_focus_pt))
        node.parm(f"outer_point_group_{side}").set(str(outer_loc_pt))

        # 另外拷贝所有灯光参数（arnold相关的）
        _copy_light_parameters(node, lgt_path, side)

def _all_required_parms_filled(node):
    '''
    检查是否所有必要的参数齐全了
    '''
    for parm in node.parms():
        if any(k in parm.name() for k in REQUIRED_PARM_KEYWORD):
            if not parm.eval():
                return False
    return True

def _copy_light_parameters(node, lgt_path, side):
    '''
    拷贝所有灯光参数(Arnold相关的)
    '''
    eyelight=node.node(f"{side.upper()}_eyelight")
    sample_light=hou.node(lgt_path)

    if not eyelight or not sample_light:
        return

    for parm in sample_light.parms():
        # 只复制那些ar开头的（即Arnold有关的）
        if parm.name().startswith("ar_"):
            target=eyelight.parm(parm.name())
            if target:
                target.set(parm.eval())

def _compute_eye_points(node, lgt_path, side):
    '''
    计算眼部聚焦点于定位点（匹配灯光的2大定位）
    '''
    sample_lgt=hou.node(lgt_path)

    # 如果没有填写样例灯光直接返还
    if not sample_lgt:
        return -1, -1

    lgt_xform=sample_lgt.worldTransform()

    # 获取灯光位置（世界坐标）
    light_pos_w=lgt_xform.extractTranslates("srt")

    # 获取灯光旋转用于获取灯光最后指向的方向
    rot = lgt_xform.extractRotationMatrix3()
    rot4 = hou.Matrix4(rot)

    # 给默认方向施加偏转来获得最后灯光的方向
    dir4 = hou.Vector4(
        LOCAL_LIGHT_FORWARD[0],
        LOCAL_LIGHT_FORWARD[1],
        LOCAL_LIGHT_FORWARD[2],
        0
    )
    world_dir4 = dir4 * rot4
    world_dir = hou.Vector3(world_dir4[0], world_dir4[1], world_dir4[2]).normalized()

    # 获取眼球几何体（原始大小）
    eyeball_node=node.node(f"{side.upper()}_track").node("eyeball")
    if not eyeball_node:
        return -1, -1
    obj=eyeball_node.parent()
    geo=eyeball_node.geometry()

    # 获取灯光在sop层级中的位置
    obj_xform=obj.worldTransform()
    world_to_obj= obj_xform.inverted()
    origin_o=light_pos_w * world_to_obj

    # 获取灯光在sop层级中的方向
    rot = world_to_obj.extractRotationMatrix3()
    rot4 = hou.Matrix4(rot)
    dir4 = hou.Vector4(world_dir[0], world_dir[1], world_dir[2], 0)
    dir_o4 = dir4 * rot4
    dir_o = hou.Vector3(dir_o4[0], dir_o4[1], dir_o4[2]).normalized()

    # 获取灯光方向与眼前的交叉点。结果也就是匹配灯光的聚焦点。
    hit_pos=hou.Vector3()
    hit_nrm=hou.Vector3()
    hit_uvw=hou.Vector3()
    prim=geo.intersect(origin_o, dir_o, hit_pos,hit_nrm, hit_uvw) 

    inner_focus_ptnum=-1
    if prim !=-1:
        inner_focus_ptnum=geo.nearestPoint(hit_pos).number()

    # 获取灯光处在rescaled的眼球球体上的定位点，也就是匹配灯光的位置
    outer_loc_ptnum=_compute_scaled_projection(
        node, side, geo, obj_xform, world_to_obj, light_pos_w
    )

    return inner_focus_ptnum, outer_loc_ptnum

def _compute_scaled_projection(node, side, geo, obj_xform, world_to_obj, light_pos_w):
    '''
    计算匹配灯光的定位点, （一般来说是rescale后的眼球球体上的某一个点）
    '''
    # 获取眼球球体（初始大小）的半径（世界坐标下）
    bbox=geo.boundingBox()
    center_obj= bbox.center()
    radius_obj=max(bbox.sizevec())*0.5
    radius_w = (hou.Vector3(radius_obj, 0, 0) * obj_xform).length()

    # 获取世界坐标的球体中心
    center_w =  center_obj * obj_xform

    # 通过得到灯光与球心距离，得到一个rescale过后的半径，以此来得到scale的数值是多少
    distance= (light_pos_w - center_w).length()
    scale= distance/radius_w if radius_w !=0 else 1.0

    # 设置scale大小
    node.parm(f"scale_{side}").set(scale)
    # 获取scale过后的眼球球体几何体
    scaled_geo=node.node(f"{side.upper()}_track").node("scale_eyeball").geometry()

    # 获取灯光与rescale后的球体的交叉点（匹配灯光位于的位置）
    direction= (light_pos_w - center_w).normalized()
    scaled_pos_w= center_w + direction * (radius_w * scale)
    scaled_pos_o = scaled_pos_w * world_to_obj
    outer_loc_ptnum=scaled_geo.nearestPoint(scaled_pos_o).number()

    return outer_loc_ptnum

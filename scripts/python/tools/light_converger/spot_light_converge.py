import hou
from  .util_exp import *
PROJ_NODE_VERSION="1.1"
MARKER_NODE_VERSION="1.0"

def create_light_formation(light_group_name, columns, rows, light_icon_size, spacing, marker_height, ground_height,  light_node_type_name ):
        '''
        创建灯光阵
        '''
        # 创建subnet包装灯光阵型并命名
        obj = hou.node("/obj")
        subnet = obj.createNode("subnet", f"{light_group_name}_formation")
        subnet.moveToGoodPosition()

        # 设置初始的灯光位置r高度
        offset = 2.0

        # 阵型中心
        center_x = (columns - 1) * spacing / 2.0
        center_z = (rows - 1) * spacing / 2.0
        center_y = 0.0 

        # 创建Marker总控制节点，置于阵型中心上方Marker Height高度
        marker = subnet.createNode(f"hlgt::light_marker::{MARKER_NODE_VERSION}", f"marker")
        marker.moveToGoodPosition()
        marker.parmTuple("t").set((center_x, center_y + marker_height, center_z))
        marker.parm("light_type").set(light_node_type_name)

        # 提取Marker上控制面板参数
        total_light_cone_angle=marker.parm("light_cone_angle")
        total_submarker_scale=marker.parm("submarker_scale")
        total_sphere_scale=marker.parm("sphere_scale")
        total_light_icon_scale=marker.parm("light_icon_scale")
        ground_height_parm=marker.parm("ground_height")

        #设置灯光图标大小
        if light_icon_size:
            total_light_icon_scale.set(light_icon_size)
        # 设置地面高度
        if ground_height:
            ground_height_parm.set(ground_height)

        # 创建灯光方向控制网格
        grid_node=create_pos_grid(subnet, rows, columns, spacing)

        # 开始按照阵型逐个创建：1. 方向控制球体系统。2. 方向控制submarker系统
        for row in range(rows):
            for col in range(columns):
                x = col * spacing
                z = row * spacing
                y = 0.0 

                #聚光灯光束牵引球体并添加按钮
                sphere = subnet.createNode("geo", f"sphere_{row}_{col}")
                sphere_node = sphere.createNode("sphere", "sphere")
                sphere_node.parm("type").set("poly")
                sphere_node.parm("scale").set(0.5)
                sphere_node.setDisplayFlag(True)
                sphere_node.setRenderFlag(True)
                sphere.parm("scale").set(total_sphere_scale)
                add_sphere_button(sphere)

                #清理球体节点
                file_node = sphere.node("file1")
                if file_node:
                    file_node.destroy()
        
                # 牵引球体Rivet控制
                rivet_node=subnet.createNode("rivet", f"rivet_{row}_{col}")
                rivet_node.parm("rivetsop").set(grid_node.path())
                point_index=rivet_index_mapper(row, col, columns)
                rivet_node.parm("rivetgroup").set(str(point_index))
                rivet_node.parm("rivetuseattribs").set(1)
                sphere.setInput(0, rivet_node)
                
                # 创建Arnold聚光灯
                light = subnet.createNode(light_node_type_name, f"{light_group_name}_at_{row}_{col}")
                light.parm("ar_light_type").set(2)

                #创建控制灯光捆绑Marker
                sub_marker = subnet.createNode("null", f"submarker_{row}_{col}")
                sub_marker.parmTuple("t").set((x, y + offset, z))
                sub_marker.parm("scale").set(total_submarker_scale)
                sub_marker.moveToGoodPosition()
                light.setInput(0, sub_marker)

                #创建灯光方向投射节点
                light_projector=subnet.createNode(f"hlgt::light_path_projector::{PROJ_NODE_VERSION}", f"light_proj_{row}_{col}")
                sub_marker.parmTuple("t").set(light_projector.parmTuple("output_pos"))

                # 加入了总控制关联以及随机函数的表达式
                index_seed=row*columns+col
                ground_height_custom_random_string=(f"""ch("../marker/ground_height")+"""
                                                    f"""ch("../marker/ground_height_var_influence")*"""
                                                    f"""fit01(rand({index_seed}*ch("../marker/ground_height_var_seed")),"""
                                                    f"""-ch("../marker/ground_height_var_scale"), """
                                                    f"""ch("../marker/ground_height_var_scale"))""")
                convergence_custom_random_string=(f"""clamp(ch("../marker/convergence")+"""
                                                  f"""ch("../marker/convergence_var_influence")*"""
                                                  f"""fit01(rand({index_seed}*ch("../marker/convergence_var_seed")),"""
                                                  f"""-ch("../marker/convergence_var_scale"),""" 
                                                  f"""ch("../marker/convergence_var_scale")), 0, 1)""")

                # 设置灯光方向投射节点的参数
                light_projector.parm("ground_height").setExpression(ground_height_custom_random_string, language=hou.exprLanguage.Hscript)
                light_projector.parm("blend").setExpression(convergence_custom_random_string, language=hou.exprLanguage.Hscript)
                # A点为Marker
                light_projector.parm("parent_a_marker").set(marker.path())
                # B点为球体
                light_projector.parm("parent_b_marker").set(sphere.path())

                # 关注AB点位移动信息
                if hou.node(marker.path()):
                    marker_node=hou.node(marker.path())
                    light_projector.parmTuple("parent_a_pos").set(marker_node.parmTuple("t"))
                if hou.node(sphere.path()):
                    sphere_node=hou.node(sphere.path())
                    light_projector.parmTuple("parent_b_pos").set(sphere_node.parmTuple("t"))
                
                # 标明总位移动物体为subnet
                light_projector.parm("master").set(sphere.parent().path())
                # 更新一下位置移动
                light_projector.parm("update").pressButton()
                light_projector.moveToGoodPosition()
                
               # 让所有灯光看向球体
                sphere_path = sphere.path()
                light.parm("lookatpath").set(sphere_path)
                light.parm("l_iconscale").set(total_light_icon_scale)
                light.parm("ar_cone_angle").set(total_light_cone_angle)
                light.moveToGoodPosition()

                # 添加灯光上的控制按钮
                add_light_control_button(light)
    
        subnet.layoutChildren()

        # 为了更清晰美观的外观设置netbox
        set_boxes(rows,columns,subnet, light_group_name)

        # 更新位置
        marker.parm("update_button").pressButton()

def set_boxes(rows, cols, subnet, light_group_name):
        '''
        设置network box分类
        '''
        # 设置间距
        x_spacing = 4.0
        y_spacing = 3.0
        netbox_spacing = 5.0

        # 创建network box
        netbox1 = subnet.createNetworkBox()
        netbox1.setComment("灯光以及Submarker")
        netbox2 = subnet.createNetworkBox()
        netbox2.setComment("牵引球体")
        netbox3 = subnet.createNetworkBox()
        netbox3.setComment("灯光位置计算节点")

        netbox1_nodes = []
        netbox2_nodes = []
        netbox3_nodes = []

        # 每一个box中排列每一个节点
        for r in range(rows):
            for c in range(cols):
                idx=f"{r}_{c}"
                x_pos=c*x_spacing
                y_pos=-r*y_spacing

                # 找到submarker, 灯光，球体，rivet 以及light_proj节点
                submarker_node=subnet.node(f"submarker_{idx}")
                light_node=subnet.node(f"{light_group_name}_at_{idx}")
                sphere_node=subnet.node(f"sphere_{idx}")
                rivet_node=subnet.node(f"rivet_{idx}")
                light_proj_node=subnet.node(f"light_proj_{idx}")
                
                # 移动它们到合适位置
                submarker_node.setPosition(hou.Vector2(x_pos, y_pos))
                light_node.setPosition(hou.Vector2(x_pos, y_pos-1.0))
                sphere_node.setPosition(hou.Vector2(x_pos,y_pos-1.0))
                rivet_node.setPosition(hou.Vector2(x_pos, y_pos))
                light_proj_node.setPosition(hou.Vector2(x_pos, y_pos))

                netbox1_nodes.append(submarker_node)
                netbox1_nodes.append(light_node)
                netbox2_nodes.append(rivet_node)                
                netbox2_nodes.append(sphere_node)
                netbox3_nodes.append(light_proj_node)

        # 将各类节点加入相应的netbox中
        for node in netbox1_nodes:
            netbox1.addItem(node)
        for node in netbox2_nodes:
            netbox2.addItem(node)
        for node in netbox3_nodes:
            netbox3.addItem(node)

        netbox1.fitAroundContents()
        netbox2.fitAroundContents()
        netbox3.fitAroundContents()

        # 将三个box各自移动到合适位置
        netbox1_width=netbox1.size().x()
        netbox2.setPosition(netbox1.position()+hou.Vector2(netbox1_width + netbox_spacing, 0))

        netbox2_width=netbox2.size().x()
        netbox3.setPosition(netbox2.position()+hou.Vector2(netbox2_width+netbox_spacing, 0))

        # 设置三个box颜色
        netbox1.setColor(hou.Color((1.0, 0.9137, 0.0)))
        netbox2.setColor(hou.Color((0.7, 0.0, 0.0)))
        netbox3.setColor(hou.Color((0.0, 0.5882, 1.0)))

        # 设置Marker和它的box的位置以及颜色
        marker_node=subnet.node("marker")
        marker_pos=netbox1.position()+hou.Vector2(-3, netbox1.size().y()-1)
        marker_node.setPosition(marker_pos)

        netbox_marker = subnet.createNetworkBox()
        netbox_marker.setComment("总控制Marker")
        netbox_marker.addItem(marker_node)
        netbox_marker.fitAroundContents()
        netbox_marker.setColor(hou.Color((0.0, 0.6, 0.0)))

        # 设置control_grid和它的box以及位置颜色
        grid_node=subnet.node("control_grid")
        grid_pos=netbox1.position()+hou.Vector2(-3, netbox1.size().y()-4)
        grid_node.setPosition(grid_pos)
        
        netbox_grid  = subnet.createNetworkBox()
        netbox_grid.setComment("球体控制器")
        netbox_grid.addItem(grid_node)
        netbox_grid.fitAroundContents()
        netbox_grid.setColor(hou.Color((1.0, 0.6, 0.0)))

        # 几个input节点摆的好看一点
        for i in range(4):
            subnet.item(f"{i+1}").setPosition(marker_pos+hou.Vector2(-3, i))

def create_pos_grid(subnet, row, col, space):
        '''
        设置牵引球体的控制网格
        '''
        #创建网格节点并设置大小
        grid_node=subnet.createNode("geo", "control_grid")
        grid_node.moveToGoodPosition()
        grid_geo=grid_node.createNode("grid")
        grid_geo.moveToGoodPosition()
        grid_length=(col-1)*space
        grid_width=(row-1)*space

        grid_geo.parmTuple("size").set(hou.Vector2(grid_length, grid_width))
        grid_geo.parmTuple("t").set(hou.Vector3(grid_length/2, 0, grid_width/2))
        grid_geo.parm("rows").set(row)
        grid_geo.parm("cols").set(col)

        #设置法线以及up vector
        python_node=grid_node.createNode("python", "add_attrib")
        python_node.setInput(0, grid_geo)

        python_node.parm("python").set(SET_N_AND_UP_SCRIPT)

        # 创建抖动节点用于位置随机
        jitter_node=grid_node.createNode("pointjitter", "jitter_points")
        jitter_node.setInput(0, python_node)
        out_node=grid_node.createNode("null","grid_out")
        out_node.setInput(0, jitter_node)

        out_node.setDisplayFlag(True)
        out_node.setRenderFlag(True)
        grid_node.layoutChildren()

        add_grid_control_button(grid_node,jitter_node)
        return grid_node

def rivet_index_mapper( r,c, cols):
        '''
        根据球体位置计算rivet节点对应的网格点位置
        '''
        point_index=r*cols+c
        return point_index

def add_sphere_button(sphere):
        '''
        添加球体节点上的按钮
        '''
        parm_group=sphere.parmTemplateGroup()

        sphere_tab=hou.FolderParmTemplate("sphere_control_tab", "球体控制", folder_type=hou.folderType.Tabs)
        
        # 烘焙球体当前位置以脱离rivet掌控
        bake_pos_button=hou.ButtonParmTemplate(
            name="bake_pos_button",
            label="烘焙位置-脱离rivet",
            script_callback=BAKE_POS_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
        )
        # 是否保留当前位移Toggle
        if_keep_offset=hou.ToggleParmTemplate("if_keep_offset", "是否保留当前位移", default_value=False)
        
        # 恢复rivet牵引
        recover_rivet_button=hou.ButtonParmTemplate(
            name="recover_rivet_button",
            label="恢复rivet牵引",
            script_callback=RECOVER_RIVET_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
        )

        # 添加球体控制按钮
        sphere_tab.addParmTemplate(bake_pos_button)
        sphere_tab.addParmTemplate(if_keep_offset)
        sphere_tab.addParmTemplate(recover_rivet_button)
        parm_group.append(sphere_tab)

        sphere.setParmTemplateGroup(parm_group)

def add_light_control_button(light):
        '''
        增加灯光节点上的按钮
        '''
        # 加入灯光控制tab
        light_tab=hou.FolderParmTemplate("light_control_tab", "灯光控制", folder_type=hou.folderType.Simple)

        #加入灯光方向烘焙
        bake_dir_button=hou.ButtonParmTemplate(
            name="bake_dir_button",
            label="烘焙方向-脱离球体牵引控制",
            script_callback=BAKE_DIR_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        #加入灯光位置烘焙
        bake_pos_button=hou.ButtonParmTemplate(
            name="bake_pos_button",
            label="烘焙位置-脱离submarker",
            script_callback=BAKE_POS_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        #恢复球体牵引
        recover_lookat_button=hou.ButtonParmTemplate(
            name="recover_lookat_button",
            label="恢复球体牵引",
            script_callback=RECOVER_LOOKAT_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )
        #是否保留当前位移Toggle
        if_keep_offset=hou.ToggleParmTemplate("if_keep_offset", "是否保留当前位移", default_value=False)

        recover_submarker_button=hou.ButtonParmTemplate(
            name="recover_submarker_button",
            label="恢复submarker牵引",
            script_callback=RECOVER_SUBMARKER_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        #移除开角总控
        remove_cone_button=hou.ButtonParmTemplate(
            name="remove_cone_button",
            label="脱离开角总控",
            script_callback=BAKE_CONE_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        #添加开角总控
        add_cone_button=hou.ButtonParmTemplate(
            name="add_cone_button",
            label="添加开角总控",
            script_callback=RECOVER_CONE_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        # 添加灯光控制按钮
        light_tab.addParmTemplate(bake_dir_button)
        light_tab.addParmTemplate(bake_pos_button)
        light_tab.addParmTemplate(recover_lookat_button)
        light_tab.addParmTemplate(if_keep_offset)
        light_tab.addParmTemplate(recover_submarker_button)
        light_tab.addParmTemplate(remove_cone_button)
        light_tab.addParmTemplate(add_cone_button)
        light_parm_group = light.parmTemplateGroup()
        light_parm_group.append(light_tab)
        light.setParmTemplateGroup(light_parm_group)
     
def add_grid_control_button( control_grid, jitter_node):
        '''
        添加控制网格按钮
        '''
        parm_group = control_grid.parmTemplateGroup()
        tab=hou.FolderParmTemplate("grid_control_tab", "控制", folder_type=hou.folderType.Tabs)

        # 加入并关联jitter的全部主要按钮
        scale_parm=hou.FloatParmTemplate(
                name="jitter_scale",
                label="扰动幅度",
                num_components=1,
                default_value=(1.0,),
            )

        axis_scale_parm=hou.FloatParmTemplate(
            name="jitter_axisscale",
            label="扰动轴向",
            num_components=3,       
            default_value=(1.0, 1.0, 1.0)
        )

        seed_parm=hou.FloatParmTemplate(
                name="jitter_seed",
                label="扰动种子",
                num_components=1,
                default_value=(1.0,),
            )
        
        # 添加网格控制按钮
        tab.addParmTemplate(scale_parm)
        tab.addParmTemplate(axis_scale_parm)
        tab.addParmTemplate(seed_parm)
        parm_group.append(tab)
        control_grid.setParmTemplateGroup(parm_group)

        jitter_node.parm("scale").set(control_grid.parm("jitter_scale"))
        jitter_node.parmTuple("axisscale").set(control_grid.parmTuple("jitter_axisscale"))
        jitter_node.parm("seed").set(control_grid.parm("jitter_seed"))

def calculate_path(node):
    '''
    计算灯光牵引位置
    '''
    
    # 标明A 点， B 点还有母点。聚集状况与地面高度
    parent_a_path = node.parm("parent_a_marker").eval()
    parent_b_path = node.parm("parent_b_marker").eval()
    master_path = node.parm("master").eval()
    blend = node.parm("blend").eval()
    ground_height = node.parm("ground_height").eval()
    
    parent_a = hou.node(parent_a_path)
    parent_b = hou.node(parent_b_path)
    master=hou.node(master_path)

    # 获取A 点与B点的位置，以及母点位置
    pos_a = parent_a.worldTransform().extractTranslates()
    pos_b = parent_b.worldTransform().extractTranslates()
    pos_master=master.worldTransform().extractTranslates()

    # 如图所表示, 我们需要计算AC到AB的投射是多少（C位于B地面高度设定处，垂直于B）
    # 投射计算公式 (a 投射到b) ((a . b)/ (len(b))^2)*b. 我们的案例下，我们要计算AC投射到AB的向量。
    #       
    #  A .
    #     .        . 
    #         .            .  
    #              .          C    
    #                  .       
    #                      .
    #                        B
    vec_a = hou.Vector3(pos_a)
    vec_b = hou.Vector3(pos_b)
    vec_c = hou.Vector3(pos_b+hou.Vector3([0,ground_height,0]))
    
    # 计算线段AB 与 AC
    ab = vec_b - vec_a
    ac = vec_c - vec_a

    # 计算ab长度
    ab_length_squared = ab.lengthSquared()
    # 按照计算新的点的位置
    t = ac.dot(ab) / ab_length_squared
    proj_point = vec_a + t * ab
    
    # 计算在考虑聚集度调整后的位置(我们要从初始灯光位置移动多少)
    new_pos = vec_c * (1 - blend) + proj_point * blend
    
    # 输出新的位置
    vec_master_pos=hou.Vector3(pos_master)
    new_pos-=vec_master_pos
    node.parmTuple("output_pos").set(new_pos)

def update_all_proj(node):
    '''
    更新全部的投射节点输出位置
    '''
    parent = node.parent(); 
    target_type = f'hlgt::light_path_projector::{PROJ_NODE_VERSION}' 
    button_name = 'update'
    for child in parent.children():
        if child.type().name() == target_type and child.parm(button_name):
            child.parm(button_name).pressButton() 

def export_and_bake_lights(node):
    '''
    输出并烘焙灯光参数
    '''
    parent=node.parent()
    light_type=node.parm("light_type").eval()
    initial_pos=parent.position()
    
    light_dict={}
    light_node_list=[]
    # 先记录每一个灯光应该烘焙出的位置旋转开角大小以及图标大小
    for child in parent.children():
        if child.type().name() == light_type:
            translate=baked_translate(child)
            rotation=baked_rotation(child)
            cone_angle=child.parm("ar_cone_angle").eval()
            icon_scale=child.parm("l_iconscale").eval()
            light_dict[child.name()]=[translate, rotation, cone_angle, icon_scale]
            light_node_list.append(child)

    # 复制到obj层级
    hou.copyNodesTo(light_node_list, hou.node("/obj"))
    
    obj_node=hou.node("/obj")

    # 创建network box
    output_netbox = obj_node.createNetworkBox()
    output_netbox.setComment("输出灯光")
    
    # 将提取出的对应灯光信息附加到对应的灯光上
    for _, (light_name, light_transform) in enumerate(light_dict.items()):
        light_node=obj_node.node(light_name)
        light_translate=light_transform[0]
        light_rotation=light_transform[1]
        cone_angle=light_transform[2]
        icon_scale=light_transform[3]

        # 设置灯光的位移和旋转
        light_node.parmTuple("t").set(light_translate)
        light_node.parmTuple("r").set(light_rotation)

        cone_angle_parm=light_node.parm("ar_cone_angle")
        icon_scale_parm=light_node.parm("l_iconscale")
        # 取消开角与图标大小的参数引用
        if cone_angle_parm.expression():
            cone_angle_parm.deleteAllKeyframes()
        if icon_scale_parm.expression():
            icon_scale_parm.deleteAllKeyframes()

        # 设置开角与图标大小以及清空球体迁移
        cone_angle_parm.set(cone_angle)
        icon_scale_parm.set(icon_scale)
        light_node.parm("lookatpath").set("")
        
        # 删除掉灯光节点上的按钮
        light_ptg=light_node.parmTemplateGroup()
        light_ptg.remove(light_ptg.find("light_control_tab"))
        light_node.setParmTemplateGroup(light_ptg)

        # 加入到netbox中
        output_netbox.addItem(light_node)

    # 将 netbox放到subnet旁边
    output_netbox.fitAroundContents()
    output_netbox.setPosition(initial_pos+hou.Vector2(2.0,0.0))

def baked_translate(node):
    '''
    烘焙位置
    '''
    world_transform=node.worldTransform()
    translate=world_transform.extractTranslates()
    return translate

def baked_rotation(node):
    '''
    烘焙旋转
    '''
    world_transform=node.worldTransform()
    rotation=world_transform.extractRotates()
    return rotation

import hou
from  .util_exp import *
PROJ_NODE_VERSION="1.1"
MARKER_NODE_VERSION="1.0"

def create_light_formation(light_group_name, columns, rows, light_icon_size, spacing, marker_height, ground_height,  light_node_type_name ):
        '''
        Create the light formation.
        '''
        # Create and name the subnet that contains the light formation.
        obj = hou.node("/obj")
        subnet = obj.createNode("subnet", f"{light_group_name}_formation")
        subnet.moveToGoodPosition()

        # Initial height offset for the light positions.
        offset = 2.0

        # Formation center.
        center_x = (columns - 1) * spacing / 2.0
        center_z = (rows - 1) * spacing / 2.0
        center_y = 0.0 

        # Create the master marker above the formation center by marker_height.
        marker = subnet.createNode(f"hlgt::light_marker::{MARKER_NODE_VERSION}", f"marker")
        marker.moveToGoodPosition()
        marker.parmTuple("t").set((center_x, center_y + marker_height, center_z))
        marker.parm("light_type").set(light_node_type_name)

        # Fetch the marker control-panel parameters.
        total_light_cone_angle=marker.parm("light_cone_angle")
        total_submarker_scale=marker.parm("submarker_scale")
        total_sphere_scale=marker.parm("sphere_scale")
        total_light_icon_scale=marker.parm("light_icon_scale")
        ground_height_parm=marker.parm("ground_height")

        # Set the light icon size.
        if light_icon_size:
            total_light_icon_scale.set(light_icon_size)
        # Set the ground height.
        if ground_height:
            ground_height_parm.set(ground_height)

        # Create the light-direction control grid.
        grid_node=create_pos_grid(subnet, rows, columns, spacing)

        # Build each formation element: the direction-control sphere and submarker systems.
        for row in range(rows):
            for col in range(columns):
                x = col * spacing
                z = row * spacing
                y = 0.0 

                # Create the sphere that attracts the spotlight beam and add its controls.
                sphere = subnet.createNode("geo", f"sphere_{row}_{col}")
                sphere_node = sphere.createNode("sphere", "sphere")
                sphere_node.parm("type").set("poly")
                sphere_node.parm("scale").set(0.5)
                sphere_node.setDisplayFlag(True)
                sphere_node.setRenderFlag(True)
                sphere.parm("scale").set(total_sphere_scale)
                add_sphere_button(sphere)

                # Remove the default file node from the sphere geo.
                file_node = sphere.node("file1")
                if file_node:
                    file_node.destroy()
        
                # Add rivet control for the attraction sphere.
                rivet_node=subnet.createNode("rivet", f"rivet_{row}_{col}")
                rivet_node.parm("rivetsop").set(grid_node.path())
                point_index=rivet_index_mapper(row, col, columns)
                rivet_node.parm("rivetgroup").set(str(point_index))
                rivet_node.parm("rivetuseattribs").set(1)
                sphere.setInput(0, rivet_node)
                
                # Create the Arnold spotlight.
                light = subnet.createNode(light_node_type_name, f"{light_group_name}_at_{row}_{col}")
                light.parm("ar_light_type").set(2)

                # Create the submarker that drives the light bundle.
                sub_marker = subnet.createNode("null", f"submarker_{row}_{col}")
                sub_marker.parmTuple("t").set((x, y + offset, z))
                sub_marker.parm("scale").set(total_submarker_scale)
                sub_marker.moveToGoodPosition()
                light.setInput(0, sub_marker)

                # Create the light-direction projection node.
                light_projector=subnet.createNode(f"hlgt::light_path_projector::{PROJ_NODE_VERSION}", f"light_proj_{row}_{col}")
                sub_marker.parmTuple("t").set(light_projector.parmTuple("output_pos"))

                # Add expressions for master-control links and randomization.
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

                # Set parameters on the light-direction projection node.
                light_projector.parm("ground_height").setExpression(ground_height_custom_random_string, language=hou.exprLanguage.Hscript)
                light_projector.parm("blend").setExpression(convergence_custom_random_string, language=hou.exprLanguage.Hscript)
                # Point A is the marker.
                light_projector.parm("parent_a_marker").set(marker.path())
                # Point B is the sphere.
                light_projector.parm("parent_b_marker").set(sphere.path())

                # Track the current positions of points A and B.
                if hou.node(marker.path()):
                    marker_node=hou.node(marker.path())
                    light_projector.parmTuple("parent_a_pos").set(marker_node.parmTuple("t"))
                if hou.node(sphere.path()):
                    sphere_node=hou.node(sphere.path())
                    light_projector.parmTuple("parent_b_pos").set(sphere_node.parmTuple("t"))
                
                # Use the subnet as the master transform object.
                light_projector.parm("master").set(sphere.parent().path())
                # Refresh the projected position.
                light_projector.parm("update").pressButton()
                light_projector.moveToGoodPosition()
                
               # Aim every light at its sphere.
                sphere_path = sphere.path()
                light.parm("lookatpath").set(sphere_path)
                light.parm("l_iconscale").set(total_light_icon_scale)
                light.parm("ar_cone_angle").set(total_light_cone_angle)
                light.moveToGoodPosition()

                # Add control buttons to the light.
                add_light_control_button(light)
    
        subnet.layoutChildren()

        # Organize the node graph into network boxes for readability.
        set_boxes(rows,columns,subnet, light_group_name)

        # Refresh positions.
        marker.parm("update_button").pressButton()

def set_boxes(rows, cols, subnet, light_group_name):
        '''
        Categorize nodes into network boxes.
        '''
        # Set layout spacing.
        x_spacing = 4.0
        y_spacing = 3.0
        netbox_spacing = 5.0

        # Create network boxes.
        netbox1 = subnet.createNetworkBox()
        netbox1.setComment("Lights and Submarkers")
        netbox2 = subnet.createNetworkBox()
        netbox2.setComment("Attraction Spheres")
        netbox3 = subnet.createNetworkBox()
        netbox3.setComment("Light Position Calculation Nodes")

        netbox1_nodes = []
        netbox2_nodes = []
        netbox3_nodes = []

        # Arrange each node inside its box.
        for r in range(rows):
            for c in range(cols):
                idx=f"{r}_{c}"
                x_pos=c*x_spacing
                y_pos=-r*y_spacing

                # Find the submarker, light, sphere, rivet, and light_proj nodes.
                submarker_node=subnet.node(f"submarker_{idx}")
                light_node=subnet.node(f"{light_group_name}_at_{idx}")
                sphere_node=subnet.node(f"sphere_{idx}")
                rivet_node=subnet.node(f"rivet_{idx}")
                light_proj_node=subnet.node(f"light_proj_{idx}")
                
                # Move them to suitable positions.
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

        # Add each category of nodes to its corresponding network box.
        for node in netbox1_nodes:
            netbox1.addItem(node)
        for node in netbox2_nodes:
            netbox2.addItem(node)
        for node in netbox3_nodes:
            netbox3.addItem(node)

        netbox1.fitAroundContents()
        netbox2.fitAroundContents()
        netbox3.fitAroundContents()

        # Move the three boxes into suitable positions.
        netbox1_width=netbox1.size().x()
        netbox2.setPosition(netbox1.position()+hou.Vector2(netbox1_width + netbox_spacing, 0))

        netbox2_width=netbox2.size().x()
        netbox3.setPosition(netbox2.position()+hou.Vector2(netbox2_width+netbox_spacing, 0))

        # Set the colors for the three boxes.
        netbox1.setColor(hou.Color((1.0, 0.9137, 0.0)))
        netbox2.setColor(hou.Color((0.7, 0.0, 0.0)))
        netbox3.setColor(hou.Color((0.0, 0.5882, 1.0)))

        # Set the marker and its box position and color.
        marker_node=subnet.node("marker")
        marker_pos=netbox1.position()+hou.Vector2(-3, netbox1.size().y()-1)
        marker_node.setPosition(marker_pos)

        netbox_marker = subnet.createNetworkBox()
        netbox_marker.setComment("Master Control Marker")
        netbox_marker.addItem(marker_node)
        netbox_marker.fitAroundContents()
        netbox_marker.setColor(hou.Color((0.0, 0.6, 0.0)))

        # Set the control_grid and its box position and color.
        grid_node=subnet.node("control_grid")
        grid_pos=netbox1.position()+hou.Vector2(-3, netbox1.size().y()-4)
        grid_node.setPosition(grid_pos)
        
        netbox_grid  = subnet.createNetworkBox()
        netbox_grid.setComment("Sphere Controller")
        netbox_grid.addItem(grid_node)
        netbox_grid.fitAroundContents()
        netbox_grid.setColor(hou.Color((1.0, 0.6, 0.0)))

        # Place the input nodes more neatly.
        for i in range(4):
            subnet.item(f"{i+1}").setPosition(marker_pos+hou.Vector2(-3, i))

def create_pos_grid(subnet, row, col, space):
        '''
        Set up the control grid for the attraction spheres.
        '''
        # Create the grid node and set its size.
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

        # Add normal and up-vector attributes.
        python_node=grid_node.createNode("python", "add_attrib")
        python_node.setInput(0, grid_geo)

        python_node.parm("python").set(SET_N_AND_UP_SCRIPT)

        # Create the jitter node for position randomization.
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
        Calculate the grid-point index used by a rivet node for this sphere.
        '''
        point_index=r*cols+c
        return point_index

def add_sphere_button(sphere):
        '''
        Add controls to the sphere node.
        '''
        parm_group=sphere.parmTemplateGroup()

        sphere_tab=hou.FolderParmTemplate("sphere_control_tab", "Sphere Control", folder_type=hou.folderType.Tabs)
        
        # Bake the current sphere position so it is no longer controlled by the rivet.
        bake_pos_button=hou.ButtonParmTemplate(
            name="bake_pos_button",
            label="Bake Position - Detach from Rivet",
            script_callback=BAKE_POS_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
        )
        # Toggle for preserving the current offset.
        if_keep_offset=hou.ToggleParmTemplate("if_keep_offset", "Keep Current Offset", default_value=False)
        
        # Restore rivet attraction.
        recover_rivet_button=hou.ButtonParmTemplate(
            name="recover_rivet_button",
            label="Restore Rivet Attraction",
            script_callback=RECOVER_RIVET_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
        )

        # Add the sphere control buttons.
        sphere_tab.addParmTemplate(bake_pos_button)
        sphere_tab.addParmTemplate(if_keep_offset)
        sphere_tab.addParmTemplate(recover_rivet_button)
        parm_group.append(sphere_tab)

        sphere.setParmTemplateGroup(parm_group)

def add_light_control_button(light):
        '''
        Add controls to the light node.
        '''
        # Add the light-control tab.
        light_tab=hou.FolderParmTemplate("light_control_tab", "Light Control", folder_type=hou.folderType.Simple)

        # Add light-direction baking.
        bake_dir_button=hou.ButtonParmTemplate(
            name="bake_dir_button",
            label="Bake Direction - Detach from Sphere Attraction",
            script_callback=BAKE_DIR_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        # Add light-position baking.
        bake_pos_button=hou.ButtonParmTemplate(
            name="bake_pos_button",
            label="Bake Position - Detach from Submarker",
            script_callback=BAKE_POS_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        # Restore sphere attraction.
        recover_lookat_button=hou.ButtonParmTemplate(
            name="recover_lookat_button",
            label="Restore Sphere Attraction",
            script_callback=RECOVER_LOOKAT_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )
        # Toggle for preserving the current offset.
        if_keep_offset=hou.ToggleParmTemplate("if_keep_offset", "Keep Current Offset", default_value=False)

        recover_submarker_button=hou.ButtonParmTemplate(
            name="recover_submarker_button",
            label="Restore Submarker Attraction",
            script_callback=RECOVER_SUBMARKER_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        # Remove master cone-angle control.
        remove_cone_button=hou.ButtonParmTemplate(
            name="remove_cone_button",
            label="Detach from Master Cone Angle",
            script_callback=BAKE_CONE_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        # Add master cone-angle control.
        add_cone_button=hou.ButtonParmTemplate(
            name="add_cone_button",
            label="Add Master Cone Angle",
            script_callback=RECOVER_CONE_SCRIPT,
            script_callback_language=hou.scriptLanguage.Python
            )

        # Add light control buttons.
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
        Add controls to the control grid.
        '''
        parm_group = control_grid.parmTemplateGroup()
        tab=hou.FolderParmTemplate("grid_control_tab", "Control", folder_type=hou.folderType.Tabs)

        # Add and link the primary jitter controls.
        scale_parm=hou.FloatParmTemplate(
                name="jitter_scale",
                label="Jitter Amount",
                num_components=1,
                default_value=(1.0,),
            )

        axis_scale_parm=hou.FloatParmTemplate(
            name="jitter_axisscale",
            label="Jitter Axis Scale",
            num_components=3,       
            default_value=(1.0, 1.0, 1.0)
        )

        seed_parm=hou.FloatParmTemplate(
                name="jitter_seed",
                label="Jitter Seed",
                num_components=1,
                default_value=(1.0,),
            )
        
        # Add the grid control buttons.
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
    Calculate the light attraction position.
    '''
    
    # Read point A, point B, master object, convergence, and ground height.
    parent_a_path = node.parm("parent_a_marker").eval()
    parent_b_path = node.parm("parent_b_marker").eval()
    master_path = node.parm("master").eval()
    blend = node.parm("blend").eval()
    ground_height = node.parm("ground_height").eval()
    
    parent_a = hou.node(parent_a_path)
    parent_b = hou.node(parent_b_path)
    master=hou.node(master_path)

    # Get point A, point B, and master-object positions.
    pos_a = parent_a.worldTransform().extractTranslates()
    pos_b = parent_b.worldTransform().extractTranslates()
    pos_master=master.worldTransform().extractTranslates()

    # Calculate the projection of AC onto AB, where C is vertically offset from B
    # by the configured ground height.
    # Projection formula: project a onto b = ((a . b) / len(b)^2) * b.
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
    
    # Calculate segments AB and AC.
    ab = vec_b - vec_a
    ac = vec_c - vec_a

    # Calculate the squared AB length.
    ab_length_squared = ab.lengthSquared()
    # Calculate the projected point position.
    t = ac.dot(ab) / ab_length_squared
    proj_point = vec_a + t * ab
    
    # Blend between the initial light position and the projected convergence position.
    new_pos = vec_c * (1 - blend) + proj_point * blend
    
    # Output the new local position.
    vec_master_pos=hou.Vector3(pos_master)
    new_pos-=vec_master_pos
    node.parmTuple("output_pos").set(new_pos)

def update_all_proj(node):
    '''
    Update every projection node output position.
    '''
    parent = node.parent(); 
    target_type = f'hlgt::light_path_projector::{PROJ_NODE_VERSION}' 
    button_name = 'update'
    for child in parent.children():
        if child.type().name() == target_type and child.parm(button_name):
            child.parm(button_name).pressButton() 

def export_and_bake_lights(node):
    '''
    Export and bake the light parameters.
    '''
    parent=node.parent()
    light_type=node.parm("light_type").eval()
    initial_pos=parent.position()
    
    light_dict={}
    light_node_list=[]
    # Record each light's baked translation, rotation, cone angle, and icon size.
    for child in parent.children():
        if child.type().name() == light_type:
            translate=baked_translate(child)
            rotation=baked_rotation(child)
            cone_angle=child.parm("ar_cone_angle").eval()
            icon_scale=child.parm("l_iconscale").eval()
            light_dict[child.name()]=[translate, rotation, cone_angle, icon_scale]
            light_node_list.append(child)

    # Copy lights to the /obj level.
    hou.copyNodesTo(light_node_list, hou.node("/obj"))
    
    obj_node=hou.node("/obj")

    # Create a network box.
    output_netbox = obj_node.createNetworkBox()
    output_netbox.setComment("Output Lights")
    
    # Apply the extracted light data to each copied light.
    for _, (light_name, light_transform) in enumerate(light_dict.items()):
        light_node=obj_node.node(light_name)
        light_translate=light_transform[0]
        light_rotation=light_transform[1]
        cone_angle=light_transform[2]
        icon_scale=light_transform[3]

        # Set light translation and rotation.
        light_node.parmTuple("t").set(light_translate)
        light_node.parmTuple("r").set(light_rotation)

        cone_angle_parm=light_node.parm("ar_cone_angle")
        icon_scale_parm=light_node.parm("l_iconscale")
        # Remove parameter references for cone angle and icon size.
        if cone_angle_parm.expression():
            cone_angle_parm.deleteAllKeyframes()
        if icon_scale_parm.expression():
            icon_scale_parm.deleteAllKeyframes()

        # Set cone angle and icon size, then clear sphere attraction.
        cone_angle_parm.set(cone_angle)
        icon_scale_parm.set(icon_scale)
        light_node.parm("lookatpath").set("")
        
        # Remove the control buttons from the light node.
        light_ptg=light_node.parmTemplateGroup()
        light_ptg.remove(light_ptg.find("light_control_tab"))
        light_node.setParmTemplateGroup(light_ptg)

        # Add the light to the network box.
        output_netbox.addItem(light_node)

    # Place the network box next to the subnet.
    output_netbox.fitAroundContents()
    output_netbox.setPosition(initial_pos+hou.Vector2(2.0,0.0))

def baked_translate(node):
    '''
    Bake translation.
    '''
    world_transform=node.worldTransform()
    translate=world_transform.extractTranslates()
    return translate

def baked_rotation(node):
    '''
    Bake rotation.
    '''
    world_transform=node.worldTransform()
    rotation=world_transform.extractRotates()
    return rotation

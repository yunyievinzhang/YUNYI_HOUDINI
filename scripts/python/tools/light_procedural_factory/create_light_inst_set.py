import hou
import os
import random

LIGHT_TYPE_MAPPER={
      "point": 0,
      "spot": 1,
      "quad": 2,
      "disk" : 3
}

def check_in_obj():
        """
        Check whether the current network editor is inside /obj.
        """
        # Get the current network editor pane.
        current_panel=hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)

        # If it exists, make sure it is at the /obj level.
        if current_panel:
                current_location=current_panel.pwd()
                if not(current_location.path()=="/obj"):
                        hou.ui.displayMessage("Create the instance template from the /obj level.")
                        return False
                else:
                        return True
        else:
               hou.ui.displayMessage("Open a Network Editor pane first.")
               return False

def create_inst_set(light_name, light_type_name):
        """
        Create the light and its related instance nodes.
        """
        obj_node=hou.node("/obj")
        # Create the light node.
        ar_light=obj_node.createNode("arnold_light", light_name)
        ar_light.parm("ar_light_type").set(light_type_name)

        # Create the light_gen geo node and load the template.
        light_gen_name=f"{light_name}_gen"
        light_gen=obj_node.createNode("geo",light_gen_name)
        current_dir=os.path.dirname(__file__).replace("\\","/")
        light_gen.loadItemsFromFile (f"{current_dir}/light_procedural_factory_template.cpio")

        # Create the instance node and configure its parameters.
        inst_name=f"{light_name}_instance"
        light_inst=obj_node.createNode("instance", inst_name)
        for child in light_inst.children():
                child.destroy()
        
        # Set the mode to fast point instancing.
        light_inst.parm("ptinstance").set(2)
        # Point to the light being instanced.
        ar_light_path=ar_light.path()
        light_inst.parm("instancepath").set(ar_light_path)
        # Create an object_merge and point it to light_gen.
        object_merge=light_inst.createNode("object_merge")
        light_out_path=light_gen.node("light_OUT").path()
        object_merge.parm("objpath1").set(light_out_path)

        # Assign a random color to the related nodes.
        rand_r=random.random()
        rand_g=random.random()
        rand_b=random.random()
        rand_color=hou.Color(rand_r,rand_g,rand_b)
        ar_light.setColor(rand_color)
        light_gen.setColor(rand_color)
        light_inst.setColor(rand_color)

        # Keep the three nodes close together in the network editor.
        ar_light.moveToGoodPosition()
        ar_light_pos=ar_light.position()
        light_gen.setPosition(ar_light_pos-hou.Vector2(0,1))
        light_inst.setPosition(ar_light_pos-hou.Vector2(0,2))
        
        # Add the nodes to a network box.
        network_box_name=f"{ar_light}_instance_group"
        light_network_box=obj_node.createNetworkBox(network_box_name)
        light_network_box.setComment(f"{light_name} light instance template")
        light_network_box.addItem(ar_light)
        light_network_box.addItem(light_gen)
        light_network_box.addItem(light_inst)
        light_network_box.fitAroundContents()

        # Set all light_type parameters inside the template to the selected type.
        set_template_to_light_type(light_name, light_type_name)
        # Focus the network editor on the created nodes.
        set_view_to_nodes(ar_light.position())

def set_view_to_nodes(light_pos):
        """
        Focus the network editor on the newly created nodes.
        """
        # Get the current desktop.
        desktop=hou.ui.curDesktop()

        # Get the network editor.
        network_editor=desktop.paneTabOfType(hou.paneTabType.NetworkEditor)
        
        # If a network editor exists, focus it on the new nodes.
        if network_editor:
                network_editor.setPwd(hou.node("/obj"))
                # Calculate the visible node area.
                bounding_rect=calculate_zoom_area(light_pos)
                network_editor.setVisibleBounds(bounding_rect, transition_time=0.5)
        else:
                print("No Network Editor Pane Found!")

        # Get the scene viewer.
        scene_viewer=desktop.paneTabOfType(hou.paneTabType.SceneViewer)
        # If a scene viewer exists, move it to /obj.
        if scene_viewer:
                scene_viewer.setPwd(hou.node('/obj'))
        else:
                print("No Scene Viewer Pane Found!")

def set_template_to_light_type(light_name, light_type_name):
        '''
        Set every light_type parameter in the template to the created light type.
        '''
        light_type_num=LIGHT_TYPE_MAPPER[light_type_name]
        light_gen_node=hou.node(f"/obj/{light_name}_gen")
        for child in light_gen_node.children():
                parms_group=child.parms()
                for parm in parms_group:
                        # Found a light_type parameter.
                        if parm.name()=="light_type":
                                 parm.set(light_type_num)
                if child.type().name()=="hlgt::light_commit::1.0":
                        child.parm("refresh_edit").pressButton()
                                  
def calculate_zoom_area(center_pos):
        """
        Calculate the viewport bounds occupied by the nodes.
        """
        bound_size=5
        bounding_rect=hou.BoundingRect(center_pos[0]-bound_size, center_pos[1]-bound_size, center_pos[0]+bound_size, center_pos[1]+bound_size)
        return bounding_rect

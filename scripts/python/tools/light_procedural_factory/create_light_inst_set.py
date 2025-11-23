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
        检查是当前是否在obj层级内
        """
        #获得当前节点视窗
        current_panel=hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)

        #如果存在的话检查是不是在obj层级
        if current_panel:
                current_location=current_panel.pwd()
                if not(current_location.path()=="/obj"):
                        hou.ui.displayMessage("需要在obj层级才可以创建！")
                        return False
                else:
                        return True
        else:
               hou.ui.displayMessage("需要打开节点视窗")
               return False

def create_inst_set(light_name, light_type_name):
        """
        创建灯光以及instance附属节点
        """
        obj_node=hou.node("/obj")
        #创建灯光节点
        ar_light=obj_node.createNode("arnold_light", light_name)
        ar_light.parm("ar_light_type").set(light_type_name)

        #创建light_gen geo节点并加载模板
        light_gen_name=f"{light_name}_gen"
        light_gen=obj_node.createNode("geo",light_gen_name)
        current_dir=os.path.dirname(__file__).replace("\\","/")
        light_gen.loadItemsFromFile (f"{current_dir}/light_procedural_factory_template.cpio")

        #创建instance并设置参数
        inst_name=f"{light_name}_instance"
        light_inst=obj_node.createNode("instance", inst_name)
        for child in light_inst.children():
                child.destroy()
        
        #设立模式为fast point instancing
        light_inst.parm("ptinstance").set(2)
        #填入被instanced的灯光
        ar_light_path=ar_light.path()
        light_inst.parm("instancepath").set(ar_light_path)
        #创立object_merge并指向light_gen
        object_merge=light_inst.createNode("object_merge")
        light_out_path=light_gen.node("light_OUT").path()
        object_merge.parm("objpath1").set(light_out_path)

        #为节点设置随机颜色
        rand_r=random.random()
        rand_g=random.random()
        rand_b=random.random()
        rand_color=hou.Color(rand_r,rand_g,rand_b)
        ar_light.setColor(rand_color)
        light_gen.setColor(rand_color)
        light_inst.setColor(rand_color)

        #让三个节点处在相近位置
        ar_light.moveToGoodPosition()
        ar_light_pos=ar_light.position()
        light_gen.setPosition(ar_light_pos-hou.Vector2(0,1))
        light_inst.setPosition(ar_light_pos-hou.Vector2(0,2))
        
        #将节点加入network box
        network_box_name=f"{ar_light}_instance_group"
        light_network_box=obj_node.createNetworkBox(network_box_name)
        light_network_box.setComment(f"{light_name} 灯光instance模板")
        light_network_box.addItem(ar_light)
        light_network_box.addItem(light_gen)
        light_network_box.addItem(light_inst)
        light_network_box.fitAroundContents()

        # 将模板内所有节点选项设置为所选灯光类型
        set_template_to_light_type(light_name, light_type_name)
        #将节点视窗聚焦于创建的节点上
        set_view_to_nodes(ar_light.position())

def set_view_to_nodes(light_pos):
        """
        聚焦节点视窗到新创建的节点
        """
        #获得桌面
        desktop=hou.ui.curDesktop()

        #获得节点视窗
        network_editor=desktop.paneTabOfType(hou.paneTabType.NetworkEditor)
        
        #如果有节点视窗，就聚焦到新创造的节点上
        if network_editor:
                network_editor.setPwd(hou.node("/obj"))
                #计算节点区域
                bounding_rect=calculate_zoom_area(light_pos)
                network_editor.setVisibleBounds(bounding_rect, transition_time=0.5)
        else:
                print("No Network Editor Pane Found!")

        # 获得场景视窗
        scene_viewer=desktop.paneTabOfType(hou.paneTabType.SceneViewer)
        #如果有场景视窗，就移动到obj层级
        if scene_viewer:
                scene_viewer.setPwd(hou.node('/obj'))
        else:
                print("No Scene Viewer Pane Found!")

def set_template_to_light_type(light_name, light_type_name):
        '''
        将模板节点内所有的light_type参数设置为创建的灯光类型
        '''
        light_type_num=LIGHT_TYPE_MAPPER[light_type_name]
        light_gen_node=hou.node(f"/obj/{light_name}_gen")
        for child in light_gen_node.children():
                parms_group=child.parms()
                for parm in parms_group:
                        # 发现light_type参数
                        if parm.name()=="light_type":
                                 parm.set(light_type_num)
                if child.type().name()=="hlgt::light_commit::1.0":
                        child.parm("refresh_edit").pressButton()
                                  
def calculate_zoom_area(center_pos):
        """
        计算节点占有的视窗区域
        """
        bound_size=5
        bounding_rect=hou.BoundingRect(center_pos[0]-bound_size, center_pos[1]-bound_size, center_pos[0]+bound_size, center_pos[1]+bound_size)
        return bounding_rect
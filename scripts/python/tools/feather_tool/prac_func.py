import sys
import math
import sys
import math
import os
import glob
import random
import hou
def create_attr_name(attribute):
    full_attrib_name="painted_"+attribute
    name_components=attribute.split("_")
    attrib_node_name="Painted"
    for component in name_components:
        capitalized_component=component.capitalize()
        
        attrib_node_name+=capitalized_component
    return full_attrib_name,attrib_node_name

def is_input_node(parent_node, child_node):
    input_nodes = parent_node.inputs()
    for input_node in input_nodes:
        if input_node == child_node:
            return True
            
    return False

def create_nodes():
    asset_name=hou.node(".")
    check_uv()
    
    
    set_groupBox_expressions()
    set_asset_parm("sopoutput", "$HIP/geo/$HIPNAME.$OS.$F.bgeo.sc")
    skinpath=skin_path()
    attach_node=hou.node(attrib_create_path())
    
    has_new_attr= False
    if not(hou.node("/obj/"+str(asset_name)+"_vellum")):
        create_vellum()
        
    
    if not(hou.node("/obj/"+str(asset_name)+"_groupbox")):
    
        group_box()
        
    if not(hou.node("/obj/"+str(asset_name)+"_sequenceRead")):
        create_clusterRead_node()
    
    attribute_dict={"scale":1,"rand_scale":0, "ribbion":1, "rotation":1, "tilt":1, "concave":0}
    for attribute in attribute_dict:
        full_attrib_name,attrib_node_name=create_attr_name(attribute)
        
        attrib_create_name="{}_attribcreate_{}".format(asset_name, attrib_node_name)
        if(not(hou.node(skinpath[0]+"/"+attrib_create_name))):
            has_new_attr=True
            attr_create=create_skin_node("attribcreate",attrib_create_name)
            attr_create.parm("name1").set(full_attrib_name)
            attr_create.parm("value1v1").set(attribute_dict[attribute])
          
        else:
            attr_create=hou.node(skinpath[0]+"/"+attrib_create_name)
  
        if(not(is_input_node(attr_create,attach_node))):
            attr_create.setInput(0,None)
            attr_create.setNextInput(attach_node)
        attach_node=attr_create
        attrib_paint_name="{}_attribpaint_{}".format(asset_name, attrib_node_name)
        if(not(hou.node(skinpath[0]+"/"+attrib_paint_name))):
            attr_paint=create_skin_node("attribpaint",attrib_paint_name)
            attr_paint.parm("attribname1").set(full_attrib_name)
        else:
            attr_paint=hou.node(skinpath[0]+"/"+attrib_paint_name)
        if(not(is_input_node(attr_paint,attach_node))):
            attr_paint.setInput(0,None)
            attr_paint.setNextInput(attach_node)
            
        attach_node=attr_paint
        
    #create null
    out_node_name="OUT_{}".format(asset_name)
    if(not(hou.node(skinpath[0]+"/"+out_node_name))):
        out_node=create_skin_node("null","OUT_{}".format(asset_name))
        out_node.setNextInput(attach_node)
        out_node.setDisplayFlag(True)
        out_node.setRenderFlag(True)
    else:
        out_node=hou.node(skinpath[0]+"/"+out_node_name)
        out_node.setInput(0,None)
        out_node.setNextInput(attach_node)
    
    #layout
    skin_geo=skinpath[2]
    skin_geo.layoutChildren()
    
    #change merge_skin_dir
    assetpath=asset_path()
    parm_str=assetpath+("/merge_skin")
    hou.parm(parm_str).set(out_node.path())
    if not has_new_attr:
        hou.ui.displayMessage("No new attributes are found, so nothing is changed")
    else:
        hou.ui.displayMessage("The newest attributes are updated")
        
    
    # add a entry where you can delete attributes on updates
    #future dev
    
    
def asset_path():
    path=hou.node(".").path()
    return path
    
def attrib_create_path():
    try:
        asset=asset_path()
        path=hou.parm(asset+"/attr_create_path").eval()
        return path
    except:
        hou.ui.displayMessage("Invalid Attribute Create Path")
        exit()
    
def skin_path():
    try:
        asset=asset_path()
        skin=hou.parm(asset+'/merge_skin').eval()
        
        skin_path=hou.node(skin).parent().path()
        skin_geo=hou.node(skin).parent()
        return skin_path,skin,skin_geo
    except:
        hou.ui.displayMessage("Invalid Merge Skin Path!")
        exit()
        
def tpose_anim():
    switch_val= eval_asset_parm("xn__t_pose_to_anim_")
    vellum_switch_val=eval_asset_parm("vellum")
    try:
        curve_geo=get_parent_node("merge_curves")
    except:
        hou.ui.displayMessage("No Valid Merge Curve")
        sys.exit()
    try:
        anim_geo=get_parent_node("animated_skin")
    except:
        hou.ui.displayMessage("No Valid Animated Skin")
        sys.exit()
    try:
        tpose_geo=get_parent_node("merge_skin")
    except:
        hou.ui.displayMessage("No Valid Merge Skin")
        sys.exit()
    
    groom_geo=tpose_geo.outputs()[0]
    
    guide_groom=hou.node(groom_geo.outputs()[0].path())
    
    m_curves=groom_geo.outputs()[0].path()+"/DISPLAY"
    
    vellum_node=hou.node(str(asset_path())+"_vellum")
    
    if switch_val ==0:
    
    
        set_asset_parm("vellum",0)
        set_asset_parm("merge_curves",m_curves)
        
        #reassignment
        vellum_node.setDisplayFlag(0)
        curve_geo=get_parent_node("merge_curves")
        
        curve_geo.setInput(2,tpose_geo)
        
        anim_geo.setDisplayFlag(0)
        tpose_geo.setDisplayFlag(1)
        groom_geo.setDisplayFlag(1)
        curve_geo.setDisplayFlag(0)
    else:
        curve_geo.setInput(2,anim_geo)
        anim_geo.setDisplayFlag(1)
        tpose_geo.setDisplayFlag(0)
        groom_geo.setDisplayFlag(0)
        curve_geo.setDisplayFlag(1)

def vellum_on():
    switch_val= eval_asset_parm("vellum")
    try:
        curve_geo=get_parent_node("merge_curves")
    except:
        hou.ui.displayMessage("No Valid Merge Curve")
        sys.exit()
    try:
        anim_geo=get_parent_node("animated_skin")
    except:
        hou.ui.displayMessage("No Valid Animated Skin")
        sys.exit()
    try:
        tpose_geo=get_parent_node("merge_skin")
    except:
        hou.ui.displayMessage("No Valid Merge Skin")
        sys.exit()
        
    groom_geo=tpose_geo.outputs()[0]
    guide_groom=hou.node(groom_geo.outputs()[0].path())
    
    m_curves=groom_geo.outputs()[0].path()+"/DISPLAY"
    
    vellum_node=hou.node(str(asset_path())+"_vellum")
    
    vellum_out=str(vellum_node.path())+"/vellum_setup/OUT"
    
    if switch_val==0:
        set_asset_parm("merge_curves",m_curves)
        guide_groom.setDisplayFlag(1)
        vellum_node.setDisplayFlag(0)
    else:
        set_asset_parm("merge_curves",vellum_out)
        guide_groom.setDisplayFlag(0)
        vellum_node.setDisplayFlag(1)
        
        
    
    
        
def get_parent_node(parm):
    parm_path = eval_asset_parm(parm)
    parm_geo = hou.node(parm_path).parent()
    return parm_geo

def set_asset_parm(parm, val):
    try:
        assetpath=asset_path()
        
        parm_str=assetpath+('/{0}'.format(parm))
        
        parm_eval=hou.parm(parm_str).set(val)
        
        
        return parm_eval
    except:
        hou.ui.displayMessage("there is no such parameter: {0}".format(parm))
        sys.exit()
    
def eval_asset_parm(parm):
    try:
        assetpath=asset_path()
        parm_str=assetpath+('/{0}'.format(parm))
        parm_eval=hou.parm(parm_str).eval()
        return parm_eval
    except:
        hou.ui.displayMessage("there is no such parameter: {0}".format(parm))
        sys.exit()
def check_uv():
    skinpath=skin_path()[1]
    skin_node=hou.node(skinpath)
    geo=skin_node.geometry()
    
    uv=geo.findVertexAttrib('uv')
    
    if not uv:
        hou.ui.displayMessage("There is no UV in the geometry")
        sys.exit()


def poly_res():
    f_res=eval_asset_parm("fres")
    feather_res=eval_asset_parm("feather_segs")
    poly_res=eval_asset_parm("poly_res")
    poly_vis=eval_asset_parm("poly_vis_switch")
    
    if poly_vis==0:
        set_asset_parm("feather_segs", f_res)
    else:
        set_asset_parm("feather_segs", poly_res)

def set_res():
    f_res = eval_asset_parm("fres")
    set_asset_parm("feather_segs", f_res)
    
def set_res_from_pres():
    poly_res = eval_asset_parm("poly_res")
    set_asset_parm("feather_segs", poly_res)
    
def asset_name():
    name=str(hou.node("."))
    return name

def create_vellum():
    assetname=asset_name()
    vellum_node=hou.node("/obj").createNode("vellum_feather",str(assetname)+"_vellum")
    asset_pos=hou.node(".").position()
    vellum_pos=hou.Vector2(asset_pos[0]-2.5,asset_pos[1])
    vellum_node.setPosition(vellum_pos)
    vellum_node.setDisplayFlag(0)
    
    #set vellum_parameter
    merge1=str(asset_path())+"_vellum/vellum_setup/object_merge1/objpath1"
    merge2=str(asset_path())+"_vellum/vellum_setup/object_merge1/objpath1"
    
    curves=eval_asset_parm("merge_curves")
    anim_skin=eval_asset_parm("merge_skin")
    
    hou.parm(merge1).set(curves)
    hou.parm(merge2).set(anim_skin)
    
    
def group_box():
    geo=hou.node("/obj")
    assetname=asset_name()
    box_name=assetname+("_groupbox")
    box_exist = 0
    
    for child in geo.children():
        if child.name() == box_name:
            box_exist = 1
        else:
            box_exist = 0
    if box_exist==0:
        # create the box geo node
        box_geo=geo.createNode("geo", box_name)
        # create the box inside the box_geo_node
        box = box_geo.createNode("box")
        # display the box as bounding box
        box_geo.parm("viewportlod").set(2)
        box_geo.setDisplayFlag(0)
        
        
        # move to a good position
        assetpath=asset_path()
        pos=hou.node(assetpath).position()
        # create a vector 
        box_pos= hou.Vector2(pos[0],pos[1]-1)
        box_geo.setPosition(box_pos)
        
def set_groupBox_expressions():

    asset= hou.node(".")
    asset.allowEditingOfContents()
    assetpath=asset_path()
    assetname=asset_name()
    
    parm_size_x=hou.parm(assetpath+'/feather_tool/delete_groupbox/sizex')
    parm_size_y=hou.parm(assetpath+'/feather_tool/delete_groupbox/sizey')
    parm_size_z=hou.parm(assetpath+'/feather_tool/delete_groupbox/sizez')
    
    parm_translate_x=hou.parm(assetpath+'/feather_tool/delete_groupbox/tx')
    parm_translate_y=hou.parm(assetpath+'/feather_tool/delete_groupbox/ty')
    parm_translate_z=hou.parm(assetpath+'/feather_tool/delete_groupbox/tz')
    
    box_name=assetname+"_groupbox"
    parm_size_x.setExpression('ch("../../../'+box_name+'/sx")')
    parm_size_y.setExpression('ch("../../../'+box_name+'/sy")')
    parm_size_z.setExpression('ch("../../../'+box_name+'/sz")')
    
     
    parm_translate_x.setExpression('ch("../../../'+box_name+'/tx")')
    parm_translate_y.setExpression('ch("../../../'+box_name+'/ty")')
    parm_translate_z.setExpression('ch("../../../'+box_name+'/tz")')
    
def group_switch():
    assetname= asset_name()
    # get the group box node
    box_path="/obj/"+assetname+"_groupbox"
    box_geo= hou.node(box_path)
    
    # get the siwtch_val
    switch_val=eval_asset_parm("enable_group")
    
    if switch_val==0:
        box_geo.setDisplayFlag(0)
        set_asset_parm("range_switch",0)
    else:
        box_geo.setDisplayFlag(1)
        set_asset_parm("range_switch",1)
        
def create_clusters():
    delete_clusters()
    loop_range=(eval_asset_parm("cluster_core")*2)-2
    assetpath=asset_path()
    in_cluster=hou.node(assetpath+"/feather_tool/IN_CLUSTER")
    in_cluster_pos=in_cluster.position()
    cluster_switcher= hou.node(assetpath+"/feather_tool/cluster_switcher")
    
    
    # for layout position
    cluster_x_center=in_cluster_pos[0]
    past_level=2
    past_side="L"
    mult=2
    current_side="L"
    past_parent=None
    offset=1.0
    neg_node=None
    basic_distance=1.5
    
    # prepare to create network box
    node_list=[]
    for i in range(loop_range):
        
        
        del_node=create_asset_node("delete","cluster_del0")
        del_node.setPosition(in_cluster_pos- hou.Vector2(0,1))
        set_assetNode_parm(del_node,"groupop",1)
        if i%2!=0:
            set_assetNode_parm(del_node,"rangestart",1)
        if i<=1:
            parent_node=in_cluster
            del_node.setInput(0, parent_node)
            parent_position=parent_node.position()
            if i==0:
                del_node.setPosition(parent_position-hou.Vector2(basic_distance+offset,1))
            else:
                del_node.setPosition(parent_position+hou.Vector2(basic_distance+offset,-1))
            
        if i>1:
            
            if i%2==0:
                parent=int((i/2)-1)
            else:
                parent=int((i/2))-1

            parent_name="cluster_del{}".format(parent)
            parent_path=str(asset_path())+"/feather_tool/"+parent_name
            parent_node=hou.node(parent_path)
            del_node.setInput(0,parent_node)
            parent_position=parent_node.position()
            past_side=current_side
            
            if parent_position[0]<cluster_x_center:
                # we are at left of the cluster
                current_side="L"
                # we are at a new line
                if (current_side=="L" and past_side=="R"):
                    neg_node=None
                if neg_node:
                    del_node.setPosition(neg_node.position()+hou.Vector2(offset,0))
                else:
                    del_node.setPosition(parent_position-hou.Vector2(basic_distance+offset,1))
            else:
                # we are at the right of the cluster
                current_side="R"
                # we are breaking to another side
                if (current_side=="R" and past_side=="L"):
                    neg_node=None
                if neg_node:
                    del_node.setPosition(neg_node.position()+hou.Vector2(offset,0))
                else:
                    del_node.setPosition(parent_position+hou.Vector2(basic_distance+offset,-1))
           
            past_parent=parent_node
            neg_node=del_node
        if i>=(loop_range/2)-1:
            cluster_switcher.setNextInput(del_node)
            
        node_list.append(del_node)
    
    nodes_parent=node_list[0].parent()
    cluster_box=nodes_parent.createNetworkBox("clusters_box")
    
    # find good position of boxes, which is center of selected nodes.
    list_x_of_selected_nodes = [node.position().x() for node in node_list]
    center_x = sum(list_x_of_selected_nodes) / len(node_list)
    list_y_of_selected_nodes = [node.position().y() for node in node_list]
    center_y = sum(list_y_of_selected_nodes) / len(node_list)
    cluster_box.setPosition(hou.Vector2(center_x, center_y))
    
    for cluster_node in node_list:
        cluster_box.addItem(cluster_node)
    # finalize network box
    cluster_box.fitAroundContents()
    cluster_box.setComment("Clusters")
    cluster_box.setColor(hou.Color(1.0,0.5,0.0))
                
            
def create_asset_node(node,name):
    path=str(asset_path())+"/feather_tool"
    node=hou.node(path).createNode("{0}".format(node), "{0}".format(name))
    return node
   
def create_skin_node(node,name):
    merge_skin_node=hou.node(hou.pwd().parm("merge_skin").eval())
    skin_node=merge_skin_node.parent()
    node=skin_node.createNode("{0}".format(node),"{0}".format(name))
    return node

    
def set_assetNode_parm(node, parm_name, value):
    path=str(asset_path())+"/feather_tool"
    parm=path+("/{0}/{1}".format(node,parm_name))
    hou.parm(parm).set(value)

def delete_clusters():
    assetpath=asset_path()
    cluster_box=hou.item(assetpath+"/feather_tool/clusters_box")
    if cluster_box:
        cluster_box.destroy(destroy_contents=True)
        cluster_switcher= hou.node(assetpath+"/feather_tool/cluster_switcher")
        for input in cluster_switcher.inputs():
            cluster_switcher.setInput(0,None)
            
            
def cluster_sequence_write():
    prev_feather_mode=eval_asset_parm("feather_mode")
    prev_toggle=eval_asset_parm("dyna_static_tgle")
    #set feather_mode first
    set_asset_parm("feather_mode",0)
    set_asset_parm("dyna_static_tgle",0)
    #got the path
    remove_original_cache("dynamicCluster")
    assetpath=asset_path()
    
    save_button= hou.parm(assetpath+"/execute")
    switch=set_asset_parm("select_cluster",0)
    c_start=eval_asset_parm("crange1")
    
    c_end=eval_asset_parm("crange2")
    
    set_asset_parm("f1",c_start)
    
    set_asset_parm("f2",c_end)
    set_asset_parm("trange",1)
    
    outputFile=eval_asset_parm("sopoutput")
    
    output_orig=outputFile
    
    frame_split="."+outputFile.split("/")[-1].split(".")[1]+"."
    
    name_split=outputFile.split("/")[-1].split(".")[0]
    
    replace_frame=".$F4."
    replace_name="cluster"
    
    change_frame=outputFile.replace(frame_split,replace_frame)
    cluster_size=eval_asset_parm("cluster_core")
    for i in range(cluster_size):
        replace_name="{0}_dynamicCluster{1}".format(name_split,i+1)
        
        outputFile_R=change_frame.replace(name_split,replace_name)
        set_asset_parm("sopoutput",outputFile_R)
        switch=set_asset_parm("select_cluster",i)
        save_button.pressButton()
        
    set_asset_parm("sopoutput","$HIP/geo/$OS.$F.bgeo.sc")
    
    set_asset_parm("select_cluster",0)
    
    cluster_sequence_read()
    # set everything back
    set_asset_parm("feather_mode",prev_feather_mode)
    set_asset_parm("dyna_static_tgle",prev_toggle)
    
def create_clusterRead_node():
    assetname=asset_name()
    cluster_sequence_geo_name=assetname+"_sequenceRead"
    
    cluster_sequence_geo=hou.node("/obj").createNode("geo",cluster_sequence_geo_name)
    
    asset_pos=hou.node(".").position()
    
    node_pos=hou.Vector2(asset_pos[0],asset_pos[1]-2)
    
    cluster_sequence_geo.setPosition(node_pos)
    
    cluster_sequence_geo.setDisplayFlag(0)
    
    #add this step for basic config
    cluster_sequence_read_basic(cluster_sequence_geo)

def cluster_sequence_read_basic(node):
    

    #create all necessary nodes
    dyn_merge_node=node.createNode("merge","dynamic_merge")
    static_merge_node=node.createNode("merge","static_merge")
    shaft_merge_node=node.createNode("merge","shaft_merge")
    switch_node=node.createNode("switch","feather_switch")
    out_node=node.createNode("null","OUT")
    
    # set connection
    shaft_merge_node.setNextInput(dyn_merge_node)
    switch_node.setNextInput(shaft_merge_node)
    switch_node.setNextInput(static_merge_node)
    out_node.setInput(0,switch_node)
    
    # set render
    out_node.setDisplayFlag(1)
    out_node.setRenderFlag(1)
    
    #layout them well
    dyn_merge_node.moveToGoodPosition()
    static_merge_node.moveToGoodPosition()
    shaft_merge_node.moveToGoodPosition()
    switch_node.moveToGoodPosition()
    out_node.moveToGoodPosition()
    
    
def create_read_file(category,num, anchor_node):
    node_list=[]
    assetpath=asset_path()
    assetname=asset_name()
    cluster_sequence_geo_name=assetpath+"_sequenceRead"
    csg_node=hou.node(cluster_sequence_geo_name)
    for i in range(num):
        file_node_name=category+"{0}".format(1)
        if num==1:
            file_node_name=category
        file=csg_node.createNode("file",file_node_name)
        file.moveToGoodPosition()
        
        file_to_read="$HIP/geo/"+assetname+"_"+category+"{0}.$F4.bgeo.sc".format(i+1)
        if num==1:
            file_to_read="$HIP/geo/"+assetname+"_"+category+".$F4.bgeo.sc"
        
        geo_file_parm=hou.parm(file.path()+'/file').set(file_to_read)
        
        set_missing_frame=hou.parm(file.path()+'/missingframe').set(1)
        
        anchor_node.setNextInput(file)
        node_list.append(file)
    nodes_parent=node_list[0].parent()
    file_box=nodes_parent.createNetworkBox(category+"_box")
    
    center_x,center_y=get_center_for_box(node_list)
    file_box.setPosition(hou.Vector2(center_x, center_y))
    
    for file_node in node_list:
        file_box.addItem(file_node)
    # finalize network box
    file_box.fitAroundContents()
    file_box.setComment(category+" cluster")
    file_box.setColor(hou.Color(random.random(),random.random(),random.random()))
    
def delete_file_node(parent_node,category):
    assetpath=asset_path()
    file_box=hou.item(path=parent_node.path()+"/"+category+"_box")
    if file_box:
        file_box.destroy(destroy_contents=True)
        
def cluster_sequence_read():
    
    assetname=asset_name()
    
    assetpath=asset_path()
    
    parent_node=hou.node(assetpath+'_sequenceRead')
    
    cluster_core_size=eval_asset_parm("cluster_core")
    

    # delete previous file

    delete_file_node(parent_node,"dynamicCluster")
    anchor_node=hou.node(assetpath+"_sequenceRead/dynamic_merge")

    create_read_file("dynamicCluster",cluster_core_size, anchor_node)
    
def remove_original_cache(key_word):
    
    abs_file_path=hou.hscriptExpression("$HIP")
    
    for cache_file in glob.glob(abs_file_path+"/geo/*{0}*".format(key_word)):
        os.remove(cache_file)
    
        
def create_static_cluster_files():


    #set feather_mode first
    set_asset_parm("feather_mode",0)
    set_asset_parm("dyna_static_tgle",0)
    delete_static_cl()
    #get the cluster core size
    cluster_core_size=eval_asset_parm("cluster_core")
    assetpath=asset_path()
    
    static_merge_node=hou.node(assetpath+"/feather_tool/static_merge")
    
    static_merge_pos=static_merge_node.position()
    # create filea and time shift node:
    cl_file_base_pos=static_merge_pos+hou.Vector2(0,4)
    cl_timeshift_base_pos=static_merge_pos+hou.Vector2(0,2)
    
    center_index=cluster_core_size/2-1
    
    node_list=[]
    
    for i in range(cluster_core_size):
        cl_file=create_asset_node("file","cl_file_0")
        
        set_missing_frame=cl_file.parm('missingframe').set(1)
        cl_timeshift=create_asset_node("timeshift","cl_fimeshift0")
        
        cl_file_pos=(cl_file_base_pos)-hou.Vector2(1.5*(center_index-i+1),0)
        cl_timeshift_pos=(cl_timeshift_base_pos)-hou.Vector2(1.5*(center_index-i+1),0)
        
        cl_file.setPosition(cl_file_pos)
        cl_timeshift.setPosition(cl_timeshift_pos)
        
        parm=hou.parm(cl_timeshift.path()+"/frame")
        parm.deleteAllKeyframes()
        parm.set(1)
        
        cl_timeshift.setInput(0, cl_file)
        
        static_merge_node.setNextInput(cl_timeshift)
        
        node_list.append(cl_file)
        node_list.append(cl_timeshift)
    
    nodes_parent=node_list[0].parent()
    cl_box=nodes_parent.createNetworkBox("static_clusters_box")
    
     # find good position of boxes, which is center of selected nodes.
    list_x_of_selected_nodes = [node.position().x() for node in node_list]
    center_x = sum(list_x_of_selected_nodes) / len(node_list)
    list_y_of_selected_nodes = [node.position().y() for node in node_list]
    center_y = sum(list_y_of_selected_nodes) / len(node_list)
    cl_box.setPosition(hou.Vector2(center_x, center_y))
    
    for cl_node in node_list:
        cl_box.addItem(cl_node)
    # finalize network box
    cl_box.fitAroundContents()
    cl_box.setComment("Static Clusters")
    cl_box.setColor(hou.Color(1.0,0.0,0.5))
    
def delete_static_cl():
    assetpath=asset_path()
    cluster_box=hou.item(assetpath+"/feather_tool/static_clusters_box")
    if cluster_box:
        cluster_box.destroy(destroy_contents=True)
    
def shaft_sequence_write():
    
    #set feather_mode first
    prev_feather_mode=eval_asset_parm("feather_mode")
    set_asset_parm("feather_mode",1)
    #got the path
    remove_original_cache("Shaft")
    assetpath=asset_path()
    
    save_button= hou.parm(assetpath+"/execute")
    c_start=eval_asset_parm("crange1")
    
    c_end=eval_asset_parm("crange2")
    
    set_asset_parm("f1",c_start)
    
    set_asset_parm("f2",c_end)
    set_asset_parm("trange",1)
    
    outputFile=eval_asset_parm("sopoutput")
    
    output_orig=outputFile
    
    frame_split=outputFile.split("/")[-1].split(".")[1]
    
    name_split=outputFile.split("/")[-1].split(".")[0]
    
    replace_frame="$F4"
    replace_name="cluster"
    
    change_frame=outputFile.replace(frame_split,replace_frame)
    replace_name="{0}_Shaft".format(name_split)
    
    outputFile_R=change_frame.replace(name_split,replace_name)
    set_asset_parm("sopoutput",outputFile_R)
    save_button.pressButton()
        
    set_asset_parm("sopoutput","$HIP/geo/$OS.$F.bgeo.sc")
    
    
    
    # update sequence read
    
    shaft_sequence_read()

    #set the feather mode back
    set_asset_parm("feather_mode",prev_feather_mode)  


def static_sequence_write():
    
    #set feather_mode first
    prev_feather_mode=eval_asset_parm("feather_mode")
    prev_toggle=eval_asset_parm("dyna_static_tgle")
    set_asset_parm("feather_mode",0)
    # set dynamic static toggle
    
    set_asset_parm("dyna_static_tgle",1)
    #got the path
    remove_original_cache("Static")
    assetpath=asset_path()
    
    save_button= hou.parm(assetpath+"/execute")
    c_start=eval_asset_parm("crange1")
    
    c_end=eval_asset_parm("crange2")
    
    set_asset_parm("f1",c_start)
    
    set_asset_parm("f2",c_end)
    set_asset_parm("trange",1)
    
    outputFile=eval_asset_parm("sopoutput")
    
    output_orig=outputFile
    
    frame_split="."+outputFile.split("/")[-1].split(".")[1]+"."
    
    name_split=outputFile.split("/")[-1].split(".")[0]
    
    replace_frame=".$F4."
    replace_name="cluster"
    
    change_frame=outputFile.replace(frame_split,replace_frame)
    replace_name="{0}_Static".format(name_split)
    
    outputFile_R=change_frame.replace(name_split,replace_name)
    set_asset_parm("sopoutput",outputFile_R)
    save_button.pressButton()
        
    set_asset_parm("sopoutput","$HIP/geo/$OS.$F.bgeo.sc")
    
    
    
    # update sequence read
    
    static_sequence_read()
    #set the original feather mode back
    set_asset_parm("feather_mode",prev_feather_mode) 
    set_asset_parm("dyna_static_tgle",prev_toggle)

def shaft_sequence_read():
    # get parent node
    assetname=asset_name()
    
    assetpath=asset_path()

    parent_node=hou.node(assetpath+'_sequenceRead')

    # delete previous file

    delete_file_node(parent_node,"Shaft")

    #create file node
    anchor_node=hou.node(assetpath+"_sequenceRead/shaft_merge")
    create_read_file("Shaft",1, anchor_node)
    shaft_node=hou.node(assetpath+"_sequenceRead/Shaft")
    static_merge_node=hou.node(assetpath+"_sequenceRead/static_merge")
    static_merge_node.setNextInput(shaft_node)
    

def static_sequence_read():
     # get parent node
    assetname=asset_name()
    
    assetpath=asset_path()

    parent_node=hou.node(assetpath+'_sequenceRead')

    # delete previous file

    delete_file_node(parent_node,"Static")

    #create file node
    anchor_node=hou.node(assetpath+"_sequenceRead/static_merge")
    create_read_file("Static",1, anchor_node)



    
    
def cluster_single_frame_write():
    #got the path
    remove_original_cache("staticCluster")
    create_static_cluster_files()
    assetpath=asset_path()
    
    #get the start frame
    # Get the current frame range
    start_frame = hou.playbar.frameRange()[0]
    hou.setFrame(start_frame)
    
    
    save_button= hou.parm(assetpath+"/execute")
    switch=set_asset_parm("select_cluster",0)
    
    set_asset_parm("trange",0)
    
    outputFile=eval_asset_parm("sopoutput")
    
    output_orig=outputFile
    
    frame_split="."+outputFile.split("/")[-1].split(".")[1]+"."
    
    name_split=outputFile.split("/")[-1].split(".")[0]
    
    replace_frame=".$F4."
    replace_name="cluster"
    
    #optimize the replace here
    change_frame=outputFile.replace(frame_split,replace_frame)
    cluster_size=eval_asset_parm("cluster_core")
    for i in range(cluster_size):
        replace_name="{0}_staticCluster{1}".format(name_split,i+1)
        outputFile_R=change_frame.replace(name_split,replace_name)
        set_asset_parm("sopoutput",outputFile_R)
        switch=set_asset_parm("select_cluster",i)
        save_button.pressButton()
        
        cl_file_node=hou.node(assetpath+"/feather_tool/cl_file_{0}".format(i))
        set_assetNode_parm(cl_file_node, "file", outputFile_R)
        
        
    set_asset_parm("sopoutput","$HIP/geo/$OS.$F.bgeo.sc")
    
    set_asset_parm("select_cluster",0)
    
    
    #update sequence read here
    
    
def clusterView_on_off():
    parm_dyna_tgle=eval_asset_parm("dyna_static_tgle")
    if parm_dyna_tgle==1:
        set_asset_parm("cluster_view",1)
    
        
  
def get_center_for_box(node_list):
  # find good position of boxes, which is center of selected nodes.
    list_x_of_selected_nodes = [node.position().x() for node in node_list]
    center_x = sum(list_x_of_selected_nodes) / len(node_list)
    list_y_of_selected_nodes = [node.position().y() for node in node_list]
    center_y = sum(list_y_of_selected_nodes) / len(node_list)
    
    return center_x,center_y

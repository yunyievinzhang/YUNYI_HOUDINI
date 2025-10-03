WING_TYPE="soulz::wing_feather::1.0"
import hou,sys

def asset_path():
    path=hou.node(".").path()
    return path


def asset_name():
    name=str(hou.node("."))
    return name
    
    
    

def set_asset_parm(parm, val):
    try:
        assetpath=asset_path()
        
        parm_str=assetpath+('/{0}'.format(parm))
        
        parm_eval=hou.parm(parm_str).set(val)
        
        
        return parm_eval
    except:
        hou.ui.displayMessage("there is no such parameter: {0}".format(parm))
        sys.exit()
        
        
def set_name():
    an=asset_name()
    outputFile="$HIP/geo/{0}.$F4.bgeo.sc".format(an)
    set_asset_parm("sopoutput",outputFile)

def render():
    wing_reader()
    set_asset_parm("switch_mat", 1)
    set_asset_parm("feather_switcher",2)
    set_asset_parm("dosinglepass",0)
    hou.pwd().parm("execute").pressButton()
    
    read_files()
    
    
def batch_render():
    wing_reader(multi_mode=True)
    
    nodes=hou.selectedNodes()
    
    for node in nodes:
        if node.type().name()=="soulz::wing_feather::1.0":
            if_render=node.parm("renderable").eval()
            if if_render:
                node.parm("switch_mat").set(1)
                node.parm("feather_switcher").set(2)
                node.parm("dosinglepass").set(0)
                
                node.parm("execute").pressButton()
    read_files()
                
def wing_reader(multi_mode=False):
    check=0
    obj=hou.node("/obj")
    for child in obj.children():
        if child.name()=="wing_reader":
            check=1
    if check==0:
        asset=hou.node(".")
        
        asset_position=asset.position()
        
        wr_pos=hou.Vector2(asset_position[0]+3, asset_position[1])
        
        wr=obj.createNode('geo', 'wing_reader')
        
        
        wr.setPosition(wr_pos)
        
        merge_node=wr.createNode("merge", "merge")
        
        merge_node.moveToGoodPosition()
    
    wr=obj.node("wing_reader")
    merge_node=wr.node("merge")
    selected_nodes=obj.selectedChildren()
    reader_used_list=[]
    for selected in selected_nodes:
        if selected.type().name()==WING_TYPE:
            wing_name=selected.name()
            if not wr.node("{0}_read".format(wing_name)):
                wing_file=wr.createNode("file", "{0}_read".format(wing_name))
                wing_file.moveToGoodPosition()
                wing_file.parm("file").set("")
                wing_file.parm("missingframe").set(1)
                merge_node.setNextInput(wing_file)
            reader_used_list.append("{0}_read".format(wing_name))
    if multi_mode:     
        if hou.node(".").parm("del_unselected").eval()==1:
            #start cleaning up ununsed node
            wing_file_list=collect_reader_file_name()
            unused_list=find_unused(reader_used_list, wing_file_list)
            for unused_name in unused_list:
                unused_node=hou.node("/obj/wing_reader/"+unused_name)
                unused_node.destroy()

def read_files():
    reader=hou.node("/obj/wing_reader")
    for child in reader.children():
        if child.type().name()=="file":
            outputfile="$HIP/geo/{0}.$F4.bgeo.sc".format(child.name().split("_read")[0])
            child.parm("file").set(outputfile)

def collect_reader_file_name():
    reader=hou.node("/obj/wing_reader")
    child_name_list=[]
    if reader:
        for child in reader.children():
            if child.type().name()=="file":
                child_name_list.append(child.name())
    return child_name_list
            
def find_unused(used_list, wr_child_list):
    unused_set=set()
    if len(used_list)<len(wr_child_list):
        used_set=set(used_list)
        wr_child_set=set(wr_child_list)
        unused_set=wr_child_set.difference(used_set)
     
    return unused_set
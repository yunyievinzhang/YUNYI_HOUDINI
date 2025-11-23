"""
State:          Hlgt::light promote edit::1.0
State type:     hlgt::light_promote_edit::1.0
Description:    Hlgt::light promote edit::1.0
Author:         zhangyunyi
Date Created:   March 03, 2025 - 18:01:45
"""

# Usage: Make sure to add 6 float parameters to the node:
# newparameter, newparameter2, newparameter3, newparameter4, newparameter5, newparameter6.
# Select node and hit enter in the viewer.

import hou
import viewerstate.utils as su

class PromoteEditState(object):
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer
        self.edit_handle = hou.Handle(self.scene_viewer, "Edit")
        self.selected_points=None

    def onEnter(self, kwargs):     
                
        self.edit_handle.show(True) 
        
    def onSelection(self, kwargs):
        """ Called when a selector has selected something
        """
        node = kwargs["node"]
        
        net_node=node.node("edit_net")
        
        if "selection" in kwargs:
            self.selected_points=kwargs["selection"]
        
        # if some points are selected
        if self.selected_points:
        
            edit_number=node.parm("multi_parm_edit").eval()
            
            #get point number
            point_num=str(self.selected_points)
            
            #get center pivot for handle
            center_pivot=self.selected_points.boundingBox().center()
            
            # create a new edit node
            edit_node=net_node.createNode("edit")
            
            # if it is not edited yet
            if not edit_number:
                # if not the stash node created
                if not net_node.node("stash_in"):
                    stash_in=net_node.createNode("stash", "stash_in")
                    stash_in.setInput(0,net_node.item("1"))
                    # load up current geo as stash
                    stash_in.parm("stashinput").pressButton()
                
                #edit will follow after stash
                edit_node.setInput(0,net_node.node("stash_in"))
            
            # if it is edited, connect to last edit_node
            else:
                edit_node.setInput(0,net_node.node("edit"+str(edit_number)))
            
            net_node.node('output0').setInput(0,edit_node)
            
            # Make them look good
            net_node.layoutChildren()
            
            # add a edit in node param
            new_edit_num=edit_number+1
            node.parm("multi_parm_edit").set(new_edit_num)
            
            # set proper channel reference
            node.parm("group"+str(new_edit_num)).set(point_num)

            # set the group type to primitive
            node.parm("grouptype"+str(new_edit_num)).set(4)

            # disable recompute point normals
            node.parm("updatenmls"+str(new_edit_num)).set(0)

            for parmtuple in edit_node.parmTuples():
                parmtuple_name=parmtuple.name()
                
                new_edit_parmtuple =node.parmTuple(parmtuple_name+str(new_edit_num))
                
                if new_edit_parmtuple:
                    parmtuple.set(new_edit_parmtuple)
            
            # center center pivot to align handler
            node.parmTuple("p"+str(new_edit_num)).set(center_pivot)
            
    def onHandleToState(self, kwargs):
        """ Used with bound dynamic handles to implement the state 
        action when a handle is modified.
        """
        handle = kwargs["handle"]
        parms = kwargs["parms"]
        mod_parms = kwargs["mod_parms"]
        prev_parms = kwargs["prev_parms"]
        ui_event = kwargs["ui_event"]
        node = kwargs["node"]
        
        edit_number=node.parm("multi_parm_edit").eval()
        
        # use geo movement to relocate the handle position
        node.parmTuple("t"+str(edit_number)).set((parms["tx"],parms["ty"],parms["tz"]))
        node.parmTuple("r"+str(edit_number)).set((parms["rx"],parms["ry"],parms["rz"]))
          
        self.log(parms)

    def onStateToHandle(self, kwargs):
        """ Used with bound dynamic handles to implement the handle 
        action when a state node parm is modified.
        """

        handle = kwargs["handle"]
        parms = kwargs["parms"]
        node = kwargs["node"]
        node = kwargs["node"]

        # this will control the distance handle with the vector handle
        
        edit_number=node.parm("multi_parm_edit").eval()
        
        # reflect handle movement on node
        if edit_number:
                 
            parms["px"] = node.evalParmTuple("p"+str(edit_number))[0]
            parms["py"] = node.evalParmTuple("p"+str(edit_number))[1]
            parms["pz"] = node.evalParmTuple("p"+str(edit_number))[2]
            parms["tx"] = node.evalParmTuple("t"+str(edit_number))[0]
            parms["ty"] = node.evalParmTuple("t"+str(edit_number))[1]
            parms["tz"] = node.evalParmTuple("t"+str(edit_number))[2]            
            parms["rx"] = node.evalParmTuple("r"+str(edit_number))[0]
            parms["ry"] = node.evalParmTuple("r"+str(edit_number))[1]
            parms["rz"] = node.evalParmTuple("r"+str(edit_number))[2]            
        self.log(parms)

    def onBeginHandleToState(self, kwargs):
        """ Used with bound dynamic handles to implement the state 
        action when a handle modification has started.
        """

        handle = kwargs["handle"]
        ui_event = kwargs["ui_event"]
        node = kwargs["node"]
        
    def onEndHandleToState(self, kwargs):
        """ Used with bound dynamic handles to implement the state 
        action when a handle modification has ended.
        """

        handle = kwargs["handle"]
        ui_event = kwargs["ui_event"]

def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = "light_promote_edit"
    state_label = "LightPromoteEdit"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(PromoteEditState)
    template.bindIcon("light_procedural_factory/HLGT_light_promote_edit.svg")
    template.bindHandle( "edit", "Edit")

    return template
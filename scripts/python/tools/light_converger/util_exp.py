import textwrap

# 烘焙方向脚本
BAKE_DIR_SCRIPT=textwrap.dedent('''
                            node = kwargs['node']
                            world_transform=node.worldTransform()
                            rotation=world_transform.extractRotates()
                            parent_node=node.parent()
                            parent_rotation=parent_node.worldTransform().extractRotates()
                            rotation-=parent_rotation
                            node.parmTuple("r").set(rotation)
                            node.parm("lookatpath").set("")
                            ''')
# 烘焙位置脚本
BAKE_POS_SCRIPT=textwrap.dedent('''
                            node = kwargs['node'];
                            world_transform=node.worldTransform();
                            translate=world_transform.extractTranslates();
                            parent_node=node.parent();
                            parent_translate=parent_node.worldTransform().extractTranslates();
                            translate-=parent_translate;
                            node.parmTuple("t").set(translate);
                            node.setInput(0, None);
                            ''')

# 恢复球体牵引脚本
RECOVER_LOOKAT_SCRIPT=textwrap.dedent('''
                            node = kwargs['node']
                            idx=node.name().split("_at_")[1]
                            parent_subnet=node.parent()
                            sphere_node=parent_subnet.node("sphere_"+idx)
                            node.parm("lookatpath").set(sphere_node.path())
                            ''')

# 恢复submarker脚本
RECOVER_SUBMARKER_SCRIPT=textwrap.dedent('''
                            node = kwargs['node']
                            idx=node.name().split("_at_")[1]
                            parent_subnet=node.parent()
                            submarker_node=parent_subnet.node("submarker_"+idx)

                            if (not (node.parm("if_keep_offset").eval())):
                                node.parmTuple("t").set(hou.Vector3([0,0,0]))

                            node.setInput(0, submarker_node)
                            ''')

# 烘焙开角脚本
BAKE_CONE_SCRIPT=textwrap.dedent('''
                            node = kwargs['node']
                            node.parm("ar_cone_angle").deleteAllKeyframes()
                            ''')

# 恢复开交总控脚本
RECOVER_CONE_SCRIPT=textwrap.dedent('''
                            node = kwargs['node']
                            parent = node.parent()
                            marker_node=parent.node("marker")
                            node.parm("ar_cone_angle").set(marker_node.parm("light_cone_angle"))
                            ''')

# 设置控制网格法线以及up脚本
SET_N_AND_UP_SCRIPT=textwrap.dedent("""
                            node = hou.pwd()
                            geo = node.geometry()
                            if not geo.findPointAttrib("N"):
                                geo.addAttrib(hou.attribType.Point, "N", (0.0, 1.0, 0.0), transform_as_normal=True)
                            if not geo.findPointAttrib("up"):
                                geo.addAttrib(hou.attribType.Point, "up", (0.0, 1.0, 0.0))
                            """)

# 恢复rivet控制脚本
RECOVER_RIVET_SCRIPT=textwrap.dedent('''
                            node = kwargs['node']
                            idx=node.name().split("sphere")[1]
                            parent_subnet=node.parent()
                            rivet_node=parent_subnet.node("rivet"+idx)

                            if (not (node.parm("if_keep_offset").eval())):
                                node.parmTuple("t").set(hou.Vector3([0,0,0]))

                            node.setInput(0, rivet_node)
                            ''')
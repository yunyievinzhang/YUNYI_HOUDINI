'''
一些适配流程的方法
'''
import os
import importlib

def get_hou_pyside_version():
    '''
    获取对应Houdini版本的PySide模块
    '''
    # 根据环境变量获取Houdini版本
    houdini_version=os.environ["HOUDINI_VERSION"]
    rough_version=int(houdini_version.split(".")[0])
    pyside_version=2

    if rough_version >20:
        pyside_version=6
    
    return pyside_version
    
def get_pyside_mod():
    '''
    导入PySide模块
    '''
    mod_full_name=f"PySide{get_hou_pyside_version()}"
    try:
        QtWidgets=importlib.import_module(f"{mod_full_name}.QtWidgets")
        QtCore=importlib.import_module(f"{mod_full_name}.QtCore")
        QtGui=importlib.import_module(f"{mod_full_name}.QtGui")
        return QtWidgets, QtCore, QtGui

    except ImportError as e:
       print(f"无法导入模块: {mod_full_name}:e")
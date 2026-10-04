'''
Pipeline compatibility helpers.
'''
import os
import importlib

def get_hou_pyside_version():
    '''
    Return the PySide major version used by the current Houdini version.
    '''
    # Read the Houdini version from the environment.
    houdini_version=os.environ["HOUDINI_VERSION"]
    rough_version=int(houdini_version.split(".")[0])
    pyside_version=2

    if rough_version >20:
        pyside_version=6
    
    return pyside_version
    
def get_pyside_mod():
    '''
    Import the matching PySide modules.
    '''
    mod_full_name=f"PySide{get_hou_pyside_version()}"
    try:
        QtWidgets=importlib.import_module(f"{mod_full_name}.QtWidgets")
        QtCore=importlib.import_module(f"{mod_full_name}.QtCore")
        QtGui=importlib.import_module(f"{mod_full_name}.QtGui")
        return QtWidgets, QtCore, QtGui

    except ImportError as e:
       print(f"Unable to import module: {mod_full_name}: {e}")

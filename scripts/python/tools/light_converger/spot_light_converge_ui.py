from tools import ppl_utils
QtWidgets=ppl_utils.get_pyside_mod()[0]
(
    QWidget, QVBoxLayout, QFormLayout, QSpinBox, 
 QDoubleSpinBox, QPushButton, QComboBox, QLineEdit
 ) = (
     QtWidgets.QWidget, QtWidgets.QVBoxLayout, 
QtWidgets.QFormLayout,QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox, 
QtWidgets.QPushButton, QtWidgets.QComboBox, QtWidgets.QLineEdit
)
'''
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QSpinBox, 
                               QDoubleSpinBox, QPushButton, QComboBox, QLineEdit)'''
from tools.light_converger import spot_light_converge
from pathlib import Path
from importlib import reload
import hou
import json
import os
PROJ_NODE_VERSION="1.1"
MARKER_NODE_VERSION="1.0"
class CreateLightFormationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Spotlight Formation")
        self.init_ui()

    def init_ui(self):
        reload(spot_light_converge)

        # Create the layout.
        layout = QVBoxLayout()
        form_layout = QFormLayout()  
        form_layout.setVerticalSpacing(5)

        # Column count.
        self.columns_input = QSpinBox()
        self.columns_input.setRange(1, 100)
        self.columns_input.setValue(5)

        # Row count.
        self.rows_input = QSpinBox()
        self.rows_input.setRange(1, 100)
        self.rows_input.setValue(5)

        # Spacing.
        self.spacing_input = QDoubleSpinBox()
        self.spacing_input.setMinimum(float('-inf'))
        self.spacing_input.setMaximum(float('inf'))
        self.spacing_input.setValue(2.0)

        # Marker height.
        self.marker_height_input=QDoubleSpinBox()
        self.marker_height_input.setMinimum(float('-inf'))
        self.marker_height_input.setMaximum(float('inf'))
        self.marker_height_input.setValue(10.0)

        # Light icon size.
        self.light_icon_input=QDoubleSpinBox()
        self.light_icon_input.setMinimum(float('-inf'))
        self.light_icon_input.setMaximum(float('inf'))
        self.light_icon_input.setValue(5.0)
        
        # Ground height.
        self.ground_height_input=QDoubleSpinBox()
        self.ground_height_input.setMinimum(float('-inf'))
        self.ground_height_input.setMaximum(float('inf'))
        self.ground_height_input.setValue(100.0)

        # Light type selector.
        self.light_combo=QComboBox()
        self.read_light_type()

        # Light group name.
        self.light_group_input=QLineEdit()
        
        # Add widgets to the form.
        form_layout.addRow("Light Type:", self.light_combo)
        form_layout.addRow("Light Group Name:", self.light_group_input)
        form_layout.addRow("Rows:", self.rows_input)
        form_layout.addRow("Columns:", self.columns_input)
        form_layout.addRow("Spacing:", self.spacing_input)
        form_layout.addRow("Default Marker Height:", self.marker_height_input)
        form_layout.addRow("Light Icon Size:", self.light_icon_input)
        form_layout.addRow("Initial Ground Height:", self.ground_height_input)

        # Button for creating the light formation.
        create_button = QPushButton("Create Formation")
        create_button.clicked.connect(self.on_submit)

        # Add widgets to the layout.
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(create_button)
        self.setLayout(layout)
        
        # Load defaults from the config file.
        self.read_default_config()

    def on_submit(self):
        # Light type.
        chosen_light_type=self.light_combo.currentText()
        light_node_type_name=self.light_type_dict[chosen_light_type]
        # Light group name.
        light_group_name=self.light_group_input.text() 
        # Row count.
        rows = self.rows_input.value()   
        # Column count.
        columns = self.columns_input.value()
        # Spacing.
        spacing = self.spacing_input.value()
        # Marker height.
        marker_height=self.marker_height_input.value()
        # Light icon size.
        light_icon_size=self.light_icon_input.value()
        # Ground height.
        ground_height=self.ground_height_input.value()

        # Check for missing values.
        item_check_dict={
            "Light Type": light_node_type_name,
            "Light Group Name": light_group_name,
            "Rows": rows,
            "Columns": columns,
            "Spacing": spacing,
            "Default Marker Height": marker_height,
            "Initial Ground Height": ground_height
        }

        missing=[ name for name, val in item_check_dict.items() if not val]
        
        if missing:
            missing_item_str=" ".join(missing)
            hou.ui.displayMessage(f"Please set the following parameters: {missing_item_str}")
            return
        # Create the light formation when all inputs are valid.
        spot_light_converge.create_light_formation(light_group_name, columns, 
                                                   rows,light_icon_size, spacing, marker_height, 
                                                   ground_height,light_node_type_name)

    def read_default_config(self):
        '''
        Read the default settings file.
        '''
        hip_dir=hou.expandString("$HIP")
        config_dir=f"{hip_dir}/config".replace("\\", "/")
        config_dir_obj=Path(config_dir)

        # Search for the config file when the directory exists.
        if config_dir_obj.is_dir():
           config_file=f"{config_dir}/light_formation_config.json"
           if os.path.exists(config_file):
                with open(config_file, "r", encoding='utf-8') as f:
                    config_obj=json.load(f)
                
                # Read values from the config file.
                light_type=config_obj.get("light_type", None)
                light_group=config_obj.get("light_group", None)
                row=config_obj.get("row", None)
                column=config_obj.get("column", None)
                space=config_obj.get("space", None)
                marker_height=config_obj.get("marker_height", None)
                light_icon_scale=config_obj.get("light_icon_scale", None)
                ground_height=config_obj.get("ground_height", None)
                
                # Apply values found in the config file to the UI.
                if light_type and (light_type in self.light_type_dict):
                    self.light_combo.setCurrentText(light_type)
                if light_group:
                    self.light_group_input.setText(light_group)
                if row:
                    self.rows_input.setValue(row)
                if column:
                    self.columns_input.setValue(column)
                if space:
                    self.spacing_input.setValue(space)
                if marker_height:
                    self.marker_height_input.setValue(marker_height)
                if light_icon_scale:
                    self.light_icon_input.setValue(light_icon_scale)
                if ground_height:
                    self.ground_height_input.setValue(ground_height)

    def read_light_type(self):
        '''
        Load the light types that can be used for convergence.
        '''
        # Locate the convergeable-light config file.
        current_dir=os.path.dirname(__file__).replace("\\", "/")
        light_type_config=f"{current_dir}/convergeable_light.json"

        # Load the UI options if the file exists.
        if os.path.exists(light_type_config):
            with open(light_type_config, "r", encoding='utf-8') as f:
                light_type_data=json.load(f)
            light_type_combo_list=list(light_type_data.keys())
            self.light_combo.addItems(light_type_combo_list)
            self.light_type_dict=light_type_data
             
    def closeEvent(self, event):
        self.setParent(None)

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
        self.setWindowTitle("聚光灯灯光阵创建")
        self.init_ui()

    def init_ui(self):
        reload(spot_light_converge)

        #创建Layout
        layout = QVBoxLayout()
        form_layout = QFormLayout()  
        form_layout.setVerticalSpacing(5)

        # 列参数
        self.columns_input = QSpinBox()
        self.columns_input.setRange(1, 100)
        self.columns_input.setValue(5)

        # 行参数
        self.rows_input = QSpinBox()
        self.rows_input.setRange(1, 100)
        self.rows_input.setValue(5)

        # 间隔参数
        self.spacing_input = QDoubleSpinBox()
        self.spacing_input.setMinimum(float('-inf'))
        self.spacing_input.setMaximum(float('inf'))
        self.spacing_input.setValue(2.0)

        # Marker 高度参数
        self.marker_height_input=QDoubleSpinBox()
        self.marker_height_input.setMinimum(float('-inf'))
        self.marker_height_input.setMaximum(float('inf'))
        self.marker_height_input.setValue(10.0)

        # 灯光图标大小参数
        self.light_icon_input=QDoubleSpinBox()
        self.light_icon_input.setMinimum(float('-inf'))
        self.light_icon_input.setMaximum(float('inf'))
        self.light_icon_input.setValue(5.0)
        
        # 地面高度参数
        self.ground_height_input=QDoubleSpinBox()
        self.ground_height_input.setMinimum(float('-inf'))
        self.ground_height_input.setMaximum(float('inf'))
        self.ground_height_input.setValue(100.0)

        # 灯光类型选择参数
        self.light_combo=QComboBox()
        self.read_light_type()

        # 灯组名参数
        self.light_group_input=QLineEdit()
        
        # 加入表格
        form_layout.addRow("灯光种类:", self.light_combo)
        form_layout.addRow("灯光组名:", self.light_group_input)
        form_layout.addRow("行:", self.rows_input)
        form_layout.addRow("列:", self.columns_input)
        form_layout.addRow("间隔:", self.spacing_input)
        form_layout.addRow("Marker默认高度: ", self.marker_height_input)
        form_layout.addRow("灯光图标大小: ", self.light_icon_input)
        form_layout.addRow("地面初始高度", self.ground_height_input)

        # 创建灯阵按钮
        create_button = QPushButton("创建阵列")
        create_button.clicked.connect(self.on_submit)

        # 加入layout
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(create_button)
        self.setLayout(layout)
        
        # 检查并阅读默认设置文件
        self.read_default_config()

    def on_submit(self):
        # 灯光类型
        chosen_light_type=self.light_combo.currentText()
        light_node_type_name=self.light_type_dict[chosen_light_type]
        # 灯光组名
        light_group_name=self.light_group_input.text() 
        # 行数
        rows = self.rows_input.value()   
        # 列数
        columns = self.columns_input.value()
        # 间隔
        spacing = self.spacing_input.value()
        # Marker高度
        marker_height=self.marker_height_input.value()
        # 灯光图标大小
        light_icon_size=self.light_icon_input.value()
        # 地面高度
        ground_height=self.ground_height_input.value()

        # 检查是否有未设置的参数
        item_check_dict={
            "灯光类型": light_node_type_name,
            "灯光组名": light_group_name,
            "行数": rows,
            "列数": columns,
            "间隔": spacing,
            "Marker 默认高度": marker_height,
            "地面初始高度": ground_height
        }

        missing=[ name for name, val in item_check_dict.items() if not val]
        
        if missing:
            missing_item_str=" ".join(missing)
            hou.ui.displayMessage(f"请妥善设置如下参数: {missing_item_str}")
            return
        # 如果一切正常就创建灯光阵
        spot_light_converge.create_light_formation(light_group_name, columns, 
                                                   rows,light_icon_size, spacing, marker_height, 
                                                   ground_height,light_node_type_name)

    def read_default_config(self):
        '''
        读取默认设置文件
        '''
        hip_dir=hou.expandString("$HIP")
        config_dir=f"{hip_dir}/config".replace("\\", "/")
        config_dir_obj=Path(config_dir)

        # 如果路径存在则搜索config文件
        if config_dir_obj.is_dir():
           config_file=f"{config_dir}/light_formation_config.json"
           if os.path.exists(config_file):
                with open(config_file, "r", encoding='utf-8') as f:
                    config_obj=json.load(f)
                
                # 获取config 文件内参数
                light_type=config_obj.get("light_type", None)
                light_group=config_obj.get("light_group", None)
                row=config_obj.get("row", None)
                column=config_obj.get("column", None)
                space=config_obj.get("space", None)
                marker_height=config_obj.get("marker_height", None)
                light_icon_scale=config_obj.get("light_icon_scale", None)
                ground_height=config_obj.get("ground_height", None)
                
                # 如果发现文件内设置就修改界面相关参数
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
        获取可以聚集的灯光类型用于加载界面
        '''
        # 寻找可聚集灯光类型配置文件
        current_dir=os.path.dirname(__file__).replace("\\", "/")
        light_type_config=f"{current_dir}/convergeable_light.json"

        # 如果法线则载入界面
        if os.path.exists(light_type_config):
            with open(light_type_config, "r", encoding='utf-8') as f:
                light_type_data=json.load(f)
            light_type_combo_list=list(light_type_data.keys())
            self.light_combo.addItems(light_type_combo_list)
            self.light_type_dict=light_type_data
             
    def closeEvent(self, event):
        self.setParent(None)
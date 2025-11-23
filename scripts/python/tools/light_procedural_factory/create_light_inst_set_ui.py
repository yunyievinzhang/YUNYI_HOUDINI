from tools import ppl_utils
QtWidgets=ppl_utils.get_pyside_mod()[0]
(
    QWidget, QVBoxLayout, QLabel, QLineEdit,QPushButton,
    QComboBox
) = (
    QtWidgets.QWidget, QtWidgets.QVBoxLayout, QtWidgets.QLabel, QtWidgets.QLineEdit, QtWidgets.QPushButton,
    QtWidgets.QComboBox
)
'''
from PySide2.QtWidgets import(
    QWidget, QVBoxLayout, QLabel, QLineEdit,QPushButton,
    QComboBox
)'''
from .create_light_inst_set import create_inst_set

def start_create(light_name, light_type_name):
     create_inst_set(light_name, light_type_name)

class CreateSetWindow(QWidget):
     def __init__(self):
          super().__init__()
          self.setWindowTitle("灯光Instance模板生成")
          layout=QVBoxLayout()
          
          self.name_label=QLabel("请输入灯光名字")
          layout.addWidget(self.name_label)
          self.line_edit=QLineEdit()
          layout.addWidget(self.line_edit)

          layout.addSpacing(20)
          
          self.type_label=QLabel("请选择灯光类型")
          layout.addWidget(self.type_label)

          self.combo= QComboBox()
          self.combo.addItems(["point", "spot", "quad", "disk"])
          layout.addWidget(self.combo)
          layout.addSpacing(20)

          self.button=QPushButton("确认")
          self.button.clicked.connect(self.on_submit)
          layout.addWidget(self.button)
          self.setLayout(layout)

     def on_submit(self):
          light_name=self.line_edit.text().strip()
          light_type_name=self.combo.currentText()

          if light_name:
               start_create(light_name, light_type_name)
               self.close()
          else:
               self.name_label.setText("请输入有效名字！")
               
     def closeEvent(self, event):
               self.setParent(None)
from Ui_SettingDialog import Ui_SettingDialog
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class PatternMenu(Ui_SettingDialog):
    def __init__(self, parent_dialog, parent_window, index, d_shape, d_radius, d_color, d_position):
        super().__init__()
        self.parent_dialog = parent_dialog
        self.parent_window = parent_window
        self.index = index
        self.setupUi(self.parent_dialog)
        self.color = d_color
        R,G,B = self.color
        X,Y = d_position
        self.comboBox_shape.setCurrentText(str(d_shape))
        self.lineedit_radius.setText(str(d_radius))
        self.button_color.setStyleSheet(f"background:rgb({R},{G},{B})")
        self.lineedit_position.setText(f"{X}, {Y}")
        self.btn_connect()
    def btn_connect(self):
        self.button_color.clicked.connect(self.btn_color_clicked)
        self.button_ok.clicked.connect(self.btn_ok_clicked)
    def menu_shape(self):
        self.shape = self.comboBox_shape.currentText()
        return self.shape
    def menu_radius(self):
        self.radius = self.lineedit_radius.text()
        return self.radius
    def btn_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.RGBcolor = list(color.getRgb())
            self.RGBcolor.pop()
            self.button_color.setStyleSheet("background:rgb{}" .format(tuple(self.RGBcolor)))
        self.color = tuple(self.RGBcolor)    
    def menu_position(self):
        self.position = self.lineedit_position.text()
        return self.position
    def btn_ok_clicked(self):
        self.parent_window.index = self.index
        self.parent_window.shape = self.menu_shape()
        self.parent_window.radius = self.menu_radius()
        self.parent_window.color = self.color
        self.parent_window.position = self.menu_position()
        self.parent_dialog.close()
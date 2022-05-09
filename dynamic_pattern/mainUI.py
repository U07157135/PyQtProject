from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from DynamicPatternTOP import DynamicPatternTOP
from Ui_MainWindow import Ui_MainWindow
from mainUI_menu import PatternMenu
import os
import sys


class MyView(QGraphicsView):
    def __init__(self, parent=None):
        super(QGraphicsView, self).__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 關閉scroll bar
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)  # 關閉scroll bar
        self.setRenderHints(
            QPainter.Antialiasing |     # 抗鋸齒
            QPainter.HighQualityAntialiasing |      # 高品質抗鋸齒
            QPainter.SmoothPixmapTransform        # 使圖片平
        )
        self.updata_data = []
        self.index, self.shape, self.radius, self.color, self.position = None, None, None, None,None
    def set_parent_window(self, parent_window):
        self.parent_window = parent_window
    def get_item_at_click(self, event):
        self.item_at_click = self.itemAt(event.pos()) # 最上層的原件
        if self.item_at_click is not None:
            if self.item_at_click.data(0) is not None:
                self.item = self.item_at_click.data(0)
                return True
            else:
                return False
        return False
    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        if self.get_item_at_click(event):
            d = self.parent_window.circle_data_dict_total
            d_index = d[str(self.item+1)]
            d_shape, d_radius, d_color, d_position = d_index['shape'], d_index[
                'radius'], d_index['color'], d_index['position']
            pattern_dialog = QtWidgets.QDialog()
            menu = PatternMenu(pattern_dialog, self, self.item, d_shape, d_radius, d_color, d_position)
            pattern_dialog.setWindowTitle(f"第{self.item+1}層")
            pattern_dialog.exec()
            if self.radius is None or self.radius == '' or self.position is None or self.position == '':
                pass
            else:
                self.updata_data = [int(self.index), str(self.shape), str(self.radius), tuple(self.color), str(self.position)]
                self.parent_window.update_data(self.updata_data)
    def mouseMoveEvent(self, event):
        if self.get_item_at_click(event):
            item_center_pos_at_scene = self.item_at_click.scenePos()
            item_x_at_scene = item_center_pos_at_scene.x()
            item_y_at_scene = item_center_pos_at_scene.y()
            self.parent_window.set_position(self.item,int(item_x_at_scene),int(item_y_at_scene))
        super().mouseMoveEvent(event)

class MyScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(-320, -180, 640, 360)   # 固定graphics
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

class MyCircle(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

class MySquare(QGraphicsRectItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable)
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.DynamicPattern.set_parent_window(self)

        self.row_total = int(self.ui.tableWidget.rowCount())  # 當前行數

        self.pattern_api = DynamicPatternTOP()
        self.res_length = int(self.ui.lineEdit_length.text())
        self.res_width = int(self.ui.lineEdit_width.text())
        self.set_resolution = self.pattern_api.set_resolution(
            self.res_length, self.res_width)

        for i in range(self.row_total):
            self.comboBox = QtWidgets.QComboBox()
            self.comboBox.addItem("circle")
            self.comboBox.addItem("square")
            self.ui.tableWidget.setCellWidget(i, 0, self.comboBox)

        self.scene = MyScene()
        self.ui.DynamicPattern.setScene(self.scene)

        self.cross_line = "False"

        self.btn_connect()
    def btn_connect(self):
        self.ui.open_btn.clicked.connect(self.image_open)
        self.ui.action_save.triggered.connect(self.save_json)
        self.ui.action_import.triggered.connect(self.import_json)
        self.ui.cross_line_click.stateChanged.connect(self.cross_line_checkbox)
    def set_position(self, item_index:int, item_x_at_scene:int, item_y_at_scene:int):
        self.ui.tableWidget.setItem(item_index, 3, QTableWidgetItem("{}, {}" .format((item_x_at_scene)*3,(item_y_at_scene)*-3)))
    def update_data(self, updata_data:list):
        updata_index, updata_shape, updata_radius, updata_color, updata_position = updata_data
        if self.cross_line == "True":
            self.scene.clear()
            self.add_cross_line()
        else:
            self.scene.clear()
        R, G, B = updata_color
        shape_combobox = self.ui.tableWidget.cellWidget(updata_index, 0)
        if updata_shape == "circle":
            shape_combobox.setCurrentIndex(0)
        elif updata_shape == "square":
            shape_combobox.setCurrentIndex(1)
        self.ui.tableWidget.setItem(updata_index, 1, QTableWidgetItem(updata_radius))
        self.ui.tableWidget.setItem(updata_index, 2, QTableWidgetItem(f"{R}, {G}, {B}"))
        self.ui.tableWidget.setItem(updata_index, 3, QTableWidgetItem(updata_position))
        self.get_data_from_tabelwidget()
    def grahics_item(self, index:int, z_value:int, shape:str, radius:int, color:tuple, position:tuple):
        radius = int(radius)*2/3
        x = int(position[0])/3
        y = int(position[1])/3
        R, G, B = color
        if shape == "circle":
            self.my_object = MyCircle(QRectF(-radius/2, -radius/2, radius, radius))
        elif shape == "square":
            self.my_object = MySquare(QRectF(-radius/2, -radius/2, radius, radius))
        else:
            pass
        self.my_object.setPos(x,y)
        self.my_object.setPen(QtGui.QPen(QtGui.QColor(R, G, B)))
        self.my_object.setBrush(QtGui.QBrush(QtGui.QColor(R, G, B)))
        self.my_object.setZValue(z_value)
        self.my_object.setData(0, index)
        self.scene.addItem(self.my_object)
        # print("第{}層".format(self.my_object.data(0)))
    def get_data_from_tabelwidget(self):
        print("觸發")
        if self.cross_line == "True":
            self.scene.clear()
            self.add_cross_line()
        else:
            self.scene.clear()
        self.circle_data_dict_total = {}
        radius = 0
        level = 0
        for i in range(self.row_total):
            self.circle_data_dict = {}  # 一層的資料
            self.shape_value_at_tablewidget = self.ui.tableWidget.cellWidget(i, 0)  # 形狀
            self.radius_value_at_tablewidget = self.ui.tableWidget.item(i, 1)  # 半徑
            self.color_value_at_tablewidget = self.ui.tableWidget.item(i, 2)  # 顏色
            self.position_value_at_tablewidget = self.ui.tableWidget.item(i, 3)  # 位置
            if (self.radius_value_at_tablewidget is not None and self.radius_value_at_tablewidget.text() != '') and (self.color_value_at_tablewidget is not None and self.radius_value_at_tablewidget.text() != ''):  # 判斷空格是否為空的

                if self.shape_value_at_tablewidget is not None and self.radius_value_at_tablewidget.text() != '':
                    self.circle_data_dict.setdefault("shape", str(self.shape_value_at_tablewidget.currentText()))

                if self.radius_value_at_tablewidget is not None and self.radius_value_at_tablewidget.text() != '':
                    radius += int(self.radius_value_at_tablewidget.text())
                    self.circle_data_dict.setdefault("radius", int(self.radius_value_at_tablewidget.text()))

                if self.color_value_at_tablewidget is not None and self.color_value_at_tablewidget.text() != '':
                    color = tuple(map(int, self.color_value_at_tablewidget.text().split(', ')))
                    self.circle_data_dict.setdefault("color", color)

                if self.position_value_at_tablewidget is not None and self.position_value_at_tablewidget.text() != '':
                    position = tuple(map(int, self.position_value_at_tablewidget.text().split(', ')))
                    self.circle_data_dict.setdefault("position", position)

                self.circle_data_dict_total.setdefault(str(i+1), self.circle_data_dict)

                self.grahics_item(i, level, self.shape_value_at_tablewidget.currentText(), radius, color, position)
                level -= 1
            else:
                break
        self.circle_data_dict_total.setdefault("cross_line", self.cross_line)
        # print(self.circle_data_dict_total)
        return self.circle_data_dict_total
    def image_open(self):
        self.pattern_api.set_pattern_dict(self.get_data_from_tabelwidget())
        self.pattern_api.save_image()
        self.pattern_api.show()
    def save_json(self):
        curPath = QDir.currentPath()
        dlgTitle = "Import File"
        filt = "all_file(*.json*)"
        filename = QFileDialog.getSaveFileName(None, dlgTitle, curPath, filt)
        if filename[0] == '':
            pass
        else:
            json_file = os.path.split(filename[0])
            json_path = json_file[0]
            json_name = json_file[1]
            self.pattern_api.save_json(path=json_path, name=json_name)
    def import_json(self):
        curPath = QDir.currentPath()
        dlgTitle = "Import File"
        filt = "all_file(*.json*)"
        filename = QFileDialog.getOpenFileName(None, dlgTitle, curPath, filt)
        if filename[0] == '':
            pass
        else:
            json_file = self.pattern_api.load_json(path=filename[0])
            self.set_data_at_tabelwidget(json_file)        
    def set_data_at_tabelwidget(self, data:dict):
        for index, circle_index in enumerate(data):
            if circle_index != "cross_line":
                circle_data = data[circle_index]
                shape = circle_data["shape"]
                radius = circle_data["radius"]
                color = circle_data["color"]
                color = str(color).lstrip("[")
                color = str(color).strip("]")
                shape_combobox = self.ui.tableWidget.cellWidget(int(index), 0)
                if shape == "circle":
                    shape_combobox.setCurrentIndex(0)
                elif shape == "square":
                    shape_combobox.setCurrentIndex(1)
                else:
                    pass
                self.ui.tableWidget.setItem(
                    int(index), 1, QTableWidgetItem(str(radius)))
                self.ui.tableWidget.setItem(
                    int(index), 2, QTableWidgetItem(str(color)))
                if "position" not in circle_data:
                    self.ui.tableWidget.setItem(
                        int(index), 3, QTableWidgetItem("0, 0"))
                else:
                    position = circle_data["position"]
                    position = str(position).lstrip("[")
                    position = str(position).strip("]")
                    self.ui.tableWidget.setItem(
                        int(index), 3, QTableWidgetItem(str(position)))
            else:
                if data[circle_index] == "True":
                    self.cross_line = "True"
                    self.ui.cross_line_click.setCheckState(Qt.Checked)
                else:
                    self.cross_line = "False"
        self.get_data_from_tabelwidget()
    def cross_line_checkbox(self, checkbox_state:int):
        if (QtCore.Qt.Checked == checkbox_state):
            self.cross_line = "True"
            self.add_cross_line()
        else:
            self.cross_line = "False"
            self.del_cross_line()
    def add_cross_line(self):
        self.line1 = QGraphicsLineItem(-640/2, 0, 640/2, 0)
        self.line1.setZValue(1000)
        self.line2 = QGraphicsLineItem(0, -360/2, 0, 360/2)
        self.line2.setZValue(1000)
        self.scene.addItem(self.line1)
        self.scene.addItem(self.line2)
    def del_cross_line(self):
        self.scene.removeItem(self.line1)
        self.scene.removeItem(self.line2)
        
        


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
